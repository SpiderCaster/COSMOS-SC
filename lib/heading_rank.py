"""Heading order on the page outline. Part chrome is ignored.

A skip is an ``h3`` after an ``h1`` with no ``h2`` between them. Headings
inside ``data-sc-part`` belong to the catalog part, not the copy outline.
"""
from __future__ import annotations

from html.parser import HTMLParser

_HEADS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class _Outline(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.levels: list[int] = []
        self._part = 0
        self._stack: list[bool] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        opened = name == "div" and any(key == "data-sc-part" for key, _value in attrs)
        self._stack.append(opened)
        if opened:
            self._part += 1
        if self._part == 0 and name in _HEADS:
            self.levels.append(int(name[1]))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "div" or not self._stack:
            return
        if self._stack.pop() and self._part:
            self._part -= 1


def heading_levels(html: str) -> list[int]:
    parser = _Outline()
    parser.feed(html)
    parser.close()
    return parser.levels


def heading_skips(html: str) -> list[str]:
    """Forward skips in the outline. An empty list means the order is intact."""
    hits: list[str] = []
    previous = 0
    for level in heading_levels(html):
        if previous and level > previous + 1:
            hits.append(f"h{previous} to h{level}")
        previous = level
    return hits
