"""Prove lock.txt reads and locked destinations. Writes only under tempfile."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.lock_file import LockError, assert_unlocked, read_locks


def _expect_raise(project: Path, dest: Path) -> None:
    try:
        assert_unlocked(project, dest)
    except LockError:
        return
    raise AssertionError(f"expected LockError for {dest}")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        project = root / "project"
        project.mkdir()
        outside = root / "outside"
        outside.mkdir()
        sibling = root / "project2"
        sibling.mkdir()

        missing = read_locks(project)
        if missing != {"ok": True, "present": False, "locks": [], "error": ""}:
            raise AssertionError(missing)
        assert_unlocked(project, project / "index.html")
        if (project / "lock.txt").exists():
            raise AssertionError("missing lock created lock.txt")

        lock = project / "lock.txt"
        lock.write_text("  index.html  \r\nsites/out/page.html\r\n\r\n", encoding="utf-8")
        good = read_locks(project)
        if good != {
            "ok": True,
            "present": True,
            "locks": ["index.html", "sites/out/page.html"],
            "error": "",
        }:
            raise AssertionError(good)
        before = lock.read_bytes()
        _expect_raise(project, project / "index.html")
        _expect_raise(project, project / "sites" / "out" / "page.html")
        assert_unlocked(project, project / "other.html")
        assert_unlocked(project, outside / "index.html")
        assert_unlocked(project, sibling / "index.html")
        if lock.read_bytes() != before:
            raise AssertionError("assert_unlocked wrote lock.txt")

        lock.write_text("dir\\nested\\page.html\n", encoding="utf-8")
        native = read_locks(project)
        if native["ok"] is not True or native["locks"] != ["dir\\nested\\page.html"]:
            raise AssertionError(native)
        _expect_raise(project, project / "dir" / "nested" / "page.html")
        assert_unlocked(project, outside / "dir" / "nested" / "page.html")

        if os.name == "nt":
            lock.write_text("Index.HTML\n", encoding="utf-8")
            _expect_raise(project, project / "index.html")
            _expect_raise(project, project / "INDEX.HTML")
            assert_unlocked(project, outside / "INDEX.HTML")
            lock.write_text("C:/Windows/note.txt\n", encoding="utf-8")
            drive = read_locks(project)
            if drive["ok"] is not False or drive["locks"] != [] or not drive["error"]:
                raise AssertionError(drive)

        for bad in (
            "../secret\n",
            "/etc/passwd\n",
            "http://example.test/a\n",
            "https://example.test/a\n",
            "file:///tmp/x\n",
            "sub/http:logo\n",
            "FILE:share\n",
        ):
            lock.write_text("index.html\n" + bad, encoding="utf-8")
            row = read_locks(project)
            if row["ok"] is not False or row["locks"] != [] or not row["error"]:
                raise AssertionError((bad, row))
            assert_unlocked(project, outside / "index.html")

    print("lock_file selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
