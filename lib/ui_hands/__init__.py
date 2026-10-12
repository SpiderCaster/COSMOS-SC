"""Thin UI hands: seat_gate first, then exactly one engine hand.

No UI wrapper calls more than one engine hand and none publish. Anything
consequential (bind --live, --indexable, paid spend, cDeck reorder) is a
command-printer: it returns the exact CLI string for the human and
executes nothing. The rater/cDeck faces are read-only views (0 hands).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib import ui_orchestrator as _orc  # noqa: E402

# ui action -> (seat, engine hand). Seats come from ROLES; the table below
# only pairs screens to hands that ROLES already allows.
_ACTIONS: dict[str, tuple[str, str]] = {
    "brief_read": ("architect", "brief_read"),
    "frame_pick": ("architect", "frame_pick"),
    "mold_pick": ("architect", "mold_pick"),
    "copy_read": ("content", "copy_read"),
    "copy_gap": ("content", "copy_gap"),
    "plan_offline": ("frontend", "plan_offline"),
    "render": ("frontend", "render"),
    "asset_list": ("graphics", "asset_list"),
    "vault_photos": ("graphics", "vault_photos"),
    "check_site": ("visual", "check_site"),
    "uniqueness": ("seo", "uniqueness"),
    "meta_basics": ("seo", "meta_basics"),
    "ticket_write": ("deployer", "ticket_write"),
}


def actions() -> dict[str, tuple[str, str]]:
    """Ui action table (action -> (seat, engine hand))."""
    return dict(_ACTIONS)


def run(action: str, ctx: dict, counter: dict | None = None) -> dict:
    """Run one ui action: seat_gate first, then exactly one engine hand."""
    pair = _ACTIONS.get(action)
    if pair is None:
        return {
            "seat": "", "hand": action, "allowed": False,
            "status": "FAIL", "detail": "refused: unknown ui action",
            "data": {}, "hands_called": 0,
        }
    seat, hand = pair
    return _orc.call(seat, hand, ctx, counter)


def bind_live_command(site: str, out: str) -> str:
    """Exact human command for a live bind. The UI never executes this."""
    return f"python spidercaster.py library bind --site {site} --live --out {out}"


def serve_command(site_dir: str, port: int = 4173) -> str:
    """Exact human command for a localhost preview. The UI never serves."""
    return f"python spidercaster.py serve {site_dir} --port {port}"


def indexable_command(out: str) -> str:
    """Exact human command for an indexable rebuild. The UI never runs it."""
    return f"python spidercaster.py build --from {out}/site.json --indexable"


# --------------------------------------------------------------------------
# Step 6-7 printers: rater surface + cDeck-last (read-only, 0 hands).
#
# The rater verdict block is judged output the UI only renders; the exact
# human command that surfaces what the judge judged is the checker run.
# The cDeck workflow order lives in the cDeck sidebar (tab `website`);
# no SpiderCaster CLI applies an order, so the reorder "button" is a file
# pointer plus the dep-order lock verdict, and the only CLI printed is the
# existing verifier (`crew roles`). Nothing here writes or executes.
# --------------------------------------------------------------------------

#: cDeck-owned workflow file when SPIDERCASTER_PROFILE_ENGINE is unset.
CDECK_DEFAULT_ENGINE = (
    r"V:\A\Ai\COSMOS\live\state\profiles\website\engine.json"
)


def rater_surface_command(site_dir: str) -> str:
    """Exact human command surfacing what the rater judged. Never run."""
    return f"python spidercaster.py check {site_dir}"


def cdeck_verify_command() -> str:
    """Exact human command surfacing the package seats/hands. Never run."""
    return "python spidercaster.py crew roles"


def cdeck_workflow_path() -> str:
    """cDeck-owned workflow file (env override wins). Pointer only."""
    env = os.environ.get("SPIDERCASTER_PROFILE_ENGINE", "").strip()
    return env or CDECK_DEFAULT_ENGINE


def cdeck_order_preview(ids: list[str]) -> dict:
    """Dep-order lock verdict for a proposed seat order. Never writes.

    Returns {"ok", "detail"} using lib.ui_orchestrator.check_order
    verbatim: deployer off last (or a dropped seat) is refused.
    """
    verdict = _orc.check_order(list(ids))
    if verdict.get("ok"):
        return {"ok": True, "detail": "order keeps every seat, deployer last"}
    return {"ok": False, "detail": str(verdict.get("error") or "refused")}


def main() -> int:
    refused = run("nope", {})
    assert refused["status"] == "FAIL" and refused["hands_called"] == 0
    crossed = _orc.call("content", "render", {}, None)
    assert crossed["allowed"] is False and crossed["hands_called"] == 0
    assert "library bind" in bind_live_command("s", "o") and "--live" in bind_live_command("s", "o")
    assert "serve" in serve_command("sites/x")
    assert "check" in rater_surface_command("sites/x")
    assert cdeck_verify_command() == "python spidercaster.py crew roles"
    assert cdeck_workflow_path().endswith("engine.json")
    good = cdeck_order_preview(
        ["architect", "content", "frontend", "graphics",
         "visual", "seo", "deployer"])
    assert good["ok"] is True
    bad = cdeck_order_preview(
        ["deployer", "content", "frontend", "graphics",
         "visual", "seo", "architect"])
    assert bad["ok"] is False and "deployer" in bad["detail"]
    print("ui_hands selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
