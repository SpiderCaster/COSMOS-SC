"""Seat hands. Each returns status, detail, and data. None of them publish."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from pathlib import Path

from lib import check as check_mod
from lib import frames as frames_mod
from lib import ingest
from lib import ir as ir_mod
from lib import offline as offline_mod
from lib import render as render_mod
from lib.frames import FrameError
from lib.library import Library, LibraryError

_VAULT = r"V:\streams\webdev\vendor-vault"
_MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
_IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
_HERO_EXTS = (".png", ".jpg", ".jpeg", ".webp")
_COPY_TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
_SCRATCH = ("palette", "type_lead", "nav", "template")


def _ret(status: str, detail: str, data: dict | None = None) -> dict:
    return {"status": status, "detail": detail, "data": data or {}}


def _library(ctx: dict) -> Library:
    pkg = ctx.get("package_library")
    if not pkg:
        raise LibraryError("package_library is required")
    vault = ctx.get("vault") or os.environ.get("SPIDERCASTER_VAULT") or _VAULT
    return Library(Path(pkg), Path(vault))


def _load_copy(ctx: dict):
    project = str(ctx.get("project") or "")
    if not project:
        raise SystemExit("project is required")
    if ctx.get("copy") is not None and ctx.get("copy_project") == project:
        return ctx["copy"]
    copy = ingest.load_project(Path(project))
    ctx["copy"] = copy
    ctx["copy_project"] = project
    return copy


def _mold(ctx: dict) -> dict | None:
    mold = ctx.get("mold")
    if isinstance(mold, dict) and mold.get("id"):
        return mold
    mold_id = str(ctx.get("mold_id") or "").strip()
    if not mold_id:
        return None
    mold = _library(ctx).load_mold(mold_id)
    ctx["mold"] = mold
    ctx["mold_id"] = mold["id"]
    return mold


def _remember_ir(ctx: dict, site_ir: dict) -> None:
    ctx["site_ir"] = site_ir
    data = ctx.get("data")
    if not isinstance(data, dict):
        data = {}
        ctx["data"] = data
    data["site_ir"] = site_ir


def _stored_ir(ctx: dict) -> dict | None:
    data = ctx.get("data")
    if isinstance(data, dict) and isinstance(data.get("site_ir"), dict):
        return data["site_ir"]
    if isinstance(ctx.get("site_ir"), dict):
        return ctx["site_ir"]
    return None


def _anchor_ok(href: str, kept: set[str]) -> bool:
    if not str(href).startswith("#"):
        return True
    frag = str(href)[1:]
    return not frag or frag in kept


def _repair_frame_links(raw: dict, sections: list) -> None:
    """Drop anchors the frame removed. Do not add a section or new copy."""
    kept = {str(sec.get("id")) for sec in sections if isinstance(sec, dict) and sec.get("id")}
    rest = [
        str(sec.get("id")) for sec in sections
        if isinstance(sec, dict) and sec.get("id") and sec.get("type") not in ("hero", "cta")
    ]
    contact = next(
        (str(sec["id"]) for sec in sections if isinstance(sec, dict) and sec.get("type") == "contact" and sec.get("id")),
        "",
    )
    fallback = {"primary": rest[0] if rest else "", "secondary": contact or (rest[0] if rest else "")}
    for sec in sections:
        data = sec.get("data") if isinstance(sec, dict) else None
        if not isinstance(data, dict):
            continue
        for key in ("primary", "secondary"):
            link = data.get(key)
            if isinstance(link, dict) and not _anchor_ok(str(link.get("href") or ""), kept):
                link["href"] = f"#{fallback[key]}" if fallback[key] else "#"
        for item in data.get("items") or []:
            if isinstance(item, dict) and isinstance(item.get("cta"), dict):
                href = str(item["cta"].get("href") or "")
                if not _anchor_ok(href, kept):
                    item["cta"]["href"] = f"#{rest[0]}" if rest else "#"
    nav = []
    for sec in sections:
        if not isinstance(sec, dict) or not sec.get("id") or sec.get("type") in ("hero", "cta"):
            continue
        data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
        label = str(data.get("title") or "").strip()
        if label:
            nav.append({"label": label, "href": f"#{sec['id']}"})
        if len(nav) >= 6:
            break
    raw["nav"] = nav
    footer = raw.get("footer")
    if isinstance(footer, dict) and isinstance(footer.get("links"), list):
        footer["links"] = [
            item for item in footer["links"]
            if isinstance(item, dict) and _anchor_ok(str(item.get("href") or ""), kept)
        ]


def _apply_ctx_frame(raw: dict, ctx: dict) -> None:
    frame = ctx.get("frame")
    if not isinstance(frame, dict):
        return
    pages = raw.get("pages")
    if not isinstance(pages, list) or not pages or not isinstance(pages[0], dict):
        return
    sections = pages[0].get("sections")
    if not isinstance(sections, list):
        return
    ordered = frames_mod.apply_frame(sections, frame)
    if ordered is sections:
        return
    pages[0]["sections"] = ordered
    _repair_frame_links(raw, ordered)


def _build_ir(ctx: dict) -> dict:
    copy = _load_copy(ctx)
    mold = _mold(ctx)
    template = (mold or {}).get("template") or ctx.get("template") or "editorial"
    if template not in ir_mod.TEMPLATES:
        template = "editorial"
    opts = {
        "brief": copy.brief or str(ctx.get("brief") or ""),
        "template": template,
        "dark": True,
        "brand": None,
    }
    raw = offline_mod.plan_offline(copy, opts)
    _apply_ctx_frame(raw, ctx)
    raw.setdefault("theme", {})
    raw["theme"]["template"] = template
    accent = (mold or {}).get("palette") or ctx.get("palette")
    if accent:
        raw["theme"]["accent"] = accent
    site_ir = ir_mod.normalize_site(raw, opts)
    # Gap gate on the crew path: mandatory miss FAILs the hand (callers
    # already convert SystemExit to a FAIL ret with no HTML emitted).
    from lib.copy_schema import raise_first_gap as _raise_gap
    _raise_gap(site_ir)
    _remember_ir(ctx, site_ir)
    return site_ir


def brief_read(ctx: dict) -> dict:
    try:
        copy = _load_copy(ctx)
    except SystemExit as exc:
        return _ret("FAIL", str(exc))
    brief = (copy.brief or "").strip()
    if not brief:
        return _ret("FAIL", "brief.md is empty")
    ctx["brief"] = copy.brief
    return _ret("PASS", f"brief read ({len(brief)} chars)", {"brief": copy.brief})


def _public_frame(frame: dict) -> dict:
    return {
        "id": frame["id"],
        "intent": frame["intent"],
        "sections": list(frame["sections"]),
        "nav": frame["nav"],
        "template": frame["template"],
    }


def frame_list(ctx: dict) -> dict:
    frames = [_public_frame(frame) for frame in frames_mod.list_frames()]
    return _ret("PASS", f"{len(frames)} frame(s)", {"frames": frames})


def frame_pick(ctx: dict) -> dict:
    frame_id = str(ctx.get("frame_id") or "").strip()
    if not frame_id:
        ctx["frame"] = None
        return _ret("PASS", "no frame selected; planner uses copy order", {"frame": None})
    try:
        frame = frames_mod.load_frame(frame_id)
    except FrameError as exc:
        return _ret("FAIL", str(exc))
    ctx["frame"] = frame
    ctx["frame_id"] = frame["id"]
    return _ret(
        "PASS",
        f"frame {frame['id']} ({', '.join(frame['sections'])})",
        {"frame": _public_frame(frame)},
    )


def mold_pick(ctx: dict) -> dict:
    try:
        lib = _library(ctx)
    except LibraryError as exc:
        return _ret("FAIL", str(exc))
    mold_id = str(ctx.get("mold_id") or "").strip()
    if not mold_id:
        if not all(str(ctx.get(key) or "").strip() for key in _SCRATCH):
            return _ret("FAIL", "pass mold_id or scratch fields")
        mold_id = ir_mod.slugify(ctx.get("site") or "scratch") or "scratch"
        try:
            mold = lib.save_mold({
                "id": mold_id,
                "origin": "scratch",
                "palette": ctx["palette"],
                "type_lead": ctx["type_lead"],
                "nav": ctx["nav"],
                "template": ctx["template"],
                "note": "scratch mold for this site",
            })
        except LibraryError as exc:
            return _ret("FAIL", str(exc))
    else:
        try:
            mold = lib.load_mold(mold_id)
        except LibraryError as exc:
            return _ret("FAIL", str(exc))
    ctx["mold"] = mold
    ctx["mold_id"] = mold["id"]
    return _ret(
        "PASS",
        f"mold {mold['id']} ({mold['origin']}, {mold['type_lead']}, {mold['nav']})",
        {"mold": mold},
    )


def library_bind(ctx: dict) -> dict:
    try:
        lib = _library(ctx)
        mold = _mold(ctx)
    except LibraryError as exc:
        return _ret("FAIL", str(exc))
    if not mold:
        return _ret("FAIL", "no mold")
    site = str(ctx.get("site") or "").strip()
    if not site:
        return _ret("FAIL", "site is required")
    live = bool(ctx.get("live", False))
    try:
        row = lib.bind(site, mold["id"], vendor_frame=ctx.get("vendor_frame") or None, live=live)
    except LibraryError as exc:
        return _ret("FAIL", str(exc))
    flag = "live" if row["live"] else "draft"
    return _ret("PASS", f"bound {row['site']} -> {row['mold']} ({flag})", {"bind": row})


def sitemap_read(ctx: dict) -> dict:
    """Architect hand: FAIL on an intent-less page or a non-frame section.

    Crew runs require sitemap.json (FINAL D1, scoped). The offline
    single-page loop never calls hands, so a missing doc here is
    FAIL pages.scope, never an emit.
    """
    from lib import sitemap as sitemap_mod

    found = sitemap_mod.find_sitemap(ctx.get("out"), ctx.get("project"))
    if found is None:
        return _ret("FAIL", "FAIL pages.scope: crew runs require sitemap.json")
    try:
        doc = sitemap_mod.load_sitemap(found.parent)
    except sitemap_mod.SitemapError as exc:
        return _ret("FAIL", str(exc))
    ctx["sitemap"] = doc
    frame = ctx.get("frame") if isinstance(ctx.get("frame"), dict) else None
    rows = sitemap_mod.read_for_architect(doc, frame)
    failed = [row for row in rows if row["status"] == "FAIL"]
    data: dict = {"sitemap": str(found), "rows": rows}
    if failed:
        return _ret("FAIL", "; ".join(str(row["detail"]) for row in failed), data)
    count = len(doc.get("pages") or [])
    return _ret("PASS", f"sitemap {count} page(s): intent present, frame vocabulary held", data)


def _copy_citation(project: Path, copy) -> tuple[list[str], list[str]]:
    """Files the blocks cite, and any file that is not inside that project's copy/."""
    copy_dir = (project / "copy").resolve()
    files: list[str] = []
    bad: list[str] = []
    seen: set[str] = set()
    for block in copy.blocks:
        raw = str(getattr(block, "file", "") or "").strip()
        if not raw:
            bad.append("(missing file)")
            continue
        if raw in seen:
            continue
        seen.add(raw)
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts or path.name != raw:
            bad.append(raw)
            continue
        full = (copy_dir / raw).resolve()
        if copy_dir not in full.parents or not full.is_file():
            bad.append(raw)
            continue
        files.append(f"copy/{raw}")
    return files, bad


