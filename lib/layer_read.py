"""Read the first page layer list from out/site.json. Never writes."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from lib.ir import SECTION_TYPES


def _fail(error: str) -> dict:
    return {"ok": False, "error": error, "layers": [], "page": ""}


def _dotdot(path: Path) -> bool:
    return any(part == ".." for part in path.parts)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def layer_read(out, root, write=None) -> dict:
    """Return {ok, error, layers, page} for the first page. Read only."""
    if write is not None:
        return _fail("write is not allowed")
    try:
        out_path = Path(out)
        root_path = Path(root)
    except TypeError:
        return _fail("out escapes root")
    if _dotdot(out_path) or _dotdot(root_path):
        return _fail("out contains ..")
    try:
        root_resolved = root_path.resolve()
        placed = out_path if out_path.is_absolute() else root_resolved / out_path
        if _dotdot(placed):
            return _fail("out contains ..")
        resolved = placed.resolve()
    except OSError:
        return _fail("out escapes root")
    if not _inside(resolved, root_resolved):
        return _fail("out escapes root")
    site_path = resolved / "site.json"
    try:
        site_resolved = site_path.resolve()
    except OSError:
        return _fail("out escapes root")
    if not _inside(site_resolved, root_resolved):
        return _fail("out escapes root")
    if not site_path.is_file():
        return _fail("site.json missing")
    try:
        data = json.loads(site_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _fail("site.json is not JSON")
    if not isinstance(data, dict):
        return _fail("site.json is not JSON")
    pages = data.get("pages")
    if pages is None:
        return {"ok": True, "error": "", "layers": [], "page": ""}
    if not isinstance(pages, list):
        return _fail("site.json is not JSON")
    if not pages or not isinstance(pages[0], dict):
        if pages and not isinstance(pages[0], dict):
            return _fail("site.json is not JSON")
        return {"ok": True, "error": "", "layers": [], "page": ""}
    first = pages[0]
    slug = first.get("slug")
    page = slug if isinstance(slug, str) else ""
    sections = first.get("sections")
    if sections is None:
        return {"ok": True, "error": "", "layers": [], "page": page}
    if not isinstance(sections, list):
        return _fail("site.json is not JSON")
    allowed = set(SECTION_TYPES)
    layers = []
    for index, section in enumerate(sections):
        if not isinstance(section, dict):
            return _fail("section type is not in SECTION_TYPES")
        kind = section.get("type")
        if kind not in allowed:
            return _fail("section type is not in SECTION_TYPES")
        sec_id = section.get("id")
        layers.append({
            "index": index,
            "id": sec_id if isinstance(sec_id, str) else "",
            "type": kind,
        })
    return {"ok": True, "error": "", "layers": layers, "page": page}


def main() -> int:
    assert "hero" in SECTION_TYPES
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        out = root / "built"
        out.mkdir()
        doc = {
            "pages": [
                {
                    "slug": "index",
                    "sections": [
                        {"id": "hero", "type": "hero"},
                    ],
                }
            ]
        }
        site_path = out / "site.json"
        site_path.write_text(json.dumps(doc), encoding="utf-8")
        before = site_path.read_bytes()
        got = layer_read(out, root)
        assert got["ok"] is True
        assert got["error"] == ""
        assert got["page"] == "index"
        assert got["layers"] == [{"index": 0, "id": "hero", "type": "hero"}]
        assert site_path.read_bytes() == before
        denied = layer_read(out, root, write=True)
        assert denied["ok"] is False
        assert denied["layers"] == []
        assert denied["page"] == ""
        assert site_path.read_bytes() == before
        escaped = layer_read(root / ".." / "outside", root)
        assert escaped["ok"] is False
        missing = layer_read(root, root)
        assert missing["ok"] is False
    print("layer_read selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
