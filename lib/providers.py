"""Model provider chain: free tiers first, paid only on explicit --allow-paid.

Cost order: Gemini free tier (AI Studio key) -> OpenRouter :free models ->
OpenWork org inference. Paid OpenRouter models join the chain ONLY when
--allow-paid is passed. The ledger records token counts and env var NAMES,
never key values.
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
        return {
            "requests": len(self.attempts),
            "ok": len(ok),
            "in_tokens": sum(a.get("in_tokens", 0) for a in ok),
            "out_tokens": sum(a.get("out_tokens", 0) for a in ok),
            "est_cost_usd": round(sum(a.get("est_cost_usd") or 0 for a in ok), 6),
        }

    def summary_line(self) -> str:
        t = self.totals()
        return (f"requests={t['requests']} ok={t['ok']} "
                f"in={t['in_tokens']} out={t['out_tokens']} est_cost=${t['est_cost_usd']:.4f}")


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
        return {"text": text,
                "usage": {"in_tokens": usage.get("prompt_tokens", 0),
                          "out_tokens": usage.get("completion_tokens", 0)}}


PROVIDERS = {"gemini": Gemini, "openrouter": OpenRouter, "openwork": OpenWork}

# Rough per-1M-token list prices for known paid fallbacks (approximate).
PAID_PRICING = {
    "meta-llama/llama-3.3-70b-instruct": {"in": 0.72, "out": 0.72},
    "deepseek/deepseek-chat": {"in": 0.14, "out": 0.28},
    "qwen/qwen-2.5-72b-instruct": {"in": 0.35, "out": 0.40},
}


def estimate_cost(provider_id: str, model: str, in_tokens: int, out_tokens: int):
    if provider_id in ("gemini", "openwork"):
        return 0.0
    if provider_id == "openrouter":
        if model.endswith(":free"):
            return 0.0
        base = model.split(":")[0]
        p = PAID_PRICING.get(base)
        if not p:
            return None
        return (in_tokens / 1e6) * p["in"] + (out_tokens / 1e6) * p["out"]
    return None


def resolve_chain(opts: dict) -> list[dict]:
    """Ordered candidate list: (provider_class, model)."""
    chain: list[dict] = []
    order = [opts["provider"]] if opts.get("provider") else ["gemini", "openrouter", "openwork"]
    for pid in order:
        p = PROVIDERS.get(pid)
        if p is None:
            raise SystemExit(f"unknown provider '{pid}'; known: {', '.join(PROVIDERS)}")
        if opts.get("provider") == pid and not p.configured():
            raise SystemExit(f"provider '{pid}' is not configured (check its API key env var)")
        if not p.configured():
            continue
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
            "or run with --offline for a zero-token build")
    errors = []
    for cand in chain:
        t0 = time.time()
        try:
            r = cand["provider"].call(
                system=system, user=user, model=cand["model"],
                max_output_tokens=int(opts.get("max_tokens") or 8192),
                temperature=temperature,
                timeout=float(opts.get("timeout") or DEFAULT_TIMEOUT))
            cost = estimate_cost(cand["provider"].id, cand["model"],
                                 r["usage"]["in_tokens"], r["usage"]["out_tokens"])
            entry = dict(provider=cand["provider"].id, model=cand["model"], purpose=purpose,
                         ok=True, error="", ms=int((time.time() - t0) * 1000),
                         est_cost_usd=cost, **r["usage"])
            key_file = os.environ.get("FORGE_GEMINI_KEY_FILE")
            if cand["provider"].id == "gemini" and key_file:
                # credit-backed draw: record WHICH wallet paid (name only, never values)
                entry["draw"] = Path(key_file).name
                entry["note"] = "draws wallet credit at vendor list rates; est_cost reflects free tier only"
            ledger.add(**entry)
            return {"text": r["text"], "provider": cand["provider"].id, "model": cand["model"]}
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