def _content_detail(copy, files: list[str]) -> str:
    cited = ", ".join(files) if files else "copy/"
    return f"{len(copy.blocks)} block(s) from {cited}"


def copy_read(ctx: dict) -> dict:
    try:
        copy = _load_copy(ctx)
    except SystemExit as exc:
        return _ret("FAIL", str(exc))
    project = Path(str(ctx.get("project") or ""))
    files, bad = _copy_citation(project, copy)
    titles = [b.title for b in copy.blocks]
    data = {"blocks": len(titles), "titles": titles, "files": files, "warnings": list(copy.warnings)}
    if bad:
        return _ret("FAIL", "block file is not under copy/: " + ", ".join(bad), data)
    return _ret("PASS", _content_detail(copy, files), data)


def copy_gap(ctx: dict) -> dict:
    try:
        copy = _load_copy(ctx)
    except SystemExit as exc:
        return _ret("FAIL", str(exc))
    if not copy.blocks:
        return _ret("FAIL", "copy/ has no blocks; nothing was invented to fill them", {"blocks": 0, "files": []})
    project = Path(str(ctx.get("project") or ""))
    files, bad = _copy_citation(project, copy)
    if bad:
        return _ret(
            "FAIL",
            "block file is not under copy/: " + ", ".join(bad),
            {"blocks": len(copy.blocks), "files": files},
        )
    return _ret("PASS", _content_detail(copy, files), {"blocks": len(copy.blocks), "files": files})


