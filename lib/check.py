"""Built-in checks, aligned with the fleet website_checker rails.

Mirrors the fleet SAMPLE patterns (no_sample), the hotlink blocklist, and adds
site-local checks: internal anchors/pages resolve, required meta present,
noindex matches the build flag, no soft placeholder text in visible copy.
Index-only mobile contract: site-header with the script setting is-stuck,
a hero-visual (letter mark or photo), a favicon.svg link and file, and
relative img src only. A page with no img still passes that row.
Index text rows for the phone layout: height:168px fails mobile_hero and
aspect-ratio:16/9 passes it. .reveal at opacity 0 fails mobile_visible unless
a max-width:860px rule sets .reveal to opacity 1, and a page whose .reveal
is never opacity 0 passes. about-panel fails no_empty_panel. href="#main"
passes skip_link. scroll-margin-top passes scroll_margin. No class="phone-bar"
adds no phone_bar row. A phone-bar link passes when its href starts with tel:
and those digits equal the link text. A leading + in the href is not a digit.
Fewer than 7 digits fails phone_bar. A letter-mark
page can pass these; they are CSS and markup, not content.
On-page rows: a relative canonical link, a WebSite JSON-LD script with no
aggregateRating anywhere in the html, a non-empty meta description, exactly
one h1 on the index, and a non-empty alt on every img. A page with no img
still passes img_alt. FAQPage JSON-LD is retired (Google removed the FAQ rich
result 2023-2026): any page emitting FAQPage/Question/Answer markup fails
faq_schema; a page with no FAQPage passes. Visible FAQ sections stay.
A relative img src must name a file beside that HTML; a page with no img
passes missing_file. When copy_text is non-empty, an h2 whose text is
exactly About fails lone_about if the word About is not in the copy, and
visible "Read on" or "Built with SpiderCaster" fails invented_chrome when
that exact phrase is not in the copy. Empty copy_text adds neither row.
Typography rows (every page, 360/390/412px and 1280px): type_floor fails rendered text
under 16px, and body text under 18px; contrast fails WCAG text under 4.5:1, or
3:1 for large text (24px+, or 18.66px+ at weight 700). Each failure names the
file, the CSS selector and the measured value. Computed styles come from a
static cascade over the page's own CSS, not a browser. Alone:
python -m lib.check <site_dir> --typography-only. Reproducibility:
python -m lib.check --reproducible [project_dir] builds the project twice
offline and compares the trees byte for byte.
Tap targets (row tap_target, STATIC, 360px): every a[href], button, input,
select, textarea, [role=button|link|tab|menuitem] and summary needs a resolved box of 44px by
44px. Width and height come from height/min-height/width/min-width/padding/
border/line-height/font-size/display as an interval; FAIL when the upper bound
is under 44px, WARN (not measurable, never PASS) when the bounds straddle 44px.
An inline text link inside a sentence is exempt (WCAG 2.5.8 inline exception).
Alone: python -m lib.check <site_dir> --tap-only.
Mobile gates (STATIC, every page, 360/390/412px): type_floor, contrast and
tap_target run at all three phone widths (type_floor and contrast also at
1280px). sideways_scroll fails an element whose resolved box ends right of the
viewport (px/vw/min-width, % over 100, negative right margin past the gutter,
img/iframe/video width attribute with no max-width, wide table, pre or nowrap
text, long unbreakable word) unless an ancestor below body clips or scrolls it.
mobile_nav_drawer: more than 4 primary nav links at a phone width need a
<button> toggle with aria-expanded="false", aria-controls naming an existing
id, an accessible name and a 44px box; the drawer it controls holds the nav
links, is hidden by default, opens in a static simulation of the page's own
script and has a close mechanism. No nav landmark: SKIP not-run.
mobile_visibility: inventory of mobile-only and hidden-on-mobile elements;
content hidden on phones is WARN; h1 or main hidden at a phone width is FAIL.
Messages: file | selector | measured | static | at Wpx. Alone:
python -m lib.check <site_dir> --mobile-only. Rendered capture evidence from a
mobile_capture.py patterns.json: --mobile-spec PATH (row mobile_spec).
Also in GATES.md: slug_shape (page file and folder names), photo_luma (mean
luma 90-200 for raster img 400px+ wide; SKIP = not-run when Pillow is missing),
svg_photo (an svg standing in for a photo) and grey_tile (always an explicit
not-run SKIP row: not provable from static CSS).
Exit code is nonzero on any FAIL so it can gate CI or a deploy.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

# Same fleet patterns as tools/owp-tools/scripts/website_checker.py
FLEET_SAMPLE_PATTERNS = [
    re.compile(r"\bSAMPLE\b", re.I),
    re.compile(r"placeholder\s+disclaimer", re.I),
    re.compile(r"demo\s+content", re.I),
    re.compile(r"hello\s+world", re.I),
    re.compile(r"sample\s+page", re.I),
    re.compile(r"SAMPLE\s+labels\s+mean\s+placeholder", re.I),
    re.compile(r"under\s+construction", re.I),
    re.compile(r"lorem\s+ipsum", re.I),
]

# Softer placeholder markers, judged on visible text only.
SOFT_PATTERNS = [
    re.compile(r"\bTODO\b"), re.compile(r"\bTBD\b"), re.compile(r"\bFIXME\b"),
    re.compile(r"\bXXX\b"), re.compile(r"\blorem\b", re.I), re.compile(r"\bipsum\b", re.I),
    re.compile(r"placeholder", re.I),
]

HOTLINK_RE = re.compile(
    r"(?:images\.unsplash\.com|plus\.unsplash\.com|img\.freepik\.com|"
    r"cdn\.pixabay\.com|images\.pexels\.com|static\.freepik\.com)",
    re.I,
)


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def visible_text(html: str) -> str:
    p = _Text()
    try:
        p.feed(html)
    except Exception:
        return ""
    return "\n".join(p.parts)


class _ImgSrc(HTMLParser):
    """Collect img src values. A tag with no src is recorded as None."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.srcs: list[str | None] = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        src = None
        for key, val in attrs:
            if key == "src":
                src = "" if val is None else val
        self.srcs.append(src)


def _class_tokens(html: str, token: str) -> bool:
    for match in re.finditer(r"""class\s*=\s*(?:"([^"]*)"|'([^']*)')""", html, re.I):
        value = match.group(1) if match.group(1) is not None else match.group(2)
        if token in value.split():
            return True
    return False


def _script_sets_stuck(html: str) -> bool:
    bodies = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.I | re.S)
    setter = re.compile(r"""classList\s*\.\s*(?:toggle|add)\s*\(\s*['"]is-stuck['"]""")
    return any(setter.search(body) for body in bodies)


def _favicon_link(html: str) -> bool:
    for match in re.finditer(r"<link\b([^>]*)>", html, re.I):
        attrs = match.group(1)
        rel_m = re.search(r"""\brel\s*=\s*(?:"([^"]*)"|'([^']*)')""", attrs, re.I)
        href_m = re.search(r"""\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')""", attrs, re.I)
        if not rel_m or not href_m:
            continue
        rel = rel_m.group(1) if rel_m.group(1) is not None else rel_m.group(2)
        href = href_m.group(1) if href_m.group(1) is not None else href_m.group(2)
        if rel == "icon" and href == "favicon.svg":
            return True
    return False


def _img_srcs(html: str) -> list[str | None]:
    parser = _ImgSrc()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        if re.search(r"<img\b", html, re.I):
            return [None]
        return []
    return parser.srcs


def _remote_img(src: str | None) -> bool:
    if src is None:
        return True
    text = src.strip()
    if not text:
        return True
    lower = text.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        return True
    if text.startswith("//"):
        return True
    return False


def _attr(attrs: str, name: str) -> str | None:
    match = re.search(
        rf"""\b{re.escape(name)}\s*=\s*(?:"([^"]*)"|'([^']*)')""",
        attrs,
        re.I,
    )
    if not match:
        return None
    return match.group(1) if match.group(1) is not None else match.group(2)


def _canonical_ok(html: str) -> bool:
    """A relative canonical link. A domain or protocol-relative href does not count."""
    for match in re.finditer(r"<link\b([^>]*)>", html, re.I):
        rel = _attr(match.group(1), "rel")
        href = _attr(match.group(1), "href")
        if rel is None or href is None or "canonical" not in rel.split():
            continue
        text = href.strip()
        if not text or text.startswith("//"):
            continue
        lower = text.lower()
        if lower.startswith(("http://", "https://")) or "://" in lower:
            continue
        return True
    return False


def _is_website(node) -> bool:
    if isinstance(node, dict):
        kind = node.get("@type")
        kinds = kind if isinstance(kind, list) else [kind]
        ctx = node.get("@context")
        contexts = ctx if isinstance(ctx, list) else [ctx]
        if "WebSite" in kinds and "https://schema.org" in contexts:
            return True
        return any(_is_website(value) for value in node.values())
    if isinstance(node, list):
        return any(_is_website(value) for value in node)
    return False


def _website_script(html: str) -> bool:
    for match in re.finditer(r"<script\b([^>]*)>(.*?)</script>", html, re.I | re.S):
        kind = _attr(match.group(1), "type")
        if not kind or kind.lower() != "application/ld+json":
            continue
        try:
            data = json.loads(match.group(2).strip())
        except ValueError:
            continue
        if _is_website(data):
            return True
    return False


def _type_names(node) -> set[str]:
    if not isinstance(node, dict):
        return set()
    kind = node.get("@type")
    if isinstance(kind, str):
        return {kind}
    if isinstance(kind, list):
        return {item for item in kind if isinstance(item, str)}
    return set()


def _has_type(node, wanted: str) -> bool:
    if isinstance(node, dict):
        if wanted in _type_names(node):
            return True
        return any(_has_type(value, wanted) for value in node.values())
    if isinstance(node, list):
        return any(_has_type(value, wanted) for value in node)
    return False


def _has_faqpage(html: str) -> bool:
    """True when any JSON-LD block carries @type FAQPage (retired type)."""
    if "FAQPage" not in html:
        return False
    for match in re.finditer(r"<script\b([^>]*)>(.*?)</script>", html, re.I | re.S):
        kind = _attr(match.group(1), "type")
        if not kind or kind.lower() != "application/ld+json":
            continue
        try:
            data = json.loads(match.group(2).strip())
        except ValueError:
            continue
        if _has_type(data, "FAQPage"):
            return True
    return False


def _description_ok(html: str) -> bool:
    for match in re.finditer(r"<meta\b([^>]*)>", html, re.I):
        name = _attr(match.group(1), "name")
        content = _attr(match.group(1), "content")
        if name and name.lower() == "description" and content and content.strip():
            return True
    return False


class _ImgAlt(HTMLParser):
    """Collect img alt values. A tag with no alt is recorded as None."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.alts: list[str | None] = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        alt = None
        for key, val in attrs:
            if key == "alt":
                alt = "" if val is None else val
        self.alts.append(alt)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def _img_alts(html: str) -> list[str | None]:
    parser = _ImgAlt()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        if re.search(r"<img\b", html, re.I):
            return [None]
        return []
    return parser.alts


# Exact phrases only. Bare "review" is not a claim.
_EXACT_CLAIM_RES = tuple(
    re.compile(r"\b" + re.escape(phrase) + r"\b", re.I)
    for phrase in ("testimonial", "customer review", "award-winning")
)
# Digit, optional decimal, then /5; or a number then the word star/stars.
_STAR_RATING_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*/\s*5\b|\b\d+(?:\.\d+)?\s+stars?\b",
    re.I,
)


def _collapse_ws(text: str) -> str:
    return " ".join(text.split())


def _local_img_src(src: str | None) -> str | None:
    """Relative img path. Remote, empty, and non-file schemes are not local."""
    if _remote_img(src):
        return None
    text = str(src).split("#", 1)[0].split("?", 1)[0].strip()
    if not text:
        return None
    head = text.split("/", 1)[0]
    if ":" in head:
        return None
    return text


def _img_file_beside(page: Path, src: str) -> bool:
    """True when the relative src is a file beside this HTML page."""
    raw = unquote(src).replace("\\", "/").strip()
    if raw.startswith("/"):
        raw = raw[1:]
    if not raw or re.match(r"^[A-Za-z]:", raw):
        return False
    try:
        return (page.parent / raw).is_file()
    except OSError:
        return False


def _missing_local_imgs(pages: list[Path]) -> tuple[list[str], int]:
    """Relative img srcs that are not files beside the page, plus how many were local."""
    missing: list[str] = []
    local = 0
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        for src in _img_srcs(html):
            rel = _local_img_src(src)
            if rel is None:
                continue
            local += 1
            if _img_file_beside(page, rel):
                continue
            shown = rel if len(rel) <= 80 else rel[:77] + "..."
            missing.append(f"{page.name}: {shown}")
    return missing, local


class _H2Text(HTMLParser):
    """Visible h2 text, one collapsed string per heading."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.texts: list[str] = []
        self._buf: list[str] | None = None
        self._depth = 0
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
            return
        if self.skip or tag != "h2":
            return
        if self._depth == 0:
            self._buf = []
        self._depth += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
            return
        if self.skip or tag != "h2" or not self._depth:
            return
        self._depth -= 1
        if self._depth == 0 and self._buf is not None:
            self.texts.append(_collapse_ws("".join(self._buf)))
            self._buf = None

    def handle_data(self, data):
        if self.skip or self._buf is None:
            return
        self._buf.append(data)


def _h2_texts(html: str) -> list[str]:
    parser = _H2Text()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        return []
    return parser.texts


# The word About, any case. The h2 test stays the exact text "About".
_ABOUT_WORD_RE = re.compile(r"\bAbout\b", re.I)
_CHROME_PHRASES = ("Read on", "Built with SpiderCaster")


def _lone_about_hits(pages: list[Path], copy_text: str) -> list[str]:
    """h2 text that is exactly About when the copy never uses that word."""
    if _ABOUT_WORD_RE.search(copy_text):
        return []
    hits: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        if any(text == "About" for text in _h2_texts(html)):
            hits.append(f"{page.name}: About")
    return hits


# The old phone hero is the property height:168px. min-height:168px is not that.
_OLD_HERO_RE = re.compile(r"(?<![\w-])height\s*:\s*168px\b", re.I)
_HERO_RATIO_RE = re.compile(r"aspect-ratio\s*:\s*16\s*/\s*9\b", re.I)
# Base .reveal, not .reveal.in. The .in class is the script, not the phone rule.
_REVEAL_OPACITY_RE = re.compile(
    r"\.reveal(?![.\w-])[^{}]*\{[^}]*opacity\s*:\s*([01])\b",
    re.I | re.S,
)


