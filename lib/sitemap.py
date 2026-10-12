"""Sitemap-first planning doc (sitemap.json). Stdlib only, zero tokens.

FINAL D1 (scoped): required for crew runs and any multi-page build;
``build --offline`` single-page may skip it (emit-only, no new friction on
the fastest loop). ``--pages>1`` without per-page copy plus sitemap is
``FAIL pages.scope`` (G47 rule kept).

Shape: {"schema", "site", "frame", "pages": [{slug, file, title, intent,
sections, links}]}. Sections come from the frame vocabulary (frame sections
when a frame is bound, else the IR SECTION_TYPES). Intent lines are one line
per page and feed hero/meta/FAQ selection. Links are internal edges only:
"#anchor" or "slug.html"; anything absolute is FAIL. Default emit is
deterministic; AI at most disambiguates ties elsewhere.

Not to be confused with ``lib/seo_pack.py``, which writes the crawl-facing
``sitemap.xml``/``robots.txt`` from pages already on disk. This module plans
pages before they exist.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.ir import SECTION_TYPES

SCHEMA = "spidercaster-sitemap/1"
FILENAME = "sitemap.json"

_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ABSOLUTE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://|^(?:mailto|tel):", re.IGNORECASE)


class SitemapError(Exception):
    pass


def _row(name: str, status: str, detail: str) -> dict:
    return {"name": name, "status": status, "detail": detail}


def scope_required(*, crew: bool = False, pages: int = 1) -> bool:
    """True when a sitemap.json is required rather than emit-only.

    Crew runs and multi-page builds require it. Offline single-page may
    skip it (emit-only path via emit_single).
    """
    try:
        count = int(pages)
    except (TypeError, ValueError):
        count = 1
    return bool(crew) or count > 1


def _clean_slug(slug: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(slug or "").lower()).strip("-")
    if not text or len(text) > 60 or _SLUG.fullmatch(text) is None:
        raise SitemapError(f"bad slug {slug!r}")
    return text


def _frame_vocab(frame: dict | None) -> list[str]:
    if isinstance(frame, dict) and isinstance(frame.get("sections"), list) and frame["sections"]:
        return [s for s in frame["sections"] if isinstance(s, str) and s in SECTION_TYPES]
    return list(SECTION_TYPES)


def emit_page(
    slug: str,
    title: str,
    intent: str,
    sections: list[str],
    links: list[str] | None = None,
    *,
    vocab: list[str] | None = None,
) -> dict:
    """One validated page entry. Raises SitemapError on a bad slug/section/link."""
    clean = _clean_slug(slug)
    if not str(title or "").strip():
        raise SitemapError(f"page {clean} needs a title")
    if not isinstance(sections, list) or not sections:
        raise SitemapError(f"page {clean} needs sections")
    allowed = set(vocab) if vocab else set(SECTION_TYPES)
    for kind in sections:
        if kind not in allowed:
            raise SitemapError(f"page {clean} section {kind!r} is not frame vocabulary")
    if sections[0] != "hero":
        raise SitemapError(f"page {clean} must start with hero")
    # Repeats are allowed: the planner may emit several sections of one
    # type (frames stay unique; sitemaps describe planned content).
    edges = list(links or [])
    for href in edges:
        if not isinstance(href, str) or not href.strip() or _ABSOLUTE.match(href.strip()):
            raise SitemapError(f"page {clean} link {href!r} is not an internal edge")
    return {
        "slug": clean,
        "file": "index.html" if clean == "index" else f"{clean}.html",
        "title": str(title).strip(),
        "intent": " ".join(str(intent or "").split()),
        "sections": list(sections),
        "links": [h.strip() for h in edges],
    }


def emit_sitemap(
    frame: dict | None,
    pages: list[dict],
    *,
    site: str = "",
) -> dict:
    """Deterministic sitemap doc from explicit page specs.

    Each spec: {slug, title, intent, sections, links?}. First page must be
    the index. Raises SitemapError on any structural problem.
    """
    vocab = _frame_vocab(frame)
    if not isinstance(pages, list) or not pages:
        raise SitemapError("at least the index page is required")
    built = [
        emit_page(
            spec.get("slug", ""), spec.get("title", ""), spec.get("intent", ""),
            spec.get("sections", []), spec.get("links", []), vocab=vocab,
        )
        for spec in pages
        if isinstance(spec, dict)
    ]
    if len(built) != len(pages):
        raise SitemapError("page specs must be objects")
    if built[0]["slug"] != "index":
        raise SitemapError("first page must be the index")
    slugs = [p["slug"] for p in built]
    if len(slugs) != len(set(slugs)):
        raise SitemapError("duplicate slug")
    frame_id = frame.get("id", "") if isinstance(frame, dict) else ""
    return {"schema": SCHEMA, "site": str(site or ""), "frame": str(frame_id or ""), "pages": built}


def emit_single(frame: dict | None, *, site: str = "", title: str = "", intent: str = "") -> dict:
    """Emit-only single-page doc for the offline fast loop.

    Sections are the frame order (copy order fallback lives in the planner;
    this helper never invents copy). Skippable per scope_required.
    """
    vocab = _frame_vocab(frame)
    if "hero" not in vocab:
        vocab = ["hero"] + [s for s in SECTION_TYPES if s != "hero"]
    return emit_sitemap(
        frame,
        [{"slug": "index", "title": title or "Index", "intent": intent, "sections": vocab}],
        site=site,
    )


def emit_from_ir(site_ir: dict, frame: dict | None, *, intents: dict | None = None) -> dict:
    """Derive a sitemap doc from normalized IR pages. No invented sections.

    Per-page intent comes from the caller-supplied {slug: intent} map;
    pages without one get an empty intent so validate() flags them
    (sitemap.intent) instead of this module inventing copy.
    """
    if not isinstance(site_ir, dict) or not isinstance(site_ir.get("pages"), list):
        raise SitemapError("site_ir pages missing")
    want = intents if isinstance(intents, dict) else {}
    specs = []
    for page in site_ir["pages"]:
        if not isinstance(page, dict):
            continue
        sections = [
            sec.get("type") for sec in (page.get("sections") or [])
            if isinstance(sec, dict) and isinstance(sec.get("type"), str)
        ]
        specs.append({
            "slug": page.get("slug", ""),
            "title": (page.get("title") or ""),
            "intent": want.get(page.get("slug", ""), ""),
            "sections": sections,
            "links": [],
        })
    return emit_sitemap(frame, specs, site=str((site_ir.get("meta") or {}).get("title") or ""))


def files_of(doc: dict) -> list[str]:
    """Rendered filenames named by the doc, index first."""
    pages = doc.get("pages") if isinstance(doc, dict) else None
    if not isinstance(pages, list):
        return []
    return [p["file"] for p in pages if isinstance(p, dict) and isinstance(p.get("file"), str)]


def validate(doc: dict, frame: dict | None = None) -> list[dict]:
    """Structural rows: schema, slugs, intent, vocab, links, orphans."""
    rows: list[dict] = []
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        return [_row("sitemap.schema", "FAIL", f"schema must be {SCHEMA}")]
    pages = doc.get("pages")
    if not isinstance(pages, list) or not pages:
        return [_row("sitemap.schema", "FAIL", "pages are required")]
    vocab = set(_frame_vocab(frame))
    seen: set[str] = set()
    dup = ""
    for page in [p for p in pages if isinstance(p, dict)]:
        slug = page.get("slug")
        if not isinstance(slug, str) or _SLUG.fullmatch(slug) is None:
            continue
        if slug in seen and not dup:
            dup = slug
        seen.add(slug)
    bad_slug = [p for p in pages if not isinstance(p, dict) or _SLUG.fullmatch(p.get("slug", "")) is None]
    if bad_slug:
        rows.append(_row("sitemap.slug", "FAIL", "bad slug"))
    elif dup:
        rows.append(_row("sitemap.slug", "FAIL", f"duplicate slug {dup}"))
    else:
        rows.append(_row("sitemap.slug", "PASS", "slugs are clean and unique"))
    if not isinstance(pages[0], dict) or pages[0].get("slug") != "index":
        rows.append(_row("sitemap.schema", "FAIL", "first page must be the index"))
    for page in [p for p in pages if isinstance(p, dict)]:
        slug = page.get("slug", "?")
        if not str(page.get("intent") or "").strip():
            rows.append(_row("sitemap.intent", "FAIL", f"{slug} has no intent line"))
        foreign = [s for s in (page.get("sections") or []) if s not in vocab]
        if foreign:
            rows.append(_row("sitemap.section", "FAIL", f"{slug} uses non-frame section {foreign[0]}"))
        for href in page.get("links") or []:
            if not isinstance(href, str) or _ABSOLUTE.match(href.strip() or " "):
                rows.append(_row("sitemap.link", "FAIL", f"{slug} links absolute {href!r}"))
            elif href.strip().endswith(".html") and href.strip() not in files_of(doc):
                rows.append(_row("sitemap.link", "FAIL", f"{slug} links missing page {href.strip()}"))
    targets: set[str] = set()
    for page in [p for p in pages if isinstance(p, dict)]:
        for href in page.get("links") or []:
            if isinstance(href, str) and href.strip().endswith(".html"):
                targets.add(href.strip())
    orphans = [f for f in files_of(doc)[1:] if f not in targets]
    if orphans:
        rows.append(_row("sitemap.orphan", "FAIL", f"orphan page(s): {', '.join(orphans)}"))
    if not any(r["status"] == "FAIL" for r in rows):
        rows.append(_row("sitemap.valid", "PASS", f"{len(pages)} page(s), frame vocabulary held"))
    return rows


def check(
    doc: dict,
    frame: dict | None = None,
    *,
    h1_counts: dict | None = None,
    faq_visible: dict | None = None,
) -> list[dict]:
    """Full sitemap_check rows: structural plus rendered-page rows.

    h1_counts maps file -> <h1> count; faq_visible maps file -> whether the
    rendered page shows its FAQ. Entries absent from the maps yield SKIP
    rows (NOT RUN evidence, never PASS) so the hand stays honest when the
    page was never rendered.
    """
    rows = validate(doc, frame)
    if any(r["name"] == "sitemap.schema" and r["status"] == "FAIL" for r in rows):
        return rows
    counts = h1_counts if isinstance(h1_counts, dict) else {}
    faqs = faq_visible if isinstance(faq_visible, dict) else {}
    for page in [p for p in doc["pages"] if isinstance(p, dict)]:
        slug, file = page.get("slug", "?"), page.get("file", "?")
        if file in counts:
            try:
                n = int(counts[file])
            except (TypeError, ValueError):
                n = -1
            rows.append(_row(
                "sitemap.h1", "PASS" if n == 1 else "FAIL", f"{slug} has one h1" if n == 1 else f"{slug} has {n} h1",
            ))
        else:
            rows.append(_row("sitemap.h1", "SKIP", f"{slug} was not rendered"))
        if "faq" in (page.get("sections") or []):
            if file in faqs:
                rows.append(_row(
                    "sitemap.faq", "PASS" if faqs[file] else "FAIL",
                    f"{slug} faq matches visible copy" if faqs[file] else f"{slug} faq has no visible match",
                ))
            else:
                rows.append(_row("sitemap.faq", "SKIP", f"{slug} faq was not rendered"))
    return rows


def read_for_architect(doc: dict, frame: dict | None = None) -> list[dict]:
    """Architect's sitemap_read subset: intent-less pages, non-frame sections."""
    return [r for r in validate(doc, frame) if r["name"] in ("sitemap.schema", "sitemap.intent", "sitemap.section")]


