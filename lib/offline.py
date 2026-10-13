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
    ("build|install|setup|deploy|launch", "rocket"),
    ("terminal|command|cli|bash|shell", "terminal"),
    ("browser|preview|view|web", "browser"),
    ("database|storage|persist|sql", "database"),
    ("server|host|network", "server"),
    ("design|art|creative|style|color|theme", "palette"),
    ("layout|wireframe|frame|structure", "layout"),
    ("module|package|tool|part|box", "box"),
    ("fast|speed|quick|instant", "zap"),
    ("secur|privac|encrypt|safe", "lock"),
    ("cloud|sync|online|remote", "cloud"),
    ("code|api|developer|sdk", "code"),
    ("search|find|discover|inspect|probe", "search"),
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
    ("setting|config|knob|tune", "sliders"),
    ("refresh|sync|reload|rebuild|again", "refresh"),
]

CONTACT_TITLE_RE = re.compile(r"\bcontact\b|\bget in touch\b|\breach us\b", re.IGNORECASE)
FAQ_TITLE_RE = re.compile(r"\bfaq\b|frequently asked", re.IGNORECASE)
PRICING_TITLE_RE = re.compile(r"\bpric(e|ing|es|plans)\b", re.IGNORECASE)
MENU_TITLE_RE = re.compile(r"\bmenu\b", re.IGNORECASE)
TEAM_TITLE_RE = re.compile(r"\bteam\b|\bstaff\b|\babout us\b|\bour story\b", re.IGNORECASE)
GALLERY_TITLE_RE = re.compile(r"\bgallery\b|\bphotos\b|\bwork\b|\bportfolio\b|\bmachines?\b", re.IGNORECASE)
STATS_TITLE_RE = re.compile(r"\bnumbers?\b|\bstats?\b|\bmetrics?\b|\bby the numbers\b|\bthe cost\b", re.IGNORECASE)
CTA_TITLE_RE = re.compile(r"\bstart\b|\bget started\b|\bready to\b|\bclosing\b", re.IGNORECASE)


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


def _nav_label(text: str) -> str:
    return (text or "").strip()


def _titled_follow(sections: list) -> dict | None:
    """First section after the hero whose title is non-empty."""
    for sec in sections:
        if sec.get("type") == "hero" or sec.get("id") == "hero":
            continue
        data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
        if str(data.get("title") or "").strip():
            return sec
    return None


def _cut_description(text: str, limit: int = 160) -> str:
    """Cut on the last sentence end inside limit, else the last space.

    Does not add punctuation. Text that already fits is returned unchanged.
    """
    if len(text) <= limit:
        return text
    window = text[:limit]
    last = max(window.rfind("."), window.rfind("!"), window.rfind("?"))
    if last >= 0:
        return window[: last + 1].rstrip()
    space = window.rfind(" ")
    if space >= 0:
        return window[:space].rstrip()
    return window


def _span_file(text: str, blocks) -> str | None:
    """File holding text as an exact span, else None.

    --brand (and any future override) is honored only when it equals a
    cited span: a block title, or a verbatim substring of a paragraph,
    bullet, numbered item, question, answer, or price name.
    """
    want = str(text or "").strip()
    if not want:
        return None
    for b in blocks:
        if want == str(b.title or "").strip():
            return b.file
        hay = list(b.paragraphs) + list(b.bullets) + list(b.numbered)
        hay += [qa.get("q", "") for qa in b.qa] + [qa.get("a", "") for qa in b.qa]
        hay += [p.get("name", "") for p in b.prices]
        if any(want == h.strip() or want in h for h in hay if isinstance(h, str)):
            return b.file
    return None


