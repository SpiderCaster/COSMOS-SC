"""UI orchestrator: screen order + gate rules for the stdio face.

Mirrors lib/crew.py: imports ROLES, never redefines them. Screen order is
seat order (cDeck override reflected, Deployer always last). Advance requires
the current seat's gate green; FAIL stops the seat and still shows the
ticket (CREW.md "stops at the first FAIL and still writes the ticket").

Consequential actions (bind --live, --indexable, paid spend) are never
executed here; lib.ui_hands printers render the exact CLI command instead.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.crew import ROLES  # noqa: E402

# (n, screen, seat-or-None, hands, does_not, gate). Menu order = ROLES order.
SCREENS: tuple[tuple[int, str, str | None, tuple[str, ...], str, str], ...] = (
    (0, "Projects", None, ("init",),
     "touch any site without selecting a project first",
     "project dir selected + exclusive lock held"),
    (1, "Brief", "architect", ("brief_read",),
     "invent pages that copy/ does not support",
     "brief present and non-empty"),
    (2, "Copy", "content", ("copy_read", "copy_gap"),
     "fill a gap with invented facts, prices, or quotes",
     "blocks cited to copy/; gaps named section.field"),
    (3, "Frame+Mold", "architect", ("frame_pick", "mold_pick"),
     "bind a mold live (draft binds only)",
     "frame slots + mold tokens picked; live collision warned"),
    (4, "Build", "frontend", ("plan_offline", "render"),
     "hotlink a photo or ship a vendor demo as-is",
     "offline plan green; render wrote pages + site.json"),
    (5, "Assets", "graphics", ("asset_list", "vault_photos"),
     "pull a stock CDN url into the page",
     "local only; remote drops warned (dropped_remote)"),
    (6, "Preview", None, ("serve",),
     "deploy, tunnel, or show anything check does not see",
     "localhost only; 360 + 1280 locked panes"),
    (7, "Checks", "visual", ("check_site",),
     "approve its own design; the checker is the gate",
     "exit-code truth; --release also fails on NOT RUN"),
    (8, "SEO", "seo", ("uniqueness", "meta_basics"),
     "reuse a mold or vendor frame that is already live",
     "one h1, title/desc, slugs, JSON-LD real-or-absent"),
    (9, "Ticket", "deployer", ("ticket_write",),
     "publish; that is a Keith click",
     "ticket always written; ok only on zero FAIL + visual PASS"),
    (10, "Library", "seo", ("uniqueness",),
     "promote a part without a green demo + BOARD ack",
     "Light subset Full; tier/white-label/credit gates"),
    (11, "Import", None, (),
     "write into the source tree (read-only reminder)",
     "importer funnel status only"),
)

_BY_SEAT = {role["id"]: role for role in ROLES}


def screens() -> list[dict]:
    """Screen table as dicts (n, name, seat, hands, does_not, gate)."""
    return [
        {
            "n": n, "name": name, "seat": seat, "hands": list(hands),
            "does_not": does_not, "gate": gate,
        }
        for n, name, seat, hands, does_not, gate in SCREENS
    ]


def screen_order() -> list[str]:
    """Screen names in seat order (Projects first, Import last)."""
    return [name for _, name, _, _, _, _ in SCREENS]


def check_order(ids: list[str]) -> dict:
    """Dep-preserving reorder check for the cDeck override.

    Refuses any order that moves Deployer off last or drops a seat.
    """
    want = [role["id"] for role in ROLES]
    if sorted(ids) != sorted(want):
        return {"ok": False, "error": "order must keep every seat exactly once"}
    if not ids or ids[-1] != "deployer":
        return {"ok": False, "error": "deployer stays last"}
    if ids.index("visual") > ids.index("deployer"):
        return {"ok": False, "error": "visual runs before ticket"}
    return {"ok": True, "error": ""}


def advance(result: dict) -> bool:
    """Advance past a seat only on a green gate (no FAIL status)."""
    if not result.get("allowed", True):
        return False
    return str(result.get("status") or "") != "FAIL"


def call(seat: str, hand: str, ctx: dict, counter: dict | None = None) -> dict:
    """Run exactly one engine hand through seat_gate. Returns its result.

    The UI invokes as the screen's seat (caller == seat); a refused hand
    returns FAIL and calls nothing. counter (when given) records how many
    engine hands ran, so the selftest can assert <= 1 per action.
    """
    from lib import hands as _hands
    from lib import seat_gate as _gate

    gate = _gate.seat_gate(seat, seat, hand)
    if not gate.get("allowed"):
        return {
            "seat": seat, "hand": hand, "allowed": False,
            "status": "FAIL",
            "detail": "refused: " + str(gate.get("error") or "unknown hand"),
            "data": {}, "hands_called": 0,
        }
    fn = _hands.HANDS.get(hand)
    if fn is None:
        return {
            "seat": seat, "hand": hand, "allowed": False,
            "status": "FAIL", "detail": "refused: unknown hand",
            "data": {}, "hands_called": 0,
        }
    if counter is not None:
        counter["hands_called"] = int(counter.get("hands_called", 0)) + 1
    try:
        out = fn(ctx)
    except SystemExit as exc:
        return {
            "seat": seat, "hand": hand, "allowed": True,
            "status": "FAIL", "detail": str(exc) or "FAIL",
            "data": {}, "hands_called": 1,
        }
    return {
        "seat": seat, "hand": hand, "allowed": True,
        "status": str(out.get("status") or "FAIL"),
        "detail": str(out.get("detail") or ""),
        "data": out.get("data") if isinstance(out.get("data"), dict) else {},
        "hands_called": 1,
    }


def main() -> int:
    assert [s["n"] for s in screens()] == list(range(12))
    assert _BY_SEAT["deployer"]["hands"] == ["ticket_write"]
    assert check_order([r["id"] for r in ROLES])["ok"]
    assert not check_order(["deployer"] + [r["id"] for r in ROLES][:-1])["ok"]
    refused = call("content", "render", {})
    assert refused["allowed"] is False and refused["status"] == "FAIL"
    assert refused["hands_called"] == 0
    print("ui_orchestrator selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
