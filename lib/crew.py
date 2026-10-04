"""Seven hands for one site build.

The hands are code. A model may sit in a seat, but the seat can only call
its tools, and the checker still has to pass. No hand publishes.

Order: architect, content, frontend, graphics, visual, seo, deployer.
That is the Wix shape (one mold, then sections), the Perplexity shape
(real sources before structure), and the Claude Code shape (a tool
allowlist plus a verify step before anyone says the build is done).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from lib.hands import HANDS
from lib.library import Library, LibraryError

ROLES = (
    {
        "id": "architect",
        "n": 1,
        "label": "Architect / lead planner",
        "hands": ["brief_read", "frame_pick", "mold_pick", "library_bind"],
        "does_not": "invent pages that copy/ does not support",
    },
    {
        "id": "content",
        "n": 2,
        "label": "Content writer",
        "hands": ["copy_read", "copy_gap"],
        "does_not": "fill a gap with invented facts, prices, or quotes",
    },
    {
        "id": "frontend",
        "n": 3,
        "label": "Frontend engineer",
        "hands": ["plan_offline", "render"],
        "does_not": "hotlink a photo or ship a vendor demo as-is",
    },
    {
        "id": "graphics",
        "n": 4,
        "label": "Graphics / photo editor",
        "hands": ["asset_list", "vault_photos"],
        "does_not": "pull a stock CDN url into the page",
    },
    {
        "id": "visual",
        "n": 5,
        "label": "Visual critic",
        "hands": ["check_site"],
        "does_not": "approve its own design; the checker is the gate",
    },
    {
        "id": "seo",
        "n": 6,
        "label": "SEO specialist",
        "hands": ["uniqueness", "meta_basics"],
        "does_not": "reuse a mold or vendor frame that is already live",
    },
    {
        "id": "deployer",
        "n": 7,
        "label": "Deployer / QA",
        "hands": ["ticket_write"],
        "does_not": "publish; that is a Keith click",
    },
)


def _hand(role: str, status: str, detail: str) -> dict:
    return {"role": role, "status": status, "detail": detail}


_ROLE_BY_ID = {role["id"]: role for role in ROLES}
_TICKET_NOTE = "ticket written; publish is a Keith click (library bind --live)"


def _valid_order(ids: list[str]) -> bool:
    return len(ids) == len(ROLES) and set(ids) == set(_ROLE_BY_ID)


def _saved_order() -> list[str] | None:
    """cDeck workflow, when a website engine file is present. Package order otherwise."""
    candidates = []
    env = os.environ.get("SPIDERCASTER_PROFILE_ENGINE")
    if env:
        candidates.append(Path(env))
    candidates.append(Path(r"V:\A\Ai\COSMOS\live\state\profiles\website\engine.json"))
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        plugin = data.get("plugin") if isinstance(data, dict) else None
        workflow = plugin.get("workflow") if isinstance(plugin, dict) else None
        if not isinstance(workflow, list):
            continue
        ids = [str(item).strip() for item in workflow]
        if _valid_order(ids):
            return ids
    return None


def _ordered_roles(order: list[str] | None) -> list[dict]:
    ids = None
    if order:
        cleaned = [str(item).strip() for item in order]
        if _valid_order(cleaned):
            ids = cleaned
    if ids is None:
        ids = _saved_order() or [role["id"] for role in ROLES]
    ids = [role_id for role_id in ids if role_id != "deployer"] + ["deployer"]
    return [_ROLE_BY_ID[role_id] for role_id in ids]


def _seat_status(statuses: list[str]) -> str:
    if "FAIL" in statuses:
        return "FAIL"
    if statuses and set(statuses) == {"SKIP"}:
        return "SKIP"
    return "PASS"


def _rerender_once(ctx: dict, rows: list[dict]) -> None:
    """Review index.html after visual. Missing triggers is a no-op. One rerender at most."""
    raw = ctx.get("out")
    if not raw:
        return
    index = Path(raw) / "index.html"
    if not index.is_file():
        return
    try:
        from lib import triggers
    except ImportError:
        return
    reviewed = triggers.review(index.read_text(encoding="utf-8", errors="replace"))
    hits = reviewed.get("hits") if isinstance(reviewed, dict) else None
    if not isinstance(hits, list):
        return
    if not any(isinstance(hit, dict) and hit.get("fix") == "rerender" for hit in hits):
        return
    rendered = HANDS["render"](ctx)
    checked = HANDS["check_site"](ctx)
    rows.append(_hand(
        "frontend",
        str(rendered.get("status") or "FAIL"),
        str(rendered.get("detail") or ""),
    ))
    rows.append(_hand(
        "visual",
        str(checked.get("status") or "FAIL"),
        str(checked.get("detail") or ""),
    ))


def run_job(
    library: Library,
    project: Path,
    site: str,
    out: Path,
    mold_id: str,
    order: list[str] | None = None,
    frame_id: str = "",
) -> dict:
    """Run the seven seats through HANDS. Writes the site and crew-ticket.json. Does not publish."""
    project = Path(project)
    out = Path(out)
    ctx = {
        "project": str(project),
        "site": site,
        "out": str(out),
        "mold_id": mold_id,
        "vault": str(library.vault_root),
        "package_library": str(library.package_root),
        "live": False,
        "frame_id": str(frame_id or "").strip(),
        "hands": [],
    }
    rows: list[dict] = []
    stopped = False
    for role in _ordered_roles(order):
        if role["id"] == "deployer":
            continue
        if stopped:
            break
        details: list[str] = []
        statuses: list[str] = []
        for name in role["hands"]:
            if name == "library_bind":
                mold = ctx.get("mold") if isinstance(ctx.get("mold"), dict) else {}
                if mold.get("id"):
                    conflict = library.live_conflict(mold["id"], site)
                    if conflict:
                        details.append(f"mold {mold['id']} is already live on {conflict}")
                        statuses.append("FAIL")
                        stopped = True
                        break
            result = HANDS[name](ctx)
            details.append(str(result.get("detail") or ""))
            statuses.append(str(result.get("status") or "FAIL"))
            if result.get("status") == "FAIL":
                stopped = True
                break
        rows.append(_hand(role["id"], _seat_status(statuses), "; ".join(details)))
        if role["id"] == "visual":
            _rerender_once(ctx, rows)
    prior_fail = any(row["status"] == "FAIL" for row in rows)
    rows.append(_hand("deployer", "FAIL" if prior_fail else "PASS", _TICKET_NOTE))
    ctx["hands"] = rows
    ctx["mold_id"] = ctx.get("mold_id") or mold_id
    written = HANDS["ticket_write"](ctx)
    ticket = (written.get("data") or {}).get("ticket")
    if isinstance(ticket, dict):
        return ticket
    return _finish(out, site, mold_id, rows)


def _finish(out: Path, site: str, mold_id: str, hands: list[dict]) -> dict:
    ticket = {
        "site": site,
        "mold": mold_id,
        "publish": "Keith click. This run does not deploy.",
        "hands": hands,
        "ok": all(h["status"] == "PASS" for h in hands),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "crew-ticket.json").write_text(json.dumps(ticket, indent=2) + "\n", encoding="utf-8")
    return ticket


def selftest(root: Path, project: Path) -> int:
    pkg = root / "pkg"
    vault = root / "vault"
    lib = Library(pkg, vault)
    lib.save_mold({
        "id": "crew-scratch", "origin": "scratch",
        "palette": "#1f6f5b", "type_lead": "serif", "nav": "segmented",
        "template": "editorial",
    })
    out = root / "site"
    ticket = run_job(
        lib, project, "crew-demo.example", out, "crew-scratch",
        order=[role["id"] for role in ROLES],
    )
    if not ticket["ok"]:
        raise SystemExit("crew selftest failed: " + json.dumps(ticket["hands"]))
    content = next(row for row in ticket["hands"] if row["role"] == "content")
    if "copy/" not in content["detail"]:
        raise SystemExit("content did not cite copy files: " + content["detail"])
    if not (out / "index.html").exists():
        raise SystemExit("crew selftest wrote no index")
    lib.bind("crew-demo.example", "crew-scratch", live=True)
    try:
        lib.bind("other.example", "crew-scratch", live=True)
        raise SystemExit("seo reuse was allowed")
    except LibraryError:
        pass
    print("crew selftest ok")
    return 0
