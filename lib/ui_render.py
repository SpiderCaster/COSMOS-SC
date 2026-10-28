"""Stdio face: 12 seat-ordered screens over the engine (print/input only).

No curses, no deps, no background process. Every user action calls at most
one engine hand through lib.ui_hands (seat_gate first); views needing two
facts split into two actions ([g]aps, [v]ault). Consequential actions
(bind --live, --indexable, paid spend) print the exact CLI command and never
execute it. Preview panes are 360 + 1280 locked; serve stays localhost.

Body builders (board_text, gaps_text, ...) emit lines through the UI and
return the engine hands used, so the composer loop can show the same views
inside one verb without breaking its one-hand cap. Steps 6-7 add the
read-only rater verdict block (rater.json part/judge/verdict/cites, shown
on Checks/SEO) and the cDeck-last face (contract/order/dep-order lock,
shown on Import); both use 0 hands and never execute.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib import ui_hands as _hands  # noqa: E402
from lib import ui_orchestrator as _orc  # noqa: E402
from lib.tokens import WEIGHT_HERO_IMG, WEIGHT_HTML_GZIP, WEIGHT_HTML_RAW, WEIGHT_SCRIPT  # noqa: E402

_MARK = {"PASS": "[pass]", "FAIL": "[FAIL]", "WARN": "[warn]", "SKIP": "[skip]"}
_BUDGETS = (
    f"page <=220KB raw ({WEIGHT_HTML_RAW}B) / <=60KB gzip ({WEIGHT_HTML_GZIP}B); "
    f"hero <={WEIGHT_HERO_IMG // 1024}KB; script <={WEIGHT_SCRIPT // 1024}KB"
)

# Exact credit string (BOARD-locked; the URL is set by BOARD only, never invented).
CREDIT_EXACT = '<a class="sc-credit" href="[URL TBD]">Built with SpiderCaster</a>'

# A14: tap_target covers block/standalone controls only; inline prose links
# are exempt (WCAG 24px floor + padding technique instead).
TAP_A14 = (
    "tap_target (A14): primary CTA, nav segments, sticky-bar controls, button, "
    "summary, link-list items >=44px; inline prose links exempt."
)


def tree_root() -> Path:
    """Repo root (the tree this file lives in)."""
    return Path(__file__).resolve().parent.parent


def site_dir_for(project: str) -> Path:
    """Default built-site dir for a project (sites/<slug>)."""
    return tree_root() / "sites" / Path(project).name


def read_ledger(site_dir: Path) -> tuple[str, dict | None]:
    """(mode, tokens) from report.json. Missing/unknown stays None, never 0."""
    try:
        raw = json.loads((Path(site_dir) / "report.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "unknown", None
    tokens = raw.get("tokens")
    if not isinstance(tokens, dict):
        return str(raw.get("mode") or "unknown"), None
    return str(raw.get("mode") or "unknown"), tokens


def read_ticket(site_dir: Path) -> dict | None:
    """crew-ticket.json or None (no ticket is not an error here)."""
    try:
        raw = json.loads((Path(site_dir) / "crew-ticket.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return raw if isinstance(raw, dict) else None


def ticket_ok_text(ticket: dict | None) -> str:
    """One-line ticket verdict for the global footer."""
    if ticket is None:
        return "ticket: none"
    ok = ticket.get("ok") is True
    visual = ""
    for row in ticket.get("hands") or []:
        if isinstance(row, dict) and row.get("role") == "visual":
            visual = str(row.get("status") or "")
    tail = f" visual:{visual}" if visual else ""
    return f"ticket: {'ok' if ok else 'NOT OK'}{tail}"


def footer_lines(project: str, site_dir: Path) -> list[str]:
    """Global footer: ledger line + ticket ok (unknown stays unknown)."""
    mode, tokens = read_ledger(site_dir)
    if tokens is None:
        ledger = f"ledger: {mode}/unknown (no report.json; run a build first)"
    else:
        try:
            req = tokens.get("requests", 0) or 0
            cost = tokens.get("est_cost_usd", 0) or 0
            ledger = f"ledger: {mode}/{req} req/${cost}"
        except (AttributeError, TypeError, ValueError):
            ledger = f"ledger: {mode}/unknown"
    return [ledger, ticket_ok_text(read_ticket(site_dir))]


def credit_status(html: str) -> str:
    """Credit-string verdict: exact match, missing, or altered."""
    if CREDIT_EXACT in html:
        return "credit: exact sc-credit present"
    if "sc-credit" in html:
        return "credit: FAIL credit-altered (sc-credit present, string differs)"
    return "credit: absent (FAIL credit-missing on credit-required builds)"


# --------------------------------------------------------------------------
# Probe wiring, read-only (UI step 4): layout-probe.json -> visual_probe.
#
# Pure reads over the built site dir. This face never launches a browser,
# never writes a probe file, and never executes a command. State mirrors
# lib/check.py `_visual_probe_row` exactly (sha256 over sorted top-level
# *.html, hexdigest[:16] bound to html_hash/hash): NOT_RUN is SKIP, never
# PASS, and --release refuses it.
# --------------------------------------------------------------------------

#: Producer named by the checker's own visual_probe detail (verbatim).
PROBE_PRODUCER = "tools/layout_probe.py"


# Exact command that surfaces the visual_probe gate row (exists; verified).
def probe_surface_command(site_dir: Path | str) -> str:
    """Exact human command that surfaces the visual_probe row. Never run."""
    return f"python spidercaster.py check {site_dir}"


def probe_status(site_dir: Path | str) -> dict:
    """Read-only probe binding state for a built site dir (no hands).

    Returns state in {NOT_RUN, UNREADABLE, STALE, FAIL_ROWS, PASS} plus
    the checker-equivalent ``row`` in {SKIP, FAIL, PASS} and a detail.
    """
    site = Path(site_dir)
    pages = sorted(site.glob("*.html"))
    if not pages:
        return {
            "state": "NOT_RUN", "row": "SKIP",
            "detail": "no built pages; run a build first (visual_probe NOT RUN)",
        }
    probe = site / "layout-probe.json"
    if not probe.is_file():
        return {
            "state": "NOT_RUN", "row": "SKIP",
            "detail": ("no layout-probe.json "
                       "(checker: run tools/layout_probe.py); unrun!=pass"),
        }
    try:
        data = json.loads(probe.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {
            "state": "UNREADABLE", "row": "FAIL",
            "detail": f"layout-probe.json unreadable: {exc}",
        }
    if not isinstance(data, dict):
        return {
            "state": "UNREADABLE", "row": "FAIL",
            "detail": "layout-probe.json is not an object",
        }
    digest = hashlib.sha256()
    for page in pages:
        digest.update(page.read_bytes())
    current = digest.hexdigest()[:16]
    want = str(data.get("html_hash") or data.get("hash") or "")
    if want and want != current and current not in want:
        return {
            "state": "STALE", "row": "FAIL",
            "detail": "layout-probe.json stale (html changed); re-run probe",
            "html_hash": current,
        }
    rows = data.get("rows")
    if not isinstance(rows, list):
        rows = data.get("profiles")
    if isinstance(rows, list) and any(
        isinstance(row, dict) and row.get("status") == "FAIL" for row in rows
    ):
        return {
            "state": "FAIL_ROWS", "row": "FAIL",
            "detail": "probe rows contain FAIL",
            "html_hash": current,
        }
    return {
        "state": "PASS", "row": "PASS",
        "detail": f"probe {probe.name} bound to html {current}",
        "html_hash": current,
    }


# --------------------------------------------------------------------------
# Rater verdicts, read-only (UI step 6): rater.json -> Checks/SEO block.
#
# Pure reads over the built site dir. This face never judges, never
# writes, and never executes a command. Each verdict row names its own
# part (built section/part id), judge (who rated it), verdict
# (PASS/FAIL/WARN/SKIP), and cites (copy sources it was judged against).
# Missing/unjudged is NOT_RUN/SKIP, never PASS: unjudged is not a pass.
# An optional html_hash/hash binds verdicts to the built HTML exactly
# like the probe binding; a mismatch is STALE/FAIL.
# --------------------------------------------------------------------------

#: Rater verdict artifact the (out-of-tree) judge writes beside the pages.
RATER_FILE = "rater.json"

#: Verdict tokens a judge row may carry; anything else is a producer bug.
_RATER_VERDICTS = ("PASS", "FAIL", "WARN", "SKIP")


def rater_status(site_dir: Path | str) -> dict:
    """Read-only rater binding state for a built site dir (no hands).

    Returns state in {NOT_RUN, UNREADABLE, STALE, FAIL_ROWS, WARN_ROWS,
    SKIP_ROWS, PASS} plus the checker-equivalent ``row`` in
    {SKIP, FAIL, WARN, PASS}, the normalized ``rows`` and a detail.
    """
    site = Path(site_dir)
    pages = sorted(site.glob("*.html"))
    if not pages:
        return {
            "state": "NOT_RUN", "row": "SKIP", "rows": [],
            "detail": "no built pages; run a build first (rater NOT RUN)",
        }
    path = site / RATER_FILE
    if not path.is_file():
        return {
            "state": "NOT_RUN", "row": "SKIP", "rows": [],
            "detail": "no rater.json (unjudged is not a pass)",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {
            "state": "UNREADABLE", "row": "FAIL", "rows": [],
            "detail": f"rater.json unreadable: {exc}",
        }
    if not isinstance(data, dict):
        return {
            "state": "UNREADABLE", "row": "FAIL", "rows": [],
            "detail": "rater.json is not an object",
        }
    rows = data.get("rows")
    if not isinstance(rows, list) or not rows:
        return {
            "state": "FAIL_ROWS", "row": "FAIL", "rows": [],
            "detail": "rater.json carries no verdict rows (nothing judged)",
        }
    default_judge = str(data.get("judge") or "unknown-judge")
    want = str(data.get("html_hash") or data.get("hash") or "")
    current = ""
    if want:
        digest = hashlib.sha256()
        for page in pages:
            digest.update(page.read_bytes())
        current = digest.hexdigest()[:16]
        if want != current and current not in want:
            return {
                "state": "STALE", "row": "FAIL", "rows": [],
                "detail": "rater.json stale (html changed); re-run the judge",
                "html_hash": current,
            }
    verdicts: list[dict] = []
    broken = 0
    for row in rows:
        if not isinstance(row, dict):
            broken += 1
            verdicts.append({
                "part": "(unnamed)", "judge": default_judge,
                "verdict": "FAIL", "cites": [],
                "detail": "verdict row is not an object",
            })
            continue
        verdict = str(row.get("verdict") or "").upper()
        if verdict not in _RATER_VERDICTS:
            broken += 1
            verdict = "FAIL"
            detail = (f"unknown verdict token "
                      f"{str(row.get('verdict'))[:40]!r}; want PASS/FAIL/WARN/SKIP")
        else:
            detail = str(row.get("detail") or "")
        cites = row.get("cites")
        cites = [str(c) for c in cites] if isinstance(cites, list) else []
        verdicts.append({
            "part": str(row.get("part") or "(unnamed)"),
            "judge": str(row.get("judge") or default_judge),
            "verdict": verdict, "cites": cites, "detail": detail,
        })
    counts = {name: 0 for name in _RATER_VERDICTS}
    for row in verdicts:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    if counts["FAIL"]:
        state, mark = "FAIL_ROWS", "FAIL"
        extra = f"{counts['FAIL']} FAIL" + (" (+producer bug)" if broken else "")
    elif counts["SKIP"]:
        state, mark = "SKIP_ROWS", "SKIP"
        extra = f"{counts['SKIP']} SKIP (judge abstained)"
    elif counts["WARN"]:
        state, mark = "WARN_ROWS", "WARN"
        extra = f"{counts['WARN']} WARN"
    else:
        state, mark = "PASS", "PASS"
        extra = f"{counts['PASS']} PASS"
    out: dict = {
        "state": state, "row": mark, "rows": verdicts,
        "detail": f"rater {path.name}: {extra}",
    }
    if current:
        out["html_hash"] = current
    return out


# --------------------------------------------------------------------------
# cDeck-last wiring, read-only (UI step 7): contract + order + lock face.
#
# Pure reads: the cDeck contract (tab/sidebar) from plugin/cosmos.json,
# the package order from lib.crew ROLES, the saved override from the
# engine's own reader (env or the cDeck-owned engine.json), and the
# effective order with deployer forced last. The dep-order lock verdict
# reuses lib.ui_orchestrator.check_order verbatim. Reordering lives in
# the cDeck sidebar; the only CLI printed is the existing verifier
# (crew roles). This face never writes a workflow and never executes.
# --------------------------------------------------------------------------

#: cDeck contract fallback (plugin/cosmos.json is the source of truth).
CDECK_TAB = "website"
CDECK_SIDEBAR = "left"


def cdeck_contract() -> dict:
    """(tab, sidebar) the cDeck sidebar binds us at; unknown when absent."""
    try:
        raw = (tree_root() / "plugin" / "cosmos.json").read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, ValueError):
        return {"tab": "unknown", "sidebar": "unknown"}
    node = data.get("cdeck") if isinstance(data, dict) else None
    if not isinstance(node, dict):
        return {"tab": "unknown", "sidebar": "unknown"}
    return {
        "tab": str(node.get("tab") or "unknown"),
        "sidebar": str(node.get("sidebar") or "unknown"),
    }


def cdeck_status() -> dict:
    """Read-only cDeck binding state (no hands, no writes).

    Returns package/saved/effective seat orders, the workflow source,
    the (tab, sidebar) contract, and the deployer-last lock verdict.
    """
    from lib import crew as _crew

    package = [str(role.get("id")) for role in _crew.ROLES]
    saved = _crew._saved_order()
    effective = [str(role.get("id")) for role in _crew._ordered_roles(None)]
    if saved is None:
        source = "package order (no saved cDeck workflow)"
    else:
        witness = Path(_hands.cdeck_workflow_path())
        if witness.is_file():
            source = f"saved cDeck workflow ({witness})"
        else:
            source = "saved cDeck workflow (env override)"
    lock = _orc.check_order(effective)
    contract = cdeck_contract()
    return {
        "package": package, "saved": saved, "effective": effective,
        "source": source, "tab": contract["tab"],
        "sidebar": contract["sidebar"],
        "lock_ok": bool(lock.get("ok")),
        "lock_detail": str(lock.get("error") or "deployer stays last"),
    }


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock(project: str) -> tuple[bool, str]:
    """Exclusive session lock: project/.sc_ui_lock (pid inside)."""
    lock = Path(project) / ".sc_ui_lock"
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        try:
            pid = int(lock.read_text(encoding="utf-8").strip().split()[0])
        except (OSError, ValueError, IndexError):
            return False, f"locked by unreadable {lock} (remove it if stale)"
        if not _pid_alive(pid):
            return False, f"stale lock from pid {pid} (remove {lock} to proceed)"
        return False, f"locked by live pid {pid}"
    except OSError as exc:
        return False, f"cannot lock {lock}: {exc}"
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(str(os.getpid()))
    return True, str(lock)


def release_lock(project: str) -> None:
    """Release our own session lock; never touch another pid's lock."""
    lock = Path(project) / ".sc_ui_lock"
    try:
        if lock.read_text(encoding="utf-8").strip().split()[0] == str(os.getpid()):
            lock.unlink()
    except (OSError, ValueError, IndexError):
        pass