_COPY_CHECK_SYSTEM = (
    "You are a terse copy editor for static small-business sites. "
    "Review the project copy below and reply with one line starting CLEAN or ISSUES, "
    "then one short note per issue. Flag only: filler phrases (in conclusion, furthermore, "
    "moreover, delve, testament, beacon, nestled, rich tapestry, crucial, vital, in summary), "
    "exclamation points, and invented facts, prices, or quotes. Do not rewrite the copy."
)

_COPY_BANNED = (
    "in conclusion", "furthermore", "moreover", "it is important to remember", "delve",
    "testament", "beacon", "nestled", "rich tapestry", "crucial", "vital", "in summary",
)


def _mechanical_copy_issues(text: str) -> list[str]:
    """Banned-phrase scan that runs with or without AI (also the offline fallback note)."""
    issues = []
    low = str(text or "").lower()
    for word in _COPY_BANNED:
        if re.search(r"\b" + re.escape(word) + r"\b", low):
            issues.append(f"banned phrase: {word}")
    if "!" in str(text or ""):
        issues.append("exclamation point")
    return issues


def _sc_ai_chain_module():
    """Import the optional AI chain the way lib/providers.py does (sys.path, no package)."""
    import sys

    for directory in (os.environ.get("SC_AI_CHAIN_DIR", ""),
                      str(Path(__file__).resolve().parent.parent / "ai_chain")):
        if directory and directory not in sys.path and Path(directory).is_dir():
            sys.path.append(directory)
    import sc_ai_chain
    return sc_ai_chain


