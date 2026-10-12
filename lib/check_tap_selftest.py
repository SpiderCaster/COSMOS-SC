"""Tap target row and the other GATES.md rows (slug_shape, photo_luma, svg_photo, grey_tile).

Run: python lib/check_tap_selftest.py
Fixtures: lib/fixtures/tap/{pass,fail,warn,roles_pass,roles_fail}; temp sites built in-process for the slug,
luma and svg rows. Mutation checks break the rule on purpose and the fixtures must notice.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib import check as ck

TAP = Path(__file__).resolve().parent / "fixtures" / "tap"
LINE = re.compile(r'^[^|]+ \| [^|]+ \| measured [^|]+px \(needs >= 44px\) \| static; <[^>]+> ".*"( \(x\d+\))? \| at 360(,390)?(,412)?px$')


def _fail(message: str) -> None:
    raise SystemExit("tap selftest: " + message)


def _expect(cond: bool, message: str) -> None:
    if not cond:
        _fail(message)


def _scan(name: str) -> dict:
    return ck.tap_scan(sorted((TAP / name).glob("*.html")))


def _keys(rows: list[dict]) -> set[tuple[str, str, str]]:
    return {(r["file"], r["selector"], r["measured"]) for r in rows}


def _units() -> None:
    e = ck._expand_decl
    _expect(e("padding", "4px 8px") == [("padding-top", "4px"), ("padding-right", "8px"),
                                        ("padding-bottom", "4px"), ("padding-left", "8px")], "padding shorthand")
    _expect(dict(e("border", "1px solid red"))["border-top-width"] == "1px", "border shorthand width")
    _expect(dict(e("border", "0"))["border-left-style"] == "none", "border 0 has no style")
    _expect(dict(e("padding-block", "6px 2px"))["padding-bottom"] == "2px", "padding-block")
    _expect(dict(e("font", "600 1rem/1.4 serif"))["line-height"] == "1.4", "font shorthand line-height")
    _expect(dict(e("font", "600 1rem / 28px serif"))["line-height"] == "28px", "font shorthand spaced slash")
    _expect(dict(e("font", "600 1rem serif"))["line-height"] == "normal", "font shorthand resets line-height")
    _expect(ck._tap_fmt((44.0, 44.0)) == "44" and ck._tap_fmt((20.0, _inf())) == ">=20"
            and ck._tap_fmt((10.0, 20.5)) == "10-20.5", "interval format")
    _expect(ck.slug_problems("harbor-tea-room") == [], "good slug")
    for bad, why in (("Harbor-Tea", "uppercase"), ("harbor_tea", "underscore"), ("harbor-tea-2026-05-01", "date"),
                     ("harbor-tea-2", "trailing number/pass/batch suffix"), ("harbor-tea-final", "trailing number/pass/batch suffix"),
                     ("a-b-c-d-e-f-g", "7 words"), ("x" * 61, "61 chars")):
        _expect(why in ck.slug_problems(bad), f"slug {bad!r} should report {why}: {ck.slug_problems(bad)}")


def _inf() -> float:
    return float("inf")


def _tap_fixtures() -> None:
    ok = _scan("pass")
    _expect(not ok["fails"] and not ok["warns"], f"pass fixture produced {ok['fails'] + ok['warns']}")
    _expect(ok["exempt"] == 1, "the inline link in a sentence is exempt (WCAG 2.5.8)")
    _expect(ok["checked"] == 7 and ok["hidden_ok"] == 2, f"pass fixture counts {ok['checked']}/{ok['hidden_ok']}")
    bad = _scan("fail")
    want = {
        ("index.html", ".b1", "100x32px"),
        ("index.html", ".i1", "200x28px"),
        ("index.html", ".icon", "24x24px"),
        ("index.html", ".pseudo", "60x20px"),
        ("index.html", ".strip", "[fill]x30px"),
        ("index.html", ".tight", "28.6-44.8x35px"),
        ("index.html", "a [no size rule: browser default]", "25.2-57.6x18-27px"),
        ("index.html", "summary", "[fill]x35px"),
    }
    _expect(_keys(bad["fails"]) == want, f"fail fixture was {sorted(_keys(bad['fails']))}")
    _expect(not bad["warns"], "fail fixture should not warn")
    for rec in bad["fails"]:
        _expect(LINE.match(ck.failure_line(rec)) is not None, "line format: " + ck.failure_line(rec))
    warn = _scan("warn")
    _expect(not warn["fails"], "warn fixture must not fail")
    _expect(len(warn["warns"]) == 3, f"warn fixture warns: {warn['warns']}")
    reasons = " ".join(w["extra"] for w in warn["warns"])
    _expect("unresolved var() in padding" in reasons and "no guaranteed 44px minimum" in reasons, reasons)


def _tap_rows() -> None:
    rows = {n: {r["name"]: r for r in ck.check_site(TAP / n, quiet=True).rows}["tap_target"] for n in ("pass", "fail", "warn")}
    _expect(rows["pass"]["status"] == "PASS" and "static" in rows["pass"]["detail"], "pass row")
    _expect(rows["fail"]["status"] == "FAIL" and len(rows["fail"]["failures"]) == 8, "fail row")
    _expect(rows["warn"]["status"] == "WARN" and rows["warn"]["status"] != "PASS", "unmeasurable is WARN, never PASS")
    _expect(len(rows["warn"]["unmeasured"]) == 3, "warn row lists the unmeasured controls")
    only = ck.Report(quiet=True)
    ck._tap_rows(only, sorted((TAP / "warn").glob("*.html")))
    _expect(only.ok() and only.counts()["WARN"] == 1, "WARN does not fail the gate")
    _expect(not any(r["name"] == "tap_target" for r in ck.check_site(TAP / "fail", quiet=True, tap_targets=False).rows),
            "tap_targets=False")


def _cli() -> None:
    def run(name: str) -> tuple[int, str]:
        proc = subprocess.run([sys.executable, "-m", "lib.check", str(TAP / name), "--tap-only"], cwd=str(_ROOT),
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        return proc.returncode, proc.stdout
    code, out = run("pass")
    _expect(code == 0 and "[pass] tap_target" in out, "CLI pass")
    code, out = run("fail")
    _expect(code == 1 and "index.html | .b1 | measured 100x32px (needs >= 44px) | static; <button.b1> \"Save\" | at 360,390,412px" in out,
            "CLI fail")
    code, out = run("warn")
    _expect(code == 0 and "[warn] tap_target" in out and "not measurable" in out, "CLI warn")


def _mutations() -> None:
    saved = (ck.TAP_MIN_PX, ck._tap_exempt_inline, ck._tap_kind)
    try:
        ck.TAP_MIN_PX = 1.0  # loosened floor: the fail fixture must stop failing, so the test would notice
        _expect(not _scan("fail")["fails"], "mutation: a 1px floor must clear the fail fixture")
        ck.TAP_MIN_PX = saved[0]
        ck._tap_exempt_inline = lambda *a, **k: False  # no inline exception: the sentence link must now fail
        _expect(_keys(_scan("pass")["fails"]), "mutation: without the inline exception the pass fixture must fail")
        ck._tap_exempt_inline = saved[1]
        ck._tap_kind = lambda node: None  # nothing is interactive: the fail fixture must see nothing
        _expect(not _scan("fail")["fails"], "mutation: no interactive elements must clear the fail fixture")
    finally:
        ck.TAP_MIN_PX, ck._tap_exempt_inline, ck._tap_kind = saved
    _expect(len(_scan("fail")["fails"]) == 8, "mutations restored")


def _roles() -> None:
    """role=link/tab/menuitem/button on non-native elements are interactive; mutation: drop the extra roles."""
    bad = _scan("roles_fail")
    _expect(_keys(bad["fails"]) == {("index.html", ".rl", "90x30px"), ("index.html", ".rt", "80x32px"),
                                    ("index.html", ".rm", "120x28px"), ("index.html", ".rb", "60x20px")},
            f"roles_fail fixture was {sorted(_keys(bad['fails']))}")
    ok = _scan("roles_pass")
    _expect(not ok["fails"] and not ok["warns"] and ok["checked"] == 4, f"roles_pass fixture: {ok}")
    saved = ck._tap_kind

    def old_kind(node):  # the pre-fix finder: only role=button
        if node.attrs.get("role", "").strip().lower() in ("link", "tab", "menuitem") and node.tag != "a":
            return None
        return saved(node)
    try:
        ck._tap_kind = old_kind
        left = {r[1] for r in _keys(_scan("roles_fail")["fails"])}
        _expect(left == {".rb"}, f"mutation: without link/tab/menuitem roles only .rb is found, got {left}")
    finally:
        ck._tap_kind = saved
    _expect(len(_scan("roles_fail")["fails"]) == 4, "roles mutation restored")


def _site(root: Path, files: dict[str, str]) -> Path:
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


def _rows_of(site: Path) -> dict:
    return {r["name"]: r for r in ck.check_site(site, quiet=True).rows}


def _gates() -> None:
    page = "<!doctype html><html lang=en><head><title>t</title></head><body><main><p>hi there friend</p>{}</main></body></html>"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        good = _site(tmp / "good", {"index.html": page.format(""), "harbor-tea-menu.html": page.format("")})
        r = _rows_of(good)
        _expect(r["slug_shape"]["status"] == "PASS", "slug pass")
        _expect(r["grey_tile"]["status"] == "SKIP" and "not-run" in r["grey_tile"]["detail"], "grey_tile is an explicit not-run")
        _expect(r["svg_photo"]["status"] == "PASS" and r["photo_luma"]["status"] == "PASS", "no images: pass")
        bad = _site(tmp / "bad", {"index.html": page.format(""), "Harbor_Menu-2026-05-01.html": page.format(""),
                                  "tea-2.html": page.format("")})
        r = _rows_of(bad)["slug_shape"]
        _expect(r["status"] == "FAIL" and len(r["failures"]) == 2, "slug fail")
        lines = [ck.failure_line(f) for f in r["failures"]]
        _expect(any(l.startswith("Harbor_Menu-2026-05-01.html | Harbor_Menu-2026-05-01 | 5 word(s), 22 char(s): uppercase, underscore, date, trailing")
                    and "(needs <= 6 words" in l for l in lines), f"slug line: {lines}")
        _expect(any(l.startswith("tea-2.html | tea-2 |") for l in lines), "numeric suffix named")
        svg = _site(tmp / "svg", {"index.html": page.format('<img src="hero-thumb.svg" alt="x"><img src="logo.svg" alt="logo">'),
                                  "hero-thumb.svg": "<svg/>", "logo.svg": "<svg/>"})
        r = _rows_of(svg)["svg_photo"]
        _expect(r["status"] == "FAIL" and len(r["failures"]) == 1 and r["failures"][0]["selector"] == 'img[src="hero-thumb.svg"]',
                "svg as photo fails, a plain logo svg does not")
        try:
            from PIL import Image
        except ImportError:
            Image = None
        if Image is not None:
            lum = {}
            for name, level in (("dark", 20), ("mid", 128), ("bright", 240)):
                site = tmp / name
                site.mkdir()
                Image.new("RGB", (800, 600), (level, level, level)).save(site / "p.png")
                _site(site, {"index.html": page.format('<img src="p.png" alt="p">')})
                lum[name] = _rows_of(site)["photo_luma"]
            _expect(lum["mid"]["status"] == "PASS", "mid luma passes")
            for name in ("dark", "bright"):
                f = lum[name]["failures"][0]
                _expect(lum[name]["status"] == "FAIL" and f["file"] == "index.html" and f["selector"] == 'img[src="p.png"]'
                        and f["required"] == "90-200" and f["measured"].startswith("mean luma"), f"{name} luma fails with names")
            # not-run, never pass, when Pillow is unavailable
            saved = sys.modules.get("PIL")
            sys.modules["PIL"] = None
            try:
                skip = _rows_of(tmp / "mid")["photo_luma"]
            finally:
                if saved is not None:
                    sys.modules["PIL"] = saved
                else:
                    del sys.modules["PIL"]
            _expect(skip["status"] == "SKIP" and "not-run" in skip["detail"], "missing Pillow is a not-run row")
            # mutation: a widened luma band clears the dark image
            old = (ck.LUMA_MIN, ck.LUMA_MAX)
            ck.LUMA_MIN, ck.LUMA_MAX = 0.0, 255.0
            try:
                _expect(_rows_of(tmp / "dark")["photo_luma"]["status"] == "PASS", "mutation: widened band must clear dark")
            finally:
                ck.LUMA_MIN, ck.LUMA_MAX = old
    old = ck.SLUG_MAX_WORDS
    ck.SLUG_MAX_WORDS = 99
    try:
        _expect("7 words" not in ck.slug_problems("a-b-c-d-e-f-g"), "mutation: word limit lifted")
    finally:
        ck.SLUG_MAX_WORDS = old
    _expect("7 words" in ck.slug_problems("a-b-c-d-e-f-g"), "slug mutation restored")


def main() -> int:
    _units()
    _tap_fixtures()
    _tap_rows()
    _cli()
    _mutations()
    _roles()
    _gates()
    print("tap selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