class UI:
    """Stdio UI. emit(input_fn) are injectable for --selftest stubbing."""

    def __init__(self, emit=None, input_fn=None):
        self._emit = emit if emit is not None else print
        self._input = input_fn if input_fn is not None else input
        self.counter: dict = {"hands_called": 0}
        self.used: list[str] = []
        self.project = ""
        self.site = ""
        self._last = -1

    def say(self, text: str = "") -> None:
        """One output line."""
        self._emit(text)

    def ask(self, prompt: str) -> str:
        """One input line (stubbed in selftest)."""
        self.say(prompt)
        try:
            return str(self._input())
        except (EOFError, StopIteration):
            return "q"

    def footer(self) -> None:
        """Global footer on every screen."""
        for line in footer_lines(self.project, Path(self.site)):
            self.say("  | " + line)

    def header(self, n: int, name: str) -> None:
        """Screen header with seat/hand/does_not/gate."""
        info = next(s for s in _orc.screens() if s["n"] == n)
        seat = info["seat"] or "-"
        self.say(f"== [{n}] {name} (seat: {seat}; hands: {', '.join(info['hands']) or 'none'}) ==")
        self.say(f"  does_not: {info['does_not']}")
        self.say(f"  gate: {info['gate']}")

    def run_hand(self, action: str, ctx: dict) -> dict:
        """One action, at most one engine hand (asserted)."""
        before = self.counter["hands_called"]
        result = _hands.run(action, ctx, self.counter)
        assert self.counter["hands_called"] - before <= 1, action
        self.used.append(action)
        return result

    # -- body builders (each: at most one hand; return hands used) --------

    def board_text(self, release: bool = False) -> list[str]:
        """Check-row board: every gate row id + status (visual/check_site)."""
        result = self.run_hand(
            "check_site", {"project": self.project, "out": self.site})
        rows = (result.get("data") or {}).get("rows") or []
        counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0}
        for row in rows:
            status = str(row.get("status") or "SKIP")
            counts[status] = counts.get(status, 0) + 1
            mark = _MARK.get(status, "[?]")
            self.say(f"  {mark} {row.get('name')} - {row.get('detail', '')}")
            for failure in (row.get("failures") or [])[:6]:
                self.say("      > " + _failure_line(failure))
            for item in (row.get("unmeasured") or [])[:4]:
                self.say("      ? " + _failure_line(item))
        self.say(f"  board: {counts['PASS']} pass / {counts['FAIL']} fail / "
                 + f"{counts['WARN']} warn / {counts['SKIP']} skip")
        blocked = counts["FAIL"] > 0 or (release and counts["SKIP"] > 0)
        if release:
            self.say("  --release: " + ("BLOCKED (NOT RUN is not a pass)"
                                        if blocked else "ok"))
        else:
            self.say("  exit-code truth: " + ("exit 1 (FAIL present)"
                                              if blocked else "exit 0"))
        self.say("  gaps name section.field; press [g] for the gap list.")
        return ["check_site"]

    def gaps_text(self) -> list[str]:
        """Gap list: FAILs name section.field (content/copy_gap)."""
        gaps = self.run_hand("copy_gap", {"project": self.project})
        self.say(f"  gaps: {gaps['status']}: {gaps['detail']}")
        if gaps["status"] == "FAIL":
            self.say("  gap FAILs name section.field (e.g. FAIL gap hero.headline).")
        else:
            self.say("  required misses FAIL as: FAIL gap <section>.<field>")
        return ["copy_gap"]

    def copy_text_view(self) -> list[str]:
        """CitedBlocks viewer (content/copy_read)."""
        result = self.run_hand("copy_read", {"project": self.project})
        data = result.get("data") or {}
        self.say(f"  {result['status']}: {result['detail']}")
        for title in (data.get("titles") or [])[:12]:
            self.say(f"    block: {title}")
        return ["copy_read"]

    def plan_text(self) -> list[str]:
        """Offline plan viewer, 0 tokens (frontend/plan_offline)."""
        result = self.run_hand("plan_offline", {"project": self.project})
        site_ir = (result.get("data") or {}).get("site_ir") or {}
        pages = site_ir.get("pages") or []
        self.say(f"  plan: {result['status']}: {result['detail']}")
        for page in pages:
            secs = page.get("sections") or []
            self.say(f"    page {page.get('file', '?')}: {len(secs)} section(s)")
        return ["plan_offline"]

    def build_run_text(self) -> list[str]:
        """Offline build executor (frontend/render). Writes pages + site.json."""
        result = self.run_hand(
            "render", {"project": self.project, "out": self.site})
        self.say(f"  build --offline: {result['status']}: {result['detail']}")
        self.say(f"  wrote: {', '.join((result.get('data') or {}).get('pages', []))}")
        return ["render"]

    def assets_text(self) -> list[str]:
        """Local assets + remote-drop warnings (graphics/asset_list)."""
        assets = self.run_hand("asset_list", {"project": self.project})
        data = assets.get("data") or {}
        self.say(f"  assets: {assets['status']}: {assets['detail']}")
        for rel in (data.get("local") or [])[:12]:
            self.say(f"    local: {rel}")
        for rel in (data.get("remote") or [])[:12]:
            self.say(f"    dropped_remote: {rel}")
        self.say("  press [v] for vault photos (separate action).")
        return ["asset_list"]

    def vault_text(self) -> list[str]:
        """Vault photo list (graphics/vault_photos)."""
        photos = self.run_hand("vault_photos", {"project": self.project})
        self.say(f"  vault: {photos['status']}: {photos['detail']}")
        return ["vault_photos"]

    def seo_text(self) -> list[str]:
        """Meta basics (seo/meta_basics). Fixes land through hands only."""
        meta = self.run_hand("meta_basics", {"out": self.site})
        self.say(f"  meta: {meta['status']}: {meta['detail']}")
        self.say("  fixes land through hands only; this screen never writes.")
        return ["meta_basics"]

    def preview_text(self) -> list[str]:
        """Preview readout: budgets, title/desc, robots, panes. No hands."""
        site = Path(self.site)
        index = site / "index.html"
        if not index.exists():
            self.say("  no index.html; run a build first (Build screen).")
        else:
            raw = index.read_bytes()
            gz = len(gzip.compress(raw))
            self.say(f"  index.html: {len(raw)}B raw / {gz}B gzip "
                     + f"(budgets {WEIGHT_HTML_RAW} / {WEIGHT_HTML_GZIP}): "
                     + f"{'OVER' if len(raw) > WEIGHT_HTML_RAW else 'ok'}")
            html = raw.decode("utf-8", errors="replace")
            title = re.search(r"<title>([^<]+)</title>", html)
            desc = re.search(r'<meta name="description" content="([^"]+)"', html)
            self.say(f"  title: {(title.group(1) if title else 'MISSING')[:70]}")
            self.say(f"  desc: {(desc.group(1)[:70] if desc else 'MISSING')}")
            robots = "noindex ON" if 'content="noindex' in html else "indexable"
            self.say(f"  robots badge: {robots} (preview shows what check sees)")
            self.say("  " + credit_status(html))
        self.say("  panes: 360 + 1280 locked (390 never substitutes for 360).")
        probe = probe_status(site)
        if probe["state"] == "PASS":
            self.say(f"  probe: visual_probe PASS ({probe['detail']}).")
        elif probe["state"] == "NOT_RUN":
            self.say("  probe: visual_probe is NOT RUN, never PASS"
                     " (--release BLOCKED until a probe binds).")
        else:
            self.say(f"  probe: visual_probe {probe['row']}"
                     f" ({probe['state']}: {probe['detail']}).")
        writer = tree_root() / PROBE_PRODUCER
        self.say(f"  probe writer: {PROBE_PRODUCER} "
                 + ("present." if writer.exists() else "absent (no probe can bind)."))
        self.say("  url: http://localhost:4173 (localhost only; no tunnel/share).")
        return []

    def probe_text(self) -> list[str]:
        """Probe wiring readout: layout-probe.json -> visual_probe (0 hands).

        Read-only: states the binding, names NOT RUN as release-blocking,
        and prints the exact surface command without running it.
        """
        site = Path(self.site)
        probe = probe_status(site)
        self.say(f"  visual_probe: {probe['row']}"
                 f" ({probe['state']}: {probe['detail']})")
        if probe["row"] == "SKIP":
            self.say("  NOT RUN is not a pass: --release refuses this site.")
        writer = tree_root() / PROBE_PRODUCER
        self.say(f"  producer: {PROBE_PRODUCER} "
                 + ("present." if writer.exists() else "absent (checker names it)."))
        self.say("  surface: " + probe_surface_command(self.site)
                 + " (UI prints it; UI never runs it).")
        return []

    def publish_text(self) -> list[str]:
        """Publish-readiness view: validity + exact bind command (0 hands).

        Validity reuses ``lib.ui_composer.verify_for_publish`` verbatim
        (engine ``verify_live_ticket`` refusal strings unchanged). The
        command is printed for a human Keith click; ``executed`` is always
        False — this face cannot publish by itself.
        """
        from lib import ui_composer as _composer

        verdict = _composer.verify_for_publish(Path(self.site))
        self.say("  publish readiness (this face never executes bind --live):")
        if verdict["ok"]:
            self.say(f"  status: READY - {verdict['message']}")
        else:
            self.say(f"  status: REFUSED - {verdict['message']}")
        if verdict["command"]:
            self.say("  human command (UI never executes it):")
            self.say("  " + verdict["command"])
        return []

    def rater_text(self) -> list[str]:
        """Rater verdict block: part/judge/verdict/cites (0 hands).

        Read-only render of ``rater_status``: every verdict row names the
        part judged, the judge, the verdict, and the copy cites. Unjudged
        is NOT RUN, never a pass. Prints the exact surface command
        without running it.
        """
        state = rater_status(Path(self.site))
        self.say(f"  rater: {state['row']} ({state['state']}: {state['detail']})")
        if state["state"] == "NOT_RUN":
            self.say("  NOT RUN (unjudged is not a pass):"
                     " no verdict row can gate a release.")
        for row in state["rows"][:12]:
            mark = _MARK.get(str(row.get("verdict")), "[?]")
            cites = ", ".join(row.get("cites") or []) or "-"
            self.say(f"    {mark} part {row.get('part')}"
                     f" (judge {row.get('judge')}): cites {cites}"[:160])
            if row.get("detail"):
                self.say(f"      > {str(row.get('detail'))[:120]}")
        self.say("  surface: " + _hands.rater_surface_command(self.site)
                 + " (UI prints it; UI never runs it).")
        return []

    def cdeck_text(self) -> list[str]:
        """cDeck-last face: contract + order + lock + buttons (0 hands).

        Read-only render of ``cdeck_status``: the sidebar contract, the
        effective seat order and its source, and the deployer-last lock
        verdict (via the ui_hands dep-order preview, check_order
        verbatim). Reordering lives in the cDeck sidebar; the only CLI
        printed is the existing verifier. Never writes, never runs.
        """
        status = cdeck_status()
        self.say(f"  cdeck: tab {status['tab']} ({status['sidebar']} sidebar;"
                 " contract plugin/cosmos.json).")
        self.say(f"  order: {' -> '.join(status['effective'])}")
        self.say(f"  source: {status['source']}")
        if status["saved"] is not None and list(status["saved"]) != list(
                status["effective"]):
            self.say(f"  saved: {' -> '.join(status['saved'])}"
                     " (deployer re-seated last)")
        preview = _hands.cdeck_order_preview(status["effective"])
        if preview["ok"]:
            self.say("  dep-order lock: LOCKED"
                     " (deployer stays last; anything else refused).")
        else:
            self.say(f"  dep-order lock: REFUSED ({preview['detail']})")
        self.say("  verify: " + _hands.cdeck_verify_command()
                 + " (UI prints it; UI never runs it).")
        self.say(f"  reorder: cDeck sidebar only ({_hands.cdeck_workflow_path()});"
                 " UI never writes it.")
        return []

    def screen_projects(self) -> None:
        """Screen 0: project list (brief? copy count? last ticket ok?)."""
        self.header(0, "Projects")
        root = tree_root() / "projects"
        names = sorted(p.name for p in root.iterdir() if p.is_dir()) if root.is_dir() else []
        for name in names:
            proj = root / name
            brief = "brief" if (proj / "brief.md").exists() else "no-brief"
            copy_dir = proj / "copy"
            count = 0
            if copy_dir.is_dir():
                count = sum(1 for p in copy_dir.iterdir() if p.is_file())
            tick = read_ticket(site_dir_for(str(proj)))
            mark = "ticket:ok" if (tick or {}).get("ok") is True else "ticket:-"
            self.say(f"  {name} [{brief} copy:{count} {mark}]")
        self.say("  select: type a project name (session = project dir + lock).")
        self.say("  scaffold: python spidercaster.py init <name> (UI prints, never runs init).")
        self.footer()

    def screen_brief(self) -> None:
        """Screen 1: brief rendered; empty-brief refusal."""
        self.header(1, "Brief")
        result = self.run_hand("brief_read", {"project": self.project})
        self.say(f"  {result['status']}: {result['detail']}")
        self.footer()

    def screen_copy(self, gaps: bool = False) -> None:
        """Screen 2: CitedBlocks; [g]aps name section.field (2nd action)."""
        self.header(2, "Copy")
        if gaps:
            self.gaps_text()
        else:
            self.copy_text_view()
            self.say("  required misses FAIL as: FAIL gap <section>.<field> ([g]aps).")
        self.footer()

    def screen_frame_mold(self) -> None:
        """Screen 3: frame slots + mold tokens; draft binds only."""
        self.header(3, "Frame+Mold")
        smap = tree_root() / self.project / "sitemap.json" if self.project else None
        if smap is not None and smap.exists():
            try:
                pages = json.loads(smap.read_text(encoding="utf-8")).get("pages", [])
                self.say(f"  sitemap: {len(pages)} page(s)")
            except (OSError, ValueError):
                self.say("  sitemap: unreadable")
        else:
            self.say("  sitemap: none")
        self.say("  picks run through architect hands; binds here are drafts only.")
        self.say("  live bind is a Keith click (see Ticket screen for the command).")
        self.footer()

    def screen_build(self, choice: str = "") -> None:
        """Screen 4 (engine room): offline plan, token mode, budgets."""
        self.header(4, "Build")
        mode, _tokens = read_ledger(Path(self.site))
        self.say(f"  token mode: {mode} (offline default; AI only explicit + providers).")
        self.say(f"  budgets: {_BUDGETS}")
        if choice == "p":
            self.plan_text()
        elif choice == "b":
            self.build_run_text()
        else:
            self.say("  [p]lan (0 tokens)  [b]uild --offline  [f]rom site.json (0 tokens)")
            self.say("  build --from: python spidercaster.py build "
                     + f"--from {self.site}/site.json --offline")
        self.footer()

    def screen_assets(self, vault: bool = False) -> None:
        """Screen 5 (engine room): local assets; [v]ault photos (2nd action)."""
        self.header(5, "Assets")
        if vault:
            self.vault_text()
        else:
            self.assets_text()
        self.footer()

    def screen_preview(self, choice: str = "") -> None:
        """Screen 6 (engine room): localhost URL; 360/1280 locked panes."""
        self.header(6, "Preview")
        self.preview_text()
        site = Path(self.site)
        if choice == "s" and (site / "index.html").exists():
            self.start_server()
        else:
            self.say("  command: " + _hands.serve_command(self.site))
            self.say("  [s]tart localhost server (Ctrl+C stops) or Enter to go back.")
        self.footer()

    def start_server(self) -> None:
        """Blocking localhost preview (interactive only; never in selftest)."""
        from lib import serve as _serve

        httpd, port = _serve.serve(Path(self.site), 4173)
        self.say(f"  preview: http://localhost:{port} (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()

    def screen_checks(self, release: bool = False, gaps: bool = False) -> None:
        """Screen 7 (check-row board): every gate row id + status.

        Gaps show section.field via a second [g]aps action (one hand each).
        --release also fails on NOT RUN (SKIP).
        """
        self.header(7, "Checks")
        self.say(f"  {TAP_A14}")
        self.say(f"  budgets: {_BUDGETS}")
        if gaps:
            self.gaps_text()
        else:
            self.board_text(release=release)
        self.rater_text()
        self.footer()

    def screen_seo(self) -> None:
        """Screen 8: one-H1, title/desc, slugs, JSON-LD (guidance only)."""
        self.header(8, "SEO")
        self.seo_text()
        self.rater_text()
        self.footer()

    def screen_ticket(self) -> None:
        """Screen 9: ticket view + publish readiness (never executes)."""
        self.header(9, "Ticket")
        ticket = read_ticket(Path(self.site))
        if ticket is None:
            self.say("  no crew-ticket.json; run the crew first (or build, then crew run).")
            from lib import ui_composer as _composer

            self.say("  command shape (needs a green ticket first; UI never executes it):")
            self.say("  " + _composer.bind_command("?", "?", self.site or "?"))
        else:
            self.say(f"  ok: {ticket.get('ok')}; site: {ticket.get('site')}; "
                     + f"mold: {ticket.get('mold')}")
            hashes = ticket.get("sha256") or ticket.get("hashes") or {}
            self.say(f"  sha-bound files: {len(hashes)}")
            visual = [r for r in ticket.get("hands") or []
                      if isinstance(r, dict) and r.get("role") == "visual"]
            for row in visual:
                self.say(f"  visual row: {row.get('status')}")
            self.say("  a 1-byte edit invalidates the hash; bind recomputes and refuses.")
        self.say("  no publish button.")
        self.publish_text()
        self.footer()

    def screen_library(self) -> None:
        """Screen 10: Light subset Full; tier/white-label/credit gates."""
        self.header(10, "Library")
        light = tree_root() / "light.json"
        self.say(f"  light.json: {'present (source of truth)' if light.exists() else 'absent'}")
        site = Path(self.site)
        index = site / "index.html"
        if index.exists():
            self.say("  " + credit_status(index.read_text(encoding="utf-8", errors="replace")))
        else:
            self.say("  credit: no built page to verify (build first).")
        self.footer()

    def screen_import(self) -> None:
        """Screen 11: importer funnel status (source tree stays read-only)."""
        self.header(11, "Import")
        inbound = tree_root() / "_inbound"
        if inbound.is_dir():
            names = sorted(p.name for p in inbound.iterdir() if p.name != ".gitkeep")
            self.say(f"  _inbound: {len(names)} candidate(s)")
            for name in names[:12]:
                self.say(f"    candidate: {name}")
        else:
            self.say("  _inbound: empty (no candidates).")
        self.say("  source tree is read-only; import lands in _inbound only.")
        self.cdeck_text()
        self.footer()

    # -- main loop -------------------------------------------------------

    def loop(self, project: str) -> int:
        """Interactive menu loop. Returns process exit code."""
        self.project = project
        self.site = str(site_dir_for(project))
        ok, info = acquire_lock(project)
        if not ok:
            self.say(info)
            return 1
        try:
            self.screen_projects()
            self._last = 0
            while True:
                raw = self.ask("ui [0-11 project|p plan|b build|s serve|r release|"
                               "g gaps|v vault|q] >").strip()
                if raw in ("q", "quit", ""):
                    self.say("bye (lock released; project state intact).")
                    return 0
                if raw.isdigit() and int(raw) in range(12):
                    self.show(int(raw))
                    continue
                if raw == "p":
                    self.screen_build(choice="p")
                elif raw == "b":
                    self.screen_build(choice="b")
                elif raw == "s":
                    self.screen_preview(choice="s")
                elif raw == "r":
                    self.screen_checks(release=True)
                    self._last = 7
                elif raw == "g" and self._last in (2, 7):
                    if self._last == 7:
                        self.screen_checks(gaps=True)
                    else:
                        self.screen_copy(gaps=True)
                elif raw == "v" and self._last == 5:
                    self.screen_assets(vault=True)
                else:
                    self.say("unknown key (0-11, p, b, s, r, g, v, q).")
        finally:
            release_lock(project)
        return 0

    def show(self, n: int) -> None:
        """Render one screen (read-only default; no writes without a key)."""
        self._last = n
        if n == 0:
            self.screen_projects()
        elif n == 1:
            self.screen_brief()
        elif n == 2:
            self.screen_copy()
        elif n == 3:
            self.screen_frame_mold()
        elif n == 4:
            self.screen_build()
        elif n == 5:
            self.screen_assets()
        elif n == 6:
            self.screen_preview()
        elif n == 7:
            self.screen_checks()
        elif n == 8:
            self.screen_seo()
        elif n == 9:
            self.screen_ticket()
        elif n == 10:
            self.screen_library()
        elif n == 11:
            self.screen_import()


def _failure_line(failure) -> str:
    """One-line failure text for board rows (dicts or plain strings)."""
    if isinstance(failure, dict):
        bits = [str(failure.get(k)) for k in ("file", "where", "detail")
                if failure.get(k)]
        return " | ".join(bits) if bits else json.dumps(failure, sort_keys=True)[:160]
    return str(failure)[:160]


def main(argv: list[str] | None = None) -> int:
    """`spidercaster.py ui --screens [project]` entry (composer owns `ui`)."""
    import argparse

    parser = argparse.ArgumentParser(prog="spidercaster.py ui --screens")
    parser.add_argument("project", nargs="?", default="projects/demo-local")
    args = parser.parse_args(argv)
    ui = UI()
    return ui.loop(args.project)


if __name__ == "__main__":
    raise SystemExit(main())
