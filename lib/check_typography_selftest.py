"""Type floor, WCAG contrast and reproducibility checks.

Run: python lib/check_typography_selftest.py
Fixtures: lib/fixtures/typography/{pass,fail_type,fail_contrast,fail_external}
          lib/fixtures/reproducibility/{same_a,same_b,diff_a,diff_b}
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib import check as ck

FIX = Path(__file__).resolve().parent / "fixtures"
TYPO = FIX / "typography"
REPRO = FIX / "reproducibility"


def _fail(message: str) -> None:
    raise SystemExit("typography selftest: " + message)


def _expect(cond: bool, message: str) -> None:
    if not cond:
        _fail(message)


def _scan(name: str) -> dict:
    return ck.typography_scan(sorted((TYPO / name).glob("*.html")))


def _keys(rows: list[dict]) -> set[tuple[str, str, str]]:
    return {(r["file"], r["selector"], r["measured"]) for r in rows}


def _units() -> None:
    _expect(abs(ck.contrast_ratio((0, 0, 0), (255, 255, 255)) - 21.0) < 1e-9, "black on white is 21:1")
    _expect(ck.contrast_ratio((0x76,) * 3, (255,) * 3) >= 4.5, "#767676 on white passes 4.5:1")
    _expect(ck.contrast_ratio((0x77,) * 3, (255,) * 3) < 4.5, "#777777 on white fails 4.5:1")
    ctx = ck._Ctx(1000, 800)
    ctx.root = 18.0
    _expect(ck._eval_len("clamp(1.6rem,3vw,2.3rem)", 18.0, ctx, 18.0) == 30.0, "clamp with vw")
    _expect(ck._eval_len("calc(1rem + 2px)", 18.0, ctx, 18.0) == 20.0, "calc")
    _expect(ck._eval_len("max(16px,1rem)", 18.0, ctx, 18.0) == 18.0, "max")
    _expect(ck._eval_len("120%", 10.0, ctx, 10.0) == 12.0, "percent of parent")
    _expect(ck._subst_vars("var(--a, 4px)", {}) == "4px", "var fallback")
    _expect(ck._subst_vars("var(--a)", {"--a": "var(--b)", "--b": "7px"}) == "7px", "nested var")
    _expect(ck._subst_vars("var(--missing)", {}) is None, "unresolved var")
    _expect(ck._parse_color("rgb(10 14 20 / 50%)") == (10.0, 14.0, 20.0, 0.5), "space rgb with alpha")
    _expect(ck._parse_color("#fff") == (255.0, 255.0, 255.0, 1.0), "short hex")
    _expect(ck._parse_color("hsl(0 100% 50%)")[:3] == (255.0, 0.0, 0.0), "hsl red")
    _expect(ck._parse_color("oklch(0.5 0.1 20)") is None, "unsupported colour is None")
    _expect(ck._parse_selector(".a .b > c#d:not(.e)").spec == (1, 3, 1), "specificity")
    _expect(not ck._parse_selector("a:hover").ok, ":hover rules are not judged")
    _expect(not ck._parse_selector("p::before").ok, "pseudo-elements are not judged")
    _expect(ck._media_matches("(max-width:600px)", 360, 740), "media max-width on phone")
    _expect(not ck._media_matches("(max-width:600px)", 1280, 800), "media max-width on desktop")
    _expect(ck._media_matches("screen and (min-width: 861px)", 1280, 800), "media min-width")
    _expect(not ck._media_matches("(prefers-reduced-motion: reduce)", 1280, 800), "reduced motion off")
    _expect(not ck._media_matches("print", 1280, 800), "print off")
    _expect(ck._media_matches("(width >= 600px) and (width <= 1400px)", 1280, 800), "range syntax")


def _fixtures() -> None:
    ok = _scan("pass")
    _expect(not ok["type_floor"] and not ok["contrast"], "pass fixture produced a failure")
    _expect(ok["min_size"] is not None and ok["min_size"] >= 16.0, "pass fixture smallest size")
    _expect(ok["min_ratio"] is not None and ok["min_ratio"] >= 3.0, "pass fixture lowest ratio")
    _expect(not ok["unmeasured"], "pass fixture had unmeasured text")

    bad = _scan("fail_type")
    want = {
        ("index.html", ".fineprint", "15px"),
        ("index.html", ".tag", "15.3px"),
        ("index.html", ".tight", "14.4px"),
        ("index.html", "h6 [browser default]", "12.06px"),
        ("index.html", "p.note", "17px"),
        ("index.html", "style attribute", "14px"),
        ("index.html", ".go", "17px"),
    }
    _expect(_keys(bad["type_floor"]) == want, f"fail_type failures were {sorted(_keys(bad['type_floor']))}")
    _expect(not bad["contrast"], "fail_type should not fail contrast")
    by_sel = {r["selector"]: r for r in bad["type_floor"]}
    _expect(by_sel[".tight"]["viewports"] == [360], ".tight must fail on the phone viewport only")
    _expect(by_sel["p.note"]["required"] == "18px" and by_sel[".fineprint"]["required"] == "16px",
            "body floor is 18px, ui floor is 16px")
    _expect(by_sel[".go"]["required"] == "18px", "buttons are body text: 18px")

    low = _scan("fail_contrast")
    want = {
        ("about.html", ".sub", "2.32:1"),
        ("index.html", ".big-faint", "1.91:1"),
        ("index.html", ".cta", "1.00:1"),
        ("index.html", ".dark .dim", "2.13:1"),
        ("index.html", ".faint", "2.84:1"),
        ("index.html", ".ghost", "2.10:1"),
        ("index.html", ".mid", "3.54:1"),
        ("index.html", ".soft", "2.61:1"),
    }
    _expect(_keys(low["contrast"]) == want, f"fail_contrast failures were {sorted(_keys(low['contrast']))}")
    _expect(not low["type_floor"], "fail_contrast should not fail type_floor")
    by_sel = {r["selector"]: r for r in low["contrast"]}
    _expect(by_sel[".big-faint"]["required"] == "3:1", "large text needs 3:1")
    _expect(by_sel[".faint"]["required"] == "4.5:1", "body text needs 4.5:1")
    _expect(".mid-bold" not in by_sel, "20px bold at 3.54:1 is large text and passes")

    ext = _scan("fail_external")
    want = {("index.html", ".small", "14px"), ("index.html", ".dim", "2.32:1")}
    _expect(_keys(ext["type_floor"] + ext["contrast"]) == want, "external stylesheet failures")


def _rows() -> None:
    for name, type_status, contrast_status in (
        ("pass", "PASS", "PASS"), ("fail_type", "FAIL", "PASS"),
        ("fail_contrast", "PASS", "FAIL"), ("fail_external", "FAIL", "FAIL"),
    ):
        rep = ck.check_site(TYPO / name, quiet=True)
        rows = {r["name"]: r for r in rep.rows}
        _expect(rows["type_floor"]["status"] == type_status, f"{name} type_floor row")
        _expect(rows["contrast"]["status"] == contrast_status, f"{name} contrast row")
        _expect("failures" in rows["type_floor"] and "failures" in rows["contrast"], f"{name} failures key")
    rep = ck.check_site(TYPO / "fail_type", quiet=True, typography=False)
    _expect(not any(r["name"] in ("type_floor", "contrast") for r in rep.rows), "typography=False")
    line = ck.failure_line(_scan("fail_type")["type_floor"][0])
    _expect(line.startswith("index.html | .fineprint | font-size 15px (needs >= 16px)"), f"line format: {line}")


def _cli() -> None:
    def run(name: str) -> tuple[int, str]:
        proc = subprocess.run(
            [sys.executable, "-m", "lib.check", str(TYPO / name), "--typography-only"],
            cwd=str(_ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
        return proc.returncode, proc.stdout
    code, out = run("pass")
    _expect(code == 0 and "[pass] type_floor" in out and "[pass] contrast" in out, "CLI pass fixture")
    code, out = run("fail_type")
    _expect(code == 1 and "index.html | .fineprint | font-size 15px" in out, "CLI fail_type fixture")
    code, out = run("fail_contrast")
    _expect(code == 1 and "about.html | .sub | contrast 2.32:1 (needs >= 4.5:1)" in out, "CLI fail_contrast fixture")


def _copy_tree_builder(src: Path):
    def build(project: Path, out: Path) -> None:
        out.mkdir(parents=True, exist_ok=True)
        for item in src.rglob("*"):
            target = out / item.relative_to(src)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.write_bytes(item.read_bytes())
    return build


def _repro() -> None:
    same, total = ck.compare_trees(REPRO / "same_a", REPRO / "same_b")
    _expect(not same and total == 3, "identical trees compare equal")
    diffs, _ = ck.compare_trees(REPRO / "diff_a", REPRO / "diff_b")
    got = {d["file"]: d for d in diffs}
    _expect(set(got) == {"index.html", "mark.bin", "only_first.txt", "only_second.txt", "report.json"},
            f"differing files were {sorted(got)}")
    _expect(got["report.json"]["where"] == "key built_at", "report.json names the built_at key")
    _expect(got["report.json"]["first"] == "2026-10-03 20:00:00"
            and got["report.json"]["second"] == "2026-10-03 20:00:07", "built_at values")
    _expect(got["index.html"]["where"] == "line 3", "index.html first differing line")
    _expect(got["mark.bin"]["where"] == "byte 15", "binary first differing byte")
    _expect(got["only_first.txt"]["kind"] == "only in first build"
            and got["only_second.txt"]["kind"] == "only in second build", "one-sided files")
    line = ck.failure_line(got["report.json"])
    _expect(line.startswith("report.json | differs at key built_at | build1="), f"repro line: {line}")

    rep = ck.check_reproducible(TYPO, quiet=True, build=_copy_tree_builder(REPRO / "same_a"))
    _expect(rep.rows[0]["status"] == "PASS", "same trees pass check_reproducible")

    counter = {"n": 0}

    def alternating(project: Path, out: Path) -> None:
        counter["n"] += 1
        _copy_tree_builder(REPRO / ("diff_a" if counter["n"] % 2 else "diff_b"))(project, out)

    rep = ck.check_reproducible(TYPO, quiet=True, build=alternating)
    row = rep.rows[0]
    _expect(row["status"] == "FAIL" and len(row["failures"]) == 5, "differing trees fail check_reproducible")
    _expect("report.json: key built_at" in row["detail"], "detail names report.json and built_at")

    rep = ck.check_reproducible(TYPO / "missing-project", quiet=True)
    _expect(rep.rows[0]["status"] == "FAIL", "missing project fails")

    # End to end against the real offline build (skipped when the project is absent).
    project = _ROOT.joinpath(*ck.REPRO_DEFAULT_PROJECT)
    if not project.is_dir() or not (_ROOT / "spidercaster.py").is_file():
        return
    saved = {k: os.environ.pop(k, None) for k in ("SOURCE_DATE_EPOCH", "SPIDERCASTER_STAMP_BUILD")}
    try:
        rep = ck.check_reproducible(project, quiet=True)
        _expect(rep.rows[0]["status"] == "PASS", "demo-local rebuilds byte-identical: " + rep.rows[0]["detail"])
        os.environ["SOURCE_DATE_EPOCH"] = "1700000000"
        rep = ck.check_reproducible(project, quiet=True)
        _expect(rep.rows[0]["status"] == "PASS", "SOURCE_DATE_EPOCH keeps the stamp reproducible")
        del os.environ["SOURCE_DATE_EPOCH"]
        os.environ["SPIDERCASTER_STAMP_BUILD"] = "1"
        calls = {"n": 0}

        def slow(p: Path, out: Path) -> None:
            calls["n"] += 1
            if calls["n"] == 2:
                time.sleep(1.2)
            ck._offline_build(p, out)

        rep = ck.check_reproducible(project, quiet=True, build=slow)
        row = rep.rows[0]
        _expect(row["status"] == "FAIL" and any(
            d["file"] == "report.json" and d["where"] == "key built_at" for d in row["failures"]),
            "wall-clock stamp must fail on report.json built_at: " + row["detail"])
    finally:
        for key in ("SOURCE_DATE_EPOCH", "SPIDERCASTER_STAMP_BUILD"):
            os.environ.pop(key, None)
            if saved[key] is not None:
                os.environ[key] = saved[key]


def main() -> int:
    _units()
    _fixtures()
    _rows()
    _cli()
    _repro()
    print("typography selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
