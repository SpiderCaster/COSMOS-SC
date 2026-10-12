"""Visit check selftest. Playwright is optional and is not required to pass.

Run from the engine root: python lib/visit_check_selftest.py
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.visit_check import visit_html, visit_site

_GOOD = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Visit</title>
</head>
<body>
<header class="site-header">Hi</header>
<main id="main">
<p><a href="#main">Top</a></p>
</main>
</body>
</html>
"""

_CODES = {"missing_header", "missing_main", "broken_hash", "missing_viewport", "sideways"}


def _fail(message: str) -> None:
    raise SystemExit("visit_check selftest FAIL: " + message)


def _expect(cond: bool, message: str) -> None:
    if not cond:
        _fail(message)


def _codes(html: str) -> list[str]:
    got = visit_html(html)
    _expect(set(got) == {"ok", "mode", "failures"}, f"shape {got}")
    _expect(got["mode"] == "static", f"visit_html mode {got}")
    _expect(got["ok"] is (not got["failures"]), f"ok flag {got}")
    codes = []
    for item in got["failures"]:
        _expect(set(item) == {"code", "detail"}, f"failure shape {item}")
        _expect(item["code"] in _CODES and item["detail"], f"failure {item}")
        codes.append(item["code"])
    return codes


def _static() -> None:
    _expect(_codes(_GOOD) == [], "good page should pass")
    broken = _GOOD.replace('href="#main"', 'href="#missing"')
    _expect(_codes(broken) == ["broken_hash"], "href #missing is broken_hash")
    _expect(
        'href="#missing"' in visit_html(broken)["failures"][0]["detail"],
        "broken_hash names the missing id",
    )
    no_header = _GOOD.replace('<header class="site-header">Hi</header>', "<div>Hi</div>")
    _expect(_codes(no_header) == ["missing_header"], "page without a header")
    only_tag = _GOOD.replace('<header class="site-header">', "<header>")
    _expect(_codes(only_tag) == [], "header element is enough")
    only_class = _GOOD.replace(
        '<header class="site-header">Hi</header>',
        '<div class="site-header">Hi</div>',
    )
    _expect(_codes(only_class) == [], "site-header class is enough")
    no_main = _GOOD.replace('id="main"', 'id="content"').replace('href="#main"', 'href="#content"')
    _expect(_codes(no_main) == ["missing_main"], "missing id=main")
    linked_main = _GOOD.replace('id="main"', 'id="content"')
    _expect(_codes(linked_main) == ["missing_main", "broken_hash"], "#main must exist")
    no_viewport = _GOOD.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
        "",
    )
    _expect(_codes(no_viewport) == ["missing_viewport"], "missing viewport")
    swapped = _GOOD.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta content="width=device-width, initial-scale=1" name="viewport">',
    )
    _expect(_codes(swapped) == [], "viewport meta attribute order")
    quoted = _GOOD.replace('id="main"', "id='main'").replace('href="#main"', "href='#main'")
    _expect(_codes(quoted) == [], "single quoted id and href")
    top = _GOOD.replace(
        '<a href="#main">Top</a>',
        '<a href="#">Top</a><a href="#main">Main</a>',
    )
    _expect(_codes(top) == [], "empty hash is not broken")
    case = _GOOD.replace('href="#main"', 'href="#Main"')
    _expect(_codes(case) == ["broken_hash"], "fragment ids are case sensitive")
    extra = _GOOD.replace(
        '<a href="#main">Top</a>',
        '<a id="extra" href="#extra">A</a>',
    )
    _expect(_codes(extra) == [], "hash to an existing id")
    commented = _GOOD.replace(
        '<header class="site-header">Hi</header>',
        '<!-- <header class="site-header">Hi</header> -->',
    )
    _expect(_codes(commented) == ["missing_header"], "commented header does not count")
    script = _GOOD.replace(
        "</head>",
        "<script>var h = '<a href=\"#missing\"></a>';</script></head>",
    )
    _expect(_codes(script) == [], "hash inside script is not a link")
    wide = _GOOD.replace("</head>", "<style>.box { width: 1400px; }</style></head>")
    wide_got = visit_html(wide)
    _expect(_codes(wide) == ["sideways"], f"fixed width {wide_got}")
    _expect("1400px > 1280px" in wide_got["failures"][0]["detail"], wide_got["failures"][0]["detail"])
    edge = _GOOD.replace("</head>", "<style>.box { width: 1280px; }</style></head>")
    _expect(_codes(edge) == [], "width 1280 is not over the limit")
    root_min = _GOOD.replace("</head>", "<style>html { min-width: 401px; }</style></head>")
    _expect(_codes(root_min) == ["sideways"], "min-width on html")
    _expect("401px > 400px" in visit_html(root_min)["failures"][0]["detail"], "min-width detail")
    body_edge = _GOOD.replace("<body>", '<body style="min-width:400px">')
    _expect(_codes(body_edge) == [], "min-width 400 on body is allowed")
    body_min = _GOOD.replace("<body>", '<body style="min-width:1400px">')
    body_got = visit_html(body_min)
    _expect(_codes(body_min) == ["sideways"], f"body min-width {body_got}")
    _expect(body_got["failures"][0]["detail"].startswith("min-width "), body_got["failures"][0]["detail"])
    card = _GOOD.replace("<main", '<main style="min-width:900px"')
    _expect(_codes(card) == [], "min-width on a div is not the body rule")
    child = _GOOD.replace(
        "</head>",
        "<style>body div { min-width: 800px; } .site-header { min-width: 700px; }</style></head>",
    )
    _expect(_codes(child) == [], "min-width on descendants is not body or html")
    desc = _GOOD.replace("</head>", "<style>div body { min-width: 800px; }</style></head>")
    _expect(_codes(desc) == ["sideways"], "descendant body selector still hits body")
    comma_ok = _GOOD.replace("</head>", "<style>div, p { min-width: 401px; }</style></head>")
    _expect(_codes(comma_ok) == [], "min-width on div and p")
    comma_bad = _GOOD.replace("</head>", "<style>div, body { min-width: 401px; }</style></head>")
    _expect(_codes(comma_bad) == ["sideways"], "grouped body selector")
    media_ok = _GOOD.replace(
        "</head>",
        "<style>@media (min-width: 1400px) { .box { width: 100px; } }</style></head>",
    )
    _expect(_codes(media_ok) == [], "media-query condition is not a width declaration")
    media_bad = _GOOD.replace(
        "</head>",
        "<style>@media (min-width: 20px) { .box { width: 1400px; } }</style></head>",
    )
    _expect(_codes(media_bad) == ["sideways"], "width inside a media query")
    comment_css = _GOOD.replace(
        "</head>",
        "<style>/* width: 4000px */ .a { max-width: 4000px; border-width: 2000px; }</style></head>",
    )
    _expect(_codes(comment_css) == [], "comments and max-width are not fixed width")
    attr = _GOOD.replace("</main>", '<img width="1400" alt=""></main>')
    _expect(_codes(attr) == ["sideways"], "element width attribute")
    attr_edge = _GOOD.replace("</main>", '<img width="1280" alt=""></main>')
    _expect(_codes(attr_edge) == [], "width attribute at 1280")
    star = _GOOD.replace("</head>", "<style>* { min-width: 401px; }</style></head>")
    _expect(_codes(star) == ["sideways"], "universal min-width applies to body")
    star_ok = _GOOD.replace(
        "</head>",
        "<style>* { min-width: 0; } * > div { min-width: 900px; }</style></head>",
    )
    _expect(_codes(star_ok) == [], "universal min-width 0 and child min-width")
    star_class = _GOOD.replace("</head>", "<style>*.card { min-width: 900px; }</style></head>")
    _expect(_codes(star_class) == [], "classed universal selector is not body or html")
    root = _GOOD.replace("</head>", "<style>:root { min-width: 401px; }</style></head>")
    _expect(_codes(root) == ["sideways"], ":root is html")
    is_ok = _GOOD.replace("</head>", "<style>:is(div, span) { min-width: 900px; }</style></head>")
    _expect(_codes(is_ok) == [], ":is without body or html")
    is_bad = _GOOD.replace("</head>", "<style>:is(div, body) { min-width: 900px; }</style></head>")
    _expect(_codes(is_bad) == ["sideways"], ":is(body) sets min-width on body")
    empty = visit_html("")
    _expect(
        [item["code"] for item in empty["failures"]] == ["missing_header", "missing_main", "missing_viewport"],
        f"empty page {empty}",
    )


