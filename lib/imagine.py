"""Prompt an image provider and save a local file.

The page never receives a provider URL. xAI is the SGH Console account
(Grok Imagine). OpenRouter is the other prompt path. Neither publishes.
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

XAI_URL = "https://api.x.ai/v1/images/generations"
XAI_MODEL = "grok-imagine-image-2.0"
OR_URL = "https://openrouter.ai/api/v1/chat/completions"
_KEY = re.compile(r"xai-[A-Za-z0-9_\-]{8,}")


class ImagineError(Exception):
    pass


def _scrub(text: str) -> str:
    return _KEY.sub("xai-…", str(text or ""))[:240]


def _read_key(env_name: str, file_env: str, default_file: str) -> str:
    env = os.environ.get(env_name, "").strip()
    if env:
        return env
    path = Path(os.environ.get(file_env) or default_file)
    if not path.is_file():
        raise ImagineError(f"no {env_name}")
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip().strip('"').strip("'")
        if not line or line.startswith("#"):
            continue
        if env_name == "XAI_API_KEY":
            if line.startswith("xai-"):
                return line
        else:
            return line
    raise ImagineError(f"no {env_name}")


def xai_key() -> str:
    return _read_key("XAI_API_KEY", "XAI_API_KEY_FILE", r"V:\Research4\.secrets\Grok_API_Token-Key.txt")


def openrouter_key() -> str:
    return _read_key(
        "OPENROUTER_API_KEY", "OPENROUTER_API_KEY_FILE",
        r"V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt",
    )


def _post(url: str, body: dict, key: str, timeout: float) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json", "authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            payload = json.loads(exc.read().decode("utf-8", errors="replace"))
            err = payload.get("error")
            if isinstance(err, dict):
                detail = str(err.get("message") or err.get("code") or "")
            elif isinstance(err, str):
                detail = err
        except (OSError, ValueError):
            detail = ""
        raise ImagineError(_scrub(f"HTTP {exc.code} {detail}")) from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise ImagineError(_scrub(str(exc))) from exc


def _bytes_from_xai(data: dict) -> tuple[bytes, str]:
    rows = data.get("data") if isinstance(data, dict) else None
    row = rows[0] if isinstance(rows, list) and rows else {}
    if not isinstance(row, dict):
        row = {}
    model = str(data.get("model") or row.get("model") or XAI_MODEL)
    b64 = row.get("b64_json")
    if isinstance(b64, str) and b64:
        return base64.b64decode(b64), model
    url = row.get("url")
    if isinstance(url, str) and url.startswith("https://"):
        with urllib.request.urlopen(url, timeout=60) as res:
            return res.read(), model
    raise ImagineError("image response had no local bytes")


def _bytes_from_openrouter(data: dict) -> tuple[bytes, str]:
    model = str(data.get("model") or "")
    choices = data.get("choices") if isinstance(data, dict) else None
    message = {}
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        message = choices[0].get("message") or {}
    images = message.get("images") if isinstance(message, dict) else None
    if not isinstance(images, list) or not images:
        raise ImagineError("openrouter response had no image")
    image = images[0] if isinstance(images[0], dict) else {}
    url = ""
    nested = image.get("image_url")
    if isinstance(nested, dict):
        url = str(nested.get("url") or "")
    elif isinstance(image.get("url"), str):
        url = image["url"]
    if url.startswith("data:image") and "," in url:
        return base64.b64decode(url.split(",", 1)[1]), model or "openrouter"
    raise ImagineError("openrouter image was not a data url")


def generate(
    prompt: str,
    dest: Path,
    *,
    provider: str = "xai",
    model: str = "",
    aspect_ratio: str = "16:9",
    quality: str = "low",
    timeout: float = 120.0,
) -> dict:
    """Save one PNG. The receipt has no key and no provider URL."""
    text = " ".join(str(prompt or "").split())
    if len(text) < 8:
        raise ImagineError("prompt is too short")
    if len(text) > 2000:
        raise ImagineError("prompt is too long")
    dest = Path(dest)
    if dest.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        dest = dest.with_suffix(".png")
    provider = provider.strip().lower()
    if provider == "xai":
        body = {
            "model": model or XAI_MODEL,
            "prompt": text,
            "n": 1,
            "response_format": "b64_json",
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "resolution": "1k",
        }
        payload = _post(XAI_URL, body, xai_key(), timeout)
        raw, used = _bytes_from_xai(payload)
    elif provider == "openrouter":
        body = {
            "model": model or "google/gemini-2.5-flash-image",
            "messages": [{"role": "user", "content": text}],
            "modalities": ["image", "text"],
        }
        payload = _post(OR_URL, body, openrouter_key(), timeout)
        raw, used = _bytes_from_openrouter(payload)
    else:
        raise ImagineError("provider must be xai or openrouter")
    if len(raw) < 32:
        raise ImagineError("image bytes were empty")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    receipt = {
        "provider": provider,
        "model": used,
        "prompt": text,
        "file": dest.name,
        "bytes": len(raw),
        "aspect_ratio": aspect_ratio,
        "quality": quality if provider == "xai" else "",
    }
    dest.with_suffix(".json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt
