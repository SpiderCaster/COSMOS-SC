"""Regression selftest for the offline plan and assemble path.

Builds a tiny temp project from copy files and calls the crew hands:
plan_offline, then render.assemble. No network. Does not publish.
"""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

from lib.hands import plan_offline
from lib.render import assemble

PHONE = "(555) 014-2288"
SENTENCE = "Ask for the desk if the line is busy."


def _fail(assertion: str) -> None:
    print(assertion)
    raise SystemExit(2)


def _write_project(root: Path) -> Path:
    """contact.md sorts before hours.md, so the next titled section is Contact."""
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
            "- Keeps the whole site",
            "  honest during JSON-repair",
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
    (copy / "menu.md").write_text(
        "\n".join((
            "# Menu",
            "",
            "- Jasmine Pearl - $4.50",
            "",
        )),
        encoding="utf-8",
    )
    (copy / "contact.md").write_text(
        "\n".join((
            "# Contact",
            "",
            PHONE,
            "",
            SENTENCE,
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
    pages = assemble(site, noindex=True)
    for page in pages:
        if page.get("file") == "index.html":
            return str(page.get("html") or "")
    _fail("assemble did not return index.html")
    return ""


def _check(html: str) -> None:
    texts = re.findall(r">([^<]*)<", html)
    if not any("JSON-repair" in text and "whole site" in text for text in texts):
        _fail("JSON-repair is not in the same text as whole site")

    if "<h2>Menu</h2>" not in html or "<h3>Menu</h3>" in html:
        _fail("there is no <h3>Menu</h3> when the section h2 is Menu")

    if PHONE not in html or SENTENCE not in html:
        _fail("the phone number is not in the same <p> as the following sentence")
    for para in re.findall(r"<p\b[^>]*>[\s\S]*?</p>", html):
        if PHONE in para and SENTENCE in para:
            _fail("the phone number is not in the same <p> as the following sentence")

    hero = re.search(r'<section id="hero"[\s\S]*?</section>', html)
    if not hero:
        _fail(
            "the primary button text is Hours (or the real next title), "
            "not Read on, and there is only one hero button"
        )
    hero_html = hero.group(0)
    buttons = re.findall(r'<a class="btn[^"]*"[^>]*>([^<]*)</a>', hero_html)
    h2s = re.findall(r"<h2>([^<]*)</h2>", html)
    next_title = h2s[0] if h2s else ""
    one = len(buttons) == 1 and buttons[0] == next_title and buttons[0] != "Read on"
    if not one or buttons[0] not in {next_title, "Hours"} or "Hours" not in h2s:
        _fail(
            "the primary button text is Hours (or the real next title), "
            "not Read on, and there is only one hero button"
        )

    if "<h2>About</h2>" in html:
        _fail("there is no <h2>About</h2>")
    if "Built with SpiderCaster" in html:
        _fail("there is no Built with SpiderCaster")
    if 'name="robots" content="noindex' not in html:
        _fail("robots noindex is present")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        html = _index_html(_write_project(Path(tmp)))
    _check(html)
    print("regress selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
