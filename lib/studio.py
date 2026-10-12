"""Localhost studio. Stdlib only. Does not publish or write the ledger.

The desk, the twelve rooms, and the paint path are the 2026-10-08
discussion in library/research/ui/DISCUSSION.md. Built pages stay noindex.
"""
from __future__ import annotations

import json
import re
import threading
from html import escape
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingTCPServer
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent

PROJECTS = ("demo-local", "bench-harbor-tearoom")
MOLDS = ("discover-grid", "clarify-mix")
KINDS = ("header", "hero", "card", "faq", "cta", "footer")
WIDTHS = (360, 390, 412, 1280)
PREVIEW_PORT = 4300
STUDIO_PORT = 4180

ROOMS = (
    ("/", "Desk"),
    ("/plan", "Plan"),
    ("/parts", "Parts"),
    ("/preview", "Preview"),
    ("/check", "Check"),
    ("/copy", "Copy"),
    ("/mold", "Mold"),
    ("/mobile", "Mobile"),
    ("/seo", "SEO"),
    ("/crew", "Crew"),
    ("/domains", "Domains"),
    ("/score", "Score"),
)

GROUPS = (
    ("Copy", (
        "no_sample", "no_soft_placeholders", "no_hotlink",
        "ungrounded_claim", "lone_about", "invented_chrome", "part_demo",
    )),
    ("Contrast", ("contrast",)),
    ("Chrome", (
        "type_floor", "tap_target", "site_header", "skip_link", "scroll_margin",
        "hero_visual", "mobile_hero", "mobile_visible", "no_empty_panel",
        "favicon_link", "favicon_svg", "phone_bar", "relative_img",
        "missing_file", "svg_photo", "photo_luma",
    )),
    ("Crawl", (
        "files_present", "meta_basics", "description", "one_h1", "heading_order",
        "canonical", "json_ld", "faq_schema", "img_alt", "internal_links",
        "slug_shape", "noindex_status",
    )),
    ("Plus", (
        "sideways_scroll", "mobile_nav_drawer", "mobile_visibility",
        "grey_tile", "token_ledger", "gate_error", "mobile_spec",
    )),
)

BLOCKED = (
    ("iseark.com", "WordPress. No copy pack. Do not invent a page."),
    ("teavital.com", "WordPress. No copy pack. Do not restage it here."),
    ("bradleybrandfurniture.com", "WordPress. No copy pack."),
    ("buyfigs.com", "WordPress. No copy pack."),
    ("chopncut.com", "WooCommerce. No copy pack."),
    ("rareplantbid.com", "Paused, pull only. No copy pack."),
    ("fruitaholics.com", "Paused. No copy pack."),
    ("jackcancode.com", "Paused. No copy pack."),
    ("lucentoils.com", "Paused. No copy pack."),
    ("lmnator.com", "Paused, do-not-test. No copy pack."),
    ("janustea.com", "Paused. No copy pack."),
    ("figidk.com", "Park. Not a SpiderCaster project."),
    ("figpollen.com", "Park, closed. No copy pack."),
    ("buypollen.com", "Park, closed. No copy pack."),
    ("okoils.com", "Park stub. No copy pack. Do not invent a page."),
    ("mdrater.com", "Park stub. No copy pack."),
    ("modelraters.com", "Park stub. No copy pack."),
    ("floelixir.com", "Elixir. No SpiderCaster copy pack."),
    ("elitelixirs.com", "Elixir hub. No copy pack."),
    ("seven elixir parks", "Frozen on the fleet row. Hosts are not spelled here. No copy pack."),
    ("recovelixir.com", "No project and no copy pack."),
    ("movelixir.com", "No copy pack. warmth-authority is already live here. Do not bind it."),
    ("adapt, bang, biom, boost, gain, immun, max, metab, mobil, mov, pow, prim, recov, thriv, trim",
     "Empty elixir names. No pages until Keith decides. This screen does not decide."),
    ("figsale.com", "Empty. No copy pack."),
    ("pcoir.com", "Empty. No copy pack."),
    ("webuymaga.com", "Empty. No copy pack."),
    ("weseark.com", "Empty. No copy pack."),
    ("wesearch.com", "Empty. No copy pack."),
    ("bbfur.com", "Paused. Old staged content is not a SpiderCaster copy pack."),
    ("bradleylumbercompany.com", "Paused. No copy pack."),
    ("salineriverworkshop.com", "Paused. No copy pack."),
    ("figroots.com", "Hands off. Never edit."),
    ("slpwow.com", "Hands off. Never edit."),
    ("wowtherapies.com", "Hands off. Never edit."),
    ("dailyscar.com", "Paused. No copy pack."),
)

_TOKEN = re.compile(r"^[a-z0-9-]{0,80}$")
_META_DESC = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.IGNORECASE)
_ROBOTS = re.compile(r'<meta\s+name="robots"\s+content="([^"]*)"', re.IGNORECASE)

CSS = """
body{margin:0;background:#fff;color:#1a1a1a;font:18px/1.45 "Segoe UI",system-ui,sans-serif}
a{color:#1a1a1a}
.skip{position:absolute;left:-999px;top:8px;background:#fff;color:#1a1a1a;padding:12px 16px;font-size:16px}
.skip:focus{left:16px;z-index:3}
.site-header{position:sticky;top:0;background:#fff;border-bottom:1px solid #1a1a1a;padding:12px 16px}
.site-header a{font-size:16px;min-height:44px;display:inline-flex;align-items:center}
nav{display:flex;flex-direction:column;gap:8px;padding:8px 16px 0}
nav a{font-size:16px;min-height:44px;display:flex;align-items:center}
main{padding:16px;max-width:40rem}
h1{font-size:28px;line-height:1.2;margin:0 0 12px}
h2{font-size:22px;line-height:1.3;margin:20px 0 8px}
button,select{font:16px/1.2 "Segoe UI",system-ui,sans-serif;min-height:44px;min-width:44px;display:block;width:100%;box-sizing:border-box;margin:8px 0;padding:12px 16px}
button{background:#1a1a1a;color:#fff;border:0}
select{background:#fff;color:#1a1a1a;border:1px solid #1a1a1a}
label{font-size:16px;display:block;margin-top:12px}
.choice{display:flex;align-items:center;gap:12px;min-height:44px;font-size:16px}
.choice input{width:44px;height:44px}
p,li,pre,td{overflow-wrap:anywhere}
pre{white-space:pre-wrap;font:16px/1.4 Consolas,ui-monospace,monospace}
table{border-collapse:collapse;width:100%}
td{border-top:1px solid #1a1a1a;padding:8px;vertical-align:top;font-size:16px}
.slot{max-width:100%;overflow-x:auto}
iframe{border:2px solid #1a1a1a;display:block;background:#fff}
.note{font-size:16px}
"""