def wireframe_text(doc: dict) -> str:
    """Printable sign-off view: sitemap plus unstyled section list."""
    lines = [f"Sitemap: {doc.get('site') or '(untitled)'} [frame: {doc.get('frame') or 'copy order'}]"]
    for page in doc.get("pages") or []:
        if not isinstance(page, dict):
            continue
        lines.append(f"\n== {page.get('file')} — {page.get('title')} ==")
        lines.append(f"intent: {page.get('intent') or '(none)'}")
        for kind in page.get("sections") or []:
            lines.append(f"  [ ] {kind}")
        if page.get("links"):
            lines.append(f"links: {', '.join(page['links'])}")
    return "\n".join(lines) + "\n"


def write_sitemap(site_dir: Path, doc: dict) -> Path:
    """Write sitemap.json beside the built pages. Returns the path."""
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise SitemapError("not a sitemap doc")
    site_dir = Path(site_dir)
    if not site_dir.is_dir():
        raise SitemapError(f"site missing: {site_dir}")
    path = site_dir / FILENAME
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


def load_sitemap(site_dir: Path) -> dict:
    """Load and schema-check sitemap.json. Raises SitemapError when absent/bad."""
    path = Path(site_dir) / FILENAME
    if not path.is_file():
        raise SitemapError(f"no {FILENAME} in {site_dir}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SitemapError(f"{FILENAME} is not JSON") from exc
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise SitemapError(f"bad {FILENAME} schema")
    return doc


def find_sitemap(*dirs: Path | str) -> Path | None:
    """First sitemap.json under the given dirs (out, then project)."""
    for raw in dirs:
        if not raw:
            continue
        candidate = Path(raw) / FILENAME
        if candidate.is_file():
            return candidate
    return None


def _selftest() -> int:
    from lib.frames import load_frame

    frame = load_frame("service-counter")
    vocab = _frame_vocab(frame)
    if "hero" not in vocab or "menu" in vocab:
        raise SystemExit("frame vocab is not the frame sections")
    if _frame_vocab(None) != SECTION_TYPES:
        raise SystemExit("frameless vocab is not the IR types")
    if scope_required(crew=True, pages=1) is not True:
        raise SystemExit("crew run must require a sitemap")
    if scope_required(pages=2) is not True:
        raise SystemExit("multi-page must require a sitemap")
    if scope_required(pages=1) is not False:
        raise SystemExit("offline single-page must be emit-only")
    doc = emit_sitemap(frame, [
        {"slug": "index", "title": "Counter", "intent": "Say the job, show proof, ask.",
         "sections": vocab, "links": ["visit.html"]},
        {"slug": "visit", "title": "Visit", "intent": "How to find the counter.",
         "sections": ["hero", "contact"], "links": ["index.html"]},
    ], site="demo.example")
    if files_of(doc) != ["index.html", "visit.html"]:
        raise SystemExit("files_of order")
    rows = validate(doc, frame)
    if any(r["status"] == "FAIL" for r in rows):
        raise SystemExit("good sitemap failed: " + "; ".join(r["detail"] for r in rows))
    text = wireframe_text(doc)
    if "visit.html" not in text or "[ ] hero" not in text:
        raise SystemExit("wireframe is not printable")
    single = emit_single(frame, site="demo.example", title="Counter", intent="Say the job.")
    if files_of(single) != ["index.html"]:
        raise SystemExit("single-page emit")
    try:
        emit_sitemap(frame, [{"slug": "index", "title": "T", "intent": "I", "sections": ["hero", "menu"]}])
    except SitemapError:
        pass
    else:
        raise SystemExit("non-frame section was emitted")
    try:
        emit_sitemap(frame, [{"slug": "visit", "title": "T", "intent": "I", "sections": ["hero"]}])
    except SitemapError:
        pass
    else:
        raise SystemExit("non-index first page was emitted")
    bad_intent = emit_single(None)
    bad_intent["pages"][0]["intent"] = ""
    if not any(r["name"] == "sitemap.intent" and r["status"] == "FAIL"
               for r in validate(bad_intent, None)):
        raise SystemExit("intent-less page passed")
    lone = emit_sitemap(None, [
        {"slug": "index", "title": "T", "intent": "I", "sections": ["hero"], "links": []},
        {"slug": "visit", "title": "V", "intent": "I2", "sections": ["hero"], "links": []},
    ])
    if not any(r["name"] == "sitemap.orphan" for r in validate(lone, None)):
        raise SystemExit("orphan page passed")
    abs_link = emit_single(None, title="T", intent="I")
    abs_link["pages"][0]["links"] = ["https://example.com/x.html"]
    if not any(r["name"] == "sitemap.link" for r in validate(abs_link, None)):
        raise SystemExit("absolute link passed")
    full = check(doc, frame, h1_counts={"index.html": 1, "visit.html": 2}, faq_visible={})
    if not any(r["name"] == "sitemap.h1" and r["status"] == "FAIL" for r in full):
        raise SystemExit("double h1 passed")
    if not any(r["name"] == "sitemap.h1" and r["status"] == "SKIP"
               for r in check(doc, frame, h1_counts={"index.html": 1})):
        raise SystemExit("unrendered page did not SKIP")
    if read_for_architect(doc, frame) != [] and any(
            r["status"] == "FAIL" for r in read_for_architect(doc, frame)):
        raise SystemExit("architect read failed a good sitemap")
    print("sitemap selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
