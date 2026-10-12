"""Prove sitemap emit/validate/check scope rules. Run: python lib/sitemap_selftest.py"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.sitemap import (
    FILENAME,
    SCHEMA,
    SitemapError,
    check,
    emit_from_ir,
    emit_single,
    emit_sitemap,
    files_of,
    find_sitemap,
    load_sitemap,
    read_for_architect,
    scope_required,
    validate,
    wireframe_text,
    write_sitemap,
)


def _raises(fn, *args, **kwargs) -> None:
    try:
        fn(*args, **kwargs)
    except SitemapError:
        return
    raise AssertionError(f"expected SitemapError from {fn.__name__}")


def main() -> int:
    # Scope: crew and multi-page require; offline single-page is emit-only.
    if scope_required(crew=True, pages=1) is not True:
        raise SystemExit("crew must require a sitemap")
    if scope_required(pages=3) is not True:
        raise SystemExit("multi-page must require a sitemap")
    if scope_required(pages=1) is not False or scope_required() is not False:
        raise SystemExit("offline single-page must be emit-only")
    frame = {"id": "local-desk", "sections": ["hero", "features", "faq", "contact"]}
    doc = emit_sitemap(frame, [
        {"slug": "index", "title": "Desk", "intent": "Say the job, show proof, ask.",
         "sections": ["hero", "features", "faq", "contact"], "links": ["visit.html"]},
        {"slug": "visit", "title": "Visit", "intent": "How to find the desk.",
         "sections": ["hero", "contact"], "links": ["index.html"]},
    ], site="desk.example")
    if doc["schema"] != SCHEMA or doc["frame"] != "local-desk":
        raise SystemExit("emit header")
    if files_of(doc) != ["index.html", "visit.html"]:
        raise SystemExit("emit files")
    if any(r["status"] == "FAIL" for r in validate(doc, frame)):
        raise SystemExit("good doc failed validate")
    if any(r["status"] == "FAIL" for r in read_for_architect(doc, frame)):
        raise SystemExit("architect read failed a good doc")
    # Emit guards: vocab, hero-first, index-first, unique slugs, internal edges.
    _raises(emit_sitemap, frame, [
        {"slug": "index", "title": "T", "intent": "I", "sections": ["hero", "menu"]}])
    _raises(emit_sitemap, frame, [
        {"slug": "index", "title": "T", "intent": "I", "sections": ["features"]}])
    _raises(emit_sitemap, frame, [
        {"slug": "visit", "title": "T", "intent": "I", "sections": ["hero"]}])
    _raises(emit_sitemap, frame, [
        {"slug": "index", "title": "T", "intent": "I", "sections": ["hero"]},
        {"slug": "index", "title": "T2", "intent": "I2", "sections": ["hero"]}])
    _raises(emit_sitemap, frame, [
        {"slug": "Bad Slug!", "title": "T", "intent": "I", "sections": ["hero"]}])
    _raises(emit_sitemap, frame, [
        {"slug": "index", "title": "", "intent": "I", "sections": ["hero"]}])
    # Validate flags: intent-less, orphan, absolute link, missing target.
    no_intent = emit_single(None, title="T", intent="I")
    no_intent["pages"][0]["intent"] = "  "
    if not any(r["name"] == "sitemap.intent" and r["status"] == "FAIL"
               for r in validate(no_intent, None)):
        raise SystemExit("intent-less page passed")
    lone = emit_sitemap(None, [
        {"slug": "index", "title": "T", "intent": "I", "sections": ["hero"]},
        {"slug": "visit", "title": "V", "intent": "I2", "sections": ["hero"]},
    ])
    if not any(r["name"] == "sitemap.orphan" and r["status"] == "FAIL"
               for r in validate(lone, None)):
        raise SystemExit("orphan page passed")
    abs_doc = emit_single(None, title="T", intent="I")
    abs_doc["pages"][0]["links"] = ["https://example.com/x.html"]
    if not any(r["name"] == "sitemap.link" and r["status"] == "FAIL"
               for r in validate(abs_doc, None)):
        raise SystemExit("absolute link passed")
    dangling = emit_single(None, title="T", intent="I")
    dangling["pages"][0]["links"] = ["gone.html"]
    if not any(r["name"] == "sitemap.link" and r["status"] == "FAIL"
               for r in validate(dangling, None)):
        raise SystemExit("dangling link passed")
    # check(): rendered rows PASS/FAIL, unrendered rows SKIP (never PASS).
    rows = check(doc, frame, h1_counts={"index.html": 1, "visit.html": 0},
                 faq_visible={"index.html": True})
    by_name = {(r["name"], r["detail"].split()[0]): r["status"] for r in rows}
    if by_name.get(("sitemap.h1", "index")) != "PASS":
        raise SystemExit("single h1 did not pass")
    if by_name.get(("sitemap.h1", "visit")) != "FAIL":
        raise SystemExit("zero h1 did not fail")
    if by_name.get(("sitemap.faq", "index")) != "PASS":
        raise SystemExit("visible faq did not pass")
    skipped = check(doc, frame, h1_counts={"index.html": 1})
    if not any(r["name"] == "sitemap.h1" and r["status"] == "SKIP" for r in skipped):
        raise SystemExit("unrendered h1 did not SKIP")
    if not any(r["name"] == "sitemap.faq" and r["status"] == "SKIP" for r in skipped):
        raise SystemExit("unrendered faq did not SKIP")
    bad_faq = check(doc, frame, h1_counts={"index.html": 1, "visit.html": 1},
                    faq_visible={"index.html": False})
    if not any(r["name"] == "sitemap.faq" and r["status"] == "FAIL" for r in bad_faq):
        raise SystemExit("faq without visible match passed")
    # IR derive: no invented sections; missing intents flagged, not filled.
    site_ir = {"meta": {"title": "Desk"}, "pages": [
        {"slug": "index", "title": "Desk",
         "sections": [{"id": "hero", "type": "hero"}, {"id": "contact", "type": "contact"}]},
    ]}
    derived = emit_from_ir(site_ir, frame, intents={"index": "Say the job."})
    if files_of(derived) != ["index.html"] or derived["pages"][0]["sections"] != ["hero", "contact"]:
        raise SystemExit("IR derive")
    mute = emit_from_ir(site_ir, frame)
    if not any(r["name"] == "sitemap.intent" for r in validate(mute, frame)):
        raise SystemExit("missing intent was invented instead of flagged")
    # Write/load/find roundtrip; bad schema refused.
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp) / "site"
        site.mkdir()
        path = write_sitemap(site, doc)
        if path.name != FILENAME or not path.is_file():
            raise SystemExit("write path")
        if load_sitemap(site) != json.loads(path.read_text(encoding="utf-8")):
            raise SystemExit("load roundtrip")
        if find_sitemap(site, Path(tmp) / "nowhere") != path:
            raise SystemExit("find order")
        if find_sitemap(Path(tmp) / "nowhere") is not None:
            raise SystemExit("find miss")
        (site / FILENAME).write_text('{"schema": "nope"}', encoding="utf-8")
        _raises(load_sitemap, site)
        (site / FILENAME).unlink()
        _raises(load_sitemap, site)
        _raises(write_sitemap, Path(tmp) / "nowhere", doc)
        _raises(write_sitemap, site, {"schema": "nope"})
    if "visit.html" not in wireframe_text(doc) or "[ ] faq" not in wireframe_text(doc):
        raise SystemExit("wireframe print")
    print("sitemap selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
