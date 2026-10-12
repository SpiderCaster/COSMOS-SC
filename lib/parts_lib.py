"""Index every SpiderCaster part manifest. Read-only. Stdlib only.

Three trees are scanned, in this order:

- fleet parts at ``V:\\streams\\webdev\\tools\\parts`` (``SPIDERCASTER_PARTS``)
- the header, popup, and hook kit (``SPIDERCASTER_KIT``)
- the in-repo sidebar and widget suite under ``tools/sidebars-widgets``

A kit item is skipped when a fleet manifest already names its folder as
``source_kit_item`` or ``source_item``. Every other manifest is kept.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from lib.check import FLEET_SAMPLE_PATTERNS, SOFT_PATTERNS

ENGINE_TREE = Path(__file__).resolve().parent.parent / "tools" / "sidebars-widgets"
_FLEET = Path(r"V:\streams\webdev\tools\parts")
_KIT = Path(r"V:\streams\webdev\kits\SPIDERCASTER_KIT\sc-tools")
_BAD_TOKEN = re.compile(r"placeholder|lorem|ipsum", re.IGNORECASE)
_FAMILY_ALIAS = {
    "popups-callouts": "popups_callouts",
    "hooks-blocks": "hooks_blocks",
    "widgets": "sidebars",
}


def default_roots() -> dict[str, Path]:
    fleet = os.environ.get("SPIDERCASTER_PARTS")
    kit = os.environ.get("SPIDERCASTER_KIT")
    return {
        "fleet": Path(fleet) if fleet else _FLEET,
        "kit": Path(kit) if kit else _KIT,
        "engine": ENGINE_TREE,
    }


def safe_visible(text: str) -> str:
    """Empty when the checker would reject this string on a built page."""
    flat = " ".join(str(text or "").split())
    if not flat:
        return ""
    for rx in (*FLEET_SAMPLE_PATTERNS, *SOFT_PATTERNS):
        if rx.search(flat):
            return ""
    return flat


def html_id_for(pid: str) -> str:
    cleaned = str(pid or "").strip()
    if not safe_visible(cleaned):
        cleaned = _BAD_TOKEN.sub("", cleaned)
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", cleaned).strip("-")
    if not cleaned or not re.match(r"^[A-Za-z]", cleaned):
        cleaned = "p-" + (cleaned or "part")
    return cleaned


def _dirs(parent: Path) -> list[Path]:
    if not parent.is_dir():
        return []
    return sorted(
        (p for p in parent.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))),
        key=lambda p: p.name.lower(),
    )


def _load(folder: Path) -> dict | None:
    man = folder / "manifest.json"
    if not man.is_file():
        return None
    try:
        data = json.loads(man.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _targets(manifest: dict) -> list[str]:
    raw = manifest.get("targets") or []
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if str(item).strip()]


def _record(folder: Path, manifest: dict, family: str, origin: str) -> dict:
    pid = str(manifest.get("tool_id") or manifest.get("id") or manifest.get("slug") or folder.name)
    name = safe_visible(manifest.get("name") or "") or safe_visible(pid) or "Part"
    purpose = safe_visible(manifest.get("purpose") or manifest.get("best_for") or "")
    if len(purpose) > 240:
        purpose = purpose[:237].rsplit(" ", 1)[0] + "..."
    php = (folder / "snippet.php").is_file() or any(folder.glob("*.php"))
    source = str(manifest.get("source_kit_item") or manifest.get("source_item") or "")
    return {
        "id": pid,
        "html_id": html_id_for(pid),
        "name": name,
        "purpose": purpose,
        "family": _FAMILY_ALIAS.get(family, family),
        "origin": origin,
        "targets": _targets(manifest),
        "runtime": "theme-hook" if php else "static",
        "dir": str(folder),
        "source": source,
    }


def _add(found: list[dict], seen: set[str], covered: set[str], rec: dict) -> None:
    pid = rec["id"]
    html_id = rec["html_id"]
    if pid in seen or html_id in seen:
        pid = rec["origin"] + "-" + pid
        html_id = html_id_for(pid)
        rec = {**rec, "id": pid, "html_id": html_id}
    if pid in seen or html_id in seen:
        return
    seen.add(pid)
    seen.add(html_id)
    found.append(rec)
    source = rec.get("source") or ""
    if source:
        covered.add(Path(source).name.lower())


def scan(roots: dict[str, Path] | None = None) -> list[dict]:
    roots = roots or default_roots()
    found: list[dict] = []
    seen: set[str] = set()
    covered: set[str] = set()

    fleet = roots.get("fleet") or _FLEET
    for family_dir in _dirs(fleet):
        for folder in _dirs(family_dir):
            manifest = _load(folder)
            if manifest is None:
                continue
            _add(found, seen, covered, _record(folder, manifest, family_dir.name, "fleet"))

    engine = roots.get("engine") or ENGINE_TREE
    for group in _dirs(engine):
        for folder in _dirs(group):
            manifest = _load(folder)
            if manifest is None:
                continue
            _add(found, seen, covered, _record(folder, manifest, group.name, "engine"))

    kit = roots.get("kit") or _KIT
    for family_dir in _dirs(kit):
        items = family_dir / "items"
        for folder in _dirs(items):
            if folder.name.lower() in covered:
                continue
            manifest = _load(folder)
            if manifest is None:
                continue
            _add(found, seen, covered, _record(folder, manifest, family_dir.name, "kit"))

    found.sort(key=lambda rec: (rec["family"], rec["origin"], rec["id"]))
    return found


def family_counts(parts: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rec in parts:
        counts[rec["family"]] = counts.get(rec["family"], 0) + 1
    return counts
