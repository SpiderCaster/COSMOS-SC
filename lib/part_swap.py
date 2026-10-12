"""Swap one wrapped part on a static page. Stdlib only. Does not publish."""

from __future__ import annotations

import re

_RAW_TEXT = frozenset({"script", "style", "textarea", "title"})
_RAW_CLOSE = {
    name: re.compile("</" + name + r"\s*>", re.IGNORECASE) for name in _RAW_TEXT
}


class PartSwapError(Exception):
    """Raised when the part style or part div is not on the page."""


def wrap_part(catalog_id: str, css: str, fragment: str) -> str:
    """Return the style tag and ``<div data-sc-part>`` for one part."""
    style, block = _pieces(catalog_id, css, fragment)
    return style + "\n" + block


def replace_part(html: str, catalog_id: str, css: str, fragment: str) -> str:
    """Replace the style and div for ``catalog_id``. Leave every other part."""
    style_span = _element_span(html, "style", "data-sc-tool", catalog_id)
    div_span = _element_span(html, "div", "data-sc-part", catalog_id)
    if style_span is None or div_span is None:
        raise PartSwapError("part not on page")
    style, block = _pieces(catalog_id, css, fragment)
    if _contains(div_span, style_span) or _contains(style_span, div_span):
        outer = div_span if _contains(div_span, style_span) else style_span
        return _splice(html, outer, style + "\n" + block)
    if _overlaps(style_span, div_span):
        # Crossed tags are not a wrapped part.
        raise PartSwapError("part not on page")
    if style_span[0] > div_span[0]:
        html = _splice(html, style_span, style)
        return _splice(html, div_span, block)
    html = _splice(html, div_span, block)
    return _splice(html, style_span, style)


def bind_hashes(html: str) -> str:
    """Rewrite ``href="#missing"`` to ``href="#main"`` when ``id="main"`` exists."""
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    if "main" not in ids:
        return html

    def repl(match: re.Match[str]) -> str:
        if match.group(1) in ids:
            return match.group(0)
        return 'href="#main"'

    return re.sub(r'href="#([^"]+)"', repl, html)


def _pieces(catalog_id: str, css: str, fragment: str) -> tuple[str, str]:
    ident = _attr(catalog_id)
    css_safe = _neutralize_style(css).rstrip(" \t\r\n")
    style = f'<style data-sc-tool="{ident}">\n{css_safe}\n</style>'
    block = f'<div data-sc-part="{ident}">{fragment}</div>'
    return style, block


def _neutralize_style(css: str) -> str:
    """Break a literal ``</style`` so the style element stays open."""
    out: list[str] = []
    token = "</style"
    size = len(token)
    i = 0
    n = len(css)
    while i < n:
        if i + size <= n and css[i : i + size].lower() == token:
            out.append("<\\/style")
            i += size
            continue
        out.append(css[i])
        i += 1
    return "".join(out)


def _attr(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _element_span(
    html: str, tag: str, attr: str, value: str
) -> tuple[int, int] | None:
    opened = _find_open_tag(html, tag, attr, value)
    if opened is None:
        return None
    start, content = opened
    if tag.lower() in _RAW_TEXT:
        end = _raw_close(html, content, tag)
    else:
        end = _balanced_end(html, content, tag)
    if end is None:
        return None
    return start, end


def _find_open_tag(
    html: str, tag: str, attr: str, value: str
) -> tuple[int, int] | None:
    escaped = _attr(value)
    want = tag.lower()
    for start, end, name, closing, attrs_start, attrs_end in _walk_tags(html):
        if closing or name != want:
            continue
        if _has_attr(html[attrs_start:attrs_end], attr, escaped):
            return start, end
    return None


def _walk_tags(html: str, start: int = 0):
    """Yield tags. Bodies of raw-text elements are not scanned."""
    i = start
    n = len(html)
    while i < n:
        lt = html.find("<", i)
        if lt < 0:
            return
        if html.startswith("<!--", lt):
            end = html.find("-->", lt + 4)
            i = n if end < 0 else end + 3
            continue
        if html.startswith("<!", lt) or html.startswith("<?", lt):
            end = html.find(">", lt + 2)
            i = n if end < 0 else end + 1
            continue
        parsed = _parse_tag(html, lt)
        if parsed is None:
            i = lt + 1
            continue
        name, end, closing, attrs_start, attrs_end = parsed
        yield lt, end, name, closing, attrs_start, attrs_end
        if not closing and name in _RAW_TEXT:
            raw_end = _raw_close(html, end, name)
            if raw_end is None:
                return
            i = raw_end
            continue
        i = end


def _parse_tag(
    html: str, lt: int
) -> tuple[str, int, bool, int, int] | None:
    n = len(html)
    i = lt + 1
    if i >= n:
        return None
    closing = False
    if html[i] == "/":
        closing = True
        i += 1
    if i >= n or not html[i].isalpha():
        return None
    name_at = i
    i += 1
    while i < n and (html[i].isalnum() or html[i] in "-:"):
        i += 1
    name = html[name_at:i].lower()
    attrs_start = i
    quote = None
    while i < n:
        char = html[i]
        if quote:
            if char == quote:
                quote = None
            i += 1
            continue
        if char in "\"'":
            quote = char
            i += 1
            continue
        if char == ">":
            return name, i + 1, closing, attrs_start, i
        i += 1
    return None


def _has_attr(raw: str, name: str, value: str) -> bool:
    return any(val == value for _start, _end, val in _attr_value_spans(raw, name))


def _attr_value_spans(raw: str, name: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    i = 0
    n = len(raw)
    want = name.lower()
    while i < n:
        while i < n and raw[i].isspace():
            i += 1
        if i >= n:
            break
        if raw[i] == "/":
            i += 1
            continue
        start = i
        while i < n and (raw[i].isalnum() or raw[i] in "-_:"):
            i += 1
        attr_name = raw[start:i].lower()
        while i < n and raw[i].isspace():
            i += 1
        if i >= n or raw[i] != "=":
            continue
        i += 1
        while i < n and raw[i].isspace():
            i += 1
        if i >= n:
            break
        if raw[i] in "\"'":
            i += 1
            vstart = i
            while i < n and raw[i] != raw[vstart - 1]:
                i += 1
            vend = i
            if i < n:
                i += 1
        else:
            vstart = i
            while i < n and not raw[i].isspace() and raw[i] != ">":
                i += 1
            vend = i
        if attr_name == want:
            spans.append((vstart, vend, raw[vstart:vend]))
    return spans


def _raw_close(html: str, content_start: int, tag: str) -> int | None:
    pattern = _RAW_CLOSE.get(tag.lower())
    if pattern is None:
        pattern = re.compile("</" + re.escape(tag) + r"\s*>", re.IGNORECASE)
    match = pattern.search(html, content_start)
    if match is None:
        return None
    return match.end()


def _balanced_end(html: str, content_start: int, tag: str) -> int | None:
    depth = 1
    want = tag.lower()
    for _start, end, name, closing, _attrs_start, _attrs_end in _walk_tags(
        html, content_start
    ):
        if name != want:
            continue
        if closing:
            depth -= 1
            if depth == 0:
                return end
            continue
        depth += 1
    return None


def _contains(outer: tuple[int, int], inner: tuple[int, int]) -> bool:
    return outer[0] <= inner[0] and inner[1] <= outer[1] and outer != inner


def _overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def _splice(html: str, span: tuple[int, int], repl: str) -> str:
    start, end = span
    return html[:start] + repl + html[end:]
