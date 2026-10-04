"""Attempt directories under a root. Release writes a marker and never deletes."""
from __future__ import annotations

import tempfile
from pathlib import Path


def _segment(name: str) -> None:
    if not isinstance(name, str) or name == "" or name in {".", ".."}:
        raise ValueError("attempt name must be one path segment")
    if "/" in name or "\\" in name:
        raise ValueError("attempt name must be one path segment")
    path = Path(name)
    if path.is_absolute() or path.drive or path.anchor or path.name != name:
        raise ValueError("attempt name must be one path segment")


def _inside(path: Path, root: Path) -> bool:
    if path == root:
        return False
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def attempt_dir(root: Path, name: str) -> Path:
    """Create root/name. name is one segment. The result stays inside root."""
    root_path = Path(root)
    if not root_path.is_dir():
        raise ValueError("root must be an existing directory")
    _segment(name)
    root_resolved = root_path.resolve()
    resolved = (root_resolved / name).resolve()
    if not _inside(resolved, root_resolved):
        raise ValueError("attempt directory is outside root")
    resolved.mkdir(exist_ok=True)
    final = resolved.resolve()
    if not _inside(final, root_resolved) or not final.is_dir():
        raise ValueError("attempt directory is outside root")
    return final


def release(directory: Path, root: Path) -> None:
    """Write _released.txt inside directory. Never delete the attempt."""
    root_path = Path(root)
    if not root_path.is_dir():
        raise ValueError("root must be an existing directory")
    root_resolved = root_path.resolve()
    resolved = Path(directory).resolve()
    if not _inside(resolved, root_resolved) or not resolved.is_dir():
        raise ValueError("directory is outside root")
    marker = resolved / "_released.txt"
    if marker.is_symlink() or not _inside(marker, root_resolved):
        raise ValueError("directory is outside root")
    marker.write_text("released", encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        made = attempt_dir(root, "job1")
        assert made == (root.resolve() / "job1")
        assert made.is_dir()
        absolute_name = str((root / "abs-name").resolve())
        for bad in ("..", "a/b", absolute_name):
            try:
                attempt_dir(root, bad)
            except ValueError:
                continue
            raise AssertionError(bad)
        release(made, root)
        assert made.is_dir()
        text = (made / "_released.txt").read_text(encoding="utf-8")
        assert text == "released"
    print("sandbox selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
