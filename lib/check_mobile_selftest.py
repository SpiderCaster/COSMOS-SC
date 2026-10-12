"""Mobile gates selftest: sideways_scroll, mobile_nav_drawer, mobile_visibility, mobile_spec, and the
360/390/412px viewport set of type_floor and tap_target.

Run: python lib/check_mobile_selftest.py
Fixtures: lib/fixtures/mobile/* (each folder is a tiny site). Every gate has a failing fixture, a passing
fixture and a mutation check (break the rule on purpose; the fixtures must notice).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib import check as ck

MOB = Path(__file__).resolve().parent / "fixtures" / "mobile"
LINE = re.compile(r"^[^|]+ \| [^|]+ \| [^|]+ \| (static|rendered)[^|]* \| at \d+(,\d+)*px$")


def _fail(message: str) -> None:
    raise SystemExit("mobile selftest: " + message)


def _expect(cond: bool, message: str) -> None:
    if not cond:
        _fail(message)


def _pages(name: str) -> list[Path]:
    return sorted((MOB / name).glob("*.html"))


def _scan(name: str) -> dict:
    return ck.mobile_scan(_pages(name))


def _rows(name: str, spec=None) -> dict:
    rep = ck.Report(quiet=True)
    ck._mobile_rows(rep, _pages(name), spec)
    return {r["name"]: r for r in rep.rows}


def _sels(rows: list[dict]) -> set[str]:
    return {r["selector"] for r in rows}


def _lines_ok(rows: list[dict]) -> None:
    for rec in rows:
        line = ck.failure_line(rec)
        _expect(LINE.match(line) is not None, "line format: " + line)
        _expect(rec["file"] and rec["selector"] and rec["measured"], "file, selector and measured value: " + line)


def _scroll() -> None:
    bad = _scan("scroll_fail")["sideways_scroll"]
    want = {".wide", ".minw", ".vw", '.bleed', ".nw", ".mid", "pre", 'img[width="800"] (no max-width)',
            "p text", "table (6 columns, min-content estimate)"}
    _expect(_sels(bad["fails"]) == want, f"scroll_fail selectors {sorted(_sels(bad['fails']))}")
    by = {r["selector"]: r for r in bad["fails"]}
    _expect(by[".wide"]["measured"] == "measured width 416px > viewport 360px", by[".wide"]["measured"])
    _expect(by[".mid"]["viewports"] == [360], ".mid (350px + 16px gutter) overflows at 360px only")
    _expect(by[".minw"]["viewports"] == [360, 390], ".minw (380px + 16px) overflows at 360 and 390px")
    _expect(by[".wide"]["viewports"] == [360, 390, 412], ".wide overflows at every phone width")
    _expect(ck.failure_line(by[".wide"]).startswith(
        "index.html | .wide | measured width 416px > viewport 360px | static"), ck.failure_line(by[".wide"]))
    _lines_ok(bad["fails"])
    ok = _scan("scroll_pass")["sideways_scroll"]
    _expect(not ok["fails"] and not ok["warns"], f"scroll_pass: {ok['fails'] + ok['warns']}")
    r = _rows("scroll_fail")["sideways_scroll"]
    _expect(r["status"] == "FAIL" and len(r["failures"]) == 10, "scroll_fail row")
    _expect(_rows("scroll_pass")["sideways_scroll"]["status"] == "PASS", "scroll_pass row")


def _drawer() -> None:
    cases = {
        "drawer_fail_notoggle": {"7 nav links shown inline, no menu toggle (needs a toggle above 4 links)"},
        "drawer_fail_hidden": {"primary nav (6 links) hidden (display:none from .menu) and no visible menu toggle: "
                               "links unreachable"},
        "drawer_fail_toggle": {"menu toggle is <a>, not a button (needs <button> or role=button)",
                               "no aria-expanded on the menu toggle (needs aria-expanded=\"false\" when closed)",
                               "menu toggle has no accessible name (needs aria-label, text or aria-labelledby)",
                               "menu toggle measured 24x24px (needs >= 44px)"},
        "drawer_fail_controls": {"aria-controls=\"nope\" names no element with id nope",
                                 "aria-expanded=\"true\" while the drawer is hidden (needs \"false\")"},
        "drawer_fail_open_default": {"drawer shown by default (needs hidden until the toggle opens it)"},
        "drawer_fail_no_open_rule": {"opening (classes .open) leaves the drawer hidden"},
        "drawer_fail_no_close": {"no close mechanism (needs a toggle that flips back, a close button inside the "
                                 "drawer, or Escape)"},
        "drawer_fail_no_script": {"drawer has no way to open: no script, no native dialog/popover"},
    }
    for name, want in cases.items():
        got = _scan(name)["mobile_nav_drawer"]
        _expect({r["measured"] for r in got["fails"]} == want, f"{name}: {sorted(r['measured'] for r in got['fails'])}")
        for r in got["fails"]:
            _expect(r["viewports"] == [360, 390, 412], f"{name}: judged at every phone width")
        _lines_ok(got["fails"])
        _expect(_rows(name)["mobile_nav_drawer"]["status"] == "FAIL", f"{name} row")
    for name in ("drawer_pass", "drawer_inline_ok"):
        got = _scan(name)["mobile_nav_drawer"]
        _expect(not got["fails"] and not got["warns"], f"{name}: {got['fails'] + got['warns']}")
        _expect(_rows(name)["mobile_nav_drawer"]["status"] == "PASS", f"{name} row")
    detail = _rows("drawer_pass")["mobile_nav_drawer"]["detail"]
    _expect("opens by .open" in detail and "Escape key" in detail, detail)
    skip = _rows("drawer_no_nav")["mobile_nav_drawer"]
    _expect(skip["status"] == "SKIP" and "not-run" in skip["detail"], "no nav landmark is not-run, never pass")


def _visibility() -> None:
    bad = _rows("vis_fail")["mobile_visibility"]
    _expect(bad["status"] == "FAIL" and [f["selector"] for f in bad["failures"]] == ["h1"], f"vis_fail {bad}")
    _expect(bad["failures"][0]["viewports"] == [360, 390, 412], "h1 hidden at every phone width")
    _expect([w["selector"] for w in bad.get("unmeasured", [])] == ["p.promo"], "content hidden on phones is WARN")
    _expect(any(i["selector"] == "a.mobile-cta" and i["measured"].startswith("shown only at phone widths")
                for i in bad.get("inventory", [])), "mobile-only CTA in the inventory")
    _lines_ok(bad["failures"])
    ok = _rows("vis_pass")["mobile_visibility"]
    _expect(ok["status"] == "PASS", f"vis_pass {ok}")
    inv = {i["selector"]: i["measured"] for i in ok.get("inventory", [])}
    _expect(inv.get("a.mobile-cta", "").startswith("shown only") and inv.get("div.deco", "").startswith("hidden at"),
            f"vis_pass inventory {inv}")
    d = _rows("drawer_pass")["mobile_visibility"]
    _expect(d["status"] == "PASS", "a drawer hidden on phones is expected, not a content loss")


def _widths() -> None:
    t = ck.typography_scan(_pages("type_vw"))
    got = {(r["measured"], tuple(r["viewports"])) for r in t["type_floor"]}
    _expect(got == {("16.56px", (360,)), ("17.94px", (390,))}, f"4.6vw body text fails at 360 and 390 only: {got}")
    tap = ck.tap_scan(_pages("tap_vw"))
    _expect([(r["selector"], r["viewports"]) for r in tap["fails"]] == [(".vbtn", [360, 390])],
            f"10.7vw button fails at 360 and 390 only: {tap['fails']}")


def _spec() -> None:
    v1 = _rows("drawer_pass", MOB / "spec" / "v1_overflow")["mobile_spec"]
    _expect(v1["status"] == "FAIL", f"v1 spec {v1}")
    ms = {f["measured"] for f in v1["failures"]}
    _expect("measured width 420px > viewport 360px" in ms, f"spec overflow {ms}")
    _expect(any(m.startswith("tap on the menu toggle failed") for m in ms), f"spec drawer fail {ms}")
    _expect(all(f["mode"].startswith("rendered") for f in v1["failures"]), "spec rows say rendered")
    _lines_ok(v1["failures"])
    v2 = _rows("drawer_pass", MOB / "spec" / "v2_clean")["mobile_spec"]
    _expect(v2["status"] == "PASS", f"v2 spec {v2}")
    gone = _rows("drawer_pass", MOB / "spec" / "missing.json")["mobile_spec"]
    _expect(gone["status"] == "SKIP" and "not-run" in gone["detail"], "unreadable spec is not-run")
    _expect("mobile_spec" not in _rows("drawer_pass"), "no --mobile-spec: no mobile_spec row")


def _cli() -> None:
    def run(*args: str) -> tuple[int, str]:
        proc = subprocess.run([sys.executable, "-m", "lib.check", *args], cwd=str(_ROOT), capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=120)
        return proc.returncode, proc.stdout
    code, out = run(str(MOB / "drawer_pass"), "--mobile-only")
    _expect(code == 0 and "[pass] mobile_nav_drawer" in out and "[pass] sideways_scroll" in out
            and "at 360+390+412px" in out, "CLI --mobile-only pass")
    code, out = run(str(MOB / "scroll_fail"), "--mobile-only")
    _expect(code == 1 and "index.html | .wide | measured width 416px > viewport 360px | static" in out, "CLI fail")
    code, out = run(str(MOB / "drawer_pass"), "--mobile-only", "--mobile-spec", str(MOB / "spec" / "v1_overflow"))
    _expect(code == 1 and "[FAIL] mobile_spec" in out, "CLI --mobile-spec PATH")
    code, out = run(str(MOB / "drawer_pass"), "--mobile-only", "--mobile-spec=" + str(MOB / "spec" / "v2_clean"))
    _expect(code == 0 and "[pass] mobile_spec" in out, "CLI --mobile-spec=PATH")
    code, _ = run(str(MOB / "drawer_pass"), "--mobile-spec")
    _expect(code == 2, "--mobile-spec with no path is a usage error")


def _mutations() -> None:
    saved = (ck.MOBILE_VIEWPORTS, ck._mob_contained, ck.MOBILE_NAV_INLINE_MAX, ck.TAP_MIN_PX, ck._MOB_CLASS_RE,
             ck._MOB_ESCAPE_RE, ck._MOB_TOGGLE_RE, ck._MOB_EXPANDED_RE)
    try:
        ck.MOBILE_VIEWPORTS = ((2000, 1000),)  # desktop-wide "phone": scroll_fail must clear, so widths matter
        left = _sels(_scan("scroll_fail")["sideways_scroll"]["fails"])
        _expect(left == {".vw", ".bleed"}, f"mutation: at 2000px only the 110vw box and the -40px bleed still "
                f"overflow, got {sorted(left)}")
        _expect(not _scan("vis_fail")["mobile_visibility"]["fails"], "mutation: 2000px clears the hidden h1")
        ck.MOBILE_VIEWPORTS = saved[0]
        ck._mob_contained = lambda *a, **k: ""  # no clipping ancestors: scroll_pass's scroller must now fail
        _expect(_scan("scroll_pass")["sideways_scroll"]["fails"], "mutation: ignoring overflow-x:auto must fail")
        ck._mob_contained = saved[1]
        ck.MOBILE_NAV_INLINE_MAX = 99  # lifted link limit: 7 inline links must stop failing
        _expect(not _scan("drawer_fail_notoggle")["mobile_nav_drawer"]["fails"], "mutation: link limit lifted")
        ck.MOBILE_NAV_INLINE_MAX = saved[2]
        ck.TAP_MIN_PX = 1.0  # loosened tap floor: the 24px toggle must stop failing on size
        ms = {r["measured"] for r in _scan("drawer_fail_toggle")["mobile_nav_drawer"]["fails"]}
        _expect("menu toggle measured 24x24px (needs >= 44px)" not in ms, "mutation: 1px floor clears toggle size")
        ck.TAP_MIN_PX = saved[3]
        ck._MOB_CLASS_RE = re.compile(r"(?!x)x")  # no open state found: drawer_pass must stop passing
        _expect(_scan("drawer_pass")["mobile_nav_drawer"]["warns"], "mutation: no open state is not a pass")
        ck._MOB_CLASS_RE = saved[4]
        ck._MOB_ESCAPE_RE = re.compile(r"(?!x)x")
        ck._MOB_TOGGLE_RE = re.compile(r"(?!x)x")
        ck._MOB_EXPANDED_RE = re.compile(r"(?!x)x")  # blind to every close signal: drawer_pass must fail
        ms = {r["measured"] for r in _scan("drawer_pass")["mobile_nav_drawer"]["fails"]}
        _expect(any(m.startswith("no close mechanism") for m in ms), f"mutation: close detection off: {ms}")
    finally:
        (ck.MOBILE_VIEWPORTS, ck._mob_contained, ck.MOBILE_NAV_INLINE_MAX, ck.TAP_MIN_PX, ck._MOB_CLASS_RE,
         ck._MOB_ESCAPE_RE, ck._MOB_TOGGLE_RE, ck._MOB_EXPANDED_RE) = saved
    _expect(len(_scan("scroll_fail")["sideways_scroll"]["fails"]) == 10, "mutations restored")
    _expect(not _scan("drawer_pass")["mobile_nav_drawer"]["fails"], "drawer mutations restored")


def main() -> int:
    _scroll()
    _drawer()
    _visibility()
    _widths()
    _spec()
    _cli()
    _mutations()
    print("mobile selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
