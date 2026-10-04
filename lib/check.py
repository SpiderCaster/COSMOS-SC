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
still passes img_alt. FAQPage JSON-LD, when present, must use only question
strings that are also visible; a page with no FAQPage passes faq_schema.
A relative img src must name a file beside that HTML; a page with no img
passes missing_file. When copy_text is non-empty, an h2 whose text is
exactly About fails lone_about if the word About is not in the copy, and
visible "Read on" or "Built with SpiderCaster" fails invented_chrome when
that exact phrase is not in the copy. Empty copy_text adds neither row.
Typography rows (every page, 360px and 1280px): type_floor fails rendered text
under 16px, and body text under 18px; contrast fails WCAG text under 4.5:1, or
3:1 for large text (24px+, or 18.66px+ at weight 700). Each failure names the
file, the CSS selector and the measured value. Computed styles come from a
static cascade over the page's own CSS, not a browser. Alone:
python -m lib.check <site_dir> --typography-only. Reproducibility:
python -m lib.check --reproducible [project_dir] builds the project twice
offline and compares the trees byte for byte.
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


def _question_names(node, found: list[str]) -> None:
    if isinstance(node, dict):
        if "Question" in _type_names(node) and isinstance(node.get("name"), str):
            found.append(node["name"])
        for value in node.values():
            _question_names(value, found)
    elif isinstance(node, list):
        for value in node:
            _question_names(value, found)


def _faq_questions(html: str) -> list[str]:
    """Question names from JSON-LD that contains FAQPage. Empty if no FAQPage."""
    if "FAQPage" not in html:
        return []
    found: list[str] = []
    for match in re.finditer(r"<script\b([^>]*)>(.*?)</script>", html, re.I | re.S):
        kind = _attr(match.group(1), "type")
        if not kind or kind.lower() != "application/ld+json":
            continue
        try:
            data = json.loads(match.group(2).strip())
        except ValueError:
            continue
        if not _has_type(data, "FAQPage"):
            continue
        _question_names(data, found)
    return found


def _faq_schema_gaps(html: str) -> list[str]:
    """JSON question strings that are not in the visible text."""
    visible = visible_text(html)
    missing: list[str] = []
    seen: set[str] = set()
    for question in _faq_questions(html):
        if question in visible or question in seen:
            continue
        seen.add(question)
        missing.append(question)
    return missing


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
# (width, height) of the two viewports every page is judged at.
TYPO_VIEWPORTS = ((360, 740), (1280, 800))

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
        return [("font-size", "inherit"), ("font-weight", "inherit")]
    if v == "initial":
        return [("font-size", "medium"), ("font-weight", "normal")]
    weight = "400"
    size = None
    for tok in _split_ws(val):
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
            size = _split_top(tok, "/")[0]
            break
    if size is None:
        return []
    return [("font-size", size), ("font-weight", weight)]


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
}


def _expand_decl(prop: str, val: str) -> list[tuple[str, str]]:
    if prop == "font":
        return _font_shorthand(val)
    if prop == "background":
        return _bg_shorthand(val)
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
    for _, label, prop, val in matched:
        if prop.startswith("--"):
            continue
        resolved = _subst_vars(val, customs)
        if resolved is None:
            continue
        for longhand, value in _expand_decl(prop, resolved):
            assign[longhand] = (value, label)

    cs = dict(pcs)
    cs["customs"] = customs
    cs["hidden"] = False

    if "font-size" in assign:
        val, label = assign["font-size"]
        cs["size"] = _resolve_size(val, pcs["size"], ctx)
        cs["size_src"] = label if val.strip().lower() not in ("inherit", "unset") else pcs["size_src"]
    if "font-weight" in assign:
        val, label = assign["font-weight"]
        got = _resolve_weight(val, pcs["weight"])
        cs["weight"] = pcs["weight"] if got is None else got
        cs["weight_src"] = label
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


def _analyze_page(page: Path, acc: _TypoAcc) -> None:
    html = page.read_text(encoding="utf-8", errors="replace")
    root = _build_dom(html)
    author_items = _stylesheet_items(root, page, acc)
    ua_items = _parse_css_items(_UA_CSS)
    acc.pages += 1
    for number, (w, h) in enumerate(TYPO_VIEWPORTS):
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


def typography_scan(pages: list[Path]) -> dict:
    """Run the type-floor and contrast judgement over HTML pages."""
    acc = _TypoAcc()
    for page in pages:
        _analyze_page(page, acc)
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


