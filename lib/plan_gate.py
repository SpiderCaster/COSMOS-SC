"""Stop before HTML. The structure file is the plan. Stdlib only.

``compose --plan`` writes the structure and does not write pages. A later
compose writes HTML. This is not a chat and it does not publish.
"""
from __future__ import annotations

from pathlib import Path


def plan_only_result(out: Path, structure: Path, part_ids: list[str]) -> dict:
    return {
        "ok": True,
        "site_dir": str(out),
        "structure": str(structure),
        "part_ids": list(part_ids),
        "error": "",
        "plan_only": True,
    }


def is_plan_file(path: Path) -> bool:
    """True when the path is a structure file and not an HTML page."""
    return Path(path).name == "structure.json" and Path(path).is_file()
