"""Provider-chain tests: TokenCTR opt-in, cost logging, no-key chain hardening.

All HTTP is mocked. No key values are used: the TokenCTR "key" below is a
placeholder string set only inside the test process. Nothing spends credit.
Run from the repo root:  python -m unittest tests.test_providers_ai -v
"""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
import urllib.error
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import providers as P  # noqa: E402

AI_ENV = ["SC_AI", "GEMINI_API_KEY", "GOOGLE_API_KEY", "FORGE_GEMINI_KEY_FILE", "OPENROUTER_API_KEY",
          "OPENROUTER_API_KEY_FILE", "OPENWORK_API_KEY", "OPENWORK_INFERENCE_BASE_URL",
          "TOKENCTR_API_KEY", "SC_TOKENCTR_PAID", "SC_TOKENCTR_PRICE_PER_TOKEN", "SC_TOKENCTR_VALIDATE",
          "SC_TOKENCTR_MODEL", "TOKENCTR_BASE_URL", "SC_OPENWORK_PRICE_PER_TOKEN", "SC_AI_BUILD_CAP",
          "SC_AI_CACHE_DIR", "SC_TOKENCTR_CATALOG_URL"]
PLACEHOLDER = "placeholder-not-a-real-key"


def ok_reply(text="{\"ok\": true}", usage=None, cost=None):
    d = {"choices": [{"message": {"content": text}}], "usage": usage or {"prompt_tokens": 100, "completion_tokens": 50}}
    if cost is not None:
        d["usage"]["cost"] = cost
    return d


def http_error(code, err_code):
    return urllib.error.HTTPError("https://api.tokenctr.com/v1/chat/completions", code, "x", {},
                                  io.BytesIO(json.dumps({"error": {"code": err_code}}).encode()))


class Base(unittest.TestCase):
    def setUp(self):
        self._env = mock.patch.dict(os.environ, {}, clear=False)
        self._env.start()
        for n in AI_ENV:
            os.environ.pop(n, None)
        os.environ["SC_TOKENCTR_VALIDATE"] = "0"          # catalog is tested separately
        P.TokenCtr._catalog, P.TokenCtr._catalog_tried = None, False
        P.NoKey._spent, P.NoKey._noticed = 0.0, False

    def tearDown(self):
        self._env.stop()

    def paid_on(self):
        os.environ["TOKENCTR_API_KEY"] = PLACEHOLDER
        os.environ["SC_TOKENCTR_PAID"] = "1"


class ChainOrder(Base):
    def test_default_no_keys_is_empty_and_build_falls_back(self):
        self.assertEqual(P.resolve_chain({}), [])
        with self.assertRaises(SystemExit):
            P.complete(system="s", user="u", opts={}, ledger=P.Ledger(), purpose="t")

    def test_nokey_last_of_free_and_before_tokenctr(self):
        os.environ["SC_AI"] = "on"
        self.paid_on()
        ids = [c["provider"].id for c in P.resolve_chain({"allow_paid": True})]
        self.assertEqual(ids, ["nokey", "tokenctr"])
        ids = [c["provider"].id for c in P.resolve_chain({})]
        self.assertEqual(ids, ["nokey"], "tokenctr must not join the auto chain without --allow-paid")

    def test_forced_nokey_without_sc_ai_message(self):
        with self.assertRaises(SystemExit) as cm:
            P.resolve_chain({"provider": "nokey"})
        self.assertIn("SC_AI=on", str(cm.exception))
        self.assertNotIn("API key", str(cm.exception))

    def test_paid_without_opt_in_refused(self):
        os.environ["TOKENCTR_API_KEY"] = PLACEHOLDER
        self.assertFalse(P.TokenCtr.configured())
        self.assertEqual([c["provider"].id for c in P.resolve_chain({"allow_paid": True})], [])
        with self.assertRaises(SystemExit) as cm:
            P.resolve_chain({"provider": "tokenctr"})
        self.assertIn("SC_TOKENCTR_PAID=1", str(cm.exception))
        with mock.patch.object(P, "_http_json") as http:
            with self.assertRaises(P.ProviderError):
                P.TokenCtr.call(system="s", user="u", model=P.TokenCtr.DEFAULT_MODEL,
                                max_output_tokens=10, temperature=0, timeout=5)
            http.assert_not_called()

    def test_opt_in_without_key_refused(self):
        os.environ["SC_TOKENCTR_PAID"] = "1"
        self.assertFalse(P.TokenCtr.configured())
        with self.assertRaises(SystemExit) as cm:
            P.resolve_chain({"provider": "tokenctr"})
        self.assertIn("TOKENCTR_API_KEY", str(cm.exception))

    def test_forced_tokenctr_falls_back_to_nokey_when_enabled(self):
        self.paid_on()
        os.environ["SC_AI"] = "on"
        self.assertEqual([c["provider"].id for c in P.resolve_chain({"provider": "tokenctr"})],
                         ["tokenctr", "nokey"])


