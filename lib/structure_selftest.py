"""Prove structure round-trip and planned section types.

Run from the engine root: python lib/structure_selftest.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.structure import (
    apply_subset,
    load_structure,
    make_structure,
    save_structure,
    subset_edit,
    validate_structure,
)


def _fail(msg: str) -> int:
    print("structure selftest FAIL: " + msg)
    return 1


def main() -> int:
    site = {
        "pages": [
            {
                "slug": "index",
                "title": "Ignored",
                "sections": [
                    {"id": "top", "type": "hero", "data": {"headline": "Keep me out"}},
                    {"id": "story", "type": "about"},
                    {"id": "blank", "type": "cta"},
                ],
            },
            {
                "slug": "visit",
                "sections": [
                    {"id": "hours", "type": "contact"},
                ],
            },
        ]
    }
    picks = {
        "hero": "part-hero",
        "story": "part-about-by-id",
        "about": "part-about-by-type",
        "blank": "",
        "cta": "part-cta",
        "faq": "part-faq-should-not-appear",
    }
    data = make_structure(site, "welcome-scroll", "clarify-mix", picks)
    if data.get("schema") != "spidercaster-structure/1":
        return _fail("bad schema")
    if data.get("frame_id") != "welcome-scroll" or data.get("mold_id") != "clarify-mix":
        return _fail("frame or mold was not stored")
    pages = data.get("pages")
    if not isinstance(pages, list) or len(pages) != 2:
        return _fail("pages were not copied")
    if "title" in pages[0] or pages[0].get("slug") != "index":
        return _fail("page shape changed")
    sections = pages[0]["sections"]
    if [sec["type"] for sec in sections] != ["hero", "about", "cta"]:
        return _fail("section types were added or dropped")
    if any("data" in sec for sec in sections):
        return _fail("section data was copied")
    if sections[0]["part_id"] != "part-hero":
        return _fail("type pick was not used")
    if sections[1]["part_id"] != "part-about-by-id":
        return _fail("section id pick did not win")
    if sections[2]["part_id"] != "part-cta":
        return _fail("empty id pick did not fall through to type")
    if pages[1]["sections"][0]["part_id"] != "":
        return _fail("missing pick was not empty")
    if any(sec["type"] == "faq" for page in pages for sec in page["sections"]):
        return _fail("added a section type the site does not have")

    planned = ["hero", "about", "cta", "contact", "menu"]
    good = validate_structure(data, planned)
    if good:
        return _fail("good structure errors: " + "; ".join(good))

    extra = {
        "schema": data["schema"],
        "frame_id": data["frame_id"],
        "mold_id": data["mold_id"],
        "pages": list(data["pages"]) + [
            {"slug": "hours", "sections": [{"id": "board", "type": "menu", "part_id": ""}]}
        ],
    }
    if validate_structure(extra, planned):
        return _fail("extra page was rejected")

    bad = {
        "schema": data["schema"],
        "frame_id": data["frame_id"],
        "mold_id": data["mold_id"],
        "pages": [
            {
                "slug": "index",
                "sections": [
                    {"id": "pop", "type": "popup", "part_id": "nope"},
                ],
            }
        ],
    }
    bad_errors = validate_structure(bad, planned)
    if not any("popup" in err for err in bad_errors):
        return _fail("bad type was not reported")

    with tempfile.TemporaryDirectory(prefix="sc-structure-") as tmp:
        path = Path(tmp) / "structure.json"
        save_structure(path, data)
        raw = path.read_bytes()
        if not raw.endswith(b"\n") or b"\r" in raw:
            return _fail("save did not write UTF-8 JSON with a trailing newline")
        loaded = load_structure(path)
        if loaded != data:
            return _fail("round-trip mismatch")
        if validate_structure(loaded, planned):
            return _fail("loaded structure was not valid")

    fresh = data
    swapped = {
        "schema": fresh["schema"],
        "frame_id": fresh["frame_id"],
        "mold_id": fresh["mold_id"],
        "pages": [
            {
                "slug": "index",
                "sections": [fresh["pages"][0]["sections"][1], fresh["pages"][0]["sections"][0]],
            },
            fresh["pages"][1],
        ],
    }
    kept, errors = subset_edit(fresh, swapped)
    if errors or kept is None:
        return _fail("reorder was refused: " + "; ".join(errors))
    if [sec["id"] for sec in kept["pages"][0]["sections"]] != ["story", "top"]:
        return _fail("reorder did not keep the edited order")

    dropped = {
        "schema": fresh["schema"],
        "frame_id": fresh["frame_id"],
        "mold_id": fresh["mold_id"],
        "pages": [
            {"slug": "index", "sections": [fresh["pages"][0]["sections"][0]]},
            fresh["pages"][1],
        ],
    }
    kept, errors = subset_edit(fresh, dropped)
    if errors or kept is None:
        return _fail("drop was refused: " + "; ".join(errors))

    added = {
        "schema": fresh["schema"],
        "frame_id": fresh["frame_id"],
        "mold_id": fresh["mold_id"],
        "pages": [
            {
                "slug": "index",
                "sections": fresh["pages"][0]["sections"] + [
                    {"id": "pop", "type": "pricing", "part_id": "nope"},
                ],
            },
            fresh["pages"][1],
        ],
    }
    _kept, errors = subset_edit(fresh, added)
    if not any("not planned" in err for err in errors):
        return _fail("added section was accepted")

    moved = {
        "schema": fresh["schema"],
        "frame_id": fresh["frame_id"],
        "mold_id": fresh["mold_id"],
        "pages": [
            {"slug": "index", "sections": [fresh["pages"][0]["sections"][0]]},
            {
                "slug": "visit",
                "sections": fresh["pages"][1]["sections"] + [fresh["pages"][0]["sections"][1]],
            },
        ],
    }
    _kept, errors = subset_edit(fresh, moved)
    if not errors:
        return _fail("cross-page move was accepted")

    changed = dict(fresh)
    changed = {
        "schema": fresh["schema"],
        "frame_id": "other-frame",
        "mold_id": fresh["mold_id"],
        "pages": fresh["pages"],
    }
    _kept, errors = subset_edit(fresh, changed)
    if not any("frame_id" in err for err in errors):
        return _fail("frame change was accepted")

    site = {
        "pages": [
            {
                "slug": "index",
                "sections": [
                    {"id": "top", "type": "hero", "data": {"headline": "Stay"}},
                    {"id": "story", "type": "about", "data": {"headline": "Also"}},
                ],
            }
        ]
    }
    apply_subset(site, swapped)
    ordered = site["pages"][0]["sections"]
    if [sec["id"] for sec in ordered] != ["story", "top"]:
        return _fail("apply_subset did not reorder")
    if ordered[1].get("data", {}).get("headline") != "Stay":
        return _fail("apply_subset dropped section data")

    print("structure selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