def copy_check(ctx: dict) -> dict:
    """Advisory AI copy check (content seat). Always PASS: the static checker stays the gate.

    When SC_AI=on and a route answers, data carries the live verdict with
    source="ai" (provider/model/ms included). Otherwise data carries the
    mechanical scan with source="template" and the reason AI did not run.
    Never raises: any import or chain error becomes a PASS advisory.
    """
    raw = str(ctx.get("project") or "").strip()
    if not raw:
        return _ret("FAIL", "project is required")
    copy_text = _project_copy_text(ctx)
    if not copy_text.strip():
        return _ret("PASS", "no copy text to AI-check; gap check governs",
                    {"source": "template", "reason": "empty copy", "issues": [],
                     "verdict": "", "provider": "", "model": "", "ms": 0, "usage": {}})
    mechanical = sorted(set(_mechanical_copy_issues(copy_text)))
    fallback_note = "; ".join(mechanical) if mechanical else "mechanical style check clean"
    clipped = copy_text[:6000]
    try:
        chain_mod = _sc_ai_chain_module()
        result = chain_mod.generate(
            system=_COPY_CHECK_SYSTEM,
            user="Project copy to review:\n\n" + clipped,
            fallback=fallback_note, purpose="copy-check",
            max_tokens=400, temperature=0.2, min_chars=5, max_chars=4000)
        source, provider, model = result.source, result.provider, result.model
        reason, ms, verdict = result.reason, result.ms, (result.text or "")[:2000]
        usage = dict(getattr(result, "usage", None) or {})
    except Exception as exc:  # noqa: BLE001 -- advisory: never break a build
        source, provider, model = "template", "", ""
        reason, ms, verdict = f"chain error {type(exc).__name__}", 0, fallback_note
        usage = {}
    data = {"source": source, "provider": provider, "model": model, "reason": reason,
            "ms": ms, "usage": usage, "issues": mechanical, "verdict": verdict}
    if source == "ai":
        first = next((line.strip() for line in verdict.splitlines() if line.strip()), "done")
        return _ret("PASS", f"AI copy check ({provider}/{model}): {first[:160]}", data)
    return _ret("PASS", f"copy check fallback ({reason}); mechanical: {fallback_note[:160]}", data)


