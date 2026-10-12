"""Prove the parts scan and the assembled site.

Run from the repo root: ``python lib/assemble_selftest.py``
or ``python spidercaster.py parts selftest``.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.assemble import AssembleError, assemble_site, load_facts
from lib.check import check_site
from lib.parts_lib import family_counts, scan

PROJECT = ROOT / "projects" / "demo-local"
FLOORS = {
    "headers": 40,
    "hooks_blocks": 25,
    "popups_callouts": 134,
    "sidebars": 89,
}


def _fail(msg: str) -> int:
    print("assemble selftest FAIL: " + msg)
    return 1


def main() -> int:
    parts = scan()
    counts = family_counts(parts)
    for family, floor in FLOORS.items():
        if counts.get(family, 0) < floor:
            return _fail(f"{family} has {counts.get(family, 0)}, need at least {floor}")
    try:
        facts = load_facts(PROJECT)
    except AssembleError as exc:
        return _fail(str(exc))
    if "copy-driven static website engine" not in facts["definition"]:
        return _fail("definition is not the overview paragraph")
    if not facts["note"].startswith("Tone:"):
        return _fail("editor note is not the brief tone line")

    tmp = Path(tempfile.mkdtemp(prefix="sc-assemble-"))
    try:
        try:
            info = assemble_site(PROJECT, tmp)
        except AssembleError as exc:
            return _fail(str(exc))
        report = check_site(tmp, expect_noindex=True, quiet=True)
        if not report.ok():
            lines = []
            for row in report.rows:
                if row["status"] != "FAIL":
                    continue
                lines.append(row["name"] + ": " + row.get("detail", ""))
                for item in (row.get("failures") or [])[:6]:
                    lines.append("  " + str(item))
            return _fail("; ".join(lines)[:2000])
        index = (tmp / "index.html").read_text(encoding="utf-8")
        catalog = (tmp / "catalog.html").read_text(encoding="utf-8")
        for needle in (
            'data-sc-part="definition-callout"',
            'data-sc-part="key-takeaways"',
            'data-sc-part="step-callout"',
            'data-sc-part="editors-note"',
            'data-sc-part="stat-callout"',
            'data-sc-part="back-to-top-button"',
            "copy-driven static website engine",
            "href=\"catalog.html\"",
        ):
            if needle not in index:
                return _fail("index is missing " + needle)
        for bad in ("fatal crash", "First point, one sentence", "lorem ipsum", "First question?"):
            if bad.lower() in index.lower() or bad.lower() in catalog.lower():
                return _fail("demo wording leaked: " + bad)
        missing = [rec["id"] for rec in parts if f'data-part="{rec["id"]}"' not in catalog]
        if missing:
            return _fail(f"catalog missing {len(missing)} parts, e.g. {missing[0]}")
        if str(info["parts"]) not in catalog:
            return _fail("catalog does not show the part count")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"assemble selftest ok ({len(parts)} parts, header {info['header']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
