"""Prove the token contract. Run from the engine root: python lib/tokens_selftest.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.render import build_palette
from lib.tokens import (
    BODY_LEAD,
    BODY_SIZE,
    DARK_INK,
    DARK_PAPER,
    INK,
    PAD_BASE,
    PAD_WIDE,
    PAPER,
    SPACING,
    WEIGHT_CRITICAL_TARGET,
    WEIGHT_HERO_IMG,
    WEIGHT_HTML_GZIP,
    WEIGHT_HTML_RAW,
    WEIGHT_IMAGE,
    WEIGHT_SCRIPT,
    TokensError,
    contrast_ratio,
    cta_ink,
    is_token_spacing,
    mold_tokens,
    nontoken_spacings,
    resolve_mold_id,
    spacing_values,
    stack_for,
    token_css,
    validate_mold,
)


def _raises(fn, *args, **kwargs) -> None:
    try:
        fn(*args, **kwargs)
    except TokensError:
        return
    raise AssertionError(f"expected TokensError from {fn.__name__}")


def main() -> int:
    if tuple(SPACING) != (4, 8, 12, 16, 24, 32, 48, 64):
        raise SystemExit("spacing scale is not the contract steps")
    if PAD_BASE != 32 or PAD_WIDE != 48:
        raise SystemExit("section padding split is not 32/48")
    for lead in ("serif", "sans", "slab", "mono-display"):
        stack = stack_for(lead)
        if "http" in stack or "@" in stack:
            raise SystemExit(f"stack is not local: {lead}")
    _raises(stack_for, "nonsense")
    _raises(stack_for, "")
    # Ink/paper pair and the dark swap both clear body-text 4.5:1.
    if contrast_ratio(INK, PAPER) < 4.5:
        raise SystemExit("ink on paper fails 4.5:1")
    if contrast_ratio(DARK_INK, DARK_PAPER) < 4.5:
        raise SystemExit("dark pair fails 4.5:1")
    # CTA label picks the higher clearing side; failing palettes refuse.
    if cta_ink("#1f6f5b") != PAPER:
        raise SystemExit("cta on a dark palette is not paper")
    if cta_ink("#c8923e") != INK:
        raise SystemExit("cta on warmth-authority is not ink")
    if cta_ink("#f5f2ea") != INK:
        raise SystemExit("cta on a light palette is not ink")
    _raises(cta_ink, "#808080")
    _raises(cta_ink, "blue")
    # Mold validation mirrors the bind floor.
    palette, lead = validate_mold({"palette": "#1f6f5b", "type_lead": "serif"})
    if (palette, lead) != ("#1f6f5b", "serif"):
        raise SystemExit("mold echo")
    _raises(validate_mold, {"palette": "#1f6f5b", "type_lead": "nope"})
    _raises(validate_mold, {"palette": "blue", "type_lead": "sans"})
    _raises(validate_mold, {"palette": "#808080", "type_lead": "sans"})
    _raises(validate_mold, "not-a-dict")
    # Only spacing props are scale-checked; fonts and borders are exempt.
    css = "p{font-size:17px;border:1px solid red;margin:16px 0;padding:0 24px;gap:7px;}"
    if spacing_values(css) != [16.0, 24.0, 7.0]:
        raise SystemExit(f"spacing extraction missed: {spacing_values(css)}")
    if nontoken_spacings(css) != [7.0]:
        raise SystemExit("off-scale spacing was not flagged")
    if nontoken_spacings("a{margin:4px;padding:32px;gap:64px;}"):
        raise SystemExit("on-scale spacing was flagged")
    if not is_token_spacing(12) or is_token_spacing(13):
        raise SystemExit("step membership")
    # Token CSS: contract numbers present, nothing remote, byte-stable.
    mold = {"palette": "#1f6f5b", "type_lead": "sans"}
    out = token_css(mold)
    for needle in (BODY_SIZE, BODY_LEAD, "clamp(1.75rem,4vw,3rem)", "68ch",
                   f"{PAD_BASE}px", f"{PAD_WIDE}px", "1120px", "#1f6f5b",
                   '"Segoe UI", system-ui, sans-serif'):
        if needle not in out:
            raise SystemExit(f"token css misses {needle}")
    for banned in ("@import", "@font-face", "http"):
        if banned in out:
            raise SystemExit(f"token css carries {banned}")
    if token_css(mold) != out:
        raise SystemExit("token css is not byte-stable")
    dark = token_css(mold, dark=True)
    if DARK_INK not in dark or DARK_PAPER not in dark:
        raise SystemExit("dark swap missing")
    _raises(token_css, {"palette": "#808080", "type_lead": "sans"})
    # VJ-01: four package molds, seed-independent palette, weight caps.
    for mold_id, accent in (
        ("warmth-authority", "#c8923e"),
        ("discover-grid", "#2a6f8f"),
        ("clarify-mix", "#6b4c3b"),
        ("spidercaster-com", "#1f6f5b"),
    ):
        row = mold_tokens(mold_id)
        if row["accent"] != accent or row["id"] != mold_id:
            raise SystemExit(f"mold tokens drifted: {mold_id}")
        if "@" in row["display_stack"] or "http" in row["body_stack"]:
            raise SystemExit(f"mold stack is not local: {mold_id}")
    _raises(mold_tokens, "not-a-mold")
    _raises(resolve_mold_id, {"mold": "not-a-mold"})
    if resolve_mold_id({"template": "editorial"}) != "warmth-authority":
        raise SystemExit("editorial did not map to warmth-authority")
    if resolve_mold_id({"template": "bold"}) != "clarify-mix":
        raise SystemExit("bold did not map to clarify-mix")
    if resolve_mold_id({}) != "discover-grid":
        raise SystemExit("default mold is not discover-grid")
    theme = {"template": "editorial"}
    if build_palette(theme, "alpha") != build_palette(theme, "beta"):
        raise SystemExit("palette still depends on seed")
    painted = build_palette(theme, "ignored")
    if painted["accent"] != "#c8923e" or painted["mold"] != "warmth-authority":
        raise SystemExit(f"editorial palette is not the mold accent: {painted['accent']}")
    overridden = build_palette({"template": "editorial", "accent": "#1f6f5b"}, "seed")
    if overridden["accent"] != "#1f6f5b":
        raise SystemExit("theme accent did not override the mold")
    if (WEIGHT_HTML_RAW, WEIGHT_HTML_GZIP, WEIGHT_SCRIPT, WEIGHT_HERO_IMG, WEIGHT_IMAGE) != (
        225280, 61440, 12288, 153600, 256000,
    ):
        raise SystemExit("weight caps are not the VJ-00 byte values")
    if WEIGHT_CRITICAL_TARGET != 100352:
        raise SystemExit("critical target drifted")
    print("tokens selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