class TokenCtrCalls(Base):
    def test_paid_opt_in_call_shape_and_cost(self):
        self.paid_on()
        os.environ["SC_TOKENCTR_PRICE_PER_TOKEN"] = "0.0000001"
        with mock.patch.object(P, "_http_json", return_value=ok_reply()) as http:
            led = P.Ledger()
            r = P.complete(system="s", user="u", opts={"provider": "tokenctr"}, ledger=led, purpose="t")
        url, body, headers, _ = http.call_args[0]
        self.assertEqual(url, "https://api.tokenctr.com/v1/chat/completions")
        self.assertEqual(body["model"], "mistralai/ministral-3b-2512")
        self.assertEqual(headers["authorization"], "Bearer " + PLACEHOLDER)
        self.assertEqual(r["provider"], "tokenctr")
        a = led.attempts[0]
        self.assertEqual(a["tier"], "paid")
        self.assertAlmostEqual(a["est_cost_usd"], 150 * 1e-7)
        t = led.totals()
        self.assertEqual(t["paid_calls"], 1)
        self.assertAlmostEqual(t["paid_cost_usd"], 1.5e-05)
        self.assertNotIn(PLACEHOLDER, json.dumps(led.attempts))

    def test_no_price_is_unknown_not_zero(self):
        self.paid_on()
        with mock.patch.object(P, "_http_json", return_value=ok_reply()):
            led = P.Ledger()
            P.complete(system="s", user="u", opts={"provider": "tokenctr"}, ledger=led, purpose="t")
        a = led.attempts[0]
        self.assertIsNone(a["est_cost_usd"])
        self.assertEqual(a["cost"], "unknown")
        self.assertEqual(led.totals()["unknown_cost_calls"], 1)
        self.assertIn("cost unknown", led.summary_line())

    def test_reply_cost_field_wins(self):
        self.paid_on()
        os.environ["SC_TOKENCTR_PRICE_PER_TOKEN"] = "1"
        with mock.patch.object(P, "_http_json", return_value=ok_reply(cost=0.0042)):
            led = P.Ledger()
            P.complete(system="s", user="u", opts={"provider": "tokenctr"}, ledger=led, purpose="t")
        self.assertAlmostEqual(led.attempts[0]["est_cost_usd"], 0.0042)
        self.assertEqual(led.attempts[0]["cost_source"], "response")

    def test_429_quota_exhausted_maps_no_credit_and_falls_back(self):
        self.paid_on()
        os.environ["SC_AI"] = "on"
        nk = {"text": "fallback text", "usage": {"in_tokens": 0, "out_tokens": 0},
              "model": "chain:llm7", "cost_usd": 0.0}
        with mock.patch.object(P, "_http_json", side_effect=http_error(429, "quota_exhausted")), \
                mock.patch.object(P.NoKey, "call", return_value=nk):
            led = P.Ledger()
            r = P.complete(system="s", user="u", opts={"provider": "tokenctr"}, ledger=led, purpose="t")
        self.assertEqual(r["provider"], "nokey")
        self.assertEqual(r["model"], "chain:llm7")
        self.assertIn("no_credit", led.attempts[0]["error"])
        self.assertEqual(led.attempts[0]["est_cost_usd"], 0.0)
        self.assertEqual(led.attempts[1]["tier"], "free")

    def test_402_maps_no_balance_then_template(self):
        self.paid_on()
        with mock.patch.object(P, "_http_json", side_effect=http_error(402, "insufficient_credits")):
            with self.assertRaises(RuntimeError) as cm:     # build's offline/template fallback catches this
                P.complete(system="s", user="u", opts={"provider": "tokenctr"}, ledger=P.Ledger(), purpose="t")
        self.assertIn("no_balance", str(cm.exception))

    def test_catalog_validation_blocks_unknown_model_without_chat_call(self):
        self.paid_on()
        os.environ.pop("SC_TOKENCTR_VALIDATE")
        with mock.patch.object(P, "_http_json", return_value=[{"id": "mistralai/ministral-3b-2512"}]) as http:
            with self.assertRaises(P.ProviderError) as cm:
                P.TokenCtr.call(system="s", user="u", model="some/other-model",
                                max_output_tokens=10, temperature=0, timeout=5)
        self.assertIn("not in the TokenCTR catalog", str(cm.exception))
        self.assertEqual(http.call_count, 1)                 # catalog GET only

    def test_catalog_unreachable_does_not_block(self):
        self.paid_on()
        os.environ.pop("SC_TOKENCTR_VALIDATE")
        calls = [OSError("offline"), ok_reply()]
        with mock.patch.object(P, "_http_json", side_effect=calls):
            r = P.TokenCtr.call(system="s", user="u", model=P.TokenCtr.DEFAULT_MODEL,
                                max_output_tokens=10, temperature=0, timeout=5)
        self.assertEqual(r["tier"], "paid")


