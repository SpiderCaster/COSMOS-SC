"""Mobile selftest for the SpiderCaster renderer.

Builds a tiny temp project and calls the crew hands the way lib/regress.py
does: plan_offline, then render.assemble. No network. Does not publish.
"""
from __future__ import annotations

import importlib
import tempfile
import time
from pathlib import Path

import lib.render as render_mod
from lib.hands import plan_offline

# (needle, must_be_present). Order is the report order. Do not loosen these.
CHECKS = (
    ("aspect-ratio:16/9", True),
    ("height:168px", False),
    ('href="#main"', True),
    ("scroll-margin-top", True),
    ("about-panel", False),
    ("max-width:860px", True),
    ("phone-bar", True),
    ("tel:5550142288", True),
    ("flex:0 1 auto;max-width:4.5rem", True),
    (".hero .lede{margin-bottom:8px}", True),
    (".menu-group{margin-bottom:0}", True),
    ("text-wrap:balance", True),
    ("tabular-nums", True),
    (".card:has(.chip)", True),
    (".grid.c3{gap:0", True),
    (".points .pt + .pt{border-top", True),
)


def _fail(assertion: str) -> None:
    print(assertion)
    raise SystemExit(2)


def _write_project(root: Path) -> Path:
    """Same tiny copy shape lib/regress.py plans. contact.md sorts before hours.md."""
    project = root / "project"
    copy = project / "copy"
    copy.mkdir(parents=True)
    (project / "brief.md").write_text(
        "# Harbor Desk\n\nA quiet desk. Local copy only.\n",
        encoding="utf-8",
    )
    (copy / "overview.md").write_text(
        "\n".join((
            "# Harbor Desk",
            "",
            "A quiet desk keeps the first note for visitors who walk in.",
            "",
            "The second paragraph stays on the page without a heading.",
            "",
        )),
        encoding="utf-8",
    )
    (copy / "hours.md").write_text(
        "\n".join((
            "# Hours",
            "",
            "Open Tuesday to Sunday, 8am to 6pm.",
            "",
        )),
        encoding="utf-8",
    )
    (copy / "contact.md").write_text(
        "\n".join((
            "# Contact",
            "",
            "(555) 014-2288",
            "",
            "Ask for the desk if the line is busy.",
            "",
        )),
        encoding="utf-8",
    )
    return project


def _index_html(project: Path) -> str:
    ctx = {"project": str(project), "template": "editorial", "dark": True}
    planned = plan_offline(ctx)
    if planned.get("status") != "PASS":
        _fail(str(planned.get("detail") or "plan_offline failed"))
    site = ctx.get("site_ir")
    if not isinstance(site, dict):
        _fail("plan_offline did not return site_ir")
    pages = render_mod.assemble(site, noindex=True)
    for page in pages:
        if page.get("file") == "index.html":
            return str(page.get("html") or "")
    _fail("assemble did not return index.html")
    return ""


def _gaps(html: str) -> list[str]:
    gaps: list[str] = []
    for needle, want in CHECKS:
        found = needle in html
        if want and not found:
            gaps.append(f"missing {needle}")
        elif not want and found:
            gaps.append(f"still present {needle}")
    return gaps


def _render_once() -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        html = _index_html(_write_project(Path(tmp)))
    return _gaps(html)


def main() -> int:
    gaps = _render_once()
    if gaps:
        time.sleep(60)
        importlib.reload(render_mod)
        gaps = _render_once()
    if gaps:
        print("\n".join(gaps))
        return 2
    print("mobile selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
