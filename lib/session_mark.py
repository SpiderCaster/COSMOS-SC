"""Append one local session line. Never restore, publish, or rewrite."""
from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from lib.crew import ROLES

_STATUSES = ("PASS", "FAIL", "SKIP")
_BY_ID = {role["id"]: role for role in ROLES}


def _result(ok: bool, error: str | None, path: str | None, seq: int | None, seat, hand, status) -> dict:
    return {
        "ok": ok,
        "error": error,
        "path": path,
        "seq": seq,
        "seat": seat,
        "hand": hand,
        "status": status,
    }


def _fail(seat, hand, status, error: str) -> dict:
    return _result(False, error, None, None, seat, hand, status)


def _has_dotdot(value: object) -> bool:
    text = str(value).replace("\\", "/")
    if any(part == ".." for part in text.split("/")):
        return True
    return ".." in Path(text).parts


def session_mark(out, root, seat, hand, status, detail, restore=None) -> dict:
    """Append one JSON line to out/session.jsonl. Fail closed. Do not create out."""
    if restore is not None:
        return _fail(seat, hand, status, "restore")
    try:
        role = _BY_ID.get(seat)
    except TypeError:
        role = None
    if role is None:
        return _fail(seat, hand, status, "seat")
    hands = role.get("hands")
    if not isinstance(hand, str) or not isinstance(hands, list) or hand not in hands:
        return _fail(seat, hand, status, "hand")
    if status not in _STATUSES:
        return _fail(seat, hand, status, "status")
    if not isinstance(detail, str):
        return _fail(seat, hand, status, "url")
    folded = detail.lower()
    if "http://" in folded or "https://" in folded:
        return _fail(seat, hand, status, "url")
    if not isinstance(out, (str, Path)) or not isinstance(root, (str, Path)):
        return _fail(seat, hand, status, "escape")
    if out == "" or _has_dotdot(out):
        return _fail(seat, hand, status, "escape")
    out_path = Path(out)
    root_path = Path(root)
    try:
        if not out_path.exists():
            return _fail(seat, hand, status, "missing")
        out_resolved = out_path.resolve()
        root_resolved = root_path.resolve()
        out_resolved.relative_to(root_resolved)
    except (OSError, ValueError):
        return _fail(seat, hand, status, "escape")
    if not out_resolved.is_dir() or not root_resolved.is_dir():
        return _fail(seat, hand, status, "escape")
    log = out_resolved / "session.jsonl"
    try:
        if log.is_symlink():
            target = log.resolve()
            target.relative_to(root_resolved)
            if not target.is_file():
                return _fail(seat, hand, status, "escape")
        elif log.exists() and not log.is_file():
            return _fail(seat, hand, status, "escape")
        else:
            log.relative_to(root_resolved)
    except (OSError, ValueError):
        return _fail(seat, hand, status, "escape")
    prior = 0
    if log.is_file():
        prior = len(log.read_text(encoding="utf-8").splitlines())
    seq = prior + 1
    record = {
        "seq": seq,
        "seat": seat,
        "hand": hand,
        "status": status,
        "detail": detail,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    with log.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
    seq = len(log.read_text(encoding="utf-8").splitlines())
    return _result(True, None, str(log), seq, seat, hand, status)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        out = root / "site"
        out.mkdir()
        first = session_mark(out, root, "deployer", "ticket_write", "PASS", "one")
        assert first["ok"] is True and first["seq"] == 1
        first_text = (out / "session.jsonl").read_text(encoding="utf-8")
        second = session_mark(out, root, "deployer", "ticket_write", "PASS", "two")
        log = out / "session.jsonl"
        text = log.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert text.startswith(first_text)
        assert len(lines) == 2
        assert second["seq"] == 2
        assert second["ok"] is True
        assert json.loads(lines[0])["status"] == "PASS"
        assert json.loads(lines[1])["hand"] == "ticket_write"
        denied = session_mark(
            out,
            root,
            "deployer",
            "ticket_write",
            "PASS",
            "see https://example.com",
        )
        assert denied["ok"] is False
        assert denied["error"] == "url"
        assert log.read_text(encoding="utf-8") == text
        assert len(log.read_text(encoding="utf-8").splitlines()) == 2
    print("session_mark selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