class OpenWorkCost(Base):
    def setUp(self):
        super().setUp()
        os.environ["OPENWORK_API_KEY"] = PLACEHOLDER
        os.environ["OPENWORK_INFERENCE_BASE_URL"] = "https://example.invalid/v1"
        self._m = mock.patch.object(P.OpenWork, "models", ["org/model"])
        self._m.start()

    def tearDown(self):
        self._m.stop()
        super().tearDown()

    def run_one(self, reply):
        with mock.patch.object(P, "_http_json", return_value=reply):
            led = P.Ledger()
            P.complete(system="s", user="u", opts={"provider": "openwork"}, ledger=led, purpose="t")
        return led

    def test_openwork_unknown_cost_not_zero(self):
        led = self.run_one(ok_reply())
        self.assertIsNone(led.attempts[0]["est_cost_usd"])
        self.assertEqual(led.attempts[0]["cost"], "unknown")
        self.assertEqual(led.attempts[0]["tier"], "unknown")

    def test_openwork_reported_cost(self):
        led = self.run_one(ok_reply(cost=0.01))
        self.assertAlmostEqual(led.attempts[0]["est_cost_usd"], 0.01)

    def test_openwork_configured_price(self):
        os.environ["SC_OPENWORK_PRICE_PER_TOKEN"] = "0.000001"
        led = self.run_one(ok_reply())
        self.assertAlmostEqual(led.attempts[0]["est_cost_usd"], 150e-6)


class NoKeyHardening(Base):
    def fake_module(self, captured):
        def generate(system, user, fallback="", **kw):
            captured.update(kw)
            return SimpleNamespace(source="ai", text="hello there friend", provider="llm7", reason="")
        return SimpleNamespace(generate=generate)

    def test_budget_notice_model_cache(self):
        os.environ["SC_AI"] = "on"
        cap = {}
        err = io.StringIO()
        with mock.patch.object(P.NoKey, "_module", return_value=self.fake_module(cap)), redirect_stderr(err):
            r1 = P.NoKey.call(system="s", user="u", model="chain", max_output_tokens=9000, temperature=0.5, timeout=90)
            P.NoKey.call(system="s", user="u", model="chain", max_output_tokens=10, temperature=0.5, timeout=20)
        self.assertEqual(err.getvalue().count("anonymous public AI endpoints"), 1)
        self.assertEqual(r1["model"], "chain:llm7")
        self.assertLessEqual(cap["budget_seconds"], 20)
        self.assertTrue(Path(os.environ["SC_AI_CACHE_DIR"]).is_absolute())

    def test_per_build_cap(self):
        os.environ["SC_AI"] = "on"
        P.NoKey._spent = 89.5
        with self.assertRaises(P.ProviderError) as cm:
            P.NoKey.call(system="s", user="u", model="chain", max_output_tokens=10, temperature=0.5, timeout=90)
        self.assertIn("per-build cap", str(cm.exception))

    def test_ledger_records_route(self):
        os.environ["SC_AI"] = "on"
        with mock.patch.object(P.NoKey, "_module", return_value=self.fake_module({})), redirect_stderr(io.StringIO()):
            led = P.Ledger()
            r = P.complete(system="s", user="u", opts={"provider": "nokey"}, ledger=led, purpose="t")
        self.assertEqual(led.attempts[0]["model"], "chain:llm7")
        self.assertEqual(led.attempts[0]["est_cost_usd"], 0.0)
        self.assertEqual(r["model"], "chain:llm7")


class ChainModule(Base):
    def test_forbidden_hosts_refused(self):
        m = P.NoKey._module()
        for url in ("https://openrouter.ai/api/v1/chat/completions", "https://api.x.ai/v1/chat",
                    "https://generativelanguage.googleapis.com/v1", "https://aiplatform.googleapis.com/v1"):
            self.assertTrue(m.route_problem({"url": url}), url)
        self.assertEqual(m.route_problem({"url": "https://api.llm7.io/v1/chat/completions", "bearer": "unused"}), "")

    def test_describe_routes_lists_free_chain(self):
        rows = P.NoKey._module().describe_routes({})
        ids = [r["id"] for r in rows]
        for rid in ("ollama-local", "llm7", "chat-at", "pollinations"):
            self.assertIn(rid, ids)
        self.assertNotIn(PLACEHOLDER, json.dumps(rows))

    def test_budget_seconds_caps_deadline(self):
        m = P.NoKey._module()
        seen = {}

        def tr(p, system, user, mt, t, timeout):
            seen["timeout"] = timeout
            return "a long enough reply for sanity", "m"
        ch = m.Chain(env={"SC_AI": "on", "SC_AI_ROUTES": "llm7", "SC_AI_CACHE_DIR": str(ROOT / ".sc_ai_cache_test_unused")},
                     transports={"openai": tr})
        r = ch.run("s", "u", budget_seconds=5, use_cache=False)
        self.assertEqual(r.source, "ai")
        self.assertLessEqual(seen["timeout"], 5)


class ReportStability(Base):
    def test_empty_ledger_totals_keys_unchanged(self):
        self.assertEqual(sorted(P.Ledger().totals()), ["est_cost_usd", "in_tokens", "ok", "out_tokens", "requests"])


if __name__ == "__main__":
    unittest.main()
