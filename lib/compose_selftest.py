"""Compose demo-local offline and prove the lock. Run from the engine root:

python lib/compose_selftest.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.check import check_site
from lib.compose import compose_project
from lib.copy_pack import project_copy_text

PROJECT = Path(r"V:\A\Ai\spidercaster\working\projects\demo-local")
PALETTE = "#2a6f8f"


def _fail(msg: str) -> int:
    print(msg)
    return 1


def _locked_project(root: Path) -> tuple[Path, Path]:
    project = root / "locked-project"
    (project / "copy").mkdir(parents=True)
    (project / "copy" / "overview.md").write_text(
        "# Locked page\n\nThis copy is only here so a missed lock would still build.\n",
        encoding="utf-8",
    )
    out = project / "out"
    (project / "lock.txt").write_text("out\n", encoding="utf-8")
    return project, out


def _part_ids(structure_path: Path) -> list[str]:
    data = json.loads(structure_path.read_text(encoding="utf-8"))
    found = []
    for page in data.get("pages") or []:
        if not isinstance(page, dict):
            continue
        for sec in page.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            part_id = sec.get("part_id")
            if isinstance(part_id, str) and part_id:
                found.append(part_id)
    return found


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="sc-compose-") as tmp:
        root = Path(tmp)
        out = root / "site"
        result = compose_project(
            PROJECT,
            out,
            frame_id="welcome-scroll",
            mold_id="discover-grid",
        )
        if not isinstance(result, dict) or not result.get("ok"):
            error = result.get("error") if isinstance(result, dict) else result
            return _fail(f"compose failed: {error}")
        report = check_site(
            out,
            expect_noindex=True,
            quiet=True,
            copy_text=project_copy_text(PROJECT),
        )
        fails = [row for row in report.rows if row.get("status") == "FAIL"]
        if fails:
            for row in fails:
                print(f"FAIL {row.get('name')}: {row.get('detail')}")
                for item in (row.get("failures") or [])[:8]:
                    print(f"  {item}")
            return _fail(f"check_site FAIL {len(fails)}")
        html = (out / "index.html").read_text(encoding="utf-8")
        if PALETTE not in html.lower():
            return _fail(f"index.html missing {PALETTE}")
        structure_path = out / "structure.json"
        if not structure_path.is_file():
            return _fail("structure.json missing")
        if not _part_ids(structure_path):
            return _fail("structure.json lists no part ids")

        locked_project, locked_out = _locked_project(root)
        blocked = False
        try:
            locked = compose_project(locked_project, locked_out)
        except Exception:
            blocked = True
        else:
            blocked = isinstance(locked, dict) and locked.get("ok") is False
        if not blocked:
            return _fail("locked out was not refused")
        if (locked_out / "index.html").is_file() or (locked_out / "site.json").is_file():
            return _fail("locked out was written")

    print("compose selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
