"""Battery for the SEO-research checker rows (google/schema/ahrefs/moz/stox static subset).

Run: python lib/check_seo_selftest.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.check import check_site

_FILLER = "Plain filler sentence about the test page topic for word counts. "


def _page(name, title, h1s, body, desc="A short description of this test page.", lang=True,
          head=""):
    lang_attr = ' lang="en"' if lang else ""
    h = "".join(f"<h1>{t}</h1>" for t in h1s)
    return (
        "<!doctype html>\n<html" + lang_attr + ">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        f"<title>{title}</title>\n<meta name=\"description\" content=\"{desc}\">\n"
        f"<link rel=\"canonical\" href=\"{name}\">\n"
        f"{head}</head>\n<body>{h}\n{body}\n</body>\n</html>\n"
    )


def _write(site: Path, files: dict[str, str]) -> Path:
    site.mkdir(parents=True, exist_ok=True)
    for name, html in files.items():
        (site / name).write_text(html, encoding="utf-8")
    return site


def _rows(site: Path) -> dict[str, dict]:
    rep = check_site(site, quiet=True, typography=False, tap_targets=False, mobile=False,
                     extra_gates=False)
    return {row["name"]: row for row in rep.rows}


def _expect(rows: dict[str, dict], name: str, status: str, needle: str = "") -> None:
    row = rows.get(name)
    if row is None:
        raise SystemExit(f"missing row {name}")
    if row["status"] != status:
        raise SystemExit(f"{name}: want {status}, got {row['status']} ({row['detail']})")
    if needle and needle not in row["detail"]:
        raise SystemExit(f"{name}: want {needle!r} in ({row['detail']})")


def _scenario_multi(tmp: Path) -> None:
    site = _write(tmp / "multi", {
        "index.html": _page(
            "index.html", "Alpha Guide to Widgets", ["Alpha"],
            '<a href="a.html">beta details</a> <a href="b.html">gamma notes</a> '
            '<a href="d1.html">deep dive one</a> <a href="z.html">zed page</a> '
            '<a href="dup1.html">first duplicate</a> <a href="dup2.html">second duplicate</a> '
            + _FILLER * 2, desc="Alpha page description for tests."),
        "a.html": _page(
            "a.html", "Beta Page Shared", ["Beta One", "Beta Two"],
            '<a href="index.html">back to alpha</a> ' + _FILLER * 2,
            desc="Shared description text here."),
        "b.html": _page(
            "b.html", "Beta Page Shared", ["Beta B"],
            "<a>no href</a> "
            "<a href=\"javascript:void(0)\">js</a> "
            "<a href=\"#\">hash</a> "
            "<a href=\"a.html\"></a> "
            "<a href=\"a.html\">click here</a> "
            "<a href=\"a.html\" rel=\"nofollow\">sculpted</a> "
            "<a href=\"a.html\">one</a> <a href=\"index.html\">two</a> "
            "<a href=\"index.html\">home</a> " + _FILLER,
            desc="Shared description text here."),
        "c.html": _page(
            "c.html", "Cee Orphan Page Here", ["Cee"],
            '<a href="index.html">back to alpha</a> ' + _FILLER * 2,
            desc="Cee page description for tests.", lang=False),
        "d1.html": _page(
            "d1.html", "Deep One Page Title", ["Deep One"],
            '<a href="d2.html">deeper two</a> ' + _FILLER,
            desc="Deep one description here."),
        "d2.html": _page(
            "d2.html", "Deep Two Page Title", ["Deep Two"],
            '<a href="d3.html">deeper three</a> ' + _FILLER,
            desc="Deep two description here."),
        "d3.html": _page(
            "d3.html", "Deep Three Page Title", ["Deep Three"],
            '<a href="d4.html">deeper four</a> ' + _FILLER,
            desc="Deep three description here."),
        "d4.html": _page(
            "d4.html", "Deep Four Page Title", ["Deep Four"],
            '<a href="index.html">back to alpha</a> ' + _FILLER,
            desc="Deep four description here."),
        "z.html": _page(
            "z.html", "Zed Dead End Page Here", ["Zed"], _FILLER * 2,
            desc="Zed page description here."),
        "dup1.html": _page(
            "dup1.html", "Dup Shared Title Page", ["Same Heading Text"],
            "<p>Same paragraph text on both duplicate pages here.</p> "
            "<a href=\"index.html\">back to alpha</a>",
            desc="Dup shared description here."),
        "dup2.html": _page(
            "dup2.html", "Dup Shared Title Page", ["Same Heading Text"],
            "<p>Same paragraph text on both duplicate pages here.</p> "
            "<a href=\"index.html\">back to alpha</a>",
            desc="Dup shared description here."),
    })
    rows = _rows(site)
    _expect(rows, "title_unique", "FAIL", "b.html: title duplicate of a.html")
    _expect(rows, "description_unique", "WARN", "b.html: meta description duplicate")
    _expect(rows, "h1_every_page", "FAIL", "a.html: h1 count=2")
    _expect(rows, "link_href", "FAIL", "b.html: a javascript: href")
    if "placeholder href=#" not in rows["link_href"]["detail"]:
        raise SystemExit("href=# warn missing from link_href detail")
    _expect(rows, "anchor_text", "FAIL", "b.html: empty anchor")
    if "generic anchor" not in rows["anchor_text"]["detail"]:
        raise SystemExit("generic anchor warn missing from anchor_text detail")
    if "adjacent links" not in rows["anchor_text"]["detail"]:
        raise SystemExit("chained-link warn missing from anchor_text detail")
    _expect(rows, "orphan_pages", "FAIL", "c.html: zero inbound internal links")
    _expect(rows, "click_depth", "WARN", "d4.html: 4 clicks")
    _expect(rows, "internal_nofollow", "FAIL", "b.html: rel=nofollow on internal")
    _expect(rows, "robots_allow", "PASS")
    _expect(rows, "noindex_crawl", "PASS")
    _expect(rows, "sitemap_parity", "WARN", "multi-page without sitemap")
    _expect(rows, "schema_required", "PASS")
    _expect(rows, "thin_content", "WARN")
    _expect(rows, "duplicate_content", "FAIL", "dup1.html, dup2.html")
    _expect(rows, "dead_end", "WARN", "z.html: zero outbound")
    _expect(rows, "doc_lang", "FAIL", "c.html: html lang missing")
    _expect(rows, "plan_links", "SKIP")


def _scenario_robots(tmp: Path) -> None:
    site = _write(tmp / "robots", {
        "index.html": _page("index.html", "Robot Test Page Title", ["Robots"],
                            '<a href="#top">top</a> ' + _FILLER * 2,
                            desc="Robot page description here."),
        "robots.txt": "User-agent: *\n\nDisallow: /\n",
    })
    rows = _rows(site)
    _expect(rows, "robots_allow", "FAIL", "Disallow: /")
    _expect(rows, "noindex_crawl", "PASS")


def _scenario_staging(tmp: Path) -> None:
    site = _write(tmp / "staging", {
        "index.html": _page(
            "index.html", "Staging Test Page Title", ["Staging"],
            _FILLER * 2, desc="Staging page description here.",
            head='<meta name="robots" content="noindex, nofollow">\n'),
        "robots.txt": "User-agent: *\n\nDisallow: /\n",
    })
    rows = _rows(site)
    _expect(rows, "robots_allow", "PASS", "staging posture")
    _expect(rows, "noindex_crawl", "WARN", "index.html: noindex but robots-disallowed")


def _scenario_sitemap(tmp: Path) -> None:
    site = _write(tmp / "sitemap", {
        "index.html": _page("index.html", "Sitemap Test Page One", ["Sitemap One"],
                            _FILLER * 2, desc="Sitemap one description here."),
        "b.html": _page(
            "b.html", "Sitemap Test Page Two", ["Sitemap Two"],
            _FILLER * 2, desc="Sitemap two description here."),
        "sitemap.json": json.dumps({"pages": [
            {"file": "index.html", "links": []},
            {"file": "ghost.html", "links": []},
        ]}),
    })
    rows = _rows(site)
    _expect(rows, "sitemap_parity", "FAIL", "sitemap lists missing ghost.html")
    _expect(rows, "plan_links", "PASS")


def _scenario_schema_fail(tmp: Path) -> None:
    head = (
        "<script type=\"application/ld+json\">"
        "{\"@context\": \"https://schema.org\", \"@type\": \"HowTo\", \"name\": \"X\"}"
        "</script>\n"
        "<script type=\"application/ld+json\">"
        "{\"@context\": \"https://schema.org\", \"@type\": \"BreadcrumbList\", "
        "\"itemListElement\": [{\"@type\": \"ListItem\", \"position\": 1, "
        "\"name\": \"Home\", \"item\": \"index.html\"}]}"
        "</script>\n"
        "<script type=\"application/ld+json\">"
        "{\"@context\": \"https://schema.org\", \"@type\": \"Restaurant\", "
        "\"name\": \"Tea Room\"}"
        "</script>\n"
    )
    site = _write(tmp / "schemafail", {
        "index.html": _page("index.html", "Schema Fail Page Title", ["Schema Fail"],
                            _FILLER * 2, desc="Schema fail description here.", head=head),
    })
    rows = _rows(site)
    _expect(rows, "schema_required", "FAIL", "HowTo deprecated")
    for needle in ("BreadcrumbList itemListElement needs >= 2", "LocalBusiness address missing"):
        if needle not in rows["schema_required"]["detail"]:
            raise SystemExit(f"schema detail missing {needle!r}")


def _scenario_schema_warn(tmp: Path) -> None:
    head = (
        "<script type=\"application/ld+json\">"
        "{\"@context\": \"https://schema.org\", \"@type\": \"NewsArticle\", "
        "\"author\": \"Some Writer\"}"
        "</script>\n"
    )
    site = _write(tmp / "schemawarn", {
        "index.html": _page("index.html", "Schema Warn Page Title", ["Schema Warn"],
                            _FILLER * 2, desc="Schema warn description here.", head=head),
    })
    rows = _rows(site)
    _expect(rows, "schema_required", "WARN", "NewsArticle without headline")


def _scenario_plan(tmp: Path) -> None:
    site = _write(tmp / "plan", {
        "index.html": _page("index.html", "Plan Test Page Title Here", ["Plan"],
                            '<a href="b.html">bee page</a> ' + _FILLER * 2,
                            desc="Plan page description here."),
        "a.html": _page(
            "a.html", "Plan Aye Page Title Here", ["Plan Aye"],
            _FILLER * 2, desc="Plan aye description here."),
        "b.html": _page(
            "b.html", "Plan Bee Page Title Here", ["Plan Bee"],
            '<a href="index.html">back to plan</a> ' + _FILLER * 2,
            desc="Plan bee description here."),
        "sitemap.json": json.dumps({"pages": [
            {"file": "index.html", "links": ["a.html"]},
            {"file": "a.html", "links": []},
            {"file": "b.html", "links": []},
        ]}),
    })
    rows = _rows(site)
    _expect(rows, "plan_links", "FAIL", "index.html: planned link to a.html not in HTML")
    _expect(rows, "sitemap_parity", "PASS")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="sc-seo-") as tmp:
        root = Path(tmp)
        _scenario_multi(root)
        _scenario_robots(root)
        _scenario_staging(root)
        _scenario_sitemap(root)
        _scenario_schema_fail(root)
        _scenario_schema_warn(root)
        _scenario_plan(root)
    print("check_seo selftest ok (7 scenarios, 17 rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
