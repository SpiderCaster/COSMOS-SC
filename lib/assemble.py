"""Build one static site that uses the SpiderCaster parts together.

The page is an offline build of a real project. Five static callouts are
filled only with sentences from that project's brief and copy. The header kit
is applied on top. A second page lists every manifest from ``parts_lib.scan``.

Nothing is installed, published, or deployed. Stdlib only. Zero tokens.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from lib.parts_lib import default_roots, family_counts, safe_visible, scan

ROOT = Path(__file__).resolve().parent.parent
_KIT_ITEMS = ("definition-callout", "key-takeaways", "step-callout", "editors-note", "stat-callout", "back-to-top-button")

_LAYOUT_CSS = """
body{padding-bottom:96px}
.sc-assemble{min-width:0}
.sc-assemble__main{min-width:0}
#sc-band,#sc-define,#sc-takeaways,#sc-steps,#sc-note,#sc-stats,.sc-assemble__side a{scroll-margin-top:96px}
.sc-statbox .sc-statbox__source{font-size:18px}
@media (min-width:960px){
  .sc-assemble{display:grid;grid-template-columns:minmax(0,1fr) 300px;column-gap:28px;align-items:start}
  .sc-assemble__side{position:sticky;top:88px}
}
.sc-assemble__side{box-sizing:border-box;margin:24px 0;padding:14px 16px 14px 18px;border:1px solid var(--accent-text);border-left-width:8px;border-radius:6px;background:var(--surface);color:var(--text);font-size:18px;line-height:1.45}
.sc-assemble__side h2{margin:0 0 8px;color:var(--text);font-size:20px;line-height:1.3}
.sc-assemble__side a{display:flex;align-items:center;min-height:44px;color:var(--accent-text);font-size:18px}
.sc-cat{font-size:18px}
.sc-cat h1{font-size:36px;line-height:1.15;margin:28px 0 12px}
.sc-cat h2{font-size:24px;line-height:1.25;margin:32px 0 8px}
.sc-cat h3{font-size:20px;line-height:1.3;margin:0}
.sc-cat p{font-size:18px;line-height:1.45;margin:4px 0 0}
.sc-families{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 8px}
.sc-families a{display:inline-flex;align-items:center;min-height:44px;padding:0 12px;font-size:18px}
.sc-cat label{display:block;font-size:18px;margin:12px 0 6px}
.sc-cat input{display:block;width:100%;box-sizing:border-box;min-height:44px;font-size:18px;padding:8px 12px;color:var(--text);background:var(--surface);border:2px solid var(--accent-text)}
.sc-row{padding:14px 0;border-bottom:1px solid var(--accent-text);overflow-wrap:anywhere}
""".strip()

_FILTER_JS = """
(function () {
  var q = document.getElementById("sc-filter");
  var count = document.getElementById("sc-count");
  var empty = document.getElementById("sc-none");
  var fams = document.querySelectorAll(".sc-fam");
  if (!q) return;
  var rows = document.querySelectorAll(".sc-row");
  function apply() {
    var n = q.value.trim().toLowerCase();
    var shown = 0;
    for (var i = 0; i < rows.length; i++) {
      var ok = !n || rows[i].textContent.toLowerCase().indexOf(n) !== -1;
      rows[i].hidden = !ok;
      if (ok) shown++;
    }
    for (var j = 0; j < fams.length; j++) {
      var any = false;
      var own = fams[j].querySelectorAll(".sc-row");
      for (var k = 0; k < own.length; k++) if (!own[k].hidden) any = true;
      fams[j].hidden = !any;
    }
    if (count) count.textContent = shown + " of " + rows.length + " parts";
    if (empty) empty.hidden = shown !== 0;
  }
  q.addEventListener("input", apply);
})();
""".strip()

_ORIGIN = {"fleet": "Fleet", "kit": "Kit", "engine": "Engine"}
_RUNTIME = {"static": "static files", "theme-hook": "theme hook"}


class AssembleError(Exception):
    pass


def _read(path: Path) -> str:
    if not path.is_file():
        raise AssembleError(f"missing {path}")
    return path.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return " ".join(text.split())


def _first_prose(md: str) -> str:
    buf: list[str] = []
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("#") or s.startswith("-"):
            if buf:
                break
            continue
        if not s:
            if buf:
                break
            continue
        buf.append(s)
    return _flat(" ".join(buf))


def _section_bullets(md: str, heading: str) -> list[str]:
    want = heading.strip().lower()
    grab = False
    out: list[str] = []
    for line in md.splitlines():
        if line.startswith("#"):
            if grab:
                break
            grab = line.lstrip("#").strip().lower() == want
            continue
        if grab and line.strip().startswith("- "):
            out.append(line.strip()[2:].strip())
    return out


def _clause(text: str, needle: str) -> str:
    flat = _flat(text)
    for chunk in re.split(r"(?<=[.!?])\s+|;\s*", flat):
        if needle.lower() in chunk.lower():
            return chunk.strip(" .")
    return ""


def _split_step(bullet: str) -> tuple[str, str]:
    if ": " in bullet:
        title, body = bullet.split(": ", 1)
        return title.strip(), body.strip()
    return bullet.strip(), ""


def load_facts(project: Path) -> dict:
    """Pull the assembled page's words from the project. Fail closed."""
    overview = _read(project / "copy" / "overview.md")
    faq = _read(project / "copy" / "faq.md")
    commands = _read(project / "copy" / "commands.md")
    brief = _read(project / "brief.md")

    definition = _first_prose(overview)
    takeaways = _section_bullets(overview, "Why it is cheap")[:3]
    wanted = []
    for bullet in _section_bullets(commands, "Build"):
        low = bullet.lower()
        if low.startswith("forge init") or "--offline" in low:
            wanted.append(bullet)
    for bullet in _section_bullets(commands, "Gate and preview"):
        if bullet.lower().startswith("forge check"):
            wanted.append(bullet)
    steps = [_split_step(item) for item in wanted[:3]]
    prose = _first_prose(brief)
    mark = prose.lower().find("tone:")
    note = prose[mark:].strip() if mark != -1 else ""
    zero = _clause(overview, "zero tokens")
    one = _clause(faq, "planning call")
    noindex = _clause(overview, "noindex")
    missing = []
    if not definition:
        missing.append("definition")
    if len(takeaways) < 3:
        missing.append("takeaways")
    if len(steps) < 3 or any(not title for title, _body in steps):
        missing.append("steps")
    if not note:
        missing.append("editor note")
    if not (zero and one and noindex):
        missing.append("stats")
    if missing:
        raise AssembleError("copy is missing " + ", ".join(missing) + f" in {project}")
    for bit in (definition, note, zero, one, noindex, *takeaways, *(a + " " + b for a, b in steps)):
        if not safe_visible(bit):
            raise AssembleError("a copy sentence is not safe to publish on a checked page")
    return {
        "definition": definition,
        "takeaways": takeaways,
        "steps": steps,
        "note": note,
        "stats": (("Zero", zero), ("One", one), ("Noindex", noindex)),
        "stat_source": "Source: overview.md and faq.md in this project.",
    }


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _kit_root(roots: dict[str, Path]) -> Path:
    kit = roots.get("kit") or default_roots()["kit"]
    if not (kit / "popups-callouts" / "items").is_dir():
        raise AssembleError(f"popup kit not found at {kit}")
    return kit


