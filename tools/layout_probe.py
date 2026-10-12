"""tools/layout_probe.py - static layout-probe producer for the visual_probe gate.

Writes ``layout-probe.json`` beside a built site's top-level ``*.html`` pages so
``lib/check.py::_visual_probe_row`` (and the read-only ``lib/ui_render.py``
``probe_status`` face) can bind the probe to the exact bytes: sha256 over the
sorted top-level ``*.html`` files, ``hexdigest()[:16]``, stored as both
``html_hash`` and ``hash``. The checker reads ``rows`` (falling back to
``profiles``) and FAILs the ``visual_probe`` row when the file is unreadable,
when the stored hash no longer matches (stale), or when any row carries
``status == "FAIL"``. Anything else -- PASS, SKIP, WARN -- keeps the row green.

Stdlib only. No browser, no network, no Pillow: every probe below is decided
from the HTML and CSS text. A condition that cannot be decided statically is
never FAIL (it is SKIP or it is not probed at all).

Probes (one row each, ``status`` in PASS/FAIL/SKIP):

- ``viewport_meta``: every page carries ``name="viewport"``.
- ``img_dimensions``: every ``<img>`` names ``width`` + ``height`` (a page
  with no ``<img>`` passes, mirroring the ``layout_stability`` checker row).
- ``wide_fixed``: no unguarded fixed ``width``/``min-width`` over 412px (the
  widest static phone viewport, 360/390/412) in inline ``<style>`` rules or
  ``style=""`` attributes unless the same rule sets ``max-width``; no numeric
  ``width`` attribute over 412px on replaced elements without a ``max-width``
  guard in the tag's own style.
- ``no_remote_assets``: no remote ``http(s)``/protocol-relative URL in markup
  or CSS (JSON-LD script bodies excluded: ``@context`` identifiers are not
  fetches), mirroring the checker's ``no_hotlink`` row.

Usage (from the repo root)::

    python tools/layout_probe.py sites/<name>            # write layout-probe.json
    python tools/layout_probe.py sites/<name> --stdout   # print JSON, still writes
    python tools/layout_probe.py --selftest              # static battery + checker parity

Exit codes: 0 when every row is PASS/SKIP, 1 when any row FAILs (the file is
still written -- the checker must see the failure, not an absence), 2 on
usage errors (missing site dir, no built pages).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PROBE_FILENAME = "layout-probe.json"
GENERATOR = "tools/layout_probe.py"
VERSION = 1

#: Widest static phone viewport (360/390/412); fixed boxes wider than this
#: cannot fit a phone screen without scrolling or clipping.
WIDE_PX = 412

#: Row statuses this producer emits. The checker only treats FAIL as failure.
STATUSES = ("PASS", "FAIL", "SKIP")

_LD_JSON_RE = re.compile(
    r"<script\b[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>.*?</script>",
    re.IGNORECASE | re.DOTALL,
)
_STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
_STYLE_ATTR_RE = re.compile(r'\bstyle\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', re.IGNORECASE)
_IMG_RE = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
_ATTR_RE_CACHE: dict[str, re.Pattern] = {}


def _attr(attrs: str, name: str) -> str | None:
    """Quoted HTML attribute value, mirroring ``lib/check.py::_attr``."""
    rx = _ATTR_RE_CACHE.get(name)
    if rx is None:
        rx = re.compile(
            rf"""\b{re.escape(name)}\s*=\s*(?:"([^"]*)"|'([^']*)')""",
            re.IGNORECASE,
        )
        _ATTR_RE_CACHE[name] = rx
    match = rx.search(attrs)
    if not match:
        return None
    return match.group(1) if match.group(1) is not None else match.group(2)


def _pages(site_dir: Path) -> list[Path]:
    """Sorted top-level ``*.html`` pages: the exact set the checker hashes."""
    return sorted(site_dir.glob("*.html"))


def _html_hash(pages: list[Path]) -> str:
    """Binding digest: sha256 over concatenated page bytes, ``hexdigest[:16]``."""
    digest = hashlib.sha256()
    for page in pages:
        digest.update(page.read_bytes())
    return digest.hexdigest()[:16]


def _read(page: Path) -> str:
    return page.read_text(encoding="utf-8", errors="replace")


def _css_of(html: str) -> str:
    return "\n".join(_STYLE_RE.findall(html))


def _strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def _probe_viewport(pages: list[Path]) -> dict:
    missing = [p.name for p in pages if 'name="viewport"' not in _read(p)]
    if missing:
        return {
            "name": "viewport_meta",
            "status": "FAIL",
            "detail": "missing viewport meta: " + ", ".join(missing[:6]),
        }
    return {
        "name": "viewport_meta",
        "status": "PASS",
        "detail": f"{len(pages)} page(s) carry a viewport meta",
    }


