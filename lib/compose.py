"""Offline compose: plan, frame, mold, then one built part per section.

Stdlib only. No network, no publish, no ledger write.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_ATTEMPTS = 9  # first try, then up to 8 retries while sibling modules land
_DEPS = None

# p and li are body text in the checker (18px), even when a part treats them
# as 16px chrome. The page also paints every details with the dark surface,
# which hides a part's own background; transparent lets that background show.
# A one-button part has no gap. A second grounded action cloned beside it
# would sit flush, so adjacent part links keep the renderer hero's 12px.
# The block sits after part styles so equal specificity loses.
_FLOOR = (
    '<style data-sc-compose="type-floor">\n'
    "[data-sc-part] p,[data-sc-part] li,[data-sc-part] span,"
    "[data-sc-part] dd,[data-sc-part] dt,[data-sc-part] blockquote"
    "{font-size:18px}\n"
    "[data-sc-part] details{background-color:transparent}\n"
    "[data-sc-part] a+a{margin-inline-start:12px}\n"
    "</style>\n"
)

_SITE_HEADER = re.compile(
    r'<header\b[^>]*\bclass="[^"]*\bsite-header\b[^"]*"[^>]*>',
    re.IGNORECASE,
)
_FOOTER = re.compile(r"<footer\b[^>]*>", re.IGNORECASE)
_SNIPPETS = ("snippet.html", "template.html")


def _load_modules() -> dict:
    from lib import (
        check,
        copy_pack,
        frames,
        ingest,
        ir,
        lock_file,
        mold_paint,
        offline,
        part_fill,
        part_pick,
        part_swap,
        render,
        structure,
    )

    return {
        "check": check,
        "copy_pack": copy_pack,
        "frames": frames,
        "ingest": ingest,
        "ir": ir,
        "lock_file": lock_file,
        "mold_paint": mold_paint,
        "offline": offline,
        "part_fill": part_fill,
        "part_pick": part_pick,
        "part_swap": part_swap,
        "render": render,
        "structure": structure,
    }


def _deps() -> dict:
    global _DEPS
    if _DEPS is not None:
        return _DEPS
    last = None
    for attempt in range(_ATTEMPTS):
        try:
            _DEPS = _load_modules()
            return _DEPS
        except ImportError as exc:
            last = exc
            _DEPS = None
            if attempt + 1 < _ATTEMPTS:
                time.sleep(20)
    raise ImportError(str(last) if last else "import failed")


def _fail(out: Path, error: str) -> dict:
    return {
        "ok": False,
        "site_dir": str(out),
        "structure": "",
        "part_ids": [],
        "error": error,
    }


def _inside(project: Path, dest: Path) -> bool:
    try:
        dest.resolve().relative_to(project.resolve())
    except (OSError, ValueError):
        return False
    return True


def _guard(lock_file, project: Path, dest: Path) -> None:
    if _inside(project, dest):
        lock_file.assert_unlocked(project, dest)


def _known_ids(raw: dict) -> set[str]:
    pages = raw.get("pages") if isinstance(raw, dict) else None
    if not isinstance(pages, list) or not pages or not isinstance(pages[0], dict):
        return set()
    sections = pages[0].get("sections")
    if not isinstance(sections, list):
        return set()
    return {
        sec.get("id")
        for sec in sections
        if isinstance(sec, dict) and isinstance(sec.get("id"), str) and sec.get("id")
    }


def _drop_dead_links(raw: dict) -> None:
    """Drop hash links the frame removed.

    A hero whose primary target was dropped takes the next section title
    already on the page. That label is not a new sentence.
    """
    ids = _known_ids(raw)
    nav = raw.get("nav") if isinstance(raw, dict) else None
    if isinstance(nav, list):
        kept = []
        for item in nav:
            if not isinstance(item, dict):
                continue
            href = item.get("href")
            if isinstance(href, str) and href.startswith("#") and href[1:] not in ids:
                continue
            kept.append(item)
        raw["nav"] = kept
    pages = raw.get("pages") if isinstance(raw, dict) else None
    if not isinstance(pages, list):
        return
    for page in pages:
        if not isinstance(page, dict):
            continue
        sections = page.get("sections")
        if not isinstance(sections, list):
            continue
        for sec in sections:
            if not isinstance(sec, dict):
                continue
            data = sec.get("data")
            if not isinstance(data, dict):
                continue
            for key in ("primary", "secondary"):
                link = data.get(key)
                if not isinstance(link, dict):
                    continue
                href = link.get("href")
                if isinstance(href, str) and href.startswith("#") and href[1:] not in ids:
                    data[key] = None
            _retarget_hero(sec, sections)


def _link_alive(link) -> bool:
    if not isinstance(link, dict):
        return False
    label = str(link.get("label") or "").strip()
    href = link.get("href")
    return bool(label) and isinstance(href, str) and bool(href.strip())


def _next_titled(sections: list, hero: dict) -> dict | None:
    """First kept section after the hero whose title is already on that section."""
    seen = False
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        if sec is hero:
            seen = True
            continue
        if not seen:
            continue
        data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
        title = str(data.get("title") or "").strip()
        sec_id = sec.get("id")
        if title and isinstance(sec_id, str) and sec_id:
            return sec
    return None


def _retarget_hero(sec: dict, sections: list) -> None:
    """When a frame drops the hero target, point primary at the next titled section.

    The label is that section's title. No new words. A matching secondary is cleared.
    """
    if sec.get("type") != "hero" and sec.get("id") != "hero":
        return
    data = sec.get("data")
    if not isinstance(data, dict) or _link_alive(data.get("primary")):
        return
    follow = _next_titled(sections, sec)
    if follow is None:
        return
    title = str(follow["data"].get("title") or "").strip()
    sec_id = follow.get("id")
    if not title or not isinstance(sec_id, str) or not sec_id:
        return
    href = f"#{sec_id}"
    data["primary"] = {"label": title, "href": href}
    secondary = data.get("secondary")
    if isinstance(secondary, dict) and (
        secondary.get("href") == href or str(secondary.get("label") or "").strip() == title
    ):
        data["secondary"] = None


def _slots(section: dict) -> dict[str, str]:
    data = section.get("data") if isinstance(section, dict) else None
    slots: dict[str, str] = {}
    if not isinstance(data, dict):
        return slots

    def walk(node, key: str) -> None:
        if isinstance(node, str):
            if key and node.strip() and key not in slots:
                slots[key] = node
            return
        if isinstance(node, dict):
            for name, value in node.items():
                walk(value, str(name))
            return
        if isinstance(node, list):
            for value in node:
                walk(value, key)

    walk(data, "")
    return slots


def _read(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return None
    return text if text.strip() else None


def _fragment(part_dir: Path) -> str | None:
    for name in _SNIPPETS:
        text = _read(part_dir / name)
        if text is not None:
            return text.strip()
    return None


def _css(part_dir: Path) -> str | None:
    return _read(part_dir / "part.css")


def _matching_close(html: str, open_end: int, tag: str) -> int | None:
    lower = html.lower()
    tag = tag.lower()
    open_token = "<" + tag
    close_token = "</" + tag
    depth = 1
    i = open_end
    n = len(html)
    while i < n:
        next_open = lower.find(open_token, i)
        next_close = lower.find(close_token, i)
        if next_close < 0:
            return None
        if 0 <= next_open < next_close:
            after = next_open + len(open_token)
            if after < n and (lower[after].isalnum() or lower[after] in "-:"):
                i = after
                continue
            depth += 1
            i = after
            continue
        after = next_close + len(close_token)
        if after < n and (lower[after].isalnum() or lower[after] in "-:"):
            i = after
            continue
        depth -= 1
        if depth == 0:
            return next_close
        i = after
    return None


def _insert_at(html: str, index: int, block: str) -> str:
    if not block:
        return html
    return html[:index] + block + html[index:]


def _select(pick, name: str, override: str, used: set[str], section: dict, copy_text: str, mold, deps) -> tuple[str, str] | None:
    """Pick until an HTML fragment exists. An override is not replaced."""
    forced = bool(override)
    seen: set[str] = set()
    while True:
        picked = pick(name, used, override if forced else "")
        if not picked.get("ok"):
            return None
        catalog_id = str(picked.get("catalog_id") or "")
        if not catalog_id or catalog_id in seen:
            return None
        seen.add(catalog_id)
        used.add(catalog_id)
        part_dir = Path(str(picked.get("part_dir") or ""))
        fragment = _fragment(part_dir)
        css = _css(part_dir)
        if fragment is None or css is None:
            if forced:
                return None
            forced = False
            continue
        if mold is not None:
            css = deps["mold_paint"].paint_css(css, mold)
        fields = deps["part_fill"].section_fields(section, copy_text)
        fragment = deps["part_fill"].bind_fragment(fragment, section, copy_text)
        slots = _slots(section)
        for index, value in enumerate(deps["part_fill"].field_strings(fields)):
            slots[f"sc-bound-{index}"] = value
        fragment = deps["part_fill"].ground_fragment(fragment, slots, copy_text)
        if not deps["part_fill"].has_grounded_markup(fragment):
            # Nothing grounded survived. The renderer already shows this section.
            return catalog_id, ""
        block = deps["part_swap"].wrap_part(catalog_id, css, fragment)
        return catalog_id, block


def _class_tokens(tag_text: str) -> list[str]:
    match = re.search(r'\bclass="([^"]*)"', tag_text, re.IGNORECASE)
    if not match:
        return []
    return match.group(1).split()


def _extract_class_element(html: str, token: str) -> str:
    """The first element whose class list contains token, including its close tag."""
    for match in re.finditer(r"<([A-Za-z][\w:-]*)\b[^>]*>", html):
        if token not in _class_tokens(match.group(0)):
            continue
        close_at = _matching_close(html, match.end(), match.group(1))
        if close_at is None:
            continue
        end = html.find(">", close_at)
        if end < 0:
            continue
        return html[match.start():end + 1]
    return ""


_WRAP = re.compile(r'<div\b[^>]*\bclass="[^"]*\bwrap\b[^"]*"[^>]*>', re.IGNORECASE)


def _replace_section(html: str, sec_id: str, block: str) -> str:
    """Replace one section body with the part. Keep the wrap and any hero-visual."""
    pattern = re.compile(
        r'<section\b[^>]*\bid="' + re.escape(sec_id) + r'"[^>]*>',
        re.IGNORECASE,
    )
    found = pattern.search(html)
    if not found:
        return html
    close_at = _matching_close(html, found.end(), "section")
    if close_at is None:
        return _insert_at(html, found.end(), block)
    inner = html[found.end():close_at]
    visual = _extract_class_element(inner, "hero-visual")
    payload = visual + block
    wrap = _WRAP.search(inner)
    if wrap is not None and not inner[:wrap.start()].strip():
        wrap_close = _matching_close(inner, wrap.end(), "div")
        if wrap_close is not None:
            end = inner.find(">", wrap_close)
            if end >= 0:
                payload = inner[:wrap.end()] + visual + block + inner[wrap_close:end + 1]
    return html[:found.end()] + payload + html[close_at:]


def _apply_page(html: str, header: str, footer: str, sections: list[tuple[str, str]], swap) -> str:
    # Append inside site-header so the renderer's nav stays the first nav.
    match = _SITE_HEADER.search(html)
    if match and header:
        close_at = _matching_close(html, match.end(), "header")
        if close_at is not None:
            html = _insert_at(html, close_at, header)
    match = _FOOTER.search(html)
    if match and footer:
        html = _insert_at(html, match.end(), footer)
    for sec_id, block in sections:
        if not sec_id or not block:
            continue
        html = _replace_section(html, sec_id, block)
    if header or footer or any(block for _sec, block in sections):
        body_at = html.lower().rfind("</body>")
        if body_at >= 0:
            html = _insert_at(html, body_at, _FLOOR)
    return swap.bind_hashes(html)


def _load_mold(mold_id: str) -> dict:
    token = str(mold_id or "").strip()
    if not token or Path(token).name != token or ".." in token:
        raise ValueError(f"unknown mold {mold_id}")
    path = _ROOT / "library" / "molds" / f"{token}.json"
    if not path.is_file():
        raise ValueError(f"unknown mold {token}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"unknown mold {token}")
    return data


def compose_project(
    project: Path,
    out: Path,
    frame_id: str = "",
    mold_id: str = "",
    part_overrides: dict | None = None,
    plan_only: bool = False,
    accepted: Path | None = None,
) -> dict:
    """Build an offline noindex site and insert header, footer, and section parts.

    ``plan_only`` writes ``structure.json`` and does not write HTML.
    ``accepted`` is a structure file that may only drop or reorder the fresh
    plan. A new section refuses the paint and writes nothing.
    """
    project = Path(project)
    out = Path(out)
    if accepted is not None and plan_only:
        return _fail(out, "plan does not read an accepted structure")
    try:
        deps = _deps()
    except ImportError as exc:
        return _fail(out, f"import failed: {exc}")

    try:
        _guard(deps["lock_file"], project, out)
        copy = deps["ingest"].load_project(project)
        raw = deps["offline"].plan_offline(copy, {"brief": copy.brief})
        frame_token = str(frame_id or "").strip()
        if frame_token:
            frame = deps["frames"].load_frame(frame_token)
            pages = raw.get("pages") if isinstance(raw, dict) else None
            if isinstance(pages, list) and pages and isinstance(pages[0], dict):
                sections = pages[0].get("sections")
                if not isinstance(sections, list):
                    sections = []
                pages[0]["sections"] = deps["frames"].apply_frame(sections, frame)
        mold = None
        mold_token = str(mold_id or "").strip()
        if mold_token:
            mold = _load_mold(mold_token)
            theme = raw.get("theme") if isinstance(raw, dict) else None
            if not isinstance(theme, dict):
                theme = {}
                raw["theme"] = theme
            palette = mold.get("palette")
            template = mold.get("template")
            if isinstance(palette, str) and palette.strip():
                theme["accent"] = palette.strip()
            if isinstance(template, str) and template.strip():
                theme["template"] = template.strip()
        if frame_token:
            _drop_dead_links(raw)
        site = deps["ir"].normalize_site(raw, {"brief": getattr(copy, "brief", "")})
        from lib.seo_pack import descriptions_by_stem
        stems = descriptions_by_stem(project)
        site_pages = [page for page in (site.get("pages") or []) if isinstance(page, dict)]
        for page in site_pages:
            stem = str(page.get("slug") or "").lower()
            if stem in stems:
                page["description"] = stems[stem]
            elif len(stems) == 1 and len(site_pages) == 1:
                page["description"] = next(iter(stems.values()))
        copy_text = deps["copy_pack"].project_copy_text(project)
        overrides = part_overrides if isinstance(part_overrides, dict) else {}

        def override_for(key: str) -> str:
            value = overrides.get(key)
            return value.strip() if isinstance(value, str) else ""

        used: set[str] = set()
        picks: dict[str, str] = {}
        part_ids: list[str] = []
        header_block = ""
        footer_block = ""
        section_blocks: list[tuple[str, str]] = []

        header = _select(
            deps["part_pick"].pick_chrome,
            "header",
            override_for("header"),
            used,
            {"id": "header", "type": "header", "data": {}},
            copy_text,
            mold,
            deps,
        )
        if header:
            part_ids.append(header[0])
            header_block = header[1]
        footer = _select(
            deps["part_pick"].pick_chrome,
            "footer",
            override_for("footer"),
            used,
            {"id": "footer", "type": "footer", "data": {}},
            copy_text,
            mold,
            deps,
        )
        if footer:
            part_ids.append(footer[0])
            footer_block = footer[1]

        for page in site.get("pages") or []:
            if not isinstance(page, dict):
                continue
            for sec in page.get("sections") or []:
                if not isinstance(sec, dict):
                    continue
                sec_id = sec.get("id") if isinstance(sec.get("id"), str) else ""
                sec_type = sec.get("type") if isinstance(sec.get("type"), str) else ""
                if not sec_type:
                    continue
                chosen = _select(
                    deps["part_pick"].pick_part,
                    sec_type,
                    override_for(sec_id),
                    used,
                    sec,
                    copy_text,
                    mold,
                    deps,
                )
                if chosen is None:
                    continue
                picks[sec_id] = chosen[0]
                if chosen[0] not in part_ids:
                    part_ids.append(chosen[0])
                section_blocks.append((sec_id, chosen[1]))

        structure = deps["structure"].make_structure(site, frame_token, mold_token, picks)
        if accepted is not None:
            try:
                loaded = deps["structure"].load_structure(Path(accepted))
            except (OSError, ValueError) as exc:
                return _fail(out, "accepted structure: " + str(exc))
            kept, edit_errors = deps["structure"].subset_edit(structure, loaded)
            if kept is None or edit_errors:
                return _fail(out, "; ".join(edit_errors) or "structure refused")
            deps["structure"].apply_subset(site, kept)
            keep_ids: list[str] = []
            for kept_page in kept.get("pages") or []:
                if not isinstance(kept_page, dict):
                    continue
                for sec in kept_page.get("sections") or []:
                    if isinstance(sec, dict) and isinstance(sec.get("id"), str):
                        keep_ids.append(sec["id"])
            blocks = {sid: html for sid, html in section_blocks}
            section_blocks = [(sid, blocks[sid]) for sid in keep_ids if sid in blocks]
            live_ids: set[str] = set()
            if header:
                live_ids.add(header[0])
            if footer:
                live_ids.add(footer[0])
            for sid, _html in section_blocks:
                pid = picks.get(sid)
                if isinstance(pid, str) and pid:
                    live_ids.add(pid)
            part_ids = [pid for pid in part_ids if pid in live_ids]
            structure = kept
        pages = [
            {"file": item["file"], "html": item["html"]}
            for item in deps["render"].assemble(site, noindex=True)
        ]
        for item in pages:
            name = str(item["file"])
            if not name.lower().endswith(".html"):
                continue
            item["html"] = _apply_page(
                item["html"], header_block, footer_block, section_blocks, deps["part_swap"]
            )
        structure_path = out / "structure.json"
        destinations = [out, structure_path, out / "site.json", out / "report.json"]
        destinations.extend(out / str(item["file"]) for item in pages)
        for dest in destinations:
            _guard(deps["lock_file"], project, dest)
    except (Exception, SystemExit) as exc:
        return _fail(out, str(exc) or exc.__class__.__name__)

    try:
        out.mkdir(parents=True, exist_ok=True)
        if plan_only:
            deps["structure"].save_structure(structure_path, structure)
            from lib.plan_gate import plan_only_result
            return plan_only_result(out, structure_path, part_ids)
        for item in pages:
            (out / str(item["file"])).write_text(item["html"], encoding="utf-8", newline="\n")
        (out / "site.json").write_text(
            json.dumps(site, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        deps["structure"].save_structure(structure_path, structure)
        report = {
            "generator": "spidercaster/0.1",
            "mode": "offline",
            "brief": "",
            "provider": None,
            "model": None,
            "noindex": True,
            "files": [str(item["file"]) for item in pages],
            "warnings": [],
            "tokens": {"in_tokens": 0, "out_tokens": 0, "est_cost_usd": 0},
            "attempts": [],
        }
        (out / "report.json").write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        from lib.seo_pack import write_pack
        write_pack(out, indexable=False)
    except (Exception, SystemExit) as exc:
        return _fail(out, str(exc) or exc.__class__.__name__)

    return {
        "ok": True,
        "site_dir": str(out),
        "structure": str(structure_path),
        "part_ids": part_ids,
        "error": "",
    }
