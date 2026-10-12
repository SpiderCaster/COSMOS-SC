#!/usr/bin/env python3
r"""Parts integration bench (stdlib). For every part under tools\parts\<family>\<id>:
  node --check part.js, fleet_check.py part DIR, webcheck.py css part.css,
  manifest sanity (targets, files exist, install_seat), and a theme-target verdict:
  a part integrates with OceanWP/GeneratePress only if targets lists it AND a snippet.php/hook is shipped.
Usage: python bench\parts_integration.py --fleet-check PATH --webcheck PATH [--out-dir DIR]
Nothing is installed; read-only on the parts."""
import argparse, datetime, json, subprocess, sys, time
from pathlib import Path

PARTS = Path(r"V:\streams\webdev\tools\parts")

def run(cmd, cwd, timeout=120):
    t = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, p.stdout, p.stderr, round(time.perf_counter() - t, 3)
    except subprocess.TimeoutExpired:
        return None, "", f"timeout {timeout}s", round(time.perf_counter() - t, 3)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fleet-check", required=True)
    ap.add_argument("--webcheck", required=True)
    ap.add_argument("--out-dir")
    a = ap.parse_args()
    rows = []
    for fam in sorted(d for d in PARTS.iterdir() if d.is_dir()):
        for part in sorted(d for d in fam.iterdir() if d.is_dir() and not d.name.startswith(("_", "."))):
            r = {"family": fam.name, "id": part.name, "steps": {}}
            man = part / "manifest.json"
            if not man.exists():
                r["steps"]["manifest"] = ("FAIL", "manifest.json missing", 0)
                rows.append(r); continue
            m = json.loads(man.read_text(encoding="utf-8"))
            missing = [v for v in m.get("files", {}).values() if not (part / v).exists()]
            r["steps"]["manifest"] = ("FAIL", f"missing files {missing}", 0) if missing else ("PASS", "", 0)
            r["targets"] = m.get("targets"); r["install_seat"] = m.get("install_seat")
            r["has_php"] = any(part.glob("*.php"))
            if (part / "part.js").exists():
                rc, o, e, s = run(["node", "--check", "part.js"], part)
                r["steps"]["node --check"] = ("PASS" if rc == 0 else "FAIL", (e or o).strip()[-300:], s)
            rc, o, e, s = run([sys.executable, a.fleet_check, "part", "."], part)
            last = [l for l in (o + e).splitlines() if l.strip()]
            r["steps"]["fleet_check part"] = ("PASS" if rc == 0 else "FAIL", "\n".join(last[-6:]) if rc else (last[-1] if last else ""), s)
            if (part / "part.css").exists():
                rc, o, e, s = run([sys.executable, a.webcheck, "css", "part.css"], part)
                last = [l for l in (o + e).splitlines() if l.strip()]
                r["steps"]["webcheck css"] = ("PASS" if rc == 0 else "FAIL", "\n".join(last[-4:]) if rc else (last[-1] if last else ""), s)
            t = [x.lower() for x in (m.get("targets") or [])]
            theme = ("oceanwp" in t or "generatepress" in t) and r["has_php"]
            r["steps"]["theme integration (OceanWP/GeneratePress)"] = (
                "PASS" if theme else "NOT-RUN",
                "" if theme else f"targets={m.get('targets')}, snippet.php shipped={r['has_php']}; nothing to install into a child theme; sites paused", 0)
            rows.append(r)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    names = ["manifest", "node --check", "fleet_check part", "webcheck css", "theme integration (OceanWP/GeneratePress)"]
    tot = {n: {"PASS": 0, "FAIL": 0, "NOT-RUN": 0} for n in names}
    secs = {n: 0.0 for n in names}
    for r in rows:
        for n, (st, _, s) in r["steps"].items():
            tot[n][st] += 1; secs[n] += s
    md = [f"# PARTS {stamp} - integration test", "", f"Parts found: {len(rows)} (" + ", ".join(f"{f}: {sum(1 for r in rows if r['family']==f)}" for f in sorted({r['family'] for r in rows})) + ")", "",
          "| Step | PASS | FAIL | NOT-RUN | Seconds total |", "|---|---|---|---|---|"]
    for n in names:
        md.append(f"| {n} | {tot[n]['PASS']} | {tot[n]['FAIL']} | {tot[n]['NOT-RUN']} | {secs[n]:.1f} |")
    fails = [(r, n, v) for r in rows for n, v in r["steps"].items() if v[0] == "FAIL"]
    md += ["", f"## Failures ({len(fails)})", ""]
    by = {}
    for r, n, v in fails:
        by.setdefault((r["family"], n, v[1].splitlines()[-1] if v[1] else ""), []).append(r["id"])
    for (fam, n, msg), ids in sorted(by.items()):
        md += [f"- {fam} / {n}: {len(ids)} part(s), e.g. `{ids[0]}`. Last line: `{msg}`"]
    md += ["", "## Per part", "", "| Part | manifest | node | fleet_check | webcheck css | theme |", "|---|---|---|---|---|---|"]
    for r in rows:
        g = lambda n: r["steps"].get(n, ("-",))[0]
        md.append(f"| {r['family']}/{r['id']} | {g('manifest')} | {g('node --check')} | {g('fleet_check part')} | {g('webcheck css')} | {g('theme integration (OceanWP/GeneratePress)')} |")
    text = "\n".join(md) + "\n"
    print(text[:3500])
    if a.out_dir:
        Path(a.out_dir).mkdir(parents=True, exist_ok=True)
        (Path(a.out_dir) / f"PARTS_{stamp}.md").write_text(text, encoding="utf-8")
        (Path(a.out_dir) / f"PARTS_{stamp}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 1 if fails else 0
raise SystemExit(main())