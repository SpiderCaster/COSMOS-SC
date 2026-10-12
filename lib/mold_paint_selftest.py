"""Paint part CSS. Run from the engine root: python lib/mold_paint_selftest.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.mold_paint import MoldPaintError, paint_css

_SAMPLE = (
    ".sc-x{color:#14213D;background:#14213d;border-color:#1a1a1a;outline-color:#ffffff}"
)
_CASES = (
    ("#2a6f8f", "sans", '"Segoe UI", system-ui, sans-serif'),
    ("#c8923e", "serif", 'Georgia, "Iowan Old Style", "Palatino Linotype", Palatino, serif'),
    ("#2a6f8f", "slab", 'Rockwell, "Rockwell Nova", Georgia, serif'),
    ("#c8923e", "mono-display", '"Cascadia Mono", Consolas, monospace'),
)


def _raises(css: str, mold: dict) -> None:
    try:
        paint_css(css, mold)
    except MoldPaintError:
        return
    raise AssertionError("expected MoldPaintError")


def main() -> int:
    for palette, lead, stack in _CASES:
        out = paint_css(_SAMPLE, {"palette": palette, "type_lead": lead})
        assert "#14213d" not in out.lower()
        assert palette in out
        assert out.count("#1a1a1a") == _SAMPLE.count("#1a1a1a")
        assert out.count("#ffffff") == _SAMPLE.count("#ffffff")
        assert out.startswith("[data-sc-part]{font-family: " + stack + ";}\n")
    _raises(_SAMPLE, {"palette": "#2a6f8f", "type_lead": "nonsense"})
    _raises(_SAMPLE, {"palette": "blue", "type_lead": "sans"})
    _raises(_SAMPLE, {"palette": "#808080", "type_lead": "sans"})
    _raises("@import url(https://fonts.example/x.css)", {"palette": "#2a6f8f", "type_lead": "sans"})
    _raises("a{background:url(http://cdn.example/a.png)}", {"palette": "#2a6f8f", "type_lead": "sans"})
    print("mold_paint selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