def _probe_img_dimensions(pages: list[Path]) -> dict:
    bad: list[str] = []
    for page in pages:
        html = _read(page)
        for match in _IMG_RE.finditer(html):
            attrs = match.group(1)
            if not (_attr(attrs, "width") and _attr(attrs, "height")):
                bad.append(
                    f"{page.name}: img without width+height: "
                    f"{(_attr(attrs, 'src') or 'img')[:40]}"
                )
                break
    if bad:
        return {"name": "img_dimensions", "status": "FAIL", "detail": "; ".join(bad[:6])}
    return {
        "name": "img_dimensions",
        "status": "PASS",
        "detail": f"{len(pages)} page(s), img dimensions set",
    }


_FIXED_RE = re.compile(
    r"(?:^|[;{])\s*(?:width|min-width)\s*:\s*(\d+(?:\.\d+)?)px",
    re.IGNORECASE,
)
_WIDTH_ATTR_RE = re.compile(
    r"<(?:img|iframe|video|table|pre|svg|canvas|embed|object)\b[^>]*"
    r"\bwidth\s*=\s*(?:\"(\d+(?:\.\d+)?)\"|'(\d+(?:\.\d+)?)'|(\d+(?:\.\d+)?)(?=[\s>/]))",
    re.IGNORECASE,
)


def _probe_wide_fixed(pages: list[Path]) -> dict:
    bad: list[str] = []
    for page in pages:
        html = _read(page)
        blocks = [(m.group(1) or m.group(2) or "") for m in _STYLE_ATTR_RE.finditer(html)]
        blocks += [
            decls
            for _, decls in re.findall(r"([^{}]+)\{([^{}]*)\}", _strip_comments(_css_of(html)))
        ]
        for block in blocks:
            if "max-width" in block.lower():
                continue
            hit = False
            for match in _FIXED_RE.finditer(";" + block):
                try:
                    width = float(match.group(1))
                except ValueError:
                    continue
                if width > WIDE_PX:
                    bad.append(
                        f"{page.name}: fixed "
                        f"{match.group(0).strip(' ;{')[:40]} over {WIDE_PX}px"
                    )
                    hit = True
                    break
            if hit:
                break
        for match in _WIDTH_ATTR_RE.finditer(html):
            raw = match.group(1) or match.group(2) or match.group(3) or ""
            try:
                width = float(raw)
            except ValueError:
                continue
            tag = match.group(0)[: match.group(0).find("width")].strip("< ")
            style = _attr(match.group(0), "style") or ""
            if width > WIDE_PX and "max-width" not in style.lower():
                bad.append(f"{page.name}: <{tag[:20]} width={raw} over {WIDE_PX}px")
                break
        if len(bad) >= 6:
            break
    if bad:
        return {"name": "wide_fixed", "status": "FAIL", "detail": "; ".join(bad[:6])}
    return {
        "name": "wide_fixed",
        "status": "PASS",
        "detail": f"{len(pages)} page(s), no fixed box over {WIDE_PX}px",
    }


_REMOTE_RE = re.compile(
    r"https?://[^\s\"'<>]+"
    r"|\bsrc\s*=\s*[\"']//[^\"']+"
    r"|\bhref\s*=\s*[\"']//[^\"']+"
    r"|url\(\s*[\"']?\s*(?:https?:)?//[^)]+"
    r"|@import\s+[^;]*https?://[^;]+"
    r"|\bsrcset\s*=\s*[\"'][^\"']*https?://[^\"']*",
    re.IGNORECASE,
)


def _probe_no_remote(pages: list[Path]) -> dict:
    bad: list[str] = []
    for page in pages:
        stripped = _LD_JSON_RE.sub("<script></script>", _read(page))
        match = _REMOTE_RE.search(stripped)
        if match:
            bad.append(f"{page.name}: remote URL in output: {match.group(0)[:80]}")
    if bad:
        return {"name": "no_remote_assets", "status": "FAIL", "detail": "; ".join(bad[:6])}
    return {
        "name": "no_remote_assets",
        "status": "PASS",
        "detail": f"{len(pages)} page(s), local only",
    }


PROBES = (_probe_viewport, _probe_img_dimensions, _probe_wide_fixed, _probe_no_remote)


def build_probe(site_dir: Path) -> dict:
    """Probe every page and bind the rows to the current HTML bytes."""
    site = Path(site_dir)
    pages = _pages(site)
    if not pages:
        raise FileNotFoundError(f"no built pages (*.html) in {site}")
    digest = _html_hash(pages)
    rows = [fn(pages) for fn in PROBES]
    for row in rows:
        if row.get("status") not in STATUSES:
            raise ValueError(f"probe {row.get('name')}: bad status {row.get('status')!r}")
    return {
        "generator": GENERATOR,
        "version": VERSION,
        "html_hash": digest,
        "hash": digest,
        "pages": [p.name for p in pages],
        "rows": rows,
    }


