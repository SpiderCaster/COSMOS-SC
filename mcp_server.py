#!/usr/bin/env python3
"""SpiderCaster MCP server - stdio transport, stdlib only (no pip deps).

Exposes the working SpiderCaster engine (IR, renderer, checks, wallets) as MCP
tools so any harness-bound agent (Claude Code, Codex, Cursor, Antigravity,
OpenCode, WOMBAT's own harness, ...) can drive it. Tool names follow the
COSMOS2 engine design; the implementation runs against the real engine.

Protocol: MCP stdio = newline-delimited JSON-RPC 2.0 on stdin/stdout.
Logs to stderr only. Never prints or stores key values.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib import check as check_mod      # noqa: E402
from lib import ingest                  # noqa: E402
from lib import ir as ir_mod            # noqa: E402
from lib import offline as offline_mod  # noqa: E402
from lib import render                  # noqa: E402
from lib.crew import ROLES              # noqa: E402
from lib.frames import FrameError, list_frames, load_frame  # noqa: E402
from lib.library import Library         # noqa: E402

SURFACE_ROOT = Path(os.environ.get("SPIDERCASTER_SURFACE_ROOT") or (ROOT / "sites"))
SECRETS_DIR = Path(os.environ.get("SPIDERCASTER_SECRETS_DIR") or r"<your-key-file-dir>")
SERVER_INFO = {"name": "spidercaster-mcp", "version": "0.1.0"}


# ---------------------------------------------------------------- helpers

def _site_dir(site: str) -> Path:
    p = Path(site) if Path(site).is_absolute() else (SURFACE_ROOT / site)
    if not (p / "site.json").exists() and not (p / "index.html").exists():
        raise FileNotFoundError(f"site not found under {SURFACE_ROOT}: {site}")
    return p


def _load_site(site: str) -> dict:
    return json.loads((_site_dir(site) / "site.json").read_text(encoding="utf-8"))


def _text(result) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False, default=str)


def _key_meta(text: str):
    t = (text or "").strip()
    if not t:
        return None
    return {"len": len(t), "last4": t[-4:],
            "fp": hashlib.sha256(t.encode("utf-8")).hexdigest()[:6]}


# ---------------------------------------------------------------- tools

def tool_catalog_read(args: dict) -> dict:
    return {
        "engine": "spidercaster/0.1",
        "granularity": "section-level IR; the renderer owns layout and styles",
        "section_types": [
            {"id": t, "data_fields": ir_mod.SECTION_DOCS.get(t, "")}
            for t in ir_mod.SECTION_TYPES
        ],
        "icons": ir_mod.ICON_NAMES,
        "templates": ir_mod.TEMPLATES,
        "rules": [
            "content must be real: no placeholder, SAMPLE, lorem or invented facts",
            "omit a section when there is nothing real to put in it",
            "styles are engine-owned: choose theme knobs (template/dark/accent), never literal values",
        ],
    }


def tool_tokens_read(args: dict) -> dict:
    template = args.get("template") if args.get("template") in ir_mod.TEMPLATES else "modern"
    theme = {
        "template": template,
        "dark": bool(args.get("dark", True)),
        "accent": ir_mod.hex6(args.get("accent")),
        "accent2": ir_mod.hex6(args.get("accent2")),
    }
    pal = render.build_palette(theme, args.get("seed") or "spidercaster")
    vars_out = {}
    m = re.search(r":root\{([^}]*)\}", render.CSS_TEMPLATE)
    if m:
        for decl in m.group(1).split(";"):
            decl = decl.strip()
            if decl.startswith("--"):
                name = decl[2:].partition(":")[0].strip()
                key = name.replace("-", "_")
                vars_out["--" + name] = pal.get(key, "1120px" if name == "maxw" else None)
    return {"theme": theme, "resolved": pal, "css_vars": vars_out,
            "note": "these are the engine's semantic tokens; agents set theme knobs only"}


def tool_pagemodel_read(args: dict) -> dict:
    site = args["site"]
    return {"site": site, "model": _load_site(site)}


def tool_pagemodel_write(args: dict) -> dict:
    role = args.get("role", "builder")
    mode = args.get("mode", "full")
    site_name = args["site"]
    sdir = _site_dir(site_name)
    sj = sdir / "site.json"
    current = json.loads(sj.read_text(encoding="utf-8")) if sj.exists() else {}
    model = args.get("pageModel") or {}
    notes = []

    if mode == "patch" or role in ("content", "editor"):
        merged = dict(current)
        for k in ("meta", "theme", "footer", "nav"):
            if k in model:
                merged[k] = model[k]
        if "pages" in model:
            cur_pages = {p.get("slug", "index"): dict(p) for p in merged.get("pages", [])}
            for p in model.get("pages", []):
                slug = p.get("slug", "index")
                if slug in cur_pages:
                    existing = {s["id"]: s for s in cur_pages[slug].get("sections", [])}
                    for s in p.get("sections", []):
                        old = existing.get(s.get("id"))
                        if role in ("content", "editor") and old and old.get("type") != s.get("type"):
                            notes.append(f"kept {s.get('id')}: role '{role}' cannot change section type")
                            continue
                        existing[s.get("id")] = s
                    cur_pages[slug]["sections"] = list(existing.values())
                else:
                    if role in ("content", "editor"):
                        notes.append(f"skipped new page {slug}: role '{role}' cannot add pages")
                        continue
                    cur_pages[slug] = p
            merged["pages"] = list(cur_pages.values())
        raw = merged
    else:
        if role != "builder":
            return {"isError": True,
                    "message": f"role '{role}' may not write full models (builder only); use mode=patch"}
        raw = model

    site = ir_mod.normalize_site(raw, {"brief": raw.get("brief") or current.get("brief", "")})
    if sj.exists():
        shutil.copy2(sj, sdir / "site.json.bak")
    sj.write_text(json.dumps(site, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "written", "site": site_name, "path": str(sj),
            "sections": [s["id"] for p in site["pages"] for s in p["sections"]],
            "notes": notes}


def tool_render_trigger(args: dict) -> dict:
    site_name = args["site"]
    sdir = _site_dir(site_name)
    site = _load_site(site_name)
    noindex = bool(args.get("noindex", True))
    outputs = []
    for p in render.assemble(site, noindex=noindex):
        f = sdir / p["file"]
        f.write_text(p["html"], encoding="utf-8")
        outputs.append({"file": p["file"], "bytes": len(p["html"].encode("utf-8"))})
    return {"status": "rendered", "site": site_name, "noindex": noindex, "outputs": outputs,
            "tokens_used": 0, "note": "deterministic render; zero model cost"}


def tool_validate_run(args: dict) -> dict:
    sdir = _site_dir(args["site"])
    rep = check_mod.check_site(sdir, None, quiet=True)  # quiet: keep the stdio channel clean
    return {"site": args["site"], "ok": rep.ok(), "counts": rep.counts(), "checks": rep.rows}


def tool_review_write(args: dict) -> dict:
    sdir = _site_dir(args["site"])
    rdir = sdir / "review"
    rdir.mkdir(exist_ok=True)
    page = Path(args.get("pagePath") or "index").stem
    out = rdir / f"{page}.review.json"
    out.write_text(json.dumps({"results": args.get("results"),
                               "writtenAt": time.strftime("%Y-%m-%d %H:%M:%S")},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "written", "path": str(out)}


def tool_brand_read(args: dict) -> dict:
    out = {}
    proj = args.get("project")
    if proj:
        p = Path(proj) if Path(proj).is_absolute() else (ROOT / "projects" / proj)
        brief = p / "brief.md"
        out["project"] = str(p)
        out["brief"] = brief.read_text(encoding="utf-8", errors="replace") if brief.exists() else ""
        cp = p / "copy"
        out["copy_files"] = sorted(x.name for x in cp.iterdir() if x.is_file()) if cp.exists() else []
    site = args.get("site")
    if site:
        m = _load_site(site)
        out["site"] = site
        out["meta"] = m.get("meta")
        out["theme"] = m.get("theme")
        out["footer"] = m.get("footer")
    return out


def tool_brand_write(args: dict) -> dict:
    site_name = args["site"]
    sdir = _site_dir(site_name)
    sj = sdir / "site.json"
    cur = json.loads(sj.read_text(encoding="utf-8"))
    brand = args.get("brand") or {}
    meta = dict(cur.get("meta", {}))
    if brand.get("title"):
        meta["title"] = str(brand["title"])[:60]
    if brand.get("description"):
        meta["description"] = str(brand["description"])[:155]
    cur["meta"] = meta
    theme = dict(cur.get("theme", {}))
    for k in ("template", "dark", "accent", "accent2"):
        if k in brand:
            theme[k] = brand[k]
    cur["theme"] = theme
    site = ir_mod.normalize_site(cur, {"brief": cur.get("brief", "")})
    shutil.copy2(sj, sdir / "site.json.bak")
    sj.write_text(json.dumps(site, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "written", "meta": site["meta"], "theme": site["theme"]}


def tool_draft_offline(args: dict) -> dict:
    proj = args["project"]
    p = Path(proj) if Path(proj).is_absolute() else (ROOT / "projects" / proj)
    copy = ingest.load_project(p)
    opts = {"template": args.get("template"), "dark": args.get("dark"),
            "brand": args.get("brand"), "brief": copy.brief}
    raw = offline_mod.plan_offline(copy, opts)
    site = ir_mod.normalize_site(raw, opts)
    return {"project": str(p), "model": site, "warnings": copy.warnings, "tokens_used": 0,
            "note": "deterministic draft from real copy only; zero model cost"}


def tool_wallets(args: dict) -> dict:
    out = {"env_key": _key_meta(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "")}
    kf = os.environ.get("FORGE_GEMINI_KEY_FILE")
    if kf and Path(kf).exists():
        out["active_draw"] = {"file": kf, **(_key_meta(Path(kf).read_text(encoding="utf-8")) or {})}
    sd = Path(args.get("secretsDir") or SECRETS_DIR)
    wallets = []
    if sd.exists():
        for p in sorted(list(sd.glob("vertex_*_key.txt")) + list(sd.glob("gemini_key5.txt"))):
            m = _key_meta(p.read_text(encoding="utf-8"))
            if m:
                wallets.append({"file": p.name, **m})
    out["wallets"] = wallets
    out["note"] = "last4 + fingerprint only; expiry = registration + 90d; dates live in console > Billing > Credits"
    return out


def tool_crew_roles(_args: dict) -> dict:
    return {"roles": [{k: role[k] for k in ("id", "n", "label", "hands", "does_not")} for role in ROLES]}


def tool_mold_list(_args: dict) -> dict:
    lib = Library(ROOT / "library", Path(os.environ.get("SPIDERCASTER_VAULT") or r"V:\streams\webdev\vendor-vault"))
    return {"molds": lib.package_manifest()["molds"], "publish": "Keith click. crew does not deploy."}


def _public_frame(frame: dict) -> dict:
    return {
        "id": frame["id"],
        "intent": frame["intent"],
        "sections": list(frame["sections"]),
        "nav": frame["nav"],
        "template": frame["template"],
    }


def tool_frame_list(_args: dict) -> dict:
    return {"frames": [_public_frame(frame) for frame in list_frames()]}


def tool_frame_pick(args: dict) -> dict:
    frame_id = str((args or {}).get("frame_id") or "").strip()
    if not frame_id:
        return {"isError": True, "message": "frame_id is required"}
    try:
        frame = load_frame(frame_id)
    except FrameError as exc:
        return {"isError": True, "message": str(exc)}
    return _public_frame(frame)


def tool_env_doctor(_args: dict) -> dict:
    try:
        from lib.doctor import report
        return report(ROOT)
    except Exception:
        return {"isError": True, "message": "doctor unavailable"}


def tool_seat_pack(args: dict) -> dict:
    seat_id = (args or {}).get("seat_id")
    if not isinstance(seat_id, str) or not seat_id.strip():
        return {"isError": True, "message": "seat_id is required"}
    try:
        from lib.seatpack import pack
        return pack(ROOT, seat_id)
    except KeyError:
        return {"isError": True, "message": "unknown seat"}


# ---------------------------------------------------------------- read-only library tools
# These call library functions. They do not publish, read secrets, or run commands.


def _lib_fn(module: str, fn_name: str):
    try:
        fn = getattr(__import__(module, fromlist=[fn_name]), fn_name)
    except ImportError:
        return None, {"isError": True, "message": "missing"}
    except Exception as exc:
        return None, {"isError": True, "message": type(exc).__name__}
    return fn, None


def _lib_call(fn, *call_args) -> dict:
    try:
        result = fn(*call_args)
    except Exception as exc:
        return {"isError": True, "message": type(exc).__name__}
    if not isinstance(result, dict):
        return {"isError": True, "message": "bad result"}
    return result


def tool_skill_read(args: dict) -> dict:
    fn, err = _lib_fn("lib.skill_read", "skill_read")
    if err:
        return err
    args = args or {}
    rel = args.get("rel")
    if not isinstance(rel, str) or rel.strip() == "":
        return {"isError": True, "message": "rel is required"}
    root = args["root"] if "root" in args else ROOT
    return _lib_call(fn, root, rel)


def tool_hook_match(args: dict) -> dict:
    fn, err = _lib_fn("lib.hook_match", "hook_match")
    if err:
        return err
    args = args or {}
    return _lib_call(fn, args.get("event"), args.get("tool_name", ""), args.get("hooks"))


def tool_perm_rule(args: dict) -> dict:
    fn, err = _lib_fn("lib.perm_rule", "perm_rule")
    if err:
        return err
    args = args or {}
    return _lib_call(fn, args.get("tool"), args.get("arg"), args.get("allow", []), args.get("deny", []))


def tool_tool_search_local(args: dict) -> dict:
    fn, err = _lib_fn("lib.tool_search_local", "tool_search_local")
    if err:
        return err
    args = args or {}
    return _lib_call(fn, args.get("query"), args.get("catalog"))


def tool_seat_tools(args: dict) -> dict:
    fn, err = _lib_fn("lib.seat_tools", "seat_tools")
    if err:
        return err
    args = args or {}
    tools = args.get("tools") if "tools" in args else None
    disallowed = args.get("disallowed") if "disallowed" in args else None
    return _lib_call(fn, args.get("parent"), tools, disallowed)


def tool_seat_gate(args: dict) -> dict:
    fn, err = _lib_fn("lib.seat_gate", "seat_gate")
    if err:
        return err
    args = args or {}
    return _lib_call(fn, args.get("caller"), args.get("seat"), args.get("hand"))


def tool_layer_read(args: dict) -> dict:
    args = args or {}
    if "write" in args:
        return {"isError": True, "message": "write refused"}
    fn, err = _lib_fn("lib.layer_read", "layer_read")
    if err:
        return err
    return _lib_call(fn, args.get("out"), args.get("root"))


def tool_code_refuse(args: dict) -> dict:
    fn, err = _lib_fn("lib.code_refuse", "code_refuse")
    if err:
        return err
    return _lib_call(fn, (args or {}).get("kind"))


def tool_mold_panel(args: dict) -> dict:
    args = args or {}
    if "live" in args:
        return {"isError": True, "message": "live refused"}
    fn, err = _lib_fn("lib.mold_panel", "mold_panel")
    if err:
        return err
    return _lib_call(fn, ROOT, args.get("mold_id"))


TOOLS = {
    "catalog_read": tool_catalog_read,
    "tokens_read": tool_tokens_read,
    "pagemodel_read": tool_pagemodel_read,
    "pagemodel_write": tool_pagemodel_write,
    "render_trigger": tool_render_trigger,
    "validate_run": tool_validate_run,
    "review_write": tool_review_write,
    "brand_read": tool_brand_read,
    "brand_write": tool_brand_write,
    "draft_offline": tool_draft_offline,
    "wallets": tool_wallets,
    "crew_roles": tool_crew_roles,
    "mold_list": tool_mold_list,
    "frame_list": tool_frame_list,
    "frame_pick": tool_frame_pick,
    "env_doctor": tool_env_doctor,
    "seat_pack": tool_seat_pack,
    "skill_read": tool_skill_read,
    "hook_match": tool_hook_match,
    "perm_rule": tool_perm_rule,
    "tool_search_local": tool_tool_search_local,
    "seat_tools": tool_seat_tools,
    "seat_gate": tool_seat_gate,
    "layer_read": tool_layer_read,
    "code_refuse": tool_code_refuse,
    "mold_panel": tool_mold_panel,
}

OBJ = {"type": "object", "properties": {}, "additionalProperties": False}

TOOL_SPECS = [
    {"name": "catalog_read", "description": "SpiderCaster section catalog: types, data fields, icons, templates, content rules.",
     "inputSchema": OBJ},
    {"name": "tokens_read", "description": "Resolved theme tokens (CSS vars) for template/dark/accent. Agents set knobs, never literals.",
     "inputSchema": {"type": "object", "properties": {
         "template": {"type": "string", "enum": ir_mod.TEMPLATES},
         "dark": {"type": "boolean"}, "accent": {"type": "string"},
         "accent2": {"type": "string"}, "seed": {"type": "string"}}}},
    {"name": "pagemodel_read", "description": "Read a built site's IR (site.json).",
     "inputSchema": {"type": "object", "required": ["site"], "properties": {"site": {"type": "string"}}}},
    {"name": "pagemodel_write", "description": "Write the IR. role=builder: mode=full. role=content|editor: mode=patch, same-type sections only, no new pages.",
     "inputSchema": {"type": "object", "required": ["site", "pageModel"], "properties": {
         "site": {"type": "string"}, "pageModel": {"type": "object"},
         "mode": {"type": "string", "enum": ["full", "patch"]},
         "role": {"type": "string", "enum": ["builder", "content", "editor"]}}}},
    {"name": "render_trigger", "description": "Deterministic render of the IR to static HTML. Zero tokens.",
     "inputSchema": {"type": "object", "required": ["site"], "properties": {
         "site": {"type": "string"}, "noindex": {"type": "boolean"}}}},
    {"name": "validate_run", "description": "Fleet-aligned checks: no_sample, hotlinks, links, meta, noindex, ledger.",
     "inputSchema": {"type": "object", "required": ["site"], "properties": {"site": {"type": "string"}}}},
    {"name": "review_write", "description": "Reviewer writes LLM judgment + revision requests to review/ on the site.",
     "inputSchema": {"type": "object", "required": ["site", "results"], "properties": {
         "site": {"type": "string"}, "pagePath": {"type": "string"}, "results": {"type": "object"}}}},
    {"name": "brand_read", "description": "Read brand inputs: project brief + copy files, and/or built site meta/theme.",
     "inputSchema": {"type": "object", "properties": {"project": {"type": "string"}, "site": {"type": "string"}}}},
    {"name": "brand_write", "description": "Patch brand knobs on a built site: title, description, template, dark, accent.",
     "inputSchema": {"type": "object", "required": ["site", "brand"], "properties": {
         "site": {"type": "string"}, "brand": {"type": "object"}}}},
    {"name": "draft_offline", "description": "Zero-token deterministic draft of a site IR from a project's real copy.",
     "inputSchema": {"type": "object", "required": ["project"], "properties": {
         "project": {"type": "string"}, "template": {"type": "string", "enum": ir_mod.TEMPLATES},
         "dark": {"type": "boolean"}, "brand": {"type": "string"}}}},
    {"name": "wallets", "description": "Fingerprint map of recorded Google wallets (last4 + fp only). FIFO planning.",
     "inputSchema": {"type": "object", "properties": {"secretsDir": {"type": "string"}}}},
    {"name": "crew_roles", "description": "The seven SpiderCaster seats, the hands each may call, and what each refuses.",
     "inputSchema": OBJ},
    {"name": "mold_list", "description": "Package molds only. Vendor frames are not listed.",
     "inputSchema": OBJ},
    {"name": "frame_list", "description": "Package section frames. Not molds, not vendor themes, no photos.",
     "inputSchema": OBJ},
    {"name": "frame_pick", "description": "Load one package section frame by id. No vault, photos, or HTML.",
     "inputSchema": {"type": "object", "required": ["frame_id"], "properties": {"frame_id": {"type": "string"}}}},
    {"name": "env_doctor", "description": "Read-only environment report. Does not publish and does not read secrets.",
     "inputSchema": OBJ},
    {"name": "seat_pack", "description": "Read-only pack for one seat. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["seat_id"], "properties": {"seat_id": {"type": "string"}}}},
    {"name": "skill_read", "description": "Read one SKILL.md. root defaults to the package root. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["rel"], "properties": {
         "root": {"type": "string"}, "rel": {"type": "string"}}}},
    {"name": "hook_match", "description": "Match hook rows in memory. Never runs a command. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["event", "tool_name", "hooks"], "properties": {
         "event": {"type": "string"}, "tool_name": {"type": "string"}, "hooks": {"type": "object"}}}},
    {"name": "perm_rule", "description": "Decide allow, deny, or ask from rule lists. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["tool", "arg", "allow", "deny"], "properties": {
         "tool": {"type": "string"}, "arg": {"type": "string"},
         "allow": {"type": "array", "items": {"type": "string"}},
         "deny": {"type": "array", "items": {"type": "string"}}}}},
    {"name": "tool_search_local", "description": "Search an in-memory tool catalog. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["query", "catalog"], "properties": {
         "query": {"type": "string"},
         "catalog": {"type": "array", "items": {"type": "object", "properties": {
             "name": {"type": "string"}, "description": {"type": "string"}}}}}}},
    {"name": "seat_tools", "description": "Filter a seat tool list offline. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["parent"], "properties": {
         "parent": {"type": "array", "items": {"type": "string"}},
         "tools": {"type": ["array", "null"], "items": {"type": "string"}},
         "disallowed": {"type": ["array", "null"], "items": {"type": "string"}}}}},
    {"name": "seat_gate", "description": "Allow a hand only when the caller is that seat. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["caller", "seat", "hand"], "properties": {
         "caller": {"type": "string"}, "seat": {"type": "string"}, "hand": {"type": "string"}}}},
    {"name": "layer_read", "description": "Read the first page layer list. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["out", "root"], "properties": {
         "out": {"type": "string"}, "root": {"type": "string"}}}},
    {"name": "code_refuse", "description": "Refuse a code-file kind. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["kind"], "properties": {"kind": {"type": "string"}}}},
    {"name": "mold_panel", "description": "Read one package mold's tokens. Does not publish and does not read secrets.",
     "inputSchema": {"type": "object", "required": ["mold_id"], "properties": {"mold_id": {"type": "string"}}}},
]


# ---------------------------------------------------------------- JSON-RPC

def handle(msg: dict):
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": (msg.get("params") or {}).get("protocolVersion") or "2025-06-18",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO}}
    if method and method.startswith("notifications/"):
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOL_SPECS}}
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        fn = TOOLS.get(name)
        if fn is None:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"unknown tool: {name}"}}
        try:
            result = fn(params.get("arguments") or {})
            if isinstance(result, dict) and result.get("isError"):
                return {"jsonrpc": "2.0", "id": mid, "result": {
                    "content": [{"type": "text", "text": _text(result)}], "isError": True}}
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": _text(result)}]}}
        except Exception as exc:  # tool errors become isError results, not protocol errors
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}], "isError": True}}
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}
    return None


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            print("spidercaster-mcp: bad JSON line ignored", file=sys.stderr)
            continue
        resp = handle(msg)
        if resp:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
