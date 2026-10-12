"""Prove robots and sitemap rules. Run: python lib/seo_pack_selftest.py"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.seo_pack import (
    SeoPackError,
    clean_host,
    description_line,
    sitemap_xml,
    write_pack,
)


def main() -> int:
    if description_line("Hello\nDescription: Real line.\n") != "Real line.":
        raise SystemExit("description line missed")
    if description_line("no label here"):
        raise SystemExit("invented a description")
    try:
        clean_host("https://example.com/path")
    except SeoPackError:
        pass
    else:
        raise SystemExit("path host was accepted")
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        (site / "index.html").write_text("<html>noindex</html>", encoding="utf-8")
        (site / "sitemap.xml").write_text("<old>", encoding="utf-8")
        pack = write_pack(site, indexable=False)
        robots = (site / "robots.txt").read_text(encoding="utf-8")
        if "Disallow: /" not in robots or (site / "sitemap.xml").exists():
            raise SystemExit("noindex pack advertised urls")
        if pack["sitemap"]:
            raise SystemExit("noindex returned a sitemap")
        (site / "index.html").write_text("<html>hello</html>", encoding="utf-8")
        write_pack(site, indexable=True, host="https://example.com")
        xml = (site / "sitemap.xml").read_text(encoding="utf-8")
        if "https://example.com/index.html" not in xml or "<priority>" in xml:
            raise SystemExit("sitemap shape")
        allow = (site / "robots.txt").read_text(encoding="utf-8")
        if "Sitemap: https://example.com/sitemap.xml" not in allow:
            raise SystemExit("robots missing sitemap")
    sample = sitemap_xml([("index.html", 0)], "https://example.com")
    if "index.html" not in sample:
        raise SystemExit("sitemap writer")
    print("seo_pack selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