def _remote_src(src: str) -> bool:
    text = str(src or "").strip()
    return text.startswith(("http://", "https://", "//", "\\\\"))


def _has_dotdot(src: str) -> bool:
    return ".." in str(src or "").replace("\\", "/")


def _local_src_file(project: Path, src: str) -> Path | None:
    """File inside project, or None if remote, contains `..`, or escapes."""
    text = str(src or "").strip()
    if not text or _remote_src(text) or _has_dotdot(text):
        return None
    rel = Path(text)
    if rel.is_absolute():
        return None
    root = project.resolve()
    try:
        full = (root / rel).resolve()
        full.relative_to(root)
    except (OSError, ValueError):
        return None
    if not full.is_file():
        return None
    return full


def _find_local_hero(project: Path) -> tuple[str, Path] | None:
    """First assets/hero.png, .jpg, .jpeg, or .webp that stays inside project."""
    for ext in _HERO_EXTS:
        rel = f"assets/hero{ext}"
        full = _local_src_file(project, rel)
        if full is not None:
            return rel, full
    return None


def _index_hero_data(site_ir: dict) -> dict | None:
    pages = site_ir.get("pages")
    if not isinstance(pages, list) or not pages or not isinstance(pages[0], dict):
        return None
    sections = pages[0].get("sections")
    if not isinstance(sections, list):
        return None
    for sec in sections:
        if isinstance(sec, dict) and sec.get("type") == "hero" and isinstance(sec.get("data"), dict):
            return sec["data"]
    return None


def _hero_alt(site_ir: dict, data: dict) -> str:
    existing = str(data.get("image_alt") or "").strip()
    if existing:
        return existing
    heading = str(data.get("headline") or "").strip()
    if heading:
        return heading
    meta = site_ir.get("meta") if isinstance(site_ir.get("meta"), dict) else {}
    name = str(meta.get("title") or "").strip()
    if name:
        return f"{name} hero"
    return "hero"


def _copy_hero_bytes(src: Path, dest: Path, rel: str) -> None:
    root = dest.resolve()
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise OSError("hero path escapes the output directory") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, target)


def _attach_local_hero(ctx: dict, site_ir: dict, dest: Path) -> None:
    """Use a project-local assets/hero file when the IR hero has no local image."""
    project_raw = str(ctx.get("project") or "").strip()
    if not project_raw:
        return
    data = _index_hero_data(site_ir)
    if data is None:
        return
    project = Path(project_raw)
    existing = str(data.get("image") or "").strip()
    if existing and _local_src_file(project, existing) is not None:
        return
    found = _find_local_hero(project)
    if found is None:
        if existing and _escapes_project(project, existing):
            data["image"] = ""
        return
    rel, src = found
    data["image"] = rel
    data["image_alt"] = _hero_alt(site_ir, data)
    _copy_hero_bytes(src, dest, rel)
    width, height = render_mod.image_box(dest / rel)
    if width > 0 and height > 0:
        data["image_w"] = width
        data["image_h"] = height


def _escapes_project(project: Path, src: str) -> bool:
    text = str(src or "").strip()
    if not text or _remote_src(text) or _has_dotdot(text) or Path(text).is_absolute():
        return True
    root = project.resolve()
    try:
        full = (root / text).resolve()
        full.relative_to(root)
    except (OSError, ValueError):
        return True
    return False


def plan_offline(ctx: dict) -> dict:
    try:
        site_ir = _build_ir(ctx)
    except SystemExit as exc:
        return _ret("FAIL", str(exc))
    except LibraryError as exc:
        return _ret("FAIL", str(exc))
    return _ret("PASS", f"planned {len(site_ir.get('pages') or [])} page(s)", {"site_ir": site_ir})


