"""Paint part CSS with one mold palette and a system type lead. No remote fonts."""
from __future__ import annotations

import re

from lib.render import contrast_ratio

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_ACCENT = re.compile(r"#14213d", re.IGNORECASE)
_REMOTE = re.compile(r"@import|url\(http", re.IGNORECASE)

_STACKS = {
    "serif": 'Georgia, "Iowan Old Style", "Palatino Linotype", Palatino, serif',
    "sans": '"Segoe UI", system-ui, sans-serif',
    "slab": 'Rockwell, "Rockwell Nova", Georgia, serif',
    "mono-display": '"Cascadia Mono", Consolas, monospace',
}


class MoldPaintError(Exception):
    pass


def paint_css(css: str, mold: dict) -> str:
    """Replace #14213d with the mold palette and lead [data-sc-part] with a system stack."""
    if not isinstance(css, str):
        raise MoldPaintError("css")
    if not isinstance(mold, dict):
        raise MoldPaintError("mold")
    palette = mold.get("palette")
    type_lead = mold.get("type_lead")
    if not isinstance(palette, str) or _HEX.fullmatch(palette) is None:
        raise MoldPaintError("palette")
    if not isinstance(type_lead, str) or type_lead not in _STACKS:
        raise MoldPaintError("type_lead")
    # Reject only when neither white nor #1a1a1a clears 4.5 on the palette.
    if contrast_ratio("#ffffff", palette) < 4.5 and contrast_ratio("#1a1a1a", palette) < 4.5:
        raise MoldPaintError("contrast")
    painted = _ACCENT.sub(lambda _match: palette, css)
    out = "[data-sc-part]{font-family: " + _STACKS[type_lead] + ";}\n" + painted
    if _REMOTE.search(out):
        raise MoldPaintError("remote")
    return out
