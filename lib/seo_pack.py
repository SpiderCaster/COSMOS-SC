"""Sitemap and robots files from pages already on disk. Stdlib only.

A noindex site gets ``Disallow: /`` and no sitemap. An indexable site gets a
sitemap only when the caller passes an origin. This module does not invent a
hostname, a page, or a ranking claim.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

_ORIGIN = re.compile(r"https?://[A-Za-z0-9.-]+(?::\d+)?\Z")
_DESC_LINE = re.compile(r"(?im)^[ \t]*description[ \t]*:[ \t]*(.+)$")


class SeoPackError(Exception):
    pass


def clean_host(host: str) -> str:
    """Return an origin with no path, or ``''``. Raise on a bad host."""
    text = str(host or "").strip().rstrip("/")
    if not text:
        return ""
    if not _ORIGIN.fullmatch(text):
        raise SeoPackError("host must be an origin like https://example.com")
    return text


def descriptions_by_stem(project: Path) -> dict[str, str]:
    """Map a copy filename stem to its ``Description:`` line. No invented text."""
    copy_dir = Path(project) / "copy"
    found: dict[str, str] = {}
    if not copy_dir.is_dir():
        return found
    for path in sorted(copy_dir.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path.suffix.lower() not in {".md", ".markdown", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        line = description_line(text)
        if line:
            found[path.stem.lower()] = line
    return found


def description_line(text: str) -> str:
    """Return the first ``Description:`` line from copy, or ``''``."""
    match = _DESC_LINE.search(str(text or ""))
    if not match:
        return ""
    return " ".join(match.group(1).split())


def robots_text(*, indexable: bool, host: str = "") -> str:
    if not indexable:
        return "User-agent: *\nDisallow: /\n"
    lines = ["User-agent: *", "Allow: /"]
    origin = clean_host(host)
    if origin:
        lines.append(f"Sitemap: {origin}/sitemap.xml")
    return "\n".join(lines) + "\n"


def _xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def sitemap_xml(pages: list[tuple[str, float]], host: str) -> str:
    """Absolute URLs for filenames that already exist. No priority values."""
    origin = clean_host(host)
    if not origin:
        raise SeoPackError("sitemap needs a host")
    rows: list[str] = []
    for name, stamp in pages:
        file_name = Path(str(name)).name
        if not file_name.lower().endswith(".html"):
            continue
        when = datetime.fromtimestamp(float(stamp), UTC).strftime("%Y-%m-%d")
        loc = f"{origin}/{file_name}"
        rows.append(f"  <url><loc>{_xml(loc)}</loc><lastmod>{when}</lastmod></url>")
    body = "\n".join(rows)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body
        + ("\n" if body else "")
        + "</urlset>\n"
    )


def _html_pages(site_dir: Path, skip: set[str]) -> list[tuple[str, float]]:
    found: list[tuple[str, float]] = []
    for path in sorted(site_dir.glob("*.html"), key=lambda item: item.name.lower()):
        if path.name.lower() in skip:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "noindex" in text.lower():
            continue
        found.append((path.name, path.stat().st_mtime))
    return found


def write_pack(site_dir: Path, *, indexable: bool, host: str = "") -> dict:
    """Write ``robots.txt``. Write ``sitemap.xml`` only when indexable and hosted.

    A noindex directory loses ``sitemap.xml`` so a later preview does not
    advertise URLs. Returns ``{"robots", "sitemap"}`` with the sitemap path
    empty when none was written.
    """
    site_dir = Path(site_dir)
    if not site_dir.is_dir():
        raise SeoPackError(f"site missing: {site_dir}")
    origin = clean_host(host)
    robots = site_dir / "robots.txt"
    sitemap = site_dir / "sitemap.xml"
    pages = _html_pages(site_dir, set()) if indexable else []
    emit = bool(indexable and pages)
    robots.write_text(
        robots_text(indexable=emit, host=origin if emit else ""),
        encoding="utf-8",
        newline="\n",
    )
    wrote_sitemap = ""
    if emit and origin:
        sitemap.write_text(sitemap_xml(pages, origin), encoding="utf-8", newline="\n")
        wrote_sitemap = str(sitemap)
    elif sitemap.is_file():
        sitemap.unlink()
    return {"robots": str(robots), "sitemap": wrote_sitemap}