def _media_body(html: str, open_brace: int) -> str:
    """CSS inside the braces that open at open_brace. Nested braces count."""
    depth = 0
    for i in range(open_brace, len(html)):
        ch = html[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return html[open_brace + 1:i]
    return html[open_brace + 1:]


def _reveal_opacity(css: str, value: str) -> bool:
    """True when a base .reveal rule in css sets opacity to value."""
    return any(match.group(1) == value for match in _REVEAL_OPACITY_RE.finditer(css))


def _phone_reveal_shown(html: str) -> bool:
    """True when a max-width:860px rule sets .reveal to opacity 1."""
    for match in re.finditer(r"@media\b", html, re.I):
        brace = html.find("{", match.end())
        if brace < 0:
            continue
        header = html[match.end():brace]
        if not re.search(r"max-width\s*:\s*860px\b", header, re.I):
            continue
        if _reveal_opacity(_media_body(html, brace), "1"):
            return True
    return False


class _PhoneBarLinks(HTMLParser):
    """Anchors whose class token is phone-bar. A CSS .phone-bar rule is not one."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str | None, str]] = []
        self._buf: list[str] | None = None
        self._href: str | None = None
        self._depth = 0

    def _start_a(self, attrs) -> None:
        klass = ""
        href = None
        seen_href = False
        for key, val in attrs:
            if key == "class":
                klass = "" if val is None else val
            elif key == "href":
                seen_href = True
                href = "" if val is None else val
        if self._depth == 0 and "phone-bar" not in klass.split():
            return
        if self._depth == 0:
            self._buf = []
            self._href = href if seen_href else None
        self._depth += 1

    def _end_a(self) -> None:
        if not self._depth:
            return
        self._depth -= 1
        if self._depth == 0 and self._buf is not None:
            self.links.append((self._href, "".join(self._buf)))
            self._buf = None
            self._href = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._start_a(attrs)

    def handle_startendtag(self, tag, attrs):
        if tag == "a":
            self._start_a(attrs)
            self._end_a()

    def handle_endtag(self, tag):
        if tag == "a":
            self._end_a()

    def handle_data(self, data):
        if self._buf is not None:
            self._buf.append(data)


def _phone_bar_links_re(html: str) -> list[tuple[str | None, str]]:
    """Regex fallback. Same anchors the parser collects."""
    found: list[tuple[str | None, str]] = []
    for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", html, re.I | re.S):
        klass = _attr(match.group(1), "class")
        if not klass or "phone-bar" not in klass.split():
            continue
        href = _attr(match.group(1), "href")
        text = re.sub(r"<[^>]*>", "", match.group(2))
        found.append((href, text))
    return found


def _phone_bar_links(html: str) -> list[tuple[str | None, str]]:
    parser = _PhoneBarLinks()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        return _phone_bar_links_re(html)
    return parser.links


def _digits(text: str) -> str:
    return "".join(ch for ch in text if ch.isdigit())


def _phone_bar_fault(href: str | None, text: str) -> str:
    """Empty when the bar matches. A leading + is not a digit."""
    raw = "" if href is None else str(href).strip()
    if raw.startswith("mailto:"):
        # D4 email fallback: the ask slot wires to the verbatim address when
        # the copy carries no digits. Verbatim proof lives in the
        # single_primary_cta row; here the shape is enough.
        addr = raw[7:].split("?")[0].strip()
        if "@" not in addr or " " in addr or chr(9) in addr:
            return "mailto href has no address"
        if any(ch in addr for ch in "<>\"'"):
            return "mailto href has no address"
        return ""
    if not raw.startswith("tel:"):
        return "href does not start with tel:"
    href_digits = _digits(raw)
    if href_digits != _digits(text):
        return "digits do not match the link text"
    if len(href_digits) < 7:
        return "fewer than 7 digits"
    return ""


def _add_phone_bar_row(rep: Report, html: str) -> None:
    """One phone_bar row when index has a phone-bar link. No link means no row."""
    links = _phone_bar_links(html)
    if not links:
        return
    faults: list[str] = []
    for href, text in links:
        fault = _phone_bar_fault(href, text)
        if fault and fault not in faults:
            faults.append(fault)
    if faults:
        rep.add("phone_bar", "FAIL", "; ".join(faults))
    else:
        rep.add("phone_bar", "PASS", "tel digits match the link text")


def _add_index_phone_rows(rep: Report, html: str) -> None:
    """Phone-layout rows from index.html text. A letter mark can pass."""
    if _OLD_HERO_RE.search(html):
        rep.add("mobile_hero", "FAIL", "height:168px")
    elif _HERO_RATIO_RE.search(html):
        rep.add("mobile_hero", "PASS", "aspect-ratio:16/9")
    else:
        rep.add("mobile_hero", "FAIL", "missing aspect-ratio:16/9")
    if not _reveal_opacity(html, "0"):
        rep.add("mobile_visible", "PASS", ".reveal is not opacity 0")
    elif _phone_reveal_shown(html):
        rep.add("mobile_visible", "PASS", "max-width:860px sets .reveal to opacity 1")
    else:
        rep.add(
            "mobile_visible",
            "FAIL",
            ".reveal starts at opacity 0 and no max-width:860px rule sets opacity 1",
        )
    if "about-panel" in html:
        rep.add("no_empty_panel", "FAIL", "about-panel")
    else:
        rep.add("no_empty_panel", "PASS")
    if re.search(r"""href\s*=\s*["']#main["']""", html, re.I):
        rep.add("skip_link", "PASS", 'href="#main"')
    else:
        rep.add("skip_link", "FAIL", 'missing href="#main"')
    if "scroll-margin-top" in html:
        rep.add("scroll_margin", "PASS", "scroll-margin-top")
    else:
        rep.add("scroll_margin", "FAIL", "missing scroll-margin-top")
    _add_phone_bar_row(rep, html)


def _part_demo_hits(pages: list[Path], copy_text: str) -> list[str]:
    """Visible catalog sentences inside a part that the copy does not contain."""
    from html.parser import HTMLParser

    class Walker(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack: list[str] = []
            self.skip = 0
            self.lines: list[str] = []

        def handle_starttag(self, tag, attrs):
            kind = "part" if any(key == "data-sc-part" for key, _value in attrs) else tag
            if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
                self.stack.append(kind)
            if tag in {"script", "style", "textarea", "title"}:
                self.skip += 1

        def handle_endtag(self, tag):
            if tag in {"script", "style", "textarea", "title"} and self.skip:
                self.skip -= 1
            for index in range(len(self.stack) - 1, -1, -1):
                if self.stack[index] == tag or (tag == "div" and self.stack[index] == "part"):
                    del self.stack[index:]
                    break

        def handle_data(self, data):
            if self.skip or "part" not in self.stack:
                return
            folded_copy = " ".join(copy_text.split())
            for line in data.splitlines():
                text = line.strip()
                folded = " ".join(text.split())
                if folded and folded not in folded_copy:
                    self.lines.append(text)

    hits: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        walker = Walker()
        try:
            walker.feed(html)
            walker.close()
        except Exception:
            continue
        seen: set[str] = set()
        for line in walker.lines:
            if line in seen:
                continue
            seen.add(line)
            hits.append(f"{page.name}: {line}")
    return hits


def _invented_chrome_hits(pages: list[Path], copy_text: str) -> list[str]:
    """Visible chrome phrases that the copy does not state exactly."""
    hits: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        visible = visible_text(html)
        for phrase in _CHROME_PHRASES:
            if phrase in visible and phrase not in copy_text:
                hits.append(f"{page.name}: {phrase}")
    return hits


def _ungrounded_claim_hits(pages: list[Path], copy_text: str) -> list[str]:
    """Phrases on a page that the supplied copy does not contain."""
    copy_norm = _collapse_ws(copy_text).casefold()
    hits: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        visible = _collapse_ws(visible_text(html))
        seen: set[str] = set()
        phrases: list[str] = []
        for rx in _EXACT_CLAIM_RES:
            match = rx.search(visible)
            if match:
                phrases.append(match.group(0))
        phrases.extend(match.group(0) for match in _STAR_RATING_RE.finditer(visible))
        for phrase in phrases:
            key = _collapse_ws(phrase).casefold()
            if not key or key in seen:
                continue
            seen.add(key)
            if key in copy_norm:
                continue
            hits.append(f"{page.name}: {phrase}")
    return hits


# ---------------------------------------------------------------------------
# Type floor and WCAG contrast. Static CSS cascade, no headless browser.
#
# Page HTML is parsed into a small DOM. <style> blocks, local <link
# rel=stylesheet> files and style="" attributes go through a cascade
# (specificity, source order, !important, inheritance, var(), calc/clamp,
# rem/em/vw, @media width queries) at two viewports. The measured font size,
# weight, text colour and backdrop colour per text element are then judged:
#   type_floor: text under 16px fails; body text (p, li, plain copy) under 18px
#               fails.
#   contrast:   WCAG 2 ratio, 4.5:1, or 3:1 for large text (>=24px, or
#               >=18.66px at weight 700+).
# Every failure names the page file, the CSS selector that set the failing
# value, and the measured value. Run it alone with --typography-only.
# ---------------------------------------------------------------------------
TYPE_FLOOR_PX = 16.0
BODY_FLOOR_PX = 18.0
CONTRAST_BODY = 4.5
CONTRAST_LARGE = 3.0
LARGE_PX = 24.0
LARGE_BOLD_PX = 18.66
BOLD_WEIGHT = 700
# Phone widths every mobile gate is judged at (small Android, iPhone 14, 412 Android),
# and the desktop baseline. type_floor and contrast run at all four; tap_target and
# the mobile rows run at the phone widths.
MOBILE_VIEWPORTS = ((360, 740), (390, 844), (412, 915))
DESKTOP_VIEWPORT = (1280, 800)
TYPO_VIEWPORTS = MOBILE_VIEWPORTS + (DESKTOP_VIEWPORT,)

# Chrome (menus, labels, footers, captions) keeps the 16px floor. Everything else,
# buttons and links included, is body text and needs 18px. Headings need 16px.
_CHROME_TAGS = frozenset((
    "header", "nav", "footer", "label", "figcaption", "caption",
    "small", "summary", "th", "legend", "select", "option",
))
_CHROME_ROLES = frozenset(("navigation", "banner", "contentinfo", "tab", "menuitem", "tablist"))
_HEADING_TAGS = frozenset(("h1", "h2", "h3", "h4", "h5", "h6"))
_SKIP_TAGS = frozenset((
    "head", "script", "style", "title", "meta", "link", "template", "noscript",
    "svg", "math", "textarea", "option", "select", "datalist", "canvas", "iframe",
    "object", "video", "audio",
))
_VOID_TAGS = frozenset((
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
))

_UA_CSS = """
[hidden]{display:none}
h1{font-size:2em;font-weight:700}
h2{font-size:1.5em;font-weight:700}
h3{font-size:1.17em;font-weight:700}
h4{font-weight:700}
h5{font-size:.83em;font-weight:700}
h6{font-size:.67em;font-weight:700}
b,strong,th{font-weight:700}
small,sub,sup{font-size:.83em}
a:link{color:#0000ee}
button,input,select,textarea{font-size:13.3333px;color:#000}
button{background-color:#efefef}
button,input,select,textarea{line-height:normal}
button{padding:1px 6px;border:2px solid}
input,select,textarea{padding:1px 2px;border:2px solid}
"""

_NAMED_COLORS = {
    "black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000",
    "blue": "#0000ff", "yellow": "#ffff00", "orange": "#ffa500", "purple": "#800080",
    "pink": "#ffc0cb", "gray": "#808080", "grey": "#808080", "silver": "#c0c0c0",
    "maroon": "#800000", "olive": "#808000", "lime": "#00ff00", "aqua": "#00ffff",
    "cyan": "#00ffff", "teal": "#008080", "navy": "#000080", "fuchsia": "#ff00ff",
    "magenta": "#ff00ff", "brown": "#a52a2a", "gold": "#ffd700", "beige": "#f5f5dc",
    "ivory": "#fffff0", "khaki": "#f0e68c", "lavender": "#e6e6fa", "coral": "#ff7f50",
    "salmon": "#fa8072", "tomato": "#ff6347", "crimson": "#dc143c", "indigo": "#4b0082",
    "violet": "#ee82ee", "turquoise": "#40e0d0", "tan": "#d2b48c", "wheat": "#f5deb3",
    "linen": "#faf0e6", "snow": "#fffafa", "azure": "#f0ffff", "orchid": "#da70d6",
    "plum": "#dda0dd", "sienna": "#a0522d", "chocolate": "#d2691e", "firebrick": "#b22222",
    "darkgray": "#a9a9a9", "darkgrey": "#a9a9a9", "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3", "dimgray": "#696969", "dimgrey": "#696969",
    "gainsboro": "#dcdcdc", "whitesmoke": "#f5f5f5", "slategray": "#708090",
    "slategrey": "#708090", "darkslategray": "#2f4f4f", "darkred": "#8b0000",
    "darkgreen": "#006400", "darkblue": "#00008b", "lightblue": "#add8e6",
    "lightgreen": "#90ee90", "skyblue": "#87ceeb", "steelblue": "#4682b4",
    "royalblue": "#4169e1", "midnightblue": "#191970", "rebeccapurple": "#663399",
    "lightyellow": "#ffffe0", "darkorange": "#ff8c00", "hotpink": "#ff69b4",
    "goldenrod": "#daa520", "forestgreen": "#228b22", "seagreen": "#2e8b57",
}

# ----- text scanning helpers ------------------------------------------------


def _strip_css_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _skip_quote(text: str, i: int) -> int:
    """text[i] is a quote. Index just past its closing quote."""
    q = text[i]
    j = i + 1
    n = len(text)
    while j < n:
        if text[j] == "\\":
            j += 2
            continue
        if text[j] == q:
            return j + 1
        j += 1
    return n


def _scan_block(css: str, i: int) -> int:
    """css[i] is '{'. Index of its matching '}' (or the end of the text)."""
    depth = 0
    n = len(css)
    j = i
    while j < n:
        ch = css[j]
        if ch in "\"'":
            j = _skip_quote(css, j)
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return n


def _split_top(text: str, sep: str) -> list[str]:
    """Split on sep outside (), [] and quotes."""
    parts: list[str] = []
    depth = 0
    cur: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in "\"'":
            j = _skip_quote(text, i)
            cur.append(text[i:j])
            i = j
            continue
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    parts.append("".join(cur))
    return parts


def _split_ws(text: str) -> list[str]:
    """Split on whitespace outside (), [] and quotes."""
    parts: list[str] = []
    depth = 0
    cur: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in "\"'":
            j = _skip_quote(text, i)
            cur.append(text[i:j])
            i = j
            continue
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch.isspace() and depth == 0:
            if cur:
                parts.append("".join(cur))
                cur = []
        else:
            cur.append(ch)
        i += 1
    if cur:
        parts.append("".join(cur))
    return parts


# ----- CSS parsing ----------------------------------------------------------


def _parse_css_items(css: str) -> list:
    """Rules and conditional at-rules. Other at-rules are dropped."""
    items: list = []
    i = 0
    n = len(css)
    while i < n:
        while i < n and css[i].isspace():
            i += 1
        if i >= n:
            break
        j = i
        depth = 0
        while j < n:
            ch = css[j]
            if ch in "\"'":
                j = _skip_quote(css, j)
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif depth == 0 and ch in "{;}":
                break
            j += 1
        prelude = css[i:j].strip()
        if j >= n:
            break
        if css[j] in ";}":
            i = j + 1
            continue
        end = _scan_block(css, j)
        body = css[j + 1:end]
        i = end + 1
        if prelude.startswith("@"):
            match = re.match(r"@([\w-]+)", prelude)
            if not match:
                continue
            name = match.group(1).lower()
            rest = prelude[match.end():].strip()
            if name in ("media", "supports", "layer"):
                items.append(("at", name, rest, _parse_css_items(body)))
        elif prelude:
            items.append(("rule", prelude, body))
    return items


def _parse_decls(body: str) -> list[tuple[str, str, bool]]:
    out: list[tuple[str, str, bool]] = []
    for chunk in _split_top(body, ";"):
        if ":" not in chunk:
            continue
        prop, val = chunk.split(":", 1)
        prop = prop.strip()
        val = val.strip()
        important = False
        match = re.search(r"!\s*important\s*$", val, re.I)
        if match:
            important = True
            val = val[:match.start()].strip()
        if not prop.startswith("--"):
            prop = prop.lower()
        if prop and val:
            out.append((prop, val, important))
    return out


def _media_length(text: str) -> float | None:
    match = re.match(r"^\s*(-?\d*\.?\d+)\s*(px|em|rem)?\s*$", text.lower())
    if not match:
        return None
    value = float(match.group(1))
    return value * 16.0 if match.group(2) in ("em", "rem") else value


def _media_feature(inner: str, w: int, h: int) -> bool:
    inner = inner.strip().lower()
    dims = {"width": float(w), "height": float(h)}
    parts = re.split(r"(<=|>=|<|>|=)", inner)
    if len(parts) in (3, 5):
        ops = {"<": lambda a, b: a < b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b,
               ">=": lambda a, b: a >= b, "=": lambda a, b: a == b}
        flip = {"<": ">", ">": "<", "<=": ">=", ">=": "<=", "=": "="}
        names = [p.strip() for p in parts[0::2]]
        symbols = parts[1::2]
        feats = [k for k, name in enumerate(names) if name in dims]
        if len(feats) != 1:
            return False
        k = feats[0]
        ok = True
        for pos, symbol in enumerate(symbols):
            left, right = names[pos], names[pos + 1]
            if left in dims:
                value = _media_length(right)
                if value is None:
                    return False
                ok = ok and ops[symbol](dims[left], value)
            else:
                value = _media_length(left)
                if value is None:
                    return False
                ok = ok and ops[flip[symbol]](dims[right], value)
        return ok
    if ":" in inner:
        name, val = (x.strip() for x in inner.split(":", 1))
    else:
        name, val = inner, ""
    for prefix, key, cmp in (("min-", None, "min"), ("max-", None, "max")):
        if name.startswith(prefix) and name[len(prefix):] in dims:
            value = _media_length(val)
            if value is None:
                return False
            actual = dims[name[len(prefix):]]
            return actual >= value if cmp == "min" else actual <= value
    if name in dims:
        value = _media_length(val)
        return value is not None and dims[name] == value
    mobile = w < 800
    table = {
        "orientation": "portrait" if h >= w else "landscape",
        "prefers-color-scheme": "light",
        "prefers-reduced-motion": "no-preference",
        "prefers-contrast": "no-preference",
        "scripting": "enabled",
        "hover": "none" if mobile else "hover",
        "any-hover": "none" if mobile else "hover",
        "pointer": "coarse" if mobile else "fine",
        "any-pointer": "coarse" if mobile else "fine",
    }
    if name in table:
        return val == table[name] if val else True
    return False


def _media_one(query: str, w: int, h: int) -> bool:
    query = query.strip().lower()
    negate = False
    if query.startswith("not "):
        negate = True
        query = query[4:].strip()
    if query.startswith("only "):
        query = query[5:].strip()
    result = True
    for part in re.split(r"\band\b", query):
        part = part.strip()
        if not part:
            continue
        if part.startswith("(") and part.endswith(")"):
            inner = part[1:-1]
            if "(" in inner:
                result = False
            else:
                result = result and _media_feature(inner, w, h)
        elif part in ("screen", "all"):
            pass
        else:
            result = False
    return (not result) if negate else result


def _media_matches(query: str, w: int, h: int) -> bool:
    query = query.strip()
    if not query:
        return True
    return any(_media_one(q, w, h) for q in _split_top(query, ","))


def _flatten_css(items: list, w: int, h: int) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for item in items:
        if item[0] == "rule":
            out.append((item[1], item[2]))
            continue
        _, name, rest, sub = item
        if name == "media" and not _media_matches(rest, w, h):
            continue
        out.extend(_flatten_css(sub, w, h))
    return out


# ----- selectors ------------------------------------------------------------

_ELEMENT_ONLY_PSEUDOS = frozenset((
    "root", "first-child", "last-child", "only-child", "first-of-type",
    "last-of-type", "only-of-type", "empty", "link", "any-link",
))
_NTH_PSEUDOS = frozenset(("nth-child", "nth-last-child", "nth-of-type", "nth-last-of-type"))
_LOGICAL_PSEUDOS = frozenset(("not", "is", "where", "matches"))


class _Sel:
    def __init__(self, text: str):
        self.text = text
        self.comps: list[dict] = []
        self.combs: list[str] = []
        self.spec = (0, 0, 0)
        self.ok = True


def _parse_nth(arg: str) -> tuple[int, int] | None:
    text = re.split(r"\s+of\s+", arg.strip().lower())[0].strip().replace(" ", "")
    if text == "odd":
        return (2, 1)
    if text == "even":
        return (2, 0)
    match = re.match(r"^([+-]?\d*)n([+-]\d+)?$", text)
    if match:
        raw = match.group(1)
        a = -1 if raw == "-" else 1 if raw in ("", "+") else int(raw)
        return (a, int(match.group(2) or 0))
    if re.match(r"^[+-]?\d+$", text):
        return (0, int(text))
    return None


def _add_spec(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _parse_compound(text: str) -> tuple[dict | None, tuple[int, int, int]]:
    comp: dict = {"tag": None, "ids": [], "cls": [], "attrs": [], "pseudos": []}
    spec = (0, 0, 0)
    i = 0
    n = len(text)
    match = re.match(r"(\*|-?[A-Za-z_][\w-]*)", text)
    if match:
        if match.group(1) != "*":
            comp["tag"] = match.group(1).lower()
            spec = _add_spec(spec, (0, 0, 1))
        i = match.end()
    while i < n:
        ch = text[i]
        if ch in "#.":
            match = re.match(r"[#.]((?:[\w-]|\\.|[^\x00-\x7f])+)", text[i:])
            if not match:
                return None, spec
            name = re.sub(r"\\(.)", r"\1", match.group(1))
            if ch == "#":
                comp["ids"].append(name)
                spec = _add_spec(spec, (1, 0, 0))
            else:
                comp["cls"].append(name)
                spec = _add_spec(spec, (0, 1, 0))
            i += match.end()
        elif ch == "[":
            depth = 0
            j = i
            while j < n:
                if text[j] in "\"'":
                    j = _skip_quote(text, j)
                    continue
                if text[j] == "[":
                    depth += 1
                elif text[j] == "]":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner = text[i + 1:j]
            match = re.match(
                r"""^\s*([\w:-]+)\s*(?:([~|^$*]?=)\s*("([^"]*)"|'([^']*)'|[^\s\]]+)\s*([iIsS])?)?\s*$""",
                inner,
            )
            if not match:
                return None, spec
            val = match.group(4) if match.group(4) is not None else match.group(5)
            if val is None and match.group(3) is not None:
                val = match.group(3)
            comp["attrs"].append((
                match.group(1).lower(), match.group(2), val,
                (match.group(6) or "").lower() == "i",
            ))
            spec = _add_spec(spec, (0, 1, 0))
            i = j + 1
        elif ch == ":":
            if text.startswith("::", i):
                return None, spec
            match = re.match(r":([\w-]+)", text[i:])
            if not match:
                return None, spec
            name = match.group(1).lower()
            i += match.end()
            arg = None
            if i < n and text[i] == "(":
                depth = 0
                j = i
                while j < n:
                    if text[j] in "\"'":
                        j = _skip_quote(text, j)
                        continue
                    if text[j] == "(":
                        depth += 1
                    elif text[j] == ")":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                arg = text[i + 1:j]
                i = j + 1
            if name in _LOGICAL_PSEUDOS:
                subs = [_parse_selector(x) for x in _split_top(arg or "", ",")]
                if not subs or any(not s.ok for s in subs):
                    return None, spec
                comp["pseudos"].append((name, subs))
                if name != "where":
                    spec = _add_spec(spec, max(s.spec for s in subs))
            elif name in _ELEMENT_ONLY_PSEUDOS:
                comp["pseudos"].append((name, None))
                spec = _add_spec(spec, (0, 1, 0))
            elif name in _NTH_PSEUDOS:
                nth = _parse_nth(arg or "")
                if nth is None:
                    return None, spec
                comp["pseudos"].append((name, nth))
                spec = _add_spec(spec, (0, 1, 0))
            else:
                # :hover, :focus, :has(), vendor and unknown pseudos: not judged.
                return None, spec
        else:
            return None, spec
    return comp, spec


def _parse_selector(text: str) -> _Sel:
    sel = _Sel(text.strip())
    chunks: list[str] = []
    combs: list[str] = []
    buf: list[str] = []
    pending: str | None = None
    start_comb = " "
    depth = 0
    i = 0
    raw = sel.text
    n = len(raw)

    def flush() -> None:
        nonlocal buf
        if buf:
            chunks.append("".join(buf))
            combs.append(start_comb)
            buf = []

    while i < n:
        ch = raw[i]
        if ch in "\"'":
            j = _skip_quote(raw, i)
            if not buf:
                start_comb = pending or " "
                pending = None
            buf.append(raw[i:j])
            i = j
            continue
        if ch == "\\" and i + 1 < n:
            if not buf:
                start_comb = pending or " "
                pending = None
            buf.append(raw[i:i + 2])
            i += 2
            continue
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if depth == 0 and (ch.isspace() or ch in ">+~"):
            flush()
            if ch in ">+~":
                pending = ch
            elif pending is None:
                pending = " "
            i += 1
            continue
        if not buf:
            start_comb = pending or " "
            pending = None
        buf.append(ch)
        i += 1
    flush()
    if not chunks or pending is not None:
        sel.ok = False
        return sel
    spec = (0, 0, 0)
    for chunk in chunks:
        comp, cspec = _parse_compound(chunk)
        if comp is None:
            sel.ok = False
            return sel
        sel.comps.append(comp)
        spec = _add_spec(spec, cspec)
    sel.combs = combs
    sel.spec = spec
    return sel


class _Node:
    def __init__(self, tag: str, attrs: dict, parent):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list[_Node] = []
        self.texts: list[str] = []
        self.raw: list[str] = []
        self.classes = attrs.get("class", "").split()
        self.cs: dict | None = None


def _sib_index(node: _Node, of_type: bool, from_end: bool) -> int:
    sibs = node.parent.children if node.parent else [node]
    if of_type:
        sibs = [s for s in sibs if s.tag == node.tag]
    if from_end:
        sibs = sibs[::-1]
    for pos, sib in enumerate(sibs):
        if sib is node:
            return pos + 1
    return 0


def _match_pseudo(name: str, arg, node: _Node) -> bool:
    if name == "not":
        return not any(_match_sel(s, node) for s in arg)
    if name in ("is", "where", "matches"):
        return any(_match_sel(s, node) for s in arg)
    if name == "root":
        return node.parent is not None and node.parent.tag == "#doc" and node.tag == "html"
    if name in ("link", "any-link"):
        return node.tag in ("a", "area") and "href" in node.attrs
    if name == "empty":
        return not node.children and not any(t.strip() for t in node.texts)
    sibs = node.parent.children if node.parent else [node]
    if name == "first-child":
        return _sib_index(node, False, False) == 1
    if name == "last-child":
        return _sib_index(node, False, True) == 1
    if name == "only-child":
        return len(sibs) == 1
    if name == "first-of-type":
        return _sib_index(node, True, False) == 1
    if name == "last-of-type":
        return _sib_index(node, True, True) == 1
    if name == "only-of-type":
        return sum(1 for s in sibs if s.tag == node.tag) == 1
    if name in _NTH_PSEUDOS:
        a, b = arg
        idx = _sib_index(node, "type" in name, "last" in name)
        if a == 0:
            return idx == b
        diff = idx - b
        return diff % a == 0 and diff // a >= 0
    return False


def _match_comp(comp: dict, node: _Node) -> bool:
    if node.tag == "#doc":
        return False
    if comp["tag"] and node.tag != comp["tag"]:
        return False
    for ident in comp["ids"]:
        if node.attrs.get("id") != ident:
            return False
    for klass in comp["cls"]:
        if klass not in node.classes:
            return False
    for name, op, val, ci in comp["attrs"]:
        have = node.attrs.get(name)
        if have is None:
            return False
        if op is None:
            continue
        want = val or ""
        if ci:
            have, want = have.lower(), want.lower()
        if op == "=" and have != want:
            return False
        if op == "~=" and want not in have.split():
            return False
        if op == "|=" and not (have == want or have.startswith(want + "-")):
            return False
        if op == "^=" and not (want and have.startswith(want)):
            return False
        if op == "$=" and not (want and have.endswith(want)):
            return False
        if op == "*=" and not (want and want in have):
            return False
    for name, arg in comp["pseudos"]:
        if not _match_pseudo(name, arg, node):
            return False
    return True


def _match_from(sel: _Sel, k: int, node: _Node) -> bool:
    if not _match_comp(sel.comps[k], node):
        return False
    if k == 0:
        return True
    comb = sel.combs[k]
    if comb == ">":
        return node.parent is not None and _match_from(sel, k - 1, node.parent)
    if comb == " ":
        anc = node.parent
        while anc is not None:
            if _match_from(sel, k - 1, anc):
                return True
            anc = anc.parent
        return False
    sibs = node.parent.children if node.parent else []
    pos = next((p for p, s in enumerate(sibs) if s is node), -1)
    if pos <= 0:
        return False
    if comb == "+":
        return _match_from(sel, k - 1, sibs[pos - 1])
    return any(_match_from(sel, k - 1, sibs[p]) for p in range(pos))


def _match_sel(sel: _Sel, node: _Node) -> bool:
    return bool(sel.comps) and _match_from(sel, len(sel.comps) - 1, node)


# ----- DOM ------------------------------------------------------------------

_P_CLOSERS = frozenset((
    "p", "div", "ul", "ol", "dl", "h1", "h2", "h3", "h4", "h5", "h6", "section",
    "article", "nav", "header", "footer", "table", "form", "blockquote", "pre",
    "hr", "aside", "main", "figure", "details", "fieldset", "address",
))
_AUTOCLOSE = {
    "li": {"li"}, "dt": {"dt", "dd"}, "dd": {"dt", "dd"}, "tr": {"tr"},
    "td": {"td", "th"}, "th": {"td", "th"}, "option": {"option"},
}


class _DomBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("#doc", {}, None)
        self.stack: list[_Node] = [self.root]

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        top = self.stack[-1]
        if top.tag == "p" and tag in _P_CLOSERS:
            self.stack.pop()
        elif tag in _AUTOCLOSE and top.tag in _AUTOCLOSE[tag]:
            self.stack.pop()
        parent = self.stack[-1]
        node = _Node(tag, {k.lower(): ("" if v is None else v) for k, v in attrs}, parent)
        parent.children.append(node)
        if tag not in _VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in _VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        for k in range(len(self.stack) - 1, 0, -1):
            if self.stack[k].tag == tag:
                del self.stack[k:]
                return

    def handle_data(self, data):
        top = self.stack[-1]
        if top.tag in ("style", "script", "title", "textarea"):
            top.raw.append(data)
        else:
            top.texts.append(data)


def _build_dom(html: str) -> _Node:
    builder = _DomBuilder()
    try:
        builder.feed(html)
        builder.close()
    except Exception:
        pass
    return builder.root


def _iter_nodes(root: _Node):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.children))


# ----- values: colours, lengths, var() ---------------------------------------


def _parse_color(text: str, current=None):
    """(r, g, b, a) with r/g/b 0..255 and a 0..1, or None when unsupported."""
    t = text.strip().lower()
    if t == "transparent":
        return (0.0, 0.0, 0.0, 0.0)
    if t == "currentcolor":
        return current
    if t in _NAMED_COLORS:
        t = _NAMED_COLORS[t]
    if t.startswith("#"):
        h = t[1:]
        if not re.match(r"^[0-9a-f]+$", h):
            return None
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            h += "ff"
        if len(h) != 8:
            return None
        return (float(int(h[0:2], 16)), float(int(h[2:4], 16)), float(int(h[4:6], 16)),
                int(h[6:8], 16) / 255.0)
    match = re.match(r"^(rgba?|hsla?)\((.*)\)$", t)
    if not match:
        return None
    args = [a for a in re.split(r"[\s,/]+", match.group(2).strip()) if a]
    if len(args) not in (3, 4) or any(a == "none" or a.startswith("from") for a in args):
        return None

    def num(a: str, scale: float) -> float | None:
        try:
            if a.endswith("%"):
                return float(a[:-1]) / 100.0 * scale
            return float(a)
        except ValueError:
            return None

    alpha = 1.0
    if len(args) == 4:
        got = num(args[3], 1.0)
        if got is None:
            return None
        alpha = min(1.0, max(0.0, got))
    if match.group(1).startswith("rgb"):
        vals = [num(a, 255.0) for a in args[:3]]
        if any(v is None for v in vals):
            return None
        return (min(255.0, max(0.0, vals[0])), min(255.0, max(0.0, vals[1])),
                min(255.0, max(0.0, vals[2])), alpha)
    hue_s = args[0]
    try:
        if hue_s.endswith("turn"):
            hue = float(hue_s[:-4]) * 360.0
        elif hue_s.endswith("rad"):
            hue = float(hue_s[:-3]) * 57.29577951308232
        elif hue_s.endswith("deg"):
            hue = float(hue_s[:-3])
        else:
            hue = float(hue_s)
    except ValueError:
        return None
    sat = num(args[1], 1.0)
    lig = num(args[2], 1.0)
    if sat is None or lig is None:
        return None
    sat = min(1.0, max(0.0, sat))
    lig = min(1.0, max(0.0, lig))
    hue = (hue % 360.0) / 360.0
    q = lig * (1 + sat) if lig < 0.5 else lig + sat - lig * sat
    p = 2 * lig - q

    def chan(tt: float) -> float:
        tt %= 1.0
        if tt < 1 / 6:
            return p + (q - p) * 6 * tt
        if tt < 1 / 2:
            return q
        if tt < 2 / 3:
            return p + (q - p) * (2 / 3 - tt) * 6
        return p

    return (chan(hue + 1 / 3) * 255.0, chan(hue) * 255.0, chan(hue - 1 / 3) * 255.0, alpha)


def _hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(int(round(min(255.0, max(0.0, c)))) for c in rgb[:3])


def _blend(fg, bg_rgb):
    """Colour fg (r, g, b, a) over an opaque (r, g, b)."""
    a = fg[3]
    return (fg[0] * a + bg_rgb[0] * (1 - a), fg[1] * a + bg_rgb[1] * (1 - a),
            fg[2] * a + bg_rgb[2] * (1 - a))


def _luminance(rgb) -> float:
    def lin(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])


def contrast_ratio(fg_rgb, bg_rgb) -> float:
    """WCAG 2 contrast ratio of two opaque colours, 1..21."""
    a, b = _luminance(fg_rgb), _luminance(bg_rgb)
    hi, lo = (a, b) if a >= b else (b, a)
    return (hi + 0.05) / (lo + 0.05)


_LEN_TOKEN = re.compile(
    r"\s*(?:(?P<num>[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)(?P<unit>[a-zA-Z%]*)"
    r"|(?P<fn>[a-zA-Z-]+)\(|(?P<op>[()+\-*/,]))"
)


class _Ctx:
    def __init__(self, w: int, h: int):
        self.w = float(w)
        self.h = float(h)
        self.root = 16.0


def _eval_len(expr: str, em, ctx: _Ctx, pct):
    """Length expression to px, or None when it cannot be resolved."""
    tokens: list[tuple[str, object]] = []
    pos = 0
    text = expr.strip()
    while pos < len(text):
        match = _LEN_TOKEN.match(text, pos)
        if not match or match.end() == pos:
            return None
        prev_value = bool(tokens) and (tokens[-1][0] == "num" or tokens[-1] == ("op", ")"))
        if match.group("num") is not None:
            numtext = match.group("num")
            if prev_value and numtext[0] in "+-":
                tokens.append(("op", numtext[0]))
                numtext = numtext[1:]
            tokens.append(("num", (float(numtext), match.group("unit").lower())))
        elif match.group("fn") is not None:
            tokens.append(("fn", match.group("fn").lower()))
        else:
            tokens.append(("op", match.group("op")))
        pos = match.end()
    idx = 0

    def need(op: str) -> None:
        nonlocal idx
        if idx < len(tokens) and tokens[idx] == ("op", op):
            idx += 1
            return
        raise ValueError(op)

    def unit_px(value: float, unit: str):
        if unit == "":
            return (value, 0)
        if unit == "px":
            return (value, 1)
        if unit == "em":
            if em is None:
                raise ValueError("em")
            return (value * em, 1)
        if unit == "rem":
            return (value * ctx.root, 1)
        if unit == "%":
            if pct is None:
                raise ValueError("%")
            return (value / 100.0 * pct, 1)
        table = {"vw": ctx.w / 100, "svw": ctx.w / 100, "lvw": ctx.w / 100,
                 "dvw": ctx.w / 100, "vh": ctx.h / 100, "svh": ctx.h / 100,
                 "lvh": ctx.h / 100, "dvh": ctx.h / 100,
                 "vmin": min(ctx.w, ctx.h) / 100, "vmax": max(ctx.w, ctx.h) / 100,
                 "pt": 96 / 72, "pc": 16.0, "in": 96.0, "cm": 96 / 2.54,
                 "mm": 96 / 25.4, "q": 96 / 101.6}
        if unit in table:
            return (value * table[unit], 1)
        if unit in ("ch", "ex"):
            if em is None:
                raise ValueError("em")
            return (value * em * 0.5, 1)
        raise ValueError(unit)

    def parse_expr():
        nonlocal idx
        left = parse_term()
        while idx < len(tokens) and tokens[idx][0] == "op" and tokens[idx][1] in "+-":
            op = tokens[idx][1]
            idx += 1
            right = parse_term()
            if left[1] != right[1]:
                raise ValueError("dim")
            left = (left[0] + right[0] if op == "+" else left[0] - right[0], left[1])
        return left

    def parse_term():
        nonlocal idx
        left = parse_factor()
        while idx < len(tokens) and tokens[idx][0] == "op" and tokens[idx][1] in "*/":
            op = tokens[idx][1]
            idx += 1
            right = parse_factor()
            if op == "*":
                left = (left[0] * right[0], left[1] + right[1])
            else:
                if right[0] == 0:
                    raise ValueError("div0")
                left = (left[0] / right[0], left[1] - right[1])
        return left

    def parse_factor():
        nonlocal idx
        if idx >= len(tokens):
            raise ValueError("end")
        kind, val = tokens[idx]
        if kind == "num":
            idx += 1
            return unit_px(val[0], val[1])
        if kind == "op" and val == "(":
            idx += 1
            inner = parse_expr()
            need(")")
            return inner
        if kind == "fn":
            idx += 1
            args = [parse_expr()]
            while idx < len(tokens) and tokens[idx] == ("op", ","):
                idx += 1
                args.append(parse_expr())
            need(")")
            if val in ("calc", "-webkit-calc", "-moz-calc") and len(args) == 1:
                return args[0]
            if val in ("min", "max") and args:
                if len({a[1] for a in args}) != 1:
                    raise ValueError("dim")
                pick = min if val == "min" else max
                return (pick(a[0] for a in args), args[0][1])
            if val == "clamp" and len(args) == 3:
                lo, mid, hi = args
                return (max(lo[0], min(mid[0], hi[0])), mid[1])
            raise ValueError(val)
        raise ValueError("token")

    try:
        value, dim = parse_expr()
        if idx != len(tokens):
            return None
    except (ValueError, IndexError):
        return None
    if dim != 1 and not (dim == 0 and value == 0):
        return None
    return value


def _subst_vars(val: str, customs: dict, depth: int = 0):
    """Replace var(--x, fallback). None when a variable cannot be resolved."""
    if "var(" not in val:
        return val
    if depth > 8:
        return None
    out: list[str] = []
    i = 0
    while True:
        k = val.find("var(", i)
        if k < 0:
            out.append(val[i:])
            break
        out.append(val[i:k])
        d = 0
        j = k + 3
        while j < len(val):
            if val[j] == "(":
                d += 1
            elif val[j] == ")":
                d -= 1
                if d == 0:
                    break
            j += 1
        if j >= len(val):
            return None
        inner = val[k + 4:j]
        parts = _split_top(inner, ",")
        name = parts[0].strip()
        fallback = ",".join(parts[1:]).strip() if len(parts) > 1 else None
        rep = customs.get(name)
        if rep is None:
            rep = fallback
        if rep is None:
            return None
        rep = _subst_vars(rep, customs, depth + 1)
        if rep is None:
            return None
        out.append(rep)
        i = j + 1
    return "".join(out)


_SIZE_WORDS = {"xx-small": 9.0, "x-small": 10.0, "small": 13.0, "medium": 16.0,
               "large": 18.0, "x-large": 24.0, "xx-large": 32.0, "xxx-large": 48.0}


def _resolve_size(val: str, psize, ctx: _Ctx):
    v = val.strip().lower()
    if v in ("inherit", "unset"):
        return psize
    if v in ("initial", "revert"):
        return 16.0
    if v in _SIZE_WORDS:
        return _SIZE_WORDS[v]
    if v == "smaller":
        return None if psize is None else psize / 1.2
    if v == "larger":
        return None if psize is None else psize * 1.2
    got = _eval_len(v, psize, ctx, psize)
    if got is None or got < 0:
        return None
    return got


_WEIGHT_WORDS = {"normal": 400, "bold": 700, "lighter": 300}


def _resolve_weight(val: str, pweight: int) -> int | None:
    v = val.strip().lower()
    if v in ("inherit", "unset"):
        return pweight
    if v == "initial":
        return 400
    if v in _WEIGHT_WORDS:
        return _WEIGHT_WORDS[v]
    if v == "bolder":
        return 700 if pweight < 600 else 900
    try:
        number = float(v)
    except ValueError:
        return None
    return int(number) if 1 <= number <= 1000 else None


def _font_shorthand(val: str) -> list[tuple[str, str]]:
    v = val.strip().lower()
    if v in ("inherit", "unset", "revert"):
        return [("font-size", "inherit"), ("font-weight", "inherit"), ("line-height", "inherit")]
    if v == "initial":
        return [("font-size", "medium"), ("font-weight", "normal"), ("line-height", "normal")]
    weight = "400"
    size = None
    lh = "normal"
    toks = _split_ws(val)
    for i, tok in enumerate(toks):
        tl = tok.lower()
        if tl in ("bold", "bolder", "lighter"):
            weight = tl
        elif re.match(r"^\d{3,4}$", tl):
            weight = tl
        elif tl in ("normal", "italic", "oblique", "small-caps", "ultra-condensed",
                    "extra-condensed", "condensed", "semi-condensed", "semi-expanded",
                    "expanded", "extra-expanded", "ultra-expanded"):
            continue
        else:
            parts = _split_top(tok, "/")
            size = parts[0]
            if len(parts) > 1 and parts[1].strip():
                lh = parts[1].strip()
            elif i + 1 < len(toks) and toks[i + 1].startswith("/") and len(toks[i + 1]) > 1:
                lh = toks[i + 1][1:]
            elif i + 2 < len(toks) and toks[i + 1] == "/":
                lh = toks[i + 2]
            elif len(parts) > 1 and i + 1 < len(toks):
                lh = toks[i + 1]
            break
    if size is None:
        return []
    return [("font-size", size), ("font-weight", weight), ("line-height", lh)]


_BG_NONCOLOR_WORDS = frozenset((
    "repeat", "no-repeat", "repeat-x", "repeat-y", "space", "round", "scroll", "fixed",
    "local", "center", "top", "bottom", "left", "right", "cover", "contain", "auto",
    "border-box", "padding-box", "content-box", "text", "none", "inherit", "initial",
    "unset", "revert",
))


def _bg_shorthand(val: str) -> list[tuple[str, str]]:
    color = "transparent"
    images: list[str] = []
    for layer in _split_top(val, ","):
        for tok in _split_ws(layer):
            tl = tok.lower()
            if tl.startswith(("url(", "image-set(", "-webkit-image-set(", "cross-fade(",
                              "element(")) or "gradient(" in tl:
                images.append(tok)
            elif tl in _BG_NONCOLOR_WORDS or re.match(r"^[-+]?[\d.]", tl):
                continue
            elif tl == "currentcolor" or _parse_color(tl, (0, 0, 0, 1)) is not None:
                color = tok
            elif "(" in tl or re.match(r"^[a-z-]+$", tl):
                color = tok  # a colour form this checker cannot read: judged unmeasured
    return [("background-color", color), ("background-image", ", ".join(images) or "none")]


_GRAD_SHAPE_WORDS = frozenset((
    "to", "in", "circle", "ellipse", "closest-side", "farthest-side",
    "closest-corner", "farthest-corner", "at", "from", "top", "left", "right",
    "bottom", "center",
))


def _parse_bg_images(val: str, current):
    """List of ('url',) / ('grad', [rgba stops]) layers, top first, and an unknown flag."""
    layers: list[tuple] = []
    unknown = False
    v = val.strip()
    if not v or v.lower() in ("none", "initial", "unset"):
        return layers, unknown
    for item in _split_top(v, ","):
        item = item.strip()
        low = item.lower()
        if low == "none" or not low:
            continue
        if "gradient(" in low:
            lo = item.find("(")
            hi = item.rfind(")")
            if lo < 0 or hi < lo:
                unknown = True
                continue
            stops = []
            for arg in _split_top(item[lo + 1:hi], ","):
                toks = _split_ws(arg)
                if not toks:
                    continue
                first = toks[0].lower()
                color = _parse_color(first, current)
                if color is None:
                    if first in _GRAD_SHAPE_WORDS or re.match(r"^[-+]?[\d.]", first):
                        continue
                    unknown = True
                    continue
                stops.append(color)
            if stops:
                layers.append(("grad", stops))
        else:
            layers.append(("url",))
    return layers, unknown


# ----- cascade --------------------------------------------------------------


class _Rule:
    __slots__ = ("sel", "label", "decls", "order", "ua", "spec")

    def __init__(self, sel, label, decls, order, ua):
        self.sel = sel
        self.label = label
        self.decls = decls
        self.order = order
        self.ua = ua
        self.spec = sel.spec


def _build_rules(items: list, w: int, h: int, ua: bool, order0: int) -> list[_Rule]:
    rules: list[_Rule] = []
    order = order0
    for sel_text, body in _flatten_css(items, w, h):
        decls = _parse_decls(body)
        if not decls:
            continue
        for part in _split_top(sel_text, ","):
            sel = _parse_selector(part)
            if not sel.ok:
                continue
            label = " ".join(part.split())
            if ua:
                label += " [browser default]"
            rules.append(_Rule(sel, label, decls, order, ua))
            order += 1
    return rules


_ROOT_CS = {
    "size": 16.0, "size_src": "browser default 16px",
    "weight": 400, "weight_src": "browser default",
    "color": (0.0, 0.0, 0.0, 1.0), "color_src": "browser default black",
    "tf": None, "tf_src": "", "customs": {}, "opacity": 1.0,
    "invisible": False, "srhide": False, "hidden": False, "bg": None,
    "lh": ("normal",), "box": {}, "unres": frozenset(),
}


_SIDES = ("top", "right", "bottom", "left")
_LOGICAL_PAD = {"padding-inline-start": "padding-left", "padding-inline-end": "padding-right",
                "padding-block-start": "padding-top", "padding-block-end": "padding-bottom"}
_BORDER_STYLE_WORDS = frozenset(("none", "hidden", "dotted", "dashed", "solid", "double", "groove",
                                 "ridge", "inset", "outset"))


def _box4(parts: list[str]):
    n = len(parts)
    if n == 1:
        return (parts[0],) * 4
    if n == 2:
        return (parts[0], parts[1], parts[0], parts[1])
    if n == 3:
        return (parts[0], parts[1], parts[2], parts[1])
    if n == 4:
        return tuple(parts)
    return None


def _expand_box(prop: str, val: str) -> list[tuple[str, str]]:
    low = val.strip().lower()
    parts = _split_ws(val)
    if prop in _LOGICAL_PAD:
        return [(_LOGICAL_PAD[prop], val)]
    if prop in ("padding", "border-width", "border-style"):
        sides = _box4(parts) if low not in ("initial", "unset", "revert") else None
        if low in ("initial", "unset", "revert"):
            sides = ("0",) * 4 if prop == "padding" else (("medium",) * 4 if prop == "border-width" else ("none",) * 4)
        if sides is None:
            sides = ("inherit",) * 4
        tail = {"padding": "padding-%s", "border-width": "border-%s-width", "border-style": "border-%s-style"}[prop]
        return [(tail % s, v) for s, v in zip(_SIDES, sides)]
    if prop in ("padding-block", "padding-inline"):
        if not 1 <= len(parts) <= 2:
            parts = ["inherit"]
        first, last = parts[0], parts[-1]
        a, b = ("top", "bottom") if prop == "padding-block" else ("left", "right")
        return [("padding-" + a, first), ("padding-" + b, last)]
    sides = list(_SIDES) if prop == "border" else [prop.split("-", 1)[1]]
    style = None
    width = None
    for tok in parts:
        tl = tok.lower()
        if tl in _BORDER_STYLE_WORDS:
            style = tl
        elif tl in ("thin", "medium", "thick") or re.match(r"^[+-]?[0-9.]", tl) or tl.startswith("calc("):
            width = tl
    if low in ("initial", "unset", "revert", "none"):
        style = "none"
    out = []
    for s in sides:
        out.append((f"border-{s}-style", style or "none"))
        out.append((f"border-{s}-width", width or "medium"))
    return out


_BOX_SHORTHANDS = frozenset((
    "padding", "padding-block", "padding-inline", "border", "border-top", "border-right",
    "border-bottom", "border-left", "border-width", "border-style",
)) | frozenset(_LOGICAL_PAD)


def _expand_decl(prop: str, val: str) -> list[tuple[str, str]]:
    if prop == "font":
        return _font_shorthand(val)
    if prop == "background":
        return _bg_shorthand(val)
    if prop in _BOX_SHORTHANDS:
        return _expand_box(prop, val)
    return [(prop, val)]


def _color_value(val: str, parent_color, own_color=None):
    """Colour value for color-like props: rgba, None (unsupported), or parent colour."""
    v = val.strip().lower()
    if v in ("inherit", "unset", "currentcolor"):
        return parent_color if own_color is None else own_color
    if v in ("initial", "revert"):
        return (0.0, 0.0, 0.0, 1.0)
    return _parse_color(v, own_color)


def _compute(node: _Node, pcs: dict, ctx: _Ctx, rules: list[_Rule]) -> dict:
    matched: list[tuple] = []
    for rule in rules:
        if _match_sel(rule.sel, node):
            for idx, (prop, val, imp) in enumerate(rule.decls):
                level = 0 if rule.ua else (2 if imp else 1)
                matched.append(((level, 0) + rule.spec + (rule.order, idx), rule.label, prop, val))
    inline = node.attrs.get("style")
    if inline:
        for idx, (prop, val, imp) in enumerate(_parse_decls(inline)):
            matched.append((((2 if imp else 1), 1, 0, 0, 0, 0, idx), "style attribute", prop, val))
    matched.sort(key=lambda m: m[0])

    customs = dict(pcs["customs"])
    for _, _, prop, val in matched:
        if prop.startswith("--"):
            customs[prop] = val
    assign: dict[str, tuple[str, str]] = {}
    dropped: set[str] = set()
    for _, label, prop, val in matched:
        if prop.startswith("--"):
            continue
        resolved = _subst_vars(val, customs)
        if resolved is None:
            dropped.add(prop)
            continue
        for longhand, value in _expand_decl(prop, resolved):
            assign[longhand] = (value, label)

    cs = dict(pcs)
    cs["customs"] = customs
    cs["hidden"] = False
    cs["box"] = assign
    cs["unres"] = frozenset(dropped)

    if "font-size" in assign:
        val, label = assign["font-size"]
        cs["size"] = _resolve_size(val, pcs["size"], ctx)
        cs["size_src"] = label if val.strip().lower() not in ("inherit", "unset") else pcs["size_src"]
    if "font-weight" in assign:
        val, label = assign["font-weight"]
        got = _resolve_weight(val, pcs["weight"])
        cs["weight"] = pcs["weight"] if got is None else got
        cs["weight_src"] = label
    if "line-height" in assign:
        low = assign["line-height"][0].strip().lower()
        if low in ("inherit", "unset"):
            pass
        elif low in ("initial", "normal", "revert"):
            cs["lh"] = ("normal",)
        else:
            try:
                cs["lh"] = ("num", float(low))
            except ValueError:
                got = _eval_len(low, cs["size"], ctx, cs["size"])
                cs["lh"] = ("px", got) if got is not None and got >= 0 else None
    if "color" in assign:
        val, label = assign["color"]
        cs["color"] = _color_value(val, pcs["color"])
        cs["color_src"] = label if val.strip().lower() not in ("inherit", "unset", "currentcolor") \
            else pcs["color_src"]
    if "-webkit-text-fill-color" in assign:
        val, label = assign["-webkit-text-fill-color"]
        low = val.strip().lower()
        if low in ("currentcolor", "initial", "unset", "revert"):
            cs["tf"], cs["tf_src"] = None, ""
        elif low != "inherit":
            got = _parse_color(low, cs["color"])
            cs["tf"], cs["tf_src"] = (got if got is not None else "unknown"), label
    if "visibility" in assign:
        low = assign["visibility"][0].strip().lower()
        if low in ("hidden", "collapse"):
            cs["invisible"] = True
        elif low in ("visible", "initial"):
            cs["invisible"] = False
    if "display" in assign and assign["display"][0].strip().lower() == "none":
        cs["hidden"] = True
    own_opacity = 1.0
    if "opacity" in assign:
        low = assign["opacity"][0].strip().lower()
        try:
            own_opacity = float(low[:-1]) / 100.0 if low.endswith("%") else float(low)
        except ValueError:
            own_opacity = 1.0
        own_opacity = min(1.0, max(0.0, own_opacity))
        if own_opacity == 0.0:
            own_opacity = 1.0  # opacity:0 is the fade-in start state, not the shipped colour
    cs["opacity"] = pcs["opacity"] * own_opacity

    hide = False
    wv = _eval_len(assign["width"][0], cs["size"], ctx, None) if "width" in assign else None
    hv = _eval_len(assign["height"][0], cs["size"], ctx, None) if "height" in assign else None
    if wv is not None and hv is not None and wv <= 1.0 and hv <= 1.0:
        hide = True
    if "clip" in assign and re.match(r"rect\(\s*0", assign["clip"][0].strip().lower()):
        hide = True
    if "clip-path" in assign and re.match(r"inset\(\s*(50|100)%", assign["clip-path"][0].strip().lower()):
        hide = True
    cs["srhide"] = hide

    cs["bg"] = None
    if "background-color" in assign or "background-image" in assign or "background-clip" in assign \
            or "-webkit-background-clip" in assign:
        bg = {"color": None, "images": [], "unknown": False, "clip_text": False, "src": ""}
        if "background-color" in assign:
            val, label = assign["background-color"]
            low = val.strip().lower()
            if low in ("initial", "unset", "inherit", "revert"):
                bg["color"] = (0.0, 0.0, 0.0, 0.0)
            else:
                got = _parse_color(low, cs["color"])
                if got is None:
                    bg["unknown"] = True
                bg["color"] = got
            bg["src"] = label
        if "background-image" in assign:
            val, label = assign["background-image"]
            images, unknown = _parse_bg_images(val, cs["color"])
            bg["images"] = images
            bg["unknown"] = bg["unknown"] or unknown
            if images or unknown:
                bg["src"] = label
        for key in ("background-clip", "-webkit-background-clip"):
            if key in assign and "text" in assign[key][0].lower():
                bg["clip_text"] = True
        cs["bg"] = bg
    return cs


def _opaque(color) -> bool:
    return color is not None and color[3] >= 0.999


def _dedupe_rgb(cands: list, cap: int = 24) -> list:
    seen: dict = {}
    for c in cands:
        seen[(round(c[0]), round(c[1]), round(c[2]))] = c
    out = list(seen.values())
    if len(out) > cap:
        out.sort(key=_luminance)
        step = len(out) / cap
        out = [out[int(k * step)] for k in range(cap)]
    return out


def _grad_samples(stops: list) -> list:
    """Stops plus the midpoint of each neighbouring pair (premultiplied)."""
    samples = list(stops)
    for a, b in zip(stops, stops[1:]):
        wa, wb = a[3], b[3]
        total = wa + wb
        alpha = total / 2
        if total <= 0:
            continue
        rgb = tuple((a[k] * wa + b[k] * wb) / total for k in range(3))
        samples.append((rgb[0], rgb[1], rgb[2], alpha))
    return samples


def _backdrop(node: _Node):
    """(candidate backdrop colours, source selector, reason). Candidates is None when unmeasurable."""
    atoms: list[tuple] = []
    src = ""
    cur = node
    done = False
    while cur is not None and cur.tag != "#doc" and not done:
        bg = cur.cs["bg"] if cur.cs else None
        if bg:
            if bg["unknown"]:
                return None, "", "unsupported background value"
            if bg["clip_text"] and cur is node:
                return None, "", "background-clip:text"
            for image in bg["images"]:
                if image[0] == "url":
                    return None, "", "background image"
                atoms.append(("grad", _grad_samples(image[1])))
                if not src:
                    src = bg["src"]
                if all(_opaque(s) for s in image[1]):
                    done = True
                    break
            if not done and bg["color"] is not None and bg["color"][3] > 0:
                atoms.append(("solid", [bg["color"]]))
                if not src:
                    src = bg["src"]
                if _opaque(bg["color"]):
                    done = True
        cur = cur.parent
    cands = [(255.0, 255.0, 255.0)]
    for _, colors in reversed(atoms):
        nxt = [_blend(c, under) for c in colors for under in cands]
        cands = _dedupe_rgb(nxt)
    return cands, src or "page canvas (white)", ""


# ----- judging --------------------------------------------------------------


def _fmt_px(value: float) -> str:
    return f"{math.floor(value * 100 + 1e-9) / 100:g}px"


def _fmt_ratio(value: float) -> str:
    return f"{math.floor(value * 100 + 1e-9) / 100:.2f}:1"


def _describe(node: _Node) -> str:
    bits = [node.tag]
    if node.attrs.get("id"):
        bits[0] += "#" + node.attrs["id"]
    if node.classes:
        bits[0] += "." + ".".join(node.classes[:3])
    return "<" + bits[0] + ">"


def _text_role(node: _Node) -> str:
    n = node
    heading = False
    while n is not None and n.tag != "#doc":
        if n.tag in _CHROME_TAGS or n.attrs.get("role", "").lower() in _CHROME_ROLES:
            return "ui"
        if n.tag in _HEADING_TAGS:
            heading = True
        n = n.parent
    if heading:
        return "heading"
    return "body"


class _TypoAcc:
    def __init__(self):
        self.fails: dict = {}
        self.unmeasured: dict = {}
        self.notes: list[str] = []
        self.texts = 0
        self.min_size: float | None = None
        self.min_ratio: float | None = None
        self.pages = 0

    def fail(self, key: tuple, rec: dict, vp: int) -> None:
        got = self.fails.get(key)
        if got is None:
            rec["count"] = 1
            rec["viewports"] = [vp]
            self.fails[key] = rec
            return
        got["count"] += 1
        if vp not in got["viewports"]:
            got["viewports"].append(vp)

    def skip(self, file: str, selector: str, reason: str, vp: int) -> None:
        key = (file, selector, reason)
        got = self.unmeasured.setdefault(
            key, {"file": file, "selector": selector, "reason": reason, "count": 0})
        got["count"] += 1


def _judge_node(node: _Node, page: str, vp: int, first_vp: bool, acc: _TypoAcc) -> None:
    text = " ".join("".join(node.texts).split())
    if not re.search(r"\w", text):
        return
    cs = node.cs
    if cs["invisible"] or cs["srhide"]:
        return
    size = cs["size"]
    if size is None:
        acc.skip(page, cs["size_src"], "unsupported font-size value", vp)
        return
    if size <= 0:
        return
    if first_vp:
        acc.texts += 1
    acc.min_size = size if acc.min_size is None else min(acc.min_size, size)
    role = _text_role(node)
    floor = BODY_FLOOR_PX if role == "body" else TYPE_FLOOR_PX
    shown = text if len(text) <= 36 else text[:33] + "..."
    if size < floor - 0.005:
        measured = _fmt_px(size)
        required = _fmt_px(floor)
        acc.fail(
            ("type_floor", page, cs["size_src"], measured, required, role),
            {"check": "type_floor", "file": page, "selector": cs["size_src"],
             "property": "font-size", "measured": measured, "required": required,
             "role": role, "element": _describe(node), "text": shown,
             "extra": f"{role} text"},
            vp,
        )

    fg = cs["tf"] if cs["tf"] is not None else cs["color"]
    fg_src = cs["tf_src"] if cs["tf"] is not None else cs["color_src"]
    if fg is None or fg == "unknown":
        acc.skip(page, fg_src, "unsupported colour value", vp)
        return
    alpha = fg[3] * cs["opacity"]
    if alpha <= 0.001:
        acc.skip(page, fg_src, "transparent text", vp)
        return
    cands, bg_src, reason = _backdrop(node)
    if cands is None:
        acc.skip(page, fg_src, reason, vp)
        return
    worst = None
    for cand in cands:
        rgb = _blend((fg[0], fg[1], fg[2], alpha), cand)
        ratio = contrast_ratio(rgb, cand)
        if worst is None or ratio < worst[0]:
            worst = (ratio, rgb, cand)
    ratio, rgb, cand = worst
    acc.min_ratio = ratio if acc.min_ratio is None else min(acc.min_ratio, ratio)
    large = size >= LARGE_PX - 0.005 or (size >= LARGE_BOLD_PX - 0.005 and cs["weight"] >= BOLD_WEIGHT)
    need = CONTRAST_LARGE if large else CONTRAST_BODY
    if ratio < need:
        measured = _fmt_ratio(ratio)
        required = f"{need:g}:1"
        kind = "large" if large else "normal"
        acc.fail(
            ("contrast", page, fg_src, measured, required, _hex(rgb), _hex(cand)),
            {"check": "contrast", "file": page, "selector": fg_src,
             "property": "color", "measured": measured, "required": required,
             "role": kind, "element": _describe(node), "text": shown,
             "extra": f"{_hex(rgb)} on {_hex(cand)} (background from {bg_src}); "
                      f"{kind} text {_fmt_px(size)} weight {cs['weight']}",
             "bg_selector": bg_src},
            vp,
        )


def _stylesheet_items(root: _Node, page: Path, acc: _TypoAcc) -> list:
    items: list = []
    for node in _iter_nodes(root):
        if node.tag == "style":
            parsed = _parse_css_items(_strip_css_comments("".join(node.raw)))
            media = node.attrs.get("media", "").strip()
            items.extend([("at", "media", media, parsed)] if media else parsed)
        elif node.tag == "link" and "stylesheet" in node.attrs.get("rel", "").lower().split():
            href = node.attrs.get("href", "").strip()
            lower = href.lower()
            local = href.split("#", 1)[0].split("?", 1)[0]
            if not href or lower.startswith(("http:", "https:", "//", "data:")) or ":" in local.split("/", 1)[0]:
                acc.notes.append(f"{page.name}: stylesheet not read (remote): {href or '<empty>'}")
                continue
            target = page.parent / unquote(local).lstrip("/")
            try:
                css = target.read_text(encoding="utf-8", errors="replace")
            except OSError:
                acc.notes.append(f"{page.name}: stylesheet not found: {href}")
                continue
            parsed = _parse_css_items(_strip_css_comments(css))
            media = node.attrs.get("media", "").strip()
            items.extend([("at", "media", media, parsed)] if media else parsed)
    return items


def _analyze_page(page: Path, acc: _TypoAcc, viewports: tuple | None = None) -> None:
    html = page.read_text(encoding="utf-8", errors="replace")
    root = _build_dom(html)
    author_items = _stylesheet_items(root, page, acc)
    ua_items = _parse_css_items(_UA_CSS)
    acc.pages += 1
    for number, (w, h) in enumerate(viewports or TYPO_VIEWPORTS):
        ctx = _Ctx(w, h)
        rules = _build_rules(ua_items, w, h, True, 0) + _build_rules(author_items, w, h, False, 10000)
        stack = [(root, _ROOT_CS)]
        while stack:
            node, pcs = stack.pop()
            if node.tag == "#doc":
                cs = pcs
            else:
                cs = _compute(node, pcs, ctx, rules)
                node.cs = cs
                if node.tag == "html" and cs["size"]:
                    ctx.root = cs["size"]
                if cs["hidden"] or node.tag in _SKIP_TAGS:
                    continue
                _judge_node(node, page.name, w, number == 0, acc)
            for child in reversed(node.children):
                stack.append((child, cs))


def typography_scan(pages: list[Path], viewports: tuple | None = None) -> dict:
    """Run the type-floor and contrast judgement over HTML pages (default: TYPO_VIEWPORTS)."""
    acc = _TypoAcc()
    for page in pages:
        _analyze_page(page, acc, viewports)
    order = sorted(acc.fails.values(), key=lambda r: (r["file"], r["check"], r["selector"], r["measured"]))
    for rec in order:
        rec["viewports"] = sorted(rec["viewports"])
    return {
        "type_floor": [r for r in order if r["check"] == "type_floor"],
        "contrast": [r for r in order if r["check"] == "contrast"],
        "unmeasured": sorted(acc.unmeasured.values(), key=lambda r: (r["file"], r["selector"], r["reason"])),
        "notes": acc.notes,
        "texts": acc.texts,
        "pages": acc.pages,
        "min_size": acc.min_size,
        "min_ratio": acc.min_ratio,
    }


def failure_line(f: dict, warn: bool = False) -> str:
    """One line per failure: file | selector | measured (needs required) | where."""
    if f["check"] == "tap_target":
        return _tap_line(f, warn)
    if f["check"] in ("sideways_scroll", "mobile_nav_drawer", "mobile_visibility", "mobile_spec"):
        return _mob_line(f, warn)
    if f["check"] in ("slug_shape", "photo_luma", "svg_photo"):
        return f"{f['file']} | {f['selector']} | {f['measured']} (needs {f['required']}) | {f['extra']}"
    if f["check"] == "reproducible":
        what = f["kind"] + (f" at {f['where']}" if f.get("where") else "")
        return f"{f['file']} | {what} | build1={f['first']} build2={f['second']}"
    views = ",".join(str(v) for v in f.get("viewports", [])) + "px"
    label = "font-size" if f["check"] == "type_floor" else "contrast"
    parts = [
        f["file"], f["selector"], f"{label} {f['measured']} (needs >= {f['required']})",
        f"{f.get('extra', '')}; {f['element']} \"{f['text']}\"", f"x{f['count']} at {views}",
    ]
    return " | ".join(parts)


def _short_failure(f: dict) -> str:
    label = "font-size" if f["check"] == "type_floor" else "contrast"
    return f"{f['file']}: {f['selector']} {label} {f['measured']} (needs >= {f['required']})"


def _typography_rows(rep: "Report", pages: list[Path], viewports: tuple | None = None) -> None:
    try:
        scan = typography_scan(pages, viewports)
    except Exception as exc:  # fail closed: a checker bug must not read as a pass
        for name in ("type_floor", "contrast"):
            rep.add(name, "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
        return
    views = "+".join(str(w) for w, _ in (viewports or TYPO_VIEWPORTS)) + "px"
    skipped = scan["unmeasured"]
    skip_note = ""
    if skipped:
        total = sum(s["count"] for s in skipped)
        sample = "; ".join(f"{s['file']}: {s['selector']} ({s['reason']})" for s in skipped[:3])
        skip_note = f"; {total} text element(s) not measurable: {sample}"
        if len(skipped) > 3:
            skip_note += f" (+{len(skipped) - 3} more)"
    for name, key in (("type_floor", "type_floor"), ("contrast", "contrast")):
        fails = scan[key]
        if fails:
            shown = "; ".join(_short_failure(f) for f in fails[:6])
            extra = f" (+{len(fails) - 6} more)" if len(fails) > 6 else ""
            rep.add(name, "FAIL", shown + extra, failures=fails)
            continue
        if name == "type_floor":
            low = scan["min_size"]
            detail = (f"{scan['texts']} text element(s), {scan['pages']} page(s) at {views}; "
                      f"smallest {_fmt_px(low) if low else 'n/a'}; floor {_fmt_px(TYPE_FLOOR_PX)}, "
                      f"body {_fmt_px(BODY_FLOOR_PX)}")
        else:
            low = scan["min_ratio"]
            detail = (f"{scan['texts']} text element(s), {scan['pages']} page(s) at {views}; "
                      f"lowest {_fmt_ratio(low) if low else 'n/a'}; needs {CONTRAST_BODY:g}:1, "
                      f"large {CONTRAST_LARGE:g}:1")
        detail += skip_note if name == "contrast" else ""
        if name == "contrast" and (skipped or scan["notes"]):
            if scan["notes"]:
                detail += "; " + "; ".join(scan["notes"][:3])
            rep.add(name, "WARN", detail, failures=[])
        else:
            rep.add(name, "PASS", detail, failures=[])


# ---------------------------------------------------------------------------
# Tap targets, STATIC (row tap_target). Same cascade as type_floor/contrast,
# judged at one viewport (360px). Every interactive element (a[href], button,
# input, select, textarea, [role=button], summary) gets a width and a height as
# an interval (low, high) in px from height/min-height/width/min-width/padding/
# border/line-height/font-size/display. FAIL only when the HIGH bound of an axis
# is under 44px (it cannot reach the floor). PASS only when the LOW bound of
# both axes reaches 44px. Anything between is WARN, "not measurable", never a
# pass. Exempt: an inline text link inside a running sentence (WCAG 2.5.8
# inline exception) and disabled controls. Controls inside display:none
# containers (closed menus) are measured as if shown; a miss there is a WARN.
# Not measured: rendered layout, container widths (block-level and grown flex
# items are assumed to fill their container), web fonts, ::before/::after.
# ---------------------------------------------------------------------------
TAP_MIN_PX = 44.0
TAP_VIEWPORT = MOBILE_VIEWPORTS[0]   # narrowest phone width (360px)
TAP_VIEWPORTS = MOBILE_VIEWPORTS     # tap_target is judged at 360, 390 and 412px
_INF = float("inf")
_TAP_LH_NORMAL = (1.0, 1.6)        # line-height: normal, multiple of font-size
_TAP_GLYPH = (0.35, 0.80)          # glyph advance range, multiple of font-size
_TAP_CONTENT_AREA = (1.0, 1.5)     # inline box content area, multiple of font-size
_TAP_ONE_LINE_PX = 200.0           # label estimated narrower than this is one line
_TAP_INLINE_TAGS = frozenset((
    "a", "span", "b", "i", "em", "strong", "small", "label", "code", "abbr", "mark",
    "sub", "sup", "cite", "q", "u", "s", "kbd", "img", "svg", "time", "bdi", "bdo",
))
_TAP_BLOCK_KIDS = frozenset((
    "div", "p", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6", "section",
    "article", "nav", "header", "footer", "table", "form", "figure", "aside",
    "main", "dl", "dt", "dd", "blockquote", "details", "fieldset", "pre",
))
_TAP_UNHANDLED = frozenset((
    "inline-size", "block-size", "min-inline-size", "min-block-size", "max-inline-size",
    "max-block-size", "aspect-ratio", "zoom", "place-items", "place-self", "grid-area",
))
_TAP_BOX_FAMILY = ("padding", "border", "min-", "max-", "width", "height", "line-height",
                   "font", "display", "box-sizing", "flex")
_TAP_TEXT_INPUTS = frozenset(("text", "email", "search", "tel", "url", "password", "number",
                              "date", "datetime-local", "month", "time", "week", "file", ""))
_TAP_BTN_INPUTS = frozenset(("submit", "button", "reset"))


def _tap_kind(node: _Node):
    tag, at = node.tag, node.attrs
    role = at.get("role", "").strip().lower()
    if tag in ("button", "input", "select", "textarea") and "disabled" in at:
        return None
    if tag == "input":
        return None if at.get("type", "text").strip().lower() == "hidden" else "input"
    if tag in ("select", "textarea"):
        return "input"
    if tag == "button" or role == "button":
        return "button"
    if role in ("link", "tab", "menuitem"):
        return role
    if tag == "summary":
        return "summary"
    if tag == "a" and "href" in at:
        return "link"
    return None


def _tap_box(node: _Node) -> dict:
    return (node.cs or {}).get("box", {}) if node is not None else {}


def _tap_boxval(node: _Node, prop: str) -> str | None:
    got = _tap_box(node).get(prop)
    return None if got is None else " ".join(got[0].strip().lower().split())


def _tap_raw_display(node: _Node) -> str:
    d = _tap_boxval(node, "display")
    if d is not None:
        d = {"inline flex": "inline-flex", "inline grid": "inline-grid", "inline flow-root": "inline-block",
             "block flex": "flex", "block grid": "grid", "block flow-root": "flow-root",
             "inline flow": "inline", "block flow": "block"}.get(d, d)
        if d == "none":
            return "none"
        if d in ("initial", "revert"):
            return "inline"
        if d in ("inherit", "unset") and node.parent is not None and node.parent.tag != "#doc":
            return _tap_raw_display(node.parent)
        return d
    if node.tag in ("button", "input", "select", "textarea"):
        return "inline-block"
    return "inline" if node.tag in _TAP_INLINE_TAGS else "block"


def _tap_val(node: _Node, prop: str, size, ctx):
    """None when unset or auto, a float in px, '%' for a percentage, '?' when unresolvable."""
    v = _tap_boxval(node, prop)
    if v is None or v in ("auto", "none", "normal", "initial", "unset", "revert"):
        return None
    if v in ("fit-content", "max-content", "min-content", "stretch", "-webkit-fill-available"):
        return v
    if v == "inherit":
        return "?"
    if re.fullmatch(r"[0-9.]+%", v):
        return "%"
    got = _eval_len(v, size, ctx, None)
    return "?" if got is None else got


def _tap_iv(v):
    """Side value to an interval."""
    if v is None:
        return (0.0, 0.0)
    if v in ("?", "%") or isinstance(v, str):
        return (0.0, _INF)
    return (max(v, 0.0), max(v, 0.0))


def _tap_border(node: _Node, side: str, size, ctx):
    style = _tap_boxval(node, f"border-{side}-style") or "none"
    if style in ("none", "hidden"):
        return (0.0, 0.0)
    w = _tap_boxval(node, f"border-{side}-width") or "medium"
    w = {"thin": "1px", "medium": "3px", "thick": "5px"}.get(w, w)
    got = _eval_len(w, size, ctx, None)
    return (0.0, _INF) if got is None or got < 0 else (got, got)


def _tap_text(node: _Node) -> str:
    parts: list[str] = []
    stack = [node]
    while stack:
        n = stack.pop()
        if n is not node:
            cs = n.cs
            if cs is None or cs.get("hidden") or cs.get("srhide") or cs.get("invisible"):
                continue
        parts.append(" ".join(n.texts))
        stack.extend(reversed(n.children))
    return " ".join(" ".join(parts).split())


def _tap_label(node: _Node) -> str:
    text = _tap_text(node)
    if not text:
        at = node.attrs
        text = at.get("aria-label") or at.get("title") or at.get("value") or at.get("placeholder") \
            or at.get("name") or at.get("type") or ""
        text = " ".join(text.split())
    return text if len(text) <= 36 else text[:33] + "..."


def _tap_num_attr(value):
    m = re.fullmatch(r"\s*([0-9.]+)(px)?\s*", value or "")
    return float(m.group(1)) if m else None


def _tap_replaced(node: _Node):
    """Sizes of visible img/svg inside the control: list of (w, h), or None if any is unknown."""
    out = []
    stack = list(node.children)
    while stack:
        n = stack.pop()
        if n.cs is None or n.cs.get("hidden"):
            continue
        if n.tag in ("img", "svg"):
            ctx = _Ctx(*TAP_VIEWPORT)
            w = _tap_num_attr(n.attrs.get("width"))
            h = _tap_num_attr(n.attrs.get("height"))
            size = n.cs.get("size")
            cw, ch = _tap_val(n, "width", size, ctx), _tap_val(n, "height", size, ctx)
            w = cw if isinstance(cw, float) else w
            h = ch if isinstance(ch, float) else h
            if w is None or h is None:
                return None
            out.append((w, h))
            continue
        stack.extend(n.children)
    return out


def _tap_has_block_kids(node: _Node) -> bool:
    stack = list(node.children)
    while stack:
        n = stack.pop()
        if n.cs is None or n.cs.get("hidden"):
            continue
        if n.tag in _TAP_BLOCK_KIDS or _tap_raw_display(n) in ("block", "flex", "grid", "list-item", "table"):
            return True
        stack.extend(n.children)
    return False


def _tap_exempt_inline(node: _Node, final_display: str) -> bool:
    """WCAG 2.5.8 inline exception: a text link inside a sentence."""
    if node.tag != "a" or final_display != "inline":
        return False
    p = node.parent
    while p is not None and p.tag != "#doc" and p.cs is not None and _tap_raw_display(p) == "inline" \
            and p.tag not in ("button", "summary"):
        p = p.parent
    if p is None or p.tag == "#doc":
        return False
    words = 0
    stack = [p]
    while stack:
        n = stack.pop()
        if n is node:
            continue
        words += len(re.findall(r"[A-Za-z\u00c0-\u024f]{2,}", " ".join(n.texts)))
        for c in n.children:
            if c.cs is not None and not c.cs.get("hidden") and _tap_raw_display(c) == "inline" and c is not node:
                stack.append(c)
    return words >= 2


def _tap_grows(node: _Node) -> bool:
    flex = _tap_boxval(node, "flex")
    if flex:
        first = flex.split()[0]
        if first == "auto":
            return True
        try:
            return float(first) > 0
        except ValueError:
            return False
    grow = _tap_boxval(node, "flex-grow")
    try:
        return grow is not None and float(grow) > 0
    except ValueError:
        return False


def _tap_measure(node: _Node, ctx: _Ctx):
    """Returns dict(w, h, notes, labels_w, labels_h, assumed) or dict(error=reason)."""
    cs = node.cs
    box = cs.get("box", {})
    size = cs["size"]
    if size is None:
        return {"error": "font-size not resolvable"}
    bad = [p for p in cs.get("unres", ()) if p.startswith(_TAP_BOX_FAMILY)]
    if bad:
        return {"error": "unresolved var() in " + ", ".join(sorted(bad))}
    for p, (v, lab) in box.items():
        if p in _TAP_UNHANDLED or (p == "transform" and "scale" in v.lower()):
            return {"error": f"{p} is not modelled statically ({lab})"}
    notes: list[str] = []
    lab_w: list[str] = []
    lab_h: list[str] = []

    def lab(into, *props):
        for p in props:
            if p in box and box[p][1] not in into:
                into.append(box[p][1])

    tag = node.tag
    raw = _tap_raw_display(node)
    parent = node.parent if node.parent is not None and node.parent.tag != "#doc" else None
    praw = _tap_raw_display(parent) if parent is not None else ""
    if praw == "none":
        praw = "block"
    flex_item = praw in ("flex", "inline-flex")
    grid_item = praw in ("grid", "inline-grid")
    pos = _tap_boxval(node, "position") or "static"
    flt = _tap_boxval(node, "float") or "none"
    out_of_flow = pos in ("absolute", "fixed") or flt not in ("none", "")
    disp = raw
    if flex_item or grid_item or out_of_flow:
        disp = {"inline": "block", "inline-block": "block", "inline-flex": "flex",
                "inline-grid": "grid", "inline-table": "table"}.get(raw, raw)
    if disp == "none":
        disp = "block"
    if disp == "contents":
        return {"error": "display:contents has no box"}

    # box-sizing, padding, border
    bs = _tap_boxval(node, "box-sizing")
    border_box = (bs == "border-box") if bs else (tag in ("button", "select") or (
        tag == "input" and node.attrs.get("type", "text").lower() in _TAP_BTN_INPUTS | {"image"}))
    pad_t, pad_r, pad_b, pad_l = (_tap_iv(_tap_val(node, f"padding-{s}", size, ctx))
                                  for s in ("top", "right", "bottom", "left"))
    bor_t, bor_r, bor_b, bor_l = (_tap_border(node, s, size, ctx) for s in ("top", "right", "bottom", "left"))
    lab(lab_h, "padding-top", "padding-bottom")
    lab(lab_w, "padding-left", "padding-right")
    pv = (pad_t[0] + pad_b[0] + bor_t[0] + bor_b[0], pad_t[1] + pad_b[1] + bor_t[1] + bor_b[1])
    ph = (pad_l[0] + pad_r[0] + bor_l[0] + bor_r[0], pad_l[1] + pad_r[1] + bor_l[1] + bor_r[1])

    # line height
    lh = cs.get("lh")
    if lh is None:
        lh_iv = (size * 1.0, _INF)
    elif lh[0] == "num":
        lh_iv = (lh[1] * size, lh[1] * size)
    elif lh[0] == "px":
        lh_iv = (lh[1], lh[1])
    else:
        lh_iv = (size * _TAP_LH_NORMAL[0], size * _TAP_LH_NORMAL[1])
    lab(lab_h, "line-height", "font", "font-size")
    if "font-size" not in box and cs.get("size_src") and not lab_h:
        pass

    # content: text and replaced children
    kind_input = tag in ("input", "select", "textarea")
    itype = node.attrs.get("type", "text").strip().lower() if tag == "input" else ""
    text = _tap_text(node)
    if tag == "input" and itype in _TAP_BTN_INPUTS:
        text = node.attrs.get("value") or {"submit": "Submit", "reset": "Reset"}.get(itype, "Button")
    nowrap = (_tap_boxval(node, "white-space") or "") in ("nowrap", "pre")
    chars = len(text)
    words = text.split()
    longest = max((len(x) for x in words), default=0)
    block_kids = _tap_has_block_kids(node)
    repl = _tap_replaced(node)
    spacing = _tap_val(node, "letter-spacing", size, ctx)
    ls = spacing if isinstance(spacing, float) and spacing > 0 else 0.0
    text_w = (longest * size * _TAP_GLYPH[0] + ls * longest, chars * size * _TAP_GLYPH[1] + ls * chars)
    if nowrap:
        text_w = (chars * size * _TAP_GLYPH[0] + ls * chars, text_w[1])
    one_line = nowrap or (not block_kids and chars * size * 0.55 <= _TAP_ONE_LINE_PX)
    if chars:
        lines = (1, 1 if one_line else _INF)
        content_h = (lines[0] * lh_iv[0], lines[1] * lh_iv[1] if lines[1] != _INF or lh_iv[1] != _INF else _INF)
        if lines[1] == _INF or lh_iv[1] == _INF:
            content_h = (lines[0] * lh_iv[0], _INF)
        content_w = text_w
    else:
        content_h = (0.0, _INF)
        content_w = (0.0, _INF)
    if repl:
        rh = (max(h for _, h in repl), max(h for _, h in repl))
        rw = (sum(w for w, _ in repl), sum(w for w, _ in repl))
        if chars:
            content_h = (max(content_h[0], rh[0]), content_h[1] if content_h[1] == _INF else max(content_h[1], rh[1]))
            content_w = (content_w[0] + rw[0], content_w[1] + rw[1])
        else:
            content_h, content_w = rh, rw
    elif repl is None and chars:
        content_h = (content_h[0], _INF)
        content_w = (content_w[0], _INF)
    elif repl is None:
        pass
    if kind_input and not chars:
        content_h = (size * _TAP_LH_NORMAL[0], size * _TAP_LH_NORMAL[1]) if tag != "textarea" else (size * 2.0, _INF)
        if tag == "textarea":
            content_w = (100.0, _INF)
        elif tag == "select":
            content_w = (40.0, _INF)
        elif itype in ("checkbox", "radio"):
            content_w, content_h = (13.0, 13.0), (13.0, 13.0)
        else:
            content_w = (100.0, _INF)

    # ---- height
    assumed = []
    if disp == "inline" and not kind_input:
        h = (size * _TAP_CONTENT_AREA[0] + pv[0], size * _TAP_CONTENT_AREA[1] + pv[1])
        notes.append("display:inline, height/min-height ignored; hit area = text content area + padding")
    else:
        hv = _tap_val(node, "height", size, ctx)
        if isinstance(hv, float):
            lab(lab_h, "height")
            h = (max(hv, pv[0]), max(hv, pv[1])) if border_box else (hv + pv[0], hv + pv[1])
        elif hv is None or hv in ("fit-content", "max-content", "min-content"):
            h = (content_h[0] + pv[0], content_h[1] + pv[1])
        else:
            h = (0.0, _INF)
            lab(lab_h, "height")
        mh = _tap_val(node, "min-height", size, ctx)
        if isinstance(mh, float):
            lab(lab_h, "min-height")
            m = mh if border_box else mh + pv[0]
            m_hi = mh if border_box else mh + pv[1]
            h = (max(h[0], m), max(h[1], m_hi))
        elif mh in ("?", "%"):
            h = (h[0], _INF)
            lab(lab_h, "min-height")
        xh = _tap_val(node, "max-height", size, ctx)
        if isinstance(xh, float):
            lab(lab_h, "max-height")
            cap = xh if border_box else xh + pv[0]
            cap_hi = xh if border_box else xh + pv[1]
            h = (min(h[0], cap), min(h[1], cap_hi))
        elif xh in ("?", "%"):
            h = (0.0, h[1])
    # stretch in a flex row or grid cell, growth in a flex column, two-sided insets
    stretch = False
    if (flex_item or grid_item) and not isinstance(_tap_val(node, "height", size, ctx), float):
        pdir = (_tap_boxval(parent, "flex-direction") or "row") if flex_item else "row"
        if flex_item and pdir.startswith("column"):
            stretch = _tap_grows(node)
        else:
            ai = _tap_boxval(parent, "align-items") or "normal"
            self_ = _tap_boxval(node, "align-self") or "auto"
            eff = ai if self_ in ("auto", "normal") else self_
            stretch = eff in ("normal", "stretch")
            if stretch:
                notes.append("stretches to its flex/grid line")
    if pos in ("absolute", "fixed") and (("inset" in box) or ("top" in box and "bottom" in box)) \
            and not isinstance(_tap_val(node, "height", size, ctx), float):
        stretch = True
    if stretch:
        h = (h[0], _INF)

    # ---- width
    wv = _tap_val(node, "width", size, ctx)
    inline_like = disp in ("inline", "inline-block", "inline-flex", "inline-grid", "inline-table")
    mode = "content"
    if isinstance(wv, float) and disp != "inline":
        lab(lab_w, "width")
        w = (max(wv, ph[0]), max(wv, ph[1])) if border_box else (wv + ph[0], wv + ph[1])
        mode = "fixed"
    elif wv == "%" and disp != "inline":
        lab(lab_w, "width")
        mode = "fill"
    elif wv in ("fit-content", "max-content", "min-content"):
        mode = "content"
    elif disp == "inline" or (inline_like and not (flex_item or grid_item)) or out_of_flow:
        mode = "content"
    elif flex_item:
        pdir = _tap_boxval(parent, "flex-direction") or "row"
        if pdir.startswith("column"):
            ai = _tap_boxval(parent, "align-items") or "stretch"
            mode = "fill" if ai in ("stretch", "normal") else "content"
        else:
            mode = "fill" if _tap_grows(node) else "content"
    else:
        mode = "fill"
    if pos in ("absolute", "fixed") and ("inset" in box or ("left" in box and "right" in box)) and mode == "content":
        mode = "fill"
    if mode == "content":
        w = (content_w[0] + ph[0], min(content_w[1] + ph[1], ctx.w if not nowrap else _INF))
        if content_w[1] == _INF:
            w = (content_w[0] + ph[0], _INF)
        lab(lab_w, "font-size", "font")
    elif mode == "fill":
        w = (TAP_MIN_PX, ctx.w)
        assumed.append("width assumed to fill its container")
    mw = _tap_val(node, "min-width", size, ctx)
    if isinstance(mw, float):
        lab(lab_w, "min-width")
        a, b = (mw, mw) if border_box else (mw + ph[0], mw + ph[1])
        w = (max(w[0], a), max(w[1], b))
    elif mw in ("?", "%"):
        w = (w[0], _INF)
        lab(lab_w, "min-width")
    xw = _tap_val(node, "max-width", size, ctx)
    if isinstance(xw, float):
        lab(lab_w, "max-width")
        a, b = (xw, xw) if border_box else (xw + ph[0], xw + ph[1])
        w = (min(w[0], a), min(w[1], b))
    elif xw in ("?", "%"):
        w = (0.0, w[1]) if xw == "?" else w
    if mode == "content" and flex_item and _tap_grows(node):
        w = (w[0], ctx.w)
    if mode == "content" and flex_item and not nowrap and False:
        pass
    if flex_item and (_tap_boxval(node, "min-width") == "0" or (_tap_boxval(node, "overflow") or "visible") not in ("visible", "")) \
            and (_tap_boxval(node, "flex-shrink") != "0") and mode == "content":
        w = (0.0, w[1])
        notes.append("flex item may shrink below its content")
    if node.tag == "input" and itype in ("checkbox", "radio") and wv is None and _tap_val(node, "height", size, ctx) is None:
        return {"error": "native checkbox/radio: size is set by the browser, hit area includes its label (check rendered)"}
    return {"w": w, "h": h, "notes": notes, "labels_w": lab_w, "labels_h": lab_h, "assumed": assumed}


def _tap_pseudo_selectors(author_items: list, w: int, h: int) -> list:
    out = []
    for sel_text, body in _flatten_css(author_items, w, h):
        if not re.search(r"position\s*:\s*(absolute|fixed)", body, re.I):
            continue
        if not re.search(r"(?:inset|top|bottom|left|right)\s*:\s*-", body, re.I):
            continue
        for part in _split_top(sel_text, ","):
            base = re.sub(r"::?(?:before|after)\s*$", "", part.strip(), flags=re.I)
            if base != part.strip():
                sel = _parse_selector(base)
                if sel.ok:
                    out.append(sel)
    return out


def _tap_fmt(iv) -> str:
    lo, hi = iv
    if hi == _INF:
        return f">={_fmt_px(lo)[:-2]}"
    if abs(hi - lo) < 0.005:
        return _fmt_px(lo)[:-2]
    return f"{_fmt_px(lo)[:-2]}-{_fmt_px(hi)[:-2]}"


class _TapAcc:
    def __init__(self):
        self.fails: dict = {}
        self.warns: dict = {}
        self.pages = 0
        self.checked = 0
        self.exempt = 0
        self.hidden_ok = 0
        self.hidden_skipped = 0
        self.notes: list[str] = []
        self.min_w: float | None = None
        self.min_h: float | None = None
        self.nodes: dict = {}   # (store, page, node) -> record key: one record per element across widths

    def add(self, store: dict, key: tuple, rec: dict) -> None:
        got = store.get(key)
        if got is None:
            rec["count"] = 1
            store[key] = rec
        else:
            got["count"] += 1


def _tap_selector(m: dict, node: _Node, axes: str) -> str:
    labs = []
    for axis in axes:
        for item in m["labels_w" if axis == "w" else "labels_h"]:
            if item not in labs:
                labs.append(item)
    author = [x for x in labs if not x.endswith("[browser default]")]
    labs = author or labs
    if not labs:
        labs = [f"{node.tag} [no size rule: browser default]"]
    return " + ".join(labs[:3])


def _tap_judge(node: _Node, page: str, hidden_by, ctx: _Ctx, pseudo: list, acc: _TapAcc,
               first: bool = True) -> None:
    cs = node.cs
    if cs["invisible"] or cs["srhide"]:
        return
    kind = _tap_kind(node)
    desc = _describe(node)
    shown = _tap_label(node)
    if cs["hidden"]:
        if first:
            acc.hidden_skipped += 1
        return
    raw = _tap_raw_display(node)
    parent = node.parent if node.parent is not None and node.parent.tag != "#doc" else None
    praw = _tap_raw_display(parent) if parent is not None else ""
    blockified = praw in ("flex", "inline-flex", "grid", "inline-grid") or \
        (_tap_boxval(node, "position") or "") in ("absolute", "fixed") or \
        (_tap_boxval(node, "float") or "none") != "none"
    final = {"inline": "block", "inline-block": "block"}.get(raw, raw) if blockified else raw
    if _tap_exempt_inline(node, final):
        if first:
            acc.exempt += 1
        return
    vp = int(ctx.w)

    def record(store, selector, measured, extra):
        nk = (id(store), page, id(node))
        key = acc.nodes.get(nk)
        if key is not None and key in store:  # same element, another phone width
            got = store[key]
            if vp not in got["viewports"]:
                got["viewports"].append(vp)
            if got["measured"] != measured:
                got.setdefault("measured_at", {})[vp] = measured
            return
        rec = {"check": "tap_target", "file": page, "selector": selector, "measured": measured,
               "required": "44px", "element": desc, "text": shown, "extra": extra,
               "kind": kind, "viewports": [vp]}
        key = (page, selector, measured, desc, extra)
        acc.nodes[nk] = key
        got = store.get(key)
        if got is not None and vp not in got["viewports"]:
            got["viewports"].append(vp)
        acc.add(store, key, rec)

    if any(sel_match for sel_match in (_match_sel(s, node) for s in pseudo)):
        record(acc.warns, f"{node.tag} (::before/::after enlarges the target)", "not measurable",
               "a pseudo-element with negative offsets may extend the tap area")
        return
    m = _tap_measure(node, ctx)
    if "error" in m:
        record(acc.warns, f"{node.tag}", "not measurable", m["error"])
        return
    (wl, wh), (hl, hh) = m["w"], m["h"]
    floor = TAP_MIN_PX - 0.005
    wtxt = "[fill]" if m["assumed"] and (wl, wh) == (TAP_MIN_PX, ctx.w) else _tap_fmt(m["w"])
    measured = f"{wtxt}x{_tap_fmt(m['h'])}px"
    where = f" (hidden at {vp}px, measured as if shown: " + hidden_by + ")" if hidden_by else ""
    if wh < floor or hh < floor:
        axes = "".join(a for a, hi in (("w", wh), ("h", hh)) if hi < floor)
        sel = _tap_selector(m, node, axes)
        extra = ("; ".join(m["notes"]) if m["notes"] else "") or "resolved box"
        if hidden_by:
            record(acc.warns, sel, measured, "under 44px" + where)
        else:
            record(acc.fails, sel, measured, extra)
        return
    if wl >= floor and hl >= floor:
        if first:
            acc.checked += 1
            acc.min_w = wl if acc.min_w is None else min(acc.min_w, wl)
            acc.min_h = hl if acc.min_h is None else min(acc.min_h, hl)
            if hidden_by:
                acc.hidden_ok += 1
        return
    axes = "".join(a for a, lo in (("w", wl), ("h", hl)) if lo < floor)
    sel = _tap_selector(m, node, axes)
    why = []
    if hl < floor:
        why.append("height is " + _tap_fmt(m["h"]) + "px, no guaranteed 44px minimum")
    if wl < floor:
        why.append("width is " + _tap_fmt(m["w"]) + "px, no guaranteed 44px minimum")
    record(acc.warns, sel, measured, "; ".join(why) + where)


def _tap_scan_page(page: Path, acc: _TapAcc, viewports: tuple | None = None) -> None:
    html = page.read_text(encoding="utf-8", errors="replace")
    root = _build_dom(html)
    sheet_acc = _TypoAcc()
    author_items = _stylesheet_items(root, page, sheet_acc)
    acc.notes.extend(sheet_acc.notes)
    acc.pages += 1
    for number, (w, h) in enumerate(viewports or TAP_VIEWPORTS):
        ctx = _Ctx(w, h)
        rules = _build_rules(_parse_css_items(_UA_CSS), w, h, True, 0) + \
            _build_rules(author_items, w, h, False, 10000)
        pseudo = _tap_pseudo_selectors(author_items, w, h)
        targets = []
        stack = [(root, _ROOT_CS, None)]
        while stack:
            node, pcs, hid = stack.pop()
            if node.tag == "#doc":
                cs = pcs
            else:
                cs = _compute(node, pcs, ctx, rules)
                node.cs = cs
                if node.tag == "html" and cs["size"]:
                    ctx.root = cs["size"]
                if cs["hidden"] and hid is None:
                    hid = _tap_box(node).get("display", ("", "display:none"))[1]
                if _tap_kind(node):
                    targets.append((node, hid))
                if node.tag in _SKIP_TAGS:
                    continue
            for child in reversed(node.children):
                stack.append((child, cs, hid))
        for node, hid in targets:
            if node.cs["hidden"]:
                if number == 0:
                    acc.hidden_skipped += 1
                continue
            _tap_judge(node, page.name, hid, ctx, pseudo, acc, number == 0)


def tap_scan(pages: list[Path], viewports: tuple | None = None) -> dict:
    acc = _TapAcc()
    for page in pages:
        _tap_scan_page(page, acc, viewports)
    key = lambda r: (r["file"], r["selector"], r["measured"], r["element"])
    for rec in list(acc.fails.values()) + list(acc.warns.values()):
        rec["viewports"].sort()
    return {
        "fails": sorted(acc.fails.values(), key=key),
        "warns": sorted(acc.warns.values(), key=key),
        "pages": acc.pages, "checked": acc.checked, "exempt": acc.exempt,
        "hidden_ok": acc.hidden_ok, "hidden_skipped": acc.hidden_skipped,
        "notes": acc.notes, "min_w": acc.min_w, "min_h": acc.min_h,
    }


def _tap_line(f: dict, warn: bool = False) -> str:
    """<page file> | <selector> | measured WxHpx (needs >= 44px) | static; <element> "text" | at 360[,390,412]px"""
    count = f" (x{f['count']})" if f.get("count", 1) > 1 else ""
    if warn:
        head = f"not measurable: {f['extra']} (needs >= 44px)"
    else:
        head = f"measured {f['measured']} (needs >= 44px)"
    views = ",".join(str(v) for v in f["viewports"])
    return " | ".join([f["file"], f["selector"], head, f"static; {f['element']} \"{f['text']}\"{count}",
                       f"at {views}px"])


def _tap_rows(rep: "Report", pages: list[Path]) -> None:
    at = "/".join(str(w) for w, _ in TAP_VIEWPORTS) + "px"
    try:
        scan = tap_scan(pages)
    except Exception as exc:  # fail closed
        rep.add("tap_target", "FAIL", f"static; checker error: {type(exc).__name__}: {exc}", failures=[])
        return
    fails, warns = scan["fails"], scan["warns"]
    tail = (f"{scan['checked']} measured >=44px, {scan['exempt']} inline-in-sentence link(s) exempt (WCAG 2.5.8), "
            f"{scan['hidden_ok']} hidden-at-360px control(s) measured as if shown")
    tail += f"; judged at {at}"
    if scan["hidden_skipped"]:
        tail += f", {scan['hidden_skipped']} control(s) with display:none themselves not measured"
    if fails:
        shown = "; ".join(f"{f['file']}: {f['selector']} {f['measured']} (needs >= 44px)" for f in fails[:6])
        extra = f" (+{len(fails) - 6} more)" if len(fails) > 6 else ""
        rep.add("tap_target", "FAIL", "static; " + shown + extra, failures=fails,
                unmeasured=warns)
        return
    if warns or scan["notes"]:
        nm = sum(w.get("count", 1) for w in warns)
        rep.add("tap_target", "WARN",
                f"static, {scan['pages']} page(s) at {at}; {nm} control(s) not measurable (never a pass); " + tail,
                failures=[], unmeasured=warns)
        return
    low = f"smallest guaranteed {_fmt_px(scan['min_w'])[:-2]}x{_fmt_px(scan['min_h'])[:-2]}px; " \
        if scan["min_w"] is not None else ""
    rep.add("tap_target", "PASS",
            f"static, {scan['pages']} page(s) at {at}; {low}floor 44px; " + tail, failures=[])



# ---------------------------------------------------------------------------
# GATES.md rows without a row before: slug_shape, photo_luma, svg_photo, grey_tile.
# slug_shape is static. photo_luma needs Pillow (SKIP = not-run when missing).
# grey_tile cannot be proven from static CSS, so it is always an explicit
# not-run row (SKIP), never a pass.
# ---------------------------------------------------------------------------
SLUG_MAX_WORDS = 6
SLUG_MAX_CHARS = 60
LUMA_MIN = 90.0
LUMA_MAX = 200.0
LUMA_PHOTO_MIN_WIDTH = 400
_SLUG_DATE = re.compile(r"(?:^|-)(?:19|20)\d{2}(?:-\d{1,2}){0,2}(?:-|$)|(?:^|-)\d{8}(?:-|$)")
_SLUG_SUFFIX = re.compile(r"-(?:\d+|v\d+|copy|final|new|old|draft|test|temp|tmp|backup|bak|batch\d*|pass\d*)$", re.I)
_RASTER_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")


def slug_problems(slug: str) -> list[str]:
    out = []
    if slug != slug.lower():
        out.append("uppercase")
    if "_" in slug:
        out.append("underscore")
    low = slug.lower()
    if _SLUG_DATE.search(low):
        out.append("date")
    if _SLUG_SUFFIX.search(low):
        out.append("trailing number/pass/batch suffix")
    words = [w for w in re.split(r"[-_]+", slug) if w]
    if len(words) > SLUG_MAX_WORDS:
        out.append(f"{len(words)} words")
    if len(slug) > SLUG_MAX_CHARS:
        out.append(f"{len(slug)} chars")
    if re.search(r"[^A-Za-z0-9_-]", slug):
        out.append("characters outside a-z 0-9 hyphen")
    return out


def slug_scan(site_dir: Path) -> dict:
    fails = []
    seen = 0
    for page in sorted(site_dir.rglob("*.html")):
        rel = page.relative_to(site_dir)
        if rel.parts and rel.parts[0] == "_attempts":
            continue  # attempts are history, not product (FINAL D2, hash-excluded)
        slugs = []
        if page.stem.lower() != "index":
            slugs.append(page.stem)
        elif rel.parent != Path("."):
            slugs.append(rel.parent.name)
        for part in rel.parent.parts:
            if part not in [s for s in slugs]:
                slugs.append(part)
        for slug in slugs:
            seen += 1
            problems = slug_problems(slug)
            if problems:
                words = len([w for w in re.split(r"[-_]+", slug) if w])
                fails.append({"check": "slug_shape", "file": rel.as_posix(), "selector": slug,
                              "measured": f"{words} word(s), {len(slug)} char(s): " + ", ".join(problems),
                              "required": f"<= {SLUG_MAX_WORDS} words, <= {SLUG_MAX_CHARS} chars, lowercase-hyphen, "
                                          "no date or number suffix", "extra": "static", "count": 1,
                              "viewports": []})
    return {"fails": fails, "seen": seen}


def _slug_row(rep: "Report", site_dir: Path) -> None:
    scan = slug_scan(site_dir)
    if scan["fails"]:
        shown = "; ".join(f"{f['file']}: {f['selector']} ({f['measured']})" for f in scan["fails"][:6])
        rep.add("slug_shape", "FAIL", "static; " + shown, failures=scan["fails"])
    else:
        rep.add("slug_shape", "PASS", f"static; {scan['seen']} page slug(s) checked (index exempt); "
                f"max {SLUG_MAX_WORDS} words, {SLUG_MAX_CHARS} chars, lowercase hyphen, no date or number suffix",
                failures=[])


def _mean_luma(path: Path):
    from PIL import Image  # raises ImportError when Pillow is absent
    with Image.open(path) as im:
        width = im.size[0]
        g = im.convert("RGB").convert("L").resize((128, 128))
    return sum(g.tobytes()) / 16384.0, width


def _photo_rows(rep: "Report", pages: list[Path]) -> None:
    files: list[tuple[str, str, Path]] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        for src in _img_srcs(html):
            local = _local_img_src(src)
            if local and local.lower().split("?", 1)[0].endswith(_RASTER_EXT):
                files.append((page.name, local, page.parent / unquote(local.split("?", 1)[0])))
    if not files:
        rep.add("photo_luma", "PASS", "static; no raster img on any page (CSS background images are not read)",
                failures=[])
        return
    try:
        import PIL  # noqa: F401
    except ImportError:
        rep.add("photo_luma", "SKIP", f"not-run: Pillow is not installed; {len(files)} raster img not measured",
                failures=[])
        return
    fails, skipped, measured, small = [], [], 0, 0
    for page_name, local, path in files:
        try:
            luma, width = _mean_luma(path)
        except Exception as exc:
            skipped.append(f"{page_name}: img[src=\"{local}\"] unreadable ({type(exc).__name__})")
            continue
        if width < LUMA_PHOTO_MIN_WIDTH:
            small += 1
            continue
        measured += 1
        if not (LUMA_MIN <= luma <= LUMA_MAX):
            fails.append({"check": "photo_luma", "file": page_name, "selector": f'img[src="{local}"]',
                          "measured": f"mean luma {luma:.0f}", "required": f"{LUMA_MIN:.0f}-{LUMA_MAX:.0f}",
                          "extra": f"static; {width}px wide file", "count": 1, "viewports": []})
    if fails:
        shown = "; ".join(f"{f['file']}: {f['selector']} {f['measured']} (needs {f['required']})" for f in fails[:6])
        rep.add("photo_luma", "FAIL", shown, failures=fails)
    elif skipped:
        rep.add("photo_luma", "WARN", f"{len(skipped)} image(s) not measurable: " + "; ".join(skipped[:3]), failures=[])
    else:
        rep.add("photo_luma", "PASS", f"{measured} photo(s) mean luma within {LUMA_MIN:.0f}-{LUMA_MAX:.0f}; "
                f"{small} img under {LUMA_PHOTO_MIN_WIDTH}px wide treated as icons/logos", failures=[])


_SVG_PHOTO_WORDS = re.compile(r"thumb|photo|hero|cover|schematic|diagram|placeholder|sample", re.I)


def _svg_photo_row(rep: "Report", pages: list[Path]) -> None:
    fails = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"<img\b([^>]*)>", html, re.I):
            attrs = m.group(1)
            src = _attr(attrs, "src") or ""
            if src.lower().split("?", 1)[0].endswith(".svg"):
                ctx = " ".join(filter(None, (_attr(attrs, "class"), _attr(attrs, "id"), _attr(attrs, "alt"), src)))
                hit = _SVG_PHOTO_WORDS.search(ctx)
                if hit:
                    fails.append({"check": "svg_photo", "file": page.name, "selector": f'img[src="{src}"]',
                                  "measured": f'svg file used as image (matches "{hit.group(0).lower()}")',
                                  "required": "a real raster photo or no image", "extra": "static", "count": 1,
                                  "viewports": []})
        for m in re.finditer(r"<svg\b[^>]*(?:class|id)\s*=\s*[\"']([^\"']*)[\"']", html, re.I):
            hit = re.search(r"thumb|photo", m.group(1), re.I)
            if hit:
                fails.append({"check": "svg_photo", "file": page.name, "selector": f'svg[class/id="{m.group(1)}"]',
                              "measured": f'inline svg posing as a photo (matches "{hit.group(0).lower()}")',
                              "required": "a real raster photo or no image", "extra": "static", "count": 1,
                              "viewports": []})
    if fails:
        shown = "; ".join(f"{f['file']}: {f['selector']} {f['measured']}" for f in fails[:6])
        rep.add("svg_photo", "FAIL", "static; " + shown, failures=fails)
    else:
        rep.add("svg_photo", "PASS", "static; no svg posing as a photo (img .svg with thumb/photo/hero/cover/"
                "schematic/diagram/placeholder/sample wording, or inline svg class thumb/photo)", failures=[])


def _grey_tile_row(rep: "Report") -> None:
    rep.add("grey_tile", "SKIP", "not-run: a grey tile standing in for a photo is a rendered condition; static CSS "
            "cannot prove it absent (use webcheck.py page at 360px and 1280px)", failures=[])


# ---------------------------------------------------------------------------
# HERO single-gate additions (team-gates): one cited CTA, every string cited,
# weight, safe-area, css contract, layout stability, visual probe.
# Stdlib only. All PASS on demo-local + bench-harbor-tearoom.
# ---------------------------------------------------------------------------
_WEIGHT_HTML_RAW = 153600
_WEIGHT_HTML_GZIP = 40960
_WEIGHT_SCRIPT = 4096
_WEIGHT_HERO_IMG = 102400
_WEIGHT_OTHER_IMG = 204800

_CITED_ALLOW = {"Skip to content"}
_FOOTER_RE = re.compile(r"^\(c\)\s+\d{4}\s+(.+)$", re.I)


def _strip_ld_json(html: str) -> str:
    return re.sub(
        r'<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>.*?</script>',
        "<script></script>",
        html,
        flags=re.I | re.S,
    )


def _cta_anchors(html: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """(hero primaries, thumb bars) as (href, label) pairs."""
    hero: list[tuple[str, str]] = []
    bars: list[tuple[str, str]] = []
    for m in re.finditer(r"<a\b([^>]*)>(.*?)</a>", html, re.I | re.S):
        attrs, inner = m.group(1), m.group(2)
        klass = _attr(attrs, "class") or ""
        toks = klass.split()
        href = _attr(attrs, "href") or ""
        label = re.sub(r"<[^>]*>", "", inner)
        label = " ".join(label.split())
        if "btn" in toks and "primary" in toks:
            hero.append((href, label))
        elif "phone-bar" in toks:
            bars.append((href, label))
    return hero, bars


def _one_cta_row(rep: "Report", pages: list[Path], copy_text: str = "") -> None:
    fails: list[str] = []
    norm = " ".join(copy_text.split()) if copy_text else ""
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        hero, bars = _cta_anchors(html)
        total = len(hero) + len(bars)
        if total == 0:
            fails.append(f"{page.name}: no primary CTA (need one cited hero action)")
            continue
        if total > 2:
            fails.append(f"{page.name}: {total} primary CTAs (hero + thumb bar at most)")
            continue
        # nav must not hold a primary marker
        nav_blocks = re.findall(r"<nav\b[^>]*>(.*?)</nav>", html, re.I | re.S)
        for blk in nav_blocks:
            if 'btn primary' in blk or 'phone-bar' in blk or 'data-cta' in blk:
                fails.append(f"{page.name}: nav holds a primary marker")
                break
        if copy_text:
            for href, label in hero + bars:
                if not label:
                    fails.append(f"{page.name}: primary CTA has empty label")
                    continue
                if " ".join(label.split()) not in norm:
                    fails.append(f"{page.name}: CTA label not in copy: {label[:60]}")
                if href.startswith("tel:"):
                    digits = "".join(ch for ch in href if ch.isdigit())
                    if digits not in "".join(ch for ch in copy_text if ch.isdigit()):
                        fails.append(f"{page.name}: tel href not in copy: {href[:40]}")
                elif href.startswith("mailto:"):
                    addr = href[7:].split("?")[0].strip()
                    if addr and addr not in copy_text:
                        fails.append(f"{page.name}: mailto href not in copy: {addr[:60]}")
                elif not href:
                    fails.append(f"{page.name}: primary CTA has empty href")
    if fails:
        extra = f" (+{len(fails) - 8} more)" if len(fails) > 8 else ""
        rep.add("one_cta", "FAIL", "; ".join(fails[:8]) + extra)
    else:
        rep.add("one_cta", "PASS", f"{len(pages)} page(s), one cited CTA (hero + optional thumb bar)")


# ---------------------------------------------------------------------------
# Conversion rows (FINAL D4: cta_present, ask_after_proof, single_primary_cta)
# plus the D5 mobile_block row. Additive: the legacy one_cta / phone_bar rows
# above are untouched; these rows carry the conversion-canonical names the
# FULL PACK batteries address. All four are fail-closed and SKIP (never PASS)
# when their evidence (site.json / copy_text) is absent.
# ---------------------------------------------------------------------------
_MOBILE_BLOCK_KEYS = ("stack", "order")


def _conversion_site_pages(site_dir: Path) -> list[tuple[str, list]] | None:
    """[(slug, sections)] from site.json, or None when it cannot be read."""
    try:
        site = json.loads((Path(site_dir) / "site.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    pages = site.get("pages") if isinstance(site, dict) else None
    if not isinstance(pages, list):
        return None
    out: list[tuple[str, list]] = []
    for page in pages:
        if not isinstance(page, dict):
            continue
        secs = page.get("sections")
        out.append((str(page.get("slug") or "index"), secs if isinstance(secs, list) else []))
    return out


def _cta_present_row(rep: "Report", pages: list[Path]) -> None:
    """Every page carries at least one primary CTA (hero button or bar)."""
    fails: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        hero, bars = _cta_anchors(html)
        if len(hero) + len(bars) == 0:
            fails.append(page.name + ": no primary CTA")
    if fails:
        rep.add("cta_present", "FAIL", "; ".join(fails[:8]))
    else:
        rep.add("cta_present", "PASS", str(len(pages)) + " page(s) carry a primary CTA")


def _ask_after_proof_row(rep: "Report", site_dir: Path) -> None:
    """Ask slots (contact/cta) close the page: never before proof."""
    from lib import frames as _frames

    info = _conversion_site_pages(site_dir)
    if info is None:
        rep.add("ask_after_proof", "SKIP", "not-run: no site.json", failures=[])
        return
    fails: list[str] = []
    for slug, secs in info:
        complaint = _frames.check_ask_after_proof(secs)
        if complaint:
            fails.append(slug + ".html: " + complaint)
    if fails:
        rep.add("ask_after_proof", "FAIL", "; ".join(fails[:8]))
    else:
        rep.add("ask_after_proof", "PASS", "offer->proof->ask holds")


def _single_primary_cta_row(
    rep: "Report", site_dir: Path, pages: list[Path], copy_text: str = ""
) -> None:
    """Exactly one visible primary per viewport, wired verbatim.

    Hero primaries <= 1, bars <= 1, nav holds no primary marker (per-view
    exclusivity is the CSS display swap; this row proves the swap has one
    owner per side). tel: digits must be verbatim copy digits and a contact
    ask slot carrying digits without a bar FAILs: absent wire, never an
    invented number.
    """
    fails: list[str] = []
    norm_digits = "".join(ch for ch in copy_text if ch.isdigit()) if copy_text else ""
    ask_digits: dict[str, str] = {}
    info = _conversion_site_pages(site_dir)
    if info is not None:
        for slug, secs in info:
            for sec in secs:
                if not isinstance(sec, dict) or sec.get("type") not in ("contact", "cta"):
                    continue
                data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
                for key in ("title", "body", "phone", "hours", "address"):
                    value = data.get(key)
                    texts = value if isinstance(value, list) else [value]
                    for item in texts:
                        if not isinstance(item, str):
                            continue
                        run = "".join(ch for ch in item if ch.isdigit())
                        if len(run) >= 7:
                            ask_digits.setdefault(slug, run)
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        hero, bars = _cta_anchors(html)
        total = len(hero) + len(bars)
        if len(hero) > 1:
            fails.append(page.name + ": " + str(len(hero)) + " hero primaries")
        if len(bars) > 1:
            fails.append(page.name + ": " + str(len(bars)) + " phone bars")
        if total == 0:
            fails.append(page.name + ": no primary CTA")
            continue
        if total > 2:
            fails.append(page.name + ": " + str(total) + " primary CTAs")
            continue
        nav_blocks = re.findall(r"<nav\b[^>]*>(.*?)</nav>", html, re.I | re.S)
        for blk in nav_blocks:
            if "btn primary" in blk or "phone-bar" in blk or "data-cta" in blk:
                fails.append(page.name + ": nav holds a primary marker")
                break
        for href, _label in hero + bars:
            if href.startswith("tel:"):
                digits = "".join(ch for ch in href if ch.isdigit())
                if len(digits) < 7:
                    fails.append(page.name + ": tel href under 7 digits: " + href[:40])
                elif norm_digits and digits not in norm_digits:
                    fails.append(page.name + ": tel href not in copy: " + href[:40])
            elif href.startswith("mailto:"):
                addr = href[7:].split("?")[0].strip()
                if copy_text and addr and addr not in copy_text:
                    fails.append(page.name + ": mailto href not in copy: " + addr[:60])
            elif not href:
                fails.append(page.name + ": primary CTA has empty href")
        if page.stem in ask_digits and not bars:
            fails.append(page.name + ": ask slot has digits but no phone-bar")
    if fails:
        extra = " (+" + str(len(fails) - 8) + " more)" if len(fails) > 8 else ""
        rep.add("single_primary_cta", "FAIL", "; ".join(fails[:8]) + extra)
    else:
        rep.add(
            "single_primary_cta",
            "PASS",
            str(len(pages)) + " page(s), one visible primary per viewport",
        )


def _mobile_block_row(rep: "Report", site_dir: Path) -> None:
    """D5 mobile blocks: known keys only, stack true, unique phone order.

    Block-free pages pass untouched: the row judges declared phone design,
    it never demands it.
    """
    info = _conversion_site_pages(site_dir)
    if info is None:
        rep.add("mobile_block", "SKIP", "not-run: no site.json", failures=[])
        return
    fails: list[str] = []
    count = 0
    for slug, secs in info:
        seen_orders: dict[int, str] = {}
        for sec in secs:
            if not isinstance(sec, dict):
                continue
            data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
            mob = data.get("mobile")
            if mob is None:
                continue
            sid = str(sec.get("id") or sec.get("type") or "?")
            count += 1
            if not isinstance(mob, dict):
                fails.append(slug + "." + sid + ": mobile must be an object")
                continue
            for key in mob:
                if key not in _MOBILE_BLOCK_KEYS:
                    fails.append(
                        slug + "." + sid + ": unknown mobile key "
                        + repr(key) + " (stack/order only)"
                    )
            if "stack" in mob and mob["stack"] is not True:
                fails.append(slug + "." + sid + ": mobile.stack must be true")
            if "order" in mob:
                order = mob["order"]
                if isinstance(order, bool) or not isinstance(order, int) or order < 0:
                    fails.append(slug + "." + sid + ": mobile.order must be int >= 0")
                elif order in seen_orders:
                    fails.append(
                        slug + "." + sid + ": mobile.order "
                        + str(order) + " duplicates " + seen_orders[order]
                    )
                else:
                    seen_orders[order] = sid
    if fails:
        rep.add("mobile_block", "FAIL", "; ".join(fails[:8]))
    else:
        rep.add("mobile_block", "PASS", str(count) + " mobile block(s), 360-first")


def _cited_text_row(rep: "Report", pages: list[Path], copy_text: str) -> None:
    if not copy_text:
        rep.add("cited_text", "SKIP", "not-run: no copy_text (pass --project or crew context)", failures=[])
        return
    norm = " ".join(copy_text.split())
    fails: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        vis = visible_text(html)
        for line in vis.splitlines():
            text = line.strip()
            if not text:
                continue
            folded = " ".join(text.split())
            if folded in norm:
                continue
            if folded in _CITED_ALLOW:
                continue
            m = _FOOTER_RE.match(folded)
            if m and " ".join(m.group(1).split()) in norm:
                continue
            fails.append(f"{page.name}: {folded[:80]}")
            if len(fails) >= 12:
                break
    if fails:
        extra = f" (+{len(fails) - 8} more)" if len(fails) > 8 else ""
        rep.add("cited_text", "FAIL", "; ".join(fails[:8]) + extra)
    else:
        rep.add("cited_text", "PASS", f"{len(pages)} page(s), every visible string cited")


def _weight_row(rep: "Report", pages: list[Path]) -> None:
    import gzip as _gzip
    fails: list[str] = []
    for page in pages:
        raw = page.read_bytes()
        if len(raw) > _WEIGHT_HTML_RAW:
            fails.append(f"{page.name}: html {len(raw)}B > {_WEIGHT_HTML_RAW}B")
        try:
            gz = len(_gzip.compress(raw))
        except Exception:
            gz = 0
        if gz > _WEIGHT_HTML_GZIP:
            fails.append(f"{page.name}: gzip {gz}B > {_WEIGHT_HTML_GZIP}B")
        html = raw.decode("utf-8", errors="replace")
        for m in re.finditer(r"<script\b(?![^>]*type\s*=\s*[\"']application/ld\+json[\"'])[^>]*>(.*?)</script>", html, re.I | re.S):
            if len(m.group(1).encode("utf-8")) > _WEIGHT_SCRIPT:
                fails.append(f"{page.name}: inline script > {_WEIGHT_SCRIPT}B")
                break
    # image budgets from files beside pages
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        for src in _img_srcs(html):
            rel = _local_img_src(src)
            if rel is None:
                continue
            f = page.parent / unquote(rel.split("?", 1)[0].split("#", 1)[0])
            try:
                size = f.stat().st_size
            except OSError:
                continue
            limit = _WEIGHT_HERO_IMG if "hero" in rel.lower() else _WEIGHT_OTHER_IMG
            if size > limit:
                fails.append(f"{page.name}: {rel} {size}B > {limit}B")
    if fails:
        rep.add("weight", "FAIL", "; ".join(fails[:6]))
    else:
        rep.add("weight", "PASS", f"{len(pages)} page(s) within budgets")


def _safe_area_row(rep: "Report", pages: list[Path]) -> None:
    fails: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        if 'name="viewport"' in html and "viewport-fit=cover" not in html:
            fails.append(f"{page.name}: viewport without viewport-fit=cover")
        if "phone-bar" in html:
            if "env(safe-area-inset-bottom)" not in html:
                fails.append(f"{page.name}: thumb bar without safe-area inset")
            if "padding-bottom" not in html:
                fails.append(f"{page.name}: thumb bar without body padding-bottom reserve")
            if "scroll-margin-top" not in html and "scroll-padding-top" not in html:
                fails.append(f"{page.name}: missing scroll-margin/padding-top")
    if fails:
        rep.add("safe_area", "FAIL", "; ".join(fails[:6]))
    else:
        rep.add("safe_area", "PASS", f"{len(pages)} page(s), thumb bar + focus not covered")


def _css_contract_row(rep: "Report", pages: list[Path]) -> None:
    fails: list[str] = []
    # Bare html/body element selectors only: a scoped state rule such as
    # body.nav-open{overflow:hidden} (drawer scroll-lock) is not a global clip.
    _bare = r"(?:(?<=[{};,\s])|^)(html|body)(?=[\s,{])"
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
        # forbid global sideways clip that hides overflow instead of fixing it
        for m in re.finditer(
            _bare + r"[^{]*\{[^}]*overflow-x\s*:\s*(hidden|clip)[^}]*\}",
            css, re.IGNORECASE,
        ):
            fails.append(f"{page.name}: {m.group(1)} overflow-x:{m.group(2)} hides overflow")
        for m in re.finditer(
            _bare + r"[^{]*\{[^}]*overflow\s*:\s*(hidden|clip)[^}]*\}",
            css, re.IGNORECASE,
        ):
            # overflow:hidden on a bare html/body rule is FAIL, even in @media.
            fails.append(f"{page.name}: {m.group(1)} overflow:{m.group(2)} hides overflow")
            break
    if fails:
        rep.add("css_contract", "FAIL", "; ".join(fails[:6]))
    else:
        rep.add("css_contract", "PASS", f"{len(pages)} page(s), no global overflow clip")


def _layout_stability_row(rep: "Report", pages: list[Path]) -> None:
    fails: list[str] = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"<img\b([^>]*)>", html, re.I):
            attrs = m.group(1)
            w = _attr(attrs, "width")
            h = _attr(attrs, "height")
            if not (w and h):
                src = _attr(attrs, "src") or "img"
                fails.append(f"{page.name}: img without width+height: {src[:40]}")
                break
    if fails:
        rep.add("layout_stability", "FAIL", "; ".join(fails[:6]))
    else:
        rep.add("layout_stability", "PASS", f"{len(pages)} page(s), img dimensions set")


def _visual_probe_row(rep: "Report", site_dir: Path, pages: list[Path]) -> None:
    probe = site_dir / "layout-probe.json"
    if not probe.is_file():
        rep.add("visual_probe", "SKIP", "not-run: no layout-probe.json (run tools/layout_probe.py); unrun!=pass", failures=[])
        return
    try:
        data = json.loads(probe.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        rep.add("visual_probe", "FAIL", f"layout-probe.json unreadable: {exc}", failures=[])
        return
    # bind probe to current bytes: stored html hash must match
    import hashlib as _hl
    h = _hl.sha256()
    for p in sorted(pages):
        h.update(p.read_bytes())
    cur = h.hexdigest()[:16]
    want = str(data.get("html_hash") or data.get("hash") or "")
    if want and want != cur and cur not in want:
        rep.add("visual_probe", "FAIL", "layout-probe.json stale (html changed); re-run probe", failures=[])
        return
    rows = data.get("rows") if isinstance(data.get("rows"), list) else data.get("profiles")
    if isinstance(rows, list) and any(isinstance(r, dict) and r.get("status") == "FAIL" for r in rows):
        rep.add("visual_probe", "FAIL", "probe rows contain FAIL", failures=[])
        return
    rep.add("visual_probe", "PASS", f"probe {probe.name} bound to html {cur}", failures=[])


def _gate_rows(rep: "Report", site_dir: Path, pages: list[Path]) -> None:
    for fn in (lambda: _slug_row(rep, site_dir), lambda: _photo_rows(rep, pages), lambda: _svg_photo_row(rep, pages)):
        try:
            fn()
        except Exception as exc:  # fail closed
            rep.add("gate_error", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
    _grey_tile_row(rep)


# ---------------------------------------------------------------------------
# Mobile gates, STATIC (rows sideways_scroll, mobile_nav_drawer, mobile_visibility,
# and mobile_spec when --mobile-spec is given). Same static cascade as
# type_floor/contrast/tap_target, evaluated at every phone width in
# MOBILE_VIEWPORTS (360, 390, 412) and, for the visibility inventory, at the
# 1280px desktop baseline. Every row says static (or rendered for capture
# evidence read from a patterns.json). A condition that cannot be decided from
# HTML and CSS is WARN "not measurable" or a SKIP "not-run", never a pass.
#   sideways_scroll:   an element whose resolved box ends right of the viewport
#                      (fixed width/min-width in px, vw over 100, % over 100,
#                      negative right margin beyond the gutter, img/iframe/video/
#                      svg width attribute with no max-width, wide table, pre or
#                      nowrap text, long unbreakable word) and no clipping or
#                      scrolling ancestor below body.
#   mobile_nav_drawer: more than MOBILE_NAV_INLINE_MAX primary nav links at a
#                      phone width need a toggle: a <button> (or role=button)
#                      with aria-expanded="false", aria-controls naming an
#                      existing id, an accessible name and a 44px box. The
#                      controlled drawer must hold the nav links, be hidden by
#                      default, open in a static simulation of the page's own
#                      script (classes it adds, hidden it removes, aria-expanded
#                      true) and have a close mechanism (toggle that flips back
#                      and stays visible, a close button inside, Escape, or a
#                      native dialog/popover).
#   mobile_visibility: inventory of elements shown only at phone widths and of
#                      elements hidden at phone widths but shown at 1280px.
#                      Content hidden on mobile is WARN; h1 or main hidden at a
#                      phone width is FAIL. The drawer and its toggle are exempt.
# Not modelled: rendered layout and real container widths, JS-built DOM,
# transforms, left-edge overflow (cut off, not scrollable), web fonts.
# Rendered follow-up: the capture tool mobile_capture.py (Playwright) writes a
# patterns.json; pass its path with --mobile-spec PATH to add the mobile_spec row.
# No path is assumed: the spec path always comes from the caller.
# ---------------------------------------------------------------------------
MOBILE_NAV_INLINE_MAX = 4   # more primary nav links than this at a phone width need a toggle
MOBILE_WORD_MIN_CHARS = 25  # unbreakable words this long are measured for overflow
_MOB_CONTAIN = frozenset(("auto", "scroll", "hidden", "clip", "overlay"))
_MOB_MONO_GLYPH = (0.50, 0.62)     # monospace advance, multiple of font-size
_MOB_REPLACED = frozenset(("img", "iframe", "video", "svg", "canvas", "embed", "object"))
_MOB_TOGGLE_WORDS = re.compile(r"menu|nav|hamburger|burger|toggle|drawer|offcanvas|off-canvas", re.I)
_MOB_CLOSE_WORDS = re.compile(r"close|dismiss|\u00d7|\u2715|\u2716", re.I)
_MOB_ESCAPE_RE = re.compile(r"""['"]Esc(?:ape)?['"]|keyCode\s*={2,3}\s*27|which\s*={2,3}\s*27""")
_MOB_CLASS_RE = re.compile(r"""(?:classList\s*\.\s*(?:add|toggle)|(?:add|toggle)Class)\s*\(\s*(['"])([\w-]+)\1""")
_MOB_TOGGLE_RE = re.compile(r"""classList\s*\.\s*toggle\s*\(|toggleClass\s*\(|toggleAttribute\s*\(""")
_MOB_UNHIDE_RE = re.compile(r"""removeAttribute\s*\(\s*['"]hidden['"]|\.hidden\s*=\s*(?:false|!)|toggleAttribute\s*\(\s*['"]hidden['"]""")
_MOB_EXPANDED_RE = re.compile(r"""setAttribute\s*\(\s*['"]aria-expanded['"]""")
_MOB_OFFSCREEN_RE = re.compile(r"translate(?:x|3d)?\(\s*-?100%|translate\(\s*-?100vw", re.I)


def _mob_desc(node: _Node) -> str:
    return _describe(node)[1:-1]


def _mob_cascade(root: _Node, author_items: list, w: int, h: int):
    """One static cascade at (w, h). Returns ctx, nodes in document order, {id: hiding node or None}."""
    ctx = _Ctx(w, h)
    rules = _build_rules(_parse_css_items(_UA_CSS), w, h, True, 0) + _build_rules(author_items, w, h, False, 10000)
    order: list[_Node] = []
    hidden: dict[int, object] = {}
    stack = [(root, _ROOT_CS, None)]
    while stack:
        node, pcs, hid = stack.pop()
        if node.tag == "#doc":
            cs = pcs
        else:
            cs = _compute(node, pcs, ctx, rules)
            node.cs = cs
            if node.tag == "html" and cs["size"]:
                ctx.root = cs["size"]
            if hid is None and (cs["hidden"] or cs["invisible"]):
                hid = node
            hidden[id(node)] = hid
            order.append(node)
            if node.tag in _SKIP_TAGS:
                continue
        for child in reversed(node.children):
            stack.append((child, cs, hid))
    return ctx, order, hidden


def _mob_hide_label(node) -> str:
    if node is None:
        return ""
    box = _tap_box(node)
    for prop in ("display", "visibility"):
        if prop in box:
            return f"{prop}:{box[prop][0].strip()} from {box[prop][1]}"
    return "hidden attribute" if "hidden" in node.attrs else "hidden"


def _mob_ancestors(node: _Node):
    p = node.parent
    while p is not None and p.tag != "#doc":
        yield p
        p = p.parent


def _mob_contained(node: _Node, include_self: bool = False) -> str:
    """Selector of the nearest element below body that clips or scrolls x overflow, or ''."""
    chain = ([node] if include_self else []) + list(_mob_ancestors(node))
    for n in chain:
        if n.tag in ("html", "body"):
            break
        for prop in ("overflow-x", "overflow"):
            v = _tap_boxval(n, prop)
            if v and v.split()[0] in _MOB_CONTAIN:
                return _mob_desc(n)
    return ""


def _mob_root_clip(order: list[_Node]) -> str:
    for n in order:
        if n.tag in ("html", "body"):
            for prop in ("overflow-x", "overflow"):
                v = _tap_boxval(n, prop)
                if v and v.split()[0] in ("hidden", "clip"):
                    return f"{n.tag} {prop}:{v}"
    return ""


def _mob_px(node: _Node, prop: str, ctx: _Ctx, base):
    """px float, None (unset/auto), or '?' (not resolvable)."""
    v = _tap_boxval(node, prop)
    if v is None or v in ("auto", "none", "normal", "initial", "unset", "revert", "0"):
        return 0.0 if v == "0" else None
    if v in ("fit-content", "max-content", "min-content", "stretch", "-webkit-fill-available", "inherit"):
        return "?"
    got = _eval_len(v, node.cs.get("size") or 16.0, ctx, base)
    return "?" if got is None else got


def _mob_num(v) -> float:
    return v if isinstance(v, float) else 0.0


class _MobGeo:
    """Approximate x geometry at one viewport: content-box left edge and inner width per node."""

    def __init__(self, ctx: _Ctx):
        self.ctx = ctx
        self.memo: dict[int, tuple] = {}

    def _pad_border(self, node: _Node, avail: float):
        size = node.cs.get("size") or 16.0
        out = []
        for side in ("left", "right"):
            p = _mob_px(node, f"padding-{side}", self.ctx, avail)
            b = _tap_border(node, side, size, self.ctx)
            out.append(_mob_num(p) + (b[0] if b[1] != _INF else 0.0))
        return out[0], out[1]

    def frame(self, node: _Node):
        """(content_left, inner_width, border_left, border_width) for node; html starts at 0..W."""
        key = id(node)
        if key in self.memo:
            return self.memo[key]
        W = self.ctx.w
        parent = node.parent
        if node.tag == "html" or parent is None or parent.tag == "#doc":
            res = (0.0, W, 0.0, W)
            self.memo[key] = res
            return res
        pleft, pinner, _, _ = self.frame(parent)
        pos = _tap_boxval(node, "position") or "static"
        if pos == "fixed":
            pleft, pinner = 0.0, W
        ml = _mob_px(node, "margin-left", self.ctx, pinner)
        mr = _mob_px(node, "margin-right", self.ctx, pinner)
        if node.tag == "body" and _tap_boxval(node, "margin-left") is None and _tap_boxval(node, "margin") is None:
            ml = mr = 8.0  # browser default body margin
        ml, mr = _mob_num(ml), _mob_num(mr)
        if pos in ("absolute", "fixed"):
            lv = _mob_px(node, "left", self.ctx, pinner)
            if isinstance(lv, float):
                ml = lv + ml
        padl, padr = self._pad_border(node, pinner)
        bw = self.border_width(node, pinner, ml, mr)
        left = pleft + ml
        inner = max(bw - padl - padr, 0.0)
        res = (left + padl, inner, left, bw)
        self.memo[key] = res
        return res

    def border_width(self, node: _Node, avail: float, ml: float, mr: float):
        """Resolved border-box width; a block with no usable width fills avail - margins."""
        box_sizing = _tap_boxval(node, "box-sizing") or "content-box"
        padl, padr = self._pad_border(node, avail)
        extra = 0.0 if box_sizing == "border-box" else padl + padr
        w = _mob_px(node, "width", self.ctx, avail)
        mn = _mob_px(node, "min-width", self.ctx, avail)
        mx = _mob_px(node, "max-width", self.ctx, avail)
        bw = (w + extra) if isinstance(w, float) else max(avail - ml - mr, 0.0)
        if isinstance(mx, float):
            bw = min(bw, mx + extra)
        if isinstance(mn, float):
            bw = max(bw, mn + extra)
        return bw


def _mob_white_space(node: _Node) -> str:
    n = node
    while n is not None and n.tag != "#doc":
        v = _tap_boxval(n, "white-space")
        if v and v not in ("inherit", "unset"):
            return v
        if n.tag in ("pre", "textarea"):
            return "pre"
        n = n.parent
    return "normal"


def _mob_breaks_words(node: _Node) -> bool:
    n = node
    while n is not None and n.tag != "#doc":
        ow = _tap_boxval(n, "overflow-wrap") or _tap_boxval(n, "word-wrap")
        wb = _tap_boxval(n, "word-break")
        if (ow and ow in ("anywhere", "break-word")) or (wb and wb in ("break-all", "break-word")):
            return True
        if ow or wb:
            return False
        n = n.parent
    return False


def _mob_raw_text(node: _Node) -> str:
    parts: list[str] = []
    stack = [node]
    while stack:
        n = stack.pop()
        parts.append("".join(n.texts))
        stack.extend(reversed(n.children))
    return "".join(parts)


def _mob_mono(node: _Node) -> bool:
    n = node
    while n is not None and n.tag != "#doc":
        ff = _tap_boxval(n, "font-family")
        if ff:
            return bool(re.search(r"mono|courier|consolas|menlo", ff))
        if n.tag in ("pre", "code", "kbd", "samp", "tt"):
            return True
        n = n.parent
    return False


def _mob_flex_row_shrinks(node: _Node) -> bool:
    parent = node.parent
    if parent is None or parent.tag == "#doc":
        return False
    if _tap_raw_display(parent) not in ("flex", "inline-flex"):
        return False
    if (_tap_boxval(parent, "flex-direction") or "row").startswith("column"):
        return False
    flex = _tap_boxval(node, "flex")
    if flex in ("none",):
        return False
    shrink = _tap_boxval(node, "flex-shrink")
    if shrink is None and flex:
        parts = flex.split()
        shrink = parts[1] if len(parts) >= 2 and re.fullmatch(r"[0-9.]+", parts[1]) else ("1" if parts[0] != "none" else "0")
    return shrink != "0"


class _MobAcc:
    def __init__(self):
        self.fails: dict = {}
        self.warns: dict = {}
        self.inventory: dict = {}
        self.nodes: dict = {}
        self.pages = 0
        self.notes: list[str] = []
        self.checked = 0

    def rec(self, store: dict, check: str, page: str, node, selector: str, measured: str, extra: str, vp: int,
            mode: str = "static", required: str = "") -> None:
        nk = (check, id(store), page, id(node) if node is not None else selector,
              measured if check != "sideways_scroll" else "")
        key = self.nodes.get(nk)
        if key is not None and key in store:
            got = store[key]
            if vp not in got["viewports"]:
                got["viewports"].append(vp)
            if got["measured"] != measured:
                got.setdefault("measured_at", {})[vp] = measured
            return
        key = (check, page, selector, measured, _mob_desc(node) if node is not None else "", extra)
        self.nodes[nk] = key
        got = store.get(key)
        if got is not None:
            got["count"] += 1
            if vp not in got["viewports"]:
                got["viewports"].append(vp)
            return
        store[key] = {"check": check, "file": page, "selector": selector, "measured": measured,
                      "required": required, "element": ("<" + _mob_desc(node) + ">") if node is not None else "",
                      "extra": extra, "mode": mode, "viewports": [vp], "count": 1}


def _mob_line(f: dict, warn: bool = False) -> str:
    """file | selector | measured | static (or rendered); element; extra | at W[,W]px"""
    views = ",".join(str(v) for v in sorted(f.get("viewports", []))) + "px"
    head = f["measured"]
    tail = f["mode"]
    if f.get("element"):
        tail += "; " + f["element"]
    if f.get("extra"):
        tail += "; " + f["extra"]
    if f.get("measured_at"):
        tail += "; also " + "; ".join(f["measured_at"][v] for v in sorted(f["measured_at"]))
    if f.get("count", 1) > 1:
        tail += f" (x{f['count']})"
    return " | ".join([f["file"], f["selector"], head, tail, f"at {views}"])


def _mob_label(node: _Node, *props: str) -> str:
    box = _tap_box(node)
    labs = []
    for p in props:
        if p in box and box[p][1] not in labs and not box[p][1].endswith("[browser default]"):
            labs.append(box[p][1])
    return " + ".join(labs[:3]) if labs else _mob_desc(node)


def _mob_text_iv(text: str, size: float, mono: bool):
    g = _MOB_MONO_GLYPH if mono else _TAP_GLYPH
    return (len(text) * g[0] * size, len(text) * g[1] * size)


def _mob_scroll_page(page: str, order: list[_Node], hidden: dict, ctx: _Ctx, acc: _MobAcc, first: bool) -> None:
    W = ctx.w
    vp = int(W)
    geo = _MobGeo(ctx)
    root_clip = _mob_root_clip(order)
    clip_note = f"; {root_clip} clips it (content cut off)" if root_clip else ""
    limit = W + 0.5

    def fail(node, selector, extent, extra):
        acc.rec(acc.fails, "sideways_scroll", page, node, selector,
                f"measured width {_fmt_px(extent)} > viewport {vp}px", extra + clip_note, vp,
                required=f"<= {vp}px")

    def warn(node, selector, lo, hi, extra):
        acc.rec(acc.warns, "sideways_scroll", page, node, selector,
                f"not measurable: width {_fmt_px(lo)}-{_fmt_px(hi) if hi != _INF else '?'} straddles viewport {vp}px",
                extra, vp, required=f"<= {vp}px")

    for node in order:
        if hidden.get(id(node)) is not None or node.tag in ("html", "head") or \
                (node.tag in _SKIP_TAGS and node.tag != "svg"):
            continue
        cs = node.cs
        if cs is None or cs.get("srhide"):
            continue
        if first:
            acc.checked += 1
        contained = _mob_contained(node)
        if contained:
            continue
        parent = node.parent
        try:
            pleft, pinner, _, _ = geo.frame(parent) if parent is not None and parent.tag != "#doc" else (0.0, W, 0.0, W)
        except RecursionError:
            continue
        display = _tap_raw_display(node)
        pos = _tap_boxval(node, "position") or "static"
        if pos == "fixed":
            pleft, pinner = 0.0, W
        size = cs.get("size") or 16.0
        # 1) resolved width / min-width / negative right margin
        if display != "inline" or node.tag in _MOB_REPLACED:
            ml = _mob_num(_mob_px(node, "margin-left", ctx, pinner))
            mr = _mob_num(_mob_px(node, "margin-right", ctx, pinner))
            if node.tag == "body" and _tap_boxval(node, "margin-left") is None and _tap_boxval(node, "margin") is None:
                ml = mr = 8.0
            if pos in ("absolute", "fixed"):
                lv = _mob_px(node, "left", ctx, pinner)
                if isinstance(lv, float):
                    ml += lv
            left = pleft + ml
            box_sizing = _tap_boxval(node, "box-sizing") or "content-box"
            padl, padr = geo._pad_border(node, pinner)
            extra = 0.0 if box_sizing == "border-box" else padl + padr
            w = _mob_px(node, "width", ctx, pinner)
            mn = _mob_px(node, "min-width", ctx, pinner)
            mx = _mob_px(node, "max-width", ctx, pinner)
            mx_set = _tap_boxval(node, "max-width") not in (None, "none", "initial", "unset", "revert")
            shrinks = _mob_flex_row_shrinks(node)
            raw_w = _tap_boxval(node, "width") or ""
            raw_mn = _tap_boxval(node, "min-width") or ""
            if "%" in raw_w and isinstance(w, float) and w <= pinner + 0.5:
                w = None  # a percentage of a container we only approximate: judged by its container
            if "%" in raw_mn and isinstance(mn, float) and mn <= pinner + 0.5:
                mn = None
            tf = _tap_boxval(node, "transform") or ""
            if (pos in ("absolute", "fixed") and _tap_boxval(node, "left") is None and
                    _tap_boxval(node, "right") is not None) or "translate" in tf:
                w = mn = None  # right-anchored or translated: x position not modelled
            bw = None
            src = ()
            if isinstance(w, float) and not shrinks:
                bw, src = w + extra, ("width",)
                if isinstance(mx, float):
                    bw = min(bw, mx + extra)
                    src = ("width", "max-width")
                elif mx == "?":
                    bw = None  # capped by a value we cannot resolve
            if node.tag in _MOB_REPLACED and _tap_boxval(node, "width") is None:
                aw = _tap_num_attr(node.attrs.get("width"))
                if aw is not None and not mx_set:
                    bw, src = aw, ()
                elif aw is None and node.tag == "img" and not mx_set and first:
                    acc.rec(acc.warns, "sideways_scroll", page, node, f'img[src="{node.attrs.get("src", "")[:60]}"]',
                            "not measurable: img has no width attribute and no max-width; intrinsic width unknown "
                            "statically", "add max-width:100% or width/height attributes", vp, required=f"<= {vp}px")
            if isinstance(mn, float) and mn + extra > (bw or 0.0):
                bw, src = mn + extra, ("min-width",)
            if bw is not None:
                extent = left + bw
                if extent > limit:
                    sel = _mob_label(node, *src) if src else (
                        f'{node.tag}[width="{node.attrs.get("width")}"] (no max-width)')
                    fail(node, sel, extent, f"box {_fmt_px(bw)} + left offset {_fmt_px(left)}")
                    continue
            elif w == "?" or mn == "?":
                acc.rec(acc.warns, "sideways_scroll", page, node, _mob_label(node, "width", "min-width"),
                        "not measurable: width/min-width value not resolvable statically", "", vp,
                        required=f"<= {vp}px")
            # negative right margin on a filling block
            if mr < 0 and bw is None and display in ("block", "flex", "grid", "list-item", "flow-root"):
                extent = pleft + pinner - mr
                gutter_right = W - (pleft + pinner)
                if -mr > gutter_right + 0.5:
                    fail(node, _mob_label(node, "margin-right", "margin"), extent,
                         f"margin-right {_fmt_px(mr)} beyond the {_fmt_px(max(gutter_right, 0.0))} right gutter")
                    continue
        # 2) wide table (min-content estimate)
        if node.tag == "table" and (_tap_boxval(node, "table-layout") or "auto") != "fixed":
            cols: dict[int, tuple[float, float]] = {}
            for tr in _iter_nodes(node):
                if tr.tag != "tr" or tr is node:
                    continue
                owner = next((a for a in _mob_ancestors(tr) if a.tag == "table"), None)
                if owner is not node:
                    continue
                col = 0
                for cell in tr.children:
                    if cell.tag not in ("td", "th") or cell.cs is None:
                        continue
                    words = re.findall(r"\S+", _tap_text(cell)) or [""]
                    longest = max(words, key=len)
                    csz = cell.cs.get("size") or size
                    lo, hi = _mob_text_iv(longest, csz, _mob_mono(cell))
                    pl, pr = geo._pad_border(cell, pinner)
                    pad = pl + pr if (pl + pr) > 0 else 2.0
                    span = max(1, int(_tap_num_attr(cell.attrs.get("colspan")) or 1))
                    lo, hi = (lo + pad) / span, (hi + pad) / span
                    for k in range(span):
                        a, b = cols.get(col + k, (0.0, 0.0))
                        cols[col + k] = (max(a, lo), max(b, hi))
                    col += span
            if cols:
                spacing = 2.0 * (len(cols) + 1)
                lo = pleft + sum(a for a, _ in cols.values()) + spacing
                hi = pleft + sum(b for _, b in cols.values()) + spacing
                if lo > limit:
                    fail(node, f"table ({len(cols)} columns, min-content estimate)", lo,
                         "no overflow-x:auto wrapper; longest word per column")
                elif hi > limit:
                    warn(node, f"table ({len(cols)} columns)", lo, hi, "wrap it in an overflow-x:auto container")
            continue
        # 3) pre / nowrap text, declared on this element
        ws = _mob_white_space(node)
        declares = "white-space" in _tap_box(node) or node.tag == "pre"
        if declares and ws in ("pre", "nowrap") and not _mob_contained(node, include_self=True):
            if not _tap_has_block_kids(node):
                text = _tap_text(node) if ws == "nowrap" else max(_mob_raw_text(node).split("\n"), key=len)
                text = text.strip() if ws == "nowrap" else text.rstrip()
                if text:
                    lo, hi = _mob_text_iv(text, size, _mob_mono(node))
                    cleft = geo.frame(node)[0] if display != "inline" else pleft
                    shown = text if len(text) <= 30 else text[:27] + "..."
                    if cleft + lo > limit:
                        fail(node, _mob_label(node, "white-space") if node.tag != "pre" else "pre",
                             cleft + lo, f"white-space:{ws} line of {len(text)} chars \"{shown}\"")
                        continue
                    if cleft + hi > limit:
                        warn(node, _mob_label(node, "white-space") if node.tag != "pre" else "pre", cleft + lo, cleft + hi,
                             f"white-space:{ws} line of {len(text)} chars \"{shown}\"")
                        continue
        # 4) long unbreakable word in normal text
        if ws not in ("pre", "nowrap") and node.texts and not _mob_breaks_words(node):
            words = [w_ for w_ in re.findall(r"\S+", " ".join(node.texts)) if len(w_) >= MOBILE_WORD_MIN_CHARS]
            if words:
                longest = max(words, key=len)
                lo, hi = _mob_text_iv(longest, size, _mob_mono(node))
                cleft = geo.frame(node)[0] if display != "inline" else pleft
                shown = longest if len(longest) <= 30 else longest[:27] + "..."
                if cleft + lo > limit:
                    fail(node, _mob_desc(node) + " text", cleft + lo,
                         f"unbreakable word of {len(longest)} chars \"{shown}\" (no overflow-wrap)")
                elif cleft + hi > limit:
                    warn(node, _mob_desc(node) + " text", cleft + lo, cleft + hi,
                         f"unbreakable word of {len(longest)} chars \"{shown}\"; add overflow-wrap:anywhere")


# ----- drawer --------------------------------------------------------------


def _mob_scripts(root: _Node, page: Path) -> tuple[str, list[str]]:
    """Inline and local script text, plus notes for scripts that could not be read."""
    texts: list[str] = []
    notes: list[str] = []
    for node in _iter_nodes(root):
        if node.tag != "script":
            continue
        typ = node.attrs.get("type", "").strip().lower()
        if typ and ("json" in typ or typ in ("text/template", "text/x-template")):
            continue
        src = node.attrs.get("src", "").strip()
        if not src:
            texts.append("".join(node.raw))
            continue
        local = src.split("#", 1)[0].split("?", 1)[0]
        if src.lower().startswith(("http:", "https:", "//", "data:")) or ":" in local.split("/", 1)[0]:
            notes.append(f"remote script not read: {src[:60]}")
            continue
        try:
            texts.append((page.parent / unquote(local).lstrip("/")).read_text(encoding="utf-8", errors="replace"))
        except OSError:
            notes.append(f"script not found: {src[:60]}")
    return "\n".join(texts), notes


def _mob_links(node: _Node) -> list[_Node]:
    return [n for n in _iter_nodes(node) if n is not node and
            ((n.tag == "a" and "href" in n.attrs) or n.attrs.get("role", "").lower() in ("link", "menuitem"))]


def _mob_primary_nav(order: list[_Node]):
    navs = [n for n in order if n.tag == "nav" or n.attrs.get("role", "").lower() == "navigation"]
    navs = [n for n in navs if _mob_links(n)]
    if not navs:
        return None
    for n in navs:
        if any(a.tag == "header" or a.attrs.get("role", "").lower() == "banner" for a in _mob_ancestors(n)):
            return n
    return navs[0]


def _mob_ids(order: list[_Node]) -> dict:
    out = {}
    for n in order:
        ident = n.attrs.get("id")
        if ident and ident not in out:
            out[ident] = n
    return out


def _mob_contains(outer: _Node, inner: _Node) -> bool:
    return outer is inner or any(a is outer for a in _mob_ancestors(inner))


def _mob_find_toggle(order: list[_Node], nav: _Node, ids: dict):
    """The control that opens the primary nav: aria-controls into the nav first, then menu-ish words."""
    for n in order:
        if _mob_contains(nav, n):
            continue
        controls = n.attrs.get("aria-controls", "").split()
        for c in controls:
            target = ids.get(c)
            if target is not None and not _mob_contains(target, n) and \
                    (_mob_contains(target, nav) or _mob_contains(nav, target)):
                return n
    for n in order:
        if _mob_contains(nav, n):
            continue
        interactive = n.tag in ("button", "label") or n.attrs.get("role", "").lower() == "button" \
            or "aria-expanded" in n.attrs or (n.tag == "input" and n.attrs.get("type", "").lower() == "checkbox")
        if not interactive:
            continue
        words = " ".join((n.attrs.get("aria-label", ""), n.attrs.get("class", ""), n.attrs.get("id", ""),
                          n.attrs.get("title", ""), " ".join(" ".join(n.texts).split())[:30]))
        if _MOB_TOGGLE_WORDS.search(words):
            return n
    return None


def _mob_name(node: _Node, ids: dict) -> str:
    for ref in node.attrs.get("aria-labelledby", "").split():
        target = ids.get(ref)
        if target is not None and _tap_text(target):
            return _tap_text(target)
    name = node.attrs.get("aria-label", "").strip()
    if name:
        return name
    text = _tap_text(node)
    if text:
        return text
    for n in _iter_nodes(node):
        if n.tag == "title" and "".join(n.texts).strip():
            return "".join(n.texts).strip()
        if n.tag == "img" and n.attrs.get("alt", "").strip():
            return n.attrs["alt"].strip()
    return node.attrs.get("title", "").strip()


def _mob_offscreen(node: _Node) -> bool:
    for n in [node] + list(_mob_ancestors(node)):
        t = _tap_boxval(n, "transform")
        if t and _MOB_OFFSCREEN_RE.search(t):
            return True
    return False


class _MobState:
    """Temporarily applies the open state (classes, attributes) to nodes."""

    def __init__(self, changes: list):
        self.changes = changes
        self.saved: list = []

    def __enter__(self):
        for node, kind, value in self.changes:
            self.saved.append((node, dict(node.attrs), list(node.classes)))
            if kind == "class":
                if value not in node.classes:
                    node.classes.append(value)
                    node.attrs["class"] = " ".join(node.classes)
            elif kind == "set":
                node.attrs[value[0]] = value[1]
            elif kind == "del":
                node.attrs.pop(value, None)
        return self

    def __exit__(self, *exc):
        for node, attrs, classes in reversed(self.saved):
            node.attrs.clear()
            node.attrs.update(attrs)
            node.classes[:] = classes
        return False


def _mob_drawer_page(page: Path, root: _Node, author_items: list, acc: _MobAcc, views: tuple,
                     exempt: set) -> dict:
    """Judges the drawer at every phone width. Returns a per-page summary."""
    name = page.name
    js, js_notes = _mob_scripts(root, page)
    summary = {"nav": None, "links": 0, "toggle": None, "status": "skip", "notes": js_notes}
    for number, (w, h) in enumerate(views):
        ctx, order, hidden = _mob_cascade(root, author_items, w, h)
        vp = w
        nav = _mob_primary_nav(order)
        if nav is None:
            if number == 0:
                summary["notes"].append(f"{name}: no <nav> or role=navigation with links: drawer gate not-run")
            return summary
        ids = _mob_ids(order)
        links = _mob_links(nav)
        summary["nav"], summary["links"] = _mob_desc(nav), len(links)
        if number == 0:
            summary["status"] = "nav"
        nav_sel = _mob_desc(nav)
        toggle = _mob_find_toggle(order, nav, ids)
        nav_hidden = hidden.get(id(nav)) is not None or _mob_offscreen(nav)
        tog_visible = toggle is not None and hidden.get(id(toggle)) is None and not (toggle.cs or {}).get("srhide")

        def fail(node, selector, measured, extra=""):
            acc.rec(acc.fails, "mobile_nav_drawer", name, node, selector, measured, extra, vp)

        def warn(node, selector, measured, extra=""):
            acc.rec(acc.warns, "mobile_nav_drawer", name, node, selector, measured, extra, vp)

        if not tog_visible:
            if nav_hidden:
                fail(nav, nav_sel, f"primary nav ({len(links)} links) hidden "
                     f"({_mob_hide_label(hidden.get(id(nav)))}) and no visible menu toggle: links unreachable")
            elif len(links) > MOBILE_NAV_INLINE_MAX:
                fail(nav, nav_sel, f"{len(links)} nav links shown inline, no menu toggle "
                     f"(needs a toggle above {MOBILE_NAV_INLINE_MAX} links)")
            elif number == 0:
                summary["status"] = "inline"
            continue
        exempt.add(id(toggle))
        summary["toggle"] = _mob_desc(toggle)
        tsel = _mob_desc(toggle)
        if toggle.tag != "button" and toggle.attrs.get("role", "").lower() != "button":
            fail(toggle, tsel, f"menu toggle is <{toggle.tag}>, not a button (needs <button> or role=button)")
        expanded = toggle.attrs.get("aria-expanded")
        if expanded is None:
            fail(toggle, tsel, "no aria-expanded on the menu toggle (needs aria-expanded=\"false\" when closed)")
        controls = toggle.attrs.get("aria-controls", "").split()
        drawer = None
        if not controls:
            fail(toggle, tsel, "no aria-controls on the menu toggle (needs the drawer id)")
        else:
            missing = [c for c in controls if c not in ids]
            if missing:
                fail(toggle, tsel, f"aria-controls=\"{' '.join(controls)}\" names no element with id "
                     f"{', '.join(missing)}")
            drawer = next((ids[c] for c in controls if c in ids), None)
        if not _mob_name(toggle, ids):
            fail(toggle, tsel, "menu toggle has no accessible name (needs aria-label, text or aria-labelledby)")
        m = _tap_measure(toggle, ctx)
        if "error" in m:
            warn(toggle, tsel, "not measurable: toggle size " + m["error"])
        else:
            (wl, wh), (hl, hh) = m["w"], m["h"]
            measured = f"{_tap_fmt(m['w'])}x{_tap_fmt(m['h'])}px"
            if wh < TAP_MIN_PX - 0.005 or hh < TAP_MIN_PX - 0.005:
                fail(toggle, _tap_selector(m, toggle, "wh"), f"menu toggle measured {measured} (needs >= 44px)")
            elif wl < TAP_MIN_PX - 0.005 or hl < TAP_MIN_PX - 0.005:
                warn(toggle, tsel, f"not measurable: menu toggle {measured}, no guaranteed 44px")
        if drawer is None:
            drawer = nav  # judge the nav itself when aria-controls is missing or broken
        exempt.add(id(drawer))
        dsel = _mob_desc(drawer)
        if not (_mob_contains(drawer, nav) or _mob_contains(nav, drawer) or
                any(_mob_contains(drawer, a) for a in links)):
            fail(drawer, dsel, f"drawer #{drawer.attrs.get('id', '?')} does not hold the primary nav links "
                 f"({nav_sel})")
        d_hidden = hidden.get(id(drawer)) is not None or _mob_offscreen(drawer)
        if not d_hidden:
            fail(drawer, dsel, "drawer shown by default (needs hidden until the toggle opens it)")
        elif expanded is not None and expanded.strip().lower() == "true":
            fail(toggle, tsel, "aria-expanded=\"true\" while the drawer is hidden (needs \"false\")")
        # reachable: simulate the open state from the page's own script
        native = drawer.tag == "dialog" or "popover" in drawer.attrs or \
            toggle.attrs.get("popovertarget", "") == drawer.attrs.get("id", "\0")
        classes = sorted(set(m_.group(2) for m_ in _MOB_CLASS_RE.finditer(js)))
        unhide = bool(_MOB_UNHIDE_RE.search(js))
        sets_expanded = bool(_MOB_EXPANDED_RE.search(js))
        opened = None
        if d_hidden and not native:
            if not js.strip() and not js_notes:
                fail(drawer, dsel, "drawer has no way to open: no script, no native dialog/popover")
            elif not (classes or unhide):
                warn(drawer, dsel, "not measurable: open state not provable statically (no classList/hidden "
                     "change found in readable script" + ("; " + "; ".join(js_notes[:2]) if js_notes else "") + ")")
            else:
                changes = [(toggle, "set", ("aria-expanded", "true"))]
                if unhide:
                    changes.append((drawer, "del", "hidden"))
                targets = [drawer, toggle] + [a for a in _mob_ancestors(drawer)] + list(_mob_ancestors(toggle))
                seen: set = set()
                for node in targets:
                    if id(node) in seen:
                        continue
                    seen.add(id(node))
                    for c in classes:
                        changes.append((node, "class", c))
                with _MobState(changes):
                    _, order2, hidden2 = _mob_cascade(root, author_items, w, h)
                    open_ok = hidden2.get(id(drawer)) is None and not _mob_offscreen(drawer)
                    links_ok = all(hidden2.get(id(a)) is None for a in links if _mob_contains(drawer, a))
                    tog_open_visible = hidden2.get(id(toggle)) is None
                if not open_ok:
                    fail(drawer, dsel, f"opening (classes {', '.join('.' + c for c in classes) or 'none'}"
                         f"{', hidden removed' if unhide else ''}) leaves the drawer hidden")
                elif not links_ok:
                    fail(drawer, dsel, "drawer opens but its links stay hidden")
                opened = open_ok and links_ok
                used = classes
                if opened and len(classes) > 1:  # name only the class(es) that open it on their own
                    alone = []
                    for c in classes:
                        one = [ch for ch in changes if ch[1] != "class" or ch[2] == c]
                        with _MobState(one):
                            _, _, h3 = _mob_cascade(root, author_items, w, h)
                            if h3.get(id(drawer)) is None and not _mob_offscreen(drawer):
                                alone.append(c)
                    used = alone or classes
                summary["open_by"] = ", ".join("." + c for c in used) + (" hidden removed" if unhide else "")
                # close mechanism
                close = []
                if (_MOB_TOGGLE_RE.search(js) or (sets_expanded and "false" in js)) and tog_open_visible \
                        and not _mob_contains(drawer, toggle):
                    close.append("toggle flips back and stays visible")
                inner_close = [n for n in _iter_nodes(drawer) if n is not drawer and (n.tag == "button" or
                               n.attrs.get("role", "").lower() == "button") and
                               (_MOB_CLOSE_WORDS.search(_mob_name(n, ids) + " " + n.attrs.get("class", "")) or
                                drawer.attrs.get("id", "\0") in n.attrs.get("aria-controls", "").split())]
                if inner_close:
                    close.append("close button " + _mob_desc(inner_close[0]))
                if _MOB_ESCAPE_RE.search(js):
                    close.append("Escape key")
                if not close:
                    fail(drawer, dsel, "no close mechanism (needs a toggle that flips back, a close "
                         "button inside the drawer, or Escape)")
                summary["close"] = "; ".join(close)
        elif native:
            summary["close"] = "native dialog/popover"
            opened = True
        if number == 0:
            summary["status"] = "drawer" if opened else ("drawer-unproven" if opened is None else "drawer-broken")
    return summary


# ----- visibility inventory ------------------------------------------------


def _mob_has_content(node: _Node) -> bool:
    if _tap_text(node):
        return True
    return any(n.tag in ("img", "video", "picture", "a", "button", "input", "iframe") for n in _iter_nodes(node))


def _mob_visibility_page(page: Path, root: _Node, author_items: list, acc: _MobAcc, views: tuple,
                         exempt: set) -> None:
    name = page.name
    dw, dh = DESKTOP_VIEWPORT
    _, d_order, d_hidden = _mob_cascade(root, author_items, dw, dh)
    d_label = {id(n): _mob_hide_label(n) for n in d_order if d_hidden.get(id(n)) is n}

    def under_exempt(node):
        return id(node) in exempt or any(id(a) in exempt for a in _mob_ancestors(node))

    for w, h in views:
        _, order, hidden = _mob_cascade(root, author_items, w, h)
        for node in order:
            if node.tag in _SKIP_TAGS or node.tag in ("html", "head", "body"):
                continue
            hm = hidden.get(id(node)) is not None
            hd = d_hidden.get(id(node)) is not None
            primary = node.tag == "h1" or node.tag == "main" or node.attrs.get("role", "").lower() == "main"
            if primary:
                if hm:
                    acc.rec(acc.fails, "mobile_visibility", name, node, _mob_desc(node),
                            f"primary content {_mob_desc(node)} hidden "
                            f"({_mob_hide_label(hidden.get(id(node)))})", "h1 and main must show on phones", w)
            if hm == hd:
                continue
            parent = node.parent
            if parent is not None and parent.tag not in ("#doc",):
                phm = hidden.get(id(parent)) is not None
                phd = d_hidden.get(id(parent)) is not None
                if phm != phd:
                    continue  # report only the topmost element whose visibility changes
            if hd and not hm:
                acc.rec(acc.inventory, "mobile_visibility", name, node, _mob_desc(node),
                        f"shown only at phone widths (hidden at {dw}px: {d_label.get(id(node), 'by an ancestor')})",
                        "mobile-only element", w)
            else:
                label = _mob_hide_label(hidden.get(id(node)))
                if under_exempt(node) or not _mob_has_content(node):
                    acc.rec(acc.inventory, "mobile_visibility", name, node, _mob_desc(node),
                            f"hidden at phone widths ({label}), shown at {dw}px",
                            "menu drawer/toggle (expected)" if under_exempt(node) else "no text, link or image", w)
                elif not primary:
                    text = _tap_text(node)
                    shown = text if len(text) <= 30 else text[:27] + "..."
                    acc.rec(acc.warns, "mobile_visibility", name, node, _mob_desc(node),
                            f"content hidden at phone widths ({label}), shown at {dw}px",
                            f"\"{shown}\": phone users lose it", w)


# ----- capture evidence (--mobile-spec) ------------------------------------


def load_mobile_spec(path) -> list[dict]:
    """Reads a mobile_capture.py patterns.json (file, or a folder holding patterns*.json or mobile/patterns.json).

    Returns one dict per captured profile: width, overflowX, scrollWidth, offenders, toggles, drawerOpened,
    tapsUnder44, taps, url, error, source. Raises OSError/ValueError on unreadable input.
    """
    p = Path(path)
    files: list[Path] = []
    if p.is_dir():
        for cand in ("patterns.json", "mobile/patterns.json"):
            if (p / cand).is_file():
                files.append(p / cand)
        files += sorted(x for x in p.glob("patterns_*.json"))
        files += sorted(x for x in p.glob("mobile/patterns_*.json"))
    elif p.is_file():
        files = [p]
    if not files:
        raise OSError(f"no patterns.json at {p}")
    out: list[dict] = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        if isinstance(data, dict) and isinstance(data.get("profiles"), dict):
            items = [(k, v) for k, v in data["profiles"].items() if isinstance(v, dict) and k != "diff"]
            url = data.get("url", "")
        else:
            items = [(data.get("profile", f.stem), data)]
            url = data.get("url", "")
        for prof, d in items:
            ov = d.get("overflow") if isinstance(d.get("overflow"), dict) else {}
            taps = d.get("tapTargets") if isinstance(d.get("tapTargets"), dict) else {}
            toggles = d.get("toggles") if d.get("toggles") is not None else d.get("menuToggles") or []
            drawer = d.get("drawerOpened")
            if drawer is None and isinstance(d.get("drawer"), dict):
                drawer = d["drawer"].get("opened", d["drawer"].get("ok"))
            width = d.get("innerWidth") or (d.get("viewport") or {}).get("width") or ov.get("innerWidth")
            out.append({
                "profile": prof, "width": width, "url": d.get("url") or url, "error": d.get("error"),
                "overflowX": d.get("overflowX", ov.get("overflowX")),
                "scrollWidth": d.get("scrollWidth", ov.get("scrollWidth")),
                "offenders": ov.get("offenders") or [],
                "toggles": toggles, "drawerOpened": drawer,
                "tapsUnder44": d.get("tapsUnder44", taps.get("under44")),
                "taps": d.get("taps", taps.get("visible")), "source": f.name,
            })
    return out


def _mobile_spec_row(rep: "Report", spec_path, static_toggle: bool | None) -> None:
    try:
        profiles = load_mobile_spec(spec_path)
    except (OSError, ValueError) as exc:
        rep.add("mobile_spec", "SKIP", f"not-run: --mobile-spec unreadable: {exc}", failures=[])
        return
    phones = [p for p in profiles if isinstance(p.get("width"), (int, float)) and p["width"] <= 480]
    acc = _MobAcc()
    ran = 0
    for p in phones:
        w = int(p["width"])
        src = p["source"]
        mode = "rendered (capture" + (f" of {p['url']}" if p.get("url") else "") + ")"
        if p.get("error"):
            acc.rec(acc.warns, "mobile_spec", src, None, p["profile"], f"not measurable: capture error {str(p['error'])[:80]}",
                    "", w, mode=mode)
            continue
        ran += 1
        if p.get("overflowX"):
            offs = ", ".join(str(o.get("el", o) if isinstance(o, dict) else o) for o in p["offenders"][:3])
            acc.rec(acc.fails, "mobile_spec", src, None, "documentElement" + (f" (offenders: {offs})" if offs else ""),
                    f"measured width {p.get('scrollWidth')}px > viewport {w}px", "sideways scroll in the render", w,
                    mode=mode)
        d = p.get("drawerOpened")
        if isinstance(d, str) and d.startswith("fail"):
            acc.rec(acc.fails, "mobile_spec", src, None, "menu toggle", f"tap on the menu toggle failed ({d})", "", w,
                    mode=mode)
        n = p.get("tapsUnder44")
        if isinstance(n, int) and n > 0:
            acc.rec(acc.warns, "mobile_spec", src, None, "tap targets",
                    f"{n} of {p.get('taps')} visible tap targets under 44px in the capture",
                    "capture does not apply the WCAG 2.5.8 inline-link exemption; static tap_target rules", w,
                    mode=mode)
        if p.get("toggles") and static_toggle is False:
            acc.rec(acc.warns, "mobile_spec", src, None, "menu toggle",
                    "capture saw a menu toggle but the static scan found none", "is the capture of this build?", w,
                    mode=mode)
    fails = sorted(acc.fails.values(), key=lambda r: (r["file"], r["selector"]))
    warns = sorted(acc.warns.values(), key=lambda r: (r["file"], r["selector"]))
    for r in fails + warns:
        r["viewports"].sort()
    head = f"rendered capture {Path(spec_path).name}: {ran} phone profile(s)"
    if not ran:
        rep.add("mobile_spec", "SKIP", f"not-run: {head}; no usable phone-width profile", failures=[],
                unmeasured=warns)
    elif fails:
        rep.add("mobile_spec", "FAIL", head + "; " + "; ".join(f"{f['selector']} {f['measured']}" for f in fails[:4]),
                failures=fails, unmeasured=warns)
    elif warns:
        rep.add("mobile_spec", "WARN", head + f"; {len(warns)} warning(s)", failures=[], unmeasured=warns)
    else:
        rep.add("mobile_spec", "PASS", head + "; no overflow, toggle opened", failures=[])


# ----- scan + rows ------------------------------------------------------------


def mobile_scan(pages: list[Path], viewports: tuple | None = None) -> dict:
    """Runs sideways_scroll, mobile_nav_drawer and mobile_visibility over HTML pages.

    sideways_scroll is judged at phones + 1280px desktop (overflow 360+1280);
    drawer/visibility stay phone-widths with a 1280px baseline for inventory.
    """
    views = tuple(viewports or MOBILE_VIEWPORTS)
    scroll_views = tuple(dict.fromkeys(list(views) + [DESKTOP_VIEWPORT]))
    scroll, drawer, vis = _MobAcc(), _MobAcc(), _MobAcc()
    summaries = []
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        root = _build_dom(html)
        sheet_acc = _TypoAcc()
        author_items = _stylesheet_items(root, page, sheet_acc)
        scroll.notes.extend(sheet_acc.notes)
        for number, (w, h) in enumerate(scroll_views):
            ctx, order, hidden = _mob_cascade(root, author_items, w, h)
            _mob_scroll_page(page.name, order, hidden, ctx, scroll, number == 0)
        scroll.pages += 1
        exempt: set = set()
        summary = _mob_drawer_page(page, root, author_items, drawer, views, exempt)
        summary["file"] = page.name
        summaries.append(summary)
        drawer.pages += 1
        _mob_visibility_page(page, root, author_items, vis, views, exempt)
        vis.pages += 1

    def done(store):
        rows = sorted(store.values(), key=lambda r: (r["file"], r["selector"], r["measured"]))
        for r in rows:
            r["viewports"].sort()
        return rows
    return {
        "views": views,
        "sideways_scroll": {"fails": done(scroll.fails), "warns": done(scroll.warns), "pages": scroll.pages,
                            "checked": scroll.checked, "notes": scroll.notes},
        "mobile_nav_drawer": {"fails": done(drawer.fails), "warns": done(drawer.warns), "pages": drawer.pages,
                              "summaries": summaries},
        "mobile_visibility": {"fails": done(vis.fails), "warns": done(vis.warns), "inventory": done(vis.inventory),
                              "pages": vis.pages},
    }


def _short_mob(f: dict) -> str:
    return f"{f['file']}: {f['selector']} {f['measured']}"


def _mobile_rows(rep: "Report", pages: list[Path], mobile_spec=None) -> None:
    names = ("sideways_scroll", "mobile_nav_drawer", "mobile_visibility")
    try:
        scan = mobile_scan(pages)
    except Exception as exc:  # fail closed: a checker bug must not read as a pass
        for name in names:
            rep.add(name, "FAIL", f"static; checker error: {type(exc).__name__}: {exc}", failures=[])
        return
    at = "/".join(str(w) for w, _ in scan["views"]) + "px"

    def emit(name, data, pass_detail, skip=None, inventory=None):
        fails, warns = data["fails"], data["warns"]
        if fails:
            shown = "; ".join(_short_mob(f) for f in fails[:4])
            extra = f" (+{len(fails) - 4} more)" if len(fails) > 4 else ""
            rep.add(name, "FAIL", f"static at {at}; " + shown + extra, failures=fails, unmeasured=warns,
                    inventory=inventory)
        elif skip:
            rep.add(name, "SKIP", skip, failures=[], unmeasured=warns, inventory=inventory)
        elif warns:
            rep.add(name, "WARN", f"static at {at}; {len(warns)} item(s) not measurable or to review (never a pass); "
                    + pass_detail, failures=[], unmeasured=warns, inventory=inventory)
        else:
            rep.add(name, "PASS", f"static at {at}; " + pass_detail, failures=[], inventory=inventory)

    s = scan["sideways_scroll"]
    note = ("; " + "; ".join(s["notes"][:2])) if s["notes"] else ""
    emit("sideways_scroll", s, f"{s['checked']} element(s) on {s['pages']} page(s), none wider than the viewport"
         + note)
    d = scan["mobile_nav_drawer"]
    sums = d["summaries"]
    statuses = [x["status"] for x in sums]
    bits = []
    for x in sums:
        if x["nav"] is None:
            bits.append(f"{x['file']}: no nav")
        elif x["toggle"]:
            bits.append(f"{x['file']}: {x['links']} links in {x['nav']}, toggle {x['toggle']}"
                        + (f", opens by {x['open_by'].strip()}" if x.get("open_by") else "")
                        + (f", closes by {x['close']}" if x.get("close") else ""))
        else:
            bits.append(f"{x['file']}: {x['links']} links shown inline (<= {MOBILE_NAV_INLINE_MAX}, no toggle needed)")
    skip = None
    if sums and all(st == "skip" for st in statuses):
        skip = "not-run: no <nav> or role=navigation with links on any page; " + "; ".join(
            n for x in sums for n in x["notes"][:1])
    emit("mobile_nav_drawer", d, "; ".join(bits[:4]) + (f" (+{len(bits) - 4} more)" if len(bits) > 4 else ""),
         skip=skip)
    v = scan["mobile_visibility"]
    inv = v["inventory"]
    mob_only = [i for i in inv if i["measured"].startswith("shown only")]
    hid = [i for i in inv if not i["measured"].startswith("shown only")]
    emit("mobile_visibility", v, f"h1 and main shown; inventory: {len(mob_only)} mobile-only element(s), "
         f"{len(hid)} hidden on phones without content loss (drawer/toggle or empty)", inventory=inv)
    if mobile_spec:
        static_toggle = None
        if sums:
            static_toggle = any(x["toggle"] for x in sums)
        try:
            _mobile_spec_row(rep, mobile_spec, static_toggle)
        except Exception as exc:  # fail closed
            rep.add("mobile_spec", "FAIL", f"rendered; checker error: {type(exc).__name__}: {exc}", failures=[])



# ---------------------------------------------------------------------------
# SEO-research rows (static-only subset of seo-research/*.md, D1/D6 scope).
# Google link/SEO rules (google.md G-LINK/G-SEO/G-CRW) + schema.org required
# props (schema.md: BreadcrumbList >= 2 items, LocalBusiness name+address,
# HowTo deprecated, FAQPage retired and owned by faq_schema) + high-signal
# ahrefs/moz/stox rules (orphans, depth, nofollow misuse, sitemap parity,
# plan-vs-render links). Lab-only rules (LCP/INP/CLS measurement, SERP or
# traffic joins, GSC field data) are NOT static and stay out. QAPage intent
# and keyword-stuffing need judgement and stay out too. Numeric cutoffs
# (title 15-70 chars, 300 words, 3 clicks) are practitioner heuristics, never
# Google quotas. Chain detection skips nav/header/footer (menus sit adjacent
# legitimately). Message shape per row: "page: field detail".
# ---------------------------------------------------------------------------
_SEO_TITLE_MIN = 15
_SEO_TITLE_MAX = 70
_SEO_BODY_MIN_WORDS = 300
_SEO_CLICK_MAX = 3
_TITLE_BOILERPLATE = frozenset((
    "home", "untitled", "page", "welcome", "index", "homepage", "new page",
))
_GENERIC_ANCHORS = frozenset((
    "click here", "read more", "learn more", "more", "here", "click this",
    "read on", "click this link", "link",
))
_INTERNAL_REL_BAD = frozenset(("nofollow", "sponsored", "ugc"))
_SEO_BARE_URL_RE = re.compile(r"^(?:https?://|www\.)\S+$", re.IGNORECASE)
_SEO_CHAIN_RE = re.compile(r"</a\s*>\s*<a\b", re.IGNORECASE)
_SEO_CHROME_RE = re.compile(
    r"<(?:nav|header|footer)\b.*?</(?:nav|header|footer)\s*>",
    re.IGNORECASE | re.DOTALL,
)
_SEO_LANG_RE = re.compile(r"<html\b([^>]*)>", re.IGNORECASE)
_SEO_H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1\s*>", re.IGNORECASE | re.DOTALL)
_SEO_TITLE_RE = re.compile(
    r"<title\b[^>]*>(.*?)</title\s*>", re.IGNORECASE | re.DOTALL)
_SEO_ANCHOR_RE = re.compile(
    r"<a\b([^>]*)>(.*?)</a\s*>", re.IGNORECASE | re.DOTALL)
_SEO_NOINDEX_RE = re.compile(
    r"<meta\b[^>]*\bname\s*=\s*(?:\"robots\"|'robots')[^>]*>", re.IGNORECASE)
_SEO_LOC_RE = re.compile(r"<loc\b[^>]*>(.*?)</loc\s*>", re.IGNORECASE | re.DOTALL)
_SEO_LD_RE = re.compile(
    r"<script\b[^>]*\btype\s*=\s*(?:\"application/ld\+json\"|'application/ld\+json')"
    r"[^>]*>(.*?)</script\s*>",
    re.IGNORECASE | re.DOTALL,
)
_LB_TYPES = frozenset((
    "LocalBusiness", "Restaurant", "CafeOrCoffeeShop", "Store", "ClothingStore",
    "OnlineStore", "DaySpa", "HealthClub", "Dentist", "Hotel", "FoodEstablishment",
))
_ARTICLE_TYPES = frozenset(("Article", "NewsArticle", "BlogPosting"))


def _seo_collapse(text: str) -> str:
    return " ".join(str(text).split())


def _seo_strip_tags(text: str) -> str:
    return re.sub(r"<[^>]*>", "", text)


def _seo_title(html: str) -> str:
    match = _SEO_TITLE_RE.search(html)
    return _seo_collapse(_seo_strip_tags(match.group(1))) if match else ""


def _seo_description(html: str) -> str:
    for match in re.finditer(r"<meta\b([^>]*)>", html, re.IGNORECASE):
        name = _attr(match.group(1), "name")
        content = _attr(match.group(1), "content")
        if name and name.lower() == "description":
            return _seo_collapse(content or "")
    return ""


def _seo_noindex(html: str) -> bool:
    for match in _SEO_NOINDEX_RE.finditer(html):
        content = _attr(match.group(0), "content")
        if content and "noindex" in content.lower():
            return True
    return False


def _seo_lang(html: str) -> str:
    match = _SEO_LANG_RE.search(html)
    if not match:
        return ""
    return (_attr(match.group(1), "lang") or "").strip()


def _seo_h1_texts(html: str) -> list[str]:
    return [_seo_collapse(_seo_strip_tags(m.group(1))) for m in _SEO_H1_RE.finditer(html)]


def _seo_anchors(html: str) -> list[dict]:
    out: list[dict] = []
    for match in _SEO_ANCHOR_RE.finditer(html):
        attrs, inner = match.group(1), match.group(2)
        alts = re.findall(
            r"<img\b[^>]*\balt\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", inner, re.IGNORECASE)
        out.append({
            "href": _attr(attrs, "href"),
            "seen_href": re.search(r"\bhref\s*=", attrs, re.IGNORECASE) is not None,
            "text": _seo_collapse(_seo_strip_tags(inner)),
            "title": (_attr(attrs, "title") or "").strip(),
            "img_alt": " ".join(
                _seo_collapse(first or second) for first, second in alts).strip(),
            "rel": (_attr(attrs, "rel") or "").lower().split(),
        })
    return out


def _seo_is_external(href: str) -> bool:
    low = href.strip().lower()
    return low.startswith(("http://", "https://", "//", "mailto:", "tel:", "data:"))


def _seo_edge_file(page: Path, href: str) -> str | None:
    """Rendered filename an internal href points at, else None (not a page edge)."""
    target = href.split("#", 1)[0].split("?", 1)[0].strip().replace("\\", "/")
    target = target.lstrip("/")
    if not target or target.startswith("#") or _seo_is_external(target):
        return None
    if target.lower().startswith("javascript:"):
        return None
    cand = page.parent / target
    if cand.suffix.lower() != ".html":
        cand = cand.parent / (cand.name + ".html")
    try:
        return cand.name if cand.is_file() else None
    except OSError:
        return None


def _seo_graph(pages: list[Path]) -> dict[str, set[str]]:
    edges: dict[str, set[str]] = {p.name: set() for p in pages}
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        for link in _seo_anchors(html):
            if link["href"] is None:
                continue
            hit = _seo_edge_file(page, link["href"])
            if hit and hit in edges and hit != page.name:
                edges[page.name].add(hit)
    return edges


def _seo_depths(pages: list[Path], edges: dict[str, set[str]]) -> dict[str, int]:
    names = {p.name for p in pages}
    if not names:
        return {}
    start = "index.html" if "index.html" in names else min(names)
    depths = {start: 0}
    frontier = [start]
    while frontier:
        cur = frontier.pop(0)
        for nxt in sorted(edges.get(cur, ())):
            if nxt not in depths:
                depths[nxt] = depths[cur] + 1
                frontier.append(nxt)
    return depths


def _robots_disallows(site_dir: Path) -> list[str] | None:
    """Disallow paths from User-agent: * groups, or None when no robots.txt."""
    path = site_dir / "robots.txt"
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    found: list[str] = []
    applies = False
    in_agents = True
    for raw_line in text.splitlines():
        bare = raw_line.split("#", 1)[0].strip()
        if not bare:
            continue  # blank lines never end a group; a new User-agent line does
        agent = re.match(r"(?i)^user-agent\s*:\s*(\S+)\s*$", bare)
        if agent:
            if not in_agents:
                applies = False
            in_agents = True
            if agent.group(1).strip() == "*":
                applies = True
            continue
        rule = re.match(r"(?i)^disallow\s*:\s*(\S*)\s*$", bare)
        if rule:
            in_agents = False
            if applies and rule.group(1).strip() not in found:
                found.append(rule.group(1).strip())
            continue
        in_agents = False
    return found


def _sitemap_expected(site_dir: Path) -> tuple[str | None, list[str] | None, dict]:
    """(kind, files, planned): kind in {"json", "xml"}; planned maps file to edges."""
    doc_path = site_dir / "sitemap.json"
    if doc_path.is_file():
        try:
            doc = json.loads(doc_path.read_text(encoding="utf-8", errors="replace"))
        except ValueError:
            return ("json", None, {})
        entries = doc.get("pages") if isinstance(doc, dict) else None
        if not isinstance(entries, list):
            return ("json", None, {})
        files = [p["file"] for p in entries
                 if isinstance(p, dict) and isinstance(p.get("file"), str)]
        planned: dict[str, list[str]] = {}
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("file"), str):
                continue
            edges = [h.strip() for h in (entry.get("links") or []) if isinstance(h, str)]
            planned[entry["file"]] = [e for e in edges if e.endswith(".html")]
        return ("json", files, planned)
    xml_path = site_dir / "sitemap.xml"
    if xml_path.is_file():
        try:
            text = xml_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ("xml", None, {})
        files = []
        for match in _SEO_LOC_RE.finditer(text):
            loc = match.group(1).strip().split("?", 1)[0].rstrip("/")
            files.append(loc.rsplit("/", 1)[-1] or "index.html")
        return ("xml", files, {})
    return (None, None, {})


def _ld_nodes(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _ld_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _ld_nodes(value)


def _ld_typed_blocks(all_html: str) -> list[tuple[str, dict]]:
    """Parsed (page marker, node) pairs for every dict node carrying @type."""
    out: list[tuple[str, dict]] = []
    for match in _SEO_LD_RE.finditer(all_html):
        try:
            data = json.loads(match.group(1).strip())
        except ValueError:
            continue
        for node in _ld_nodes(data):
            kind = node.get("@type")
            kinds = kind if isinstance(kind, list) else [kind]
            for name in kinds:
                if isinstance(name, str) and name:
                    out.append((name, node))
    return out


def _breadcrumb_faults(node: dict, page: str) -> list[str]:
    items = node.get("itemListElement")
    if not isinstance(items, list) or len(items) < 2:
        return [f"{page}: BreadcrumbList itemListElement needs >= 2 ListItems"]
    got = [it.get("position") if isinstance(it, dict) else None for it in items]
    if got != list(range(1, len(items) + 1)):
        return [f"{page}: BreadcrumbList position must run 1..{len(items)}"]
    faults = []
    for pos, item in enumerate(items, 1):
        if not isinstance(item, dict):
            return [f"{page}: BreadcrumbList item {pos} not an object"]
        name = item.get("name")
        if not (isinstance(name, str) and name.strip()):
            faults.append(f"{page}: BreadcrumbList name missing on item {pos}")
        if pos < len(items) and not item.get("item"):
            faults.append(f"{page}: BreadcrumbList item missing on item {pos}")
    return faults


def _seo_rows(rep: Report, site_dir: Path, pages: list[Path]) -> None:
    """SEO-research battery. Row names, severities and sources in order below."""
    site_dir = Path(site_dir)
    htmls = {p.name: p.read_text(encoding="utf-8", errors="replace") for p in pages}
    names = sorted(htmls)
    noindexed = {name for name, html in htmls.items() if _seo_noindex(html)}
    indexable = [name for name in names if name not in noindexed]

    def _verdict(name: str, fails: list[str], warns: list[str], ok_detail: str) -> None:
        if fails:
            detail = "; ".join(fails[:8])
            if len(fails) > 8:
                detail += f" (+{len(fails) - 8} more)"
            if warns:
                detail += "; also: " + "; ".join(warns[:4])
            rep.add(name, "FAIL", detail)
        elif warns:
            detail = "; ".join(warns[:8])
            if len(warns) > 8:
                detail += f" (+{len(warns) - 8} more)"
            rep.add(name, "WARN", detail)
        else:
            rep.add(name, "PASS", ok_detail)

    # G-SEO-01 + Ahrefs titles: unique, non-empty, non-boilerplate; 15-70 chars heuristic.
    titles = {name: _seo_title(html) for name, html in htmls.items()}
    seen: dict[str, str] = {}
    title_fails, title_warns = [], []
    for name in names:
        title = titles[name]
        if not title:
            title_fails.append(f"{name}: title empty")
            continue
        if title.lower() in _TITLE_BOILERPLATE:
            title_fails.append(f"{name}: title boilerplate-only {title!r}")
        key = title.casefold()
        if key in seen:
            title_fails.append(f"{name}: title duplicate of {seen[key]}")
        else:
            seen[key] = name
        if len(title) < _SEO_TITLE_MIN:
            title_warns.append(f"{name}: title {len(title)} chars (<{_SEO_TITLE_MIN})")
        elif len(title) > _SEO_TITLE_MAX:
            title_warns.append(f"{name}: title {len(title)} chars (>{_SEO_TITLE_MAX})")
    _verdict("title_unique", title_fails, title_warns, f"{len(pages)} page(s), unique")

    # G-SEO-02: missing description already FAILs in description; here duplicates WARN.
    descs = {name: _seo_description(html) for name, html in htmls.items() if _seo_description(html)}
    desc_seen: dict[str, str] = {}
    desc_warns = []
    for name in names:
        if name not in descs:
            continue
        key = descs[name].casefold()
        if key in desc_seen:
            desc_warns.append(f"{name}: meta description duplicate of {desc_seen[key]}")
        else:
            desc_seen[key] = name
    _verdict("description_unique", [], desc_warns, f"{len(pages)} page(s)")

    # G-SEO-03: exactly one non-empty h1 on EVERY page (one_h1 covers index only).
    h1_fails = []
    for name in names:
        texts = _seo_h1_texts(htmls[name])
        if len(texts) != 1:
            h1_fails.append(f"{name}: h1 count={len(texts)}, want 1")
        elif not texts[0]:
            h1_fails.append(f"{name}: h1 empty")
    _verdict("h1_every_page", h1_fails, [], f"{len(pages)} page(s), one h1 each")

    # G-LINK-01 + Stox C2: every link is <a> with a resolvable URI. A bare "#"
    # is a WARN (placeholder or script hook; sole-route-to-content needs a
    # browser to judge), while missing/empty/javascript: hrefs FAIL outright.
    href_fails, href_warns = [], []
    for name in names:
        for link in _seo_anchors(htmls[name]):
            raw = link["href"]
            if raw is None or not link["seen_href"] or not raw.strip():
                href_fails.append(f"{name}: a without href")
            elif raw.strip().lower().startswith("javascript:"):
                href_fails.append(f"{name}: a javascript: href")
            elif raw.strip() == "#":
                href_warns.append(f"{name}: a placeholder href=#")
    _verdict("link_href", sorted(set(href_fails)), sorted(set(href_warns)),
             f"{len(pages)} page(s), crawlable hrefs")

    # G-LINK-02/03/04 + Stox C3: named anchors, descriptive, unchained.
    anchor_fails, anchor_warns = [], []
    for name in names:
        html = htmls[name]
        for link in _seo_anchors(html):
            label = link["text"] or link["title"] or link["img_alt"]
            if not label:
                href = (link["href"] or "").strip() or "<missing href>"
                anchor_fails.append(f"{name}: empty anchor -> {href[:60]}")
            elif label.lower() in _GENERIC_ANCHORS or _SEO_BARE_URL_RE.match(label):
                anchor_warns.append(f"{name}: generic anchor {label[:40]!r}")
        prose = _SEO_CHROME_RE.sub(" ", html)
        if _SEO_CHAIN_RE.search(prose):
            anchor_warns.append(f"{name}: adjacent links with no separating text")
    _verdict("anchor_text", sorted(set(anchor_fails)), sorted(set(anchor_warns)),
             f"{len(pages)} page(s), named anchors")

    # G-LINK-05 + G-CRW-01 + Stox C1: zero inbound internal links on indexable pages.
    edges = _seo_graph(pages)
    inbound: dict[str, set[str]] = {name: set() for name in names}
    for src, targets in edges.items():
        for hit in targets:
            inbound[hit].add(src)
    orphan_fails = [f"{name}: zero inbound internal links" for name in indexable
                    if not inbound[name]]
    if len(pages) == 1:
        rep.add("orphan_pages", "PASS", "single-page emit-only (D1)")
    else:
        _verdict("orphan_pages", orphan_fails, [],
                 f"{len(pages)} page(s), every indexable page linked")

    # G-LINK-06 + Stox C5: BFS depth from index; >3 clicks is a heuristic WARN.
    depths = _seo_depths(pages, edges)
    deep_warns = [f"{name}: {depths[name]} clicks from index (heuristic limit {_SEO_CLICK_MAX})"
                  for name in indexable
                  if name in depths and depths[name] > _SEO_CLICK_MAX]
    deep_warns += [f"{name}: unreachable from index" for name in indexable if name not in depths]
    if len(pages) == 1:
        rep.add("click_depth", "PASS", "single-page emit-only (D1)")
    else:
        _verdict("click_depth", [], sorted(deep_warns),
                 f"max depth {max(depths.values()) if depths else 0} from index")

    # Stox C4 (VERIFIED-core): rel sculpting values are the wrong tool in-site.
    sculpt_fails = []
    for name in names:
        for link in _seo_anchors(htmls[name]):
            raw = (link["href"] or "").strip()
            if not raw or _seo_is_external(raw) or raw.startswith("#"):
                continue
            bad = sorted(set(link["rel"]) & _INTERNAL_REL_BAD)
            if bad:
                sculpt_fails.append(f"{name}: rel={'+'.join(bad)} on internal {raw[:60]}")
    _verdict("internal_nofollow", sorted(set(sculpt_fails)), [],
             f"{len(pages)} page(s), no internal sculpting")

    # G-SEO-08 + G-CRW-02: render-critical assets and index-intended pages stay allowed.
    disallows = _robots_disallows(site_dir)
    asset_hit = ""
    if disallows:
        for rule in disallows:
            low = rule.lower()
            if any(token in low for token in (".css", ".js", ".png", ".jpg", ".jpeg",
                                              ".webp", ".avif", ".svg", "favicon",
                                              "/assets", "/static", "/images")):
                asset_hit = rule
                break
    if disallows is None:
        rep.add("robots_allow", "PASS", "no robots.txt")
    elif not indexable:
        rep.add("robots_allow", "PASS", "staging posture: noindex pages + disallow coherent")
    elif "" in disallows or "/" in disallows:
        rep.add("robots_allow", "FAIL", "robots.txt: Disallow: / blocks index-intended pages")
    elif asset_hit:
        rep.add("robots_allow", "FAIL", f"robots.txt: Disallow: {asset_hit} blocks assets")
    else:
        rep.add("robots_allow", "PASS", "index-intended pages and assets allowed")

    # G-CRW-03: a noindex page that is also disallowed can never have it seen.
    crawl_warns = []
    if disallows:
        blanket = "" in disallows or "/" in disallows
        for name in sorted(noindexed):
            hit = blanket or any(name.startswith(rule.lstrip("/")) for rule in disallows if rule)
            if hit:
                crawl_warns.append(f"{name}: noindex but robots-disallowed (directive never seen)")
    _verdict("noindex_crawl", [], crawl_warns, "no noindex/crawl conflict")

    # G-CRW-05 + S1/S2/S3 + G-SEO-09, D1-scoped: sitemap lists canonical indexable URLs.
    kind, files, _planned = _sitemap_expected(site_dir)
    if kind is None and len(pages) == 1:
        rep.add("sitemap_parity", "PASS", "single-page emit-only (D1)")
    elif kind is None:
        rep.add("sitemap_parity", "WARN",
                "multi-page without sitemap (D1: required for crew/multi-page)")
    elif files is None:
        rep.add("sitemap_parity", "FAIL", "sitemap present but unreadable")
    else:
        on_disk = set(names)
        listed = set(files)
        miss_fails = [f"sitemap lists missing {item}" for item in files if item not in on_disk]
        gap_warns = [f"{name}: indexable page missing from sitemap" for name in indexable
                     if name not in listed]
        _verdict("sitemap_parity", miss_fails, sorted(gap_warns),
                 f"sitemap lists {len(files)} file(s), parity holds")

    # schema.md: required props per type; HowTo deprecated; FAQPage owned by faq_schema.
    typed = _ld_typed_blocks("\n".join(htmls.values()))
    schema_fails, schema_warns = [], []
    for _kind, node in typed:
        where = next((n for n, h in htmls.items() if _kind in h), "?")
        if _kind == "FAQPage":
            continue
        if _kind == "HowTo":
            schema_fails.append(f"{where}: HowTo deprecated (rich result retired); remove")
        elif _kind == "BreadcrumbList":
            schema_fails.extend(_breadcrumb_faults(node, where))
        elif _kind in _LB_TYPES:
            if not (isinstance(node.get("name"), str) and node.get("name").strip()):
                schema_fails.append(f"{where}: LocalBusiness name missing")
            addr = node.get("address")
            addr_fields = ("streetAddress", "addressLocality", "addressRegion",
                           "postalCode", "addressCountry")
            addr_full = (isinstance(addr, str) and bool(addr.strip())
                         or isinstance(addr, dict)
                         and any(addr.get(k) for k in addr_fields))
            if addr_full:
                pass
            elif isinstance(addr, dict):
                schema_warns.append(f"{where}: LocalBusiness address thin (add locality+)")
            else:
                schema_fails.append(f"{where}: LocalBusiness address missing")
            if not node.get("telephone"):
                schema_warns.append(f"{where}: LocalBusiness telephone missing")
        elif _kind in _ARTICLE_TYPES and not (
                isinstance(node.get("headline"), str) and node.get("headline").strip()):
            schema_warns.append(f"{where}: {_kind} without headline")
    if not typed or all(k == "FAQPage" for k, _n in typed):
        rep.add("schema_required", "PASS", "no typed blocks (valid-or-absent)")
    else:
        _verdict("schema_required", schema_fails, sorted(set(schema_warns)),
                 f"{len(typed)} typed block(s), required props present")

    # G-SEO-07: thin pages WARN (300-word practitioner heuristic).
    thin_warns = []
    for name in names:
        words = len(visible_text(htmls[name]).split())
        if words < _SEO_BODY_MIN_WORDS:
            thin_warns.append(f"{name}: {words} words (<{_SEO_BODY_MIN_WORDS} heuristic)")
    _verdict("thin_content", [], sorted(thin_warns), f"{len(pages)} page(s), substantive")

    # G-SEO-06: identical visible text under multiple URLs needs canonical intent.
    buckets: dict[str, list[str]] = {}
    for name in names:
        key = _seo_collapse(visible_text(htmls[name])).casefold()
        buckets.setdefault(key, []).append(name)
    dup_fails = [f"identical visible text: {', '.join(sorted(group))}"
                 for group in buckets.values() if len(group) > 1]
    _verdict("duplicate_content", sorted(dup_fails), [], f"{len(pages)} page(s), distinct")

    # Stox C9 (heuristic): dead-end pages kill equity circulation on multi-page sites.
    if len(pages) == 1:
        rep.add("dead_end", "PASS", "single-page emit-only (D1)")
    else:
        dead_warns = [f"{name}: zero outbound internal links (heuristic)" for name in indexable
                      if not edges[name]]
        _verdict("dead_end", [], sorted(dead_warns), "every indexable page links onward")

    # Ahrefs localization family: the document language must be declared.
    lang_fails = [f"{name}: html lang missing" for name in names if not _seo_lang(htmls[name])]
    _verdict("doc_lang", sorted(lang_fails), [], f"{len(pages)} page(s), lang declared")

    # D1/D6 plan-vs-render: sitemap.json edges must exist in HTML and vice versa.
    if kind != "json" or files is None:
        rep.add("plan_links", "SKIP", "not-run: no sitemap.json grouping data")
    else:
        _kind2, _files2, planned = _sitemap_expected(site_dir)
        plan_fails, plan_warns = [], []
        for src in names:
            want = set(planned.get(src, ()))
            got = edges.get(src, set())
            for hit in sorted(want - got):
                if hit in names:
                    plan_fails.append(f"{src}: planned link to {hit} not in HTML")
            for hit in sorted(got - want):
                plan_warns.append(f"{src}: unplanned link to {hit}")
        _verdict("plan_links", plan_fails, plan_warns, "plan edges match rendered HTML")


class Report:
    def __init__(self, quiet: bool = False):
        self.rows: list[dict] = []
        self.quiet = quiet  # quiet=True: never print (MCP stdio channel stays clean)

    def add(self, name: str, status: str, detail: str = "", failures: list | None = None,
            unmeasured: list | None = None, inventory: list | None = None) -> None:
        row = {"name": name, "status": status, "detail": detail}
        if failures is not None:
            row["failures"] = failures  # every failure, untruncated: file, selector, measured
        if unmeasured:
            row["unmeasured"] = unmeasured  # not measurable: never a pass
        if inventory:
            row["inventory"] = inventory  # informational only (mobile_visibility)
        self.rows.append(row)
        if self.quiet:
            return
        mark = {"PASS": "[pass]", "FAIL": "[FAIL]", "WARN": "[warn]", "SKIP": "[skip]"}[status]
        line = f"  {mark} {name}"
        if detail:
            line += f" - {detail}"
        print(line)
        for failure in failures or []:
            print("      > " + failure_line(failure))
        for item in unmeasured or []:
            print("      ? " + failure_line(item, warn=True))
        for item in (inventory or [])[:20]:
            print("      i " + failure_line(item))
        if inventory and len(inventory) > 20:
            print(f"      i (+{len(inventory) - 20} more in the row's inventory)")

    def counts(self) -> dict:
        c = {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0}
        for r in self.rows:
            c[r["status"]] += 1
        return c

    def ok(self) -> bool:
        return self.counts()["FAIL"] == 0


def check_site(
    site_dir: Path,
    expect_noindex: bool | None = None,
    quiet: bool = False,
    copy_text: str = "",
    typography: bool = True,
    tap_targets: bool = True,
    extra_gates: bool = True,
    mobile: bool = True,
    mobile_spec=None,
) -> Report:
    rep = Report(quiet=quiet)
    site_dir = Path(site_dir)
    index = site_dir / "index.html"
    if not index.exists():
        rep.add("files_present", "FAIL", f"missing {index}")
        return rep
    rep.add("files_present", "PASS", str(site_dir))

    pages = sorted(site_dir.glob("*.html"))
    all_html = ""
    for p in pages:
        all_html += p.read_text(encoding="utf-8", errors="replace") + "\n"

    # 1) fleet no_sample patterns on raw HTML
    hits = []
    for rx in FLEET_SAMPLE_PATTERNS:
        m = rx.search(all_html)
        if m:
            hits.append(m.group(0))
    if hits:
        rep.add("no_sample", "FAIL", "fleet pattern(s): " + ", ".join(sorted(set(hits))))
    else:
        rep.add("no_sample", "PASS", f"{len(pages)} page(s) scanned")

    # 2) soft placeholder markers in visible text
    vis = visible_text(all_html)
    soft = [m.group(0) for rx in SOFT_PATTERNS for m in [rx.search(vis)] if m]
    if soft:
        rep.add("no_soft_placeholders", "FAIL", "visible text contains: " + ", ".join(sorted(set(soft))))
    else:
        rep.add("no_soft_placeholders", "PASS")

    # 3) hotlink: any remote URL fails. JSON-LD @context identifiers are not
    # a fetch, so ld+json script bodies are stripped before the scan. A URL
    # dropped at ingest is a warning there; a URL that survives in HTML/CSS
    # is FAIL here, even when the host is not on the stock-CDN list.
    _ld_stripped = re.sub(
        r'<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>.*?</script>',
        "<script></script>",
        all_html,
        flags=re.I | re.S,
    )
    _remote_hits = []
    if HOTLINK_RE.search(_ld_stripped):
        _remote_hits.append("stock-CDN host")
    # any http(s) URL or protocol-relative URL in markup/CSS, srcset, url(), @import
    for _m in re.finditer(
        r"""https?://[^\s"'<>()]+|src\s*=\s*["']//[^"']+|href\s*=\s*["']//[^"']+|"""
        r"""url\(\s*["']?\s*(?:https?:)?//[^)]+|@import\s+[^;]*https?://[^;]+|"""
        r"""srcset\s*=\s*["'][^"']*https?://[^"']*""",
        _ld_stripped,
        re.I,
    ):
        _remote_hits.append(_m.group(0)[:80])
        break
    if _remote_hits:
        seen_hit = sorted(set(_remote_hits))[0]
        rep.add("no_hotlink", "FAIL", f"remote URL in output: {seen_hit}")
    else:
        rep.add("no_hotlink", "PASS", f"{len(pages)} page(s), local only")

    # 4) basics per page
    bad_meta = []
    for p in pages:
        html = p.read_text(encoding="utf-8", errors="replace")
        if "<!doctype html>" not in html[:64].lower():
            bad_meta.append(f"{p.name}: doctype")
        if not re.search(r"<title>[^<]+</title>", html):
            bad_meta.append(f"{p.name}: title")
        if not re.search(r'<meta name="description" content="[^"]+"', html):
            bad_meta.append(f"{p.name}: description")
        if 'name="viewport"' not in html:
            bad_meta.append(f"{p.name}: viewport")
    if bad_meta:
        rep.add("meta_basics", "FAIL", "; ".join(bad_meta))
    else:
        rep.add("meta_basics", "PASS", f"{len(pages)} page(s)")

    # 5) noindex status
    has_robots = 'name="robots" content="noindex' in all_html
    if expect_noindex is None:
        rep.add("noindex_status", "SKIP", f"robots noindex={'on' if has_robots else 'off'}")
    elif expect_noindex and not has_robots:
        rep.add("noindex_status", "FAIL", "expected noindex but pages are indexable")
    elif not expect_noindex and has_robots:
        rep.add("noindex_status", "WARN", "pages are noindex; pass --indexable at build to flip")
    else:
        rep.add("noindex_status", "PASS", "matches build flag")

    # 6) internal anchors + page links resolve
    anchor_ids = set(re.findall(r'\bid="([^"]+)"', all_html))
    broken = []
    for p in pages:
        html = p.read_text(encoding="utf-8", errors="replace")
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("#",)):
                frag = href[1:]
                if frag and frag not in anchor_ids:
                    broken.append(f"{p.name}: {href}")
            elif href.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            else:
                target = href.split("#")[0]
                if target and not (site_dir / target).exists():
                    broken.append(f"{p.name}: {href}")
    if broken:
        rep.add("internal_links", "FAIL", "; ".join(broken[:8]) + (f" (+{len(broken) - 8} more)" if len(broken) > 8 else ""))
    else:
        rep.add("internal_links", "PASS", f"{len(anchor_ids)} anchors, {len(pages)} pages")

    # 7) index mobile / visual contract. img src is not an href, so it stays
    # off the internal_links row. A letter-mark hero has no img and passes.
    index_html = index.read_text(encoding="utf-8", errors="replace")
    header_gaps = []
    if not _class_tokens(index_html, "site-header"):
        header_gaps.append("missing class site-header")
    if not _script_sets_stuck(index_html):
        header_gaps.append("script does not set is-stuck")
    if header_gaps:
        rep.add("site_header", "FAIL", "; ".join(header_gaps))
    else:
        rep.add("site_header", "PASS", "class site-header; script sets is-stuck")

    if _class_tokens(index_html, "hero-visual"):
        rep.add("hero_visual", "PASS")
    else:
        rep.add("hero_visual", "FAIL", "index has no class hero-visual")

    if _favicon_link(index_html):
        rep.add("favicon_link", "PASS", 'rel="icon" href="favicon.svg"')
    else:
        rep.add("favicon_link", "FAIL", 'index missing rel="icon" href="favicon.svg"')

    favicon = site_dir / "favicon.svg"
    if not favicon.is_file():
        rep.add("favicon_svg", "FAIL", "missing favicon.svg beside index.html")
    else:
        fav_text = favicon.read_text(encoding="utf-8", errors="replace")
        if "<svg" not in fav_text.lower():
            rep.add("favicon_svg", "FAIL", "favicon.svg has no <svg")
        else:
            rep.add("favicon_svg", "PASS", "favicon.svg contains <svg")

    srcs = _img_srcs(index_html)
    if not srcs:
        rep.add("relative_img", "PASS", "no img")
    else:
        bad = []
        for src in srcs:
            if not _remote_img(src):
                continue
            shown = "<missing src>" if not (src and src.strip()) else src.strip()
            if len(shown) > 80:
                shown = shown[:77] + "..."
            bad.append(shown)
        if bad:
            rep.add("relative_img", "FAIL", "remote img src: " + "; ".join(bad[:6]))
        else:
            rep.add("relative_img", "PASS", f"{len(srcs)} relative img src(s)")

    _add_index_phone_rows(rep, index_html)

    # On-page SEO. Does not replace header, hero, favicon, remote image, or noindex.
    bad_canonical = []
    bad_description = []
    missing_ld = []
    rated = []
    bad_alt = []
    faq_pages = []
    img_count = 0
    for p in pages:
        html = p.read_text(encoding="utf-8", errors="replace")
        if not _canonical_ok(html):
            bad_canonical.append(p.name)
        if not _description_ok(html):
            bad_description.append(p.name)
        if "aggregateRating" in html:
            rated.append(p.name)
        if not _website_script(html):
            missing_ld.append(p.name)
        for alt in _img_alts(html):
            img_count += 1
            if alt is None or not str(alt).strip():
                bad_alt.append(p.name)
                break
        if _has_faqpage(html):
            faq_pages.append(p.name)
    if bad_canonical:
        rep.add("canonical", "FAIL", "missing rel=canonical: " + ", ".join(bad_canonical))
    else:
        rep.add("canonical", "PASS", f"{len(pages)} page(s)")
    # JSON-LD valid-or-absent: absent is PASS (thin copy cannot fill a type).
    # Present must parse and must not invent aggregateRating. Retired FAQPage
    # is judged by faq_schema, not here. The @context identifier is not a
    # fetch (see no_hotlink).
    _ld_blocks = re.findall(
        r'<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        all_html,
        re.I | re.S,
    )
    _ld_bad = []
    for _blk in _ld_blocks:
        try:
            json.loads(_blk.strip())
        except ValueError:
            _ld_bad.append("unparsable JSON-LD")
            break
    if rated:
        _ld_bad.append("aggregateRating: " + ", ".join(rated))
    if _ld_bad:
        rep.add("json_ld", "FAIL", "; ".join(_ld_bad))
    elif not _ld_blocks:
        rep.add("json_ld", "PASS", "absent (copy cannot fill a type)")
    elif missing_ld:
        # ld+json present but no WebSite type: still valid-or-absent PASS when
        # the blocks parse; faq_schema rejects retired FAQPage separately.
        rep.add("json_ld", "PASS", "present types valid; WebSite absent (copy cannot fill it)")
    else:
        rep.add("json_ld", "PASS", "WebSite; no aggregateRating")
    if bad_description:
        rep.add("description", "FAIL", "empty meta description: " + ", ".join(bad_description))
    else:
        rep.add("description", "PASS", f"{len(pages)} page(s)")
    h1_count = len(re.findall(r"<h1\b", index_html, re.I))
    if h1_count == 1:
        rep.add("one_h1", "PASS", "index has 1 h1")
    else:
        rep.add("one_h1", "FAIL", f"index has {h1_count} h1")
    from lib.heading_rank import heading_skips
    skipped = []
    for page_path in pages:
        page_html = page_path.read_text(encoding="utf-8", errors="replace")
        for hit in heading_skips(page_html):
            skipped.append(f"{page_path.name}: {hit}")
    if skipped:
        extra = f" (+{len(skipped) - 8} more)" if len(skipped) > 8 else ""
        rep.add("heading_order", "FAIL", "; ".join(skipped[:8]) + extra)
    else:
        rep.add("heading_order", "PASS", f"{len(pages)} page(s)")
    if bad_alt:
        rep.add("img_alt", "FAIL", "img missing alt: " + ", ".join(bad_alt))
    elif img_count == 0:
        rep.add("img_alt", "PASS", "no img")
    else:
        rep.add("img_alt", "PASS", f"{img_count} img alt(s)")
    missing_files, local_imgs = _missing_local_imgs(pages)
    if missing_files:
        extra = f" (+{len(missing_files) - 8} more)" if len(missing_files) > 8 else ""
        rep.add("missing_file", "FAIL", "; ".join(missing_files[:8]) + extra)
    elif local_imgs == 0:
        rep.add("missing_file", "PASS", "no img")
    else:
        rep.add("missing_file", "PASS", f"{local_imgs} local img file(s)")
    if faq_pages:
        extra = f" (+{len(faq_pages) - 8} more)" if len(faq_pages) > 8 else ""
        rep.add(
            "faq_schema",
            "FAIL",
            "FAQPage retired (Google removed the FAQ rich result); "
            "remove JSON-LD, keep visible FAQ: " + ", ".join(faq_pages[:8]) + extra,
        )
    else:
        rep.add("faq_schema", "PASS", "no FAQPage")

    # SEO-research battery (google/schema/ahrefs/moz/stox, static D1/D6 subset).
    try:
        _seo_rows(rep, site_dir, pages)
    except Exception as exc:  # noqa: BLE001 -- fail closed, file convention
        rep.add("seo_rows", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])

    # Type floor and WCAG contrast over every page. typography=False skips both rows.
    if typography:
        _typography_rows(rep, pages)
    if tap_targets:
        _tap_rows(rep, pages)
    if mobile:
        _mobile_rows(rep, pages, mobile_spec)
    if extra_gates:
        _gate_rows(rep, site_dir, pages)
        try:
            _weight_row(rep, pages)
        except Exception as exc:  # fail closed
            rep.add("weight", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
        try:
            _safe_area_row(rep, pages)
        except Exception as exc:  # fail closed
            rep.add("safe_area", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
        try:
            _css_contract_row(rep, pages)
        except Exception as exc:  # fail closed
            rep.add("css_contract", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
        try:
            _layout_stability_row(rep, pages)
        except Exception as exc:  # fail closed
            rep.add("layout_stability", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
        try:
            _visual_probe_row(rep, site_dir, pages)
        except Exception as exc:  # fail closed
            rep.add("visual_probe", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
        try:
            _one_cta_row(rep, pages, copy_text)
        except Exception as exc:  # fail closed
            rep.add("one_cta", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
        for _row_name, _row_fn in (
            ("cta_present", lambda: _cta_present_row(rep, pages)),
            ("ask_after_proof", lambda: _ask_after_proof_row(rep, site_dir)),
            ("single_primary_cta", lambda: _single_primary_cta_row(rep, site_dir, pages, copy_text)),
            ("mobile_block", lambda: _mobile_block_row(rep, site_dir)),
        ):
            try:
                _row_fn()
            except Exception as exc:  # fail closed
                rep.add(_row_name, "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])

    # 8) token ledger: strict schema, unknown never coerced to 0.
    report_path = site_dir / "report.json"
    if report_path.exists():
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
            t = data.get("tokens", {})
            mode = data.get("mode")
            attempts = data.get("attempts")
            _ledger_bad = []
            if mode not in ("offline", "ai", "offline-fallback", "rebuild", "refine", "refine-offline", "from-ir", "compose"):
                _ledger_bad.append(f"mode={mode!r}")
            if not isinstance(t, dict) or not isinstance(t.get("in_tokens"), int) or not isinstance(t.get("out_tokens"), int):
                _ledger_bad.append("tokens.in/out not ints (unknown must stay null, never 0)")
            elif t.get("in_tokens", 0) < 0 or t.get("out_tokens", 0) < 0:
                _ledger_bad.append("negative token counts")
            elif mode == "offline" and (t.get("in_tokens") != 0 or t.get("out_tokens") != 0):
                _ledger_bad.append("offline must total 0")
            if not isinstance(attempts, list):
                _ledger_bad.append("attempts not a list")
            if _ledger_bad:
                rep.add("token_ledger", "FAIL", "; ".join(_ledger_bad))
            else:
                rep.add("token_ledger", "PASS",
                        f"mode={data.get('mode')} in={t.get('in_tokens', 0)} out={t.get('out_tokens', 0)} "
                        f"est=${t.get('est_cost_usd', 0):.4f}")
        except (OSError, ValueError) as exc:
            rep.add("token_ledger", "FAIL", f"report.json unreadable: {exc}")
    else:
        # No ledger to judge on the direct-hands path (no build ran).
        # NOT RUN is SKIP, never PASS; release flows must refuse NOT RUN.
        rep.add("token_ledger", "SKIP",
                "not-run: no report.json (run a build first)", failures=[])

    # Cited-text + anti-invention rows. cited_text always reports (SKIP when no
    # copy_text, so unrun!=pass at ticket time); the older claim rows only run
    # when copy is present, preserving their fail-closed behavior.
    if extra_gates:
        try:
            _cited_text_row(rep, pages, copy_text or "")
        except Exception as exc:  # fail closed
            rep.add("cited_text", "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
    if copy_text:
        claim_hits = _ungrounded_claim_hits(pages, copy_text)
        if claim_hits:
            extra = f" (+{len(claim_hits) - 8} more)" if len(claim_hits) > 8 else ""
            rep.add("ungrounded_claim", "FAIL", "; ".join(claim_hits[:8]) + extra)
        about_hits = _lone_about_hits(pages, copy_text)
        if about_hits:
            extra = f" (+{len(about_hits) - 8} more)" if len(about_hits) > 8 else ""
            rep.add("lone_about", "FAIL", "; ".join(about_hits[:8]) + extra)
        chrome_hits = _invented_chrome_hits(pages, copy_text)
        if chrome_hits:
            extra = f" (+{len(chrome_hits) - 8} more)" if len(chrome_hits) > 8 else ""
            rep.add("invented_chrome", "FAIL", "; ".join(chrome_hits[:8]) + extra)
        demo_hits = _part_demo_hits(pages, copy_text)
        if demo_hits:
            extra = f" (+{len(demo_hits) - 8} more)" if len(demo_hits) > 8 else ""
            rep.add("part_demo", "FAIL", "; ".join(demo_hits[:8]) + extra)

    return rep


# ---------------------------------------------------------------------------
# Reproducibility: build one project twice (offline, into temp dirs), compare
# byte for byte. A mismatch names each differing file and the first differing
# JSON key or text line. Does not touch the project or sites/.
# Run: python -m lib.check --reproducible [project_dir]   (default projects/demo-local)
# ---------------------------------------------------------------------------
REPRO_DEFAULT_PROJECT = ("projects", "demo-local")


def _clip(value, limit: int = 80) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = text.replace("\r", "\\r").replace("\n", "\\n")
    return text if len(text) <= limit else text[:limit - 3] + "..."


def _json_first_diff(a, b, path: str = ""):
    """First differing key path in document order: (path, a_value, b_value) or None."""
    here = path or "$"
    if type(a) is not type(b):
        return here, a, b
    if isinstance(a, dict):
        keys = list(a) + [k for k in b if k not in a]
        for key in keys:
            sub = f"{path}.{key}" if path else str(key)
            if key not in a:
                return sub, "<absent>", b[key]
            if key not in b:
                return sub, a[key], "<absent>"
            got = _json_first_diff(a[key], b[key], sub)
            if got:
                return got
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{here}[length]", len(a), len(b)
        for k, (x, y) in enumerate(zip(a, b)):
            got = _json_first_diff(x, y, f"{here}[{k}]")
            if got:
                return got
        return None
    return None if a == b else (here, a, b)


def _first_file_diff(rel: str, raw_a: bytes, raw_b: bytes) -> dict:
    rec = {"check": "reproducible", "file": rel, "kind": "differs", "where": "", "first": "", "second": ""}
    try:
        text_a, text_b = raw_a.decode("utf-8"), raw_b.decode("utf-8")
    except UnicodeDecodeError:
        text_a = text_b = None
    if text_a is None:
        at = next((k for k, (x, y) in enumerate(zip(raw_a, raw_b)) if x != y), min(len(raw_a), len(raw_b)))
        rec.update(where=f"byte {at}", first=f"{len(raw_a)} bytes", second=f"{len(raw_b)} bytes")
        return rec
    if rel.lower().endswith(".json"):
        try:
            got = _json_first_diff(json.loads(text_a), json.loads(text_b))
        except ValueError:
            got = None
        if got:
            rec.update(where=f"key {got[0]}", first=_clip(got[1]), second=_clip(got[2]))
            return rec
    lines_a, lines_b = text_a.split("\n"), text_b.split("\n")
    for k in range(max(len(lines_a), len(lines_b))):
        x = lines_a[k] if k < len(lines_a) else "<end of file>"
        y = lines_b[k] if k < len(lines_b) else "<end of file>"
        if x != y:
            rec.update(where=f"line {k + 1}", first=_clip(x), second=_clip(y))
            return rec
    rec.update(where="bytes", first=f"{len(raw_a)} bytes", second=f"{len(raw_b)} bytes")
    return rec


def _tree_files(root: Path) -> dict[str, Path]:
    return {p.relative_to(root).as_posix(): p for p in sorted(root.rglob("*")) if p.is_file()}


def compare_trees(first: Path, second: Path) -> tuple[list[dict], int]:
    """Byte-for-byte diff of two output trees: (differences, files compared)."""
    a, b = _tree_files(Path(first)), _tree_files(Path(second))
    diffs: list[dict] = []
    for rel in sorted(set(a) | set(b)):
        if rel not in b:
            diffs.append({"check": "reproducible", "file": rel, "kind": "only in first build",
                          "where": "", "first": "present", "second": "missing"})
        elif rel not in a:
            diffs.append({"check": "reproducible", "file": rel, "kind": "only in second build",
                          "where": "", "first": "missing", "second": "present"})
        else:
            raw_a, raw_b = a[rel].read_bytes(), b[rel].read_bytes()
            if raw_a != raw_b:
                diffs.append(_first_file_diff(rel, raw_a, raw_b))
    return diffs, len(set(a) | set(b))


def _tree_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _offline_build(project: Path, out: Path) -> None:
    """Default builder: spidercaster.py build <project> --offline --out <out>, in a subprocess."""
    root = _tree_root()
    proc = subprocess.run(
        [sys.executable, str(root / "spidercaster.py"), "build", str(project), "--offline",
         "--out", str(out)],
        cwd=str(root), stdin=subprocess.DEVNULL, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
    )
    if proc.returncode != 0:
        tail = [ln.strip() for ln in (proc.stdout + "\n" + proc.stderr).splitlines() if ln.strip()]
        raise RuntimeError(tail[-1] if tail else f"exit {proc.returncode}")


def check_reproducible(project_dir=None, quiet: bool = False, build=None) -> Report:
    """Build the project twice into temp dirs and compare the trees byte for byte.

    build(project, out_dir) overrides the builder (used by the selftest).
    The environment is passed through as-is: SOURCE_DATE_EPOCH makes the stamp
    deterministic, SPIDERCASTER_STAMP_BUILD=1 makes it differ on purpose.
    """
    rep = Report(quiet=quiet)
    project = Path(project_dir) if project_dir else _tree_root().joinpath(*REPRO_DEFAULT_PROJECT)
    if not project.is_dir():
        rep.add("reproducible", "FAIL", f"project not found: {project}", failures=[])
        return rep
    builder = build or _offline_build
    with tempfile.TemporaryDirectory(prefix="sc-repro-") as tmp:
        outs = [Path(tmp) / "build1", Path(tmp) / "build2"]
        for out in outs:
            try:
                builder(project, out)
            except Exception as exc:
                rep.add("reproducible", "FAIL", f"offline build failed: {exc}", failures=[])
                return rep
        diffs, total = compare_trees(outs[0], outs[1])
    if diffs:
        shown = "; ".join(
            f"{d['file']}: {d['where'] or d['kind']}" for d in diffs[:6])
        extra = f" (+{len(diffs) - 6} more)" if len(diffs) > 6 else ""
        rep.add("reproducible", "FAIL",
                f"{len(diffs)} of {total} file(s) differ between two offline builds: {shown}{extra}",
                failures=diffs)
    else:
        rep.add("reproducible", "PASS", f"{total} file(s) byte-identical across two offline builds of {project.name}",
                failures=[])
    return rep


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    mobile_spec = None
    for i, a in enumerate(list(args)):
        if a.startswith("--mobile-spec="):
            mobile_spec = a.split("=", 1)[1]
        elif a == "--mobile-spec":
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                print("--mobile-spec needs a path to a patterns.json (or a folder holding one)")
                return 2
            mobile_spec = args[i + 1]
    if mobile_spec is not None:
        cut = [i for i, a in enumerate(args) if a == "--mobile-spec"]
        if cut:
            del args[cut[0]:cut[0] + 2]
        args = [a for a in args if not a.startswith("--mobile-spec=")]
    positional = [a for a in args if not a.startswith("--")]
    if "--reproducible" in args:
        project = Path(positional[0]) if positional else None
        print(f"reproducibility: {project or Path(*REPRO_DEFAULT_PROJECT)} (two offline builds)")
        rep = check_reproducible(project)
        c = rep.counts()
        print(f"result: {c['PASS']} pass / {c['FAIL']} fail / {c['WARN']} warn / {c['SKIP']} skip")
        return 0 if rep.ok() else 1
    if not positional:
        print("usage: python -m lib.check <site_dir> [--expect-noindex|--expect-indexable]\n"
              "                         [--typography-only|--tap-only|--mobile-only] [--mobile-spec PATH]\n"
              "       python -m lib.check --reproducible [project_dir]")
        return 2
    site_dir = Path(positional[0])
    expect = None
    if "--expect-noindex" in args:
        expect = True
    if "--expect-indexable" in args:
        expect = False
    print(f"checking {site_dir}")
    if "--mobile-only" in args:
        rep = Report()
        pages = sorted(site_dir.glob("*.html"))
        if pages:
            _typography_rows(rep, pages, MOBILE_VIEWPORTS)
            _tap_rows(rep, pages)
            _mobile_rows(rep, pages, mobile_spec)
        else:
            rep.add("files_present", "FAIL", f"no .html in {site_dir}")
    elif "--tap-only" in args:
        rep = Report()
        pages = sorted(site_dir.glob("*.html"))
        if pages:
            _tap_rows(rep, pages)
        else:
            rep.add("files_present", "FAIL", f"no .html in {site_dir}")
    elif "--typography-only" in args:
        rep = Report()
        pages = sorted(site_dir.glob("*.html"))
        if pages:
            _typography_rows(rep, pages)
        else:
            rep.add("files_present", "FAIL", f"no .html in {site_dir}")
    else:
        rep = check_site(site_dir, expect, mobile_spec=mobile_spec)
    c = rep.counts()
    print(f"result: {c['PASS']} pass / {c['FAIL']} fail / {c['WARN']} warn / {c['SKIP']} skip")
    return 0 if rep.ok() else 1


if __name__ == "__main__":
    raise SystemExit(main())
