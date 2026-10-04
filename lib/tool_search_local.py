"""In-memory tool catalog search. No MCP, no network, no file writes."""
from __future__ import annotations

_MAX_HITS = 5


def _fail(error: str) -> dict:
    return {"ok": False, "error": error, "hits": [], "limited": False}


def _row(item: object) -> tuple[str, str] | None:
    if not isinstance(item, dict):
        return None
    name = item.get("name")
    if not isinstance(name, str) or name.strip() == "":
        return None
    description = item.get("description", "")
    if not isinstance(description, str):
        return None
    return name, description


def tool_search_local(query: str, catalog: list) -> dict:
    """Casefold substring search. A name hit outranks a description hit."""
    if not isinstance(query, str) or query.strip() == "":
        return _fail("empty_query")
    if not isinstance(catalog, list):
        return _fail("bad_catalog")
    needle = query.strip().casefold()
    name_hits: list[dict] = []
    desc_hits: list[dict] = []
    for item in catalog:
        row = _row(item)
        if row is None:
            continue
        name, description = row
        hit = {"name": name, "description": description}
        if needle in name.casefold():
            name_hits.append(hit)
        elif needle in description.casefold():
            desc_hits.append(hit)
    matched = name_hits + desc_hits
    if not matched:
        return _fail("no_match")
    return {
        "ok": True,
        "error": None,
        "hits": matched[:_MAX_HITS],
        "limited": len(matched) > _MAX_HITS,
    }


def main() -> int:
    catalog = [
        {"name": "zeta", "description": "has needle in text"},
        {"name": "needle_a", "description": "unrelated one"},
        {"name": "needle_b", "description": "unrelated two"},
        {"name": "needle_c", "description": "unrelated three"},
        {"name": "needle_d", "description": "unrelated four"},
        {"name": "omega", "description": "another needle mention"},
    ]
    assert len(catalog) == 6
    found = tool_search_local("NEEDLE", catalog)
    assert found["ok"] is True
    assert found["error"] is None
    assert found["limited"] is True
    assert len(found["hits"]) == 5
    names = [hit["name"] for hit in found["hits"]]
    assert names.index("needle_a") < names.index("zeta")
    zeta = found["hits"][names.index("zeta")]
    assert "needle" not in zeta["name"].casefold()
    assert "needle" in zeta["description"].casefold()
    empty = tool_search_local("", catalog)
    assert empty["ok"] is False
    assert empty["error"] == "empty_query"
    assert empty["hits"] == []
    assert empty["limited"] is False
    print("tool_search selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
