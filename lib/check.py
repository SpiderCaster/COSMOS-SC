"""Built-in checks, aligned with the fleet website_checker rails.

Mirrors the fleet SAMPLE patterns (no_sample), the hotlink blocklist, and adds
site-local checks: internal anchors/pages resolve, required meta present,
noindex matches the build flag, no soft placeholder text in visible copy.
Exit code is nonzero on any FAIL so it can gate CI or a deploy.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

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


class Report:
    def __init__(self, quiet: bool = False):
        self.rows: list[dict] = []
        self.quiet = quiet  # quiet=True: never print (MCP stdio channel stays clean)

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.rows.append({"name": name, "status": status, "detail": detail})
        if self.quiet:
            return
        mark = {"PASS": "[pass]", "FAIL": "[FAIL]", "WARN": "[warn]", "SKIP": "[skip]"}[status]
        line = f"  {mark} {name}"
        if detail:
            line += f" - {detail}"
        print(line)

    def counts(self) -> dict:
        c = {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0}
        for r in self.rows:
            c[r["status"]] += 1
        return c

    def ok(self) -> bool:
        return self.counts()["FAIL"] == 0


def check_site(site_dir: Path, expect_noindex: bool | None = None, quiet: bool = False) -> Report:
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
    anchor_ids = set(re.findall(r'<section id="([^"]+)"', all_html))
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

    # 7) token ledger present (from build report)
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

    return rep


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m lib.check <site_dir> [--expect-noindex|--expect-indexable]")
        return 2
    site_dir = Path(sys.argv[1])
    expect = None
    if "--expect-noindex" in sys.argv:
        expect = True
    if "--expect-indexable" in sys.argv:
        expect = False
    print(f"checking {site_dir}")
    rep = check_site(site_dir, expect)
    c = rep.counts()
    print(f"result: {c['PASS']} pass / {c['FAIL']} fail / {c['WARN']} warn / {c['SKIP']} skip")
    return 0 if rep.ok() else 1


if __name__ == "__main__":
    raise SystemExit(main())
