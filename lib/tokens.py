"""Design tokens: spacing scale, system type stacks, ink/paper pair.

G47 contract (arch-G47-fresh.md section 5, adopted by arch-FINAL.md D5):
spacing steps, type-lead system stacks, ink/paper contrast floors, and the
360-base / 1280-enhancement padding split. Stdlib only, zero tokens.

This module owns the numbers. ``lib/mold_paint.py`` paints palettes;
``lib/check.py`` enforces the cascade statically; ``tools/layout_probe.py``
measures viewports. Nothing here reads the network or a model.
"""
from __future__ import annotations

import re

#: Spacing steps in px. Anything else in a spacing declaration is off-token.
SPACING = (4, 8, 12, 16, 24, 32, 48, 64)

#: type_lead -> system font stack. No @font-face, no remote, no @import.
STACKS = {
    "serif": 'Georgia, "Iowan Old Style", "Palatino Linotype", Palatino, serif',
    "sans": '"Segoe UI", system-ui, sans-serif',
    "slab": 'Rockwell, "Rockwell Nova", Georgia, serif',
    "mono-display": '"Cascadia Mono", Consolas, monospace',
}

INK = "#1a1a1a"
PAPER = "#ffffff"
#: Dark-mode swap of the ink/paper pair.
DARK_INK = "#f5f2ea"
DARK_PAPER = "#14110c"

BODY_SIZE = "1.125rem"
BODY_LEAD = "1.5"
CHROME_SIZE = "1rem"
H1_SIZE = "clamp(1.75rem,4vw,3rem)"
TEXT_MAX = "min(68ch,100%)"
#: Section padding: 32px below 1280px, 48px at the 1280px layer.
PAD_BASE = 32
PAD_WIDE = 48
WIDE_MIN = 1280
CONTAINER_MAX = 1120

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_REMOTE = re.compile(r"@import|@font-face|url\(\s*[\"']?https?:", re.IGNORECASE)
_SPACING_PROP = re.compile(
    r"(?:margin|padding|gap)(?:-(?:top|right|bottom|left|inline|block|x|y))?\s*:([^;{}]+)",
    re.IGNORECASE,
)
_PX = re.compile(r"(\d+(?:\.\d+)?)px")


class TokensError(Exception):
    pass


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.strip().lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(h: str) -> float:
    """Relative luminance of a #rrggbb color."""
    r, g, b = _rgb(h)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast_ratio(a: str, b: str) -> float:
    """WCAG contrast ratio of two #rrggbb colors."""
    hi, lo = luminance(a), luminance(b)
    if hi < lo:
        hi, lo = lo, hi
    return (hi + 0.05) / (lo + 0.05)


def stack_for(type_lead: str) -> str:
    """System stack for a mold type_lead. Raises TokensError when unknown."""
    try:
        return STACKS[str(type_lead or "").strip()]
    except KeyError as exc:
        raise TokensError(f"bad type_lead {type_lead!r}") from exc


def validate_mold(mold: dict) -> tuple[str, str]:
    """Return (palette, type_lead) or raise TokensError.

    Mirrors the bind floor: palette must be #rrggbb and at least one of
    ink/paper must clear 4.5:1 on it, else the mold cannot bind.
    """
    if not isinstance(mold, dict):
        raise TokensError("mold")
    palette = mold.get("palette")
    type_lead = mold.get("type_lead")
    if not isinstance(palette, str) or _HEX.fullmatch(palette) is None:
        raise TokensError("palette")
    if not isinstance(type_lead, str) or type_lead not in STACKS:
        raise TokensError("type_lead")
    if contrast_ratio(PAPER, palette) < 4.5 and contrast_ratio(INK, palette) < 4.5:
        raise TokensError("contrast")
    return palette, type_lead


def cta_ink(palette: str) -> str:
    """CTA label color: ink or paper, whichever clears 4.5:1 with the higher ratio.

    Raises TokensError when neither clears (mold-bind FAIL per G47 section 5).
    """
    if not isinstance(palette, str) or _HEX.fullmatch(palette) is None:
        raise TokensError("palette")
    paper_ratio = contrast_ratio(PAPER, palette)
    ink_ratio = contrast_ratio(INK, palette)
    best = PAPER if paper_ratio >= ink_ratio else INK
    if max(paper_ratio, ink_ratio) < 4.5:
        raise TokensError("contrast")
    return best


def is_token_spacing(px: float) -> bool:
    """True when a px value is an exact spacing step."""
    return any(abs(float(px) - step) < 1e-9 for step in SPACING)


def spacing_values(css: str) -> list[float]:
    """Px values used in margin/padding/gap declarations only.

    Font sizes, borders, and tap floors are not spacing steps; only the
    box-spacing properties are checked against the scale.
    """
    found: list[float] = []
    for decl in _SPACING_PROP.findall(str(css or "")):
        found.extend(float(v) for v in _PX.findall(decl))
    return found


def nontoken_spacings(css: str) -> list[float]:
    """Spacing px values outside the token scale, in order of appearance."""
    return [v for v in spacing_values(css) if not is_token_spacing(v)]


def token_css(mold: dict, *, dark: bool = False) -> str:
    """Token-only base CSS for a mold: custom props plus base rules.

    Raises TokensError on a bad mold, a failing palette, or any remote
    font/import smuggled through the mold values.
    """
    palette, type_lead = validate_mold(mold)
    ink = DARK_INK if dark else INK
    paper = DARK_PAPER if dark else PAPER
    if contrast_ratio(ink, paper) < 4.5:
        raise TokensError("contrast")
    label = cta_ink(palette)
    css = (
        ":root{"
        f"--sc-ink:{ink};--sc-paper:{paper};--sc-accent:{palette};"
        f"--sc-cta-ink:{label};--sc-body:{BODY_SIZE};--sc-chrome:{CHROME_SIZE};"
        f"--sc-h1:{H1_SIZE};--sc-text-max:{TEXT_MAX};"
        f"--sc-pad:{PAD_BASE}px;--sc-gap:{SPACING[4]}px"
        "}\n"
        f"body{{font-family:{STACKS[type_lead]};font-size:var(--sc-body);"
        "line-height:" + BODY_LEAD + ";color:var(--sc-ink);"
        "background:var(--sc-paper);}\n"
        "h1{font-size:var(--sc-h1);overflow-wrap:anywhere;}\n"
        "nav,.sc-chrome{font-size:var(--sc-chrome);}\n"
        ".sc-text{max-width:var(--sc-text-max);}\n"
        "img{max-width:100%;height:auto;}\n"
        "section,[data-sc-part]{padding:var(--sc-pad);}\n"
        f"@media (min-width:{WIDE_MIN}px){{"
        f":root{{--sc-pad:{PAD_WIDE}px;}}"
        f".sc-shell{{max-width:{CONTAINER_MAX}px;margin:0 auto;}}"
        "}\n"
    )
    if _REMOTE.search(css):
        raise TokensError("remote")
    return css
