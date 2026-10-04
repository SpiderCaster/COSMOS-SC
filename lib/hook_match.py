"""Match a Claude Code hooks object. Never starts a command. Never writes a file."""
from __future__ import annotations

# Names from the hooks-guide event table, including Notification.
KNOWN_EVENTS = frozenset({
    "SessionStart",
    "Setup",
    "UserPromptSubmit",
    "UserPromptExpansion",
    "PreToolUse",
    "PermissionRequest",
    "PermissionDenied",
    "PostToolUse",
    "PostToolUseFailure",
    "PostToolBatch",
    "Notification",
    "MessageDisplay",
    "SubagentStart",
    "SubagentStop",
    "TaskCreated",
    "TaskCompleted",
    "Stop",
    "StopFailure",
    "TeammateIdle",
    "InstructionsLoaded",
    "ConfigChange",
    "CwdChanged",
    "DirectoryAdded",
    "FileChanged",
    "WorktreeCreate",
    "WorktreeRemove",
    "PreCompact",
    "PostCompact",
    "PreModelSwitch",
    "PostModelSwitch",
    "Elicitation",
    "ElicitationResult",
    "SessionEnd",
})

# These events compare matcher tokens to tool_name. Every other known event does not.
TOOL_EVENTS = frozenset({
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "PermissionRequest",
    "PermissionDenied",
})


def _fail(error: str) -> dict:
    return {"ok": False, "error": error, "matched": [], "ran": False}


def _ok(matched: list[dict]) -> dict:
    return {"ok": True, "error": None, "matched": matched, "ran": False}


def _tokens(matcher: str) -> list[str]:
    parts: list[str] = []
    start = 0
    for index, char in enumerate(matcher):
        if char == "|" or char == ",":
            parts.append(matcher[start:index].strip())
            start = index + 1
    parts.append(matcher[start:].strip())
    return [part for part in parts if part != ""]


def _tool_hit(matcher: object, tool_name: str) -> bool:
    """Empty or missing matcher matches every tool_name. Else case-sensitive tokens."""
    if matcher is None:
        return True
    if not isinstance(matcher, str):
        return False
    if matcher.strip() == "":
        return True
    return tool_name in _tokens(matcher)


def _group(item: object) -> list[dict] | None:
    """Return the hook dicts in one matcher group, or None when the shape is wrong."""
    if not isinstance(item, dict):
        return None
    hooks = item.get("hooks")
    if not isinstance(hooks, list):
        return None
    if "matcher" in item and item["matcher"] is not None and not isinstance(item["matcher"], str):
        return None
    parsed: list[dict] = []
    for hook in hooks:
        if not isinstance(hook, dict):
            return None
        kind = hook.get("type")
        if not isinstance(kind, str) or kind == "":
            return None
        if "command" in hook and not isinstance(hook["command"], str):
            return None
        parsed.append(hook)
    return parsed


def _groups(hooks: object) -> dict[str, list[dict]] | None:
    if not isinstance(hooks, dict):
        return None
    parsed: dict[str, list[dict]] = {}
    for key, value in hooks.items():
        if not isinstance(key, str) or not isinstance(value, list):
            return None
        groups: list[dict] = []
        for item in value:
            if not isinstance(item, dict) or _group(item) is None:
                return None
            groups.append(item)
        parsed[key] = groups
    return parsed


def hook_match(event: str, tool_name: str, hooks: dict) -> dict:
    """Return matched {group, type} rows. group is the matcher-group index. ran is always false."""
    if not isinstance(event, str) or event not in KNOWN_EVENTS:
        return _fail("unknown_event")
    grouped = _groups(hooks)
    if grouped is None:
        return _fail("bad_hooks")
    if event in TOOL_EVENTS and not isinstance(tool_name, str):
        return _fail("bad_hooks")
    matched: list[dict] = []
    for index, item in enumerate(grouped.get(event, [])):
        if event in TOOL_EVENTS and not _tool_hit(item.get("matcher"), tool_name):
            continue
        for hook in item["hooks"]:
            matched.append({"group": index, "type": hook["type"]})
    return _ok(matched)


def main() -> int:
    import os
    import subprocess

    started = {"n": 0}

    def _blocked(*_args, **_kwargs):
        started["n"] += 1
        raise AssertionError("command started")

    real_run = subprocess.run
    real_system = os.system
    subprocess.run = _blocked
    os.system = _blocked
    try:
        command = "py -3.14 -c \"raise SystemExit('executed')\""
        hooks = {
            "PreToolUse": [
                {
                    "matcher": "Read|Grep",
                    "hooks": [{"type": "command", "command": command}],
                }
            ]
        }
        hit = hook_match("PreToolUse", "Read", hooks)
        assert hit == {
            "ok": True,
            "error": None,
            "matched": [{"group": 0, "type": "command"}],
            "ran": False,
        }
        assert started["n"] == 0
        assert hook_match("PreToolUse", "Grep", hooks)["matched"] == [{"group": 0, "type": "command"}]
        assert hook_match("PreToolUse", "read", hooks)["matched"] == []
        assert hook_match("PreToolUse", "Write", hooks)["matched"] == []
        comma = hook_match(
            "PostToolUse",
            "Grep",
            {"PostToolUse": [{"matcher": "Read, Grep", "hooks": [{"type": "command", "command": command}]}]},
        )
        assert comma["ok"] is True and comma["ran"] is False
        assert comma["matched"] == [{"group": 0, "type": "command"}]
        blank = hook_match(
            "PermissionRequest",
            "Write",
            {"PermissionRequest": [{"matcher": "", "hooks": [{"type": "http", "command": command}]}]},
        )
        assert blank["matched"] == [{"group": 0, "type": "http"}]
        assert blank["ran"] is False
        missing = hook_match(
            "PermissionDenied",
            "Anything",
            {"PermissionDenied": [{"hooks": [{"type": "prompt"}]}]},
        )
        assert missing["matched"] == [{"group": 0, "type": "prompt"}]
        stop = hook_match(
            "Stop",
            "Nope",
            {
                "Stop": [
                    {"matcher": "Read|Grep", "hooks": [{"type": "command", "command": command}]},
                    {"hooks": [{"type": "agent"}]},
                ]
            },
        )
        assert stop["ran"] is False
        assert stop["matched"] == [
            {"group": 0, "type": "command"},
            {"group": 1, "type": "agent"},
        ]
        for event in ("SubagentStop", "SessionStart", "Notification"):
            every = hook_match(event, "Nope", {event: [{"matcher": "Read|Grep", "hooks": [{"type": "command", "command": command}]}]})
            assert every["ok"] is True and every["ran"] is False
            assert every["matched"] == [{"group": 0, "type": "command"}]
        unknown = hook_match("NoSuch", "Read", hooks)
        assert unknown == {"ok": False, "error": "unknown_event", "matched": [], "ran": False}
        bad = hook_match("PreToolUse", "Read", ["nope"])
        assert bad == {"ok": False, "error": "bad_hooks", "matched": [], "ran": False}
        assert started["n"] == 0
    finally:
        subprocess.run = real_run
        os.system = real_system
    print("hook_match selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
