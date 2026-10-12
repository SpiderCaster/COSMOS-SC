"""Read-only tree check. No secrets, no key files, no site output."""
from __future__ import annotations

import json
import os
import platform
from pathlib import Path

from lib.crew import ROLES
from lib.hands import HANDS

_SEATS = ("architect", "content", "frontend", "graphics", "visual", "seo", "deployer")
_VAULT = Path(r"V:\streams\webdev\vendor-vault")


def _root(root: Path | None) -> Path:
    if root is None:
        return Path(__file__).resolve().parent.parent
    return Path(root).resolve()


def _mold_ids(molds_dir: Path) -> list[str]:
    ids: list[str] = []
    if not molds_dir.is_dir():
        return ids
    for path in sorted(molds_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        mold_id = data.get("id") if isinstance(data, dict) else None
        if isinstance(mold_id, str) and mold_id:
            ids.append(mold_id)
    return ids


def report(root: Path | None = None) -> dict:
    tree = _root(root)
    molds = _mold_ids(tree / "library" / "molds")
    frames_dir = tree / "library" / "frames"
    frames = len(list(frames_dir.glob("*.json"))) if frames_dir.is_dir() else 0
    seats_dir = tree / "library" / "seats"
    seats = []
    errors: list[str] = []
    for seat_id in _SEATS:
        skill = (seats_dir / seat_id / "SKILL.md").is_file()
        wrapper = (seats_dir / seat_id / "WRAPPER.md").is_file()
        seats.append({"id": seat_id, "skill": skill, "wrapper": wrapper})
        if not skill:
            errors.append(f"seat file missing: {seat_id}/SKILL.md")
        if not wrapper:
            errors.append(f"seat file missing: {seat_id}/WRAPPER.md")
    flat = [name for role in ROLES for name in role["hands"]]
    hands_match = flat == list(HANDS)
    for required in ("clarify-mix", "discover-grid", "warmth-authority"):
        if required not in molds:
            errors.append(f"shipped mold missing: {required}")
    if not hands_match:
        errors.append("hands do not match")
    env = (os.environ.get("SPIDERCASTER_VAULT") or "").strip()
    vault = Path(env) if env else _VAULT
    return {
        "python": platform.python_version(),
        "root": str(tree),
        "molds": molds,
        "frames": frames,
        "seats": seats,
        "hands_match": hands_match,
        "vault_exists": vault.exists(),
        "ok": not errors,
        "errors": errors,
    }


def main() -> int:
    data = report()
    if data["ok"]:
        print("doctor selftest ok")
        return 0
    for err in data["errors"]:
        print(err)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
