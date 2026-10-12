"""Negative controls for the harness. Copies one widget, injects a defect, and expects the named check to fail.
A harness that cannot fail proves nothing, so run this after any change to _lib.
  python selftest.py
"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = "recent-posts"
CASES = [
    ("font below 16px", ".css", lambda s: s + "\n.sc-recent .sc-recent-t{font-size:14px}\n", ["css.lint", "measure.text_floor.oceanwp@360"]),
    ("rem unit", ".css", lambda s: s + "\n.sc-recent .sc-meta{margin-top:.5rem}\n", ["css.lint"]),
    ("tap target 30px", ".css", lambda s: s + "\n.sc-w .sc-row{min-height:0;padding:0}\n.sc-recent .sc-recent-t{font-size:18px;line-height:18px}\n.sc-recent .sc-meta{display:none}\n", ["measure.tap_44.oceanwp@360"]),
    ("low contrast meta", ".css", lambda s: s + "\n.sc-recent .sc-meta{color:#b0b0b0}\n", ["measure.contrast.oceanwp@360"]),
    ("horizontal overflow", ".css", lambda s: s + "\n.sc-recent{width:700px}\n", ["measure.no_overflow.oceanwp@360"]),
    ("unscoped selector", ".css", lambda s: s + "\nli{color:red}\n", ["css.lint"]),
    ("unclosed tag", ".html", lambda s: s.replace("</section>", ""), ["html.lint.full"]),
    ("exclamation point", "fixture", lambda s: s.replace("Fixture post one", "Fixture post one!"), ["html.lint.full"]),
    ("secret in file", ".css", lambda s: s + '\n/* api_key = "abcd1234efgh5678" */\n', ["secrets.none"]),
    ("undeclared token", ".html", lambda s: s.replace("{{title}}", "{{heading}}", 1), ["tokens.declared"]),
    ("behavior assertion fails", "behavior", lambda s: s.replace("a.length===3", "a.length===4"), ["behavior.rows.oceanwp@360"]),
]


def run_case(name, kind, fn, expect):
    tmp = Path(tempfile.mkdtemp(prefix="scself_"))
    try:
        shutil.copytree(ROOT / "_lib", tmp / "_lib", ignore=shutil.ignore_patterns("__pycache__"))
        dst = tmp / "widgets" / SRC
        shutil.copytree(ROOT / "widgets" / SRC, dst, ignore=shutil.ignore_patterns("demo", "__pycache__"))
        f = {".css": dst / (SRC + ".css"), ".html": dst / (SRC + ".html"), "fixture": dst / "fixture.json", "behavior": dst / "test.behavior.js"}[kind]
        f.write_text(fn(f.read_text(encoding="utf-8")), encoding="utf-8")
        subprocess.run([sys.executable, "test.py"], cwd=str(dst), capture_output=True, text=True)
        res = json.loads((tmp / "results" / (SRC + ".json")).read_text(encoding="utf-8"))
        failed = {c["id"] for c in res["checks"] if not c["ok"]}
        missing = [e for e in expect if e not in failed]
        return not missing, sorted(failed), missing
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    base = subprocess.run([sys.executable, "test.py"], cwd=str(ROOT / "widgets" / SRC), capture_output=True, text=True)
    bad = 0
    print("control (unmodified %s): %s" % (SRC, base.stdout.strip().splitlines()[0] if base.stdout.strip() else base.stderr[-200:]))
    for name, kind, fn, expect in CASES:
        ok, failed, missing = run_case(name, kind, fn, expect)
        print("%s  %-26s expect %s%s" % ("CAUGHT" if ok else "MISSED", name, expect, "" if ok else "  failed instead: %s" % failed))
        bad += 0 if ok else 1
    print("%d of %d defects caught" % (len(CASES) - bad, len(CASES)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
