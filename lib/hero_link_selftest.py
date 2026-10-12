"""Hero buttons survive a frame that drops their old target.

Run from the engine root: python lib/hero_link_selftest.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.compose import _drop_dead_links
from lib.render import render_section


def _fail(msg: str) -> int:
    print("hero link selftest FAIL: " + msg)
    return 1


def _site() -> dict:
    return {
        "meta": {"title": "Harbor Tea Room"},
        "theme": {"template": "modern"},
        "pages": [{"slug": "index"}],
    }


def _hero(primary, secondary) -> dict:
    return {
        "id": "hero",
        "type": "hero",
        "data": {
            "headline": "Harbor Tea Room",
            "subhead": "A quiet tea room.",
            "primary": primary,
            "secondary": secondary,
            "bullets": [],
        },
    }


def main() -> int:
    site = _site()
    only_secondary = render_section(
        _hero(None, {"label": "Contact", "href": "#contact"}),
        site,
        {},
        "index",
    )
    # One-CTA contract: a lone secondary is promoted to the single primary
    # button, never drawn as a second competing treatment.
    if 'class="btn primary"' not in only_secondary or ">Contact</a>" not in only_secondary:
        return _fail("lone secondary was not promoted to the primary button")
    if 'data-cta="primary"' not in only_secondary:
        return _fail("promoted secondary misses the primary marker")
    if 'btn ghost' in only_secondary or 'hero-more' in only_secondary:
        return _fail("lone secondary drew a second treatment")

    both = render_section(
        _hero(
            {"label": "Menu", "href": "#menu"},
            {"label": "Contact", "href": "#contact"},
        ),
        site,
        {},
        "index",
    )
    if 'class="btn primary"' not in both or 'class="hero-more"' not in both:
        return _fail("hero did not draw one button plus a subordinate link")
    if 'btn ghost' in both:
        return _fail("hero secondary regressed to a second button")
    if both.count('data-cta="primary"') != 1:
        return _fail("hero does not carry exactly one primary marker")
    if both.find("Menu") > both.find("Contact"):
        return _fail("primary was drawn after secondary")

    dup = render_section(
        _hero(
            {"label": "Menu", "href": "#menu"},
            {"label": "Menu", "href": "#menu"},
        ),
        site,
        {},
        "index",
    )
    if "hero-more" in dup or dup.count("<a ") != 1:
        return _fail("a secondary repeating the primary was not dropped")

    neither = render_section(_hero(None, None), site, {}, "index")
    if "hero-cta" in neither:
        return _fail("an empty hero action row was drawn")

    raw = {
        "pages": [
            {
                "sections": [
                    _hero({"label": "Hours", "href": "#hours"}, {"label": "Contact", "href": "#contact"}),
                    {"id": "menu", "type": "menu", "data": {"title": "Menu"}},
                    {
                        "id": "contact",
                        "type": "contact",
                        "data": {"title": "Contact", "body": "Walk-ins only."},
                    },
                ]
            }
        ]
    }
    _drop_dead_links(raw)
    data = raw["pages"][0]["sections"][0]["data"]
    if data.get("primary") != {"label": "Menu", "href": "#menu"}:
        return _fail("dropped hero target was not moved to the next title: " + str(data.get("primary")))
    if data.get("secondary") != {"label": "Contact", "href": "#contact"}:
        return _fail("contact secondary was changed")

    kept = {
        "pages": [
            {
                "sections": [
                    _hero({"label": "Build", "href": "#features"}, None),
                    {"id": "features", "type": "features", "data": {"title": "Build"}},
                ]
            }
        ]
    }
    _drop_dead_links(kept)
    if kept["pages"][0]["sections"][0]["data"].get("primary") != {"label": "Build", "href": "#features"}:
        return _fail("a live hero target was replaced")

    print("hero link selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