class Desk:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else ROOT
        self.project = ""
        self.site = ""
        self.kind = "header"
        self.width = 390
        self.message = ""
        self.error = ""
        self.accepted: set[str] = set()
        self.rows: list[dict] = []
        self.counts: dict = {}
        self.visit: dict = {}
        self.checked = ""
        self.preview = None
        self.preview_port = 0
        self.preview_folder = ""
        self.lock = threading.Lock()

    def stop_preview(self) -> None:
        with self.lock:
            httpd = self.preview
            self.preview = None
            self.preview_port = 0
            self.preview_folder = ""
        if httpd is not None:
            httpd.shutdown()
            httpd.server_close()

    def start_preview(self, folder: Path) -> int:
        self.stop_preview()
        from lib.serve import serve

        httpd, port = serve(folder, port=PREVIEW_PORT)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        with self.lock:
            self.preview = httpd
            self.preview_port = port
            self.preview_folder = folder.name
        return port


def plan_dir(root: Path, project: str) -> Path:
    return root / "sites" / f"{project}-studio-plan"


def studio_dir(root: Path, project: str) -> Path:
    return root / "sites" / f"{project}-studio"


def project_dir(root: Path, project: str) -> Path:
    return root / "projects" / project


def site_choices(project: str) -> tuple[str, ...]:
    if project == "demo-local":
        return ("demo-local-studio", "demo-local", "demo-local-compose", "demo-local-ai")
    if project == "bench-harbor-tearoom":
        return ("bench-harbor-tearoom-studio", "bench-harbor-tearoom")
    return ()


def resolve_site(root: Path, project: str, name: str, assembled: bool = False) -> Path | None:
    choices = list(site_choices(project))
    if assembled:
        choices.append("assembled")
    if name not in choices or not _TOKEN.fullmatch(name or ""):
        return None
    path = (root / "sites" / name).resolve()
    try:
        path.relative_to((root / "sites").resolve())
    except ValueError:
        return None
    return path


def _token(value: str) -> bool:
    return bool(_TOKEN.fullmatch(value or ""))


def _form(raw: dict) -> dict:
    out = {}
    for key, values in raw.items():
        if not isinstance(values, list) or not values:
            continue
        out[str(key)] = str(values[0])
    return out


def _frames(root: Path) -> list[dict]:
    from lib.frames import list_frames

    found = list_frames()
    if found:
        return found
    folder = root / "library" / "frames"
    return [{"id": path.stem, "sections": []} for path in sorted(folder.glob("*.json"))]


def _frame_ids(root: Path) -> list[str]:
    return [str(item.get("id") or "") for item in _frames(root) if item.get("id")]


def _copy_names(root: Path, project: str) -> list[str]:
    folder = project_dir(root, project) / "copy"
    if not folder.is_dir():
        return []
    return sorted(
        path.name for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in {".md", ".markdown", ".txt", ".json"}
    )