def render(ctx: dict) -> dict:
    site_ir = _stored_ir(ctx)
    if not site_ir:
        try:
            site_ir = _build_ir(ctx)
        except SystemExit as exc:
            return _ret("FAIL", str(exc))
        except LibraryError as exc:
            return _ret("FAIL", str(exc))
    out = ctx.get("out")
    if not out:
        return _ret("FAIL", "out is required")
    try:
        dest = Path(out)
        dest.mkdir(parents=True, exist_ok=True)
        _attach_local_hero(ctx, site_ir, dest)
        pages = render_mod.assemble(site_ir, noindex=True)
        for page in pages:
            (dest / page["file"]).write_text(page["html"], encoding="utf-8")
        (dest / "site.json").write_text(json.dumps(site_ir, indent=2), encoding="utf-8")
    except (OSError, KeyError, TypeError) as exc:
        return _ret("FAIL", str(exc))
    names = [page["file"] for page in pages]
    return _ret("PASS", f"{len(names)} page(s) written", {"pages": names, "site_ir": site_ir})


def attempt_snapshot(ctx: dict) -> dict:
    """Frontend-seat hand: snapshot the built tree before dirty ops (D2)."""
    from lib import attempts as _attempts

    result = _attempts.attempt_snapshot(ctx if isinstance(ctx, dict) else {})
    data = result.get("data")
    return _ret(
        str(result.get("status") or "FAIL"),
        str(result.get("detail") or ""),
        dict(data) if isinstance(data, dict) else {},
    )


