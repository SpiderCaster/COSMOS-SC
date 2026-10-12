"""Append or replace one built part on a static page. Stdlib only. Does not publish.

The page keeps its noindex marker, site header, and favicon link. With
``replace`` false, the part is wrapped and inserted immediately before
``</body>``. With ``replace`` true, the existing part is swapped. A mold
repaints the part CSS before that. A project lock can refuse the write.
"""
from __future__ import annotations

import re
from pathlib import Path

from lib.lock_file import LockError, assert_unlocked
from lib.mold_paint import paint_css
from lib.part_swap import PartSwapError, bind_hashes, replace_part, wrap_part
from lib.tools_index import index_rows

_SNIPPETS = ("snippet.html", "template.html")


class ToolsApplyError(Exception):
    pass


def fragment_file(part_dir: Path) -> Path | None:
    """Prefer a non-empty ``snippet.html``, then ``template.html``."""
    folder = Path(part_dir)
    for name in _SNIPPETS:
        path = folder / name
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError:
            continue
        if text.strip():
            return path
    return None


def _kept(source: str, written: str) -> None:
    if source.lower().count("noindex") > written.lower().count("noindex"):
        raise ToolsApplyError("apply removed noindex")
    for needle, label in (('rel="icon"', "favicon link"), ("rel='icon'", "favicon link"), ("site-header", "site header")):
        if source.count(needle) > written.count(needle):
            raise ToolsApplyError(f"apply removed the {label}")
    if re.search(r"<header\b", source, re.IGNORECASE) and not re.search(r"<header\b", written, re.IGNORECASE):
        raise ToolsApplyError("apply removed the site header")


def _refuse_locked(project: Path, out: Path) -> None:
    try:
        assert_unlocked(Path(project), out)
    except LockError as exc:
        raise ToolsApplyError(str(exc)) from exc


def apply_part(
    catalog_id: str,
    page: Path,
    out: Path,
    rows: list[dict] | None = None,
    *,
    replace: bool = False,
    mold: dict | None = None,
    project: Path | None = None,
) -> dict:
    """Write ``out`` with the built part for ``catalog_id`` applied to ``page``."""
    catalog_id = str(catalog_id or "").strip()
    if not catalog_id:
        raise ToolsApplyError("missing catalog row: (empty id)")
    page = Path(page)
    out = Path(out)
    if project is not None:
        _refuse_locked(project, out)
    if not page.is_file():
        raise ToolsApplyError(f"page missing: {page}")
    listed = rows if rows is not None else index_rows()
    match = next((row for row in listed if row.get("catalog_id") == catalog_id), None)
    if match is None or match.get("status") != "built" or not match.get("part_dir"):
        raise ToolsApplyError(f"missing catalog row: {catalog_id}")
    part_dir = Path(match["part_dir"])
    frag_path = fragment_file(part_dir)
    if frag_path is None:
        raise ToolsApplyError(f"part has no snippet: {part_dir}")
    css_path = part_dir / "part.css"
    try:
        css = css_path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ToolsApplyError(f"part has no part.css: {part_dir}") from exc
    if not css.strip():
        raise ToolsApplyError(f"part has no part.css: {part_dir}")
    try:
        html = page.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ToolsApplyError(f"cannot read {page}: {exc}") from exc
    try:
        fragment = frag_path.read_text(encoding="utf-8-sig").strip()
    except OSError as exc:
        raise ToolsApplyError(f"part has no snippet: {part_dir}") from exc
    if mold is not None:
        css = paint_css(css, mold)
    if replace:
        try:
            written = replace_part(html, catalog_id, css, fragment)
        except PartSwapError as exc:
            raise ToolsApplyError("part not on page") from exc
    else:
        body_at = html.lower().rfind("</body>")
        if body_at < 0:
            raise ToolsApplyError(f"page has no </body>: {page}")
        block = wrap_part(catalog_id, css, fragment)
        if not block.endswith("\n"):
            block += "\n"
        written = html[:body_at] + block + html[body_at:]
    written = bind_hashes(written)
    _kept(html, written)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(written, encoding="utf-8", newline="\n")
    return {
        "catalog_id": catalog_id,
        "part_dir": str(part_dir),
        "snippet": frag_path.name,
        "out": str(out),
    }
