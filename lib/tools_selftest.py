"""Prove the catalog index and one part apply against the real fleet tree.

Also proves replace swaps css, a mold palette is written, and a lock refuses
the write. Run from the repo root: ``python lib/tools_selftest.py``.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.tools_apply import ToolsApplyError, apply_part, fragment_file
from lib.tools_index import PARTS, ToolsIndexError, index_rows

PAGE = ROOT / "sites" / "demo-local" / "index.html"
EXPECTED = 208
_SENTINEL = "/*sc-old-css*/"
_MOLD = {"palette": "#2a6f8f", "type_lead": "sans"}


def _fail(msg: str) -> int:
    print("tools selftest FAIL: " + msg)
    return 1


def _dirs(parent: Path) -> list[Path]:
    if not parent.is_dir():
        return []
    return sorted(
        (p for p in parent.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))),
        key=lambda p: p.name.lower(),
    )


def _marker(snippet: str, source: str) -> str:
    for group in re.findall(r'class\s*=\s*"([^"]+)"', snippet):
        for token in group.split():
            if token and token not in source:
                return token
    for group in re.findall(r"class\s*=\s*'([^']+)'", snippet):
        for token in group.split():
            if token and token not in source:
                return token
    for attr in re.findall(r"\bdata-sc-[A-Za-z0-9_-]+", snippet):
        if attr not in source:
            return attr
    return ""


def _pick(rows: list[dict]) -> tuple[dict, Path] | None:
    built = [row for row in rows if row.get("status") == "built" and row.get("part_dir")]
    popups: list[tuple[dict, Path]] = []
    for row in built:
        part = Path(row["part_dir"])
        if part.parent.name != "popups_callouts":
            continue
        frag = fragment_file(part)
        if frag is not None:
            popups.append((row, frag))
    if popups:
        popups.sort(key=lambda item: str(item[0]["part_dir"]).lower())
        return popups[0]
    print("tools selftest: no popups_callouts part has snippet.html or template.html")
    by_dir = {Path(row["part_dir"]): row for row in built}
    for folder in _dirs(PARTS / "headers"):
        frag = fragment_file(folder)
        if frag is None:
            continue
        row = by_dir.get(folder)
        if row is None:
            continue
        return row, frag
    return None


def _css_needle(part_dir: Path) -> str:
    css = (part_dir / "part.css").read_text(encoding="utf-8-sig")
    for line in css.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("/*") or stripped.startswith("*"):
            continue
        if "</" in stripped.lower():
            continue
        return stripped
    return ""


def _mark_style(html: str, catalog_id: str) -> str:
    token = f'data-sc-tool="{catalog_id}"'
    at = html.find(token)
    if at < 0:
        return ""
    end = html.find(">", at)
    if end < 0:
        return ""
    return html[: end + 1] + _SENTINEL + html[end + 1 :]


def _style_text(html: str, catalog_id: str) -> str:
    token = f'data-sc-tool="{catalog_id}"'
    at = html.find(token)
    if at < 0:
        return ""
    start = html.find(">", at)
    if start < 0:
        return ""
    end = html.lower().find("</style>", start)
    if end < 0:
        return ""
    return html[start + 1 : end]


def _mold_row(rows: list[dict]) -> dict | None:
    for row in rows:
        if row.get("status") != "built" or not row.get("part_dir"):
            continue
        part = Path(row["part_dir"])
        if fragment_file(part) is None:
            continue
        css_path = part / "part.css"
        if not css_path.is_file():
            continue
        css = css_path.read_text(encoding="utf-8-sig")
        if "#14213d" in css.lower():
            return row
    return None


def main() -> int:
    try:
        rows = index_rows()
    except ToolsIndexError as exc:
        return _fail(str(exc))
    if len(rows) != EXPECTED:
        return _fail(f"row count is {len(rows)}, need {EXPECTED}")
    if not PAGE.is_file():
        return _fail(f"page missing: {PAGE}")
    picked = _pick(rows)
    if picked is None:
        return _fail("no popup or header part has a static snippet")
    row, frag = picked
    source = PAGE.read_text(encoding="utf-8-sig")
    snippet = frag.read_text(encoding="utf-8-sig")
    marker = _marker(snippet, source)
    if not marker:
        return _fail(f"snippet has no class or marker that is new to the page: {frag}")
    mold_row = _mold_row(rows)
    if mold_row is None:
        return _fail("no built part css contains #14213d")
    tmp = Path(tempfile.mkdtemp(prefix="sc-tools-"))
    try:
        page = tmp / "index.html"
        out = tmp / "applied.html"
        shutil.copyfile(PAGE, page)
        try:
            info = apply_part(row["catalog_id"], page, out, rows=rows)
        except ToolsApplyError as exc:
            return _fail(str(exc))
        text = out.read_text(encoding="utf-8")
        if marker not in text:
            return _fail(f"output is missing snippet marker {marker}")
        if source.lower().count("noindex") > text.lower().count("noindex"):
            return _fail("output lost noindex")
        if source.count('rel="icon"') > text.count('rel="icon"'):
            return _fail("output lost the favicon link")
        if source.count("site-header") > text.count("site-header"):
            return _fail("output lost the site header")
        catalog_id = row["catalog_id"]
        if f'data-sc-tool="{catalog_id}"' not in text:
            return _fail("output has no part style tag")
        if f'data-sc-part="{catalog_id}"' not in text:
            return _fail("output has no part div")

        marked = _mark_style(text, catalog_id)
        if _SENTINEL not in marked:
            return _fail("could not mark part css for replace")
        marked_page = tmp / "marked.html"
        replaced_out = tmp / "replaced.html"
        marked_page.write_text(marked, encoding="utf-8", newline="\n")
        try:
            apply_part(catalog_id, marked_page, replaced_out, rows=rows, replace=True)
        except ToolsApplyError as exc:
            return _fail(f"replace failed: {exc}")
        replaced = replaced_out.read_text(encoding="utf-8")
        if _SENTINEL in replaced:
            return _fail("replace left the old css in place")
        if replaced.count(f'data-sc-tool="{catalog_id}"') != 1:
            return _fail("replace did not keep a single part style")
        if replaced.count(f'data-sc-part="{catalog_id}"') != 1:
            return _fail("replace did not keep a single part div")
        needle = _css_needle(Path(row["part_dir"]))
        if not needle or needle not in replaced:
            return _fail("replace did not write the part css")
        if marker not in replaced:
            return _fail("replace dropped the snippet marker")
        if source.lower().count("noindex") > replaced.lower().count("noindex"):
            return _fail("replace output lost noindex")

        mold_page = tmp / "mold-page.html"
        mold_out = tmp / "molded.html"
        shutil.copyfile(PAGE, mold_page)
        try:
            apply_part(mold_row["catalog_id"], mold_page, mold_out, rows=rows, mold=_MOLD)
        except ToolsApplyError as exc:
            return _fail(f"mold apply failed: {exc}")
        molded = mold_out.read_text(encoding="utf-8")
        style = _style_text(molded, mold_row["catalog_id"])
        if "#2a6f8f" not in style:
            return _fail("mold palette #2a6f8f missing from written style")
        if "#14213d" in style.lower():
            return _fail("mold left #14213d in the part style")

        project = tmp / "locked-project"
        project.mkdir()
        locked_page = project / "page.html"
        locked_out = project / "applied.html"
        shutil.copyfile(PAGE, locked_page)
        (project / "lock.txt").write_text("applied.html\n", encoding="utf-8", newline="\n")
        try:
            apply_part(catalog_id, locked_page, locked_out, rows=rows, project=project)
        except ToolsApplyError as exc:
            if "locked" not in str(exc).lower():
                return _fail(f"locked project raised an unexpected error: {exc}")
        else:
            return _fail("locked project did not refuse the write")
        if locked_out.exists():
            return _fail("locked project still wrote the page")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(
        f"tools selftest ok ({len(rows)} rows, applied {info['catalog_id']} "
        f"via {info['snippet']}, marker {marker})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
