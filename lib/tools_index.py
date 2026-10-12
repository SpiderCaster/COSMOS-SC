"""Match each catalog row to a built part folder. Read-only. Stdlib only.

The spec is ``V:\\streams\\webdev\\templates\\components\\catalog.jsonl``.
A row is built when some ``manifest.json`` one level under a family folder
lists that catalog id. Folders named ``_...`` or ``....`` are skipped.
"""
from __future__ import annotations

import json
from pathlib import Path

CATALOG = Path(r"V:\streams\webdev\templates\components\catalog.jsonl")
PARTS = Path(r"V:\streams\webdev\tools\parts")


class ToolsIndexError(Exception):
    pass


def _family_dirs(parent: Path) -> list[Path]:
    if not parent.is_dir():
        return []
    return sorted(
        (p for p in parent.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))),
        key=lambda p: p.name.lower(),
    )


def _as_list(raw) -> list:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return raw
    return []


def _first_route(row: dict) -> str:
    for item in _as_list(row.get("route_to")):
        text = str(item).strip()
        if text:
            return text
    return ""


def _catalog_ids(manifest: dict) -> list[str]:
    found: list[str] = []
    for item in _as_list(manifest.get("catalog_ids")):
        text = str(item).strip()
        if text:
            found.append(text)
    return found


def load_catalog(catalog: Path | None = None) -> list[dict]:
    path = Path(catalog) if catalog else CATALOG
    if not path.is_file():
        raise ToolsIndexError(f"catalog missing: {path}")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ToolsIndexError(f"cannot read {path}: {exc}") from exc
    rows: list[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ToolsIndexError(f"{path}:{number}: {exc}") from exc
        if not isinstance(data, dict) or not str(data.get("id") or "").strip():
            raise ToolsIndexError(f"{path}:{number}: row has no id")
        rows.append(data)
    return rows


def built_dirs(parts: Path | None = None) -> dict[str, Path]:
    """Map a catalog id to the first part folder that claims it.

    Family folders, then part folders, are walked in name order. A later
    manifest that repeats an id does not replace the first claim. A manifest
    that is not valid JSON is skipped so a half-written part does not blank
    the index.
    """
    root = Path(parts) if parts else PARTS
    if not root.is_dir():
        raise ToolsIndexError(f"parts tree missing: {root}")
    found: dict[str, Path] = {}
    for family in _family_dirs(root):
        for folder in _family_dirs(family):
            man = folder / "manifest.json"
            if not man.is_file():
                continue
            try:
                data = json.loads(man.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            for catalog_id in _catalog_ids(data):
                found.setdefault(catalog_id, folder)
    return found


def index_rows(catalog: Path | None = None, parts: Path | None = None) -> list[dict]:
    """One dict per catalog row, in file order.

    Keys: ``catalog_id``, ``route`` (first ``route_to``), ``status``
    (``built`` or ``missing``), and ``part_dir`` when the row is built.
    """
    claimed = built_dirs(parts)
    rows: list[dict] = []
    for row in load_catalog(catalog):
        catalog_id = str(row["id"]).strip()
        part = claimed.get(catalog_id)
        item = {
            "catalog_id": catalog_id,
            "route": _first_route(row),
            "status": "built" if part is not None else "missing",
        }
        if part is not None:
            item["part_dir"] = str(part)
        rows.append(item)
    return rows


def counts(rows: list[dict]) -> dict[str, int]:
    built = sum(1 for row in rows if row.get("status") == "built")
    return {"rows": len(rows), "built": built, "missing": len(rows) - built}
