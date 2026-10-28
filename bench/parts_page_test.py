#!/usr/bin/env python3
r"""Parts page-integration bench: build demo-local offline, apply each header kit item with sc_header.py,
then run the engine's own `check` (type floor, contrast, links, noindex, ...) on the result.
Writes nothing but temp files and the optional report.
Paths (2026-10-18, path-independent): --parts-dir / --kit-dir, else env SPIDERCASTER_PARTS / SPIDERCASTER_KIT,
else bench/bench_paths.json, else repo-relative, else the old KC-PC default only if it exists (see bench/sc_paths.py).
If the header parts or the kit are absent, prints SKIP with the reason and exits 3 (never a pass, never a crash)."""
import argparse, datetime, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sc_paths import EXIT_SKIP, resolve
ROOT = Path(__file__).resolve().parent.parent
KIT = PARTS = None  # resolved in main()

def run(cmd, cwd, env=None, t=120):
    s = time.perf_counter()
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=t)
    return p.returncode, p.stdout, p.stderr, round(time.perf_counter() - s, 3)

def main():
    global KIT, PARTS
    ap = argparse.ArgumentParser(); ap.add_argument("--out-dir"); ap.add_argument("--parts-dir"); ap.add_argument("--kit-dir"); a = ap.parse_args()
    parts_root, psrc = resolve("parts", a.parts_dir)
    kit_root, ksrc = resolve("kit", a.kit_dir)
    why = []
    if parts_root is None: why.append(psrc)
    elif not (parts_root / "headers").is_dir(): why.append(f"no headers/ under parts root {parts_root} [{psrc}]")
    if kit_root is None: why.append(ksrc)
    elif not (kit_root / "headers" / "_shared" / "sc_header.py").is_file(): why.append(f"no headers/_shared/sc_header.py under kit {kit_root} [{ksrc}]")
    if why:
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        text = f"# PAGES {stamp} - SKIP\n\nSKIP: " + "; ".join(why) + "\n"
        print(text)
        if a.out_dir:
            Path(a.out_dir).mkdir(parents=True, exist_ok=True); (Path(a.out_dir) / f"PAGES_{stamp}.md").write_text(text, encoding="utf-8")
        return EXIT_SKIP
    PARTS, KIT = parts_root / "headers", kit_root / "headers"
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    tmp = Path(tempfile.mkdtemp(prefix="sc-parts-"))
    base = tmp / "base"
    rc, o, e, s = run([sys.executable, "spidercaster.py", "build", "projects/demo-local", "--offline", "--out", str(base)], ROOT, env)
    rows = [{"step": "base build", "item": "-", "rc": rc, "sec": s, "result": "PASS" if rc == 0 else "FAIL", "detail": (e or o).strip()[-300:] if rc else ""}]
    if rc == 0:
        rc0, o0, e0, s0 = run([sys.executable, "spidercaster.py", "check", str(base), "--expect-noindex"], ROOT, env)
        rows.append({"step": "base check", "item": "-", "rc": rc0, "sec": s0, "result": "PASS" if rc0 == 0 else "FAIL", "detail": ""})
        for man in sorted(PARTS.glob("*/manifest.json")):
            m = json.loads(man.read_text(encoding="utf-8"))
            item = Path(m["source_kit_item"]).name
            out = tmp / item
            shutil.copytree(base, out)
            rca, oa, ea, sa = run([sys.executable, str(KIT / "_shared" / "sc_header.py"), "apply", str(base / "index.html"), str(out / "index.html")] + (["--item", "hdr-classic-sticky", "--with", item] if item.startswith("cmp-") else ["--item", item]), KIT / "_shared", env)
            if rca != 0:
                rows.append({"step": "apply+check", "item": item, "rc": rca, "sec": sa, "result": "FAIL", "detail": "apply: " + (ea or oa).strip()[-300:]}); continue
            rcc, oc, ec, sc = run([sys.executable, "spidercaster.py", "check", str(out), "--expect-noindex"], ROOT, env)
            bad = [l.strip() for l in oc.splitlines() if "[fail]" in l or "[warn]" in l]
            rows.append({"step": "apply+check", "item": item, "rc": rcc, "sec": round(sa + sc, 3), "result": "PASS" if rcc == 0 else "FAIL",
                         "detail": "; ".join(bad)[:400] if bad else (oc.strip().splitlines() or [""])[-1]})
    shutil.rmtree(tmp, ignore_errors=True)
    n = sum(1 for r in rows if r["step"] == "apply+check")
    p = sum(1 for r in rows if r["step"] == "apply+check" and r["result"] == "PASS")
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    md = [f"# PAGES {stamp} - header parts applied to a built page", "", f"Parts: `{PARTS}` [{psrc}]; kit: `{KIT}` [{ksrc}].", "Method: `spidercaster.py build projects/demo-local --offline`, then `sc_header.py apply` per item, then `spidercaster.py check <out> --expect-noindex` (includes type_floor, contrast, internal_links, noindex).", f"Applied and checked: {n}; PASS {p}; FAIL {n-p}.", "", "| Step | Item | Exit | Seconds | Result | Detail |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['step']} | {r['item']} | {r['rc']} | {r['sec']} | {r['result']} | {r['detail'].replace('|','/')[:200]} |")
    text = "\n".join(md) + "\n"; print(text)
    if a.out_dir:
        Path(a.out_dir).mkdir(parents=True, exist_ok=True); (Path(a.out_dir) / f"PAGES_{stamp}.md").write_text(text, encoding="utf-8")
    return 0 if p == n and all(r["result"] == "PASS" for r in rows) else 1
raise SystemExit(main())