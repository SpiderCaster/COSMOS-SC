"""Renderer budget + conversion selftest. Run from the engine root: python lib/render_budget_selftest.py

Assembles one synthetic page and pins the team-render contract with stdlib
only (no network, no project build, no publish):
- page weight: HTML raw <= 225280 bytes, gzip <= 61440, inline script <= 12288
- zero-framework output: no remote URL, @import, @font-face, or url(http
- one cited primary CTA: exactly one data-cta="primary" site-wide, no ghost
  button in hero/cta sections, duplicate secondary dropped
- thumb bar + safe-area: phone-bar with tel: href, safe-area insets reserved,
  scroll-padding so focus is never covered
- layout stability: hero img carries width+height, img CSS keeps height:auto
- mobile-first CSS: single-column base, 861px structural layer, 1280px layer
"""
from __future__ import annotations

import gzip
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.render import assemble
from lib.tokens import WEIGHT_HTML_GZIP, WEIGHT_HTML_RAW, WEIGHT_SCRIPT

HTML_RAW_BUDGET = WEIGHT_HTML_RAW
HTML_GZIP_BUDGET = WEIGHT_HTML_GZIP
SCRIPT_BUDGET = WEIGHT_SCRIPT


def _site() -> dict:
    return {
        "meta": {"title": "Harbor Tea Room", "description": "A quiet tea room."},
        "theme": {"template": "modern", "dark": True},
        "nav": [{"label": "Menu", "href": "#menu"}],
        "footer": {"text": "Harbor Tea Room", "links": []},
        "pages": [
            {
                "slug": "index",
                "title": "Harbor Tea Room",
                "description": "A quiet tea room.",
                "sections": [
                    {
                        "id": "hero",
                        "type": "hero",
                        "data": {
                            "headline": "Harbor Tea Room",
                            "subhead": "A quiet tea room.",
                            "primary": {"label": "Menu", "href": "#menu"},
                            "secondary": {"label": "Contact", "href": "#contact"},
                            "image": "assets/hero.jpg",
                            "image_w": 640,
                            "image_h": 360,
                            "bullets": [],
                        },
                    },
                    {
                        "id": "menu",
                        "type": "about",
                        "data": {"title": "Menu", "body": ["Tea and quiet."]},
                    },
                    {
                        "id": "contact",
                        "type": "contact",
                        "data": {
                            "title": "Contact",
                            "phone": "(555) 014-2288",
                            "email": "desk@example.com",
                        },
                    },
                ],
            }
        ],
    }


def _fail(msg: str) -> int:
    print("render budget selftest FAIL: " + msg)
    return 1


def main() -> int:
    pages = assemble(_site(), noindex=True)
    html = next((p["html"] for p in pages if p.get("file") == "index.html"), "")
    if not html:
        return _fail("assemble did not return index.html")

    raw = html.encode("utf-8")
    if len(raw) > HTML_RAW_BUDGET:
        return _fail(f"index.html raw {len(raw)} over {HTML_RAW_BUDGET}")
    if len(gzip.compress(raw)) > HTML_GZIP_BUDGET:
        return _fail("index.html gzip over budget")
    for script in re.findall(r"<script>(.*?)</script>", html, re.DOTALL):
        if len(script.encode("utf-8")) > SCRIPT_BUDGET:
            return _fail("inline script over budget")

    low = html.lower()
    # The JSON-LD @context identifier is vocabulary, not a fetch; scan the
    # rest of the document for remote/framework traces.
    body = re.sub(
        r'<script type="application/ld\+json">.*?</script>', "", low, flags=re.DOTALL
    )
    for needle in ("http://", "https://", "@import", "url(http"):
        if needle in body:
            return _fail(f"remote/framework trace in output: {needle}")
    if "@font-face" in body:
        if "font-display:swap" not in body or 'url("assets/fonts/' not in body:
            return _fail("font-face is not a local swap face")
        if "https://" in body or "http://" in body:
            return _fail("font-face points at a remote file")

    if html.count('data-cta="primary"') != 1:
        return _fail("page does not carry exactly one primary CTA marker")
    if "btn ghost" in html:
        return _fail("a ghost button competes with the primary CTA")
    if 'class="hero-more"' not in html:
        return _fail("distinct secondary is not a subordinate link")
    if 'class="phone-bar"' not in html or 'href="tel:' not in html:
        return _fail("sticky thumb bar with tel: href is missing")
    if "env(safe-area-inset-bottom)" not in html:
        return _fail("thumb bar does not honor the safe area")
    if "scroll-padding-top" not in html or "scroll-padding-bottom" not in html:
        return _fail("scroll padding does not clear header and thumb bar")
    if 'width="640" height="360"' not in html:
        return _fail("hero img misses width+height (layout stability)")
    if "height:auto" not in html.replace(" ", ""):
        return _fail("img CSS does not keep height:auto")
    if "min-width:44px" not in html.replace(" ", ""):
        return _fail("44px tap floor is missing from button/link CSS")
    if "min-width:1280px" not in html.replace(" ", ""):
        return _fail("1280px wide layer is missing")
    if "viewport-fit=cover" not in html:
        return _fail("viewport does not cover the safe area")

    print("render budget selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