def _part_css(kit: Path) -> str:
    chunks = [_LAYOUT_CSS]
    items = kit / "popups-callouts" / "items"
    for name in _KIT_ITEMS:
        css = items / name / f"{name}.css"
        if not css.is_file():
            raise AssembleError(f"missing {css}")
        chunks.append(css.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _totop_js(kit: Path) -> str:
    path = kit / "popups-callouts" / "items" / "back-to-top-button" / "back-to-top-button.js"
    if not path.is_file():
        raise AssembleError(f"missing {path}")
    return path.read_text(encoding="utf-8")


def _band(facts: dict, page_links: list[tuple[str, str]]) -> str:
    takes = "".join(f"<li>{_esc(item)}</li>" for item in facts["takeaways"])
    steps = "".join(
        f"<li><strong>{_esc(title)}</strong> {_esc(body)}</li>" for title, body in facts["steps"]
    )
    stats = "".join(
        f'<li><span class="sc-stats__value">{_esc(value)}</span>'
        f'<span class="sc-stats__label">{_esc(label)}</span></li>'
        for value, label in facts["stats"]
    )
    own = [
        ("sc-define", "Definition"),
        ("sc-takeaways", "Key takeaways"),
        ("sc-steps", "Commands"),
        ("sc-note", "Editor's note"),
        ("sc-stats", "By the numbers"),
    ]
    seen = {sid for sid, _label in own}
    links = list(own)
    for sid, label in page_links:
        if sid in seen or not safe_visible(label):
            continue
        seen.add(sid)
        links.append((sid, label))
    nav = "".join(f'<a href="#{_esc(sid)}">{_esc(label)}</a>' for sid, label in links)
    return f"""<section class="sec" id="sc-band">
<div class="wrap sc-assemble">
<div class="sc-assemble__main">
<aside class="sc-define" id="sc-define" data-sc-part="definition-callout" aria-labelledby="df-1"><p class="sc-define__title" id="df-1">Definition</p><dl><dt><dfn>SpiderCaster</dfn></dt><dd>{_esc(facts["definition"])}</dd></dl></aside>
<section class="sc-takeaways" id="sc-takeaways" data-sc-part="key-takeaways" aria-labelledby="kt-1"><h2 class="sc-takeaways__title" id="kt-1">Key takeaways</h2><ul>{takes}</ul></section>
<div class="sc-steps" id="sc-steps" data-sc-part="step-callout" role="group" aria-labelledby="stp-1"><h2 class="sc-steps__title" id="stp-1">Commands</h2><ol>{steps}</ol></div>
<aside class="sc-editors-note" id="sc-note" data-sc-part="editors-note" aria-labelledby="ed-1"><p class="sc-editors-note__title" id="ed-1">Editor's note</p><p>{_esc(facts["note"])}</p></aside>
<section class="sc-statbox" id="sc-stats" data-sc-part="stat-callout" aria-labelledby="st-1"><h2 class="sc-statbox__title" id="st-1">By the numbers</h2><ul class="sc-stats">{stats}</ul><p class="sc-statbox__source">{_esc(facts["stat_source"])}</p></section>
</div>
<aside class="sc-assemble__side" aria-labelledby="sc-onpage"><h2 id="sc-onpage">On this page</h2>{nav}<a href="catalog.html">Parts library</a></aside>
</div>
</section>"""


def _page_links(html: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for match in re.finditer(r'<section id="([^"]+)"', html):
        end = html.find("</section>", match.end())
        window = html[match.end(): end if end != -1 else match.end() + 2000]
        heading = re.search(r"<h[12][^>]*>(.*?)</h[12]>", window, re.DOTALL)
        if not heading:
            continue
        text = re.sub(r"<[^>]+>", "", heading.group(1))
        text = _flat(text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
        if text:
            out.append((match.group(1), text))
    return out


def _insert_band(html: str, band: str) -> str:
    match = re.search(r"</section>", html)
    if not match:
        raise AssembleError("built page has no section to follow")
    return html[: match.end()] + "\n" + band + html[match.end() :]


def _add_nav_link(html: str) -> str:
    link = '<a href="catalog.html">Parts library</a>'
    html2, n = re.subn(
        r'(<nav id="site-nav" class="nav-links">)(.*?)(</nav>)',
        lambda m: m.group(1) + m.group(2) + link + m.group(3),
        html,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        raise AssembleError("built page has no #site-nav")
    html3, n2 = re.subn(
        r'(<div class="foot-links">)(.*?)(</div>)',
        lambda m: m.group(1) + m.group(2) + link + m.group(3),
        html2,
        count=1,
        flags=re.DOTALL,
    )
    if n2 != 1:
        raise AssembleError("built page has no footer link row")
    return html3


def _inject_assets(html: str, css: str, js: str) -> str:
    if "</head>" not in html or "</body>" not in html:
        raise AssembleError("built page is missing head or body")
    style = '<style id="sc-parts">\n' + css + "\n</style>\n"
    button = '<button type="button" class="sc-totop" data-sc-totop data-sc-part="back-to-top-button" data-sc-after="600" data-sc-focus="main" aria-label="Back to top">&uarr; Top</button>\n'
    script = '<script id="sc-totop-js">\n' + js + "\n</script>\n"
    html = html.replace("</head>", style + "</head>", 1)
    return html.replace("</body>", button + script + "</body>", 1)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )


def _build_offline(project: Path, out: Path) -> None:
    proc = _run(
        [sys.executable, str(ROOT / "spidercaster.py"), "build", str(project), "--offline", "--out", str(out)],
        ROOT,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise AssembleError("offline build failed: " + detail[-500:])


def _apply_header(index: Path, kit: Path) -> str:
    tool = kit / "headers" / "_shared" / "sc_header.py"
    if not tool.is_file():
        return "engine"
    dest = index.with_name("index.header.html")
    attempts = [
        ["--item", "hdr-classic-sticky", "--with", "cmp-scroll-progress"],
        ["--item", "hdr-classic-sticky"],
    ]
    for extra in attempts:
        proc = _run([sys.executable, str(tool), "apply", str(index), str(dest), *extra], tool.parent)
        if proc.returncode == 0 and dest.is_file():
            dest.replace(index)
            return "hdr-classic-sticky" if len(extra) == 2 else "hdr-classic-sticky+cmp-scroll-progress"
        dest.unlink(missing_ok=True)
    return "engine"


def _family_label(name: str) -> str:
    labels = {
        "headers": "Headers",
        "hooks_blocks": "Hooks and blocks",
        "popups_callouts": "Popups and callouts",
        "sidebars": "Sidebars and widgets",
    }
    return labels.get(name, name.replace("_", " ").replace("-", " ").title())


def _catalog(index_html: str, parts: list[dict]) -> str:
    lang = "en"
    lang_m = re.search(r'<html lang="([^"]+)"', index_html)
    if lang_m:
        lang = lang_m.group(1)
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", index_html, re.DOTALL))
    header_m = re.search(r'<header class="site-header".*?</header>', index_html, re.DOTALL)
    footer_m = re.search(r'<footer class="site-footer".*?</footer>', index_html, re.DOTALL)
    if not header_m or not footer_m:
        raise AssembleError("built page is missing a header or footer to reuse")

    def retarget(block: str) -> str:
        def repl(match: re.Match[str]) -> str:
            href = match.group(1)
            if href.startswith("#"):
                return f'href="index.html{href}"'
            return match.group(0)

        return re.sub(r'href="([^"]*)"', repl, block)

    header = retarget(header_m.group(0)).replace(' aria-current="page"', "")
    header = header.replace('href="catalog.html"', 'href="catalog.html" aria-current="page"', 1)
    footer = retarget(footer_m.group(0))
    kept = []
    for match in re.finditer(r"<script\b([^>]*)>(.*?)</script>", index_html, re.DOTALL):
        kind = ""
        kind_m = re.search(r'type="([^"]*)"', match.group(1))
        if kind_m:
            kind = kind_m.group(1).lower()
        if "ld+json" in kind:
            continue
        kept.append(match.group(0))
    scripts = "\n".join(kept)
    groups: dict[str, list[dict]] = {}
    for rec in parts:
        groups.setdefault(rec["family"], []).append(rec)
    fam_links = []
    sections = []
    for family in sorted(groups):
        label = _family_label(family)
        fid = "fam-" + re.sub(r"[^A-Za-z0-9_-]+", "-", family)
        fam_links.append(f'<a href="#{fid}">{_esc(label)} ({len(groups[family])})</a>')
        rows = []
        for rec in groups[family]:
            purpose = f"<p>{_esc(rec['purpose'])}</p>" if rec.get("purpose") else ""
            shown_targets = [item for item in rec["targets"] if safe_visible(item)]
            targets = ", ".join(shown_targets) if shown_targets else "no theme target"
            shown_id = rec["id"] if safe_visible(rec["id"]) else rec["html_id"]
            meta = " · ".join(
                (
                    label,
                    _ORIGIN.get(rec["origin"], rec["origin"]),
                    _RUNTIME.get(rec["runtime"], rec["runtime"]),
                    targets,
                )
            )
            rows.append(
                f'<article class="sc-row" id="{_esc(rec["html_id"])}" data-part="{_esc(rec["id"])}" '
                f'data-family="{_esc(family)}"><h3>{_esc(rec["name"])}</h3>'
                f'<p class="sc-meta">{_esc(meta)}</p><p class="sc-id">{_esc(shown_id)}</p>{purpose}</article>'
            )
        sections.append(f'<section class="sc-fam" id="{fid}"><h2>{_esc(label)}</h2>{"".join(rows)}</section>')
    title = f"Parts library ({len(parts)})"
    desc = (
        f"{len(parts)} SpiderCaster part manifests, grouped by family. "
        "The front page uses the static callouts and the classic sticky header. This page is noindex."
    )
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": title,
        "description": desc,
        "url": "catalog.html",
    }
    website_tag = (
        '<script type="application/ld+json">'
        + json.dumps(website, ensure_ascii=True).replace("<", "\\u003c")
        + "</script>"
    )
    return f"""<!doctype html>
<html lang="{_esc(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{_esc(title)}</title>
<meta name="description" content="{_esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="catalog.html">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{website_tag}
<style>
{styles}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{header}
<main id="main">
<div class="wrap sc-cat">
<h1>Parts library</h1>
<p id="sc-count">{len(parts)} parts</p>
<p>{_esc(desc)}</p>
<nav class="sc-families" aria-label="Part families">{"".join(fam_links)}</nav>
<label for="sc-filter">Filter parts by name</label>
<input id="sc-filter" type="text" autocomplete="off">
<p id="sc-none" hidden>No part matches that filter.</p>
{"".join(sections)}
</div>
</main>
{footer}
<button type="button" class="sc-totop" data-sc-totop data-sc-after="600" data-sc-focus="main" aria-label="Back to top">&uarr; Top</button>
{scripts}
<script>
{_FILTER_JS}
</script>
</body>
</html>
"""


def assemble_site(project: Path, out: Path, roots: dict[str, Path] | None = None) -> dict:
    project = Path(project)
    out = Path(out)
    roots = roots or default_roots()
    if not project.is_dir():
        raise AssembleError(f"no project at {project}")
    facts = load_facts(project)
    parts = scan(roots)
    if len(parts) < 40:
        raise AssembleError(f"only {len(parts)} parts found; the fleet tree is missing or empty")
    kit = _kit_root(roots)
    out.mkdir(parents=True, exist_ok=True)
    _build_offline(project, out)
    index = out / "index.html"
    html = index.read_text(encoding="utf-8")
    links = _page_links(html)
    html = _insert_band(html, _band(facts, links))
    html = _add_nav_link(html)
    html = _inject_assets(html, _part_css(kit), _totop_js(kit))
    index.write_text(html, encoding="utf-8")
    header = _apply_header(index, kit)
    html = index.read_text(encoding="utf-8")
    (out / "catalog.html").write_text(_catalog(html, parts), encoding="utf-8")
    counts = family_counts(parts)
    info = {
        "project": str(project),
        "out": str(out),
        "mode": "offline",
        "tokens": 0,
        "header": header,
        "parts": len(parts),
        "families": counts,
        "used_on_index": [
            "definition-callout",
            "key-takeaways",
            "step-callout",
            "editors-note",
            "stat-callout",
            "back-to-top-button",
            header,
        ],
        "pages": ["index.html", "catalog.html", "favicon.svg"],
    }
    (out / "assemble.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    (out / "parts.json").write_text(json.dumps(parts, indent=2) + "\n", encoding="utf-8")
    return info
