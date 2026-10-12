"""SpiderCaster optional AI path: free, no-key provider chain with template fallback.

Stdlib only. AI is OFF unless SC_AI=on. Every failure (off, offline, timeout,
HTTP error, rate limit, bad output) returns the caller's template result with a
logged reason. generate() never raises.

Route order: the free no-key chain first, then an OPT-IN OpenRouter route that
exists only when the operator provided OPENROUTER_API_KEY (or a file path in
OPENROUTER_API_KEY_FILE) and SC_AI=on. The key is read in-process at call time
and never appears in logs, cache files, or results. Config files still cannot
carry keys (fleet lock). With no key the default stays zero-token: the template
fallback is used with a logged reason.

Drop-in:
    from sc_ai_chain import generate
    r = generate(system=SYS, user=USER, fallback=lambda: template_text, purpose="hero")
    text = r.text          # AI text, or the fallback text
    r.source               # "ai" | "template"
    r.reason               # why the template was used ("" when source == "ai")
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Union

log = logging.getLogger("sc_ai_chain")

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "provider_chain.json"
USER_AGENT = "SpiderCaster-AI/1 (+static-site engine; anonymous, public text only)"

# Config-supplied routes may never carry keys or touch keyed/banned providers
# (fleet lock). The opt-in OpenRouter route below is code-built, not config, and
# is exempt: it reads the operator's key from env/file at call time.
FORBIDDEN_HOST_PARTS = ("openrouter", "x.ai", "grok", "aiplatform.googleapis", "generativelanguage.googleapis")
ALLOWED_BEARER = ("", "unused")

# Output that is really an error page / refusal / leaked markup, not copy.
BAD_OUTPUT_PATTERNS = [
    r"reached its budget", r"raise the key budget", r"api key", r"unauthori[sz]ed", r"rate limit",
    r"too many requests", r"error code", r"\"error\"\s*:", r"\bENOSPC\b", r"insufficient (funds|balance|credits)",
    r"payment required", r"as an ai language model", r"i (can('|’)t|cannot) (help|assist) with",
    r"<\s*(html|body|script|div|head)\b", r"<\|", r"<\s*/?think", r"^\s*(the user|okay, the user|we need to|let me think)\b", r"\[/?INST\]", r"^```", r"</?s>",
]
_BAD_RE = re.compile("|".join(BAD_OUTPUT_PATTERNS), re.I | re.M)

# Keith's style rules (used by style_issues / style_check=True).
BANNED_PHRASES = [
    "in conclusion", "furthermore", "moreover", "it is important to remember", "delve", "testament",
    "beacon", "nestled", "rich tapestry", "crucial", "vital", "in summary",
]
_SECRET_SHAPES = [
    re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}"), re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}", re.I),
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*\S{8,}"),
]


class RouteError(Exception):
    """One route failed. .kind is a short machine reason; .retry says if one retry is sensible."""

    def __init__(self, kind: str, detail: str = "", retry: bool = False):
        super().__init__(f"{kind}: {detail}" if detail else kind)
        self.kind, self.detail, self.retry = kind, detail, retry


@dataclass
class AIResult:
    text: str
    source: str                      # "ai" | "template"
    provider: str = ""
    model: str = ""
    reason: str = ""                 # fallback reason, empty on ai
    ms: int = 0
    cached: bool = False
    attempts: list = field(default_factory=list)   # [(provider, outcome)] for the log
    usage: dict = field(default_factory=dict)      # {"in_tokens": n, "out_tokens": n} (OpenRouter only)


# ----------------------------------------------------------------------------- config

def mode_enabled(env=None) -> bool:
    env = os.environ if env is None else env
    return str(env.get("SC_AI", "off")).strip().lower() in ("on", "1", "true", "yes")


def load_config(env=None) -> dict:
    """Config = JSON file (SC_AI_CONFIG or the bundled one), then env overrides. URLs/ids only."""
    env = os.environ if env is None else env
    path = Path(env.get("SC_AI_CONFIG") or DEFAULT_CONFIG)
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # unreadable config must not break a build
        log.warning("sc_ai: config unreadable (%s); AI path has no routes", type(exc).__name__)
        cfg = {"providers": []}
    provs = {p["id"]: dict(p) for p in cfg.get("providers", []) if isinstance(p, dict) and p.get("id")}
    order = [p["id"] for p in cfg.get("providers", []) if isinstance(p, dict) and p.get("id")]
    routes = env.get("SC_AI_ROUTES")          # e.g. "llm7,chat-at"  (order + allow-list)
    if routes:
        order = [r.strip() for r in routes.split(",") if r.strip()]
    for pid in list(provs):                   # SC_AI_URL_LLM7=https://... (URL override only)
        override = env.get("SC_AI_URL_" + re.sub(r"\W", "_", pid).upper())
        if override:
            provs[pid]["url"] = override
    if env.get("SC_AI_TIMEOUT"):
        try:
            for p in provs.values():
                p["timeout"] = float(env["SC_AI_TIMEOUT"])
        except ValueError:
            pass
    out = []
    for pid in order:
        p = provs.get(pid)
        if p and p.get("enabled", True):
            out.append(p)
    return {
        "providers": out,
        "budget_seconds": float(env.get("SC_AI_BUDGET") or cfg.get("budget_seconds") or 45),
        "cache_dir": env.get("SC_AI_CACHE_DIR") or cfg.get("cache_dir") or ".sc_ai_cache",
    }


def route_problem(p: dict) -> str:
    """Return why a route is refused (keys, banned hosts), or ''. Enforces the no-keys rule."""
    url = str(p.get("url", ""))
    low = url.lower()
    if not low.startswith(("http://127.0.0.1", "http://localhost", "https://")):
        return "url must be https (or local ollama)"
    if any(h in low for h in FORBIDDEN_HOST_PARTS):
        return "forbidden host (keyed or banned provider)"
    if str(p.get("bearer", "")) not in ALLOWED_BEARER:
        return "bearer must be empty or the literal 'unused'; keys are never allowed"
    for k in p:
        if k.lower() in ("api_key", "apikey", "key", "token", "secret", "authorization", "headers"):
            return f"field '{k}' not allowed (no keys in config)"
    return ""


# ----------------------------------------------------------------------------- helpers

def redact(text: str) -> str:
    for rx in _SECRET_SHAPES:
        text = rx.sub("[redacted]", text)
    return text


def style_issues(text: str) -> list[str]:
    """Keith's copy rules that can be checked mechanically."""
    issues = []
    low = text.lower()
    for w in BANNED_PHRASES:
        if re.search(r"\b" + re.escape(w) + r"\b", low):
            issues.append(f"banned phrase: {w}")
    if "!" in text:
        issues.append("exclamation point")
    return issues


