"""UI selftest: screen walk + gaps battery + engine-room end-to-end.

All offline, zero tokens, stdlib only. Builds go to temp dirs; the tree is
never written (the session lock is taken on a temp project copy, and the
library ledger is snapshotted to prove the Ticket screen never binds).
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib import ui_hands as _hands  # noqa: E402
from lib import ui_orchestrator as _orc  # noqa: E402
from lib import ui_render as _render  # noqa: E402

_DEMO = "projects/demo-local"
_GAP_RE = re.compile(r"FAIL gap [A-Za-z0-9_]+\.[A-Za-z0-9_]+")


class _Cap:
    """Capture emitted lines; feed stubbed input words."""

    def __init__(self, words: list[str] | None = None):
        self.lines: list[str] = []
        self.words = list(words or [])

    def emit(self, text: str = "") -> None:
        """Collect one line."""
        self.lines.append(str(text))

    def feed(self) -> str:
        """Next stubbed word (q when exhausted)."""
        if self.words:
            return self.words.pop(0)
        return "q"

    def text(self) -> str:
        """All captured output."""
        return "\n".join(self.lines)


def _expect(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"ui_selftest FAIL: {label}")


def _temp_project() -> tuple[Path, Path]:
    """Temp copy of projects/demo-local (tmp dir, project dir)."""
    tmp = Path(tempfile.mkdtemp(prefix="ui_e2e_"))
    src = _render.tree_root() / _DEMO
    proj = tmp / "proj"
    shutil.copytree(src, proj)
    return tmp, proj


def walk_all_screens() -> str:
    """Walk screens 0-11 on projects/demo-local with stubbed input."""
    cap = _Cap()
    ui = _render.UI(emit=cap.emit, input_fn=cap.feed)
    ui.project = _DEMO
    ui.site = str(_render.site_dir_for(_DEMO))
    for n in range(12):
        before = ui.counter["hands_called"]
        ui.show(n)
        used = ui.counter["hands_called"] - before
        _expect(used <= 1, f"screen {n} uses at most one hand (used {used})")
    for second, label in (
            (lambda: ui.screen_checks(gaps=True), "checks gaps"),
            (lambda: ui.screen_copy(gaps=True), "copy gaps"),
            (lambda: ui.screen_assets(vault=True), "assets vault")):
        before = ui.counter["hands_called"]
        second()
        _expect(ui.counter["hands_called"] - before == 1, f"{label}: one hand")
    out = cap.text()
    for n, name in ((4, "Build"), (5, "Assets"), (6, "Preview"), (7, "Checks")):
        _expect(f"[{n}] {name}" in out, f"screen {n} {name} rendered")
    _expect("ledger:" in out, "global footer ledger on every screen")
    _expect("ticket:" in out, "global footer ticket on every screen")
    _expect("library bind" in out and "--live" in out, "ticket prints bind command")
    _expect("360 + 1280 locked" in out, "preview panes locked")
    _expect("A14" in out, "tap-target A14 scoping text on Checks")
    return out


def refused_hands() -> None:
    """Refused hands FAIL and call nothing (<=1 hand per action enforced)."""
    counter: dict = {"hands_called": 0}
    missing = _hands.run("render", {"project": _DEMO}, counter)
    _expect(missing["status"] == "FAIL" and counter["hands_called"] == 1,
            "hand runs once and reports its own FAIL (out required)")
    direct = _orc.call("content", "render", {}, counter)
    _expect(direct["allowed"] is False and direct["hands_called"] == 0,
            "cross-seat call refused")
    bogus = _hands.run("bind_live", {}, counter)
    _expect(bogus["status"] == "FAIL", "no ui action executes a live bind")


def gaps_battery() -> None:
    """Gap FAILs name section.field; no HTML is written on FAIL."""
    tmp = Path(tempfile.mkdtemp(prefix="ui_gap_"))
    try:
        proj = tmp / "proj"
        (proj / "copy").mkdir(parents=True)
        (proj / "brief.md").write_text("# Brief\nEmpty on purpose.\n", encoding="utf-8")
        (proj / "copy" / "thin.md").write_text("nothing useful here\n", encoding="utf-8")
        out = tmp / "out"
        counter: dict = {"hands_called": 0}
        planned = _hands.run("plan_offline", {"project": str(proj)}, counter)
        _expect(planned["status"] == "FAIL", "gutted copy fails the plan gate")
        _expect(bool(_GAP_RE.search(planned["detail"])),
                f"gap names section.field: {planned['detail'][:120]}")
        _expect(list(out.glob("*.html")) == [], "no HTML written on gap FAIL")
        cap = _Cap()
        ui = _render.UI(emit=cap.emit, input_fn=cap.feed)
        ui.project = str(proj)
        ui.site = str(out)
        ui.screen_build(choice="p")
        _expect(bool(_GAP_RE.search(cap.text())), "board surfaces the gap FAIL")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def engine_room_end_to_end() -> None:
    """Plan -> render -> check board -> ticket, all through UI hands."""
    tmp, proj = _temp_project()
    try:
        out = tmp / "out"
        counter: dict = {"hands_called": 0}
        planned = _hands.run("plan_offline", {"project": str(proj)}, counter)
        _expect(planned["status"] == "PASS", f"demo plan green: {planned['detail']}")
        built = _hands.run(
            "render", {"project": str(proj), "out": str(out)}, counter)
        _expect(built["status"] == "PASS", f"demo render green: {built['detail']}")
        _expect((out / "index.html").exists(), "index.html written to temp out")
        checked = _hands.run(
            "check_site", {"project": str(proj), "out": str(out)}, counter)
        rows = (checked.get("data") or {}).get("rows") or []
        ids = [str(r.get("name")) for r in rows]
        _expect(len(rows) > 20 and "weight" in ids and "tap_target" in ids,
                "board carries every gate row id")
        fails = [r for r in rows if r.get("status") == "FAIL"]
        _expect(not fails, f"board 0 FAIL: {[r.get('name') for r in fails][:5]}")
        weight = next(r for r in rows if r.get("name") == "weight")
        _expect(weight["status"] == "PASS", f"budgets green: {weight.get('detail')}")
        cap = _Cap()
        ui = _render.UI(emit=cap.emit, input_fn=cap.feed)
        ui.project = str(proj)
        ui.site = str(out)
        ui.screen_checks()
        ui.screen_preview()
        text = cap.text()
        _expect("153600" in text and "40960" in text, "budgets printed on board")
        _expect("board: " in text, "board totals printed")
        visual = "PASS" if checked["status"] == "PASS" else "FAIL"
        ticket = _hands.run("ticket_write", {
            "project": str(proj), "out": str(out), "site": "ui-e2e",
            "hands": [{"role": "visual", "status": visual}],
        }, counter)
        _expect(ticket["status"] == "PASS", "green-ticket attempt writes ok ticket")
        saved = _render.read_ticket(out)
        _expect(saved is not None and saved.get("ok") is True, "ticket ok:true")
        _expect(bool(saved.get("sha256")), "ticket sha-bound")
        _expect(_render.ticket_ok_text(saved).startswith("ticket: ok"),
                "footer reads ticket ok")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def bind_print_never_runs() -> None:
    """Ticket screen prints the bind command; the ledger is untouched."""
    ledger = _render.tree_root() / "library" / "ledger.json"
    before = ledger.read_text(encoding="utf-8") if ledger.exists() else None
    cap = _Cap()
    ui = _render.UI(emit=cap.emit, input_fn=cap.feed)
    ui.project = _DEMO
    ui.site = str(_render.site_dir_for(_DEMO))
    ui.screen_ticket()
    after = ledger.read_text(encoding="utf-8") if ledger.exists() else None
    _expect(before == after, "ticket screen never executes a bind")
    _expect("--live" in cap.text() and "UI never executes" in cap.text(),
            "bind command printed, not run")


def lock_roundtrip() -> None:
    """Exclusive lock: second session refused, stale lock reported."""
    tmp = Path(tempfile.mkdtemp(prefix="ui_lock_"))
    try:
        proj = tmp / "proj"
        proj.mkdir()
        ok, _ = _render.acquire_lock(str(proj))
        _expect(ok, "first session takes the lock")
        ok2, why = _render.acquire_lock(str(proj))
        _expect(not ok2 and "live pid" in why, "second session refused")
        _render.release_lock(str(proj))
        _expect(not (proj / ".sc_ui_lock").exists(), "lock released")
        (proj / ".sc_ui_lock").write_text("999999999", encoding="utf-8")
        ok3, why3 = _render.acquire_lock(str(proj))
        _expect(not ok3 and "stale" in why3, "dead pid reported stale")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def probe_publish_battery() -> None:
    """Step 4+5: probe wiring read-only; publish readiness never executes."""
    import hashlib
    import json as _json

    tmp = Path(tempfile.mkdtemp(prefix="ui_probe_pub_"))
    try:
        site = tmp / "out"
        site.mkdir()
        (site / "index.html").write_text(
            "<html><head><title>t</title></head><body>probe</body></html>\n",
            encoding="utf-8",
        )

        def _probe_cap() -> tuple:
            cap = _Cap()
            ui = _render.UI(emit=cap.emit, input_fn=cap.feed)
            ui.project = _DEMO
            ui.site = str(site)
            return cap, ui

        # NOT_RUN: no probe file; release refuses it.
        state = _render.probe_status(site)
        _expect(state["state"] == "NOT_RUN" and state["row"] == "SKIP",
                f"missing probe is NOT_RUN/SKIP: {state}")
        cap, ui = _probe_cap()
        before = ui.counter["hands_called"]
        ui.probe_text()
        _expect(ui.counter["hands_called"] == before, "probe view uses 0 hands")
        _expect("NOT RUN" in cap.text() and "--release refuses" in cap.text(),
                "probe view names NOT RUN release-blocking")
        _expect("spidercaster.py check" in cap.text(), "surface command printed")
        checked = _hands.run("check_site", {"project": _DEMO, "out": str(site)})
        visual = next((r for r in (checked.get("data") or {}).get("rows", [])
                       if r.get("name") == "visual_probe"), None)
        _expect(visual is not None and visual["status"] == "SKIP",
                "checker agrees: visual_probe SKIP without a probe")
        cap2, ui2 = _probe_cap()
        ui2.screen_checks(release=True)
        _expect("BLOCKED (NOT RUN is not a pass)" in cap2.text(),
                "--release blocked on NOT RUN")

        # STALE: wrong hash refuses.
        (site / "layout-probe.json").write_text(
            _json.dumps({"html_hash": "0" * 16, "rows": []}), encoding="utf-8")
        state = _render.probe_status(site)
        _expect(state["state"] == "STALE" and state["row"] == "FAIL",
                f"wrong hash is STALE/FAIL: {state}")

        # FAIL rows: bound hash but a FAIL row refuses.
        digest = hashlib.sha256()
        for page in sorted(site.glob("*.html")):
            digest.update(page.read_bytes())
        current = digest.hexdigest()[:16]
        (site / "layout-probe.json").write_text(
            _json.dumps({"html_hash": current,
                         "rows": [{"status": "FAIL", "detail": "overflow"}]}),
            encoding="utf-8")
        state = _render.probe_status(site)
        _expect(state["state"] == "FAIL_ROWS" and state["row"] == "FAIL",
                f"FAIL rows refuse: {state}")

        # PASS: bound hash, green rows; checker parity.
        (site / "layout-probe.json").write_text(
            _json.dumps({"html_hash": current,
                         "rows": [{"status": "PASS", "detail": "360/1280"}]}),
            encoding="utf-8")
        state = _render.probe_status(site)
        _expect(state["state"] == "PASS" and state["row"] == "PASS",
                f"bound green probe passes: {state}")
        checked = _hands.run("check_site", {"project": _DEMO, "out": str(site)})
        visual = next((r for r in (checked.get("data") or {}).get("rows", [])
                       if r.get("name") == "visual_probe"), None)
        _expect(visual is not None and visual["status"] == "PASS",
                "checker agrees: visual_probe PASS on a bound probe")

        # Publish READY on a green ticket; ledger untouched; never executes.
        ledger = _render.tree_root() / "library" / "ledger.json"
        before_ledger = ledger.read_text(encoding="utf-8") if ledger.exists() else None
        ticket = _hands.run("ticket_write", {
            "project": _DEMO, "out": str(site), "site": "probe-site",
            "mold_id": "probe-mold",
            "hands": [{"role": "visual", "status": "PASS", "detail": "checker"}],
        })
        _expect(ticket["status"] == "PASS", "green-ticket attempt writes ok ticket")
        cap3, ui3 = _probe_cap()
        before_hands = ui3.counter["hands_called"]
        ui3.publish_text()
        _expect(ui3.counter["hands_called"] == before_hands,
                "publish view uses 0 hands")
        text = cap3.text()
        _expect("READY" in text, "green ticket reads READY")
        _expect("--live" in text and "--mold probe-mold" in text
                and "--site probe-site" in text, "exact mold-bound command printed")
        _expect("never executes" in text, "never-executes stated")
        after_ledger = ledger.read_text(encoding="utf-8") if ledger.exists() else None
        _expect(before_ledger == after_ledger, "readiness never executes a bind")

        # A 1-byte edit flips READY to REFUSED (verbatim hash mismatch).
        (site / "index.html").write_text(
            "<html><head><title>t</title></head><body>probe!</body></html>\n",
            encoding="utf-8",
        )
        cap4, ui4 = _probe_cap()
        ui4.publish_text()
        _expect("REFUSED" in cap4.text() and "hash mismatch" in cap4.text(),
                "1-byte flip refused verbatim")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def rater_cdeck_battery() -> None:
    """Step 6+7: rater verdicts read-only; cDeck-last face + lock printers."""
    import hashlib
    import json as _json
    import os as _os

    tmp = Path(tempfile.mkdtemp(prefix="ui_rater_cdeck_"))
    try:
        site = tmp / "out"
        site.mkdir()
        (site / "index.html").write_text(
            "<html><head><title>t</title></head><body>rater</body></html>\n",
            encoding="utf-8",
        )

        def _face_cap() -> tuple:
            cap = _Cap()
            ui = _render.UI(emit=cap.emit, input_fn=cap.feed)
            ui.project = _DEMO
            ui.site = str(site)
            return cap, ui

        ledger = _render.tree_root() / "library" / "ledger.json"
        before_ledger = ledger.read_text(encoding="utf-8") if ledger.exists() else None

        # NOT_RUN: no rater.json; unjudged never passes.
        state = _render.rater_status(site)
        _expect(state["state"] == "NOT_RUN" and state["row"] == "SKIP",
                f"missing rater is NOT_RUN/SKIP: {state}")
        cap, ui = _face_cap()
        before = ui.counter["hands_called"]
        ui.rater_text()
        _expect(ui.counter["hands_called"] == before, "rater view uses 0 hands")
        _expect("NOT RUN" in cap.text() and "unjudged is not a pass" in cap.text(),
                "rater view names NOT RUN as unjudged")
        _expect("spidercaster.py check" in cap.text(), "rater surface printed")

        # STALE: wrong hash refuses.
        (site / "rater.json").write_text(
            _json.dumps({"html_hash": "0" * 16, "judge": "j",
                         "rows": [{"part": "hero", "verdict": "PASS"}]}),
            encoding="utf-8")
        state = _render.rater_status(site)
        _expect(state["state"] == "STALE" and state["row"] == "FAIL",
                f"wrong hash is STALE/FAIL: {state}")

        # Bound hash for the verdict rows below.
        digest = hashlib.sha256()
        for page in sorted(site.glob("*.html")):
            digest.update(page.read_bytes())
        current = digest.hexdigest()[:16]

        def _write_rater(rows, judge="hero-rater/1") -> None:
            (site / "rater.json").write_text(
                _json.dumps({"html_hash": current, "judge": judge,
                             "rows": rows}), encoding="utf-8")

        # FAIL verdict rows render part/judge/verdict/cites.
        _write_rater([{"part": "hero", "judge": "hero-rater/1",
                       "verdict": "FAIL", "cites": ["copy/hero.md"],
                       "detail": "invented price"}])
        state = _render.rater_status(site)
        _expect(state["state"] == "FAIL_ROWS" and state["row"] == "FAIL",
                f"FAIL verdict refuses: {state}")
        cap, ui = _face_cap()
        ui.rater_text()
        text = cap.text()
        for needle in ("part hero", "hero-rater/1", "copy/hero.md", "FAIL"):
            _expect(needle in text, f"verdict block names {needle}")

        # SKIP (abstain) and WARN verdicts map checker-like, never PASS.
        _write_rater([{"part": "hero", "verdict": "SKIP", "cites": []}])
        state = _render.rater_status(site)
        _expect(state["state"] == "SKIP_ROWS" and state["row"] == "SKIP",
                f"abstain is SKIP: {state}")
        _write_rater([{"part": "hero", "verdict": "WARN", "cites": []}])
        state = _render.rater_status(site)
        _expect(state["state"] == "WARN_ROWS" and state["row"] == "WARN",
                f"warn is WARN: {state}")

        # Producer bugs FAIL loudly: bad token, empty rows, non-object.
        _write_rater([{"part": "hero", "verdict": "MAYBE"}])
        state = _render.rater_status(site)
        _expect(state["state"] == "FAIL_ROWS" and "producer bug" in state["detail"],
                f"bad token is FAIL: {state}")
        (site / "rater.json").write_text(
            _json.dumps({"html_hash": current, "rows": []}), encoding="utf-8")
        state = _render.rater_status(site)
        _expect(state["row"] == "FAIL", "empty rows judge nothing: FAIL")
        (site / "rater.json").write_text("[1, 2]", encoding="utf-8")
        state = _render.rater_status(site)
        _expect(state["state"] == "UNREADABLE" and state["row"] == "FAIL",
                "non-object rater is UNREADABLE/FAIL")

        # PASS: bound green rows with cites.
        _write_rater([
            {"part": "hero", "verdict": "PASS", "cites": ["copy/hero.md"]},
            {"part": "cta", "verdict": "PASS", "cites": ["copy/cta.md"],
             "detail": "one cited CTA"},
        ])
        state = _render.rater_status(site)
        _expect(state["state"] == "PASS" and state["row"] == "PASS",
                f"bound green verdicts pass: {state}")
        _expect(state["rows"][0]["cites"] == ["copy/hero.md"], "cites kept")

        # Checks + SEO screens carry the block and stay at one hand each.
        for screen, label in ((lambda u: u.screen_checks(), "checks"),
                              (lambda u: u.screen_seo(), "seo")):
            cap, ui = _face_cap()
            before = ui.counter["hands_called"]
            screen(ui)
            used = ui.counter["hands_called"] - before
            _expect(used <= 1, f"{label} screen uses at most one hand")
            _expect("rater:" in cap.text(), f"{label} screen shows verdicts")

        # cDeck-last: package order, deployer-last lock, contract, buttons.
        status = _render.cdeck_status()
        _expect(status["package"] == ["architect", "content", "frontend",
                                      "graphics", "visual", "seo", "deployer"],
                f"package order is the seven seats: {status['package']}")
        _expect(status["effective"][-1] == "deployer", "deployer stays last")
        _expect(status["lock_ok"] is True, "dep-order lock green")
        _expect(status["tab"] == "website" and status["sidebar"] == "left",
                f"contract quoted: tab={status['tab']} sidebar={status['sidebar']}")
        cap, ui = _face_cap()
        before = ui.counter["hands_called"]
        ui.cdeck_text()
        _expect(ui.counter["hands_called"] == before, "cdeck face uses 0 hands")
        text = cap.text()
        for needle in ("cdeck: tab website", "deployer", "LOCKED",
                       "crew roles", "never writes"):
            _expect(needle in text, f"cdeck face shows {needle}")
        cap, ui = _face_cap()
        before = ui.counter["hands_called"]
        ui.screen_import()
        _expect(ui.counter["hands_called"] == before, "import screen: 0 hands")
        _expect("cdeck: tab website" in cap.text(), "cdeck lives on Import (last)")

        # Dep-order lock printers: green order ok, deployer-first refused.
        good = _hands.cdeck_order_preview(status["package"])
        _expect(good["ok"] is True, "package order passes the lock")
        bad = _hands.cdeck_order_preview(
            ["deployer", "content", "frontend", "graphics",
             "visual", "seo", "architect"])
        _expect(bad["ok"] is False and "deployer" in bad["detail"],
                "deployer-first refused")
        _expect(_hands.cdeck_verify_command() == "python spidercaster.py crew roles",
                "verify printer is the existing crew roles command")
        _expect("check" in _hands.rater_surface_command("sites/x"),
                "rater surface printer is the check command")

        # Env override is a pointer, never a write.
        old_env = _os.environ.get("SPIDERCASTER_PROFILE_ENGINE")
        try:
            _os.environ["SPIDERCASTER_PROFILE_ENGINE"] = str(tmp / "engine.json")
            _expect(_hands.cdeck_workflow_path() == str(tmp / "engine.json"),
                    "env override wins the pointer")
            _expect(not (tmp / "engine.json").exists(), "pointer wrote nothing")
        finally:
            if old_env is None:
                _os.environ.pop("SPIDERCASTER_PROFILE_ENGINE", None)
            else:
                _os.environ["SPIDERCASTER_PROFILE_ENGINE"] = old_env

        after_ledger = ledger.read_text(encoding="utf-8") if ledger.exists() else None
        _expect(before_ledger == after_ledger, "rater/cdeck faces never bind")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    """Run every battery. Exit 0 only on all green."""
    walk_all_screens()
    refused_hands()
    gaps_battery()
    engine_room_end_to_end()
    probe_publish_battery()
    rater_cdeck_battery()
    bind_print_never_runs()
    lock_roundtrip()
    print("ui_selftest ok (walk 0-11, gaps, e2e, probe, rater, cdeck, bind, lock)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