def _remote_and_local(project: Path, copy) -> tuple[list[str], list[str]]:
    remote: list[str] = []
    local: list[str] = []
    assets = project / "assets.json"
    if assets.exists():
        data = json.loads(assets.read_text(encoding="utf-8"))
        for rel in (data.get("images") or {}).values():
            rel = str(rel)
            if rel.startswith(("http://", "https://")) or ingest.HOTLINK_RE.search(rel):
                remote.append(rel)
            else:
                local.append(rel)
    copy_dir = project / "copy"
    if copy_dir.is_dir():
        for path in sorted(p for p in copy_dir.iterdir() if p.is_file()):
            if path.suffix.lower() not in {".md", ".markdown", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for src in _MD_IMG.findall(text):
                if src.startswith(("http://", "https://")) or ingest.HOTLINK_RE.search(src):
                    remote.append(src)
    for block in copy.blocks:
        for image in block.images:
            src = str(image.get("src") or "")
            if src.startswith(("http://", "https://")) or ingest.HOTLINK_RE.search(src):
                remote.append(src)
    for warning in copy.warnings:
        if "external image" in warning or "hotlinked" in warning:
            remote.append(warning)
    found = _find_local_hero(project)
    if found is not None:
        rel = found[0]
        if rel not in {item.replace("\\", "/") for item in local}:
            local.append(rel)
    return remote, local


def asset_list(ctx: dict) -> dict:
    project = ctx.get("project")
    if not project:
        return _ret("FAIL", "project is required")
    try:
        copy = _load_copy(ctx)
        remote, local = _remote_and_local(Path(project), copy)
    except SystemExit as exc:
        return _ret("FAIL", str(exc))
    except (OSError, ValueError) as exc:
        return _ret("FAIL", f"assets.json unreadable ({exc})")
    if remote:
        return _ret("FAIL", "remote asset urls are not allowed", {"remote": remote, "local": local})
    return _ret("PASS", f"{len(local)} local asset(s); no stock CDN", {"remote": [], "local": local})


def vault_photos(ctx: dict) -> dict:
    try:
        lib = _library(ctx)
        mold = _mold(ctx)
    except LibraryError as exc:
        return _ret("FAIL", str(exc))
    if not mold:
        return _ret("FAIL", "no mold")
    parents = [str(p) for p in (mold.get("parents") or []) if str(p).startswith(("owp:", "gp:"))]
    if not parents:
        return _ret("PASS", "no parent frames", {"photos": []})
    photos: list[str] = []
    missing: list[str] = []
    for frame_id in parents:
        frame = lib.frame_by_id(frame_id)
        snap = frame.get("snapshot") if frame else None
        folder = Path(snap) if snap else None
        if folder is None or not folder.is_dir():
            missing.append(frame_id)
            continue
        photos.extend(sorted(
            path.name for path in folder.rglob("*")
            if path.is_file() and path.suffix.lower() in _IMG_EXT
        ))
    if missing:
        return _ret(
            "SKIP",
            "snapshot not in vault for " + ", ".join(missing),
            {"photos": photos, "missing": missing},
        )
    return _ret("PASS", f"{len(photos)} vault photo(s)", {"photos": photos})


def _project_copy_text(ctx: dict) -> str:
    """Concatenated project copy, files in sorted name order."""
    raw = str(ctx.get("project") or "").strip()
    if not raw:
        return ""
    copy_dir = Path(raw) / "copy"
    if not copy_dir.is_dir():
        return ""
    names = sorted(
        path.name for path in copy_dir.iterdir()
        if path.is_file() and path.suffix.lower() in _COPY_TEXT_SUFFIXES
    )
    parts = [
        (copy_dir / name).read_text(encoding="utf-8", errors="replace")
        for name in names
    ]
    return "\n".join(parts)


def check_site(ctx: dict) -> dict:
    out = ctx.get("out")
    if not out:
        return _ret("FAIL", "out is required")
    dest = Path(out)
    copy_text = _project_copy_text(ctx)
    report = check_mod.check_site(dest, expect_noindex=True, quiet=True, copy_text=copy_text)
    failed = [row["name"] for row in report.rows if row["status"] == "FAIL"]
    data = {"rows": report.rows}
    if failed:
        return _ret("FAIL", ", ".join(failed), data)
    return _ret("PASS", "checker 0 FAIL, noindex on", data)


def uniqueness(ctx: dict) -> dict:
    try:
        lib = _library(ctx)
        mold = _mold(ctx)
    except LibraryError as exc:
        return _ret("FAIL", str(exc))
    if not mold:
        return _ret("FAIL", "no mold")
    site = str(ctx.get("site") or "")
    conflict = lib.live_conflict(mold["id"], site)
    if conflict:
        return _ret(
            "FAIL",
            f"mold {mold['id']} is already live on {conflict}",
            {"conflict": conflict, "mold": mold["id"]},
        )
    return _ret(
        "PASS",
        "one mold on this site; a second live use will be refused",
        {"mold": mold["id"], "site": site},
    )


def meta_basics(ctx: dict) -> dict:
    out = ctx.get("out")
    if not out:
        return _ret("FAIL", "out is required")
    report = check_mod.check_site(Path(out), expect_noindex=True, quiet=True)
    rows = [row for row in report.rows if row["name"] in ("meta_basics", "no_sample")]
    meta = next((row for row in rows if row["name"] == "meta_basics"), None)
    if meta is None or any(row["status"] == "FAIL" for row in rows):
        return _ret("FAIL", "meta or sample checks failed", {"rows": rows})
    return _ret("PASS", meta.get("detail") or "meta basics present", {"rows": rows})


def sitemap_check(ctx: dict) -> dict:
    """SEO hand: orphan/intent/vocab/link rows plus rendered-page rows.

    h1 counts and FAQ visibility are read from the rendered HTML the
    frontend seat wrote. A page with no rendered file yields SKIP rows
    (NOT RUN evidence, never PASS). A missing sitemap.json in a crew run
    is FAIL pages.scope.
    """
    from lib import sitemap as sitemap_mod

    out = ctx.get("out")
    if not out:
        return _ret("FAIL", "out is required")
    dest = Path(out)
    found = sitemap_mod.find_sitemap(dest, ctx.get("project"))
    if found is None:
        return _ret("FAIL", "FAIL pages.scope: crew runs require sitemap.json")
    try:
        doc = sitemap_mod.load_sitemap(found.parent)
    except sitemap_mod.SitemapError as exc:
        return _ret("FAIL", str(exc))
    ctx["sitemap"] = doc
    frame = ctx.get("frame") if isinstance(ctx.get("frame"), dict) else None
    faq_sections = {
        str(page.get("file")): "faq" in (page.get("sections") or [])
        for page in (doc.get("pages") or [])
        if isinstance(page, dict)
    }
    h1_counts: dict[str, int] = {}
    faq_visible: dict[str, bool] = {}
    for file, wants_faq in faq_sections.items():
        page = dest / file
        if not page.is_file():
            continue
        try:
            html = page.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        h1_counts[file] = len(re.findall(r"<h1[\s>]", html, re.IGNORECASE))
        if wants_faq:
            faq_visible[file] = "<details" in html.lower()
    rows = sitemap_mod.check(doc, frame, h1_counts=h1_counts, faq_visible=faq_visible)
    failed = [row for row in rows if row["status"] == "FAIL"]
    data: dict = {"sitemap": str(found), "rows": rows}
    if failed:
        return _ret("FAIL", "; ".join(str(row["detail"]) for row in failed), data)
    count = len(doc.get("pages") or [])
    skipped = sum(1 for row in rows if row["status"] == "SKIP")
    note = f"sitemap {count} page(s): no orphan, intent and links held"
    if skipped:
        note += f" ({skipped} row(s) SKIP: page not rendered)"
    return _ret("PASS", note, data)


def _sha_bound(dest: Path) -> dict[str, str]:
    """sha256 of the release artifact: HTML + assets + site.json.

    The ticket file itself is excluded (it cannot hash itself), as is
    _attempts/ provenance and *.bak scratch: attempts are history, not
    product, and hashing them would break stable rebuild identity. A byte
    change in any bound file invalidates sign-off: re-run the crew.
    """
    bound: dict[str, str] = {}
    if not dest.is_dir():
        return bound
    for path in sorted(dest.rglob("*")):
        if not path.is_file() or path.name in ("crew-ticket.json",):
            continue
        if path.suffix == ".bak":
            continue
        try:
            rel = path.relative_to(dest)
        except ValueError:
            continue
        if rel.parts and rel.parts[0] == "_attempts":
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
        bound[str(path.relative_to(dest)).replace("\\", "/")] = digest
    return bound


def ticket_write(ctx: dict) -> dict:
    out = ctx.get("out")
    if not out:
        return _ret("FAIL", "out is required")
    dest = Path(out)
    dest.mkdir(parents=True, exist_ok=True)
    site = str(ctx.get("site") or "")
    mold = ctx.get("mold") if isinstance(ctx.get("mold"), dict) else {}
    mold_id = str(ctx.get("mold_id") or mold.get("id") or "")
    note = "ticket written; publish is a Keith click (library bind --live)"
    hands = ctx.get("hands")
    if hands:
        ok = not any(str(hand.get("status")) == "FAIL" for hand in hands)
        ticket = {
            "site": site,
            "mold": mold_id,
            "publish": "Keith click. This run does not deploy.",
            "hands": hands,
            "ok": ok,
            "sha256": _sha_bound(dest),
        }
    else:
        ok = True
        ticket = {
            "site": site,
            "mold": mold_id,
            "publish": "Keith click. This run does not deploy.",
            "note": note,
            "ok": True,
            "sha256": _sha_bound(dest),
        }
    path = dest / "crew-ticket.json"
    path.write_text(json.dumps(ticket, indent=2) + "\n", encoding="utf-8")
    return _ret("PASS" if ok else "FAIL", note, {"ticket": ticket, "path": str(path)})


HANDS = {
    "brief_read": brief_read,
    "frame_pick": frame_pick,
    "mold_pick": mold_pick,
    "library_bind": library_bind,
    "sitemap_read": sitemap_read,
    "copy_read": copy_read,
    "copy_gap": copy_gap,
    "copy_check": copy_check,
    "plan_offline": plan_offline,
    "render": render,
    "attempt_snapshot": attempt_snapshot,
    "asset_list": asset_list,
    "vault_photos": vault_photos,
    "check_site": check_site,
    "uniqueness": uniqueness,
    "meta_basics": meta_basics,
    "sitemap_check": sitemap_check,
    "ticket_write": ticket_write,
}
