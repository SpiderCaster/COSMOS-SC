#!/usr/bin/env python3
"""SpiderCaster CLI - a copy-driven static website engine on free/nearly-free tokens.

Commands:
  init     scaffold a project (brief.md + copy/)
  build    project (or --from site.json) -> static site  [offline = 0 tokens]
  compose  offline compose of one project (0 tokens, no publish)
  refine   patch one section of a built site (small token cost)
  check    run the built-in checks against a built site
  visit    static visit check of a built site
  serve    preview a built site on localhost
  start    first run: doctor + demo site + studio desk in browser (0 tokens)
  studio   localhost desk for plan, paint, check, and preview (does not publish)
  models   show the provider chain (free tiers first); --probe queries live
  sections list the section types and their data fields
  library  vendor vault index, molds we made, live-use ledger
  crew     run the seven hands on one project (does not publish)
  ui       stdio face: composer + ticket/ledger (propose-only, 0-token default)
  doctor   report python, molds, frames, seats, and hand order
  shipcheck say whether the app is ship-ready
  seat     print one seat pack
  parts    index every part manifest; assemble one site that uses them
  tools    list catalog rows; apply one built part onto a page

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
from lib.crew import ROLES, run_job          # noqa: E402
from lib.doctor import report as doctor_report  # noqa: E402
from lib.library import Library, LibraryError  # noqa: E402
from lib.seatpack import pack as seat_pack   # noqa: E402
from lib.shipcheck import main as shipcheck_main  # noqa: E402

_HOME = os.environ.get("SPIDERCASTER_HOME", "").strip()
ROOT = Path(_HOME).resolve() if _HOME else Path(__file__).resolve().parent


# ---------------------------------------------------------------- helpers

def build_stamp() -> str | None:
    """Timestamp for report.json, or None so the output stays byte-reproducible.

    SOURCE_DATE_EPOCH (reproducible-builds.org) set -> that instant, in UTC.
    SPIDERCASTER_STAMP_BUILD=1 -> wall clock (opt in; breaks byte-identical rebuilds).
    Neither -> no built_at key at all.
    """
    epoch = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    if epoch:
        try:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(epoch)))
        except (ValueError, OverflowError, OSError):
            pass
    if os.environ.get("SPIDERCASTER_STAMP_BUILD") == "1":
        return time.strftime("%Y-%m-%d %H:%M:%S")
    return None


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
    }
    stamp = build_stamp()
    if stamp:
        data["built_at"] = stamp
    (site_dir / "report.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def print_warnings(warnings: list[str]) -> None:
    for w in warnings:
        print(f"  [warn] {w}")


def copy_assets(site: dict, project_dir: Path, site_dir: Path) -> list[str]:
    """Copy referenced local images from the project into site/assets/."""
    copied = []
    for page in site.get("pages", []):
        for sec in page.get("sections", []):
            if sec.get("type") == "hero":
                d = sec.get("data") if isinstance(sec.get("data"), dict) else {}
                src = d.get("image") or ""
                if not src:
                    for ext in (".png", ".jpg", ".jpeg", ".webp"):
                        cand = project_dir / f"assets/hero{ext}"
                        if cand.is_file():
                            src = f"assets/hero{ext}"
                            d["image"] = src
                            break
                if src and not src.startswith(("http://", "https://", "//")):
                    origin = (project_dir / src).resolve()
                    if origin.is_file():
                        dest_dir = site_dir / "assets"
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        dest = dest_dir / origin.name
                        if not dest.exists() or dest.stat().st_size != origin.stat().st_size:
                            shutil.copy2(origin, dest)
                        new_ref = f"assets/{origin.name}"
                        d["image"] = new_ref
                        copied.append(new_ref)
            elif sec.get("type") == "gallery":
                for item in sec.get("data", {}).get("items", []):
                    src = item.get("src") or ""
                    if not src or src.startswith(("http://", "https://")):
                        continue
                    origin = (project_dir / src).resolve()
                    if not origin.exists():
                        continue
                    dest_dir = site_dir / "assets"
                    dest_dir.mkdir(parents=True, exist_ok=True)
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


def _compose_default_out(project: Path) -> Path:
    return ROOT / "sites" / f"{Path(project).name}-compose"


def _run_compose(
    project: Path,
    out: Path | None,
    frame_id: str,
    mold_id: str,
    plan_only: bool = False,
    accepted: str = "",
) -> int:
    """Offline compose. Prints the compose_project result. Does not write the ledger."""
    from lib.compose import compose_project

    project = Path(project)
    dest = Path(out) if out else _compose_default_out(project)
    if plan_only and accepted:
        print("compose --plan does not take --structure")
        return 1
    result = compose_project(
        project,
        dest,
        frame_id or "",
        mold_id or "",
        plan_only=plan_only,
        accepted=Path(accepted) if accepted else None,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    if not isinstance(result, dict) or not result.get("ok"):
        return 1
    return 0


def _load_apply_mold(mold_id: str) -> dict:
    """Read library/molds/<id>.json. Returns palette and type_lead only."""
    mold_id = str(mold_id or "").strip()
    if not mold_id or "/" in mold_id or "\\" in mold_id or ".." in mold_id:
        raise ValueError(f"bad mold id: {mold_id}")
    path = ROOT / "library" / "molds" / f"{mold_id}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"mold missing: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"mold missing: {path}")
    return {
        "palette": data.get("palette") or "",
        "type_lead": data.get("type_lead") or "",
    }


def cmd_build(args) -> int:
    if getattr(args, "dry_run", False) and getattr(args, "compose", False):
        print("build --dry-run does not combine with --compose; use compose --plan for a 0-token preview")
        return 1
    if getattr(args, "dry_run", False) and not getattr(args, "site_json", None):
        # 0-token guarantee: a dry-run preview never calls providers.
        args.offline = True
    if getattr(args, "compose", False):
        if getattr(args, "site_json", None) or not getattr(args, "project", None):
            print("build --compose needs a project directory, not --from")
            return 1
        out = Path(args.out) if args.out else None
        return _run_compose(
            Path(args.project), out,
            getattr(args, "frame", "") or "",
            getattr(args, "mold", "") or "",
            plan_only=bool(getattr(args, "plan", False)),
            accepted=getattr(args, "structure", "") or "",
        )

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
        # --from re-read: cited spans must still resolve against copy/.
        # Legacy site.json without citations passes through, as does a
        # layout with no copy/ dir next to the site (nothing to re-read).
        from lib import copy_schema as _gaps
        _copy_base = None
        for _cand in (src.parent / "copy", src.parent.parent / "copy"):
            if _cand.is_dir():
                _copy_base = _cand.parent
                break
        if _copy_base is not None:
            cite_gaps = _gaps.verify_citations(site, _copy_base)
            if cite_gaps:
                print(f"FAIL gap {cite_gaps[0]} (citation no longer resolves in copy/)",
                      file=sys.stderr)
                return 1
        missing = _gaps.validate_site(site)
        if missing:
            print(f"FAIL gap {missing[0]}", file=sys.stderr)
            return 1
    else:
        project_dir = Path(args.project)
        if getattr(args, "imagine", False):
            hero_target = project_dir / "assets" / "hero.png"
            if not hero_target.exists():
                from lib.imagine import ImagineError, generate
                prompt = (
                    f"Editorial still life photograph for {project_dir.name}, no text, no logo, no watermark, "
                    "warm natural lighting, subject on right third, quiet space on left, "
                    "calm craftsmanship. Not a product ad."
                )
                try:
                    print(f"  [imagine] generating local hero image for {project_dir.name}...")
                    generate(prompt, hero_target, aspect_ratio="16:9", quality="low")
                    print(f"  [imagine] saved {hero_target}")
                except (ImagineError, OSError, ValueError) as exc:
                    print(f"  [imagine] skipped ({exc})")
        copy = ingest.load_project(project_dir)
        warnings.extend(copy.warnings)
        brief = copy.brief
        opts["brief"] = brief
        if args.offline:
            try:
                raw = offline_mod.plan_offline(copy, opts)
            except SystemExit as exc:
                print(str(exc) or "FAIL gap hero.headline", file=sys.stderr)
                return 1
            mode, provider, model = "offline", None, None
        else:
            try:
                raw, provider, model = ai_site_json(copy, opts, ledger)
                mode = "ai"
            except (RuntimeError, SystemExit) as exc:
                if args.no_fallback:
                    raise
                print(f"  [warn] AI build failed -> offline fallback ({exc})")
                try:
                    raw = offline_mod.plan_offline(copy, opts)
                except SystemExit as exc2:
                    print(str(exc2) or "FAIL gap hero.headline", file=sys.stderr)
                    return 1
                mode, provider, model = "offline-fallback", None, None
        site = ir_mod.normalize_site(raw, opts)
        # Gap gate: mandatory miss is FAIL with no HTML emitted.
        # plan_offline raises GapError for missing hero/integrity gaps, but
        # the AI path (and hand-edited raw) can still arrive here hollow.
        from lib import copy_schema as _gaps
        try:
            _gaps.raise_first_gap(site)
        except SystemExit as exc:
            print(str(exc), file=sys.stderr)
            return 1

    # output dir
    if args.out:
        out = Path(args.out)
    else:
        slug = ir_mod.slugify(site["meta"]["title"]) or "site"
        out = ROOT / "sites" / slug
    if getattr(args, "dry_run", False):
        from lib import attempts as _attempts

        _old = None
        if (out / "site.json").is_file():
            try:
                _old = json.loads((out / "site.json").read_text(encoding="utf-8"))
            except ValueError:
                _old = None
        print(_attempts.dry_run_diff(_old, site, label=str(out)), end="")
        print("  (sitemap stage diff lands with lib/sitemap.py; IR layer above)")
        return 0
    out.mkdir(parents=True, exist_ok=True)
    if mode == "ai" and (out / "site.json").is_file():
        from lib import attempts as _attempts

        try:
            _manifest = _attempts.snapshot(out, reason="ai-plan")
            print(f"  attempt: {_manifest['id']} ({len(_manifest['files'])} files)")
        except (ValueError, OSError) as exc:
            print(f"  [warn] attempt snapshot skipped: {exc}")

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
    from lib.seo_pack import SeoPackError, write_pack
    try:
        pack = write_pack(out, indexable=not noindex, host=getattr(args, "host", "") or "")
    except SeoPackError as exc:
        print(f"  [warn] {exc}")
    else:
        print(f"  robots: {pack['robots']}")
        if pack["sitemap"]:
            print(f"  sitemap: {pack['sitemap']}")
    print(f"  next: python spidercaster.py check {out}")
    print(f"        python spidercaster.py serve {out}")
    return 0


def cmd_compose(args) -> int:
    out = Path(args.out) if args.out else None
    return _run_compose(
        Path(args.project), out,
        getattr(args, "frame", "") or "",
        getattr(args, "mold", "") or "",
        plan_only=bool(getattr(args, "plan", False)),
        accepted=getattr(args, "structure", "") or "",
    )


def cmd_refine(args) -> int:
    site_dir = Path(args.site)
    if getattr(args, "rollback", ""):
        from lib import attempts as _attempts

        try:
            manifest = _attempts.rollback(site_dir, str(args.rollback))
        except (ValueError, OSError) as exc:
            print(f"rollback failed: {exc}")
            return 1
        print(f"rolled back {site_dir} to attempt {manifest['id']} "
              f"({len(manifest.get('restored', []))} files, logged)")
        return 0
    site_json = site_dir / "site.json"
    if getattr(args, "dry_run", False) and not getattr(args, "offline", False):
        print("refine --dry-run previews offline theme flips only at 0 tokens; "
              "AI refine would spend tokens: refusing")
        return 1
    if not site_json.exists():
        print(f"no site.json in {site_dir}; run a build first")
        return 1
    site = json.loads(site_json.read_text(encoding="utf-8"))
    before_json = json.dumps(site, sort_keys=True)
    if not getattr(args, "dry_run", False):
        try:
            from lib import attempts as _attempts

            _manifest = _attempts.snapshot(site_dir, reason="refine")
            print(f"  attempt: {_manifest['id']} ({len(_manifest['files'])} files)")
        except (ValueError, OSError) as exc:
            print(f"  [warn] attempt snapshot skipped: {exc}")
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

    if getattr(args, "dry_run", False):
        if not args.offline:
            print("refine --dry-run previews offline theme flips only at 0 tokens; "
                  "AI refine would spend tokens: refusing")
            return 1
        from lib import attempts as _attempts

        _old = json.loads(before_json)
        print(_attempts.dry_run_diff(_old, site, label=str(site_dir)), end="")
        return 0
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
    project = getattr(args, "project", None)
    if project:
        from lib.copy_pack import project_copy_text
        rep = check_mod.check_site(
            site_dir, expect, copy_text=project_copy_text(Path(project)),
        )
    else:
        rep = check_mod.check_site(site_dir, expect)
    c = rep.counts()
    print(f"result: {c['PASS']} pass / {c['FAIL']} fail / {c['WARN']} warn / {c['SKIP']} skip")
    return 0 if rep.ok() else 1


def cmd_visit(args) -> int:
    from lib.visit_check import visit_site
    result = visit_site(Path(args.site))
    print(f"mode: {result.get('mode', '')}")
    for failure in result.get("failures") or []:
        if isinstance(failure, dict):
            print(f"  {failure.get('code', '')}: {failure.get('detail', '')}")
        else:
            print(f"  {failure}")
    return 0 if result.get("ok") else 1


def cmd_start(args) -> int:
    """First run for a cold machine: doctor + demo site + studio desk.

    0 tokens, localhost only, never publishes. Steps:
      1. doctor gate (fail fast with the JSON error list);
      2. ensure an offline demo site exists (builds demo-local if missing);
      3. serve the studio desk and open it in the default browser.
    The desk IS the engaging face (plan / paint / check / preview rooms,
    crew hands); the stdio composer stays one `ui` command away.
    --dry-run prints the exact steps and runs doctor only (no writes,
    no server, no browser) so a cold install can be rehearsed.
    """
    import argparse as _ap
    import webbrowser as _wb

    project = getattr(args, "project", "") or "demo-local"
    port = int(getattr(args, "port", 4180) or 4180)
    dry = bool(getattr(args, "dry_run", False))
    no_browser = bool(getattr(args, "no_browser", False))
    no_build = bool(getattr(args, "no_build", False))

    if dry:
        print("start --dry-run (no writes, no server, no browser):")
        print(f"  1. doctor gate (python, molds, frames, seats, hands)")
        print(f"  2. ensure offline demo site from project {project!r} (0 tokens)")
        print(f"  3. serve studio desk on http://127.0.0.1:{port}/ and open browser")
        print(f"  live agent: desk rooms (plan/check/preview/crew) + `spidercaster.py ui`")
    rep = doctor_report()
    if not rep.get("ok"):
        print(f"doctor FAIL: {rep.get('errors')}")
        if dry:
            print("(dry-run stops here: fix the checkout, then re-run without --dry-run)")
        return 1
    if dry:
        print("doctor ok")
        return 0

    print(f"doctor ok (python {rep.get('python')}, "
          f"{len(rep.get('molds', []))} molds, {rep.get('frames')} frames)")

    if not no_build:
        demo_proj = Path(project)
        if not demo_proj.is_dir():
            cand = ROOT / "projects" / Path(project).name
            if cand.is_dir():
                demo_proj = cand
        out = ROOT / "sites" / demo_proj.name
        if not (out / "index.html").is_file():
            print(f"building offline demo site from {demo_proj} -> {out} (0 tokens) ...")
            ns = _ap.Namespace(project=str(demo_proj), site_json=None, out=str(out),
                               offline=True, compose=False, dry_run=False,
                               frame="", mold="", plan=None, structure="",
                               indexable=False, host="", provider=None, model=None,
                               allow_paid=False, max_tokens=8192, max_copy_chars=24000,
                               template=None, dark=None, pages=1, brand=None,
                               no_fallback=True)
            code = cmd_build(ns)
            if code != 0:
                print("demo build failed; fix copy/ gaps, then re-run start")
                return code
        else:
            print(f"demo site ready: {out}")
    else:
        print("(skipping demo build: --no-build)")

    from lib.studio import serve_studio

    httpd, port = serve_studio(port=port)
    url = f"http://127.0.0.1:{port}/"
    print(f"studio {url}")
    print("Engaging face: Desk/Plan/Preview/Check rooms. Live agent: Crew room + `spidercaster.py ui`.")
    print("noindex. This does not publish. Ctrl+C to stop.")
    if not no_browser:
        try:
            _wb.open(url, new=2)
        except Exception as exc:  # browser opener is best-effort only
            print(f"  [warn] could not open browser: {exc}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


def cmd_studio(args) -> int:
    from lib.studio import serve_studio

    httpd, port = serve_studio(port=args.port)
    print(f"studio http://127.0.0.1:{port}/")
    print("noindex. This does not publish.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


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


# ---------------------------------------------------------------- library + crew

PACKAGE_LIBRARY = ROOT / "library"
DEFAULT_VAULT = Path(os.environ.get("SPIDERCASTER_VAULT") or r"V:\streams\webdev\vendor-vault")
DEFAULT_OWP = Path(r"V:\streams\webdev\templates\owp\_catalog.json")
DEFAULT_GP = Path(r"V:\streams\webdev\templates\gp\_catalog.json")
DEFAULT_FRAMES = Path(r"V:\streams\webdev\templates\owp\core-frames")


def _library(args) -> Library:
    vault = Path(getattr(args, "vault", None) or DEFAULT_VAULT)
    return Library(PACKAGE_LIBRARY, vault)


def cmd_library(args) -> int:
    lib = _library(args)
    if args.library_cmd == "selftest":
        import tempfile
        from lib.library import selftest as library_selftest
        with tempfile.TemporaryDirectory() as tmp:
            return library_selftest(Path(tmp))
    if args.library_cmd == "index":
        summary = lib.index_catalogs(Path(args.owp), Path(args.gp), Path(args.frames))
        print(f"vault indexed: {summary['frames']} frame name(s)")
        print(f"  {summary['vault']}")
        print("  photos and theme files are not downloaded by this command")
        return 0
    if args.library_cmd == "list":
        molds = lib.list_molds()
        frames = lib.frames().get("frames", [])
        print(f"molds (package): {len(molds)}")
        for mold in molds:
            print(f"  {mold['id']}  {mold['origin']}  {mold['type_lead']}  {mold['nav']}")
        from lib.frames import list_frames
        section_frames = list_frames()
        print(f"section frames (package): {len(section_frames)}")
        for frame in section_frames:
            print(f"  {frame['id']}  {frame['nav']}  {frame['template']}")
        print(f"vendor frames (vault, not packaged): {len(frames)}")
        return 0
    if args.library_cmd == "mold":
        try:
            mold = lib.save_mold({
                "id": args.id, "origin": args.origin, "parents": args.parent or [],
                "palette": args.palette, "type_lead": args.type_lead, "nav": args.nav,
                "template": args.template, "sections": args.section or [],
                "note": args.note or "",
            })
        except LibraryError as exc:
            print(f"mold refused: {exc}")
            return 2
        print(f"mold saved: {mold['id']} ({mold['origin']})")
        return 0
    if args.library_cmd == "bind":
        site_dir = None
        if args.live:
            raw_out = str(getattr(args, "out", "") or "").strip()
            if raw_out:
                site_dir = Path(raw_out)
            else:
                site_dir = ROOT / "sites" / ir_mod.slugify(args.site)
        try:
            row = lib.bind(
                args.site,
                args.mold,
                vendor_frame=args.vendor,
                live=args.live,
                site_dir=site_dir,
            )
        except LibraryError as exc:
            print(f"bind refused: {exc}")
            return 2
        flag = "live" if row["live"] else "draft"
        print(f"bound {row['site']} -> {row['mold']} ({flag})")
        return 0
    if args.library_cmd == "accept":
        try:
            row = lib.accept_snapshot(args.frame, Path(args.snapshot))
        except LibraryError as exc:
            print(f"snapshot refused: {exc}")
            return 2
        print(f"vault snapshot {row['id']}: {row['photos']} photo(s)")
        return 0
    print("library command missing")
    return 2


def cmd_image(args) -> int:
    from lib.imagine import ImagineError, generate
    dest = Path(args.out)
    try:
        receipt = generate(
            args.prompt, dest,
            provider=args.provider, model=args.model or "",
            aspect_ratio=args.aspect, quality=args.quality,
        )
    except ImagineError as exc:
        print(f"image refused: {exc}")
        return 2
    print(f"saved {dest if dest.suffix else dest.with_suffix('.png')}")
    print(f"  {receipt['provider']}/{receipt['model']}  {receipt['bytes']} bytes")
    print("  provider URL was not stored")
    return 0


def cmd_graphics(args) -> int:
    from lib import graphics_engine as ge

    subcmd = getattr(args, "graphics_cmd", None)
    if subcmd == "selftest":
        return ge.selftest()

    if subcmd == "vector":
        kind = getattr(args, "kind", "browser")
        brand = getattr(args, "brand", "Studio")
        svg = ge.generate_vector_scene(kind=kind, brand=brand)
        out_path = getattr(args, "out", None)
        if out_path:
            p = Path(out_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(svg, encoding="utf-8")
            print(f"saved vector scene ({kind}): {p}")
        else:
            print(svg)
        return 0

    if subcmd == "audit":
        project_dir = Path(args.project)
        report = ge.audit_project_assets(project_dir)
        print(f"assets audit for {project_dir}: {report['count']} file(s)")
        for a in report["assets"]:
            status = "PASS" if a["ok"] else "FAIL"
            print(f"  [{status}] {a['file']}: {a['width']}x{a['height']}, {a['bytes']}B, luma={a['luma']}")
        return 0 if report["ok"] else 1

    if subcmd == "optimize":
        project_dir = Path(args.project)
        assets_dir = project_dir / "assets"
        if not assets_dir.is_dir():
            print(f"no assets/ directory under {project_dir}")
            return 1
        count = 0
        for p in assets_dir.iterdir():
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                if ge.normalize_image_luma_and_weight(p):
                    count += 1
        print(f"optimized {count} asset(s) under {assets_dir}")
        return 0

    if subcmd == "imagine":
        project_dir = Path(args.project)
        slots = [s.strip() for s in getattr(args, "slots", "hero").split(",") if s.strip()]
        receipts = ge.imagine_project_slots(
            project_dir,
            slots=slots,
            provider=getattr(args, "provider", "xai"),
            model=getattr(args, "model", "") or "",
        )
        print(f"imagine for {project_dir}: {len(receipts)} slot(s)")
        for rc in receipts:
            if "error" in rc:
                print(f"  [FAIL] {rc['slot']}: {rc['error']}")
            else:
                print(f"  [PASS] {rc['file']}: {rc['provider']}/{rc['model']} ({rc['bytes']} bytes)")
        return 0

    print("graphics subcommand required: vector | audit | optimize | imagine | selftest")
    return 2


def cmd_crew(args) -> int:
    if args.crew_cmd == "roles":
        for role in ROLES:
            hands = ", ".join(role["hands"])
            print(f"{role['n']}. {role['label']}")
            print(f"   hands: {hands}")
            print(f"   does not: {role['does_not']}")
        return 0
    if args.crew_cmd == "selftest":
        import tempfile
        from lib.crew import selftest as crew_selftest
        with tempfile.TemporaryDirectory() as tmp:
            return crew_selftest(Path(tmp), ROOT / "projects" / "demo-local")
    if args.crew_cmd == "run":
        lib = _library(args)
        mold_id = args.mold
        if args.scratch:
            mold_id = args.mold or ir_mod.slugify(args.site)
            try:
                lib.save_mold({
                    "id": mold_id, "origin": "scratch",
                    "palette": args.palette, "type_lead": args.type_lead, "nav": args.nav,
                    "template": args.template, "note": "scratch mold for this site",
                })
            except LibraryError as exc:
                print(f"scratch mold refused: {exc}")
                return 2
        if not mold_id:
            print("pass --mold or --scratch")
            return 2
        out = Path(args.out) if args.out else ROOT / "sites" / ir_mod.slugify(args.site)
        ticket = run_job(
            lib, Path(args.project), args.site, out, mold_id,
            frame_id=getattr(args, "frame", "") or "",
        )
        for hand in ticket["hands"]:
            print(f"  [{hand['status']}] {hand['role']}: {hand['detail']}")
        print(ticket["publish"])
        print(f"  ticket: {out / 'crew-ticket.json'}")
        return 0 if ticket["ok"] else 1
    print("crew command missing")
    return 2


def cmd_doctor(_args) -> int:
    data = doctor_report(ROOT)
    print(json.dumps(data, separators=(",", ":")))
    return 0 if data["ok"] else 2


def cmd_shipcheck(_args) -> int:
    return shipcheck_main()


def cmd_parts(args) -> int:
    from lib.assemble import AssembleError, assemble_site
    from lib.assemble_selftest import main as assemble_selftest
    from lib.parts_lib import family_counts, scan

    if args.parts_cmd == "selftest":
        return assemble_selftest()
    if args.parts_cmd == "scan":
        parts = scan()
        counts = family_counts(parts)
        if args.json:
            print(json.dumps({"parts": len(parts), "families": counts, "items": parts}, indent=2))
            return 0 if parts else 1
        print(f"{len(parts)} parts")
        for name in sorted(counts):
            print(f"  {name}: {counts[name]}")
        return 0 if parts else 1
    try:
        info = assemble_site(Path(args.project), Path(args.out))
    except AssembleError as exc:
        print(str(exc))
        return 1
    fam = ", ".join(f"{name} {info['families'][name]}" for name in sorted(info["families"]))
    print(f"assembled {info['out']} (mode: offline, 0 tokens)")
    print(f"  parts: {info['parts']} ({fam})")
    print(f"  header: {info['header']}")
    print(f"  pages: {', '.join(info['pages'])}")
    print(f"  next: python spidercaster.py check {info['out']}")
    return 0


def cmd_tools(args) -> int:
    from lib.tools_apply import ToolsApplyError, apply_part
    from lib.tools_index import ToolsIndexError, counts, index_rows

    try:
        if args.tools_cmd == "list":
            rows = index_rows()
            info = counts(rows)
            print(f"{info['rows']} rows: {info['built']} built, {info['missing']} missing")
            for row in rows:
                part = row.get("part_dir") or ""
                tail = f"  {part}" if part else ""
                print(f"  {row['catalog_id']}  {row['route']}  {row['status']}{tail}")
            return 0 if info["rows"] else 1
        mold = None
        if getattr(args, "mold", ""):
            try:
                mold = _load_apply_mold(args.mold)
            except ValueError as exc:
                print(str(exc))
                return 1
        project = Path(args.project) if getattr(args, "project", "") else None
        info = apply_part(
            args.catalog_id, Path(args.page), Path(args.out),
            replace=bool(getattr(args, "replace", False)),
            mold=mold,
            project=project,
        )
    except (ToolsIndexError, ToolsApplyError) as exc:
        print(str(exc))
        return 1
    print(f"applied {info['catalog_id']} -> {info['out']}")
    print(f"  part: {info['part_dir']}")
    print(f"  snippet: {info['snippet']}")
    return 0


def cmd_seat(args) -> int:
    try:
        data = seat_pack(ROOT, args.seat)
    except KeyError:
        print("unknown seat")
        return 2
    print(json.dumps(data, separators=(",", ":")))
    return 0


# ---------------------------------------------------------------- parser

def cmd_ui(args) -> int:
    """Stdio face: composer + ticket/ledger (steps 0-1), screens (steps 2+).

    Default opens the composer loop (Projects screen, /plan dry-run,
    ticket/ledger views, publish-readiness printer). --screens opens the
    check-board / engine-room loop instead. --selftest runs both
    batteries. Read-only throughout: consequential actions print the
    exact CLI command and never execute it.
    """
    if getattr(args, "selftest", False):
        from lib import ui_selftest as _screens_test
        from lib.ui_composer import main as composer_selftest

        code = composer_selftest()
        code2 = _screens_test.main()
        return 0 if (code == 0 and code2 == 0) else 1
    if getattr(args, "screens", False):
        from lib import ui_render as _ui

        return _ui.UI().loop(args.project or "projects/demo-local")
    from lib.ui_composer import run_ui

    project = getattr(args, "project", None)
    if project:
        cand = Path(project)
        if not cand.is_dir():
            named = ROOT / "projects" / Path(project).name
            if named.is_dir():
                project = str(named)
    return run_ui(project, root=ROOT)


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

    p = sub.add_parser("build", help="build a site (project dir, --from site.json, or --compose)")
    p.add_argument("project", nargs="?", help="project directory")
    p.add_argument("--from", dest="site_json", help="rebuild from an existing site.json (0 tokens)")
    p.add_argument("--out", help="output site dir (default sites/<slug>, or sites/<name>-compose with --compose)")
    p.add_argument("--offline", action="store_true", help="zero-token deterministic build")
    p.add_argument("--dry-run", action="store_true",
                   help="0-token sitemap/IR diff preview; writes nothing")
    p.add_argument("--compose", action="store_true",
                   help="offline compose path; requires a project, not --from")
    p.add_argument("--frame", default="", help="package frame id (used with --compose)")
    p.add_argument("--mold", default="", help="package mold id (used with --compose)")
    p.add_argument("--no-fallback", action="store_true", help="fail instead of falling back offline")
    p.add_argument("--template", choices=ir_mod.TEMPLATES)
    p.add_argument("--dark", dest="dark", action="store_true", default=None)
    p.add_argument("--light", dest="dark", action="store_false")
    p.add_argument("--pages", type=int, default=1, help="page count hint for the AI planner")
    p.add_argument("--brand", help="brand/title override")
    p.add_argument("--imagine", action="store_true",
                   help="prompt image provider and generate local assets/hero.png if missing")
    p.add_argument("--indexable", action="store_true",
                   help="omit robots noindex (default is noindex until approved)")
    p.add_argument("--host", default="", help="origin for sitemap.xml, used only with --indexable")
    p.add_argument("--max-copy-chars", type=int, default=24000)
    add_provider_opts(p)
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("compose", help="offline compose of one project (0 tokens, no publish)")
    p.add_argument("project", help="project directory")
    p.add_argument("--out", help="output site dir (default sites/<name>-compose)")
    p.add_argument("--frame", default="", help="package frame id")
    p.add_argument("--mold", default="", help="package mold id")
    p.add_argument("--plan", action="store_true", help="write structure.json and do not write HTML")
    p.add_argument("--structure", default="", help="accepted structure.json; drop or reorder only")
    p.set_defaults(fn=cmd_compose)

    p = sub.add_parser("refine", help="patch one section of a built site")
    p.add_argument("site", help="built site dir")
    p.add_argument("instruction")
    p.add_argument("--section", help="target section id (default: auto-match)")
    p.add_argument("--offline", action="store_true", help="theme flips only, 0 tokens")
    p.add_argument("--rollback", default="", help="restore a logged _attempts/<id> snapshot (0 tokens)")
    p.add_argument("--dry-run", action="store_true",
                   help="preview an offline refine as a 0-token diff; writes nothing")
    add_provider_opts(p)
    p.set_defaults(fn=cmd_refine)

    p = sub.add_parser("check", help="run built-in checks")
    p.add_argument("site")
    p.add_argument("--expect-noindex", action="store_true")
    p.add_argument("--expect-indexable", action="store_true")
    p.add_argument("--project", help="project dir; pass its copy text into the checker")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("ui", help="stdio face: composer + ticket/ledger + screens")
    p.add_argument("project", nargs="?", default=None,
                   help="project dir or name (default: Projects screen)")
    p.add_argument("--selftest", action="store_true",
                   help="composer/ticket batteries + screen walk; exit 0 required")
    p.add_argument("--screens", action="store_true",
                   help="check-board / engine-room loop instead of the composer")
    p.set_defaults(fn=cmd_ui)

    p = sub.add_parser("visit", help="visit-check a built site")
    p.add_argument("site", help="built site directory")
    p.set_defaults(fn=cmd_visit)

    p = sub.add_parser("start", help="first run: doctor + demo site + studio desk in browser (0 tokens)")
    p.add_argument("--project", default="demo-local", help="demo project (default demo-local)")
    p.add_argument("--port", type=int, default=4180)
    p.add_argument("--dry-run", action="store_true", help="print steps + doctor only; no writes, server, or browser")
    p.add_argument("--no-browser", action="store_true", help="serve but do not auto-open the browser")
    p.add_argument("--no-build", action="store_true", help="skip the demo-site ensure step")
    p.set_defaults(fn=cmd_start)

    p = sub.add_parser("studio", help="localhost desk; does not publish")
    p.add_argument("--port", type=int, default=4180)
    p.set_defaults(fn=cmd_studio)

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

    p = sub.add_parser("image", help="prompt xAI or OpenRouter and save a local image")
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--provider", choices=["xai", "openrouter"], default="xai")
    p.add_argument("--model", default="")
    p.add_argument("--aspect", default="16:9")
    p.add_argument("--quality", default="low", choices=["low", "medium", "auto"])
    p.set_defaults(fn=cmd_image)

    grp = sub.add_parser("graphics", help="multi-level graphics generator: vector, imagine, audit, optimize")
    grsub = grp.add_subparsers(dest="graphics_cmd", required=True)
    p = grsub.add_parser("selftest", help="run graphics engine unit selftest")
    p = grsub.add_parser("vector", help="generate procedural 16:9 vector scene (0 tokens)")
    p.add_argument("name", nargs="?", default="scene")
    p.add_argument("--kind", choices=["browser", "terminal", "dashboard", "isometric", "editorial"], default="browser")
    p.add_argument("--brand", default="Studio")
    p.add_argument("--out", help="optional output path (default: print stdout)")
    p = grsub.add_parser("audit", help="audit project images for bounds, weight, and luminance")
    p.add_argument("project")
    p = grsub.add_parser("optimize", help="normalize project image luminance and file weight")
    p.add_argument("project")
    p = grsub.add_parser("imagine", help="AI multi-slot image generation (hero, gallery)")
    p.add_argument("project")
    p.add_argument("--slots", default="hero", help="comma-separated slots, e.g. hero,gallery-1")
    p.add_argument("--provider", choices=["xai", "openrouter"], default="xai")
    p.add_argument("--model", default="")
    grp.set_defaults(fn=cmd_graphics)

    libp = sub.add_parser("library", help="vault, molds, and the live-use ledger")
    libp.add_argument("--vault", help="private vendor vault (default SPIDERCASTER_VAULT)")
    libsub = libp.add_subparsers(dest="library_cmd", required=True)
    p = libsub.add_parser("index", help="register OWP and GP catalog names into the vault")
    p.add_argument("--owp", default=str(DEFAULT_OWP))
    p.add_argument("--gp", default=str(DEFAULT_GP))
    p.add_argument("--frames", default=str(DEFAULT_FRAMES))
    p = libsub.add_parser("list", help="list package molds and vault frame count")
    p = libsub.add_parser("mold", help="save a scratch, mutation, or mix mold")
    p.add_argument("--id", required=True)
    p.add_argument("--origin", required=True, choices=["scratch", "mutate", "mix"])
    p.add_argument("--palette", required=True, help="#rrggbb accent")
    p.add_argument("--type-lead", required=True, choices=["serif", "sans", "slab", "mono-display"])
    p.add_argument("--nav", required=True, choices=["segmented", "top-bar", "sidebar", "one-page", "footer-only"])
    p.add_argument("--template", default="editorial", choices=ir_mod.TEMPLATES)
    p.add_argument("--parent", action="append", help="parent mold or vendor frame id; repeat for a mix")
    p.add_argument("--section", action="append")
    p.add_argument("--note", default="")
    p = libsub.add_parser("bind", help="attach one mold to a site")
    p.add_argument("--site", required=True)
    p.add_argument("--mold", required=True)
    p.add_argument("--vendor", help="one as-is vendor frame, mutate molds only")
    p.add_argument("--live", action="store_true", help="mark live; refuses a frame or mold already live elsewhere")
    p.add_argument(
        "--out",
        default="",
        help="built site dir holding crew-ticket.json (default sites/<slug>); --live verifies it",
    )
    p = libsub.add_parser("accept", help="record a snapshot directory that already sits in the vault")
    p.add_argument("--frame", required=True)
    p.add_argument("--snapshot", required=True)
    p = libsub.add_parser("selftest", help="run the library rule checks")
    libp.set_defaults(fn=cmd_library)

    crewp = sub.add_parser("crew", help="seven hands; does not publish")
    crewp.add_argument("--vault", help="private vendor vault")
    crewsub = crewp.add_subparsers(dest="crew_cmd", required=True)
    crewsub.add_parser("roles", help="print the seven seats and their hands")
    p = crewsub.add_parser("run", help="build one site through all seven hands")
    p.add_argument("project")
    p.add_argument("--site", required=True)
    p.add_argument("--out")
    p.add_argument("--mold")
    p.add_argument("--scratch", action="store_true")
    p.add_argument("--palette", default="#1f6f5b")
    p.add_argument("--type-lead", default="serif", choices=["serif", "sans", "slab", "mono-display"])
    p.add_argument("--nav", default="segmented", choices=["segmented", "top-bar", "sidebar", "one-page", "footer-only"])
    p.add_argument("--template", default="editorial", choices=ir_mod.TEMPLATES)
    p.add_argument("--frame", default="", help="package section frame id from library/frames")
    crewsub.add_parser("selftest", help="run the crew against the demo-local project")
    crewp.set_defaults(fn=cmd_crew)

    p = sub.add_parser("doctor", help="report python, molds, frames, seats, and hand order")
    p.set_defaults(fn=cmd_doctor)

    p = sub.add_parser("shipcheck", help="say whether the app is ship-ready")
    p.set_defaults(fn=cmd_shipcheck)

    p = sub.add_parser("seat", help="print one seat pack")
    p.add_argument("seat", help="seat id")
    p.set_defaults(fn=cmd_seat)

    partp = sub.add_parser("parts", help="index every part and assemble one site")
    partsub = partp.add_subparsers(dest="parts_cmd", required=True)
    p = partsub.add_parser("scan", help="count every part manifest")
    p.add_argument("--json", action="store_true")
    p = partsub.add_parser("assemble", help="build a noindex site that uses the parts")
    p.add_argument("--project", default=str(ROOT / "projects" / "demo-local"))
    p.add_argument("--out", default=str(ROOT / "sites" / "assembled"))
    partsub.add_parser("selftest", help="scan, assemble to a temp dir, and run check")
    partp.set_defaults(fn=cmd_parts)

    toolp = sub.add_parser("tools", help="list catalog parts and apply one onto a page")
    toolsub = toolp.add_subparsers(dest="tools_cmd", required=True)
    toolsub.add_parser("list", help="list catalog rows as built or missing")
    p = toolsub.add_parser("apply", help="append one built part onto a page")
    p.add_argument("catalog_id", metavar="CATALOG_ID")
    p.add_argument("--page", required=True, help="source HTML page")
    p.add_argument("--out", required=True, help="output HTML path")
    p.add_argument("--replace", action="store_true", help="replace the part already on the page")
    p.add_argument("--mold", default="", help="mold id; palette and type lead are passed through")
    p.add_argument("--project", default="", help="project dir passed through to the lock check")
    toolp.set_defaults(fn=cmd_tools)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
