"""Pick one built catalog part for a section type or a chrome slot.

Smallest catalog_id wins. An override wins only when that id is built.
"""
from __future__ import annotations

from lib.tools_index import built_dirs, load_catalog

# Catalog kind strings already match the contract, lowercase, so the names
# below are real kinds (not inventions). feature-grid is in the catalog but
# unused: card is present for the card-like sections. comparison is tried
# before table because both exist. schema-jsonld, popup, and sidebar kinds
# are never auto-picked (routes below also exclude those families).
#
# tools-hooks-blocks:
#   hero -> hero
#   features, stats, steps, gallery, testimonials, about, team, logocloud -> card
#   pricing -> comparison, then table
#   faq -> faq
#   cta, contact -> cta
#   menu -> table
# tools-headers:
#   header -> header, then sticky-header
#   footer -> footer

SECTION_ROUTE = "tools-hooks-blocks"
CHROME_ROUTE = "tools-headers"

SECTION_KIND_ORDER: dict[str, tuple[str, ...]] = {
    "hero": ("hero",),
    "features": ("card",),
    "stats": ("card",),
    "steps": ("card",),
    "gallery": ("card",),
    "testimonials": ("card",),
    "about": ("card",),
    "team": ("card",),
    "logocloud": ("card",),
    "pricing": ("comparison", "table"),
    "faq": ("faq",),
    "cta": ("cta",),
    "contact": ("cta",),
    "menu": ("table",),
}

CHROME_KIND_ORDER: dict[str, tuple[str, ...]] = {
    "header": ("header", "sticky-header"),
    "footer": ("footer",),
}

_ROWS: list[dict] | None = None


def _route(row: dict) -> str:
    raw = row.get("route_to")
    if isinstance(raw, str):
        items = [raw]
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    for item in items:
        text = str(item).strip()
        if text:
            return text
    return ""


def _built_rows() -> list[dict]:
    """Built rows from load_catalog joined to built_dirs. One walk per process."""
    global _ROWS
    if _ROWS is not None:
        return _ROWS
    claimed = built_dirs()
    rows: list[dict] = []
    for row in load_catalog():
        catalog_id = str(row.get("id") or "").strip()
        part = claimed.get(catalog_id)
        if not catalog_id or part is None:
            continue
        rows.append(
            {
                "catalog_id": catalog_id,
                "part_dir": str(part),
                "kind": str(row.get("kind") or "").strip().lower(),
                "route": _route(row),
            }
        )
    _ROWS = rows
    return rows


def _fail(error: str) -> dict:
    return {
        "ok": False,
        "catalog_id": "",
        "part_dir": "",
        "kind": "",
        "route": "",
        "error": error,
    }


def _ok(row: dict) -> dict:
    return {
        "ok": True,
        "catalog_id": row["catalog_id"],
        "part_dir": row["part_dir"],
        "kind": row["kind"],
        "route": row["route"],
        "error": "",
    }


def _skip(used: set[str] | None) -> set[str]:
    if not used:
        return set()
    return {str(item).strip() for item in used if str(item).strip()}


def _pick(
    name: str,
    kind_order: dict[str, tuple[str, ...]],
    route: str,
    used: set[str] | None,
    override: str,
    unknown_label: str,
) -> dict:
    rows = _built_rows()
    token = str(override or "").strip()
    if token:
        for row in rows:
            if row["catalog_id"] == token:
                return _ok(row)
        return _fail("unknown override")
    kinds = kind_order.get(str(name or "").strip())
    if not kinds:
        return _fail(unknown_label)
    skip = _skip(used)
    pool = [row for row in rows if row["route"] == route and row["kind"]]
    for kind in kinds:
        matches = [
            row for row in pool if row["kind"] == kind and row["catalog_id"] not in skip
        ]
        if matches:
            return _ok(min(matches, key=lambda row: row["catalog_id"]))
    return _fail("no match")


def pick_part(section_type: str, used: set[str] | None = None, override: str = "") -> dict:
    return _pick(
        section_type,
        SECTION_KIND_ORDER,
        SECTION_ROUTE,
        used,
        override,
        "unknown section type",
    )


def pick_chrome(slot: str, used: set[str] | None = None, override: str = "") -> dict:
    return _pick(
        slot,
        CHROME_KIND_ORDER,
        CHROME_ROUTE,
        used,
        override,
        "unknown chrome slot",
    )
