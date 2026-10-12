"""Read one SKILL.md. Flat frontmatter only. Never runs a command."""

from __future__ import annotations

import hashlib
from pathlib import Path

_KEYS = (
    "name",
    "description",
    "allowed_tools",
    "disallowed_tools",
    "user_invocable",
    "disable_model_invocation",
    "context",
)
_LIST_KEYS = {"allowed_tools", "disallowed_tools"}
_ALIASES = {
    "allowed-tools": "allowed_tools",
    "disallowed-tools": "disallowed_tools",
}


class _FrontError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code


def _fail(error: str) -> dict:
    out = {key: None for key in ("ok", "error", *_KEYS, "body_sha256")}
    out["ok"] = False
    out["error"] = error
    out["allowed_tools"] = []
    out["disallowed_tools"] = []
    return out


def _inside(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
    except ValueError:
        return False
    return True


def _scalar(raw: str):
    text = raw.strip()
    if text in {">", ">-", "|", "|-"}:
        raise _FrontError("block")
    if text.startswith("!") or "!`" in text:
        raise _FrontError("unsupported_value")
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_unquote(part.strip()) for part in inner.split(",") if part.strip()]
    if text.startswith("{") and text.endswith("}"):
        raise _FrontError("unsupported_value")
    low = text.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in {"null", "~"}:
        return None
    return _unquote(text)


def _unquote(text: str) -> str:
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        return text[1:-1]
    return text


def _parse_front(lines: list[str]) -> dict:
    data: dict = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith((" ", "\t")):
            raise _FrontError("bad_frontmatter")
        if ":" not in line:
            raise _FrontError("bad_frontmatter")
        key, _, raw = line.partition(":")
        key = _ALIASES.get(key.strip(), key.strip())
        if not key or " " in key:
            raise _FrontError("bad_frontmatter")
        raw = raw.strip()
        if raw in {">", ">-", "|", "|-"}:
            folded = raw.startswith(">")
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            text = " ".join(part for part in block if part) if folded else "\n".join(block).strip()
            data[key] = text
            continue
        if raw == "":
            items: list[str] = []
            i += 1
            while i < len(lines) and lines[i].startswith((" ", "\t")):
                item = lines[i].strip()
                if item.startswith("- "):
                    value = _scalar(item[2:])
                    if isinstance(value, (dict, list)):
                        raise _FrontError("unsupported_value")
                    items.append("" if value is None else str(value))
                elif ":" in item:
                    raise _FrontError("unsupported_value")
                else:
                    raise _FrontError("bad_frontmatter")
                i += 1
            data[key] = items
            continue
        try:
            data[key] = _scalar(raw)
        except _FrontError as exc:
            if exc.code == "unsupported_value":
                raise
            raise _FrontError("bad_frontmatter") from exc
        i += 1
    return data


def skill_read(root: Path | str, rel: str) -> dict:
    base = Path(root)
    text = str(rel or "")
    parts = text.replace("\\", "/").split("/")
    if not text or text.startswith(("/", "\\")) or Path(text).is_absolute() or ".." in parts:
        return _fail("escape")
    try:
        root_res = base.resolve()
    except OSError:
        return _fail("missing")
    target = base.joinpath(*parts)
    if target.is_symlink():
        try:
            linked = target.resolve()
        except OSError:
            return _fail("escape")
        if not _inside(root_res, linked):
            return _fail("escape")
        target = linked
    else:
        try:
            if not _inside(root_res, target.resolve()):
                return _fail("escape")
        except OSError:
            return _fail("missing")
    if not target.exists():
        return _fail("missing")
    if not target.is_file():
        return _fail("not_file")
    try:
        raw = target.read_bytes()
    except OSError:
        return _fail("missing")
    try:
        text_body = raw.decode("utf-8")
    except UnicodeError:
        return _fail("bad_frontmatter")
    body = raw
    meta: dict = {}
    if text_body.startswith("---"):
        lines = text_body.splitlines()
        end = None
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                end = idx
                break
        if end is None:
            return _fail("bad_frontmatter")
        try:
            meta = _parse_front(lines[1:end])
        except _FrontError as exc:
            code = "unsupported_value" if exc.code == "unsupported_value" else "bad_frontmatter"
            return _fail(code)
        rest = "\n".join(lines[end + 1:])
        if text_body.endswith("\n"):
            rest += "\n"
        body = rest.encode("utf-8")
    out = _fail("")
    out["ok"] = True
    out["error"] = None
    for key in _KEYS:
        if key in _LIST_KEYS:
            value = meta.get(key, [])
            if isinstance(value, str):
                value = [part.strip() for part in value.split(",") if part.strip()]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                return _fail("unsupported_value")
            out[key] = value
        elif key in meta:
            value = meta[key]
            if isinstance(value, (dict, list)):
                return _fail("unsupported_value")
            out[key] = value
    out["body_sha256"] = hashlib.sha256(body).hexdigest()
    return out


def _selftest() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skill = root / "SKILL.md"
        skill.write_text(
            "---\nname: demo\nallowed_tools:\n  - Read\n  - Grep\n---\nHello\n",
            encoding="utf-8",
        )
        got = skill_read(root, "SKILL.md")
        if not got["ok"] or got["name"] != "demo" or got["allowed_tools"] != ["Read", "Grep"]:
            raise SystemExit(f"flat read failed: {got}")
        if got["body_sha256"] != hashlib.sha256(b"Hello\n").hexdigest():
            raise SystemExit("body hash mismatch")
        escaped = skill_read(root, "..\\x")
        if escaped["error"] != "escape" or escaped["allowed_tools"] != []:
            raise SystemExit(f"escape failed: {escaped}")
        nested = root / "NEST.md"
        nested.write_text("---\nname:\n  inner: 1\n---\n", encoding="utf-8")
        bad = skill_read(root, "NEST.md")
        if bad["ok"] or bad["error"] not in {"bad_frontmatter", "unsupported_value"}:
            raise SystemExit(f"nested map was accepted: {bad}")
    print("skill_read selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
