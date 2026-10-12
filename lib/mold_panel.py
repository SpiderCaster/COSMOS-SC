"""Read one mold's package tokens. Does not write, download, or go live."""
from __future__ import annotations

import json
import re
from pathlib import Path

_ORIGINS = ("scratch", "mutate", "mix")
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def _fail(error: str) -> dict:
    return {
        "ok": False,
        "error": error,
        "id": None,
        "origin": None,
        "palette": None,
        "type_lead": None,
        "nav": None,
        "template": None,
        "parents": [],
    }


def _has_url(value) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return "http://" in lowered or "https://" in lowered
    if isinstance(value, dict):
        return any(_has_url(key) or _has_url(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_has_url(item) for item in value)
    return False


def _mold_file(root: Path, mold_id: str) -> Path | None:
    if not isinstance(mold_id, str) or mold_id in {"", ".", ".."}:
        return None
    if any(ch in mold_id for ch in "/\\:\0"):
        return None
    if Path(mold_id).name != mold_id:
        return None
    root_path = Path(root).resolve()
    molds = root_path / "library" / "molds"
    path = molds / f"{mold_id}.json"
    try:
        resolved = path.resolve()
        resolved.relative_to(molds.resolve())
        molds.resolve().relative_to(root_path)
    except (OSError, ValueError):
        return None
    if not resolved.is_file():
        return None
    return resolved


def mold_panel(root, mold_id, live=None) -> dict:
    """Show tokens from library/molds/<id>.json. live must stay None."""
    if live is not None:
        return _fail("live")
    path = _mold_file(Path(root), mold_id)
    if path is None:
        return _fail("missing")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _fail("bad_json")
    if not isinstance(data, dict):
        return _fail("bad_json")
    if _has_url(data):
        return _fail("url")
    origin = data.get("origin")
    if origin not in _ORIGINS:
        return _fail("origin")
    palette = data.get("palette")
    if not isinstance(palette, str) or not _HEX.fullmatch(palette):
        return _fail("palette")
    parents = data.get("parents", [])
    if parents is None:
        parents = []
    if not isinstance(parents, list) or any(not isinstance(item, str) for item in parents):
        return _fail("parents")

    def _text(key: str):
        value = data.get(key)
        return value if isinstance(value, str) else None

    return {
        "ok": True,
        "error": None,
        "id": _text("id"),
        "origin": origin,
        "palette": palette,
        "type_lead": _text("type_lead"),
        "nav": _text("nav"),
        "template": _text("template"),
        "parents": list(parents),
    }


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    shown = mold_panel(root, "warmth-authority", live=None)
    assert shown["origin"] == "scratch"
    blocked = mold_panel(root, "warmth-authority", live=True)
    assert blocked["ok"] is False
    print("mold_panel selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
