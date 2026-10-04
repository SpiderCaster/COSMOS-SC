"""Match permission rules. Decisions only. Does not start a shell or write a file."""
from __future__ import annotations


def _fail(error: str) -> dict:
    return {"ok": False, "error": error, "decision": "deny", "matched_rule": None}


def _done(decision: str, matched_rule: str | None) -> dict:
    return {"ok": True, "error": None, "decision": decision, "matched_rule": matched_rule}


def _parse_rule(rule: object) -> tuple[str, str | None] | None:
    """Return (tool, specifier). specifier None is a bare tool name. None means bad_rule."""
    if not isinstance(rule, str):
        return None
    text = rule.strip()
    if text == "":
        return None
    if "(" not in text and ")" not in text:
        if "*" in text:
            return None
        return text, None
    if text.count("(") != 1 or text.count(")") != 1 or not text.endswith(")"):
        return None
    open_at = text.index("(")
    if open_at < 1 or text.rfind(")") != len(text) - 1:
        return None
    name = text[:open_at]
    if name.strip() != name or name == "" or "*" in name:
        return None
    spec = text[open_at + 1 : -1]
    stars = spec.count("*")
    if stars > 1 or (stars == 1 and not spec.endswith("*")):
        return None
    return name, spec


def _rule_list(items: object) -> list[tuple[str, str | None, str]] | None:
    if not isinstance(items, list):
        return None
    parsed: list[tuple[str, str | None, str]] = []
    for item in items:
        got = _parse_rule(item)
        if got is None or not isinstance(item, str):
            return None
        name, spec = got
        parsed.append((name, spec, item))
    return parsed


def _hits(name: str, spec: str | None, tool: str, arg: str) -> bool:
    if name != tool:
        return False
    if spec is None:
        return True
    if spec.endswith("*") and spec.count("*") == 1:
        return arg.startswith(spec[:-1])
    return arg == spec


def perm_rule(tool: str, arg: str, allow: list[str], deny: list[str]) -> dict:
    """Decide allow, deny, or ask. Deny wins. No match asks. Never runs a command."""
    if not isinstance(tool, str) or tool.strip() == "":
        return _fail("empty_tool")
    if not isinstance(arg, str):
        return _fail("bad_rule")
    denied = _rule_list(deny)
    allowed = _rule_list(allow)
    if denied is None or allowed is None:
        return _fail("bad_rule")
    for name, spec, raw in denied:
        if _hits(name, spec, tool, arg):
            return _done("deny", raw)
    for name, spec, raw in allowed:
        if _hits(name, spec, tool, arg):
            return _done("allow", raw)
    return _done("ask", None)


def main() -> int:
    denied = perm_rule("Bash", "rm -rf /tmp", ["Bash(rm *)"], ["Bash(rm *)"])
    assert denied["ok"] is True
    assert denied["error"] is None
    assert denied["decision"] == "deny"
    assert denied["matched_rule"] == "Bash(rm *)"
    broader = perm_rule("Read", "notes.txt", ["Read"], ["Read(notes.txt)"])
    assert broader["decision"] == "deny"
    assert broader["matched_rule"] == "Read(notes.txt)"

    starred = perm_rule("Bash", "rm -rf /tmp", ["Bash(rm *)"], [])
    assert starred["ok"] is True
    assert starred["decision"] == "allow"
    assert starred["matched_rule"] == "Bash(rm *)"
    assert starred["error"] is None
    assert perm_rule("Bash", "ls", ["Bash(rm *)"], [])["decision"] == "ask"
    assert perm_rule("Bash", "rmdir /tmp", ["Bash(rm *)"], [])["decision"] == "ask"

    mid = perm_rule("Bash", "rm foo", ["Bash(rm * foo)"], [])
    assert mid["ok"] is False
    assert mid["error"] == "bad_rule"
    assert mid["decision"] == "deny"
    assert mid["matched_rule"] is None
    assert perm_rule("Read", "a", ["Read(a*b)"], [])["error"] == "bad_rule"
    assert perm_rule("Bash", "rm", ["Bash(rm *"], [])["error"] == "bad_rule"
    assert perm_rule("Bash", "rm", [""], [])["error"] == "bad_rule"

    asked = perm_rule("Edit", "notes.txt", ["Read"], ["Bash"])
    assert asked == {"ok": True, "error": None, "decision": "ask", "matched_rule": None}
    assert perm_rule("Grep", "", [], [])["decision"] == "ask"

    empty = perm_rule("", "rm", ["Bash"], [])
    assert empty["ok"] is False
    assert empty["error"] == "empty_tool"
    assert empty["decision"] == "deny"
    assert empty["matched_rule"] is None

    print("perm_rule selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
