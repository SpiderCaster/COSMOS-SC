"""Saved structure: frame, mold, and the part id for each site section."""
from __future__ import annotations

import json
from pathlib import Path

SCHEMA = "spidercaster-structure/1"


def _part_id(picks: dict, section_id: str, section_type: str) -> str:
    chosen = picks.get(section_id) or picks.get(section_type) or ""
    return chosen if isinstance(chosen, str) else ""


def make_structure(site: dict, frame_id: str, mold_id: str, picks: dict) -> dict:
    """Copy pages and sections from site. Do not invent section types."""
    pages_in = site.get("pages") if isinstance(site, dict) else None
    if not isinstance(pages_in, list):
        pages_in = []
    if not isinstance(picks, dict):
        picks = {}
    pages = []
    for page in pages_in:
        if not isinstance(page, dict):
            continue
        slug = page.get("slug")
        if not isinstance(slug, str):
            slug = ""
        sections = []
        raw_sections = page.get("sections")
        if isinstance(raw_sections, list):
            for sec in raw_sections:
                if not isinstance(sec, dict):
                    continue
                sec_type = sec.get("type")
                if not isinstance(sec_type, str):
                    continue
                sec_id = sec.get("id")
                if not isinstance(sec_id, str):
                    sec_id = ""
                sections.append({
                    "id": sec_id,
                    "type": sec_type,
                    "part_id": _part_id(picks, sec_id, sec_type),
                })
        pages.append({"slug": slug, "sections": sections})
    return {
        "schema": SCHEMA,
        "frame_id": frame_id if isinstance(frame_id, str) else "",
        "mold_id": mold_id if isinstance(mold_id, str) else "",
        "pages": pages,
    }


def save_structure(path: Path, data: dict) -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    dest.write_text(text, encoding="utf-8", newline="\n")


def load_structure(path: Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("structure is not an object")
    return data


def validate_structure(data: dict, planned_types: list[str]) -> list[str]:
    """Return error strings. An empty list means the structure is valid.

    Every section type must be in planned_types. Extra pages are not errors.
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["structure is not an object"]
    if data.get("schema") != SCHEMA:
        errors.append("bad schema")
    if not isinstance(data.get("frame_id"), str):
        errors.append("frame_id must be a string")
    if not isinstance(data.get("mold_id"), str):
        errors.append("mold_id must be a string")
    if not isinstance(planned_types, list) or not all(isinstance(item, str) for item in planned_types):
        errors.append("planned_types must be a list of strings")
        allowed: set[str] = set()
    else:
        allowed = set(planned_types)
    pages = data.get("pages")
    if not isinstance(pages, list):
        errors.append("pages must be a list")
        return errors
    for pi, page in enumerate(pages):
        if not isinstance(page, dict):
            errors.append(f"pages[{pi}] must be an object")
            continue
        if not isinstance(page.get("slug"), str):
            errors.append(f"pages[{pi}].slug must be a string")
        sections = page.get("sections")
        if not isinstance(sections, list):
            errors.append(f"pages[{pi}].sections must be a list")
            continue
        for si, sec in enumerate(sections):
            where = f"pages[{pi}].sections[{si}]"
            if not isinstance(sec, dict):
                errors.append(f"{where} must be an object")
                continue
            if not isinstance(sec.get("id"), str):
                errors.append(f"{where}.id must be a string")
            if not isinstance(sec.get("part_id"), str):
                errors.append(f"{where}.part_id must be a string")
            sec_type = sec.get("type")
            if not isinstance(sec_type, str):
                errors.append(f"{where}.type must be a string")
                continue
            if sec_type not in allowed:
                errors.append(f"section type not planned: {sec_type}")
    return errors


def _sec_key(sec: dict) -> tuple[str, str, str]:
    def text(field: str) -> str:
        value = sec.get(field)
        return value if isinstance(value, str) else ""

    return (text("id"), text("type"), text("part_id"))


def subset_edit(fresh: dict, edited: dict) -> tuple[dict | None, list[str]]:
    """Return ``edited`` when it only drops or reorders rows from ``fresh``.

    Schema, frame, mold, page count, and slugs must match. A new section,
    a changed id, type, or part id, or a move onto another page is refused.
    """
    errors: list[str] = []
    if not isinstance(fresh, dict) or not isinstance(edited, dict):
        return None, ["structure is not an object"]
    for field in ("schema", "frame_id", "mold_id"):
        if edited.get(field) != fresh.get(field):
            errors.append(f"{field} changed")
    fresh_pages = fresh.get("pages")
    edited_pages = edited.get("pages")
    if not isinstance(fresh_pages, list) or not isinstance(edited_pages, list):
        errors.append("pages must be a list")
        return None, errors
    if len(fresh_pages) != len(edited_pages):
        errors.append("page count changed")
        return None, errors
    for index, (fresh_page, edited_page) in enumerate(zip(fresh_pages, edited_pages)):
        if not isinstance(fresh_page, dict) or not isinstance(edited_page, dict):
            errors.append(f"pages[{index}] must be an object")
            continue
        if fresh_page.get("slug") != edited_page.get("slug"):
            errors.append(f"slug changed on page {index}")
            continue
        fresh_sections = fresh_page.get("sections")
        edited_sections = edited_page.get("sections")
        if not isinstance(fresh_sections, list) or not isinstance(edited_sections, list):
            errors.append(f"pages[{index}].sections must be a list")
            continue
        fresh_keys = [_sec_key(sec) for sec in fresh_sections if isinstance(sec, dict)]
        seen: set[tuple[str, str, str]] = set()
        for sec in edited_sections:
            if not isinstance(sec, dict):
                errors.append(f"pages[{index}] section must be an object")
                continue
            key = _sec_key(sec)
            if key in seen:
                errors.append(f"duplicate section: {key[0]}")
            seen.add(key)
            if key not in fresh_keys:
                errors.append(f"section not planned: {key[0]} {key[1]} {key[2]}")
    if errors:
        return None, errors
    return edited, []


def apply_subset(site: dict, kept: dict) -> None:
    """Reorder and drop site sections to match a subset. The section objects stay."""
    pages = site.get("pages") if isinstance(site, dict) else None
    kept_pages = kept.get("pages") if isinstance(kept, dict) else None
    if not isinstance(pages, list) or not isinstance(kept_pages, list):
        return
    for page, kept_page in zip(pages, kept_pages):
        if not isinstance(page, dict) or not isinstance(kept_page, dict):
            continue
        sections = page.get("sections")
        if not isinstance(sections, list):
            sections = []
        pools: dict[tuple[str, str], list] = {}
        for sec in sections:
            if not isinstance(sec, dict):
                continue
            sid = sec.get("id") if isinstance(sec.get("id"), str) else ""
            sec_type = sec.get("type") if isinstance(sec.get("type"), str) else ""
            pools.setdefault((sid, sec_type), []).append(sec)
        ordered = []
        kept_sections = kept_page.get("sections")
        if not isinstance(kept_sections, list):
            kept_sections = []
        for sec in kept_sections:
            if not isinstance(sec, dict):
                continue
            sid = sec.get("id") if isinstance(sec.get("id"), str) else ""
            sec_type = sec.get("type") if isinstance(sec.get("type"), str) else ""
            bucket = pools.get((sid, sec_type)) or []
            if bucket:
                ordered.append(bucket.pop(0))
        page["sections"] = ordered
