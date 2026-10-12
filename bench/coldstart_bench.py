#!/usr/bin/env python3
r"""SpiderCaster cold-start bench (stdlib only).

Copies the tree into a fresh temp dir (so the real tree is never touched), strips
provider keys and SPIDERCASTER_HOME from the environment, then runs:

  1. build      build projects/demo-local --offline into a fresh out dir
  2. repro      build a second time (different PYTHONHASHSEED, same paths) and
                compare every output file byte for byte
  3. check      spidercaster check <site> --expect-noindex
  4. serve      start `serve`, GET / (expect 200) and a missing path (expect 404)
  5. doctor     spidercaster doctor
  6. crew       spidercaster crew selftest

Each step records pass/fail, seconds, exit code, and the exact stdout/stderr.

Usage:
  python bench\coldstart_bench.py                  # source = working tree (tracked + untracked)
  python bench\coldstart_bench.py --source head    # source = git HEAD only (what a git clone gets)
  python bench\coldstart_bench.py --keep           # keep the temp checkout for debugging

Results: bench\results\latest-<source>.json / .md (previous run kept as prev-<source>.json).
Exit code: 0 if every step passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXCLUDE = {".git", "__pycache__", "_delme", "bench", ".venv", "venv", ".idea", ".vscode"}
STRIP_ENV = (
    "SPIDERCASTER_HOME", "GEMINI_API_KEY", "GOOGLE_API_KEY", "FORGE_GEMINI_KEY_FILE",
    "OPENROUTER_API_KEY", "OPENWORK_API_KEY", "OPENWORK_INFERENCE_BASE_URL",
    "FORGE_OPENWORK_MODEL", "FORGE_GEMINI_MODELS", "FORGE_OPENROUTER_MODELS",
    "XAI_API_KEY",
)
CAP = 20000
PROJECT = "projects/demo-local"


def clip(text: str) -> str:
    if len(text) <= CAP:
        return text
    return text[:CAP // 2] + f"\n...[{len(text) - CAP} chars clipped]...\n" + text[-CAP // 2:]


def make_env(hashseed: str = "0") -> dict:
    env = {k: v for k, v in os.environ.items() if k not in STRIP_ENV}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONHASHSEED"] = hashseed
    return env


def snapshot_worktree(dest: Path) -> None:
    def ignore(_d, names):
        return [n for n in names if n in EXCLUDE or n.endswith(".pyc")]
    shutil.copytree(ROOT, dest, ignore=ignore)


def snapshot_head(dest: Path) -> None:
    zpath = dest.parent / "head.zip"
    subprocess.run(["git", "-C", str(ROOT), "archive", "--format=zip", "-o", str(zpath), "HEAD"],
                   check=True, capture_output=True)
    dest.mkdir(parents=True)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(dest)


def run(name, argv, cwd, env, timeout, expect_in_stdout=None) -> dict:
    cmd = [sys.executable] + argv
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        rc, out, err, note = p.returncode, p.stdout, p.stderr, ""
    except subprocess.TimeoutExpired as exc:
        rc, out, err, note = None, (exc.stdout or ""), (exc.stderr or ""), f"timeout after {timeout}s"
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", "replace")
    dt = time.perf_counter() - t0
    ok = rc == 0
    if ok and expect_in_stdout and expect_in_stdout not in out:
        ok = False
        note = f"exit 0 but stdout lacks expected text {expect_in_stdout!r}"
    return {"step": name, "status": "PASS" if ok else "FAIL", "seconds": round(dt, 3),
            "command": "python " + " ".join(argv), "exit_code": rc, "note": note,
            "stdout": clip(out), "stderr": clip(err)}


def tree_hashes(root: Path) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def step_serve(cwd: Path, env: dict, site: str, timeout: int) -> dict:
    port = free_port()
    argv = ["spidercaster.py", "serve", site, "--port", str(port)]
    t0 = time.perf_counter()
    proc = subprocess.Popen([sys.executable] + argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    problems, got = [], {}
    deadline = time.time() + min(timeout, 20)
    while time.time() < deadline:
        if proc.poll() is not None:
            problems.append(f"server exited early with code {proc.returncode}")
            break
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3) as r:
                body = r.read().decode("utf-8", "replace")
                got["index"] = {"status": r.status, "content_type": r.headers.get("Content-Type"), "bytes": len(body)}
                if r.status != 200:
                    problems.append(f"GET / returned {r.status}")
                if "<title" not in body.lower():
                    problems.append("GET / body has no <title>")
                break
        except Exception:
            time.sleep(0.25)
    else:
        problems.append("server did not answer GET / within 20s")
    if "index" in got:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/__missing__.html", timeout=3)
            problems.append("GET /__missing__.html returned 200, expected 404")
        except urllib.error.HTTPError as exc:
            got["missing"] = exc.code
            if exc.code != 404:
                problems.append(f"GET /__missing__.html returned {exc.code}, expected 404")
        except Exception as exc:
            problems.append(f"GET /__missing__.html raised {exc!r}")
    rc_before = proc.poll()
    if rc_before is None:
        proc.terminate()
    try:
        out, err = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
    dt = time.perf_counter() - t0
    return {"step": "serve", "status": "FAIL" if problems else "PASS", "seconds": round(dt, 3),
            "command": "python " + " ".join(argv), "exit_code": rc_before,
            "note": "; ".join(problems) or json.dumps(got), "stdout": clip(out or ""), "stderr": clip(err or "")}


def diff_summary(a: Path, b: Path, rels: list[str]) -> list[str]:
    lines = []
    for rel in rels[:5]:
        try:
            ta = (a / rel).read_text(encoding="utf-8").splitlines()
            tb = (b / rel).read_text(encoding="utf-8").splitlines()
        except Exception:
            lines.append(f"{rel}: binary or unreadable, hashes differ")
            continue
        d = list(difflib.unified_diff(ta, tb, "build1/" + rel, "build2/" + rel, lineterm="", n=0))
        lines.append("\n".join(d[:30]))
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=["worktree", "head"], default="worktree")
    ap.add_argument("--keep", action="store_true", help="keep the temp checkout")
    ap.add_argument("--timeout", type=int, default=180, help="per-step timeout seconds")
    ap.add_argument("--results", default=str(HERE / "results"))
    ap.add_argument("--out-dir", default=None, help="also write RUN_*.md and REPRO_*.md here (e.g. V:\\streams\\webdev\\OUT\\bench-qa)")
    args = ap.parse_args()

    results = Path(args.results)
    results.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="sc-coldstart-"))
    co = tmp / "checkout"
    steps: list[dict] = []
    t_all = time.perf_counter()
    try:
        t0 = time.perf_counter()
        (snapshot_head if args.source == "head" else snapshot_worktree)(co)
        nfiles = sum(1 for p in co.rglob("*") if p.is_file())
        steps.append({"step": "checkout", "status": "PASS", "seconds": round(time.perf_counter() - t0, 3),
                      "command": f"snapshot {args.source}", "exit_code": 0,
                      "note": f"{nfiles} files into {co}", "stdout": "", "stderr": ""})

        site = "sites/bench-out"
        build_argv = ["spidercaster.py", "build", PROJECT, "--offline", "--out", site]
        s1 = run("build", build_argv, co, make_env("1"), args.timeout)
        steps.append(s1)
        snap1 = tmp / "build1"
        if (co / site).exists():
            shutil.copytree(co / site, snap1)
            shutil.rmtree(co / site)

        # second build, same paths, different hash seed; wait >1s so second-resolution timestamps would differ
        time.sleep(1.2)
        s2 = run("build#2", build_argv, co, make_env("2"), args.timeout)
        snap2 = tmp / "build2"
        if (co / site).exists():
            shutil.copytree(co / site, snap2)
        s2["step"] = "build#2"
        steps.append(s2)

        # repro verdict
        t0 = time.perf_counter()
        if not snap1.exists() or not snap2.exists():
            rep = {"status": "FAIL", "note": "a build produced no output dir, cannot compare", "diff": []}
        else:
            h1, h2 = tree_hashes(snap1), tree_hashes(snap2)
            only1 = sorted(set(h1) - set(h2))
            only2 = sorted(set(h2) - set(h1))
            changed = sorted(r for r in set(h1) & set(h2) if h1[r] != h2[r])
            if only1 or only2 or changed:
                ts_only = (not only1 and not only2 and changed == ["report.json"] and all(l.startswith(("---", "+++", "@@")) or "built_at" in l for l in "\n".join(diff_summary(snap1, snap2, changed)).splitlines()))
                rep = {"status": "FAIL", "note": ("ONLY report.json built_at differs (wall-clock timestamp). " if ts_only else "") + f"{len(h1)} files in build1, {len(h2)} in build2; only-in-1={only1}; only-in-2={only2}; differing={changed}",
                       "diff": diff_summary(snap1, snap2, changed)}
            else:
                rep = {"status": "PASS", "note": f"{len(h1)} files identical across two builds (PYTHONHASHSEED 1 vs 2)", "diff": []}
        steps.append({"step": "repro", "status": rep["status"], "seconds": round(time.perf_counter() - t0, 3),
                      "command": "sha256 of every file in build #1 vs build #2", "exit_code": None,
                      "note": rep["note"], "stdout": "\n\n".join(rep["diff"]), "stderr": ""})

        if (co / site).exists():
            steps.append(run("check", ["spidercaster.py", "check", site, "--expect-noindex"], co, make_env(), args.timeout))
            steps.append(step_serve(co, make_env(), site, args.timeout))
        else:
            for n in ("check", "serve"):
                steps.append({"step": n, "status": "SKIP", "seconds": 0, "command": "", "exit_code": None,
                              "note": "no built site to test (build failed)", "stdout": "", "stderr": ""})
        steps.append(run("doctor", ["spidercaster.py", "doctor"], co, make_env(), args.timeout))
        steps.append(run("crew selftest", ["spidercaster.py", "crew", "selftest"], co, make_env(), args.timeout,
                         expect_in_stdout="crew selftest ok"))
        steps.append(run("shipcheck", ["spidercaster.py", "shipcheck"], co, make_env(), max(args.timeout, 600)))
    finally:
        total = round(time.perf_counter() - t_all, 3)
        if not args.keep:
            shutil.rmtree(tmp, ignore_errors=True)

    git_head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--short"], capture_output=True, text=True).stdout.splitlines()
    run_info = {
        "when": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": args.source, "git_head": git_head, "dirty_paths": len(dirty),
        "python": sys.version.split()[0], "platform": platform.platform(),
        "total_seconds": total, "kept": str(tmp) if args.keep else None, "steps": steps,
        "overall": "PASS" if all(s["status"] in ("PASS",) for s in steps) else "FAIL",
    }

    latest = results / f"latest-{args.source}.json"
    prev = results / f"prev-{args.source}.json"
    prev_data = None
    if latest.exists():
        prev_data = json.loads(latest.read_text(encoding="utf-8"))
        shutil.copyfile(latest, prev)
    regress = []
    if prev_data:
        old = {s["step"]: s["status"] for s in prev_data["steps"]}
        for s in steps:
            if old.get(s["step"]) == "PASS" and s["status"] == "FAIL":
                regress.append(s["step"])
    run_info["regressions_vs_previous"] = regress
    latest.write_text(json.dumps(run_info, indent=2), encoding="utf-8")

    md = [f"# SpiderCaster cold-start bench ({args.source})", "",
          f"- When: {run_info['when']}", f"- Git HEAD: {git_head} ({len(dirty)} uncommitted paths in the working tree)",
          f"- Python: {run_info['python']} on {run_info['platform']}", f"- Total: {total}s", f"- Overall: **{run_info['overall']}**",
          f"- Regressions vs previous run: {', '.join(regress) or 'none'}", "",
          "| Step | Result | Seconds | Exit | Note |", "|---|---|---|---|---|"]
    for s in steps:
        note = (s["note"] or "").replace("|", "\\|").replace("\n", " ")[:200]
        md.append(f"| {s['step']} | {s['status']} | {s['seconds']} | {s['exit_code']} | {note} |")
    for s in steps:
        if s["status"] == "FAIL":
            md += ["", f"## {s['step']} FAIL", "", f"Reproduce: `{s['command']}` (from a fresh copy of the tree)", ""]
            if s["note"]:
                md += [f"Note: {s['note']}", ""]
            if s["stderr"].strip():
                md += ["stderr:", "```", s["stderr"].rstrip(), "```"]
            if s["stdout"].strip():
                md += ["stdout:", "```", s["stdout"].rstrip(), "```"]
    (results / f"latest-{args.source}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    if args.out_dir:
        od = Path(args.out_dir)
        od.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        old = {}
        if prev_data:
            old = {s["step"]: s["status"] for s in prev_data["steps"]}
        rl = [f"# RUN {stamp} - cold start ({args.source})", "",
              f"Engine: git {git_head}, {len(dirty)} uncommitted paths. Python {run_info['python']}, {run_info['platform']}.",
              "Variables needed: none. Stripped from the environment (names only): " + ", ".join(STRIP_ENV) + ". Set: PYTHONDONTWRITEBYTECODE, PYTHONIOENCODING, PYTHONHASHSEED.",
              f"Fixture: `{PROJECT}`, offline. Overall: **{run_info['overall']}** in {total}s.", "",
              "| Step | Command | Exit | Seconds | Result | Exact error |", "|---|---|---|---|---|---|"]
        for s in steps:
            err = ((s["stderr"].strip().splitlines() or [""])[-1] if s["status"] == "FAIL" else "")
            err = (err or (s["note"] if s["status"] == "FAIL" else "")).replace("|", "\\|")[:240]
            rl.append(f"| {s['step']} | `{s['command']}` | {s['exit_code']} | {s['seconds']} | {s['status']} | {err} |")
        rl += ["", "## Changes vs previous run", ""]
        if prev_data:
            ch = [f"- {s['step']}: {old[s['step']]} -> {s['status']}" for s in steps if s["step"] in old and old[s["step"]] != s["status"]]
            rl += ch or ["- none"]
        else:
            rl += ["- no previous run recorded"]
        (od / f"RUN_{stamp}_{args.source}.md").write_text("\n".join(rl) + "\n", encoding="utf-8")
        rp = next((s for s in steps if s["step"] == "repro"), None)
        if rp:
            rr = [f"# REPRO {stamp} ({args.source})", "",
                  "Allowed differences (written before the result): none. No timestamp may differ; the engine must honor SOURCE_DATE_EPOCH or write none.",
                  f"Method: fixture `{PROJECT}` built twice with `--offline` into the same relative path in two separate processes, PYTHONHASHSEED 1 and 2, 1.2 s apart; SHA-256 of every file compared.",
                  f"Engine: git {git_head}, {len(dirty)} uncommitted paths.", "",
                  f"Verdict: **{'IDENTICAL' if rp['status'] == 'PASS' else 'NOT IDENTICAL'}**", "", rp["note"]]
            if rp["stdout"].strip():
                rr += ["", "```", rp["stdout"].rstrip(), "```"]
            (od / f"REPRO_{stamp}_{args.source}.md").write_text("\n".join(rr) + "\n", encoding="utf-8")
    for s in steps:
        print(f"{s['status']:5} {s['step']:14} {s['seconds']:>8}s  {(s['note'] or '')[:110]}")
    print(f"overall {run_info['overall']} in {total}s -> {latest}")
    return 0 if run_info["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())