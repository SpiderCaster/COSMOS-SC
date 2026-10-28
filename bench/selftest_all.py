#!/usr/bin/env python3
r"""Run every SpiderCaster selftest in a throwaway copy, CI-style (stdlib only).

What it does
  1. Copies the repo (no .git, dist, caches, bench/results) into a fresh temp dir. The real tree is never touched.
  2. Strips machine/secret env vars (SPIDERCASTER_*, SC_*, FORGE_*, *_API_KEY, *_KEY_FILE, *_TOKEN, *_SECRET,
     PYTHONPATH). Names are reported, values never printed. It sets no V:\ paths itself.
  3. Discovers selftests (default glob lib/*_selftest.py = the 26 in EVAL 2026-10-18) and runs each as
     `python -m lib.<name>` from the copy root, with a per-test timeout.
  4. Classifies each result:
       PASS  exit 0
       SKIP  failed AND the failure is explained by a hard-coded absolute path that does not exist on this host
             (the path appears in the output, or is a literal in the selftest / a directly imported lib module).
             Reason and evidence are recorded. Use --strict to count SKIP as failure in the exit code.
       FAIL  anything else (including timeouts and crashes)
  5. Prints a pass/fail/skip table with timings and writes SELFTEST_ALL_<ts>_<host>.json/.md into --out-dir.

Options
  --parts-dir DIR       exported as SPIDERCASTER_PARTS (+ SPIDERCASTER_PARTS_DIR). Report says which lib modules read it.
  --components-dir DIR  exported as SPIDERCASTER_COMPONENTS_DIR (+ SPIDERCASTER_CATALOG if DIR/catalog.jsonl exists).
                        If no engine module reads those names, the option is reported as NOT-RUN (ignored by engine).
  --offline             Linux only: run each test under `unshare -rn` with loopback up (no network). Recorded.
  --glob PATTERN        repeatable; default lib/*_selftest.py. Example extra: bench/mobile_bench_selftest.py
  --only NAME           repeatable; run only these test names (e.g. visit_check_selftest)
  --keep                keep the temp copy

Exit code: 0 if no FAIL (and no SKIP with --strict), else 1.
Usage (repo root):  python bench/selftest_all.py --out-dir <dir> [--offline] [--parts-dir D] [--components-dir D]
"""
from __future__ import annotations

import argparse
import ast
import datetime
import fnmatch
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXCLUDE_DIRS = {".git", "__pycache__", "dist", "build", ".venv", "venv", "node_modules", "_to_be_deleted",
                "_delme", ".idea", ".vscode", ".pytest_cache"}
STRIP_PREFIX = ("SPIDERCASTER_", "SC_", "FORGE_", "OPENWORK_", "OPENROUTER_", "GEMINI_", "XAI_", "TOKENCTR_")
STRIP_SUFFIX = ("_API_KEY", "_KEY_FILE", "_TOKEN", "_SECRET", "_SECRETS_DIR")
STRIP_EXACT = {"PYTHONPATH", "GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS"}
ABS_PATH = re.compile(r"(?<![A-Za-z])([A-Za-z]:\\[^\s'\"<>|,;)\]]+)")
DRIVE_LIT = re.compile(r"""r?["']([A-Za-z]:\\[^"']+)["']""")
CAP = 4000


def strip_env(extra: dict) -> tuple[dict, list[str]]:
    env, removed = {}, []
    for k, v in os.environ.items():
        ku = k.upper()
        if ku in STRIP_EXACT or ku.startswith(STRIP_PREFIX) or ku.endswith(STRIP_SUFFIX):
            removed.append(k)
            continue
        env[k] = v
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "PYTHONHASHSEED": "0"})
    env.update(extra)
    return env, sorted(removed)


def copy_tree(src: Path, dest: Path) -> None:
    def ignore(d, names):
        out = [n for n in names if n in EXCLUDE_DIRS or n.endswith((".pyc", ".exe"))]
        if Path(d).resolve() == (src / "bench").resolve():
            out.append("results")
        return out
    shutil.copytree(src, dest, ignore=ignore)


