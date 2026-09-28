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

SURFACE_ROOT = Path(os.environ.get("SPIDERCASTER_SURFACE_ROOT") or (ROOT / "sites"))
SECRETS_DIR = Path(os.environ.get("SPIDERCASTER_SECRETS_DIR") or r"V:\Research4\.secrets")
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
        for p in sorted(list(sd.glob("vertex_*_key.txt")) + list(sd.glob("vertex_key.txt"))):
            m = _key_meta(p.read_text(encoding="utf-8"))
            if m:
                wallets.append({"file": p.name, **m})
    out["wallets"] = wallets
    out["note"] = "last4 + fingerprint only; expiry = registration + 90d; dates live in console > Billing > Credits"
    return out


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