def write_probe(site_dir: Path, out: str | None = None) -> Path:
    """Build the probe and write ``layout-probe.json`` beside the pages."""
    target = Path(site_dir) / (out or PROBE_FILENAME)
    data = build_probe(Path(site_dir))
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return target


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Write layout-probe.json bound to a built site's HTML bytes "
        "(stdlib only; feeds the visual_probe gate).",
    )
    ap.add_argument("site", nargs="?", help="built site dir holding top-level *.html")
    ap.add_argument(
        "--out",
        default=None,
        help="probe file name inside the site dir " f"(default: {PROBE_FILENAME})",
    )
    ap.add_argument("--stdout", action="store_true", help="also print the probe JSON to stdout")
    ap.add_argument(
        "--selftest",
        action="store_true",
        help="run the static battery (temp dirs + checker parity)",
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.site:
        print("layout_probe: need a site dir (or --selftest)", file=sys.stderr)
        return 2
    site = Path(args.site)
    if not site.is_dir():
        print(f"layout_probe: not a directory: {site}", file=sys.stderr)
        return 2
    try:
        data = build_probe(site)
    except FileNotFoundError as exc:
        print(f"layout_probe: {exc}", file=sys.stderr)
        return 2
    target = site / (args.out or PROBE_FILENAME)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    failed = [r for r in data["rows"] if r.get("status") == "FAIL"]
    summary = (
        f"layout_probe: wrote {target} "
        f"(html {data['html_hash']}, "
        f"{len(data['rows']) - len(failed)}/{len(data['rows'])} pass)"
    )
    print(summary)
    if args.stdout:
        print(json.dumps(data, indent=2))
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# Selftest: static battery on temp dirs plus direct parity with the checker
# row and the read-only UI face. Run: ``python tools/layout_probe.py --selftest``.
# ---------------------------------------------------------------------------


def _expect(cond: bool, msg: str, failures: list[str]) -> None:
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        failures.append(msg)


def selftest() -> int:
    import shutil
    import tempfile

    failures: list[str] = []
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from lib import check as check_mod
    from lib import ui_render

    def _write_page(site: Path, name: str = "index.html", **kw: str) -> None:
        viewport = kw.get("viewport", True)
        extra_head = kw.get("extra_head", "")
        extra_body = kw.get("extra_body", "")
        style = kw.get("style", "")
        meta = (
            ('<meta name="viewport" ' 'content="width=device-width,initial-scale=1">')
            if viewport
            else ""
        )
        site.mkdir(parents=True, exist_ok=True)
        (site / name).write_text(
            '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            + meta
            + "\n<title>t</title>\n"
            + extra_head
            + ("<style>\n" + style + "\n</style>\n" if style else "")
            + "</head>\n<body>\n"
            + extra_body
            + "\n</body>\n</html>\n",
            encoding="utf-8",
        )

    def _visual(site: Path) -> dict | None:
        rep = check_mod.check_site(site, quiet=True)
        for row in rep.rows:
            name = row.get("name") if isinstance(row, dict) else getattr(row, "name", None)
            if name == "visual_probe":
                if isinstance(row, dict):
                    return row
                return {"name": name, "status": row.status, "detail": row.detail}
        return None

    tmp = Path(tempfile.mkdtemp(prefix="layout-probe-selftest-"))
    try:
        # 1) No built pages is a usage error, never a probe file.
        empty = tmp / "empty"
        empty.mkdir()
        try:
            build_probe(empty)
            _expect(False, "empty site raises FileNotFoundError", failures)
        except FileNotFoundError:
            _expect(True, "empty site raises FileNotFoundError", failures)

        # 2) Missing probe: checker SKIP, UI NOT_RUN/SKIP.
        site = tmp / "site"
        _write_page(site)
        state = ui_render.probe_status(site)
        _expect(
            state["state"] == "NOT_RUN" and state["row"] == "SKIP",
            f"missing probe is NOT_RUN/SKIP: {state}",
            failures,
        )
        visual = _visual(site)
        _expect(
            visual is not None and visual.get("status") == "SKIP",
            f"checker agrees: visual_probe SKIP without a probe: {visual}",
            failures,
        )

        # 3) Fresh producer output binds: checker PASS, UI PASS.
        target = write_probe(site)
        _expect(target.name == PROBE_FILENAME, "probe file name is layout-probe.json", failures)
        data = json.loads(target.read_text(encoding="utf-8"))
        _expect(
            data.get("html_hash") == data.get("hash") and len(data["html_hash"]) == 16,
            "html_hash/hash aliases agree (16 hex chars)",
            failures,
        )
        _expect(
            all(r.get("status") in STATUSES for r in data["rows"]),
            "row statuses are PASS/FAIL/SKIP tokens",
            failures,
        )
        state = ui_render.probe_status(site)
        _expect(
            state["state"] == "PASS" and state["row"] == "PASS",
            f"bound probe is PASS/PASS: {state}",
            failures,
        )
        visual = _visual(site)
        _expect(
            visual is not None and visual.get("status") == "PASS",
            f"checker agrees: visual_probe PASS on a bound probe: {visual}",
            failures,
        )

        # 4) One-byte edit stales the binding: checker FAIL, UI STALE/FAIL.
        (site / "index.html").write_text(
            (site / "index.html").read_text(encoding="utf-8").replace("</body>", "x</body>"),
            encoding="utf-8",
        )
        state = ui_render.probe_status(site)
        _expect(
            state["state"] == "STALE" and state["row"] == "FAIL",
            f"edited html is STALE/FAIL: {state}",
            failures,
        )
        visual = _visual(site)
        _expect(
            visual is not None
            and visual.get("status") == "FAIL"
            and "stale" in str(visual.get("detail", "")).lower(),
            f"checker agrees: visual_probe FAIL stale: {visual}",
            failures,
        )

        # 5) Bound hash with a FAIL row refuses: checker FAIL, UI FAIL_ROWS/FAIL.
        write_probe(site)
        data = json.loads((site / PROBE_FILENAME).read_text(encoding="utf-8"))
        data["rows"].append(
            {"name": "wide_fixed", "status": "FAIL", "detail": "synthetic overflow"}
        )
        (site / PROBE_FILENAME).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        state = ui_render.probe_status(site)
        _expect(
            state["state"] == "FAIL_ROWS" and state["row"] == "FAIL",
            f"bound FAIL row is FAIL_ROWS/FAIL: {state}",
            failures,
        )
        visual = _visual(site)
        _expect(
            visual is not None and visual.get("status") == "FAIL",
            f"checker agrees: visual_probe FAIL on FAIL rows: {visual}",
            failures,
        )

        # 6) Unreadable probe: checker FAIL, UI UNREADABLE/FAIL.
        (site / PROBE_FILENAME).write_text("{not json", encoding="utf-8")
        state = ui_render.probe_status(site)
        _expect(
            state["state"] == "UNREADABLE" and state["row"] == "FAIL",
            f"corrupt probe is UNREADABLE/FAIL: {state}",
            failures,
        )
        visual = _visual(site)
        _expect(
            visual is not None
            and visual.get("status") == "FAIL"
            and "unreadable" in str(visual.get("detail", "")).lower(),
            f"checker agrees: visual_probe FAIL unreadable: {visual}",
            failures,
        )

        # 7) Each probe FAILs honestly on a violating page.
        cases = [
            ({"viewport": False}, "viewport_meta"),
            ({"extra_body": '<img src="a.png">'}, "img_dimensions"),
            ({"style": ".wide { width: 900px; }"}, "wide_fixed"),
            (
                {"extra_body": '<img src="https://example.com/a.png" width="10" ' 'height="10">'},
                "no_remote_assets",
            ),
        ]
        for kw, want in cases:
            bad = tmp / f"bad-{want}"
            _write_page(bad, **kw)
            rows = {r["name"]: r for r in build_probe(bad)["rows"]}
            _expect(
                rows[want]["status"] == "FAIL",
                f"{want} FAILs its violating page ({rows[want]['detail'][:60]})",
                failures,
            )
            if want == "wide_fixed":
                _expect(
                    rows["viewport_meta"]["status"] == "PASS",
                    "wide_fixed fixture keeps sibling rows green",
                    failures,
                )

        # 8) Guarded wide rules and remote-free pages stay green.
        good = tmp / "good-guards"
        _write_page(
            good,
            style=".wide { width: 900px; max-width: 100%; }\n"
            "@media (min-width: 861px) { .x { width: 40px; } }",
            extra_body='<img src="a.png" width="10" height="10">',
        )
        rows = {r["name"]: r for r in build_probe(good)["rows"]}
        _expect(
            all(r["status"] == "PASS" for r in rows.values()),
            f"guarded page is all-PASS: {rows}",
            failures,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print(f"layout_probe selftest FAIL ({len(failures)}): " + "; ".join(failures))
        return 1
    print(
        "layout_probe selftest ok (empty, NOT_RUN, PASS, STALE, "
        "FAIL_ROWS, UNREADABLE, per-probe FAILs, guards green)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
