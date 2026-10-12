#!/usr/bin/env python3
r"""Self-test for the mobile gates in bench\mobile_bench.py.

Serves bench\fixtures\mobile\ from a stdlib server on 127.0.0.1 (random port), renders
every fixture at each viewport with the same capture + gate code the bench uses, and
asserts that each bad fixture fails exactly its own gate at every mobile viewport (at the
desktop viewport it may fail only its own gate or nothing), and that clean.html passes
every gate everywhere. No gate may be not-run. Also checks the not-run path: with
Playwright "missing", every gate reports not-run and the readiness verdict is NOT READY.

Usage (from V:\A\Ai\spidercaster\working):
  python bench\mobile_bench_selftest.py [--viewports 360x800,...] [--out-dir DIR]
Exit code: 0 all expectations met, 1 a gate did not bite (or bit the wrong fixture),
2 capture not-run (Playwright/Chrome missing) so nothing was proven.
"""
from __future__ import annotations

import argparse
import datetime
import functools
import http.server
import io
import json
import sys
import threading
import time
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mobile_bench as mb  # noqa: E402

FIX = HERE / "fixtures" / "mobile"
EXPECT = {
    "clean.html": set(),
    "overflow.html": {"overflow_x"},
    "tap30.html": {"tap_target_rendered"},
    "text12.html": {"type_floor_rendered"},
    "no_viewport.html": {"viewport_meta"},
    "grey_tile.html": {"grey_tile_rendered"},
    "nav_broken.html": {"nav_toggle"},
    "nav_clipped.html": {"nav_toggle"},
    "sticky_tall.html": {"sticky_25"},
    "img_nosrcset.html": {"img_srcset"},
}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve_dir(d: Path):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(d)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--viewports", default=mb.DEFAULT_VIEWPORTS)
    ap.add_argument("--out-dir", default=mb.DEFAULT_OUT)
    ap.add_argument("--timeout", type=int, default=45)
    args = ap.parse_args()
    vps = mb.parse_viewports(args.viewports)
    buf = io.StringIO()
    t0 = time.perf_counter()
    ok_all, notrun = True, False
    rows = []
    with redirect_stdout(buf):
        floors = mb.engine_floors(mb.ROOT)
        print(f"engine floors from {floors.get('source')}: TYPE_FLOOR_PX={floors.get('TYPE_FLOOR_PX')} "
              f"BODY_FLOOR_PX={floors.get('BODY_FLOOR_PX')} TAP_MIN_PX={floors.get('TAP_MIN_PX')}")

        # 1. not-run path must never read as pass
        nr = mb.not_run_gates("simulated: playwright not importable")
        items = mb.readiness_items([{"step": "build", "status": "PASS", "note": "", "command": ""}], [],
                                   {"x": {"360x800": {"gates": nr}}}, {"status": "not-run", "note": "simulated"}, True)
        v, _, nri = mb.verdict(items)
        nr_ok = all(g["status"] == "not-run" for g in nr.values()) and v == "NOT READY"
        print(f"[{'ok' if nr_ok else 'FAIL'}] not-run path: {len(nr)} gates not-run, readiness {v} ({len(nri)} not-run items)")
        ok_all &= nr_ok

        # 2. fixtures
        missing = [f for f in EXPECT if not (FIX / f).exists()]
        if missing:
            print(f"[FAIL] fixtures missing: {missing}")
            ok_all = False
        srv = serve_dir(FIX)
        port = srv.server_address[1]
        pages = [(name, f"http://127.0.0.1:{port}/{name}") for name in EXPECT]
        try:
            results, meta = mb.capture_all(pages, vps, floors, args.timeout * 1000, None, None)
        finally:
            srv.shutdown()
        print(f"browser: {meta.get('browser') or meta.get('error')}; capture {meta['seconds']}s")
        if meta.get("error"):
            notrun = True
            print(f"[NOT-RUN] capture: {meta['error']}")
        for name, expect in EXPECT.items():
            for vp in vps:
                r = results[name][mb.vp_name(vp)]
                gates = r["gates"]
                fails = {g for g, x in gates.items() if x["status"] == "fail"}
                nrs = {g for g, x in gates.items() if x["status"] == "not-run"}
                if mb.is_mobile(vp):
                    ok = fails == expect and not nrs
                else:
                    ok = fails <= expect and not nrs
                ok_all &= ok
                rows.append((name, mb.vp_name(vp), sorted(expect), sorted(fails), sorted(nrs), ok))
                status = "ok" if ok else ("NOT-RUN" if nrs else "FAIL")
                print(f"[{status}] {name:18} {mb.vp_name(vp):9} expect={sorted(expect) or '-'} failed={sorted(fails) or '-'}"
                      + (f" not-run={sorted(nrs)}" if nrs else ""))
            first = mb.vp_name(vps[0])
            for g in sorted(expect) or ["(all gates pass)"]:
                if g in results[name][first]["gates"]:
                    print(f"      evidence {first} {g}: {results[name][first]['gates'][g]['evidence'][:260]}")
    secs = round(time.perf_counter() - t0, 3)
    text = buf.getvalue()
    code = 2 if notrun else (0 if ok_all else 1)
    verdict_txt = {0: "SELFTEST PASS: every bad fixture fails exactly its gate, clean passes all",
                   1: "SELFTEST FAIL: see rows marked FAIL", 2: "SELFTEST NOT-RUN: capture unavailable"}[code]
    text += f"{verdict_txt} ({secs}s)\n"
    print(text, end="")
    od = Path(args.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    (od / f"MOBILE_SELFTEST_{stamp}.txt").write_text(text, encoding="utf-8")
    md = [f"# MOBILE_SELFTEST {stamp}", "", f"Command: `python bench\\mobile_bench_selftest.py` from V:\\A\\Ai\\spidercaster\\working.",
          f"Fixtures: `bench\\fixtures\\mobile\\`. Verdict: **{verdict_txt}** in {secs}s.", "",
          "| Fixture | Viewport | Expected failing gate | Gates that failed | not-run | OK |", "|---|---|---|---|---|---|"]
    for name, vp, exp, fails, nrs, ok in rows:
        md.append(f"| {name} | {vp} | {', '.join(exp) or '-'} | {', '.join(fails) or '-'} | {', '.join(nrs) or '-'} | {'yes' if ok else 'NO'} |")
    md += ["", "Raw output:", "", "```", text.rstrip(), "```"]
    (od / f"MOBILE_SELFTEST_{stamp}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {od / f'MOBILE_SELFTEST_{stamp}.md'}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
