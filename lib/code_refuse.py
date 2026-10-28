"""Refuse to emit a code file. Writes nothing."""
from __future__ import annotations

from lib.ir import SECTION_TYPES

_CODE_KINDS = frozenset({"liquid", "velo", "javascript", "css", "custom_element"})
# Reviewed once. The renderer reuses these. Arbitrary css/js stays refused.
_ALLOW = frozenset({
    "motion",
    "hero-screenshot",
    "hero-split",
    "hero-full-bleed",
    "hero-collage",
    "card-plain",
    "card-raised",
    "card-band",
    "texture-mesh",
    "texture-dots",
    "texture-noise",
    "texture-geo",
})
_CATALOG = "the type stays in the catalog and no code file is emitted"
_KEYS = ("ok", "kind", "refused", "reason", "error")


def _row(ok: bool, kind: str, refused: bool, reason: str, error: str) -> dict:
    return {
        "ok": ok,
        "kind": kind,
        "refused": refused,
        "reason": reason,
        "error": error,
    }


def code_refuse(kind) -> dict:
    """Refuse code emission for one kind. Does not write a file."""
    if not isinstance(kind, str) or kind.strip() == "":
        shown = kind if isinstance(kind, str) else ""
        return _row(False, shown, True, "kind is empty", "empty_kind")
    text = kind.strip()
    if text in _ALLOW:
        return _row(True, text, False, "reviewed allowlist; reused, not emitted", "")
    if text in _CODE_KINDS or "http://" in text or "https://" in text:
        return _row(False, text, True, "no code file is emitted", "forbidden")
    if text in SECTION_TYPES:
        return _row(True, text, True, _CATALOG, "")
    return _row(False, text, True, "unknown kind", "unknown_kind")


def main() -> int:
    liquid = code_refuse("liquid")
    assert liquid["refused"] is True and liquid["ok"] is False
    for name in ("velo", "javascript", "css", "custom_element"):
        row = code_refuse(name)
        assert row["refused"] is True and row["ok"] is False
    for remote in ("http://example.test", "see https://example.test/x"):
        row = code_refuse(remote)
        assert row["refused"] is True and row["ok"] is False
    if "hero" in SECTION_TYPES:
        hero = code_refuse("hero")
        assert hero["refused"] is True and hero["ok"] is True
        assert "stays in the catalog" in hero["reason"]
        assert "no code file is emitted" in hero["reason"]
    else:
        raise AssertionError("hero")
    empty = code_refuse("")
    assert empty["ok"] is False and empty["refused"] is True
    blank = code_refuse("   ")
    assert blank["ok"] is False and blank["refused"] is True
    other = code_refuse("not-a-section")
    assert other["ok"] is False and other["refused"] is True
    assert other["error"] == "unknown_kind"
    motion = code_refuse("motion")
    assert motion["ok"] is True and motion["refused"] is False
    assert "allowlist" in motion["reason"]
    hero_var = code_refuse("hero-split")
    assert hero_var["ok"] is True and hero_var["refused"] is False
    for row in (liquid, empty, other, code_refuse("hero")):
        assert tuple(row) == _KEYS
    print("code_refuse selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
