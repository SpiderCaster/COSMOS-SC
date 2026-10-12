"""Claim and ship checks. Run: py -3.14 lib\\check_claims_selftest.py"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import tempfile

from lib.check import check_site


def _claim_rows(report) -> list[dict]:
    return [row for row in report.rows if row["name"] == "ungrounded_claim"]


def _named(report, name: str) -> list[dict]:
    return [row for row in report.rows if row["name"] == name]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        (site / "index.html").write_text(
            "<!doctype html><html><head><title>Tea</title></head>"
            "<body><p>Our award-winning tea is served daily.</p></body></html>\n",
            encoding="utf-8",
        )
        missing = check_site(site, quiet=True, copy_text="tea served daily")
        fails = [row for row in _claim_rows(missing) if row["status"] == "FAIL"]
        if len(fails) != 1:
            raise SystemExit("expected one FAIL ungrounded_claim")
        grounded = check_site(site, quiet=True, copy_text="This shop is award-winning.")
        if _claim_rows(grounded):
            raise SystemExit("grounded award-winning was flagged")
        bare = check_site(site, quiet=True, copy_text="")
        if _claim_rows(bare):
            raise SystemExit("copy_text empty added ungrounded_claim")

        mark = site / "mark"
        mark.mkdir()
        (mark / "index.html").write_text(
            "<!doctype html><html><head><title>Mark</title></head><body>"
            '<div class="hero-visual hero-mark"><span>M</span></div>'
            "<p>Letter mark only.</p></body></html>\n",
            encoding="utf-8",
        )
        marked = check_site(mark, quiet=True, copy_text="Letter mark only.")
        mark_rows = _named(marked, "missing_file")
        if len(mark_rows) != 1 or mark_rows[0]["status"] != "PASS":
            raise SystemExit("letter-mark page did not pass missing_file")

        gone = site / "gone"
        gone.mkdir()
        (gone / "index.html").write_text(
            "<!doctype html><html><head><title>Gone</title></head><body>"
            '<img src="assets/missing.png" alt="missing"></body></html>\n',
            encoding="utf-8",
        )
        lost = check_site(gone, quiet=True, copy_text="tea")
        lost_fails = [row for row in _named(lost, "missing_file") if row["status"] == "FAIL"]
        if len(lost_fails) != 1:
            raise SystemExit("missing local img did not fail missing_file")

        kept = site / "kept"
        (kept / "assets").mkdir(parents=True)
        (kept / "assets" / "hero.png").write_bytes(b"png")
        (kept / "index.html").write_text(
            "<!doctype html><html><head><title>Kept</title></head><body>"
            '<img src="assets/hero.png" alt="hero"></body></html>\n',
            encoding="utf-8",
        )
        held = check_site(kept, quiet=True, copy_text="tea")
        if any(row["status"] == "FAIL" for row in _named(held, "missing_file")):
            raise SystemExit("present local img failed missing_file")

        chrome = site / "chrome"
        chrome.mkdir()
        (chrome / "index.html").write_text(
            "<!doctype html><html><body><h2>About</h2>"
            "<a>Read on</a><p>Built with SpiderCaster</p></body></html>\n",
            encoding="utf-8",
        )
        empty = check_site(chrome, quiet=True, copy_text="")
        if _named(empty, "lone_about") or _named(empty, "invented_chrome"):
            raise SystemExit("copy_text empty added a chrome row")
        filled = check_site(chrome, quiet=True, copy_text="tea served daily")
        if not any(row["status"] == "FAIL" for row in _named(filled, "lone_about")):
            raise SystemExit("lone About was not flagged")
        if not any(row["status"] == "FAIL" for row in _named(filled, "invented_chrome")):
            raise SystemExit("invented chrome was not flagged")
        stated = check_site(
            chrome,
            quiet=True,
            copy_text="About this shop. Read on. Built with SpiderCaster",
        )
        if _named(stated, "lone_about") or _named(stated, "invented_chrome"):
            raise SystemExit("copy that states the chrome was flagged")
    print("claims selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