def _site() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="sc-visit-"))
    index = tmp / "index.html"
    try:
        index.write_text(_GOOD, encoding="utf-8")
        good = visit_site(tmp)
        _expect(set(good) == {"ok", "mode", "failures"}, f"site shape {good}")
        _expect(good["mode"] in {"static", "rendered"}, f"site mode {good}")
        _expect(good["ok"] is True and good["failures"] == [], f"good index failed: {good}")

        index.write_text(_GOOD.replace('href="#main"', 'href="#missing"'), encoding="utf-8")
        broken = visit_site(tmp)
        _expect(
            any(item["code"] == "broken_hash" for item in broken["failures"]),
            f"temp index #missing: {broken}",
        )
        _expect(broken["ok"] is False, f"broken page should fail: {broken}")

        no_header_html = _GOOD.replace('<header class="site-header">Hi</header>', "<div>Hi</div>")
        index.write_text(no_header_html, encoding="utf-8")
        bare = visit_site(tmp)
        _expect(
            any(item["code"] == "missing_header" for item in bare["failures"]),
            f"temp index without header: {bare}",
        )

        wide_html = _GOOD.replace("</main>", '<div style="width:2000px">wide</div></main>')
        index.write_text(wide_html, encoding="utf-8")
        wide = visit_site(tmp)
        _expect(any(item["code"] == "sideways" for item in wide["failures"]), f"wide index: {wide}")
        if wide["mode"] == "rendered":
            details = [item["detail"] for item in wide["failures"] if item["code"] == "sideways"]
            _expect(any("scrollWidth" in detail and "390x800" in detail for detail in details), f"390 measure: {wide}")
            _expect(any("scrollWidth" in detail and "1280x800" in detail for detail in details), f"1280 measure: {wide}")
            _expect(
                not any(item["code"] == "missing_header" for item in wide["failures"]),
                f"visible header was marked missing: {wide}",
            )

        hidden_html = _GOOD.replace("<header", '<header style="display:none"')
        _expect(_codes(hidden_html) == [], "display none still has a header element")
        index.write_text(hidden_html, encoding="utf-8")
        hidden = visit_site(tmp)
        if hidden["mode"] == "static":
            _expect(hidden["ok"] is True, f"skipped render should keep the static pass: {hidden}")
        else:
            _expect(
                any(
                    item["code"] == "missing_header" and "visible" in item["detail"]
                    for item in hidden["failures"]
                ),
                f"hidden header should fail rendered: {hidden}",
            )

        missing = visit_site(tmp / "no-such-dir")
        _expect(missing["mode"] == "static" and missing["ok"] is False, f"missing index: {missing}")
        _expect(
            [item["code"] for item in missing["failures"]] == ["missing_header", "missing_main", "missing_viewport"],
            f"missing index codes: {missing}",
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    _static()
    _site()
    print("visit_check selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