def git_info(src: Path) -> dict:
    def g(*a):
        try:
            p = subprocess.run(["git", "-C", str(src), *a], capture_output=True, text=True, timeout=20)
            return p.stdout.strip() if p.returncode == 0 else ""
        except Exception:
            return ""
    dirty = g("status", "--porcelain")
    return {"rev": g("rev-parse", "--short", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty_files": len(dirty.splitlines()) if dirty else 0}


def lib_imports(py: Path) -> list[str]:
    try:
        tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("lib."):
            mods.add(node.module)
        elif isinstance(node, ast.Import):
            mods.update(a.name for a in node.names if a.name.startswith("lib."))
    return sorted(mods)


def module_file(copy: Path, mod: str) -> Path | None:
    base = copy.joinpath(*mod.split("."))
    for cand in (base.with_suffix(".py"), base / "__init__.py"):
        if cand.is_file():
            return cand
    return None


def drive_literals(py: Path) -> list[tuple[str, int]]:
    out = []
    for i, line in enumerate(py.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        for m in DRIVE_LIT.finditer(line):
            out.append((m.group(1).replace("\\\\", "\\"), i))
    return out


def host_has(path: str) -> bool:
    if os.name != "nt" and re.match(r"^[A-Za-z]:\\", path):
        return False
    try:
        return Path(path).exists()
    except OSError:
        return False


def env_readers(copy: Path, names: list[str]) -> dict[str, list[str]]:
    found = {n: [] for n in names}
    for py in sorted((copy / "lib").rglob("*.py")) + [copy / "spidercaster.py"]:
        if not py.is_file():
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        for n in names:
            if re.search(r"""["']%s["']""" % re.escape(n), text):
                found[n].append(py.relative_to(copy).as_posix())
    return found


def offline_prefix() -> tuple[list[str], str]:
    if not sys.platform.startswith("linux") or not shutil.which("unshare"):
        return [], "not enforced (unshare unavailable on this platform)"
    probe = subprocess.run(["unshare", "-rn", "true"], capture_output=True)
    if probe.returncode != 0:
        return [], "not enforced (unshare -rn not permitted)"
    return ["unshare", "-rn", "sh", "-c", 'ip link set lo up 2>/dev/null; exec "$@"', "sh"], "enforced (unshare -rn, loopback up)"


def classify(rc, out: str, test_py: Path, copy: Path) -> tuple[str, str, list[dict]]:
    if rc == 0:
        return "PASS", "", []
    if rc is None:
        return "FAIL", "timeout", []
    evidence = []
    for m in ABS_PATH.finditer(out):
        p = m.group(1).rstrip(".")
        if not host_has(p):
            evidence.append({"path": p, "where": "output"})
    files = [test_py] + [f for f in (module_file(copy, m) for m in lib_imports(test_py)) if f]
    for f in files:
        for lit, line in drive_literals(f):
            if not host_has(lit):
                evidence.append({"path": lit, "where": f"{f.relative_to(copy).as_posix()}:{line}"})
    seen, uniq = set(), []
    for e in evidence:
        key = (e["path"], e["where"])
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    if uniq:
        return "SKIP", "hard-coded path absent on this host: " + "; ".join(sorted({e["path"] for e in uniq})), uniq
    return "FAIL", "", []


def last_line(text: str) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-1][:300] if lines else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=str(ROOT))
    ap.add_argument("--out-dir", default=str(HERE / "results"))
    ap.add_argument("--parts-dir")
    ap.add_argument("--components-dir")
    ap.add_argument("--glob", action="append")
    ap.add_argument("--only", action="append")
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    src = Path(a.repo).resolve()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    host = (a.label or socket.gethostname() or "host").replace(" ", "_")
    tmp = Path(tempfile.mkdtemp(prefix="sc-selftest-all-"))
    copy = tmp / "repo"
    t0 = time.perf_counter()
    copy_tree(src, copy)

    extra, options = {}, {}
    if a.parts_dir:
        pd = Path(a.parts_dir)
        extra["SPIDERCASTER_PARTS"] = extra["SPIDERCASTER_PARTS_DIR"] = str(pd)
        options["parts_dir"] = {"value": str(pd), "exists": pd.exists()}
    if a.components_dir:
        cd = Path(a.components_dir)
        extra["SPIDERCASTER_COMPONENTS_DIR"] = str(cd)
        if (cd / "catalog.jsonl").is_file():
            extra["SPIDERCASTER_CATALOG"] = str(cd / "catalog.jsonl")
        options["components_dir"] = {"value": str(cd), "exists": cd.exists()}
    env, removed = strip_env(extra)
    readers = env_readers(copy, ["SPIDERCASTER_PARTS", "SPIDERCASTER_PARTS_DIR", "SPIDERCASTER_KIT",
                                 "SPIDERCASTER_COMPONENTS_DIR", "SPIDERCASTER_CATALOG", "SPIDERCASTER_HOME"])
    if a.parts_dir:
        r = readers["SPIDERCASTER_PARTS"] + readers["SPIDERCASTER_PARTS_DIR"]
        options["parts_dir"]["read_by"] = sorted(set(r))
        options["parts_dir"]["status"] = "applied (partial: only modules listed in read_by honor it)" if r else "NOT-RUN: ignored by engine (no reader)"
    if a.components_dir:
        r = readers["SPIDERCASTER_COMPONENTS_DIR"] + readers["SPIDERCASTER_CATALOG"]
        options["components_dir"]["read_by"] = sorted(set(r))
        options["components_dir"]["status"] = "applied" if r else "NOT-RUN: ignored by engine (no module reads SPIDERCASTER_COMPONENTS_DIR / SPIDERCASTER_CATALOG yet)"

    prefix, offline_note = offline_prefix() if a.offline else ([], "not requested")
    globs = a.glob or ["lib/*_selftest.py"]
    tests = []
    for g in globs:
        for p in sorted(copy.glob(g)):
            if p.is_file() and p not in tests:
                tests.append(p)
    if a.only:
        tests = [p for p in tests if p.stem in a.only or p.name in a.only]

    rows = []
    for py in tests:
        rel = py.relative_to(copy)
        mod = ".".join(rel.with_suffix("").parts)
        cmd = prefix + [sys.executable, "-m", mod]
        s = time.perf_counter()
        try:
            p = subprocess.run(cmd, cwd=copy, env=env, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=a.timeout)
            rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
        except subprocess.TimeoutExpired as exc:
            rc, out = None, f"timeout after {a.timeout}s\n" + str(exc.stdout or "")[-2000:]
        except Exception as exc:  # never crash the runner
            rc, out = -999, f"runner error: {exc!r}"
        sec = round(time.perf_counter() - s, 2)
        status, reason, evidence = classify(rc, out, py, copy)
        row = {"test": py.stem, "module": mod, "status": status, "rc": rc, "seconds": sec,
               "reason": reason, "last_line": last_line(out), "evidence": evidence,
               "output_tail": out[-CAP:] if status != "PASS" else ""}
        rows.append(row)
        print(f"{status:<4} {sec:>7.2f}s  {py.stem}" + (f"  -- {reason or row['last_line']}"[:220] if status != "PASS" else ""), flush=True)

    total = round(time.perf_counter() - t0, 2)
    counts = {k: sum(1 for r in rows if r["status"] == k) for k in ("PASS", "FAIL", "SKIP")}
    summary = {
        "stamp": stamp, "host": host, "platform": platform.platform(), "python": sys.version.split()[0],
        "source": str(src), "git": git_info(src), "copy": str(copy) if a.keep else "(deleted)",
        "globs": globs, "offline": offline_note, "env_stripped_names": removed,
        "env_set_by_runner": sorted(extra) + ["PYTHONDONTWRITEBYTECODE", "PYTHONHASHSEED", "PYTHONIOENCODING"],
        "options": options, "counts": counts, "total": len(rows), "seconds_total": total,
        "strict": a.strict, "rows": rows,
    }
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / f"SELFTEST_ALL_{stamp}_{host}"
    base.with_suffix(".json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    md = [f"# SELFTEST_ALL {stamp} - {host}", "",
          f"- Source: `{src}` (git {summary['git']['branch']} {summary['git']['rev']}, {summary['git']['dirty_files']} dirty files); run in a temp copy.",
          f"- Platform: {summary['platform']}, Python {summary['python']}. Offline: {offline_note}.",
          f"- Env names stripped: {', '.join(removed) or 'none'} (values never read or printed). Runner sets no V:\\ paths.",
          f"- Result: **{counts['PASS']} PASS / {counts['FAIL']} FAIL / {counts['SKIP']} SKIP** of {len(rows)} in {total}s."
          + (" SKIP counts as failure (--strict)." if a.strict else " SKIP = failed only because a hard-coded path is absent on this host."), ""]
    for k, v in options.items():
        md.append(f"- `--{k.replace('_', '-')}` = `{v['value']}` (exists: {v['exists']}): {v['status']}. Read by: {', '.join(v['read_by']) or 'none'}.")
    md += ["", "| Test | Status | Exit | Seconds | Reason / last line |", "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['test']} | {r['status']} | {r['rc']} | {r['seconds']} | {(r['reason'] or r['last_line']).replace('|', '/')[:240]} |")
    bad = [r for r in rows if r["status"] != "PASS"]
    if bad:
        md += ["", "## Non-pass detail", ""]
        for r in bad:
            md.append(f"### {r['test']} ({r['status']}, exit {r['rc']})")
            for e in r["evidence"]:
                md.append(f"- absent path `{e['path']}` ({e['where']})")
            md += ["```", r["output_tail"][-1500:].strip(), "```", ""]
    base.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\n{counts['PASS']} PASS / {counts['FAIL']} FAIL / {counts['SKIP']} SKIP of {len(rows)} ({total}s)")
    print(f"wrote {base}.json and .md")
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if counts["FAIL"] or (a.strict and counts["SKIP"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