def sanity(text: str, *, system: str = "", min_chars: int = 20, max_chars: int = 6000,
           style_check: bool = False) -> str:
    """Return '' if the text is usable copy, else the reason it is not."""
    t = (text or "").strip()
    if not t:
        return "empty output"
    if len(t) < min_chars:
        return f"too short ({len(t)} < {min_chars})"
    if len(t) > max_chars:
        return f"too long ({len(t)} > {max_chars})"
    if _BAD_RE.search(t):
        return "error text or markup in output"
    probe = re.sub(r"\s+", " ", system or "").strip()[:60]
    if len(probe) >= 40 and probe.lower() in re.sub(r"\s+", " ", t).lower():
        return "prompt leaked into output"
    if style_check:
        bad = style_issues(t)
        if bad:
            return "style: " + "; ".join(bad[:3])
    return ""


def cache_key(provider_id: str, model: str, system: str, user: str, settings: dict) -> str:
    blob = json.dumps([provider_id, model, system, user, settings], sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- transports

def _http(req: urllib.request.Request, timeout: float) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:   # noqa: S310 (https/local only, checked)
            return r.status, r.read(400_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        code = exc.code
        retry = code >= 500 and code != 501
        kind = "rate_limited" if code == 429 else f"http_{code}"
        raise RouteError(kind, "", retry=retry) from None
    except (TimeoutError, urllib.error.URLError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        is_to = isinstance(exc, TimeoutError) or "timed out" in str(reason).lower()
        refused = isinstance(reason, ConnectionRefusedError)
        raise RouteError("timeout" if is_to else "unreachable", type(reason).__name__, retry=not refused) from None


def _call_openai(p: dict, system: str, user: str, max_tokens: int, temperature: float, timeout: float):
    body = {"model": p.get("model") or "default", "max_tokens": max_tokens, "temperature": temperature,
            "messages": ([{"role": "system", "content": system}] if system else []) +
                        [{"role": "user", "content": user}]}
    headers = {"Content-Type": "application/json", "User-Agent": USER_AGENT}
    if p.get("bearer"):
        headers["Authorization"] = "Bearer " + p["bearer"]    # literal 'unused' only (route_problem)
    req = urllib.request.Request(p["url"], json.dumps(body).encode(), headers, method="POST")
    _, raw = _http(req, timeout)
    try:
        data = json.loads(raw)
        text = data["choices"][0]["message"]["content"]
        model = data.get("model") or body["model"]
    except Exception:
        raise RouteError("bad_json", "not an OpenAI-style reply") from None
    return text, model


def _call_ollama(p: dict, system: str, user: str, max_tokens: int, temperature: float, timeout: float):
    base = p["url"].rstrip("/")
    model = p.get("model") or os.environ.get("SC_AI_OLLAMA_MODEL", "")
    if not model:
        _, raw = _http(urllib.request.Request(base + "/api/tags", headers={"User-Agent": USER_AGENT}), min(timeout, 3))
        try:
            model = json.loads(raw)["models"][0]["name"]
        except Exception:
            raise RouteError("not_installed", "no local model") from None
    body = {"model": model, "stream": False, "options": {"temperature": temperature, "num_predict": max_tokens},
            "messages": ([{"role": "system", "content": system}] if system else []) +
                        [{"role": "user", "content": user}]}
    req = urllib.request.Request(base + "/api/chat", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "User-Agent": USER_AGENT}, method="POST")
    _, raw = _http(req, timeout)
    try:
        return json.loads(raw)["message"]["content"], model
    except Exception:
        raise RouteError("bad_json", "not an ollama reply") from None


def _call_get_q(p: dict, system: str, user: str, max_tokens: int, temperature: float, timeout: float):
    prompt = (system + "\n\n" if system else "") + user
    if len(prompt) > int(p.get("max_prompt_chars", 1500)):
        raise RouteError("prompt_too_long", "GET route")
    url = p["url"] + ("&" if "?" in p["url"] else "?") + urllib.parse.urlencode({p.get("param", "q"): prompt})
    _, raw = _http(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout)
    m = re.search(r"^A:\s*(.*)\Z", raw, re.S | re.M)       # ch.at replies "Q: ...\nA: ..."
    return (m.group(1) if m else raw), p.get("model", "chat-at")


# ----------------------------------------------------------------------------- opt-in OpenRouter route
# Appended AFTER the free chain, built only when SC_AI=on and a key is present.
# The key travels one Authorization header and is never logged, cached, or
# stored on the route dict (resolved at call time in Chain._try_route).

OR_URL = "https://openrouter.ai/api/v1/chat/completions"
OR_MODEL_PIN = "deepseek/deepseek-chat"   # cheapest paid pin in lib/providers.py PAID_PRICING

# Per-1M-token list prices for the pinned models (approximate, mirrors providers.py).
_OR_PRICING = {
    "deepseek/deepseek-chat": {"in": 0.14, "out": 0.28},
    "meta-llama/llama-3.3-70b-instruct": {"in": 0.72, "out": 0.72},
    "qwen/qwen-2.5-72b-instruct": {"in": 0.35, "out": 0.40},
}


def _openrouter_key(env=None) -> str:
    """Operator key only: env var wins, else first non-blank line of the file."""
    env = os.environ if env is None else env
    key = str(env.get("OPENROUTER_API_KEY") or "").strip().strip('"').strip("'")
    if key:
        return key
    path = str(env.get("OPENROUTER_API_KEY_FILE") or "").strip()
    if not path:
        return ""
    try:
        for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip().strip('"').strip("'")
            if line and not line.startswith("#"):
                return line
    except OSError:
        return ""
    return ""


def _openrouter_model(env=None) -> str:
    env = os.environ if env is None else env
    return str(env.get("SC_AI_OR_MODEL") or "").strip() or OR_MODEL_PIN


def _openrouter_route(env=None) -> Optional[dict]:
    """Code-built route dict (no key on it), or None when it must not run."""
    env = os.environ if env is None else env
    if not mode_enabled(env):
        return None
    if not _openrouter_key(env):
        return None
    routes = str(env.get("SC_AI_ROUTES") or "").strip()
    if routes and "openrouter" not in [r.strip() for r in routes.split(",") if r.strip()]:
        return None
    timeout = 25.0
    try:
        if env.get("SC_AI_TIMEOUT"):
            timeout = float(env["SC_AI_TIMEOUT"])
    except ValueError:
        pass
    return {"id": "openrouter", "kind": "openrouter", "enabled": True, "url": OR_URL,
            "model": _openrouter_model(env), "timeout": timeout, "retries": 0,
            "note": "opt-in keyed route; key from env/file only, never config"}


def _call_openrouter(p: dict, system: str, user: str, max_tokens: int, temperature: float,
                     timeout: float, key: str = ""):
    if not key:
        raise RouteError("no_key", "OPENROUTER_API_KEY is not set")
    model = p.get("model") or OR_MODEL_PIN
    body = {"model": model, "max_tokens": max_tokens, "temperature": temperature,
            "messages": ([{"role": "system", "content": system}] if system else []) +
                        [{"role": "user", "content": user}]}
    headers = {"Content-Type": "application/json", "User-Agent": USER_AGENT,
               "Authorization": "Bearer " + key, "HTTP-Referer": "https://spidercaster.local",
               "X-Title": "SpiderCaster copy"}
    req = urllib.request.Request(p.get("url") or OR_URL, json.dumps(body).encode(),
                                 headers, method="POST")
    try:
        _, raw = _http(req, timeout)
    except RouteError as exc:
        if exc.kind == "http_402":
            raise RouteError("http_402", "key out of credit") from None
        if exc.kind == "http_401":
            raise RouteError("http_401", "key rejected") from None
        raise
    try:
        data = json.loads(raw)
        text = data["choices"][0]["message"]["content"]
        used = data.get("model") or model
        raw_usage = data.get("usage") or {}
    except Exception:
        raise RouteError("bad_json", "not an OpenRouter reply") from None
    p["usage"] = {"in_tokens": int(raw_usage.get("prompt_tokens") or 0),
                  "out_tokens": int(raw_usage.get("completion_tokens") or 0)}
    return text, used


def _estimate_or_cost(provider: str, model: str, usage: dict):
    """Rough USD for a finished call, or None when the model is unpriced."""
    if provider != "openrouter" or not usage:
        return 0.0
    base = str(model or "").split(":")[0]
    price = _OR_PRICING.get(base)
    if not price:
        return None
    return (int(usage.get("in_tokens") or 0) / 1e6) * price["in"] + \
        (int(usage.get("out_tokens") or 0) / 1e6) * price["out"]


TRANSPORTS = {"openai": _call_openai, "ollama": _call_ollama, "get_q": _call_get_q,
              "openrouter": _call_openrouter}


# ----------------------------------------------------------------------------- chain

class Chain:
    """Provider chain. Dead routes are skipped for the rest of the process (circuit breaker)."""

    def __init__(self, env=None, sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.monotonic, transports: Optional[dict] = None):
        self.env = os.environ if env is None else env
        self.sleep, self.clock = sleep, clock
        self.transports = transports or TRANSPORTS
        self.dead: dict[str, str] = {}

    def _try_route(self, p, system, user, max_tokens, temperature, deadline):
        fn = self.transports.get(p.get("kind"))
        if fn is None:
            raise RouteError("unknown_kind", str(p.get("kind")))
        tries = 1 + max(0, min(1, int(p.get("retries", 0))))    # at most 1 retry
        last = None
        extra: dict = {}
        if p.get("kind") == "openrouter":                       # key resolved here so it
            key = _openrouter_key(self.env)                     # never sits on the route dict
            if not key:
                raise RouteError("no_key", "OPENROUTER_API_KEY is not set")
            extra["key"] = key
        for i in range(tries):
            left = deadline - self.clock()
            if left <= 1:
                raise RouteError("budget_exhausted")
            try:
                return fn(p, system, user, max_tokens, temperature, min(float(p.get("timeout", 20)), left),
                          **extra)
            except RouteError as exc:
                last = exc
                if not exc.retry or i == tries - 1:
                    raise
                self.sleep(1.0 * (2 ** i))                      # backoff
        raise last  # pragma: no cover

    def run(self, system, user, *, purpose="", max_tokens=700, temperature=0.7, min_chars=20,
            max_chars=6000, style_check=False, use_cache=True) -> AIResult:
        cfg = load_config(self.env)
        t0 = self.clock()
        deadline = t0 + cfg["budget_seconds"]
        attempts: list = []
        safe_user, safe_sys = redact(user), redact(system)      # public text only; strip secret shapes
        settings = {"mt": max_tokens, "t": temperature, "sc": style_check}
        cache_dir = Path(cfg["cache_dir"])
        providers = list(cfg["providers"])
        or_route = _openrouter_route(self.env)                  # free chain first; opt-in keyed route last
        if or_route is not None:
            providers.append(or_route)
        for p in providers:
            pid = p["id"]
            bad = "" if p.get("kind") == "openrouter" else route_problem(p)
            if bad:
                attempts.append((pid, "refused: " + bad)); continue
            if pid in self.dead:
                attempts.append((pid, "skipped: " + self.dead[pid])); continue
            key = cache_key(pid, p.get("model", ""), safe_sys, safe_user, settings)
            cfile = cache_dir / f"{key}.json"
            if use_cache and cfile.is_file():
                try:
                    c = json.loads(cfile.read_text(encoding="utf-8"))
                    if not sanity(c["text"], system=safe_sys, min_chars=min_chars, max_chars=max_chars,
                                  style_check=style_check):
                        attempts.append((pid, "cache hit"))
                        return AIResult(c["text"], "ai", pid, c.get("model", ""), "", 0, True, attempts,
                                        dict(c.get("usage") or {}))
                except Exception:
                    pass
            s = self.clock()
            try:
                text, model = self._try_route(p, safe_sys, safe_user, max_tokens, temperature, deadline)
                text = (text or "").strip()
                why = sanity(text, system=safe_sys, min_chars=min_chars, max_chars=max_chars,
                             style_check=style_check)
                if why:
                    raise RouteError("bad_output", why)
            except RouteError as exc:
                attempts.append((pid, str(exc)))
                if exc.kind in ("unreachable", "not_installed", "rate_limited", "bad_json") or \
                        exc.kind.startswith("http_4") or exc.kind == "timeout":
                    self.dead[pid] = exc.kind
                log.info("sc_ai: %s failed (%s) %dms purpose=%s", pid, exc.kind, int((self.clock() - s) * 1000), purpose)
                if exc.kind == "budget_exhausted":
                    break
                continue
            except Exception as exc:                            # a bug in a transport must not break a build
                attempts.append((pid, f"error: {type(exc).__name__}"))
                self.dead[pid] = "error"
                continue
            ms = int((self.clock() - s) * 1000)
            log.info("sc_ai: %s ok %dms purpose=%s", pid, ms, purpose)   # id + duration only, never the prompt
            usage = dict(p.get("usage") or {})                          # OpenRouter token counts; never the key
            if use_cache:
                try:
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    cfile.write_text(json.dumps({"text": text, "model": model, "provider": pid,
                                                 "usage": usage}), encoding="utf-8")
                except OSError:
                    pass
            attempts.append((pid, "ok"))
            return AIResult(text, "ai", pid, model, "", ms, False, attempts, usage)
        why = "; ".join(f"{a}={b}" for a, b in attempts) or "no routes configured"
        return AIResult("", "template", reason="all routes failed: " + why, attempts=attempts)


_default_chain: Optional[Chain] = None


def generate(system: str, user: str, fallback: Union[str, Callable[[], str]] = "", *, purpose: str = "",
             chain: Optional[Chain] = None, **opts) -> AIResult:
    """Optional AI text with guaranteed template fallback. Never raises."""
    global _default_chain

    def template(reason: str, attempts=None) -> AIResult:
        try:
            txt = fallback() if callable(fallback) else fallback
        except Exception as exc:                                # the caller's own template is the last resort
            txt = ""
            reason += f" (fallback raised {type(exc).__name__})"
        log.warning("sc_ai: using template (%s) purpose=%s", reason, purpose)
        return AIResult(txt, "template", reason=reason, attempts=attempts or [])

    try:
        env = chain.env if chain else os.environ
        if not mode_enabled(env):
            return template("SC_AI is off")
        if chain is None:
            _default_chain = _default_chain or Chain()
            chain = _default_chain
        r = chain.run(system, user, purpose=purpose, **opts)
        if r.source == "ai":
            return r
        return template(r.reason, r.attempts)
    except Exception as exc:
        return template(f"chain error {type(exc).__name__}")


def complete(*, system: str, user: str, opts: Optional[dict] = None, ledger=None, purpose: str = "",
             temperature: float = 0.8) -> dict:
    """Same call shape as lib/providers.complete(); raises RuntimeError if AI unavailable so the
    engine's existing 'AI failed -> offline/template' branch takes over."""
    opts = opts or {}
    r = generate(system, user, "", purpose=purpose, temperature=temperature,
                 max_tokens=int(opts.get("max_tokens") or 700))
    if r.source != "ai":
        raise RuntimeError("AI unavailable: " + r.reason)
    if ledger is not None:
        try:
            usage = dict(r.usage or {})
            ledger.add(provider=r.provider, model=r.model, purpose=purpose, ok=True, error="", ms=r.ms,
                       est_cost_usd=_estimate_or_cost(r.provider, r.model, usage) or 0.0,
                       in_tokens=int(usage.get("in_tokens") or 0),
                       out_tokens=int(usage.get("out_tokens") or 0))
        except Exception:
            pass
    return {"text": r.text, "provider": r.provider, "model": r.model}


# ----------------------------------------------------------------------------- deterministic fallbacks
# Rule-based results built from the page's own text. They never invent facts and never fail.

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


def fallback_summary(text: str, max_chars: int = 200) -> str:
    """First whole sentence(s) of the page text, cut at a word boundary."""
    t = _clean(text)
    if len(t) <= max_chars:
        return t
    cut = t[:max_chars]
    end = max(cut.rfind(". "), cut.rfind("? "))
    if end >= 40:
        return cut[:end + 1]
    return cut[:cut.rfind(" ")].rstrip(" ,;:") + "." if " " in cut else cut


def fallback_meta_description(title: str, text: str, max_chars: int = 155) -> str:
    s = fallback_summary(text, max_chars) or _clean(title)
    return s[:max_chars].rstrip()


def fallback_slug(title: str, max_words: int = 4) -> str:
    stop = {"a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "how", "is", "are", "your"}
    words = [w for w in re.findall(r"[a-z0-9]+", (title or "").lower()) if w not in stop]
    return "-".join(words[:max_words]) or "page"


def fallback_alt_text(title: str, caption: str = "") -> str:
    return _clean(caption) or _clean(title)


def detect_ollama(url: str = "http://127.0.0.1:11434", timeout: float = 2.0) -> dict:
    """Report whether a local Ollama is installed and running, without sending any prompt."""
    try:
        _, raw = _http(urllib.request.Request(url.rstrip("/") + "/api/tags", headers={"User-Agent": USER_AGENT}), timeout)
        names = [m.get("name", "") for m in json.loads(raw).get("models", [])]
        return {"state": "running", "models": names}
    except RouteError as exc:
        return {"state": "not_running", "reason": exc.kind, "models": []}
    except Exception:
        return {"state": "not_running", "reason": "error", "models": []}
