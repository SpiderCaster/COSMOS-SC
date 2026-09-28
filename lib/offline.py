"""Zero-token planner: real copy blocks -> site IR with NO invented content.

Every headline, paragraph, bullet, price and contact detail comes verbatim from
the ingested copy. Section types are chosen by what the copy actually contains:
bullets become features, Q&A becomes faq, price rows become pricing/menu, and a
Contact heading becomes contact. Nothing in, nothing rendered.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from . import ir

FEATURE_ICON_HINTS = [
    ("fast|speed|quick|instant", "zap"),
    ("secur|privac|encrypt|safe", "lock"),
    ("cloud|sync|online|remote", "cloud"),
    ("code|api|developer|sdk", "code"),
    ("search|find|discover", "pin"),
    ("team|people|crew|staff", "users"),
    ("time|schedule|hour|deadline", "clock"),
    ("report|metric|analytic|track", "trending"),
    ("photo|image|picture|gallery", "camera"),
    ("support|help|contact", "mail"),
    ("price|cost|afford|free", "star"),
    ("grow|scale|increase", "trending"),
    ("shield|protect|backup", "shield"),
    ("globe|world|region|local", "globe"),
    ("layer|module|component", "layers"),
    ("cpu|engine|model|compute", "cpu"),
]

CONTACT_TITLE_RE = re.compile(r"\bcontact\b|\bget in touch\b|\breach us\b", re.I)
FAQ_TITLE_RE = re.compile(r"\bfaq\b|frequently asked", re.I)
PRICING_TITLE_RE = re.compile(r"\bpric(e|ing|es|plans)\b", re.I)
MENU_TITLE_RE = re.compile(r"\bmenu\b", re.I)
TEAM_TITLE_RE = re.compile(r"\bteam\b|\bstaff\b|\babout us\b|\bour story\b", re.I)
GALLERY_TITLE_RE = re.compile(r"\bgallery\b|\bphotos\b|\bwork\b|\bportfolio\b", re.I)


def guess_icon(text: str) -> str:
    low = text.lower()
    for pattern, icon in FEATURE_ICON_HINTS:
        if re.search(pattern, low):
            return icon
    return "sparkles"


def _first_paragraph(block) -> str:
    for p in block.paragraphs:
        if len(p) >= 40:
            return p
    return block.paragraphs[0] if block.paragraphs else ""


HERO_FILE_HINTS = ("overview", "index", "home", "main", "intro", "about")


def _pick_hero(blocks):
    """Hero block: first content-bearing block of an overview-style file,
    else the first content-bearing block anywhere. Deterministic."""
    for hint in HERO_FILE_HINTS:
        for b in blocks:
            if Path(b.file).stem.lower().startswith(hint) and (b.paragraphs or b.bullets):
                return b
    for b in blocks:
        if b.paragraphs or b.bullets:
            return b
    return blocks[0]


def _nav_label(text: str, limit: int = 28) -> str:
    t = (text or "").strip()
    if len(t) <= limit:
        return t
    cut = t[:limit].rsplit(" ", 1)[0]
    return (cut or t[:limit]).strip()


def plan_offline(copy, opts: dict) -> dict:
    """Build the raw IR dict from ingested copy only. Zero tokens."""
    blocks = [b for b in copy.blocks if b.title or b.paragraphs or b.bullets]
    if not blocks:
        raise SystemExit("offline planner: no copy blocks found; add files under copy/")

    # hero first, so the brand derives from the same block the hero uses
    hero_block = _pick_hero(blocks)
    if opts.get("brand"):
        brand = opts["brand"]
    elif hero_block.title:
        brand = hero_block.title[:60]
    else:
        first_line = copy.brief.splitlines()[0].strip() if copy.brief else ""
        brand = first_line[:60] or "Local Build"

    sections: list[dict] = []
    sections.append({
        "id": "hero", "type": "hero",
        "data": {
            "eyebrow": "",
            "headline": hero_block.title or brand,
            "subhead": _first_paragraph(hero_block),
            "primary": {"label": "Read on", "href": "#learn-more"},
            "secondary": None,
            "bullets": hero_block.bullets[:4],
        },
    })

    # 2) map remaining blocks by what they contain
    for b in blocks:
        if b is hero_block:
            continue
        title = b.title or ""
        has_prices = bool(b.prices)
        has_qa = len(b.qa) >= 2
        has_bullets = len(b.bullets) >= 3
        is_contact = bool(CONTACT_TITLE_RE.search(title)) or (not title and (b.emails or b.phones))
        has_images = bool(b.images) or bool(copy.assets)

        if is_contact:
            sections.append({
                "id": "contact", "type": "contact",
                "data": {
                    "title": title or "Contact",
                    "body": " ".join(b.paragraphs[:2]),
                    "email": (b.emails or copy.emails or [""])[0],
                    "phone": (b.phones or copy.phones or [""])[0],
                    "address": "",
                    "hours": "",
                },
            })
            continue
        if has_qa or FAQ_TITLE_RE.search(title):
            sections.append({
                "id": "faq", "type": "faq",
                "data": {"title": title or "Questions", "subhead": "",
                         "items": b.qa[:8] or [{"q": q, "a": a} for q, a in []]},
            })
            continue
        if has_prices and (PRICING_TITLE_RE.search(title) or MENU_TITLE_RE.search(title)):
            kind = "menu" if MENU_TITLE_RE.search(title) else "pricing"
            if kind == "menu":
                sections.append({
                    "id": "menu", "type": "menu",
                    "data": {"title": title, "subhead": " ".join(b.paragraphs[:1]),
                             "groups": [{"name": title or "Menu",
                                         "items": [{"name": p["name"], "desc": p["desc"], "price": p["price"]}
                                                   for p in b.prices[:8]]}]},
                })
            else:
                items = []
                for p in b.prices[:4]:
                    items.append({"name": p["name"], "price": p["price"], "period": "",
                                  "blurb": p["desc"], "features": [], "featured": False, "badge": "", "cta": None})
                sections.append({
                    "id": "pricing", "type": "pricing",
                    "data": {"title": title, "subhead": " ".join(b.paragraphs[:1]), "items": items},
                })
            continue
        if has_bullets and not GALLERY_TITLE_RE.search(title):
            sections.append({
                "id": "features", "type": "features",
                "data": {"title": title, "subhead": " ".join(b.paragraphs[:1]),
                         "items": [{"icon": guess_icon(f"{x} {title}"), "title": x.split(":")[0][:60],
                                    "body": x.split(":", 1)[1].strip() if ":" in x else ""}
                                   for x in b.bullets[:8]]},
            })
            continue
        if has_images and (GALLERY_TITLE_RE.search(title) or copy.assets):
            imgs = b.images or [{"src": rel, "alt": name} for name, rel in list(copy.assets.items())[:12]]
            sections.append({
                "id": "gallery", "type": "gallery",
                "data": {"title": title or "Gallery", "subhead": "",
                         "items": [{"label": im.get("alt") or "", "caption": "", "src": im.get("src", ""),
                                    "alt": im.get("alt") or "", "hue": None} for im in imgs[:12]]},
            })
            continue
        if TEAM_TITLE_RE.search(title):
            sections.append({
                "id": "about", "type": "about",
                "data": {"title": title or "About", "body": b.paragraphs[:3],
                         "points": [{"title": x.split(":")[0][:60],
                                     "body": x.split(":", 1)[1].strip() if ":" in x else ""}
                                    for x in b.bullets[:4]]},
            })
            continue
        # default: about-style text section
        if b.paragraphs or b.bullets or b.numbered:
            sections.append({
                "id": ir.slugify(title) or "section", "type": "about",
                "data": {"title": title or "More", "body": b.paragraphs[:3],
                         "points": [{"title": x.split(":")[0][:60],
                                     "body": x.split(":", 1)[1].strip() if ":" in x else ""}
                                    for x in (b.bullets + b.numbered)[:4]]},
            })

    # hero CTA: point at the first real anchor target
    targets = [sec["id"] for sec in sections if sec["id"] not in ("hero",)]
    if targets:
        sections[0]["data"]["primary"] = {"label": "Read on", "href": f"#{targets[0]}"}
        contact = next((sec for sec in sections if sec["type"] == "contact"), None)
        if contact:
            sections[0]["data"]["secondary"] = {"label": "Contact", "href": f"#{contact['id']}"}

    # de-dup ids like faq/faq
    seen: set = set()
    for sec in sections:
        base = sec["id"]
        n = 2
        while sec["id"] in seen:
            sec["id"] = f"{base}-{n}"
            n += 1
        seen.add(sec["id"])

    theme = {
        "template": opts.get("template") or "modern",
        "dark": opts.get("dark") if isinstance(opts.get("dark"), bool) else True,
        "accent": None,
        "accent2": None,
    }
    return {
        "meta": {"title": brand, "description": _first_paragraph(hero_block)[:155] or f"{brand} - local build"},
        "theme": theme,
        "nav": [{"label": _nav_label(s["data"].get("title") or ir.title_case(s["id"])),
                 "href": f"#{s['id']}"}
                for s in sections if s["type"] not in ("hero",)][:6],
        "pages": [{"slug": "index", "title": brand, "sections": sections}],
        "footer": {"text": f"(c) {date.today().year} {brand}", "links": [], "credit": True},
    }