def _load_structure(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _page_sections(data: dict) -> list[tuple[int, int, dict]]:
    found = []
    pages = data.get("pages") if isinstance(data.get("pages"), list) else []
    for pi, page in enumerate(pages):
        if not isinstance(page, dict):
            continue
        sections = page.get("sections") if isinstance(page.get("sections"), list) else []
        for si, sec in enumerate(sections):
            if isinstance(sec, dict):
                found.append((pi, si, sec))
    return found


def _save_plan(path: Path, data: dict) -> None:
    from lib.structure import save_structure

    save_structure(path, data)


def _mold_file(root: Path, mold_id: str) -> dict:
    path = root / "library" / "molds" / f"{mold_id}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _ledger_lines(root: Path) -> list[str]:
    path = root / "library" / "ledger.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["ledger was not read"]
    rows = data.get("assignments") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return ["ledger was not read"]
    lines = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        site = str(row.get("site") or "")
        mold = str(row.get("mold") or "")
        flag = "live" if row.get("live") is True else "draft"
        lines.append(f"{flag}: {site}, mold {mold}")
    return lines or ["ledger has no rows"]


def _preview_block(folder: Path) -> str:
    index = folder / "index.html"
    if not index.is_file():
        return f"no index.html in {folder.name}; run a build first"
    try:
        html = index.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"cannot read index.html: {exc}"
    match = _ROBOTS.search(html)
    if match is None or "noindex" not in match.group(1).lower():
        return "Serve refused: the page is not noindex"
    if (folder / "sitemap.xml").is_file():
        return "Serve refused: sitemap.xml is present"
    robots = folder / "robots.txt"
    if robots.is_file():
        try:
            text = robots.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        if "Disallow: /" not in text:
            return "Serve refused: robots.txt does not disallow /"
    return ""


def _group_rows(rows: list[dict]) -> dict[str, list[dict]]:
    grouped = {name: [] for name, _members in GROUPS}
    for row in rows:
        placed = False
        for name, members in GROUPS:
            if row.get("name") in members:
                grouped[name].append(row)
                placed = True
                break
        if not placed:
            grouped["Plus"].append(row)
    return grouped


def _group_word(rows: list[dict]) -> str:
    if not rows:
        return "not run"
    statuses = {str(row.get("status") or "") for row in rows}
    for word in ("FAIL", "WARN", "SKIP", "PASS"):
        if word in statuses:
            return word
    return "not run"


def _only_files_present(rows: list[dict]) -> bool:
    return len(rows) == 1 and rows[0].get("name") == "files_present" and rows[0].get("status") == "FAIL"


def layout(title: str, body: str, message: str, error: str) -> str:
    links = "\n".join(
        f'<a href="{escape(path)}">{escape(label)}</a>' for path, label in ROOMS
    )
    banner = ""
    if error:
        banner += f'<p class="error">{escape(error)}</p>'
    if message:
        banner += f'<p>{escape(message)}</p>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><a href="/">spidercaster</a> <span class="note">127.0.0.1 · noindex · does not publish</span></header>
<nav>{links}</nav>
<main id="main">
<h1>{escape(title)}</h1>
{banner}
{body}
</main>
</body>
</html>
"""


def _project_form(desk: Desk, action: str, extra: str = "") -> str:
    options = ['<option value="">Choose a project</option>']
    for name in PROJECTS:
        selected = " selected" if name == desk.project else ""
        options.append(f'<option value="{escape(name)}"{selected}>{escape(name)}</option>')
    return (
        f'<form method="post" action="/act">'
        f'<input type="hidden" name="action" value="{escape(action)}">'
        f'<label for="project">Project</label>'
        f'<select id="project" name="project">{"".join(options)}</select>'
        f'{extra}'
        f'<button type="submit">Open</button>'
        f'</form>'
    )


def _site_form(desk: Desk, action: str, assembled: bool = False, button: str = "Use this folder", screen: str = "") -> str:
    if not desk.project:
        return "<p>Choose a project on the desk first.</p>"
    names = list(site_choices(desk.project))
    if assembled:
        names.append("assembled")
    options = []
    for name in names:
        selected = " selected" if name == desk.site else ""
        options.append(f'<option value="{escape(name)}"{selected}>{escape(name)}</option>')
    screen_field = f'<input type="hidden" name="screen" value="{escape(screen)}">' if screen else ""
    return (
        f'<form method="post" action="/act">'
        f'<input type="hidden" name="action" value="{escape(action)}">'
        f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        f'{screen_field}'
        f'<label for="site">Site</label>'
        f'<select id="site" name="site">{"".join(options)}</select>'
        f'<button type="submit">{escape(button)}</button>'
        f'</form>'
    )


def _options(names: list[str], current: str) -> str:
    parts = []
    for name in names:
        selected = " selected" if name == current else ""
        parts.append(f'<option value="{escape(name)}"{selected}>{escape(name)}</option>')
    return "".join(parts)


def render_desk(desk: Desk) -> str:
    rows = []
    for name in PROJECTS:
        files = ", ".join(_copy_names(desk.root, name)) or "no copy files"
        brief = project_dir(desk.root, name) / "brief.md"
        try:
            context = brief.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            context = ""
        rows.append(
            f"<li><p>{escape(name)}</p><p class=\"note\">copy: {escape(files)}</p>"
            f"<pre>{escape(context)}</pre></li>"
        )
    check = "This session has not run check."
    if desk.checked:
        check = desk.checked
    body = (
        "<p>Opening this desk runs no command. It does not write HTML.</p>"
        f"<ul>{''.join(rows)}</ul>"
        f"{_project_form(desk, 'select')}"
        "<h2>Last check</h2>"
        f"<pre>{escape(check)}</pre>"
        "<h2>Doors</h2>"
        '<p><a href="/plan">Plan</a> writes structure.json and does not write HTML.</p>'
        '<p><a href="/parts">Parts</a> lists built catalog ids. Apply is a second control.</p>'
        '<p><a href="/preview">Preview</a> serves a built folder on 127.0.0.1.</p>'
        '<p><a href="/check">Check</a> runs the checker with the project and noindex.</p>'
        "<p class=\"note\">Copy, Mold, Mobile, SEO, Crew, Domains, and Score are on the list above. "
        "warmth-authority is not a choice. library bind is not a control.</p>"
    )
    return layout("spidercaster", body, desk.message, desk.error)


def render_domains(desk: Desk) -> str:
    may = []
    for name in PROJECTS:
        files = ", ".join(_copy_names(desk.root, name)) or "no copy files"
        may.append(
            f"<tr><td>{escape(name)}</td><td>{escape(files)}</td>"
            f"<td>Indexable build, a fleet host, deploy, and library bind stay refused.</td></tr>"
        )
    blocked = "".join(
        f"<tr><td>{escape(name)}</td><td>{escape(reason)}</td></tr>" for name, reason in BLOCKED
    )
    buttons = ""
    if desk.project:
        buttons = (
            f'<form method="post" action="/act">'
            f'<input type="hidden" name="action" value="plan">'
            f'<input type="hidden" name="project" value="{escape(desk.project)}">'
            f'<input type="hidden" name="frame" value="">'
            f'<input type="hidden" name="mold" value="discover-grid">'
            f'<button type="submit">Plan</button></form>'
            f'<form method="post" action="/act">'
            f'<input type="hidden" name="action" value="compose">'
            f'<input type="hidden" name="project" value="{escape(desk.project)}">'
            f'<input type="hidden" name="frame" value="">'
            f'<input type="hidden" name="mold" value="discover-grid">'
            f'<button type="submit">Compose local</button></form>'
        )
    body = (
        "<p>May stage, then Blocked. A blocked row has no button.</p>"
        f"{_project_form(desk, 'select')}"
        "<h2>May stage</h2>"
        f"<table><tr><td>Project</td><td>Copy files</td><td>Still refused</td></tr>{''.join(may)}</table>"
        f"{buttons}"
        "<p class=\"note\">Compose local writes sites/&lt;project&gt;-studio. "
        "It does not write sites/&lt;project&gt;-compose.</p>"
        "<h2>Blocked</h2>"
        f"<table>{blocked}</table>"
    )
    return layout("Staging list", body, desk.message, desk.error)


def render_copy(desk: Desk) -> str:
    from lib.ingest import load_project

    if not desk.project:
        return layout("Copy Desk", _project_form(desk, "select"), desk.message, desk.error)
    try:
        copy = load_project(project_dir(desk.root, desk.project))
    except SystemExit as exc:
        return layout("Copy Desk", f"<p>{escape(exc)}</p>", desk.message, desk.error)
    blocks = []
    for block in copy.blocks:
        name = str(block.file)
        scaffold = " scaffold" if name.lower() == "readme.md" else ""
        json_note = ""
        if name.lower().endswith(".json"):
            json_note = " The check join does not include .json."
        lines = [f"{name}{scaffold} h{block.level} {block.title}.{json_note}"]
        lines.extend(block.paragraphs)
        lines.extend(block.bullets)
        lines.extend(block.numbered)
        for qa in block.qa:
            if isinstance(qa, dict):
                lines.append(str(qa.get("q") or ""))
                lines.append(str(qa.get("a") or ""))
        for price in block.prices:
            if isinstance(price, dict):
                lines.append(str(price.get("name") or ""))
                lines.append(str(price.get("price") or ""))
        blocks.append("<pre>" + escape("\n".join(lines)) + "</pre>")
    if not blocks:
        blocks.append("<p>copy/ has no blocks; nothing was invented to fill them</p>")
    frames = _frames(desk.root)
    frame_select = _options([""] + [str(item.get("id") or "") for item in frames], desk.frame)
    structure = _load_structure(plan_dir(desk.root, desk.project) / "structure.json")
    gap_rows = ["<p>no frame selected</p>"]
    body = (
        f"<p>Project {escape(desk.project)}. This page does not save copy.</p>"
        "<h2>Context</h2>"
        f"<pre>{escape(copy.brief)}</pre>"
        "<h2>Blocks</h2>"
        + "".join(blocks)
        + "<h2>Frame</h2>"
        + '<form method="post" action="/act"><input type="hidden" name="action" value="gap">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<label for="frame">Frame</label><select id="frame" name="frame">{frame_select}</select>'
        + "<button type=\"submit\">Show gap</button></form>"
        + "<h2>Gap</h2>"
        + _gap_html(desk, frames, structure)
        + '<form method="post" action="/act"><input type="hidden" name="action" value="plan">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<label for="plan-frame">Plan frame</label><select id="plan-frame" name="frame">{frame_select}</select>'
        + '<input type="hidden" name="mold" value="discover-grid">'
        + "<button type=\"submit\">Plan</button></form>"
    )
    return layout("Copy Desk", body, desk.message, desk.error)


def _gap_html(desk: Desk, frames: list[dict], structure: dict | None) -> str:
    frame_id = desk.frame
    if not frame_id and structure and isinstance(structure.get("frame_id"), str):
        frame_id = structure["frame_id"]
    chosen = next((item for item in frames if item.get("id") == frame_id), None)
    if chosen is None:
        return "<p>no frame selected</p>"
    have: dict[str, str] = {}
    if structure:
        for _pi, _si, sec in _page_sections(structure):
            sec_type = sec.get("type") if isinstance(sec.get("type"), str) else ""
            sec_id = sec.get("id") if isinstance(sec.get("id"), str) else ""
            if sec_type and sec_type not in have:
                have[sec_type] = sec_id
    rows = []
    for sec_type in chosen.get("sections") or []:
        if structure is None:
            rows.append(f"<li>{escape(sec_type)} plan not run</li>")
        elif sec_type in have:
            rows.append(f"<li>{escape(sec_type)} kept {escape(have[sec_type])}</li>")
        else:
            rows.append(f"<li>{escape(sec_type)} missing not in copy</li>")
    return "<ul>" + "".join(rows) + "</ul>"


def render_plan(desk: Desk) -> str:
    frames = _options([""] + _frame_ids(desk.root), "")
    molds = _options(["", *MOLDS], "discover-grid")
    structure_path = plan_dir(desk.root, desk.project) / "structure.json" if desk.project else None
    data = _load_structure(structure_path) if structure_path else None
    rows = []
    if data:
        rows.append(
            f"<p>schema {escape(str(data.get('schema') or ''))}; "
            f"frame {escape(str(data.get('frame_id') or ''))}; "
            f"mold {escape(str(data.get('mold_id') or ''))}</p>"
        )
        for _pi, _si, sec in _page_sections(data):
            sid = str(sec.get("id") or "")
            rows.append(
                f"<div><p>{escape(sid)} {escape(str(sec.get('type') or ''))} "
                f"{escape(str(sec.get('part_id') or ''))}</p>"
                f'<form method="post" action="/act">'
                f'<input type="hidden" name="action" value="move">'
                f'<input type="hidden" name="direction" value="earlier">'
                f'<input type="hidden" name="project" value="{escape(desk.project)}">'
                f'<input type="hidden" name="section" value="{escape(sid)}">'
                f'<button type="submit">Move earlier</button></form>'
                f'<form method="post" action="/act">'
                f'<input type="hidden" name="action" value="move">'
                f'<input type="hidden" name="direction" value="later">'
                f'<input type="hidden" name="project" value="{escape(desk.project)}">'
                f'<input type="hidden" name="section" value="{escape(sid)}">'
                f'<button type="submit">Move later</button></form>'
                f'<form method="post" action="/act">'
                f'<input type="hidden" name="action" value="drop">'
                f'<input type="hidden" name="project" value="{escape(desk.project)}">'
                f'<input type="hidden" name="section" value="{escape(sid)}">'
                f'<button type="submit">Drop</button></form></div>'
            )
    else:
        rows.append("<p>No plan file yet.</p>")
    accepted = "plan accepted, no HTML" if desk.project in desk.accepted else "not accepted"
    choose = ""
    if not desk.project:
        choose = _project_form(desk, "select")
    body = (
        choose
        + "<p>Move earlier, Move later, and Drop change only rows already in the file. "
        + "Add section, paint from a new type, and publish are refused.</p>"
        + '<form method="post" action="/act">'
        + '<input type="hidden" name="action" value="plan">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<label for="frame">Frame</label><select id="frame" name="frame">{frames}</select>'
        + f'<label for="mold">Mold</label><select id="mold" name="mold">{molds}</select>'
        + '<button type="submit">Plan</button></form>'
        + "".join(rows)
        + f"<p>{escape(accepted)}</p>"
        + '<form method="post" action="/act"><input type="hidden" name="action" value="accept">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + '<button type="submit">Accept</button></form>'
        + '<form method="post" action="/act"><input type="hidden" name="action" value="paint">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + '<button type="submit">Paint</button></form>'
        + '<form method="post" action="/act"><input type="hidden" name="action" value="replan">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + '<label class="choice"><input type="checkbox" name="confirm" value="replace"> '
        + "Replace the plan file. Drops and order changes are gone.</label>"
        + '<button type="submit">Discard and replan</button></form>'
    )
    return layout("Plan Room", body, desk.message, desk.error)


def render_mold(desk: Desk) -> str:
    lines = []
    for mold_id in (*MOLDS, "warmth-authority"):
        data = _mold_file(desk.root, mold_id)
        from lib.mold_paint import _STACKS

        lead = str(data.get("type_lead") or "")
        stack = _STACKS.get(lead, "")
        palette = str(data.get("palette") or "")
        if mold_id == "warmth-authority":
            status = "bind refused: mold warmth-authority is already live on movelixir.com"
        else:
            status = "not live"
        lines.append(
            f"<h2>{escape(mold_id)}</h2>"
            f"<p>Palette {escape(palette)}. Type lead {escape(lead)}. {escape(stack)}</p>"
            f"<p>{escape(status)}</p>"
        )
    ledger = "".join(f"<li>{escape(line)}</li>" for line in _ledger_lines(desk.root))
    body = (
        "<p>Palette is read from the mold file. There is no Suggest control and no new hex.</p>"
        f"<ul>{ledger}</ul>"
        + "".join(lines)
        + "<p>Live bind is not a button. Paint uses the mold stored on the accepted plan.</p>"
        f'<form method="post" action="/act"><input type="hidden" name="action" value="paint">'
        f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        '<button type="submit">Paint</button></form>'
    )
    return layout("Mold Room", body, desk.message, desk.error)


def _shelf(kind: str) -> list[dict]:
    from lib.tools_index import index_rows, load_catalog

    kinds = {}
    for row in load_catalog():
        kinds[str(row.get("id") or "").strip()] = str(row.get("kind") or "")
    found = []
    for row in index_rows():
        if row.get("status") != "built":
            continue
        catalog_id = str(row.get("catalog_id") or "")
        if kinds.get(catalog_id) != kind:
            continue
        found.append({
            "catalog_id": catalog_id,
            "route": str(row.get("route") or ""),
            "kind": kind,
            "status": "built",
        })
    return found


def render_parts(desk: Desk) -> str:
    from lib.tools_index import counts, index_rows

    try:
        rows = index_rows()
        total = counts(rows)
    except Exception as exc:
        return layout("Parts Shelf", f"<p>{escape(exc)}</p>", desk.message, desk.error)
    kind_links = []
    for kind in KINDS:
        kind_links.append(
            f'<form method="post" action="/act"><input type="hidden" name="action" value="kind">'
            f'<input type="hidden" name="project" value="{escape(desk.project)}">'
            f'<input type="hidden" name="kind" value="{escape(kind)}">'
            f'<button type="submit">{escape(kind)}</button></form>'
        )
    radios = []
    try:
        shelf = _shelf(desk.kind or "header")
    except Exception as exc:
        shelf = []
        radios.append(f"<p>{escape(exc)}</p>")
    for row in shelf:
        radios.append(
            f'<label class="choice"><input type="radio" name="catalog_id" value="{escape(row["catalog_id"])}" required> '
            f'{escape(row["catalog_id"])} {escape(row["kind"])} {escape(row["route"])} built</label>'
        )
    molds = _options(["", *MOLDS], "")
    target = f"sites/{desk.project}-studio/index.html" if desk.project else "no project"
    body = (
        f"<p>Catalog rows {total['rows']}. Built {total['built']}. Missing {total['missing']}. "
        "The shelf lists six kinds. The other kinds stay off this screen. No snippet is shown.</p>"
        f"<p>Apply writes only {escape(target)}. Proven folders are not targets.</p>"
        + "".join(kind_links)
        + f'<form method="post" action="/act"><input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<label for="mold">Mold</label><select id="mold" name="mold">{molds}</select>'
        + "".join(radios)
        + '<button type="submit" name="action" value="apply">Apply</button>'
        + '<button type="submit" name="action" value="replace">Replace</button></form>'
        + "<p class=\"note\">Apply appends before &lt;/body&gt;. Replace swaps that same catalog id only.</p>"
    )
    return layout("Parts Shelf", body, desk.message, desk.error)


def _frames_html(desk: Desk, widths: tuple[int, ...]) -> str:
    if not desk.preview_port:
        return "<p>Serve has not been started.</p>"
    heights = {360: 740, 390: 844, 412: 915, 1280: 800}
    blocks = []
    for width in widths:
        height = heights.get(width, 800)
        src = f"http://127.0.0.1:{desk.preview_port}/"
        blocks.append(
            f'<div class="slot"><p>{width}</p>'
            f'<iframe title="{width}" src="{src}" width="{width}" height="{height}"></iframe></div>'
        )
    return "".join(blocks)


def render_preview(desk: Desk) -> str:
    address = "Serve has not been started."
    if desk.preview_port:
        address = f"http://127.0.0.1:{desk.preview_port}/"
    width_buttons = []
    for width in WIDTHS:
        width_buttons.append(
            f'<form method="post" action="/act"><input type="hidden" name="action" value="width">'
            f'<input type="hidden" name="project" value="{escape(desk.project)}">'
            f'<input type="hidden" name="width" value="{width}">'
            f'<button type="submit">{width}</button></form>'
        )
    body = (
        "<p>NOINDEX. Staged. The address is 127.0.0.1. A ledger host is not a link.</p>"
        + _site_form(desk, "serve", assembled=True, button="Serve")
        + f"<p>{escape(address)}</p>"
        + "".join(width_buttons)
        + _frames_html(desk, (desk.width,))
        + '<form method="post" action="/act"><input type="hidden" name="action" value="check">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<input type="hidden" name="site" value="{escape(desk.site)}">'
        + '<button type="submit">Check</button></form>'
        + '<form method="post" action="/act"><input type="hidden" name="action" value="visit">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<input type="hidden" name="site" value="{escape(desk.site)}">'
        + '<button type="submit">Visit</button></form>'
        + '<form method="post" action="/act"><input type="hidden" name="action" value="stop">'
        + '<button type="submit">Stop</button></form>'
        + "<h2>Check</h2><pre>"
        + escape(desk.checked or "Check has not been run.")
        + "</pre><h2>Visit</h2><pre>"
        + escape(_visit_text(desk))
        + "</pre>"
    )
    return layout("Staged preview", body, desk.message, desk.error)


def render_mobile(desk: Desk) -> str:
    from lib.check import failure_line

    lists = []
    wanted = {
        "Overflow": "sideways_scroll",
        "Tap": "tap_target",
        "Type": "type_floor",
        "Drawer": "mobile_nav_drawer",
    }
    by_name = {str(row.get("name")): row for row in desk.rows}
    for label, name in wanted.items():
        row = by_name.get(name)
        if row is None:
            lists.append(f"<h2>{label}</h2><p>not run</p>")
            continue
        status = str(row.get("status") or "")
        lines = [f"[{status}] {row.get('detail') or ''}"]
        for failure in row.get("failures") or []:
            if isinstance(failure, dict):
                lines.append(failure_line(failure))
        lists.append(f"<h2>{label}</h2><pre>{escape(chr(10).join(lines))}</pre>")
    if desk.visit:
        mode = str(desk.visit.get("mode") or "")
        note = "rendered" if mode == "rendered" else "static is not a measure at 390 and 1280"
        lists.append(f"<p>visit mode {escape(mode)}. {escape(note)}</p>")
    body = (
        "<p>Three widths stay on screen. The stage has no Menu button. It does not build.</p>"
        + _site_form(desk, "serve", assembled=True, button="Show page", screen="mobile")
        + '<form method="post" action="/act"><input type="hidden" name="action" value="read">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<input type="hidden" name="site" value="{escape(desk.site)}">'
        + '<button type="submit">Read failures</button></form>'
        + _frames_html(desk, (360, 390, 1280))
        + "".join(lists)
    )
    return layout("Mobile Stage", body, desk.message, desk.error)


def _row_lines(row: dict) -> str:
    from lib.check import failure_line

    lines = [f"[{row.get('status')}] {row.get('name')} {row.get('detail') or ''}"]
    for failure in row.get("failures") or []:
        if isinstance(failure, dict):
            lines.append(failure_line(failure))
    return "\n".join(lines)


def _groups_html(desk: Desk) -> str:
    if not desk.rows:
        return "<p>Check has not been run.</p>"
    grouped = _group_rows(desk.rows)
    only = _only_files_present(desk.rows)
    blocks = []
    claim_names = {"ungrounded_claim", "lone_about", "invented_chrome"}
    for name, _members in GROUPS:
        rows = grouped[name]
        if only and name != "Copy" and name != "Crawl" or only and name == "Copy":
            word = "not run"
            detail = "<p>not run</p>"
        else:
            word = _group_word(rows)
            detail = "<pre>" + escape("\n\n".join(_row_lines(row) for row in rows)) + "</pre>"
            if name == "Copy" and desk.project and not any(row.get("name") in claim_names for row in rows):
                detail += "<p>no claim row</p>"
        blocks.append(f"<h2>{escape(name)} {escape(word)}</h2>{detail}")
    fails = int(desk.counts.get("FAIL") or 0)
    if not desk.rows:
        nxt = "Next is stopped. Check has not been run."
    elif fails:
        nxt = "Next is stopped."
    else:
        nxt = "Check passed. The site is still noindex."
    counts = desk.counts
    summary = (
        f"result: {counts.get('PASS', 0)} pass / {counts.get('FAIL', 0)} fail / "
        f"{counts.get('WARN', 0)} warn / {counts.get('SKIP', 0)} skip"
    )
    return f"<p>{escape(summary)}</p><p>{escape(nxt)}</p>" + "".join(blocks)


def render_check(desk: Desk) -> str:
    body = (
        "<p>A fail stops Next. Skip stays skip. grey_tile is a skip. Warn is not a pass.</p>"
        + _site_form(desk, "check", button="Check")
        + '<form method="post" action="/act"><input type="hidden" name="action" value="check">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<input type="hidden" name="site" value="{escape(desk.site)}">'
        + '<button type="submit">Re-check</button></form>'
        + _site_form(desk, "serve", button="Look")
        + '<form method="post" action="/act"><input type="hidden" name="action" value="visit">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<input type="hidden" name="site" value="{escape(desk.site)}">'
        + '<button type="submit">Measure</button></form>'
        + _groups_html(desk)
        + "<h2>Visit</h2><pre>"
        + escape(_visit_text(desk))
        + "</pre>"
    )
    return layout("Check Board", body, desk.message, desk.error)


def _visit_text(desk: Desk) -> str:
    if not desk.visit:
        return "Visit has not been run."
    mode = str(desk.visit.get("mode") or "")
    lines = [f"mode: {mode}"]
    if mode != "rendered":
        lines.append("static is not a measure at 390 and 1280")
    for failure in desk.visit.get("failures") or []:
        if isinstance(failure, dict):
            lines.append(f"{failure.get('code', '')}: {failure.get('detail', '')}")
    return "\n".join(lines)


def render_seo(desk: Desk) -> str:
    folder = resolve_site(desk.root, desk.project, desk.site) if desk.project and desk.site else None
    if folder is None or not (folder / "index.html").is_file():
        body = (
            "<p>This desk does not clear noindex and does not write a sitemap.</p>"
            "<p>Choose a built folder. A plan folder has no meta tag and no sitemap.</p>"
            + _site_form(desk, "select-site", button="Open")
        )
        return layout("SEO Desk", body, desk.message, desk.error)
    index = (folder / "index.html").read_text(encoding="utf-8", errors="replace")
    robots_meta = _ROBOTS.search(index)
    desc = _META_DESC.search(index)
    report = _load_structure(folder / "report.json") or {}
    robots_path = folder / "robots.txt"
    robots_text = robots_path.read_text(encoding="utf-8", errors="replace") if robots_path.is_file() else "missing"
    sitemap = "Present" if (folder / "sitemap.xml").is_file() else "Absent"
    from lib.heading_rank import heading_skips

    skips = heading_skips(index)
    from lib.seo_pack import descriptions_by_stem

    stems = {}
    if desk.project:
        stems = descriptions_by_stem(project_dir(desk.root, desk.project))
    if stems:
        source = "Description: line in copy"
    else:
        source = "site.json meta.description, or the hero paragraph the offline planner stored"
    body = (
        "<p>This desk does not clear noindex and does not write a sitemap. "
        "A human can run build --offline --indexable --host in a terminal. "
        "That command is not a button here, because it drops composed parts and it is not a rank.</p>"
        f"<p>robots meta: {escape(robots_meta.group(1) if robots_meta else 'missing')}</p>"
        f"<p>report.json noindex: {escape(str(report.get('noindex')))}</p>"
        f"<h2>robots.txt</h2><pre>{escape(robots_text)}</pre>"
        f"<p>Sitemap: {escape(sitemap)}</p>"
        f"<p>Description source: {escape(source)}</p>"
        f"<pre>{escape(desc.group(1) if desc else 'missing')}</pre>"
        f"<p>Heading skips: {escape(', '.join(skips) if skips else 'none')}</p>"
        + _site_form(desk, "check", button="Check again")
    )
    return layout("SEO Desk", body, desk.message, desk.error)


def render_crew(desk: Desk) -> str:
    from lib.crew import ROLES
    from lib.doctor import report

    data = report(desk.root)
    doctor = "ok" if data.get("ok") else "not ok: " + "; ".join(data.get("errors") or [])
    rows = []
    for role in ROLES:
        hands = ", ".join(role["hands"])
        rows.append(
            f"<li>{role['n']} {escape(role['id'])} {escape(role['label'])}. "
            f"Hands: {escape(hands)}. Does not: {escape(role['does_not'])}. Status: not run</li>"
        )
    body = (
        f"<p>Doctor: {escape(doctor)}</p>"
        "<p>Run crew is refused. crew run writes a draft ledger row through library_bind. "
        "This studio does not write library/ledger.json. There is no Publish control.</p>"
        f"<ol>{''.join(rows)}</ol>"
    )
    return layout("Crew Board", body, desk.message, desk.error)


def render_score(desk: Desk) -> str:
    fresh = (
        f'<form method="post" action="/act"><input type="hidden" name="action" value="compose">'
        f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        f'<input type="hidden" name="frame" value="">'
        f'<input type="hidden" name="mold" value="discover-grid">'
        f'<button type="submit">Compose</button></form>'
    )
    body = (
        "<p>A row is PASS only when every child row is PASS. WARN and SKIP block PASS. "
        "This is not a rank.</p>"
        + _project_form(desk, "select")
        + fresh
        + _site_form(desk, "check", button="Check")
        + '<form method="post" action="/act"><input type="hidden" name="action" value="visit">'
        + f'<input type="hidden" name="project" value="{escape(desk.project)}">'
        + f'<input type="hidden" name="site" value="{escape(desk.site)}">'
        + '<button type="submit">Visit</button></form>'
        + _groups_html(desk)
        + "<h2>Visit</h2><pre>" + escape(_visit_text(desk)) + "</pre>"
        + "<p class=\"note\">robots.txt and sitemap are read on the SEO desk. They are not a checker status.</p>"
    )
    return layout("4Cs+ Scorecard", body, desk.message, desk.error)


RENDER = {
    "/": render_desk,
    "/copy": render_copy,
    "/plan": render_plan,
    "/mold": render_mold,
    "/parts": render_parts,
    "/mobile": render_mobile,
    "/check": render_check,
    "/seo": render_seo,
    "/crew": render_crew,
    "/preview": render_preview,
    "/domains": render_domains,
    "/score": render_score,
}


def _set_project(desk: Desk, form: dict) -> str:
    project = (form.get("project") or desk.project or "").strip()
    if not project:
        desk.error = "Choose a project."
        return ""
    if project not in PROJECTS or not _token(project):
        desk.error = "refused: that project is not a copy pack"
        desk.message = ""
        return ""
    desk.project = project
    return project


def _run_check(desk: Desk, folder: Path) -> None:
    from lib.check import check_site
    from lib.copy_pack import project_copy_text

    report = check_site(
        folder,
        expect_noindex=True,
        quiet=True,
        copy_text=project_copy_text(project_dir(desk.root, desk.project)),
    )
    desk.rows = list(report.rows)
    desk.counts = report.counts()
    lines = [_row_lines(row) for row in desk.rows]
    c = desk.counts
    lines.append(
        f"result: {c.get('PASS', 0)} pass / {c.get('FAIL', 0)} fail / "
        f"{c.get('WARN', 0)} warn / {c.get('SKIP', 0)} skip"
    )
    desk.checked = "\n".join(lines)


def _run_visit(desk: Desk, folder: Path) -> None:
    from lib.visit_check import visit_site

    desk.visit = visit_site(folder)


def _compose(desk: Desk, project: str, frame: str, mold: str, plan_only: bool, accepted: Path | None) -> dict:
    from lib.compose import compose_project

    dest = plan_dir(desk.root, project) if plan_only else studio_dir(desk.root, project)
    if plan_only and (dest / "index.html").is_file():
        return {"ok": False, "error": "Plan refused: index.html is already in the plan folder."}
    return compose_project(
        project_dir(desk.root, project),
        dest,
        frame,
        mold,
        plan_only=plan_only,
        accepted=accepted,
    )


def act(desk: Desk, form: dict) -> str:
    action = (form.get("action") or "").strip()
    desk.error = ""
    desk.message = ""
    for key in ("project", "frame", "mold", "site", "section", "kind", "catalog_id"):
        value = form.get(key) or ""
        if value and not _token(value):
            desk.error = "nothing was invented to fill them"
            return "/"
    if action == "select":
        project = _set_project(desk, form)
        if project:
            desk.message = project
        return "/"
    if action == "select-site":
        project = _set_project(desk, form)
        site = form.get("site") or ""
        if project and resolve_site(desk.root, project, site, assembled=True):
            desk.site = site
        elif project:
            desk.error = "That folder is not a staged site for this project."
        return "/seo"
    if action == "kind":
        _set_project(desk, form)
        kind = form.get("kind") or ""
        if kind not in KINDS:
            desk.error = "That kind stays off the shelf."
        else:
            desk.kind = kind
        return "/parts"
    if action == "width":
        try:
            width = int(form.get("width") or "0")
        except ValueError:
            width = 0
        if width not in WIDTHS:
            desk.error = "That width is not a checker window."
        else:
            desk.width = width
        return "/preview"
    if action == "stop":
        desk.stop_preview()
        desk.message = "Preview stopped."
        return "/preview"
    if action in {"plan", "replan", "compose", "paint", "accept", "move", "drop", "gap"}:
        project = _set_project(desk, form)
        if not project:
            return "/plan" if action != "gap" else "/copy"
        frame = (form.get("frame") or "").strip()
        mold = (form.get("mold") or "").strip()
        if mold == "warmth-authority":
            desk.error = "bind refused: mold warmth-authority is already live on movelixir.com"
            return "/mold"
        if mold and mold not in MOLDS:
            desk.error = "That mold is not a studio choice."
            return "/mold"
        if frame and frame not in _frame_ids(desk.root):
            desk.error = f"unknown frame {frame}"
            return "/plan"
        if action == "gap":
            desk.frame = frame
            return "/copy"
        if action == "replan":
            if form.get("confirm") != "replace":
                desk.error = "Discard and replan stays refused until the replace box is checked."
                return "/plan"
            frame = ""
            mold = "discover-grid"
            path = plan_dir(desk.root, project) / "structure.json"
            previous = _load_structure(path)
            if previous:
                frame = str(previous.get("frame_id") or "")
                mold = str(previous.get("mold_id") or "") or "discover-grid"
            if mold == "warmth-authority":
                desk.error = "bind refused: mold warmth-authority is already live on movelixir.com"
                return "/mold"
            result = _compose(desk, project, frame, mold, True, None)
            desk.accepted.discard(project)
            if not result.get("ok"):
                desk.error = str(result.get("error") or "plan failed")
            else:
                desk.message = "plan replaced. Drops and order changes are gone. No HTML."
            return "/plan"
        if action == "plan":
            result = _compose(desk, project, frame, mold, True, None)
            desk.accepted.discard(project)
            if not result.get("ok"):
                desk.error = str(result.get("error") or "plan failed")
            else:
                desk.message = "plan written, no HTML"
            return "/plan"
        if action == "compose":
            if project in desk.accepted:
                action = "paint"
            else:
                result = _compose(desk, project, frame, mold, False, None)
                if not result.get("ok"):
                    desk.error = str(result.get("error") or "compose failed")
                else:
                    desk.site = f"{project}-studio"
                    desk.message = "composed from copy. noindex. not a rank."
                return "/score"
        if action == "accept":
            path = plan_dir(desk.root, project) / "structure.json"
            if not path.is_file():
                desk.error = "Accept refused: there is no plan file."
            else:
                desk.accepted.add(project)
                desk.message = "plan accepted, no HTML"
            return "/plan"
        if action == "paint":
            path = plan_dir(desk.root, project) / "structure.json"
            if project not in desk.accepted or not path.is_file():
                desk.error = "Paint refused until Accept. The plan file is the only section list."
                return "/plan"
            data = _load_structure(path) or {}
            frame = str(data.get("frame_id") or "")
            mold = str(data.get("mold_id") or "")
            if mold == "warmth-authority":
                desk.error = "bind refused: mold warmth-authority is already live on movelixir.com"
                return "/mold"
            result = _compose(desk, project, frame, mold, False, path)
            if not result.get("ok"):
                desk.error = str(result.get("error") or "paint failed")
            else:
                desk.site = f"{project}-studio"
                desk.message = "painted from the accepted plan. noindex. not a rank."
            return "/plan"
        if action in {"move", "drop"}:
            path = plan_dir(desk.root, project) / "structure.json"
            data = _load_structure(path)
            section = form.get("section") or ""
            if data is None:
                desk.error = "There is no plan file."
                return "/plan"
            pages = data.get("pages") if isinstance(data.get("pages"), list) else []
            found = None
            for pi, page in enumerate(pages):
                if not isinstance(page, dict):
                    continue
                sections = page.get("sections") if isinstance(page.get("sections"), list) else []
                for si, sec in enumerate(sections):
                    if isinstance(sec, dict) and sec.get("id") == section:
                        found = (pi, si, sections)
                        break
            if found is None:
                desk.error = "That section is not on the plan."
                return "/plan"
            pi, si, sections = found
            if action == "drop":
                sections.pop(si)
                desk.message = f"dropped {section}"
            else:
                direction = form.get("direction") or ""
                if direction == "earlier" and si == 0:
                    desk.message = "already first"
                    return "/plan"
                if direction == "later" and si == len(sections) - 1:
                    desk.message = "already last"
                    return "/plan"
                if direction == "earlier":
                    sections[si - 1], sections[si] = sections[si], sections[si - 1]
                    desk.message = f"moved {section} earlier"
                elif direction == "later":
                    sections[si + 1], sections[si] = sections[si], sections[si + 1]
                    desk.message = f"moved {section} later"
                else:
                    desk.error = "Move needs earlier or later."
                    return "/plan"
            _save_plan(path, data)
            desk.accepted.discard(project)
            return "/plan"
    if action in {"check", "visit", "serve", "read", "apply", "replace"}:
        project = _set_project(desk, form)
        if not project:
            return "/check"
        site_name = (form.get("site") or desk.site or "").strip()
        assembled = action in {"serve", "read"}
        folder = resolve_site(desk.root, project, site_name, assembled=assembled)
        if action in {"apply", "replace"}:
            folder = studio_dir(desk.root, project)
            site_name = f"{project}-studio"
        if folder is None:
            desk.error = "That folder is not a staged site for this project."
            return "/check"
        desk.site = site_name
        if action == "check" or action == "read":
            if site_name == "assembled":
                desk.error = "Check needs a copy project. assembled is the catalog."
                return "/mobile" if action == "read" else "/check"
            if not (folder / "index.html").is_file():
                desk.rows = [{"name": "files_present", "status": "FAIL", "detail": f"missing {folder / 'index.html'}"}]
                desk.counts = {"PASS": 0, "FAIL": 1, "WARN": 0, "SKIP": 0}
                desk.checked = f"[FAIL] files_present missing {folder / 'index.html'}"
                desk.error = "Check refused to fill the other groups."
            else:
                _run_check(desk, folder)
                if action == "read":
                    _run_visit(desk, folder)
                desk.message = "check finished. a fail stays a fail."
            return "/mobile" if action == "read" else "/check"
        if action == "visit":
            if not (folder / "index.html").is_file():
                desk.error = f"no index.html in {folder.name}; run a build first"
            else:
                _run_visit(desk, folder)
                mode = str(desk.visit.get("mode") or "")
                desk.message = f"visit mode {mode}"
            return "/check"
        if action == "serve":
            reason = _preview_block(folder)
            if reason:
                desk.error = reason
            else:
                try:
                    port = desk.start_preview(folder)
                except Exception as exc:
                    desk.error = str(exc)
                else:
                    desk.message = f"http://127.0.0.1:{port}/"
            return "/preview" if form.get("screen") != "mobile" else "/mobile"
        if action in {"apply", "replace"}:
            page = folder / "index.html"
            if not page.is_file():
                desk.error = "Paint a page first. Apply does not invent one."
                return "/parts"
            catalog_id = form.get("catalog_id") or ""
            kind = desk.kind if desk.kind in KINDS else ""
            try:
                shelf = _shelf(kind)
            except Exception as exc:
                desk.error = str(exc)
                return "/parts"
            if not any(row["catalog_id"] == catalog_id for row in shelf):
                desk.error = "That id is not a built row of the selected kind."
                return "/parts"
            mold = None
            mold_id = form.get("mold") or ""
            if mold_id:
                data = _mold_file(desk.root, mold_id)
                mold = {"palette": data.get("palette") or "", "type_lead": data.get("type_lead") or ""}
            from lib.tools_apply import ToolsApplyError, apply_part

            try:
                apply_part(
                    catalog_id,
                    page,
                    page,
                    replace=action == "replace",
                    mold=mold,
                    project=project_dir(desk.root, project),
                )
            except ToolsApplyError as exc:
                desk.error = str(exc)
                return "/parts"
            _run_check(desk, folder)
            if action == "replace":
                desk.message = "swapped the same catalog id. applied is not a check pass."
            else:
                desk.message = "appended before </body>. applied is not a check pass."
            return "/parts"
    desk.error = "That control is refused."
    return "/"


def serve_studio(port: int = STUDIO_PORT, attempts: int = 20, root: Path | None = None):
    desk = Desk(root)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/act":
                self._send(405, "POST only")
                return
            render = RENDER.get(path)
            if render is None:
                self._send(404, "not found")
                return
            try:
                html = render(desk)
            except Exception as exc:
                html = layout("spidercaster", f"<p>{escape(exc)}</p>", "", "The room failed.")
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Robots-Tag", "noindex, nofollow")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if urlparse(self.path).path != "/act":
                self._send(404, "not found")
                return
            length = int(self.headers.get("Content-Length") or "0")
            if length > 65536:
                self._send(413, "too large")
                return
            raw = self.rfile.read(length).decode("utf-8", "replace")
            form = _form(parse_qs(raw, keep_blank_values=True))
            try:
                target = act(desk, form)
            except Exception as exc:
                desk.error = str(exc)
                target = "/"
            self.send_response(303)
            self.send_header("Location", target or "/")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _send(self, status: int, text: str) -> None:
            body = text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args) -> None:
            return

    if port == 0:
        httpd = ThreadingTCPServer(("127.0.0.1", 0), Handler)
        httpd.daemon_threads = True
        return httpd, httpd.server_address[1]
    last = None
    for candidate in range(port, port + attempts):
        try:
            httpd = ThreadingTCPServer(("127.0.0.1", candidate), Handler)
            httpd.daemon_threads = True
            return httpd, candidate
        except OSError as exc:
            last = exc
    raise RuntimeError(f"no free port in {port}..{port + attempts - 1} ({last})")
