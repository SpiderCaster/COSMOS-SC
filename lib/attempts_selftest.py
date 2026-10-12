"""Selftest batteries for the G47 build: attempts + tel auto-wire + mobile.

Run: ``python -m lib.attempts_selftest`` (also a ``lib.shipcheck`` step).
Zero tokens, stdlib only, synthetic sites under a temp dir.

1. Attempts battery: snapshot refuses clean reasons, snapshot -> mutate ->
   rollback is byte-equal, retention keeps the last 10, ``_attempts/`` is
   release-hash-excluded, ``dry_run_diff`` is pure and 0-token.
2. Tel battery (FINAL D4): precedence first explicit ask line -> first phone
   -> first email, verbatim digits only, absent renders no bar (never
   invented); the checker rows pass the wired page and fail the ask slot
   whose digits never reach a bar.
3. Mobile battery (FINAL D5): ``mobile`` blocks survive IR normalize, render
   honors phone ``order`` without touching 1280 DOM order, and the
   ``mobile_block`` gate row fails unknown keys / ``stack:false`` / duplicate
   orders while leaving block-free pages green.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib import attempts
from lib import check as check_mod
from lib import frames as frames_mod
from lib import ir as ir_mod
from lib import render as render_mod


def _fail(message: str) -> int:
    raise SystemExit(f"attempts selftest: {message}")


def _expect(cond: bool, message: str) -> None:
    if not cond:
        _fail(message)


def _mk_site(site_dir: Path, *, phone: str = "(555) 014-2288") -> dict:
    contact_data: dict = {
        "title": "Contact",
        "body": "Walk-ins only; no reservations needed.",
        "email": "",
        "phone": phone,
        "address": "14 Harbor Lane",
        "hours": "",
    }
    site = {
        "meta": {"title": "Attempt Bay", "description": "A quiet test counter."},
        "theme": {"template": "editorial", "dark": False},
        "nav": [],
        "footer": {"text": "Attempt Bay", "links": []},
        "pages": [
            {
                "slug": "index",
                "title": "Attempt Bay",
                "description": "A quiet test counter.",
                "sections": [
                    {
                        "id": "hero",
                        "type": "hero",
                        "data": {
                            "headline": "Attempt Bay",
                            "subhead": "A quiet test counter.",
                            "primary": {"label": "Contact", "href": "#contact"},
                        },
                    },
                    {
                        "id": "contact",
                        "type": "contact",
                        "data": contact_data,
                    },
                ],
            }
        ],
    }
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "site.json").write_text(
        json.dumps(site, indent=2), encoding="utf-8"
    )
    for page in render_mod.assemble(site, noindex=True):
        (site_dir / page["file"]).write_text(page["html"], encoding="utf-8")
    return site


def _battery_attempts(root: Path) -> None:
    site_dir = root / "attempt-site"
    _mk_site(site_dir)

    try:
        attempts.snapshot(site_dir, reason="offline")
        _fail("clean offline reason was allowed to snapshot")
    except ValueError:
        pass

    first = attempts.snapshot(site_dir, reason="refine")
    _expect(first["reason"] == "refine", "snapshot reason not recorded")
    _expect("site.json" in first["files"], "site.json missing from snapshot")
    _expect("index.html" in first["files"], "rendered tree missing from snapshot")
    _expect(first["parent"] == "", "first attempt should have no parent")

    second = attempts.snapshot(site_dir, reason="refine")
    _expect(second["parent"] == first["id"], "parent pointer not chained")

    before = {
        name: (site_dir / name).read_bytes()
        for name in ("site.json", "index.html")
    }
    (site_dir / "index.html").write_text(
        before["index.html"].decode("utf-8") + "\n<!-- mutate -->",
        encoding="utf-8",
    )
    site = json.loads((site_dir / "site.json").read_text(encoding="utf-8"))
    site["meta"]["title"] = "Mutated Bay"
    (site_dir / "site.json").write_text(json.dumps(site, indent=2), encoding="utf-8")
    (site_dir / "extra.html").write_text("<!doctype html><html></html>", encoding="utf-8")

    rolled = attempts.rollback(site_dir, first["id"])
    _expect((site_dir / "site.json").read_bytes() == before["site.json"],
            "rollback site.json not byte-equal")
    _expect((site_dir / "index.html").read_bytes() == before["index.html"],
            "rollback index.html not byte-equal")
    _expect(not (site_dir / "extra.html").exists(),
            "rollback left a page the snapshot never knew")
    _expect("restored" in rolled, "rollback manifest missing restored list")
    log = site_dir / attempts.ATTEMPTS_DIRNAME / attempts.ROLLBACK_LOGNAME
    _expect(log.is_file() and first["id"] in log.read_text(encoding="utf-8"),
            "rollback was not logged")

    for _ in range(attempts.RETENTION_CAP + 3):
        attempts.snapshot(site_dir, reason="refine")
    kept = attempts.list_attempts(site_dir)
    _expect(len(kept) == attempts.RETENTION_CAP,
            f"retention kept {len(kept)}, want {attempts.RETENTION_CAP}")
    ids = [entry["id"] for entry in kept]
    _expect(ids == sorted(ids), "attempt ids are not time-ordered")
    _expect(first["id"] not in ids, "retention did not prune the oldest")

    rels = [str(path.relative_to(site_dir)).replace("\\", "/")
            for path in site_dir.rglob("*") if path.is_file()]
    _expect(any(attempts.is_attempts_path(rel) for rel in rels),
            "_attempts/ payload missing from tree")
    release = [rel for rel in rels if not attempts.is_attempts_path(rel)]
    _expect(release and all("manifest.json" not in rel for rel in release),
            "release set leaks attempt provenance")
    _expect(not attempts.is_attempts_path("index.html"), "index.html misclassified")
    _expect(not attempts.is_attempts_path("assets/hero.png"), "asset misclassified")

    try:
        attempts.rollback(site_dir, "a20990101T000000Z_deadbeef")
        _fail("unknown attempt id was accepted")
    except ValueError:
        pass

    old = json.loads((site_dir / "site.json").read_text(encoding="utf-8"))
    new = json.loads(json.dumps(old))
    new["pages"][0]["sections"][0]["data"]["headline"] = "Attempt Bay Two"
    diff = attempts.dry_run_diff(old, new)
    _expect("Attempt Bay Two" in diff and "0 tokens" in diff,
            "dry-run diff missing the change or the 0-token stamp")
    same = attempts.dry_run_diff(old, json.loads(json.dumps(old)))
    _expect("no changes" in same, "identical IR should report no changes")
    fresh = attempts.dry_run_diff(None, new)
    _expect("0 tokens" in fresh, "fresh dry-run missing the 0-token stamp")

    hand = attempts.attempt_snapshot({"out": str(site_dir), "reason": "crew"})
    _expect(hand["status"] == "PASS", f"attempt_snapshot hand: {hand['detail']}")
    bad = attempts.attempt_snapshot({"reason": "crew"})
    _expect(bad["status"] == "FAIL", "attempt_snapshot without out should FAIL")


def _battery_tel(root: Path) -> None:
    # Precedence 1: explicit ask line beats the phone field.
    href, label = render_mod.tel_autowire(
        {"title": "Contact", "body": "Call (555) 999-0100 today.", "phone": "(555) 014-2288",
         "email": "bay@example.com"},
    )
    _expect(href == "tel:5559990100", f"ask line did not win: {href}")
    _expect(label == "(555) 999-0100", f"ask label not verbatim: {label}")

    # Precedence 2: phone field when no ask line.
    href, label = render_mod.tel_autowire(
        {"title": "Contact", "body": "Walk-ins only.", "phone": "(555) 014-2288",
         "email": "bay@example.com"},
    )
    _expect(href == "tel:5550142288", f"phone field not wired: {href}")

    # Precedence 3: email when no digits anywhere.
    href, label = render_mod.tel_autowire(
        {"title": "Contact", "body": "Walk-ins only.", "phone": "", "email": "bay@example.com"},
    )
    _expect(href == "mailto:bay@example.com", f"email fallback not wired: {href}")

    # Absent: nothing invented.
    href, label = render_mod.tel_autowire(
        {"title": "Contact", "body": "Walk-ins only.", "phone": "", "email": ""},
    )
    _expect(href == "" and label == "", "absent contact invented a bar")

    # Leading + is preserved, never added.
    href, _ = render_mod.tel_autowire({"phone": "+1 (555) 014-2288"})
    _expect(href == "tel:+15550142288", f"leading + mishandled: {href}")
    href, _ = render_mod.tel_autowire({"phone": "(555) 014-2288"})
    _expect(href == "tel:5550142288", f"country code added: {href}")

    # Fewer than 7 digits is not a phone number.
    href, _ = render_mod.tel_autowire({"phone": "ext 42"})
    _expect(href == "", "short digit run wired as tel:")

    # End to end: the wired page passes the conversion rows.
    site_dir = root / "tel-site"
    _mk_site(site_dir)
    html = (site_dir / "index.html").read_text(encoding="utf-8")
    _expect('href="tel:5550142288"' in html, "phone bar not auto-wired at build")
    rep = check_mod.check_site(site_dir, quiet=True)
    rows = {row["name"]: row for row in rep.rows}
    for name in ("cta_present", "ask_after_proof", "single_primary_cta"):
        _expect(name in rows, f"conversion row {name} missing")
        _expect(rows[name]["status"] == "PASS",
                f"conversion row {name}: {rows[name].get('detail')}")
    _expect(rows["phone_bar"]["status"] == "PASS",
            f"phone_bar: {rows['phone_bar'].get('detail')}")

    # Ask slot with digits but no bar: FAIL, never invented elsewhere.
    noslot = root / "tel-noslot"
    _mk_site(noslot)
    noslot_html = (noslot / "index.html").read_text(encoding="utf-8")
    noslot_html = noslot_html.replace('class="phone-bar"', 'class="phone-bar-x"')
    (noslot / "index.html").write_text(noslot_html, encoding="utf-8")
    rep = check_mod.check_site(noslot, quiet=True)
    single = next(row for row in rep.rows if row["name"] == "single_primary_cta")
    _expect(single["status"] == "FAIL", "missing bar on a digit ask slot passed")
    _expect("phone-bar" in single.get("detail", ""), "FAIL does not name the bar")

    # Order rule: an ask section before proof fails ask_after_proof.
    bad_order = [
        {"id": "contact", "type": "contact", "data": {}},
        {"id": "features", "type": "features", "data": {}},
    ]
    complaint = frames_mod.check_ask_after_proof(bad_order)
    _expect(bool(complaint) and "contact" in complaint, "ask-before-proof passed")
    good_order = [
        {"id": "features", "type": "features", "data": {}},
        {"id": "faq", "type": "faq", "data": {}},
        {"id": "contact", "type": "contact", "data": {}},
    ]
    _expect(frames_mod.check_ask_after_proof(good_order) == "",
            "proof-before-ask failed")


def _battery_mobile(root: Path) -> None:
    raw = {
        "id": "features",
        "type": "features",
        "data": {"title": "Pours", "items": []},
    }
    seen: set[str] = set()
    plain = ir_mod.normalize_section(
        {"id": "x", "type": "features",
         "data": {"title": "Pours", "items": [],
                  "mobile": {"stack": True, "order": 2}}},
        seen,
    )
    _expect(plain is not None and plain["data"].get("mobile") == {"stack": True, "order": 2},
            "mobile block did not survive IR normalize")
    _ = raw

    site_dir = root / "mob-site"
    site = _mk_site(site_dir)
    sections = site["pages"][0]["sections"]
    sections.insert(1, {"id": "pours", "type": "about",
                        "data": {"title": "Pours", "body": ["Slow pours all afternoon."]},
                        "mobile": {"stack": True, "order": 0}})
    site["pages"][0]["sections"][1]["data"]["mobile"] = {"stack": True, "order": 0}
    site = ir_mod.normalize_site(site, {})
    (site_dir / "site.json").write_text(json.dumps(site, indent=2), encoding="utf-8")
    for page in render_mod.assemble(site, noindex=True):
        (site_dir / page["file"]).write_text(page["html"], encoding="utf-8")
    html = (site_dir / "index.html").read_text(encoding="utf-8")
    _expect('data-sc-order="0"' in html, "phone order not rendered")
    _expect('id="pours"' in html, "ordered section missing from HTML")

    rep = check_mod.check_site(site_dir, quiet=True)
    mob = next(row for row in rep.rows if row["name"] == "mobile_block")
    _expect(mob["status"] == "PASS", f"mobile_block: {mob.get('detail')}")

    bad = root / "mob-bad"
    bad_site = _mk_site(bad)
    bad_sections = bad_site["pages"][0]["sections"]
    bad_sections[0]["data"]["mobile"] = {"stack": False}
    bad_sections[1]["data"]["mobile"] = {"stack": True, "order": 0, "parallax": True}
    (bad / "site.json").write_text(json.dumps(bad_site, indent=2), encoding="utf-8")
    rep = check_mod.check_site(bad, quiet=True)
    mob = next(row for row in rep.rows if row["name"] == "mobile_block")
    _expect(mob["status"] == "FAIL", "bad mobile blocks passed")
    detail = mob.get("detail", "")
    _expect("stack" in detail and "parallax" in detail,
            f"FAIL does not name both faults: {detail}")

    dup = root / "mob-dup"
    dup_site = _mk_site(dup)
    dup_sections = dup_site["pages"][0]["sections"]
    dup_sections[0]["data"]["mobile"] = {"stack": True, "order": 1}
    dup_sections[1]["data"]["mobile"] = {"stack": True, "order": 1}
    (dup / "site.json").write_text(json.dumps(dup_site, indent=2), encoding="utf-8")
    rep = check_mod.check_site(dup, quiet=True)
    mob = next(row for row in rep.rows if row["name"] == "mobile_block")
    _expect(mob["status"] == "FAIL", "duplicate phone orders passed")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _battery_attempts(root)
        _battery_tel(root)
        _battery_mobile(root)
    print("attempts selftest ok (attempts + tel + mobile_block)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
