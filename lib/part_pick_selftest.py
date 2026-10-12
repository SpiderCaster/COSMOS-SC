"""Prove part pick against the real catalog.

Run from the engine root: ``python lib/part_pick_selftest.py``.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.ir import SECTION_TYPES
from lib.part_pick import (
    CHROME_KIND_ORDER,
    CHROME_ROUTE,
    SECTION_KIND_ORDER,
    SECTION_ROUTE,
    pick_chrome,
    pick_part,
)
from lib.tools_index import built_dirs, load_catalog

_KEYS = ("ok", "catalog_id", "part_dir", "kind", "route", "error")


def _fail(msg: str) -> int:
    print("part_pick selftest FAIL: " + msg)
    return 1


def _eligible(rows: list[dict], kinds: tuple[str, ...], route: str) -> list[str]:
    wanted = set(kinds)
    return [
        row["catalog_id"]
        for row in rows
        if row["route"] == route and row["kind"] in wanted
    ]


def _expected(rows: list[dict], kinds: tuple[str, ...], route: str, skip: set[str]) -> str:
    for kind in kinds:
        ids = [
            row["catalog_id"]
            for row in rows
            if row["route"] == route and row["kind"] == kind and row["catalog_id"] not in skip
        ]
        if ids:
            return min(ids)
    return ""


def _built(catalog: list[dict], claimed: dict) -> list[dict]:
    rows: list[dict] = []
    for row in catalog:
        catalog_id = str(row.get("id") or "").strip()
        if not catalog_id or catalog_id not in claimed:
            continue
        raw = row.get("route_to")
        if isinstance(raw, str):
            items = [raw]
        elif isinstance(raw, list):
            items = raw
        else:
            items = []
        route = ""
        for item in items:
            text = str(item).strip()
            if text:
                route = text
                break
        rows.append(
            {
                "catalog_id": catalog_id,
                "kind": str(row.get("kind") or "").strip().lower(),
                "route": route,
            }
        )
    return rows


def _check_ok(result: dict, label: str) -> str | None:
    if set(result) != set(_KEYS):
        return f"{label} keys {sorted(result)}"
    if result["ok"] is not True:
        return f"{label} not ok: {result.get('error')}"
    if not result["catalog_id"] or not result["part_dir"]:
        return f"{label} missing id or part_dir"
    if result["error"]:
        return f"{label} error set on success"
    return None


def _check_second(pick, name: str, kinds: tuple[str, ...], route: str, rows: list[dict]) -> str | None:
    first = pick(name)
    bad = _check_ok(first, name)
    if bad:
        return bad
    eligible = _eligible(rows, kinds, route)
    expect = _expected(rows, kinds, route, set())
    if first["catalog_id"] != expect:
        return f"{name} picked {first['catalog_id']}, smallest is {expect}"
    if len(eligible) > 1:
        second = pick(name, used={first["catalog_id"]})
        bad = _check_ok(second, f"{name} second")
        if bad:
            return bad
        expect_next = _expected(rows, kinds, route, {first["catalog_id"]})
        if second["catalog_id"] == first["catalog_id"] or second["catalog_id"] != expect_next:
            return f"{name} second pick {second['catalog_id']} != {expect_next}"
    return None


def main() -> int:
    catalog = load_catalog()
    if not catalog:
        return _fail("real catalog is empty")
    rows = _built(catalog, built_dirs())
    if not rows:
        return _fail("no built catalog rows")
    for section_type in SECTION_TYPES:
        kinds = SECTION_KIND_ORDER.get(section_type)
        if not kinds:
            return _fail(f"{section_type} has no kind order")
        bad = _check_second(pick_part, section_type, kinds, SECTION_ROUTE, rows)
        if bad:
            return _fail(bad)
    for slot, kinds in CHROME_KIND_ORDER.items():
        bad = _check_second(pick_chrome, slot, kinds, CHROME_ROUTE, rows)
        if bad:
            return _fail(bad)
    unknown = pick_part("hero", override="no-such-catalog-id")
    if unknown["ok"] is not False:
        return _fail("unknown override returned ok true")
    if unknown["catalog_id"] or unknown["part_dir"] or unknown["kind"] or unknown["route"]:
        return _fail("unknown override did not return empty ids")
    print("part_pick selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