def plan_offline(copy, opts: dict) -> dict:
    """Build the raw IR dict from ingested copy only. Zero tokens."""
    from .copy_schema import GapError, load_frame_slots

    blocks = [b for b in copy.blocks if b.title or b.paragraphs or b.bullets]
    if not blocks:
        raise SystemExit("FAIL gap hero.headline (no copy blocks found; add files under copy/)")

    # hero first, so the brand derives from the same block the hero uses.
    # Strict: the headline must be a cited span. An uncited --brand is
    # ignored; brief/Local Build never supply visible words.
    hero_block = _pick_hero(blocks)
    brand_opt = str((opts or {}).get("brand") or "").strip()
    if brand_opt and _span_file(brand_opt, blocks):
        brand = brand_opt[:60]
    elif hero_block.title and hero_block.title.strip():
        brand = hero_block.title.strip()[:60]
    else:
        raise GapError("hero", "headline", "no cited headline in copy")

    sections: list[dict] = []
    hero_sub = _first_paragraph(hero_block)
    hero_img = ""
    if getattr(copy, "assets", None):
        hero_img = copy.assets.get("hero") or copy.assets.get("reading-room") or ""
        if not hero_img:
            for k, v in copy.assets.items():
                if "hero" in k.lower():
                    hero_img = v
                    break
    sections.append({
        "id": "hero", "type": "hero",
        "data": {
            "eyebrow": "",
            "headline": hero_block.title or brand,
            "subhead": hero_sub,
            "primary": None,
            "secondary": None,
            "bullets": hero_block.bullets[:4],
            "image": hero_img,
            "image_alt": f"{brand} hero" if hero_img else "",
        },
        "_source": hero_block.file,
    })
    # remaining real paragraphs from the hero block keep their place on the page
    extra_paras = [p for p in hero_block.paragraphs if p != hero_sub]
    if extra_paras:
        sections.append({
            "id": "about", "type": "about",
            "data": {"title": "", "body": extra_paras[:3], "points": []},
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
            paras = b.paragraphs[:]
            addr = next((p for p in paras if re.match(r"^\d{1,4}\s+\w", p)), "")
            hours = next((p for p in paras
                          if re.search(r"\bam\b|\bpm\b|closed|\b(?:mon|tue|wed|thu|fri|sat|sun)", p, re.IGNORECASE)
                          and p != addr), "")
            phone = (b.phones or copy.phones or [""])[0]
            email = (b.emails or copy.emails or [""])[0]
            exact = {x.strip() for x in (phone, email, addr) if str(x).strip()}
            body = [p for p in paras if p != hours and p.strip() not in exact]
            data = {
                "title": title or "Contact",
                "body": " ".join(body[:2]),
                "email": email,
                "phone": phone,
                "address": addr,
                "hours": hours,
            }
            if not any(str(data[k] or "").strip() for k in ("body", "email", "phone", "address", "hours")):
                raise GapError("contact", "body", f"block '{b.file}' asks for contact with no cited facts")
            sections.append({
                "id": "contact", "type": "contact", "data": data, "_source": b.file,
            })
            continue
        if FAQ_TITLE_RE.search(title) and not b.qa:
            # A FAQ heading with no Q&A pairs is a gap, not generic prose.
            raise GapError("faq", "items", f"block '{b.file}' has a faq heading with no cited Q&A")
        if has_qa or FAQ_TITLE_RE.search(title):
            sections.append({
                "id": "faq", "type": "faq",
                "data": {"title": title or "Questions", "subhead": "",
                         "items": b.qa[:8] or [{"q": q, "a": a} for q, a in []]},
                "_source": b.file,
            })
            continue
        if (PRICING_TITLE_RE.search(title) or MENU_TITLE_RE.search(title)) and not has_prices:
            # A Pricing/Menu heading with zero price rows is a gap, not about text.
            kind = "menu" if MENU_TITLE_RE.search(title) else "pricing"
            raise GapError(kind, "items", f"block '{b.file}' has a {kind} heading with no cited prices")
        if has_prices and (PRICING_TITLE_RE.search(title) or MENU_TITLE_RE.search(title)):
            kind = "menu" if MENU_TITLE_RE.search(title) else "pricing"
            if kind == "menu":
                group_name = title or "Menu"
                if group_name.strip() == title.strip():
                    group_name = ""
                sections.append({
                    "id": "menu", "type": "menu",
                    "data": {"title": title, "subhead": " ".join(b.paragraphs[:1]),
                             "groups": [{"name": group_name,
                                         "items": [{"name": p["name"], "desc": p["desc"], "price": p["price"]}
                                                   for p in b.prices[:8]]}]},
                    "_source": b.file,
                })
            else:
                items = []
                for p in b.prices[:4]:
                    items.append({"name": p["name"], "price": p["price"], "period": "",
                                  "blurb": p["desc"], "features": [], "featured": False, "badge": "", "cta": None})
                sections.append({
                    "id": "pricing", "type": "pricing",
                    "data": {"title": title, "subhead": " ".join(b.paragraphs[:1]), "items": items},
                    "_source": b.file,
                })
            continue
        if STATS_TITLE_RE.search(title):
            stat_items = []
            full_text = " ".join(b.paragraphs + b.bullets)
            for m in re.finditer(r"(\d+[\w%+-]*)\s+([a-zA-Z][^,.;\n]+(?=[.,;]|\s+\d|$))", full_text):
                val, lab = m.group(1).strip(), m.group(2).strip()
                if lab and len(lab) < 70:
                    stat_items.append({"value": val, "label": lab})
            if len(stat_items) >= 2:
                sections.append({
                    "id": ir.slugify(title) or "stats", "type": "stats",
                    "data": {"title": title, "items": stat_items[:6]},
                    "_source": b.file,
                })
                continue
        if len(b.numbered) >= 2:
            step_items = []
            for num_text in b.numbered[:6]:
                parts = num_text.split(":", 1) if ":" in num_text else (num_text.split(". ", 1) if ". " in num_text else [num_text, ""])
                item_title = parts[0].strip()[:60]
                item_body = parts[1].strip() if len(parts) > 1 else ""
                step_items.append({"title": item_title, "body": item_body})
            sections.append({
                "id": ir.slugify(title) or "steps", "type": "steps",
                "data": {"title": title, "subhead": " ".join(b.paragraphs[:1]), "items": step_items},
                "_source": b.file,
            })
            continue
        if has_bullets and not GALLERY_TITLE_RE.search(title):
            sections.append({
                "id": "features", "type": "features",
                "data": {"title": title, "subhead": " ".join(b.paragraphs[:1]),
                         "items": [{"icon": guess_icon(f"{x} {title}"), "title": x.split(":")[0][:60],
                                    "body": x.split(":", 1)[1].strip() if ":" in x else ""}
                                   for x in b.bullets[:8]]},
                "_source": b.file,
            })
            continue
        if GALLERY_TITLE_RE.search(title) or (bool(b.images) and not has_bullets):
            gallery_assets = [
                {"src": rel, "alt": name, "label": name.replace("-", " ").capitalize(), "caption": name.replace("-", " ").capitalize()}
                for name, rel in copy.assets.items()
                if "hero" not in name.lower()
            ]
            imgs = b.images or gallery_assets or [{"src": rel, "alt": name} for name, rel in list(copy.assets.items())[:12]]
            if imgs:
                sections.append({
                    "id": ir.slugify(title) or "gallery", "type": "gallery",
                    "data": {"title": title or "Gallery", "subhead": " ".join(b.paragraphs[:1]) if b.paragraphs else "",
                             "items": [{"label": im.get("label") or im.get("alt") or "", "caption": im.get("caption") or im.get("label") or "", "src": im.get("src", ""),
                                        "alt": im.get("alt") or im.get("label") or "", "hue": None} for im in imgs[:12]]},
                    "_source": b.file,
                })
                continue
        if CTA_TITLE_RE.search(title) and not b.bullets and not b.numbered:
            sections.append({
                "id": ir.slugify(title) or "cta", "type": "cta",
                "data": {"title": title, "body": " ".join(b.paragraphs[:2]), "primary": None},
                "_source": b.file,
            })
            continue
        if TEAM_TITLE_RE.search(title):
            sections.append({
                "id": "about", "type": "about",
                "data": {"title": title or "About", "body": b.paragraphs[:3],
                         "points": [{"title": x.split(":")[0][:60],
                                     "body": x.split(":", 1)[1].strip() if ":" in x else ""}
                                    for x in b.bullets[:4]]},
                "_source": b.file,
            })
            continue
        # default: about-style text section for cited leftover prose only.
        # Blocks that asked for a required slot above already raised GapError;
        # reaching here means plain prose with no special contract.
        if b.paragraphs or b.bullets or b.numbered:
            sections.append({
                "id": ir.slugify(title) or "section", "type": "about",
                "data": {"title": title or "More", "body": b.paragraphs[:3],
                         "points": [{"title": x.split(":")[0][:60],
                                     "body": x.split(":", 1)[1].strip() if ":" in x else ""}
                                    for x in (b.bullets + b.numbered)[:4]]},
                "_source": b.file,
            })

    # de-dup ids like faq/faq
    seen: set = set()
    for sec in sections:
        base = sec["id"]
        n = 2
        while sec["id"] in seen:
            sec["id"] = f"{base}-{n}"
            n += 1
        seen.add(sec["id"])

    # Ask sections (cta and contact) close the case and always come last (offer -> proof -> ask).
    sections[:] = (
        [sec for sec in sections if sec["type"] not in ("contact", "cta")]
        + [sec for sec in sections if sec["type"] == "cta"]
        + [sec for sec in sections if sec["type"] == "contact"]
    )

    # Primary names the next titled section. Skip an empty-title about.
    # No titled section: leave primary unset. Do not slice the subhead.
    target = _titled_follow(sections)
    if target:
        title = str(target["data"].get("title") or "").strip()
        sections[0]["data"]["primary"] = {"label": title, "href": f"#{target['id']}"}
    # A secondary that repeats the primary href or label is the same button twice.
    contact = next((sec for sec in sections if sec["type"] == "contact"), None)
    if contact:
        secondary = {"label": "Contact", "href": f"#{contact['id']}"}
        primary = sections[0]["data"].get("primary")
        same = isinstance(primary, dict) and (
            secondary["href"] == primary.get("href")
            or secondary["label"] == primary.get("label")
        )
        if not same:
            sections[0]["data"]["secondary"] = secondary

    theme = {
        "template": (opts or {}).get("template") or "modern",
        "dark": (opts or {}).get("dark") if isinstance((opts or {}).get("dark"), bool) else True,
        "accent": None,
        "accent2": None,
    }
    # Gap-gate record: per-section source files for --from re-read, plus the
    # frame slot contract the planner enforced. normalize_site() preserves
    # both keys; the renderer ignores them.
    citations: dict = {}
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        src = sec.get("_source")
        data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
        texts = [str(v).strip() for v in (
            data.get("headline"), data.get("title"), data.get("subhead"),
        ) if isinstance(v, str) and str(v).strip()]
        if isinstance(src, str) and src:
            citations[str(sec.get("id"))] = {"file": src, "texts": texts[:3]}
    slots = load_frame_slots((opts or {}).get("frame"))
    presentation = {
        "frame_id": str((opts or {}).get("frame") or ""),
        "mold_id": str((opts or {}).get("mold") or ""),
        "slots": [{"section": name, "required": True} for name in slots.get("required", [])]
        + [{"section": name, "required": False} for name in slots.get("optional", [])],
    }
    return {
        "meta": {"title": brand, "description": _cut_description(_first_paragraph(hero_block)) or f"{brand} - local build"},
        "theme": theme,
        "nav": [{"label": label, "href": f"#{s['id']}"}
                for s in sections if s["type"] not in ("hero",)
                for label in [_nav_label(s["data"].get("title") or "")] if label][:6],
        "pages": [{"slug": "index", "title": brand, "sections": sections}],
        "footer": {"text": f"(c) {date.today().year} {brand}", "links": [], "credit": True},
        "citations": citations,
        "presentation": presentation,
    }


def _selftest() -> int:
    from .ingest import Block, Copy

    overview = (
        "SpiderCaster is a copy-driven static website engine. "
        "You give it a brief and real copy files; it returns a self-contained static site. "
        + "The structure stays deterministic. " * 8
    )
    assert len(overview) > 160
    desc = _cut_description(overview)
    assert overview.startswith(desc)
    assert len(desc) <= 160
    assert desc.endswith((".", "!", "?"))
    assert not desc.endswith(" and")
    assert "award" not in desc.lower()
    assert "review" not in desc.lower()
    window = overview[:160]
    last = max(window.rfind("."), window.rfind("!"), window.rfind("?"))
    assert desc == window[: last + 1].rstrip()

    words = " ".join(["river"] * 40)
    assert "." not in words and "!" not in words and "?" not in words
    cut = _cut_description(words)
    assert words.startswith(cut)
    assert len(cut) <= 160
    assert words[len(cut)] == " "
    assert not cut.endswith((".", "!", "?"))
    assert "award" not in cut.lower()
    assert "review" not in cut.lower()

    short = "A quiet tea room that seats walk-ins by the water."
    assert _cut_description(short) == short

    copy = Copy()
    block = Block("overview.md", 1, "SpiderCaster")
    block.paragraphs = [overview, "Second paragraph stays whole."]
    copy.blocks = [block]
    site = plan_offline(copy, {})
    meta = site["meta"]["description"]
    assert meta == desc
    hero = site["pages"][0]["sections"][0]["data"]["subhead"]
    assert hero == overview
    assert "award" not in meta.lower()
    assert "review" not in meta.lower()
    assert site["pages"][0]["sections"][0]["data"]["primary"] is None

    contact_only = Copy()
    contact_hero = Block("overview.md", 1, "Harbor Tea Room")
    contact_hero.paragraphs = ["A quiet tea room that seats walk-ins by the water."]
    contact_block = Block("contact.md", 1, "Contact")
    contact_block.paragraphs = ["Walk-ins only."]
    contact_only.blocks = [contact_hero, contact_block]
    contact_hero_data = plan_offline(contact_only, {})["pages"][0]["sections"][0]["data"]
    assert contact_hero_data["primary"]["label"] == "Contact"
    assert contact_hero_data["primary"]["href"] == "#contact"
    contact_secondary = contact_hero_data["secondary"]
    assert contact_secondary is None or contact_secondary.get("href") != contact_hero_data["primary"]["href"]

    kept = Copy()
    kept_hero = Block("overview.md", 1, "Harbor Tea Room")
    kept_hero.paragraphs = ["A quiet tea room that seats walk-ins by the water."]
    kept_hours = Block("hours.md", 1, "Hours")
    kept_hours.paragraphs = ["Open Tuesday to Sunday."]
    kept_contact = Block("contact.md", 1, "Contact")
    kept_contact.paragraphs = ["Walk-ins only."]
    kept.blocks = [kept_hero, kept_hours, kept_contact]
    kept_data = plan_offline(kept, {})["pages"][0]["sections"][0]["data"]
    assert kept_data["primary"] == {"label": "Hours", "href": "#hours"}
    assert kept_data["secondary"] == {"label": "Contact", "href": "#contact"}

    hours = Block("hours.md", 1, "Hours")
    hours.paragraphs = ["Open Tuesday to Sunday."]
    copy.blocks.append(hours)
    linked = plan_offline(copy, {})["pages"][0]["sections"]
    button = linked[0]["data"]["primary"]
    assert button == {"label": "Hours", "href": "#hours"}
    assert any(sec["id"] == "hours" for sec in linked)
    about = next(sec for sec in linked if sec["id"] == "about")
    assert not str(about["data"].get("title") or "").strip()

    bare = Copy()
    titled = Block("overview.md", 1, "Harbor Tea")
    titled.bullets = ["Loose leaf", "Walk ins", "Quiet room"]
    bare.blocks = [titled]
    fallback = plan_offline(bare, {})["meta"]["description"]
    assert fallback == "Harbor Tea - local build"
    assert "award" not in fallback.lower()
    assert "review" not in fallback.lower()

    menu_copy = Copy()
    menu_hero = Block("overview.md", 1, "Harbor Tea Room")
    menu_hero.paragraphs = ["A quiet tea room that seats walk-ins by the water."]
    menu_block = Block("menu.md", 1, "Menu")
    menu_block.paragraphs = ["12oz cups, brewed to order."]
    menu_block.prices = [
        {"name": "Jasmine Pearl", "desc": "", "price": "$4.50"},
        {"name": "Assam Malt", "desc": "", "price": "$3.75"},
    ]
    menu_copy.blocks = [menu_hero, menu_block]
    menu_sec = next(sec for sec in plan_offline(menu_copy, {})["pages"][0]["sections"] if sec["type"] == "menu")
    assert menu_sec["data"]["title"] == "Menu"
    menu_group = menu_sec["data"]["groups"][0]
    assert menu_group["name"] != menu_sec["data"]["title"]
    assert menu_group["name"] == ""
    assert [it["name"] for it in menu_group["items"]] == ["Jasmine Pearl", "Assam Malt"]
    assert [it["price"] for it in menu_group["items"]] == ["$4.50", "$3.75"]
    print("offline selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
