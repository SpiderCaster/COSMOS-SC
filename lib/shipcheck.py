"""Ship-ready gate. Subprocess selftests only. No downloads and no secret reads."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

_TIMEOUT_S = 120
_REGRESS_WAIT_S = 90

# name, args after this interpreter, path under the tree, wait once if missing
_STEPS: tuple[tuple[str, tuple[str, ...], tuple[str, ...], bool], ...] = (
    ("lib.doctor", ("-m", "lib.doctor"), ("lib", "doctor.py"), False),
    ("lib.ingest", ("-m", "lib.ingest"), ("lib", "ingest.py"), False),
    ("lib.offline", ("-m", "lib.offline"), ("lib", "offline.py"), False),
    ("lib.frames", ("-m", "lib.frames"), ("lib", "frames.py"), False),
    ("lib.sandbox", ("-m", "lib.sandbox"), ("lib", "sandbox.py"), False),
    ("lib.skill_read", ("-m", "lib.skill_read"), ("lib", "skill_read.py"), False),
    ("lib.hands.selftest", ("-m", "lib.hands.selftest"), ("lib", "hands", "selftest.py"), False),
    ("lib.regress", ("-m", "lib.regress"), ("lib", "regress.py"), True),
    ("lib.triggers", ("-m", "lib.triggers"), ("lib", "triggers.py"), False),
    ("lib.mobile_selftest", ("-m", "lib.mobile_selftest"), ("lib", "mobile_selftest.py"), False),
    ("lib.attempts_selftest", ("-m", "lib.attempts_selftest"), ("lib", "attempts_selftest.py"), False),
    (
        "spidercaster.py crew selftest",
        ("spidercaster.py", "crew", "selftest"),
        ("spidercaster.py",),
        False,
    ),
    (
        "lib/check_claims_selftest.py",
        ("lib/check_claims_selftest.py",),
        ("lib", "check_claims_selftest.py"),
        False,
    ),
    (
        "lib/check_typography_selftest.py",
        ("lib/check_typography_selftest.py",),
        ("lib", "check_typography_selftest.py"),
        False,
    ),
    (
        "lib/ui_selftest.py",
        ("lib/ui_selftest.py",),
        ("lib", "ui_selftest.py"),
        False,
    ),
    (
        "lib/check_tap_selftest.py",
        ("lib/check_tap_selftest.py",),
        ("lib", "check_tap_selftest.py"),
        False,
    ),
    (
        "lib/check_seo_selftest.py",
        ("lib/check_seo_selftest.py",),
        ("lib", "check_seo_selftest.py"),
        False,
    ),
    (
        "lib/check_mobile_selftest.py",
        ("lib/check_mobile_selftest.py",),
        ("lib", "check_mobile_selftest.py"),
        False,
    ),
)


def _root(root: Path | None) -> Path:
    if root is None:
        return Path(__file__).resolve().parent.parent
    return Path(root).resolve()


def _decode(chunk: str | bytes | None) -> str:
    if chunk is None:
        return ""
    if isinstance(chunk, bytes):
        return chunk.decode("utf-8", errors="replace")
    return chunk


def _tail(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def _on_disk(tree: Path, parts: tuple[str, ...]) -> bool:
    path = tree.joinpath(*parts)
    if path.is_file():
        return True
    if path.suffix == ".py":
        return (path.with_suffix("") / "__init__.py").is_file()
    return False


def _command(tree: Path, args: tuple[str, ...]) -> list[str]:
    command = [sys.executable]
    for arg in args:
        if arg.startswith("-") or not arg.endswith(".py"):
            command.append(arg)
        else:
            command.append(str((tree / arg).resolve()))
    return command


def _run(tree: Path, args: tuple[str, ...]) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            _command(tree, args),
            cwd=str(tree),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        text = _decode(exc.stdout) + "\n" + _decode(exc.stderr)
        return False, _tail(text) or "timeout"
    text = _decode(proc.stdout) + "\n" + _decode(proc.stderr)
    return proc.returncode == 0, _tail(text)


def run(root: Path | None = None) -> dict:
    tree = _root(root)
    steps: list[dict] = []
    for name, args, parts, wait in _STEPS:
        if not _on_disk(tree, parts):
            if wait:
                # lib.regress may still be landing. One wait, then a miss fails the gate.
                time.sleep(_REGRESS_WAIT_S)
            if not _on_disk(tree, parts):
                steps.append({"name": name, "ok": False, "tail": "missing"})
                continue
        ok, tail = _run(tree, args)
        steps.append({"name": name, "ok": ok, "tail": tail})
    return {"ok": bool(steps) and all(step["ok"] for step in steps), "steps": steps}


def main() -> int:
    data = run()
    if data["ok"]:
        print("shipcheck ok")
        return 0
    for step in data["steps"]:
        if not step["ok"]:
            print(step["name"])
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
