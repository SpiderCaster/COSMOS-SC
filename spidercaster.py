#!/usr/bin/env python3
"""SpiderCaster CLI - a copy-driven static website engine on free/nearly-free tokens.

Commands:
  init     scaffold a project (brief.md + copy/)
  build    project (or --from site.json) -> static site  [offline = 0 tokens]
  refine   patch one section of a built site (small token cost)
  check    run the built-in checks against a built site
  serve    preview a built site on localhost
  models   show the provider chain (free tiers first); --probe queries live
  sections list the section types and their data fields

Token rules: offline/rebuild = 0 tokens; AI build = 1-2 calls on the free
chain (Gemini free tier -> OpenRouter :free -> OpenWork inference); paid
models join only with --allow-paid. Every run writes a token ledger.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import check as check_mod          # noqa: E402
from lib import ingest                       # noqa: E402
from lib import ir as ir_mod                 # noqa: E402
from lib import offline as offline_mod       # noqa: E402
from lib import providers                    # noqa: E402
from lib import render                       # noqa: E402
from lib import serve as serve_mod           # noqa: E402

ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------- helpers

def write_report(site_dir: Path, *, mode: str, brief: str, ledger: providers.Ledger,
                 provider: str | None, model: str | None, files: list[str],
                 noindex: bool, warnings: list[str]) -> None:
    totals = ledger.totals()
    data = {
        "generator": "spidercaster/0.1",
        "mode": mode,
        "brief": brief[:400],
        "provider": provider,
        "model": model,
        "noindex": noindex,
        "files": files,
        "warnings": warnings,
        "tokens": totals,
        "attempts": ledger.attempts,
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (site_dir / "report.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def print_warnings(warnings: list[str]) -> None:
    for w in warnings:
        print(f"  [warn] {w}")


def copy_assets(site: dict, project_dir: Path, site_dir: Path) -> list[str]:
    """Copy referenced local images from the project into site/assets/."""
    copied = []
    for page in site.get("pages", []):
        for sec in page.get("sections", []):
            if sec["type"] != "gallery":
                continue
            for item in sec["data"].get("items", []):
                src = item.get("src") or ""
                if not src or src.startswith(("http://", "https://")):
                    continue
                origin = (project_dir / src).resolve()
                if not origin.exists():
                    continue
                dest_dir = site_dir / "assets"
                dest_dir.mkdir(exist_ok=True)
                dest = dest_dir / origin.name
                if not dest.exists() or dest.stat().st_size != origin.stat().st_size:
                    shutil.copy2(origin, dest)
                new_ref = f"assets/{origin.name}"
                if item["src"] != new_ref:
                    item["src"] = new_ref
                    copied.append(new_ref)
    return copied


def ai_site_json(copy: ingest.Copy, opts: dict, ledger: providers.Ledger) -> tuple[dict, str, str]:
    """One LLM call (plus at most one JSON-repair retry) -> raw site dict."""
    user = (
        f"BRIEF:\n{copy.brief or '(no brief file)'}\n\n"
        f"SOURCE COPY (the only allowed source of facts and wording):\n"
        f"{copy.text_digest(int(opts.get('max_copy_chars') or 24000))}\n\n"
        f"Pages wanted: {opts.get('pages') or 1}. "
        f"Return the JSON object now."
    )
    result = providers.complete(system=ir_mod.SCHEMA_PROMPT, user=user, opts=opts,
                                ledger=ledger, purpose="plan+fit")
    try:
        return providers.extract_json(result["text"]), result["provider"], result["model"]
    except ValueError as exc:
        repair = providers.complete(
            system=ir_mod.SCHEMA_PROMPT,
            user=user + f"\n\nYour previous reply was not valid JSON ({exc}). "
                        f"Return the corrected minified JSON object only.",
            opts=opts, ledger=ledger, purpose="plan+fit-repair")
        try:
            return providers.extract_json(repair["text"]), repair["provider"], repair["model"]
        except ValueError as exc2:
            raise RuntimeError(f"model reply was not valid JSON twice: {exc2}") from exc2


# ---------------------------------------------------------------- commands

def cmd_init(args) -> int:
    project = Path(args.project)
    if project.exists() and any(project.iterdir()) and not args.force:
        print(f"refusing to overwrite non-empty {project}; pass --force to add files anyway")
        return 1
    (project / "copy").mkdir(parents=True, exist_ok=True)
    brief = project / "brief.md"
    if not brief.exists() or args.force:
        brief.write_text(
            "# Brief\n\n"
            "Describe the site in plain language: what it is for, who it serves,\n"
            "the tone, and anything that must or must not appear.\n"
            "SpiderCaster never invents facts; everything on the site comes from\n"
            "this brief plus the files in copy/.\n",
            encoding="utf-8")
    readme = project / "copy" / "README.md"
    if not readme.exists() or args.force:
        readme.write_text(
            "# Copy folder\n\n"
            "Put REAL copy here as markdown (.md), plain text (.txt) or JSON (.json).\n"
            "Mapping rules used by the zero-token offline build:\n"
            "- First h1 (or first block) becomes the hero headline + lead paragraph.\n"
            "- A block with 3+ bullets becomes a features section.\n"
            "- Question paragraphs followed by answers become an faq section.\n"
            "- Bullet lines shaped like 'Name - $12' become pricing or menu rows.\n"
            "- A heading matching 'contact' becomes the contact section\n"
            "  (email/phone are picked up from the text).\n"
            "- Everything else becomes about-style text sections.\n\n"
            "Images: list local files in ../assets.json as {\"images\": {\"name\": \"path\"}}.\n"
            "External image URLs are dropped (download-only rule; no hotlinking).\n",
            encoding="utf-8")
    print(f"project ready: {project}")
    print("  next: fill brief.md and copy/, then:")
    print(f"    python spidercaster.py build {project} --offline")
    return 0


def cmd_build(args) -> int:
    ledger = providers.Ledger()
    warnings: list[str] = []
    noindex = not args.indexable
    opts = {
        "provider": args.provider, "model": args.model, "allow_paid": args.allow_paid,
        "max_tokens": args.max_tokens, "max_copy_chars": args.max_copy_chars,
        "template": args.template, "dark": None if args.dark is None else args.dark,
        "pages": args.pages, "brief": "", "brand": args.brand,
    }

    if args.site_json:
        src = Path(args.site_json)
        raw = json.loads(src.read_text(encoding="utf-8"))
        project_dir = src.parent.parent
        mode = "rebuild"
        provider = model = None
        brief = raw.get("brief", "")
        opts["brief"] = brief
        site = ir_mod.normalize_site(raw, opts)
    else:
        project_dir = Path(args.project)
        copy = ingest.load_project(project_dir)
        warnings.extend(copy.warnings)
        brief = copy.brief
        opts["brief"] = brief
        if args.offline:
            raw = offline_mod.plan_offline(copy, opts)
            mode, provider, model = "offline", None, None
        else:
            try:
                raw, provider, model = ai_site_json(copy, opts, ledger)
                mode = "ai"
            except (RuntimeError, SystemExit) as exc:
                if args.no_fallback:
                    raise
                print(f"  [warn] AI build failed -> offline fallback ({exc})")
                raw = offline_mod.plan_offline(copy, opts)
                mode, provider, model = "offline-fallback", None, None
        site = ir_mod.normalize_site(raw, opts)

    # output dir
    if args.out:
        out = Path(args.out)
    else:
        slug = ir_mod.slugify(site["meta"]["title"]) or "site"
        out = ROOT / "sites" / slug
    out.mkdir(parents=True, exist_ok=True)

    copied = copy_assets(site, project_dir if project_dir.exists() else out, out)
    if copied:
        warnings.append(f"copied {len(copied)} asset(s) to assets/")

    pages = render.assemble(site, noindex=noindex)
    for p in pages:
        (out / p["file"]).write_text(p["html"], encoding="utf-8")
    (out / "site.json").write_text(json.dumps(site, indent=2), encoding="utf-8")
    write_report(out, mode=mode, brief=brief, ledger=ledger, provider=provider, model=model,
                 files=[p["file"] for p in pages], noindex=noindex, warnings=warnings)

    print(f"built {out} (mode: {mode}"
          + (f", {provider}/{model}" if provider else "") + ")")
    print(f"  pages: {', '.join(p['file'] for p in pages)}")
    print(f"  tokens: {ledger.summary_line()}")
    print(f"  index: {'NOINDEX (default; pass --indexable to flip)' if noindex else 'indexable'}")
    print_warnings(warnings)
    print(f"  next: python spidercaster.py check {out}")
    print(f"        python spidercaster.py serve {out}")
    return 0


def cmd_refine(args) -> int:
    site_dir = Path(args.site)
    site_json = site_dir / "site.json"
    if not site_json.exists():
        print(f"no site.json in {site_dir}; run a build first")
        return 1
    site = json.loads(site_json.read_text(encoding="utf-8"))
    ledger = providers.Ledger()
    opts = {"provider": args.provider, "model": args.model, "allow_paid": args.allow_paid,
            "max_tokens": args.max_tokens}

    page = site["pages"][0]
    sections = page["sections"]

    # offline refine: theme flips only
    if args.offline:
        text = args.instruction.lower()
        changed = []
        for tpl in ir_mod.TEMPLATES:
            if tpl in text:
                site["theme"]["template"] = tpl
                changed.append(f"template={tpl}")
        if "light" in text:
            site["theme"]["dark"] = False
            changed.append("dark=False")
        elif "dark" in text:
            site["theme"]["dark"] = True
            changed.append("dark=True")
        hexes = [c for c in args.instruction.split() if ir_mod.hex6(c)]
        if hexes:
            site["theme"]["accent"] = ir_mod.hex6(hexes[0])
            changed.append(f"accent={site['theme']['accent']}")
        if not changed:
            print("offline refine supports theme flips only (template/dark/light/#hex); "
                  "run without --offline for copy edits")
            return 1
        mode = "refine-offline"
        provider = model = None
    else:
        # pick target section
        if args.section:
            target = next((s for s in sections if s["id"] == args.section), None)
            if target is None:
                print(f"section '{args.section}' not found; known: " +
                      ", ".join(s["id"] for s in sections))
                return 1
        else:
            words = [w for w in "".join(ch if ch.isalnum() else " " for ch in args.instruction.lower()).split() if len(w) > 2]
            def score(sec):
                blob = json.dumps(sec).lower()
                return sum(1 for w in words if w in blob)
            ranked = sorted(sections, key=score, reverse=True)
            target = ranked[0] if score(ranked[0]) > 0 else None
            if target is None:
                print("could not match the instruction to a section; pass --section <id>. "
                      "known: " + ", ".join(f"{s['id']}({s['type']})" for s in sections))
                return 1
        user = (f"SITE: {site['meta']['title']}\n"
                f"SECTION JSON:\n{json.dumps(target, ensure_ascii=False)}\n\n"
                f"INSTRUCTION: {args.instruction}\n\nReturn the replacement section JSON now.")
        try:
            result = providers.complete(system=ir_mod.REFINE_PROMPT, user=user, opts=opts,
                                        ledger=ledger, purpose="refine", temperature=0.6)
        except RuntimeError as exc:
            print(f"refine needs a working provider; all failed:\n{exc}")
            print("theme-only edits work with --offline at zero tokens.")
            return 1
        try:
            patched = providers.extract_json(result["text"])
        except ValueError as exc:
            print(f"refine reply was not valid JSON: {exc}")
            return 1
        fixed = ir_mod.normalize_section(
            {"id": target["id"], "type": target["type"], "data": patched.get("data", {})},
            {s["id"] for s in sections})
        if fixed is None:
            print("refine reply had an unknown section type; site unchanged")
            return 1
        sections[sections.index(target)] = fixed
        mode = "refine"
        provider, model = result["provider"], result["model"]

    # backup + rewrite + rebuild
    shutil.copy2(site_json, site_dir / "site.json.bak")
    site = ir_mod.normalize_site(site, {"brief": site.get("brief", "")})
    noindex = 'name="robots" content="noindex' in (site_dir / "index.html").read_text(encoding="utf-8") \
        if (site_dir / "index.html").exists() else True
    (site_dir / "site.json").write_text(json.dumps(site, indent=2), encoding="utf-8")
    pages = render.assemble(site, noindex=noindex)
    for p in pages:
        (site_dir / p["file"]).write_text(p["html"], encoding="utf-8")
    prev = {}
    rp = site_dir / "report.json"
    if rp.exists():
        try:
            prev = json.loads(rp.read_text(encoding="utf-8"))
        except ValueError:
            prev = {}
    write_report(site_dir, mode=mode, brief=prev.get("brief", ""), ledger=ledger,
                 provider=provider, model=model, files=[p["file"] for p in pages],
                 noindex=noindex, warnings=prev.get("warnings", []))
    print(f"refined {site_dir} ({mode}"
          + (f", {provider}/{model}" if provider else "") + ")")
    print(f"  tokens: {ledger.summary_line()}")
    print(f"  backup: site.json.bak")
    return 0


def cmd_check(args) -> int:
    site_dir = Path(args.site)
    expect = True if args.expect_noindex else (False if args.expect_indexable else None)
    print(f"checking {site_dir}")
    rep = check_mod.check_site(site_dir, expect)
    c = rep.counts()
    print(f"result: {c['PASS']} pass / {c['FAIL']} fail / {c['WARN']} warn / {c['SKIP']} skip")
    return 0 if rep.ok() else 1


def cmd_serve(args) -> int:
    site_dir = Path(args.site)
    if not (site_dir / "index.html").exists():
        print(f"no index.html in {site_dir}; run a build first")
        return 1
    httpd, port = serve_mod.serve(site_dir, args.port)
    print(f"preview: http://localhost:{port}  (serving {site_dir}; Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


def cmd_models(args) -> int:
    print("provider chain (free tiers first; paid only with --allow-paid):")
    for pid in ["gemini", "openrouter", "openwork"]:
        p = providers.PROVIDERS[pid]
        status = "configured" if p.configured() else "not configured"
        models = ", ".join(p.models) or "(no models set)"
        print(f"  {pid:11s} {status:15s} {p.label}")
        print(f"              models: {models}")
    if args.probe:
        for pid in ["gemini", "openrouter"]:
            p = providers.PROVIDERS[pid]
            if not p.configured():
                continue
            print(f"probing {pid} ...")
            try:
                names = p.probe()
                print(f"  {len(names)} models reachable; first few: {', '.join(names[:6])}")
            except Exception as exc:
                print(f"  probe failed: {exc}")
    return 0


def cmd_wallets(args) -> int:
    """Fingerprint map of recorded Google wallets. last4 + short SHA-256
    fingerprint ONLY - never a key value. For FIFO draw planning."""
    def meta(text: str):
        t = text.strip()
        if not t:
            return None
        return {"len": len(t), "last4": t[-4:],
                "fp": hashlib.sha256(t.encode("utf-8")).hexdigest()[:6]}

    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    env_meta = meta(env_key) if env_key else None
    if env_meta:
        print(f"env GEMINI_API_KEY : len={env_meta['len']} last4={env_meta['last4']} fp={env_meta['fp']}")
    key_file = os.environ.get("FORGE_GEMINI_KEY_FILE")
    draw_fp = None
    if key_file:
        m = meta(Path(key_file).read_text(encoding="utf-8"))
        draw_fp = m["fp"] if m else None
        print(f"active draw source : {key_file} (last4={m['last4']} fp={m['fp']})")
    elif env_meta:
        draw_fp = env_meta["fp"]

    secrets_dir = Path(args.secrets_dir)
    if not secrets_dir.exists():
        print(f"(no wallet dir at {secrets_dir}; pass --secrets-dir)")
        return 0
    print(f"recorded wallets in {secrets_dir}:")
    for p in sorted(list(secrets_dir.glob("vertex_*_key.txt")) + list(secrets_dir.glob("vertex_key.txt"))):
        try:
            m = meta(p.read_text(encoding="utf-8"))
        except OSError as exc:
            print(f"  {p.name}: unreadable ({exc})")
            continue
        if not m:
            continue
        active = draw_fp is not None and m["fp"] == draw_fp
        tag = "  <-- ACTIVE DRAW" if active else ""
        print(f"  {p.name:36s} len={m['len']} last4={m['last4']} fp={m['fp']}{tag}")
    print("note: registration/expiry dates are not stored here; read them per")
    print("account in Google console > Billing > Credits (each row shows its window).")
    return 0


def cmd_sections(_args) -> int:
    print("section types (data fields):")
    for k, v in ir_mod.SECTION_DOCS.items():
        print(f"  {k:12s} {v}")
    return 0


# ---------------------------------------------------------------- parser

def add_provider_opts(p: argparse.ArgumentParser) -> None:
    p.add_argument("--provider", choices=list(providers.PROVIDERS), help="force one provider")
    p.add_argument("--model", help="force one model id")
    p.add_argument("--allow-paid", action="store_true", help="allow paid OpenRouter models")
    p.add_argument("--max-tokens", type=int, default=8192, help="max output tokens per call")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="spidercaster", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="scaffold a project")
    p.add_argument("project")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("build", help="build a site (project dir or --from site.json)")
    p.add_argument("project", nargs="?", help="project directory")
    p.add_argument("--from", dest="site_json", help="rebuild from an existing site.json (0 tokens)")
    p.add_argument("--out", help="output site dir (default sites/<slug>)")
    p.add_argument("--offline", action="store_true", help="zero-token deterministic build")
    p.add_argument("--no-fallback", action="store_true", help="fail instead of falling back offline")
    p.add_argument("--template", choices=ir_mod.TEMPLATES)
    p.add_argument("--dark", dest="dark", action="store_true", default=None)
    p.add_argument("--light", dest="dark", action="store_false")
    p.add_argument("--pages", type=int, default=1, help="page count hint for the AI planner")
    p.add_argument("--brand", help="brand/title override")
    p.add_argument("--indexable", action="store_true",
                   help="omit robots noindex (default is noindex until approved)")
    p.add_argument("--max-copy-chars", type=int, default=24000)
    add_provider_opts(p)
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("refine", help="patch one section of a built site")
    p.add_argument("site", help="built site dir")
    p.add_argument("instruction")
    p.add_argument("--section", help="target section id (default: auto-match)")
    p.add_argument("--offline", action="store_true", help="theme flips only, 0 tokens")
    add_provider_opts(p)
    p.set_defaults(fn=cmd_refine)

    p = sub.add_parser("check", help="run built-in checks")
    p.add_argument("site")
    p.add_argument("--expect-noindex", action="store_true")
    p.add_argument("--expect-indexable", action="store_true")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("serve", help="preview a built site")
    p.add_argument("site")
    p.add_argument("--port", type=int, default=4173)
    p.set_defaults(fn=cmd_serve)

    p = sub.add_parser("models", help="show provider chain")
    p.add_argument("--probe", action="store_true", help="query live model lists")
    p.set_defaults(fn=cmd_models)

    p = sub.add_parser("wallets", help="fingerprint map of recorded Google wallets (last4 only)")
    p.add_argument("--secrets-dir", default=r"V:\Research4\.secrets")
    p.set_defaults(fn=cmd_wallets)

    p = sub.add_parser("sections", help="list section types")
    p.set_defaults(fn=cmd_sections)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
