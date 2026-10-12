"""Prove slot fill and grounded copy blocks.

Run from the engine root: python lib/part_fill_selftest.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.part_fill import (
    bind_fragment,
    copy_block,
    field_strings,
    fill_fragment,
    ground_fragment,
    has_grounded_markup,
    section_fields,
)

COPY = "Tea is served at dawn. Tom & <Jerry> likes the harbor."
SENTENCE = "Tea is served at dawn."
HTML_SENTENCE = "Tom & <Jerry> likes the harbor."
ESCAPED = "Tom &amp; &lt;Jerry&gt; likes the harbor."


def _fail(msg: str) -> int:
    print("part_fill selftest FAIL: " + msg)
    return 1


def main() -> int:
    fragment = (
        '<article class="sc-x" data-sc-slot="title" id="intro">About</article>'
        '<p title="a>b" data-sc-slot="body">Placeholder</p>'
    )
    filled = fill_fragment(
        fragment,
        {"title": "Not in the source", "body": SENTENCE},
        COPY,
    )
    if SENTENCE not in filled or "Placeholder" in filled:
        return _fail("grounded slot was not replaced")
    if 'data-sc-slot="title"' not in filled or ">About</article>" not in filled:
        return _fail("ungrounded slot was not left")
    if "Not in the source" in filled:
        return _fail("ungrounded slot text was inserted")
    if filled != (
        '<article class="sc-x" data-sc-slot="title" id="intro">About</article>'
        '<p title="a>b" data-sc-slot="body">' + SENTENCE + "</p>"
    ):
        return _fail("grounded replacement did not keep the surrounding tags")

    plain = "<p>Keep this paragraph.</p>"
    if fill_fragment(plain, {"body": SENTENCE}, COPY) != plain:
        return _fail("fragment with no slot changed")
    commented = '<!-- <b data-sc-slot="body">Placeholder</b> --><i>Stay</i>'
    if fill_fragment(commented, {"body": SENTENCE}, COPY) != commented:
        return _fail("a slot inside a comment was changed")

    quoted = "<p data-sc-slot='body'>Placeholder</p>"
    if fill_fragment(quoted, {"body": SENTENCE}, COPY) != "<p data-sc-slot='body'>" + SENTENCE + "</p>":
        return _fail("single-quoted slot was not replaced")

    nested = '<div data-sc-slot="outer">Head <span data-sc-slot="inner">In</span></div>'
    inner_only = fill_fragment(
        nested,
        {"outer": "Nope", "inner": SENTENCE},
        COPY,
    )
    if inner_only != '<div data-sc-slot="outer">Head <span data-sc-slot="inner">' + SENTENCE + "</span></div>":
        return _fail("nested grounded slot was not replaced in place")
    outer = fill_fragment(
        nested,
        {"outer": SENTENCE, "inner": SENTENCE},
        COPY,
    )
    if outer != '<div data-sc-slot="outer">' + SENTENCE + "</div>":
        return _fail("grounded parent slot did not replace its text")

    slot_html = fill_fragment(
        '<p data-sc-slot="html">old</p>',
        {"html": HTML_SENTENCE},
        COPY,
    )
    if ESCAPED not in slot_html or "<Jerry>" in slot_html:
        return _fail("HTML in a slot copy string was not escaped")

    block = copy_block(
        {
            "id": "about",
            "type": "about",
            "data": {
                "Read on": SENTENCE,
                "title": "About",
                "lead": "Read on",
                "credit": "Built with SpiderCaster",
                "body": [SENTENCE, "Invented slogan for the shop"],
                "html": HTML_SENTENCE,
                "empty": "",
                "blank": "   ",
                "n": 4,
                "points": [{"title": "Also invented", "body": ""}],
            },
        },
        COPY + "\nRead on\nBuilt with SpiderCaster\nAbout\n",
    )
    if not block.startswith('<div class="sc-fill">') or not block.endswith("</div>"):
        return _fail("copy_block did not wrap grounded strings")
    if SENTENCE not in block:
        return _fail("copy_block dropped a real sentence")
    if "Invented slogan" in block or "Also invented" in block:
        return _fail("copy_block kept an invented string")
    if ESCAPED not in block or "<Jerry>" in block:
        return _fail("HTML in a copy string was not escaped")
    for phrase in ("Read on", "Built with SpiderCaster", "About"):
        if phrase in block:
            return _fail("forbidden phrase was emitted: " + phrase)

    longer = copy_block(
        {"data": {"title": "About", "body": "About the harbor tea."}},
        "About the harbor tea.",
    )
    if longer != '<div class="sc-fill">About the harbor tea.</div>':
        return _fail("a real sentence containing About was dropped or doubled")

    if copy_block({"data": {"title": "About", "lead": "Read on"}}, COPY + "\nAbout\nRead on") != "":
        return _fail("only forbidden strings should return empty")
    if copy_block({"data": {"body": "Invented slogan for the shop"}}, COPY) != "":
        return _fail("nothing grounded should return empty")
    if copy_block({"id": "about"}, COPY) != "":
        return _fail("a section with no data dict should return empty")

    demo = (
        "<h2>Hero: full-bleed dark band</h2>"
        "<p>High-contrast dark band with light text.</p>"
        "<p>Tea is served at dawn.</p>"
        "<p>Hours</p>"
    )
    grounded = ground_fragment(demo, {}, COPY + "\n# Hours\n")
    if "full-bleed" in grounded or "High-contrast" in grounded or ">Hours<" in grounded:
        return _fail("catalog demo text was kept: " + grounded)
    if "Tea is served at dawn." not in grounded:
        return _fail("a real copy sentence was dropped")
    slotted = ground_fragment(
        '<p data-sc-slot="body">Placeholder</p><a href="#main">Phone</a>',
        {"body": SENTENCE},
        COPY,
    )
    if SENTENCE not in slotted or "Placeholder" in slotted or "Phone" in slotted:
        return _fail("slot fill did not replace demo text: " + slotted)
    only_demo = ground_fragment(
        "<h2>Hero: full-bleed dark band</h2><p>High-contrast dark band with light text.</p>",
        {},
        COPY,
    )
    if has_grounded_markup(only_demo):
        return _fail("a stripped catalog shell still counts as grounded markup: " + only_demo)
    if not has_grounded_markup(grounded):
        return _fail("a real copy sentence inside a part was treated as empty")
    if not has_grounded_markup(slotted):
        return _fail("a grounded slot sentence was treated as empty")
    if has_grounded_markup("<div><p> </p></div>"):
        return _fail("whitespace inside an empty shell counts as grounded markup")

    joined = "Open Tuesday to Sunday, 8am to 6pm. Closed Mondays."
    hours_copy = "Open Tuesday to Sunday, 8am to 6pm.\n\nClosed Mondays.\n"
    collapsed = ground_fragment(f"<p>{joined}</p>", {}, hours_copy)
    if joined not in collapsed:
        return _fail("a joined copy sentence was dropped: " + collapsed)
    labeled = ground_fragment(
        '<td data-label="Hours">Jasmine Pearl</td>',
        {"name": "Jasmine Pearl"},
        "Jasmine Pearl\n# Hours\n",
    )
    if "Jasmine Pearl" not in labeled or "data-label" in labeled:
        return _fail("an ungrounded data-label was kept: " + labeled)

    def paint(fragment: str, section: dict, copy: str) -> str:
        fields = section_fields(section, copy)
        bound = bind_fragment(fragment, section, copy)
        slots = {f"sc-bound-{index}": value for index, value in enumerate(field_strings(fields))}
        return ground_fragment(bound, slots, copy)

    hero_copy = (
        "# Harbor Tea Room\n\n"
        "A quiet tea room that seats walk-ins by the water.\n\n"
        "# Menu\n\n# Contact\n"
    )
    hero_html = (
        '<section class="sc-darkband">'
        '<h2 id="sc-darkband-title" class="sc-darkband__title">Hero: full-bleed dark band</h2>'
        '<p class="sc-darkband__lead">High-contrast dark band with light text.</p>'
        '<a class="sc-darkband__action" href="#sc-darkband-title">Full-bleed dark band</a>'
        "</section>"
    )
    hero = paint(
        hero_html,
        {
            "id": "hero",
            "type": "hero",
            "data": {
                "headline": "Harbor Tea Room",
                "subhead": "A quiet tea room that seats walk-ins by the water.",
                "primary": {"label": "Menu", "href": "#menu"},
                "secondary": {"label": "Contact", "href": "#contact"},
            },
        },
        hero_copy,
    )
    for phrase in ("Harbor Tea Room", "A quiet tea room that seats walk-ins by the water.", ">Menu<", ">Contact<"):
        if phrase not in hero:
            return _fail("hero bind missed " + phrase + ": " + hero)
    if "full-bleed" in hero.lower() or "Read more" in hero or "<h2" in hero:
        return _fail("hero bind kept demo text or the h2: " + hero)
    if 'href="#menu"' not in hero or 'href="#contact"' not in hero:
        return _fail("hero actions lost their targets: " + hero)

    menu_copy = "# Menu\n\n12oz cups, brewed to order.\n\n- Jasmine Pearl - $4.50\n- Assam Malt - $3.75\n"
    menu_html = (
        '<div class="sc-tbl-basic"><div role="region" aria-label="Table: basic data table">'
        "<table><caption><span>Table: basic data table</span><span>Plain table with row headers.</span></caption>"
        "<thead><tr><th>Shift</th><th>Hours</th><th>Days</th></tr></thead>"
        '<tbody><tr><th data-label="Shift">Desk</th><td data-label="Hours">8</td><td data-label="Days">5</td></tr>'
        '<tr><th data-label="Shift">Field</th><td data-label="Hours">6</td><td data-label="Days">4</td></tr>'
        "</tbody></table></div></div>"
    )
    menu = paint(
        menu_html,
        {
            "id": "menu",
            "type": "menu",
            "data": {
                "title": "Menu",
                "subhead": "12oz cups, brewed to order.",
                "groups": [{"items": [
                    {"name": "Jasmine Pearl", "desc": "", "price": "$4.50"},
                    {"name": "Assam Malt", "desc": "", "price": "$3.75"},
                ]}],
            },
        },
        menu_copy,
    )
    for phrase in ("Jasmine Pearl", "$4.50", "Assam Malt", "12oz cups, brewed to order."):
        if phrase not in menu:
            return _fail("menu bind missed " + phrase + ": " + menu)
    if "Desk" in menu or "data-label" in menu or ">Shift<" in menu or ">8<" in menu:
        return _fail("menu bind kept a demo cell: " + menu)

    faq_copy = (
        "# Questions about the engine\n\n"
        "Does the offline build really cost zero tokens?\n"
        "Yes. The offline planner maps your copy files into sections with deterministic rules.\n"
    )
    faq_html = (
        '<div class="sc-faqflush"><p class="sc-faqflush__lead">Flush FAQ accordion without outer border.</p>'
        '<div class="sc-faqflush__item"><details><summary><h2>Flush FAQ accordion without outer border</h2></summary>'
        "<p>Only a rule separates each question.</p></details></div>"
        '<div class="sc-faqflush__item"><details><summary><h2>Rules between items</h2></summary>'
        "<p>There is no outer border.</p></details></div></div>"
    )
    question = "Does the offline build really cost zero tokens?"
    answer = "Yes. The offline planner maps your copy files into sections with deterministic rules."
    faq = paint(
        faq_html,
        {
            "id": "faq",
            "type": "faq",
            "data": {
                "title": "Questions about the engine",
                "items": [{"q": question, "a": answer}, {"q": question, "a": answer}],
            },
        },
        faq_copy,
    )
    if question not in faq or answer not in faq or "Flush FAQ" in faq:
        return _fail("faq bind kept demo text or dropped the question: " + faq)

    contact_copy = (
        "# Contact\n\n14 Harbor Lane\n\n(555) 014-2288\n\n"
        "Walk-ins only; no reservations needed.\n\n"
        "Open Tuesday to Sunday, 8am to 6pm.\n\nClosed Mondays.\n"
    )
    contact_html = (
        '<div class="sc-cta-pair"><p class="sc-cta-pair__lead">Book a free call this week.</p>'
        '<div><a href="#book">Book a free call</a><a href="#details">Read the plan details</a></div></div>'
    )
    contact = paint(
        contact_html,
        {
            "id": "contact",
            "type": "contact",
            "data": {
                "title": "Contact",
                "body": "Walk-ins only; no reservations needed.",
                "phone": "(555) 014-2288",
                "address": "14 Harbor Lane",
                "hours": joined,
                "email": "",
            },
        },
        contact_copy,
    )
    for phrase in ("Walk-ins only; no reservations needed.", "14 Harbor Lane", joined, "(555) 014-2288", "tel:5550142288"):
        if phrase not in contact:
            return _fail("contact bind missed " + phrase + ": " + contact)
    if "Book a free call" in contact or "Read the plan" in contact:
        return _fail("contact bind kept a demo action: " + contact)
    if not (contact.find("Walk-ins only") < contact.find("14 Harbor Lane") < contact.find(joined)):
        return _fail("contact lines were reordered: " + contact)

    from lib.compose import _apply_page
    from lib.part_swap import bind_hashes

    class _Swap:
        def __init__(self, fn):
            self.bind_hashes = fn

    swap = _Swap(bind_hashes)

    sample = (
        '<section id="hero" class="hero"><div class="wrap hero-stage">'
        '<div class="hero-visual hero-mark" aria-hidden="true"><span>H</span></div>'
        '<div class="hero-copy"><h1>Old headline</h1><p>Old lede</p></div>'
        "</div></section>"
        '<section id="menu" class="sec"><div class="wrap"><h2>Old menu</h2><p>Old rows</p></div></section>'
        "</body>"
    )
    applied = _apply_page(
        sample,
        "",
        "",
        [
            ("hero", '<div data-sc-part="hero-x"><h1>Harbor Tea Room</h1></div>'),
            ("menu", '<div data-sc-part="table-x"><p>Jasmine Pearl</p></div>'),
        ],
        swap,
    )
    if "hero-visual" not in applied or "Old headline" in applied or "Old menu" in applied:
        return _fail("section replace did not keep the mark and drop the renderer: " + applied)
    if applied.count("<h1") != 1 or "Jasmine Pearl" not in applied or 'id="hero"' not in applied:
        return _fail("section replace broke the outline: " + applied)
    if 'class="wrap hero-stage"' not in applied or 'id="menu"' not in applied:
        return _fail("section replace dropped the wrap or the id: " + applied)
    if "[data-sc-part] a+a{margin-inline-start:12px}" not in applied:
        return _fail("part floor did not separate adjacent actions: " + applied)

    print("part_fill selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
