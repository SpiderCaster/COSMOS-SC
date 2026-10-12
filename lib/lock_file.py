"""Read project/lock.txt. Never creates that file."""
from __future__ import annotations

import os
from pathlib import Path

_SCHEMES = ("http:", "https:", "file:")


class LockError(Exception):
    """Destination resolves inside the project and is listed in lock.txt."""


def _result(ok: bool, present: bool, locks: list[str], error: str) -> dict:
    return {"ok": ok, "present": present, "locks": locks, "error": error}


def _line_problem(line: str) -> str:
    folded = line.replace("\\", "/")
    lower = folded.casefold()
    if any(scheme in lower for scheme in _SCHEMES):
        return "contains a scheme"
    if ".." in folded:
        return "contains .."
    path = Path(line)
    if path.is_absolute() or path.drive or path.anchor or folded.startswith("/"):
        return "absolute path"
    return ""


def read_locks(project: Path) -> dict:
    """Return lock.txt lines. A missing file is not an error and is not created."""
    try:
        root = Path(project)
    except TypeError:
        return _result(False, False, [], "project is not a path")
    lock_path = root / "lock.txt"
    try:
        exists = lock_path.exists()
        link = lock_path.is_symlink()
    except OSError:
        return _result(False, False, [], "lock.txt is not readable")
    if not exists:
        if link:
            return _result(False, True, [], "lock.txt is not readable")
        return _result(True, False, [], "")
    if not lock_path.is_file():
        return _result(False, True, [], "lock.txt is not a file")
    try:
        text = lock_path.read_text(encoding="utf-8")
    except UnicodeError:
        return _result(False, True, [], "lock.txt is not utf-8")
    except OSError:
        return _result(False, True, [], "lock.txt is not readable")
    text = text.removeprefix("\ufeff")
    locks: list[str] = []
    for index, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if line == "":
            continue
        problem = _line_problem(line)
        if problem:
            return _result(False, True, [], f"lock.txt line {index} {problem}")
        locks.append(line)
    return _result(True, True, locks, "")


def _key(text: str) -> str:
    parts = [part for part in text.replace("\\", "/").split("/") if part not in ("", ".")]
    rel = "/".join(parts)
    if os.name == "nt":
        return os.path.normcase(rel)
    return rel


def _relative(project: Path, dest: Path) -> str | None:
    """Posix path of dest inside project, or None when dest resolves outside."""
    try:
        root = Path(project).resolve()
        target = Path(dest).resolve()
    except (OSError, TypeError, ValueError) as exc:
        raise LockError("path") from exc
    root_parts = root.parts
    target_parts = target.parts
    if os.name == "nt":
        if len(target_parts) < len(root_parts):
            return None
        for left, right in zip(root_parts, target_parts):
            if os.path.normcase(left) != os.path.normcase(right):
                return None
        rel_parts = target_parts[len(root_parts) :]
    else:
        try:
            rel_parts = target.relative_to(root).parts
        except ValueError:
            return None
    if any(part == ".." for part in rel_parts):
        return None
    if not rel_parts:
        return "."
    return "/".join(rel_parts)


def assert_unlocked(project: Path, dest: Path) -> None:
    """Raise LockError when dest is inside project and its relative path is locked.

    A missing lock file does not raise. A dest that resolves outside project does not raise.
    """
    rel = _relative(project, dest)
    if rel is None:
        return
    found = read_locks(project)
    if not found["ok"] or not found["present"]:
        return
    locked = {_key(item) for item in found["locks"]}
    native = rel.replace("/", "\\") if os.name == "nt" else rel
    if _key(rel) in locked or _key(native) in locked:
        raise LockError(f"locked: {rel}")
