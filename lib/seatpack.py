"""One seat pack: label, hands, and the skill and wrapper paths. No site output."""
from __future__ import annotations

from pathlib import Path

from lib.crew import ROLES


def _root(root: Path | None) -> Path:
    if root is None:
        return Path(__file__).resolve().parent.parent
    return Path(root).resolve()


def pack(root: Path | None, seat_id: str) -> dict:
    role = next((item for item in ROLES if item["id"] == seat_id), None)
    if role is None:
        raise KeyError(seat_id)
    tree = _root(root)
    seat_dir = tree / "library" / "seats" / seat_id
    return {
        "id": role["id"],
        "label": role["label"],
        "hands": list(role["hands"]),
        "skill": str((seat_dir / "SKILL.md").resolve()),
        "wrapper": str((seat_dir / "WRAPPER.md").resolve()),
        "does_not": role["does_not"],
    }


def main() -> int:
    architect = pack(None, "architect")
    pack(None, "content")
    assert architect["hands"] == ["brief_read", "frame_pick", "mold_pick", "library_bind"]
    print("seatpack selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
