"""Run the SpiderCaster Python checker bench (stdlib-only runner; checkers are dev tools).

Usage: python tools/pycheckers/run.py [path...]  (default: lib/)
Runs, in order: ruff, pycodestyle, flake8, black --check, mypy, pylint,
bandit, vulture, pytest (collect-only ping), pip-audit, detect-secrets scan.
Exit 1 on any FAIL. Never modifies files (black --check only, no --fix).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = sys.argv[1:] or ["lib"]

CHECKS = [
    ([sys.executable, "-m", "ruff", "check"] + TARGETS, "ruff"),
    ([sys.executable, "-m", "pycodestyle", "--max-line-length=100"] + TARGETS, "pycodestyle"),
    ([sys.executable, "-m", "flake8", "--max-line-length=100"] + TARGETS, "flake8"),
    ([sys.executable, "-m", "black", "--check", "--line-length=100"] + TARGETS, "black-check"),
    ([sys.executable, "-m", "mypy"] + TARGETS, "mypy"),
    ([sys.executable, "-m", "pylint", "--disable=all", "--enable=E"] + TARGETS, "pylint-errors"),
    ([sys.executable, "-m", "bandit", "-r", "-q"] + TARGETS, "bandit"),
    ([sys.executable, "-m", "vulture"] + TARGETS, "vulture"),
    ([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests"], "pytest-collect"),
    ([sys.executable, "-m", "pip_audit", "-r", "tools/pycheckers/requirements-pycheckers.txt"], "pip-audit"),
    ([sys.executable, "-m", "detect_secrets", "scan", "--all-files"] + TARGETS, "detect-secrets"),
]


def main() -> int:
    failed = []
    for cmd, name in CHECKS:
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
        except FileNotFoundError:
            print("SKIP %s: module missing (pip install -r tools/pycheckers/requirements-pycheckers.txt)" % name)
            continue
        except subprocess.TimeoutExpired:
            print("FAIL %s: timeout" % name)
            failed.append(name)
            continue
        ok = r.returncode == 0
        print(("PASS %s" if ok else "FAIL %s") % name)
        if not ok:
            failed.append(name)
            print((r.stdout + r.stderr)[-2000:])
    if failed:
        print("pycheckers FAIL: %s" % ", ".join(failed))
        return 1
    print("pycheckers ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
