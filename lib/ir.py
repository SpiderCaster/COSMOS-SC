"""SpiderCaster IR: the normalized site.json intermediate representation.

Everything the renderer consumes goes through normalize_site() so both the
zero-token offline planner and the LLM planner produce the same shape.
House rules baked in: no invented content downstream, noindex by default,
secrets never touch this file.
"""
from __future__ import annotations

import re
from datetime import date

SECTION_TYPES = [
    "hero", "features", "stats", "steps", "gallery", "pricing", "testimonials",
    "faq", "cta", "contact", "about", "team", "menu", "logocloud",
]

ICON_NAMES = [
    "zap", "shield", "heart", "star", "check", "code", "cloud", "lock", "pulse",
    "globe", "sparkles", "layers", "cpu", "camera", "mail", "map", "users",
    "clock", "trending", "phone", "pin", "terminal", "browser", "database",
    "server", "palette", "layout", "feather", "compass", "award", "rocket",
    "box", "arrow_right", "refresh", "search", "sliders",
]

TEMPLATES = ["modern", "editorial", "bold"]


def s(v) -> str:
    if isinstance(v, str):
        return v.strip()
    if v is None:
        return ""
    return str(v).strip()


def is_str(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def slugify(v) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", str(v or "").lower()).strip("-")
    return out[:40]


def hex6(v):
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", str(v or "").strip())
    return "#" + m.group(1).lower() if m else None


def clamp(lst, n):
    return lst[:n] if isinstance(lst, list) else []


def pick_icon(v) -> str:
    name = s(v).lower()
    return name if name in ICON_NAMES else "sparkles"


def link_obj(v):
    if not isinstance(v, dict):
        return None
    label = s(v.get("label"))
    if not label:
        return None
    return {"label": label, "href": s(v.get("href")) or "#"}


def title_case(v) -> str:
    return re.sub(r"\b\w", lambda m: m.group(0).upper(), re.sub(r"[-_]+", " ", str(v or "")))


# ---------------------------------------------------------------- data shapes

def normalize_data(kind: str, d: dict) -> dict:
    d = d if isinstance(d, dict) else {}
    out: dict = {}

    if kind == "hero":
        out["eyebrow"] = s(d.get("eyebrow"))
        # Strict gap-gate: no invented headline. An empty headline stays
        # empty here; copy_schema.validate_site() FAILs gap hero.headline.
        out["headline"] = s(d.get("headline"))
        out["subhead"] = s(d.get("subhead"))
        out["primary"] = link_obj(d.get("primary"))
        out["secondary"] = link_obj(d.get("secondary"))
        out["bullets"] = [s(b) for b in clamp(d.get("bullets"), 4) if is_str(b)]
        raw_img = d.get("image")
        src = s(raw_img) if isinstance(raw_img, str) else ""
        alt = ""
        if isinstance(raw_img, dict):
            src = s(raw_img.get("src"))
            alt = s(raw_img.get("alt"))
        parts = src.replace("\\", "/").split("/")
        if src.startswith(("http://", "https://", "//")) or ".." in parts:
            src = ""
        out["image"] = src
        out["image_alt"] = alt

    elif kind == "features":
        out["title"] = s(d.get("title"))
        out["subhead"] = s(d.get("subhead"))
        items = []
        for it in clamp(d.get("items"), 8):
            if isinstance(it, dict) and is_str(it.get("title")):
                items.append({"icon": pick_icon(it.get("icon")), "title": s(it.get("title")), "body": s(it.get("body"))})
        out["items"] = items

    elif kind == "stats":
        out["title"] = s(d.get("title"))
        items = []
        for it in clamp(d.get("items"), 6):
            if isinstance(it, dict) and (is_str(it.get("value")) or is_str(it.get("label"))):
                items.append({"value": s(it.get("value")), "label": s(it.get("label"))})
        out["items"] = items

    elif kind == "steps":
        out["title"] = s(d.get("title"))
        out["subhead"] = s(d.get("subhead"))
        items = []
        for it in clamp(d.get("items"), 6):
            if isinstance(it, dict) and is_str(it.get("title")):
                items.append({"title": s(it.get("title")), "body": s(it.get("body"))})
        out["items"] = items

    elif kind == "gallery":
        out["title"] = s(d.get("title"))
        out["subhead"] = s(d.get("subhead"))
        items = []
        for it in clamp(d.get("items"), 12):
            if isinstance(it, str) and it.strip():
                it = {"label": it}
            if isinstance(it, dict) and (is_str(it.get("label")) or is_str(it.get("caption")) or is_str(it.get("src"))):
                items.append({
                    "label": s(it.get("label")),
                    "caption": s(it.get("caption")),
                    "src": s(it.get("src")),
                    "alt": s(it.get("alt")),
                    "hue": it.get("hue") if isinstance(it.get("hue"), (int, float)) else None,
                })
        out["items"] = items

    elif kind == "pricing":
        out["title"] = s(d.get("title"))
        out["subhead"] = s(d.get("subhead"))
        items = []
        for it in clamp(d.get("items"), 4):
            if isinstance(it, dict) and is_str(it.get("name")):
                items.append({
                    "name": s(it.get("name")),
                    "price": s(it.get("price")),
                    "period": s(it.get("period")),
                    "blurb": s(it.get("blurb")),
                    "features": [s(f) for f in clamp(it.get("features"), 6) if is_str(f)],
                    "featured": it.get("featured") is True,
                    "badge": s(it.get("badge")),
                    "cta": link_obj(it.get("cta")),
                })
        out["items"] = items

    elif kind == "testimonials":
        out["title"] = s(d.get("title"))
        items = []
        for it in clamp(d.get("items"), 6):
            if isinstance(it, dict) and is_str(it.get("quote")):
                items.append({"quote": s(it.get("quote")), "name": s(it.get("name")), "role": s(it.get("role"))})
        out["items"] = items

    elif kind == "faq":
        out["title"] = s(d.get("title"))
        out["subhead"] = s(d.get("subhead"))
        items = []
        for it in clamp(d.get("items"), 8):
            if isinstance(it, dict) and is_str(it.get("q")):
                items.append({"q": s(it.get("q")), "a": s(it.get("a"))})
        out["items"] = items

    elif kind == "cta":
        # Strict gap-gate: no invented title or button. Empty stays empty;
        # an optional cta with nothing real is omitted by normalize_site().
        out["title"] = s(d.get("title"))
        out["body"] = s(d.get("body"))
        out["primary"] = link_obj(d.get("primary"))
        out["secondary"] = link_obj(d.get("secondary"))

    elif kind == "contact":
        out["title"] = s(d.get("title"))
        out["body"] = s(d.get("body"))
        out["email"] = s(d.get("email"))
        out["phone"] = s(d.get("phone"))
        out["address"] = s(d.get("address"))
        out["hours"] = s(d.get("hours"))

    elif kind == "about":
        out["title"] = s(d.get("title"))
        body = d.get("body")
        if isinstance(body, list):
            out["body"] = [s(b) for b in clamp(body, 4) if is_str(b)]
        elif is_str(body):
            out["body"] = [s(body)]
        else:
            out["body"] = []
        points = []
        for p in clamp(d.get("points"), 4):
            if isinstance(p, dict) and is_str(p.get("title")):
                points.append({"title": s(p.get("title")), "body": s(p.get("body"))})
        out["points"] = points

    elif kind == "team":
        out["title"] = s(d.get("title"))
        out["subhead"] = s(d.get("subhead"))
        items = []
        for it in clamp(d.get("items"), 8):
            if isinstance(it, dict) and is_str(it.get("name")):
                items.append({"name": s(it.get("name")), "role": s(it.get("role")), "bio": s(it.get("bio"))})
        out["items"] = items

    elif kind == "menu":
        out["title"] = s(d.get("title"))
        out["subhead"] = s(d.get("subhead"))
        groups = []
        for g in clamp(d.get("groups"), 4):
            if not isinstance(g, dict):
                continue
            items = []
            for it in clamp(g.get("items"), 8):
                if isinstance(it, dict) and is_str(it.get("name")):
                    items.append({"name": s(it.get("name")), "desc": s(it.get("desc")), "price": s(it.get("price"))})
            if items:
                groups.append({"name": s(g.get("name")), "items": items})
        out["groups"] = groups

    elif kind == "logocloud":
        out["title"] = s(d.get("title"))
        out["items"] = [s(i) for i in clamp(d.get("items"), 8) if is_str(i)]

    # D5 mobile block (FINAL MERGE): optional per-section phone design data,
    # extended in place on the section — no new section taxonomy. Preserved
    # verbatim (JSON scalars only) so --from rebuilds keep it and the
    # mobile_block gate row can judge it strictly.
    mob = d.get("mobile")
    if isinstance(mob, dict):
        clean: dict = {}
        for key, value in mob.items():
            if not isinstance(key, str):
                continue
            if isinstance(value, bool) or isinstance(value, (int, float, str)):
                clean[key] = value
        if clean:
            out["mobile"] = clean

    return out


def normalize_section(raw, seen_ids: set):
    if not isinstance(raw, dict):
        return None
    kind = s(raw.get("type")).lower()
    if kind not in SECTION_TYPES:
        return None
    sec_id = slugify(raw.get("id")) or kind
    base_id = sec_id
    n = 2
    while sec_id in seen_ids:
        sec_id = f"{base_id}-{n}"
        n += 1
    seen_ids.add(sec_id)
    data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
    sec = {"id": sec_id, "type": kind, "data": normalize_data(kind, data)}
    # Carry the planner's source file through normalize so --from rebuilds
    # can re-slice the cited span. The renderer ignores this key.
    if isinstance(raw.get("_source"), str) and raw.get("_source"):
        sec["_source"] = raw["_source"]
    return sec


def _section_has_content(kind: str, data: dict) -> bool:
    """True when an optional section has something real to render.

    Optional miss = omit: normalize_site() drops sections with no content
    instead of emitting hollow markup. hero is never dropped here; an
    empty headline is a gap FAIL raised by the caller.
    """
    if not isinstance(data, dict):
        return False
    if kind == "hero":
        return True
    if kind in ("features", "stats", "steps", "testimonials", "team"):
        return bool(data.get("items"))
    if kind == "faq":
        return bool(data.get("items"))
    if kind == "pricing":
        return bool(data.get("items"))
    if kind == "menu":
        return bool(data.get("groups"))
    if kind == "gallery":
        return bool(data.get("items"))
    if kind == "logocloud":
        return bool(data.get("items"))
    if kind == "contact":
        return any(str(data.get(k) or "").strip()
                   for k in ("title", "body", "email", "phone", "address", "hours"))
    if kind == "cta":
        return bool(str(data.get("title") or "").strip()
                    or str(data.get("body") or "").strip()
                    or data.get("primary"))
    if kind == "about":
        return bool(data.get("body") or data.get("points") or str(data.get("title") or "").strip())
    return bool(data)


def normalize_site(raw: dict, opts: dict | None = None) -> dict:
    opts = opts or {}
    raw = raw if isinstance(raw, dict) else {}
    today = date.today()
    brand = s(opts.get("brand")) or s((raw.get("meta") or {}).get("title")) or "Local Build"

    meta_in = raw.get("meta") if isinstance(raw.get("meta"), dict) else {}
    site = {
        "version": 1,
        "generator": "spidercaster/0.1",
        "brief": s(opts.get("brief") or raw.get("brief")),
        "meta": {
            "title": s(meta_in.get("title")) or brand,
            "description": (s(meta_in.get("description")) or f"{brand} - local build by SpiderCaster")[:155],
            "lang": s(meta_in.get("lang")) or "en",
        },
    }

    theme_in = raw.get("theme") if isinstance(raw.get("theme"), dict) else {}
    template = theme_in.get("template") if theme_in.get("template") in TEMPLATES else None
    if not template and opts.get("template") in TEMPLATES:
        template = opts.get("template")
    dark = theme_in.get("dark")
    if not isinstance(dark, bool):
        dark = opts.get("dark") if isinstance(opts.get("dark"), bool) else True
    site["theme"] = {
        "template": template or "modern",
        "dark": dark,
        "accent": hex6(theme_in.get("accent")),
        "accent2": hex6(theme_in.get("accent2")),
    }

    site["nav"] = [lo for lo in (link_obj(n) for n in clamp(raw.get("nav"), 7)) if lo]

    pages_in = raw.get("pages") if isinstance(raw.get("pages"), list) and raw.get("pages") else None
    if not pages_in:
        pages_in = [{"slug": "index", "title": site["meta"]["title"],
                     "sections": raw.get("sections") if isinstance(raw.get("sections"), list) else []}]
    seen_ids: set = set()
    pages = []
    for pi, p in enumerate(clamp(pages_in, 5)):
        p = p if isinstance(p, dict) else {}
        normalized = [sec for sec in (normalize_section(x, seen_ids) for x in clamp(p.get("sections"), 12)) if sec]
        # Optional miss = omit: drop hollow optional sections. hero is kept
        # even when empty so the gap gate can name hero.headline.
        sections = [sec for sec in normalized if _section_has_content(sec["type"], sec["data"])]
        pages.append({
            "slug": slugify(p.get("slug")) or ("index" if pi == 0 else f"page-{pi + 1}"),
            "title": s(p.get("title")) or site["meta"]["title"],
            "sections": sections,
        })
    if not pages:
        pages = [{"slug": "index", "title": site["meta"]["title"], "sections": []}]
    pages[0]["slug"] = "index"
    # Strict gap-gate: no invented hero/about when the planner produced no
    # sections. An empty index page stays empty; the caller FAILs
    # gap hero.headline instead of rendering a substitute sentence.
    site["pages"] = pages

    # Auto-nav from section titles when the planner skipped it.
    if not site["nav"]:
        nav = []
        for sec in pages[0]["sections"]:
            if sec["type"] in ("hero", "cta"):
                continue
            label = s(sec["data"].get("title"))
            if not label:
                continue
            nav.append({"label": label, "href": f"#{sec['id']}"})
        site["nav"] = nav[:6]

    foot_in = raw.get("footer") if isinstance(raw.get("footer"), dict) else {}
    site["footer"] = {
        "text": s(foot_in.get("text")) or f"(c) {today.year} {site['meta']['title']}",
        "links": [lo for lo in (link_obj(l) for l in clamp(foot_in.get("links"), 6)) if lo],
        "credit": foot_in.get("credit") is not False,
    }
    # Preserve the gap-gate record through normalize. The renderer ignores it.
    if isinstance(raw.get("citations"), dict):
        site["citations"] = raw["citations"]
    if isinstance(raw.get("presentation"), dict):
        site["presentation"] = raw["presentation"]
    return site


# ---------------------------------------------------------------- LLM prompts
# Kept deliberately small: the whole system prompt is a few hundred tokens, so
# a full build fits comfortably inside free-tier quotas.

SCHEMA_PROMPT = """You are the planner for SpiderCaster, a static website engine. Reply with ONLY one minified JSON object. No markdown fences, no commentary.
HARD RULE: use ONLY facts, names, numbers, prices, claims and wording present in the SOURCE COPY given by the user. You may reorganize, trim, tighten and write connective phrasing, but never invent facts, statistics, prices, dates, names, quotes or offers.
Shape: {"meta":{"title","description"},"theme":{"template":"modern|editorial|bold","dark":bool,"accent":"#rrggbb","accent2":"#rrggbb"},"nav":[{"label","href"}],"pages":[{"slug","title","sections":[{"id","type","data"}]}],"footer":{"text","links":[{"label","href"}]}}
Section types and their data:
hero: {"eyebrow","headline","subhead","primary":{"label","href"},"secondary":{"label","href"},"bullets":[str]}
features: {"title","items":[{"icon","title","body"}]} icon one of: zap shield heart star check code cloud lock pulse globe sparkles layers cpu camera mail map users clock trending phone pin
stats: {"items":[{"value","label"}]}
steps: {"title","items":[{"title","body"}]}
gallery: {"title","items":[{"label","caption","src","alt"}]} src only for image paths listed in SOURCE COPY assets
pricing: {"title","items":[{"name","price","period","blurb","features":[str],"featured":bool,"cta":{"label","href"}}]}
testimonials: {"items":[{"quote","name","role"}]}
faq: {"title","items":[{"q","a"}]}
cta: {"title","body","primary":{"label","href"}}
contact: {"title","body","email","phone","address","hours"}
about: {"title","body":[str],"points":[{"title","body"}]}
team: {"title","items":[{"name","role","bio"}]}
menu: {"title","groups":[{"name","items":[{"name","desc","price"}]}]}
logocloud: {"title","items":[str]}
Rules: first page slug must be "index" with 4-8 sections; extra pages 3-6 sections. Omit a section type entirely when the SOURCE COPY has nothing real for it. hrefs: "#sectionId" for same-page anchors, "slug.html" for other pages, or absolute URLs. Pick accent colors that suit the brand. meta.title <= 60 chars; meta.description <= 155 chars."""

REFINE_PROMPT = """You patch ONE section of an existing SpiderCaster site. Reply with ONLY the replacement section as minified JSON: {"id","type","data"} keeping the same id and type. HARD RULE: use only facts present in the current section data and the user instruction; never invent facts, prices, names or claims. Keep unchanged fields unless the instruction requires changing them. Match the site's voice."""


SECTION_DOCS = {
    "hero": "eyebrow, headline, subhead, primary{label,href}, secondary{label,href}, bullets[str]",
    "features": "title, items[{icon,title,body}] (max 8)",
    "stats": "items[{value,label}] (max 6)",
    "steps": "title, items[{title,body}] (max 6)",
    "gallery": "title, items[{label,caption,src,alt}] (max 12; src only for real local assets)",
    "pricing": "title, items[{name,price,period,blurb,features[str],featured,badge,cta}] (max 4)",
    "testimonials": "items[{quote,name,role}] (max 6)",
    "faq": "title, items[{q,a}] (max 8)",
    "cta": "title, body, primary{label,href}",
    "contact": "title, body, email, phone, address, hours",
    "about": "title, body[str], points[{title,body}]",
    "team": "title, items[{name,role,bio}] (max 8)",
    "menu": "title, groups[{name,items[{name,desc,price}]}]",
    "logocloud": "title, items[str] (max 8)",
}