def failure_line(f: dict) -> str:
    """One line per failure: file | selector | measured (needs required) | where."""
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


def _typography_rows(rep: "Report", pages: list[Path]) -> None:
    try:
        scan = typography_scan(pages)
    except Exception as exc:  # fail closed: a checker bug must not read as a pass
        for name in ("type_floor", "contrast"):
            rep.add(name, "FAIL", f"checker error: {type(exc).__name__}: {exc}", failures=[])
        return
    views = "+".join(str(w) for w, _ in TYPO_VIEWPORTS) + "px"
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


class Report:
    def __init__(self, quiet: bool = False):
        self.rows: list[dict] = []
        self.quiet = quiet  # quiet=True: never print (MCP stdio channel stays clean)

    def add(self, name: str, status: str, detail: str = "", failures: list | None = None) -> None:
        row = {"name": name, "status": status, "detail": detail}
        if failures is not None:
            row["failures"] = failures  # every failure, untruncated: file, selector, measured
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

    # 3) hotlink blocklist
    if HOTLINK_RE.search(all_html):
        rep.add("no_hotlink", "FAIL", "external stock-photo CDN reference found")
    else:
        rep.add("no_hotlink", "PASS")

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
    faq_missing = []
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
        for question in _faq_schema_gaps(html):
            shown = question if len(question) <= 80 else question[:77] + "..."
            faq_missing.append(f"{p.name}: {shown}")
    if bad_canonical:
        rep.add("canonical", "FAIL", "missing rel=canonical: " + ", ".join(bad_canonical))
    else:
        rep.add("canonical", "PASS", f"{len(pages)} page(s)")
    if missing_ld or rated:
        bits = []
        if missing_ld:
            bits.append("missing WebSite script: " + ", ".join(missing_ld))
        if rated:
            bits.append("aggregateRating: " + ", ".join(rated))
        rep.add("json_ld", "FAIL", "; ".join(bits))
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
    if faq_missing:
        extra = f" (+{len(faq_missing) - 8} more)" if len(faq_missing) > 8 else ""
        rep.add("faq_schema", "FAIL", "; ".join(faq_missing[:8]) + extra)
    else:
        rep.add("faq_schema", "PASS", "questions visible or no FAQPage")

    # Type floor and WCAG contrast over every page. typography=False skips both rows.
    if typography:
        _typography_rows(rep, pages)

    # 8) token ledger present (from build report)
    report_path = site_dir / "report.json"
    if report_path.exists():
        try:
            import json
            data = json.loads(report_path.read_text(encoding="utf-8"))
            t = data.get("tokens", {})
            rep.add("token_ledger", "PASS",
                    f"mode={data.get('mode')} in={t.get('in_tokens', 0)} out={t.get('out_tokens', 0)} "
                    f"est=${t.get('est_cost_usd', 0):.4f}")
        except (OSError, ValueError) as exc:
            rep.add("token_ledger", "WARN", f"report.json unreadable: {exc}")
    else:
        rep.add("token_ledger", "WARN", "no report.json (run a build first)")

    # Empty copy_text adds no row, so older callers keep the same results.
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
    positional = [a for a in args if not a.startswith("--")]
    if "--reproducible" in args:
        project = Path(positional[0]) if positional else None
        print(f"reproducibility: {project or Path(*REPRO_DEFAULT_PROJECT)} (two offline builds)")
        rep = check_reproducible(project)
        c = rep.counts()
        print(f"result: {c['PASS']} pass / {c['FAIL']} fail / {c['WARN']} warn / {c['SKIP']} skip")
        return 0 if rep.ok() else 1
    if not positional:
        print("usage: python -m lib.check <site_dir> [--expect-noindex|--expect-indexable] [--typography-only]\n"
              "       python -m lib.check --reproducible [project_dir]")
        return 2
    site_dir = Path(positional[0])
    expect = None
    if "--expect-noindex" in args:
        expect = True
    if "--expect-indexable" in args:
        expect = False
    print(f"checking {site_dir}")
    if "--typography-only" in args:
        rep = Report()
        pages = sorted(site_dir.glob("*.html"))
        if pages:
            _typography_rows(rep, pages)
        else:
            rep.add("files_present", "FAIL", f"no .html in {site_dir}")
    else:
        rep = check_site(site_dir, expect)
    c = rep.counts()
    print(f"result: {c['PASS']} pass / {c['FAIL']} fail / {c['WARN']} warn / {c['SKIP']} skip")
    return 0 if rep.ok() else 1


if __name__ == "__main__":
    raise SystemExit(main())
