"""Offline subagent tool allowlist. No spawn, no publish, no file write."""
from __future__ import annotations


def _bare(name: str) -> str:
    """Drop a trailing (...) specifier. The whole tool name is what remains."""
    if name.endswith(")") and "(" in name:
        return name[: name.index("(")].rstrip()
    return name


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    if any(not isinstance(item, str) for item in value):
        return None
    return value


def _bad() -> dict:
    return {"ok": False, "error": "bad_list", "granted": [], "unresolved": []}


def seat_tools(parent: list[str], tools: list[str] | None, disallowed: list[str] | None) -> dict:
    """Filter parent by disallowed, then by tools. Null tools and disallowed inherit parent."""
    parent_list = _string_list(parent)
    if parent_list is None:
        return _bad()
    if tools is None:
        tools_list = None
    else:
        tools_list = _string_list(tools)
        if tools_list is None:
            return _bad()
    if disallowed is None:
        denied_list: list[str] | None = None
    else:
        denied_list = _string_list(disallowed)
        if denied_list is None:
            return _bad()

    denied_raw = set(denied_list or [])
    denied_bare = {_bare(name) for name in denied_raw}
    pool = [name for name in parent_list if name not in denied_bare and name not in denied_raw]
    pool_set = set(pool)

    if tools_list is None:
        return {"ok": True, "error": None, "granted": pool, "unresolved": []}

    granted: list[str] = []
    unresolved: list[str] = []
    for name in tools_list:
        blocked = name in denied_raw or name in denied_bare or _bare(name) in denied_bare
        if name in pool_set and not blocked:
            granted.append(name)
        else:
            unresolved.append(name)
    if tools_list and not granted:
        return {"ok": False, "error": "zero_tools", "granted": [], "unresolved": unresolved}
    return {"ok": True, "error": None, "granted": granted, "unresolved": unresolved}


def main() -> int:
    inherit = seat_tools(["Read", "Edit", "Bash"], None, None)
    assert inherit == {
        "ok": True,
        "error": None,
        "granted": ["Read", "Edit", "Bash"],
        "unresolved": [],
    }

    denied = seat_tools(["Read", "Edit", "Bash"], None, ["Bash(git push *)"])
    assert denied["ok"] is True
    assert denied["error"] is None
    assert denied["granted"] == ["Read", "Edit"]
    assert denied["unresolved"] == []

    filtered = seat_tools(["Read", "Edit", "Bash"], ["Bash", "Read"], None)
    assert filtered["ok"] is True
    assert filtered["granted"] == ["Bash", "Read"]
    assert filtered["unresolved"] == []

    missing = seat_tools(["Read", "Edit"], ["Read", "WebSearch"], None)
    assert missing["ok"] is True
    assert missing["error"] is None
    assert missing["granted"] == ["Read"]
    assert missing["unresolved"] == ["WebSearch"]

    both = seat_tools(["Read", "Bash", "Edit"], ["Read", "Bash"], ["Bash(git push *)"])
    assert both["ok"] is True
    assert both["granted"] == ["Read"]
    assert both["unresolved"] == ["Bash"]

    same = seat_tools(["Read", "Bash"], ["Bash"], ["Bash"])
    assert same["ok"] is False
    assert same["error"] == "zero_tools"
    assert same["granted"] == []
    assert same["unresolved"] == ["Bash"]

    zero = seat_tools(["Read"], ["Nope", "Also"], None)
    assert zero == {
        "ok": False,
        "error": "zero_tools",
        "granted": [],
        "unresolved": ["Nope", "Also"],
    }

    empty_tools = seat_tools(["Read", "Edit"], [], None)
    assert empty_tools == {"ok": True, "error": None, "granted": [], "unresolved": []}

    order = seat_tools(["Edit", "Read", "Bash", "Grep"], None, ["Read"])
    assert order["granted"] == ["Edit", "Bash", "Grep"]

    for bad in (
        seat_tools(["Read", 1], ["Read"], None),
        seat_tools(["Read"], ["Read", None], None),
        seat_tools(["Read"], None, ["Read", 2]),
        seat_tools(None, None, None),
    ):
        assert bad["ok"] is False
        assert bad["error"] == "bad_list"
        assert bad["granted"] == []
        assert bad["unresolved"] == []

    print("seat_tools selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
