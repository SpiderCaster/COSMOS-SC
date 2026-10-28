"""Model provider chain: free tiers first, paid only on explicit --allow-paid.

Cost order: Gemini free tier (AI Studio key) -> OpenRouter :free models ->
OpenWork org inference -> no-key free chain (SC_AI=on) -> TokenCTR purchased
credits (opt-in only). Paid OpenRouter models join the chain ONLY when
--allow-paid is passed. TokenCTR joins only when TOKENCTR_API_KEY is present
AND SC_TOKENCTR_PAID=1 is set (and --allow-paid, or --provider tokenctr).
The ledger records token counts, tier and env var NAMES, never key values.
A cost the engine cannot know is recorded as None ("unknown"), never as $0.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_TIMEOUT = 90.0
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


def env_list(name: str, fallback: str) -> list[str]:
    raw = os.environ.get(name) or fallback
    return [x.strip() for x in raw.split(",") if x.strip()]


def _http_json(url: str, payload: dict | None, headers: dict | None, timeout: float) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class ProviderError(Exception):
    pass


class Ledger:
    """Token ledger for one run. Records counts only, never key values."""

    def __init__(self):
        self.attempts: list[dict] = []

    def add(self, **kw) -> None:
        kw["at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.attempts.append(kw)

    def totals(self) -> dict:
        ok = [a for a in self.attempts if a.get("ok")]
        out = {
            "requests": len(self.attempts),
            "ok": len(ok),
            "in_tokens": sum(a.get("in_tokens", 0) for a in ok),
            "out_tokens": sum(a.get("out_tokens", 0) for a in ok),
            "est_cost_usd": round(sum(a.get("est_cost_usd") or 0 for a in ok), 6),
        }
        # Extra keys appear only when they carry information, so a zero-token
        # (offline / AI-off) report.json stays byte-identical to older builds.
        unknown = sum(1 for a in ok if a.get("est_cost_usd") is None)
        if unknown:
            out["unknown_cost_calls"] = unknown
        paid = [a for a in ok if a.get("tier") == "paid"]
        if paid:
            out["paid_calls"] = len(paid)
            out["paid_cost_usd"] = round(sum(a.get("est_cost_usd") or 0 for a in paid), 6)
        return out

    def summary_line(self) -> str:
        t = self.totals()
        line = (f"requests={t['requests']} ok={t['ok']} "
                f"in={t['in_tokens']} out={t['out_tokens']} est_cost=${t['est_cost_usd']:.4f}")
        if t.get("paid_calls"):
            line += f" paid_calls={t['paid_calls']}"
        if t.get("unknown_cost_calls"):
            line += f" (+{t['unknown_cost_calls']} call(s) cost unknown)"
        return line


# ---------------------------------------------------------------- providers

class Gemini:
    id = "gemini"
    label = "Google Gemini (AI Studio free tier / Vertex express)"
    free = True
    models = env_list("FORGE_GEMINI_MODELS", "gemini-2.5-flash-lite,gemini-2.0-flash,gemini-2.5-flash")

    @classmethod
    def configured(cls) -> bool:
        if os.environ.get("FORGE_GEMINI_KEY_FILE"):
            return True
        return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))

    @classmethod
    def key(cls) -> str:
        """Draw-source selection: FORGE_GEMINI_KEY_FILE (a key file path, the
        house pattern) wins; else GEMINI_API_KEY / GOOGLE_API_KEY. Fails closed
        if the file is set but unreadable - never silently draw another wallet."""
        key_file = os.environ.get("FORGE_GEMINI_KEY_FILE")
        if key_file:
            with open(key_file, "r", encoding="utf-8") as fh:
                return fh.read().strip()
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""

    @classmethod
    def call(cls, *, system, user, model, max_output_tokens, temperature, timeout) -> dict:
        """Try AI Studio first, then Vertex express mode; same key, same shape."""
        errors = []
        for route in (cls._call_studio, cls._call_vertex):
            try:
                return route(system=system, user=user, model=model,
                             max_output_tokens=max_output_tokens, temperature=temperature,
                             timeout=timeout)
            except ProviderError as exc:
                errors.append(str(exc))
        raise ProviderError(" | ".join(errors))

    @classmethod
    def _call_studio(cls, *, system, user, model, max_output_tokens, temperature, timeout) -> dict:
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
                "responseMimeType": "application/json",
            },
        }
        try:
            data = _http_json(
                f"{GEMINI_BASE}/models/{model}:generateContent",
                body, {"content-type": "application/json", "x-goog-api-key": cls.key()}, timeout)
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("error", {}).get("message", "")
            except Exception:
                detail = "(non-JSON block page; API likely not enabled for this key)"
            raise ProviderError(f"studio {model}: HTTP {exc.code} {detail}".strip()) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"studio {model}: {exc}") from exc
        return cls._parse(data, f"studio {model}")

    @classmethod
    def _call_vertex(cls, *, system, user, model, max_output_tokens, temperature, timeout) -> dict:
        body = {
            "contents": [{"role": "user", "parts": [{"text": system + "\n\n" + user}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
                "responseMimeType": "application/json",
            },
        }
        try:
            data = _http_json(
                "https://aiplatform.googleapis.com/v1/publishers/google/models/"
                f"{model}:generateContent",
                body, {"content-type": "application/json", "x-goog-api-key": cls.key()}, timeout)
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("error", {}).get("message", "")
            except Exception:
                pass
            raise ProviderError(f"vertex {model}: HTTP {exc.code} {detail}".strip()) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"vertex {model}: {exc}") from exc
        return cls._parse(data, f"vertex {model}")

    @staticmethod
    def _parse(data: dict, label: str) -> dict:
        cands = data.get("candidates") or []
        text = ""
        if cands:
            parts = (cands[0].get("content") or {}).get("parts") or []
            text = "".join(p.get("text", "") for p in parts)
        if not text:
            reason = cands[0].get("finishReason") if cands else None
            raise ProviderError(f"{label}: empty response (finishReason={reason})")
        usage = data.get("usageMetadata") or {}
        return {"text": text,
                "usage": {"in_tokens": usage.get("promptTokenCount", 0),
                          "out_tokens": usage.get("candidatesTokenCount", 0)}}

    @classmethod
    def probe(cls) -> list[str]:
        errors = []
        try:
            data = _http_json(f"{GEMINI_BASE}/models", None, {"x-goog-api-key": cls.key()}, 20.0)
            return [m.get("name", "").replace("models/", "")
                    for m in data.get("models", [])
                    if "generateContent" in (m.get("supportedGenerationMethods") or [])]
        except Exception as exc:
            errors.append(f"studio: {exc}")
        # Vertex express: a 1-token ping is the cheapest reliable reachability test
        try:
            cls._call_vertex(system="ping", user="Reply with the single word: ok",
                             model=cls.models[0], max_output_tokens=2000,
                             temperature=0.0, timeout=20.0)
            return [f"{m} (via vertex express)" for m in cls.models]
        except Exception as exc:
            errors.append(f"vertex: {exc}")
        raise ProviderError(" | ".join(errors))


class OpenRouter:
    id = "openrouter"
    label = "OpenRouter"
    free = "conditional"
    models = env_list("FORGE_OPENROUTER_MODELS",
                      "meta-llama/llama-3.3-70b-instruct:free,"
                      "deepseek/deepseek-chat-v3-0324:free,"
                      "google/gemini-2.0-flash-exp:free,"
                      "qwen/qwen-2.5-72b-instruct:free")

    @staticmethod
    def configured() -> bool:
        return bool(os.environ.get("OPENROUTER_API_KEY"))

    @staticmethod
    def is_free_model(model: str) -> bool:
        return model.endswith(":free")

    @classmethod
    def call(cls, *, system, user, model, max_output_tokens, temperature, timeout) -> dict:
        body = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_output_tokens,
            "temperature": temperature,
        }
        try:
            data = _http_json(
                "https://openrouter.ai/api/v1/chat/completions", body,
                {"content-type": "application/json",
                 "authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}, timeout)
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = str(json.loads(exc.read().decode("utf-8")).get("error", {}).get("message", ""))
            except Exception:
                pass
            raise ProviderError(f"openrouter {model}: HTTP {exc.code} {detail}".strip()) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"openrouter {model}: {exc}") from exc

        msg = ((data.get("choices") or [{}])[0]).get("message") or {}
        text = str(msg.get("content") or "")
        if not text:
            raise ProviderError(f"openrouter {model}: empty response")
        usage = data.get("usage") or {}
        return {"text": text,
                "usage": {"in_tokens": usage.get("prompt_tokens", 0),
                          "out_tokens": usage.get("completion_tokens", 0)}}

    @classmethod
    def probe(cls) -> list[str]:
        data = _http_json("https://openrouter.ai/api/v1/models", None, {}, 20.0)
        ids = [m.get("id", "") for m in data.get("data", [])]
        return [i for i in ids if i.endswith(":free")][:40]


class OpenWork:
    id = "openwork"
    label = "OpenWork inference (org-provided)"
    free = True
    models = env_list("FORGE_OPENWORK_MODEL", "")

    @classmethod
    def configured(cls) -> bool:
        return bool(os.environ.get("OPENWORK_API_KEY") and os.environ.get("OPENWORK_INFERENCE_BASE_URL")
                    and cls.models)

    @classmethod
    def base(cls) -> str:
        return os.environ["OPENWORK_INFERENCE_BASE_URL"].rstrip("/")

    @classmethod
    def call(cls, *, system, user, model, max_output_tokens, temperature, timeout) -> dict:
        body = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_output_tokens,
            "temperature": temperature,
        }
        try:
            data = _http_json(
                f"{cls.base()}/chat/completions", body,
                {"content-type": "application/json",
                 "authorization": f"Bearer {os.environ['OPENWORK_API_KEY']}"}, timeout)
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"openwork {model}: HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"openwork {model}: {exc}") from exc

        msg = ((data.get("choices") or [{}])[0]).get("message") or {}
        text = str(msg.get("content") or "")
        if not text:
            raise ProviderError(f"openwork {model}: empty response")
        usage = data.get("usage") or {}
        out = {"text": text,
               "usage": {"in_tokens": usage.get("prompt_tokens", 0),
                         "out_tokens": usage.get("completion_tokens", 0)}}
        reported = reported_cost_usd(data)
        if reported is not None:
            out["cost_usd"] = reported
        return out


class NoKey:
    """Free, no-key chain (lib/ai_chain/sc_ai_chain.py). Optional: configured only when SC_AI=on.

    Hardening (SC Renderer review 2026-10-04): honors the engine timeout per call
    (capped at the chain's 45 s budget) and a per-build cap (SC_AI_BUILD_CAP,
    default 90 s) across plan/repair/refine; prints one stderr privacy notice the
    first time it is used in a process; pins the cache to an absolute path under
    the repo; reports which route answered ("chain:<route>") to the ledger.
    """
    id = "nokey"
    label = "SpiderCaster no-key free chain (SC_AI=on; no key)"
    free = True
    models = ["chain"]
    PER_CALL_CAP = 45.0
    _spent = 0.0          # seconds used by this process (one build = one process)
    _noticed = False

    @classmethod
    def configured(cls) -> bool:
        return os.environ.get("SC_AI", "off").strip().lower() in ("on", "1", "true", "yes")

    @classmethod
    def build_cap(cls) -> float:
        try:
            return float(os.environ.get("SC_AI_BUILD_CAP") or 90)
        except ValueError:
            return 90.0

    @classmethod
    def _module(cls):
        import sys
        for d in (os.environ.get("SC_AI_CHAIN_DIR", ""), str(Path(__file__).resolve().parent / "ai_chain")):
            if d and d not in sys.path and Path(d).is_dir():
                sys.path.append(d)
        import sc_ai_chain
        return sc_ai_chain

    @classmethod
    def call(cls, *, system, user, model, max_output_tokens, temperature, timeout) -> dict:
        import sys
        left = cls.build_cap() - cls._spent
        if left <= 1:
            raise ProviderError(f"nokey: per-build cap reached ({cls.build_cap():.0f}s, SC_AI_BUILD_CAP)")
        budget = max(1.0, min(float(timeout or DEFAULT_TIMEOUT), cls.PER_CALL_CAP, left))
        try:
            sc_ai_chain = cls._module()
        except ImportError as exc:
            raise ProviderError(f"nokey: module missing ({exc})") from exc
        if not os.environ.get("SC_AI_CACHE_DIR"):
            # absolute, repo-level cache: never lands inside a project or a built site
            os.environ["SC_AI_CACHE_DIR"] = str(Path(__file__).resolve().parent.parent / ".sc_ai_cache")
        if not cls._noticed:
            cls._noticed = True
            print("SC_AI=on: brief text is being sent to anonymous public AI endpoints "
                  "(no key; see `spidercaster models`)", file=sys.stderr)
        t0 = time.time()
        try:
            r = sc_ai_chain.generate(system, user, "", purpose="engine",
                                     max_tokens=min(int(max_output_tokens), 1500),
                                     temperature=temperature, style_check=False, max_chars=20000,
                                     budget_seconds=budget)
        finally:
            cls._spent += time.time() - t0
        if r.source != "ai":
            raise ProviderError("nokey: " + r.reason)
        return {"text": r.text, "usage": {"in_tokens": 0, "out_tokens": 0},
                "model": f"chain:{r.provider}" if r.provider else "chain", "cost_usd": 0.0}


class TokenCtr:
    """TokenCTR gateway (https://api.tokenctr.com/v1), purchased credits only.

    OpenAI-shape POST {base}/chat/completions with a Bearer key. Opt-in only:
    configured() needs TOKENCTR_API_KEY present AND SC_TOKENCTR_PAID=1. Builds
    never mint anonymous keys (they carry $0 credit and are limited per IP).
    Cost = usage tokens x SC_TOKENCTR_PRICE_PER_TOKEN (USD, config value, not a
    secret). Without a price the cost is recorded as None ("unknown"), never 0.
    TokenCTR proxies upstream to OpenRouter through its own gateway.
    """
    id = "tokenctr"
    label = "TokenCTR gateway (purchased credits; opt-in SC_TOKENCTR_PAID=1)"
    free = False
    DEFAULT_BASE = "https://api.tokenctr.com/v1"
    DEFAULT_MODEL = "mistralai/ministral-3b-2512"
    DEFAULT_CATALOG = "https://tokenctr.com/data/models.json"
    KEY_ENV = "TOKENCTR_API_KEY"
    OPT_IN_ENV = "SC_TOKENCTR_PAID"
    models = env_list("SC_TOKENCTR_MODEL", DEFAULT_MODEL)
    _catalog: list | None = None      # model ids, fetched once per process
    _catalog_tried = False

    @classmethod
    def key_present(cls) -> bool:
        return bool(os.environ.get(cls.KEY_ENV, "").strip())

    @classmethod
    def opted_in(cls) -> bool:
        return os.environ.get(cls.OPT_IN_ENV, "").strip().lower() in ("1", "on", "true", "yes")

    @classmethod
    def configured(cls) -> bool:
        return cls.key_present() and cls.opted_in()

    @classmethod
    def not_configured_reason(cls) -> str:
        if not cls.key_present():
            return f"tokenctr needs {cls.KEY_ENV} (purchased-credit key) and {cls.OPT_IN_ENV}=1"
        return (f"tokenctr is paid-only: {cls.KEY_ENV} is set but {cls.OPT_IN_ENV}=1 is not; "
                "refusing to spend purchased credits without the explicit opt-in")

    @classmethod
    def base(cls) -> str:
        return (os.environ.get("TOKENCTR_BASE_URL") or cls.DEFAULT_BASE).rstrip("/")

    @classmethod
    def price_per_token(cls):
        raw = os.environ.get("SC_TOKENCTR_PRICE_PER_TOKEN", "").strip()
        if not raw:
            return None
        try:
            v = float(raw)
        except ValueError:
            return None
        return v if v >= 0 else None

    @classmethod
    def catalog_ids(cls):
        """Model ids from the public catalog (no auth), or None if unreachable/disabled."""
        if os.environ.get("SC_TOKENCTR_VALIDATE", "1").strip().lower() in ("0", "off", "false", "no"):
            return None
        if not cls._catalog_tried:
            cls._catalog_tried = True
            try:
                data = _http_json(os.environ.get("SC_TOKENCTR_CATALOG_URL") or cls.DEFAULT_CATALOG,
                                  None, {"user-agent": "SpiderCaster/0.1 (+catalog check)"}, 8.0)
                rows = data.get("data") or data.get("models") if isinstance(data, dict) else data
                cls._catalog = [str(m.get("id", "")) for m in (rows or []) if isinstance(m, dict)]
            except Exception:
                cls._catalog = None
        return cls._catalog

    @staticmethod
    def _error_code(exc: urllib.error.HTTPError) -> str:
        try:
            return str((json.loads(exc.read().decode("utf-8")).get("error") or {}).get("code") or "")
        except Exception:
            return ""

    @classmethod
    def call(cls, *, system, user, model, max_output_tokens, temperature, timeout) -> dict:
        if not cls.configured():
            raise ProviderError("tokenctr: " + cls.not_configured_reason())
        ids = cls.catalog_ids()
        if ids and model not in ids:
            raise ProviderError(f"tokenctr {model}: not in the TokenCTR catalog (set SC_TOKENCTR_MODEL)")
        body = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_output_tokens,
            "temperature": temperature,
        }
        try:
            data = _http_json(
                f"{cls.base()}/chat/completions", body,
                {"content-type": "application/json",
                 "authorization": f"Bearer {os.environ[cls.KEY_ENV].strip()}"}, timeout)
        except urllib.error.HTTPError as exc:
            code = cls._error_code(exc)
            if exc.code == 429 and code in ("quota_exhausted", ""):
                raise ProviderError(f"tokenctr {model}: no_credit (HTTP 429 quota_exhausted: "
                                    "free daily capacity is $0; buy credits or fall back)") from exc
            if exc.code == 402:
                raise ProviderError(f"tokenctr {model}: no_balance (HTTP 402 {code or 'insufficient_credits'}: "
                                    "purchased balance is empty)") from exc
            if exc.code == 401:
                raise ProviderError(f"tokenctr {model}: bad_key (HTTP 401; check {cls.KEY_ENV})") from exc
            if exc.code == 503 and code == "no_supply":
                raise ProviderError(f"tokenctr {model}: model not in the registry (HTTP 503)") from exc
            raise ProviderError(f"tokenctr {model}: HTTP {exc.code} {code}".strip()) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"tokenctr {model}: {exc}") from exc

        msg = ((data.get("choices") or [{}])[0]).get("message") or {}
        text = str(msg.get("content") or "")
        if not text:
            raise ProviderError(f"tokenctr {model}: empty response")
        usage = data.get("usage") or {}
        in_t = int(usage.get("prompt_tokens") or 0)
        out_t = int(usage.get("completion_tokens") or 0)
        reported = reported_cost_usd(data)
        price = cls.price_per_token()
        if reported is not None:
            cost, src = reported, "response"
        elif price is not None and (in_t or out_t):
            cost, src = (in_t + out_t) * price, "usage x SC_TOKENCTR_PRICE_PER_TOKEN"
        else:
            cost, src = None, "unknown"
        return {"text": text, "usage": {"in_tokens": in_t, "out_tokens": out_t},
                "cost_usd": cost, "cost_source": src, "tier": "paid"}

    @classmethod
    def usage_today(cls) -> dict:
        """GET {base}/usage/today (no spend) for reconciling the ledger with the gateway meter."""
        if not cls.configured():
            raise ProviderError("tokenctr: " + cls.not_configured_reason())
        try:
            return _http_json(f"{cls.base()}/usage/today", None,
                              {"authorization": f"Bearer {os.environ[cls.KEY_ENV].strip()}"}, 20.0)
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"tokenctr usage/today: HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"tokenctr usage/today: {exc}") from exc

    @classmethod
    def probe(cls) -> list[str]:
        ids = cls.catalog_ids()
        if ids is None:
            raise ProviderError("catalog unreachable or SC_TOKENCTR_VALIDATE=0")
        want = cls.models[0]
        return [f"catalog has {len(ids)} models; {want} {'listed' if want in ids else 'NOT listed'}"]


def reported_cost_usd(data: dict):
    """USD cost a gateway put in its reply (usage.cost / usage.total_cost / cost), else None."""
    usage = data.get("usage") or {}
    for v in (usage.get("cost"), usage.get("total_cost"), usage.get("cost_usd"), data.get("cost")):
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0:
            return float(v)
    return None


PROVIDERS = {"gemini": Gemini, "openrouter": OpenRouter, "openwork": OpenWork, "nokey": NoKey,
             "tokenctr": TokenCtr}
DEFAULT_ORDER = ["gemini", "openrouter", "openwork", "nokey", "tokenctr"]   # free/no-key before paid

# Rough per-1M-token list prices for known paid fallbacks (approximate).
PAID_PRICING = {
    "meta-llama/llama-3.3-70b-instruct": {"in": 0.72, "out": 0.72},
    "deepseek/deepseek-chat": {"in": 0.14, "out": 0.28},
    "qwen/qwen-2.5-72b-instruct": {"in": 0.35, "out": 0.40},
}


def estimate_cost(provider_id: str, model: str, in_tokens: int, out_tokens: int):
    """USD estimate when the reply carried no cost. None means unknown (never booked as $0)."""
    if provider_id in ("gemini", "nokey"):
        return 0.0
    if provider_id == "openwork":
        raw = os.environ.get("SC_OPENWORK_PRICE_PER_TOKEN", "").strip()
        try:
            return (in_tokens + out_tokens) * float(raw) if raw else None
        except ValueError:
            return None
    if provider_id == "tokenctr":
        price = TokenCtr.price_per_token()
        return None if price is None else (in_tokens + out_tokens) * price
    if provider_id == "openrouter":
        if model.endswith(":free"):
            return 0.0
        base = model.split(":")[0]
        p = PAID_PRICING.get(base)
        if not p:
            return None
        return (in_tokens / 1e6) * p["in"] + (out_tokens / 1e6) * p["out"]
    return None


def tier_of(provider_id: str, model: str) -> str:
    if provider_id in ("gemini", "nokey"):
        return "free"
    if provider_id == "openrouter":
        return "free" if model.endswith(":free") else "paid"
    if provider_id == "tokenctr":
        return "paid"
    return "unknown"          # openwork: org-provided, may be purchased credit


def resolve_chain(opts: dict) -> list[dict]:
    """Ordered candidate list: (provider_class, model). Free/no-key routes come before paid."""
    chain: list[dict] = []
    forced = opts.get("provider")
    order = [forced] if forced else list(DEFAULT_ORDER)
    if forced == "tokenctr" and NoKey.configured():
        order.append("nokey")          # clean fallback when credit/balance is empty
    for pid in order:
        p = PROVIDERS.get(pid)
        if p is None:
            raise SystemExit(f"unknown provider '{pid}'; known: {', '.join(PROVIDERS)}")
        if forced == pid and not p.configured():
            if pid == "nokey":
                raise SystemExit("provider 'nokey' needs SC_AI=on (no key required)")
            if pid == "tokenctr":
                raise SystemExit("provider 'tokenctr': " + TokenCtr.not_configured_reason())
            raise SystemExit(f"provider '{pid}' is not configured (check its API key env var)")
        if not p.configured():
            continue
        if pid == "tokenctr" and not forced and not opts.get("allow_paid"):
            continue                   # purchased credits never join the auto chain without --allow-paid
        models = [opts["model"]] if opts.get("model") else p.models
        if pid == "openrouter" and not opts.get("allow_paid"):
            models = [m for m in models if p.is_free_model(m)]
        for model in models:
            chain.append({"provider": p, "model": model})
    return chain


def complete(*, system: str, user: str, opts: dict, ledger: Ledger, purpose: str,
             temperature: float = 0.8) -> dict:
    """Walk the chain until one provider returns text. Records every attempt."""
    chain = resolve_chain(opts)
    if not chain:
        raise SystemExit(
            "no AI provider configured; set GEMINI_API_KEY (free tier) or OPENROUTER_API_KEY, "
            "or SC_AI=on for the free no-key chain, or run with --offline for a zero-token build")
    errors = []
    for cand in chain:
        t0 = time.time()
        try:
            r = cand["provider"].call(
                system=system, user=user, model=cand["model"],
                max_output_tokens=int(opts.get("max_tokens") or 8192),
                temperature=temperature,
                timeout=float(opts.get("timeout") or DEFAULT_TIMEOUT))
            if "cost_usd" in r:        # provider measured it (reply field or usage x price); None = unknown
                cost = r["cost_usd"]
            else:
                cost = estimate_cost(cand["provider"].id, cand["model"],
                                     r["usage"]["in_tokens"], r["usage"]["out_tokens"])
            entry = dict(provider=cand["provider"].id, model=r.get("model") or cand["model"],
                         purpose=purpose, ok=True, error="", ms=int((time.time() - t0) * 1000),
                         est_cost_usd=cost, **r["usage"])
            entry["tier"] = r.get("tier") or tier_of(cand["provider"].id, cand["model"])
            if cost is None:
                entry["cost"] = "unknown"
            if r.get("cost_source"):
                entry["cost_source"] = r["cost_source"]
            key_file = os.environ.get("FORGE_GEMINI_KEY_FILE")
            if cand["provider"].id == "gemini" and key_file:
                # credit-backed draw: record WHICH wallet paid (name only, never values)
                entry["draw"] = Path(key_file).name
                entry["note"] = "draws wallet credit at vendor list rates; est_cost reflects free tier only"
            ledger.add(**entry)
            return {"text": r["text"], "provider": cand["provider"].id,
                    "model": r.get("model") or cand["model"]}
        except ProviderError as exc:
            ledger.add(provider=cand["provider"].id, model=cand["model"], purpose=purpose,
                       ok=False, error=str(exc), ms=int((time.time() - t0) * 1000),
                       in_tokens=0, out_tokens=0, est_cost_usd=0.0)
            errors.append(f"{cand['provider'].id}/{cand['model']}: {exc}")
    raise RuntimeError("all providers failed:\n  " + "\n  ".join(errors))


def extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model reply (handles fences/prose)."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n?```\s*$", "", t)
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object found in reply")
    return json.loads(t[start:end + 1])
