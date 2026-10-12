"""SpiderCaster UI composer + ticket/ledger face (UI steps 0-1).

Thin stdio face over the deterministic engine: propose-only, offline-first,
zero-token default, checker-gated, human publish. Stdlib only.

Composer semantics follow SPARK plan section 3 as requirements (FINAL V3):

* ``/``-prefixed lines are frozen parse-only descriptors (``effect=none``);
  anything else is plain prompt text. Descriptors never execute.
* Caps: history 50, multiline buffer 32 lines x 4000 chars/line, RETRY_CAP 2.
* No ``off``/``yolo`` mode (BAD_MODE); ``!`` lines stay plain text and never
  shell; SECRET-looking lines are refused and never stored.
* Approval ladder is manual -> acceptEdits -> plan; transcripts rebuild and
  restore without side effects; Esc/Esc-Esc map to interrupt-then-rewind
  ("re-run from the last green gate", no snapshot machinery in v1).
* Consequential actions print the exact CLI command and never run it
  (``executed`` is always False on the publish path).

Ticket/ledger face (UI step 1): the ticket panel always renders, even on
FAIL or when the ticket file is missing. ``ok:true`` displays only on zero
FAIL plus visual PASS. Publish readiness reuses the engine gate
``lib.library.verify_live_ticket`` verbatim: its refusal strings are shown
unchanged, never repaired or reworded.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# --------------------------------------------------------------------------
# Composer caps and frozen descriptors (parse-only, effect=none)
# --------------------------------------------------------------------------

HISTORY_CAP = 50
BUFFER_LINES = 32
BUFFER_CHARS = 4000
RETRY_CAP = 2

APPROVALS = ("manual", "acceptEdits", "plan")

#: Frozen descriptor table: (verb, effect target outside the parser, help).
DESCRIPTORS = (
    ("/help", "none", "list verbs; parse-only, never executes"),
    ("/tools", "none", "list available verbs; same caps as /help"),
    ("/model", "none", "show the provider chain; read-only"),
    ("/approval", "none", "show or set manual -> acceptEdits -> plan"),
    ("/rollback", "none", "rewind help; v1 has no snapshot store"),
    ("/interrupt", "none", "set the interrupt flag; in-flight runs land"),
    ("/plan", "none", "0-token offline dry run; writes nothing"),
    ("/diff", "none", "deferred to step 2+; use the CLI meanwhile"),
    ("/check", "none", "deferred to step 2+; use spidercaster.py check"),
    ("/ticket", "none", "show crew-ticket.json binding; always renders"),
    ("/publish", "none", "arm the human publish click; never executes"),
    ("/compact", "none", "summarize history to free context"),
    ("/account", "none", "quota header is TokenCenter scope; show pointer"),
)

_DESCRIBE = {verb: (target, help_) for verb, target, help_ in DESCRIPTORS}

_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|passwd|password)\b\s*[:=]\s*\S"
)
_BANG_RE = re.compile(r"^\s*!\s*\S")


def _is_bad_mode(text: str) -> bool:
    """Bare off/yolo words or flags are never a composer mode."""
    words = re.split(r"\s+", text.strip().strip("/").lower())
    return any(word in ("off", "yolo", "--yolo", "--off") for word in words)


def parse_line(text: str) -> dict:
    """Parse one composer line. Never executes, never shells, never stores.

    Returns a small dict with ``kind`` in
    {empty, descriptor, plain, unknown, refused} plus a machine ``code``.
    """
    raw = text if isinstance(text, str) else ""
    stripped = raw.strip()
    if not stripped:
        return {"kind": "empty", "code": "EMPTY", "text": raw}
    if _is_bad_mode(stripped):
        return {
            "kind": "refused",
            "code": "BAD_MODE",
            "text": raw,
            "detail": "no off/yolo mode; ladder is manual -> acceptEdits -> plan",
        }
    if _SECRET_RE.search(stripped):
        return {
            "kind": "refused",
            "code": "SECRET",
            "text": "",
            "detail": "secret-looking line refused; not stored, not echoed",
        }
    if _BANG_RE.match(stripped):
        # `!` lines stay plain text in the parser; shell execution, if ever,
        # lives behind the approval gate in the runner, never here.
        return {"kind": "plain", "code": "PLAIN", "text": raw}
    if stripped.startswith("/"):
        verb = stripped.split()[0]
        args = stripped[len(verb):].strip()
        if verb in _DESCRIBE:
            if verb == "/approval" and args and args not in APPROVALS:
                return {
                    "kind": "refused",
                    "code": "BAD_MODE",
                    "text": raw,
                    "detail": "ladder is manual -> acceptEdits -> plan",
                }
            return {
                "kind": "descriptor",
                "code": "DESCRIPTOR",
                "verb": verb,
                "args": args,
                "text": raw,
            }
        return {
            "kind": "unknown",
            "code": "UNKNOWN",
            "text": raw,
            "detail": "unknown verb; /help lists the frozen set",
        }
    return {"kind": "plain", "code": "PLAIN", "text": raw}


# --------------------------------------------------------------------------
# Session: history, multiline buffer, interrupt, transcript rebuild/restore
# --------------------------------------------------------------------------


class Session:
    """Owns composer history (cap 50), buffer, approval, interrupt flag."""

    def __init__(self) -> None:
        self.history: list[dict] = []
        self.buffer: list[str] = []
        self.approval = "manual"
        self.interrupted = False
        self.compacted = 0
        self._rollback_miss = False

    # -- intake -----------------------------------------------------------
    def accept(self, text: str) -> dict:
        """Parse one line and record it. Refused lines are never stored."""
        action = parse_line(text)
        if action["kind"] == "refused":
            return action
        if action["kind"] == "empty":
            return action
        if action["kind"] == "descriptor" and action.get("verb") == "/interrupt":
            self.interrupted = True
        self.history.append({
            "line": action.get("text", ""),
            "kind": action["kind"],
            "verb": action.get("verb", ""),
        })
        del self.history[:-HISTORY_CAP]
        return action

    def append_line(self, text: str) -> dict:
        """Append to the multiline buffer (32 lines x 4000 chars)."""
        line = text if isinstance(text, str) else ""
        if len(self.buffer) >= BUFFER_LINES:
            return {"ok": False, "code": "BUFFER_FULL"}
        if len(line) > BUFFER_CHARS:
            return {"ok": False, "code": "LINE_TOO_LONG"}
        self.buffer.append(line)
        return {"ok": True, "code": "BUFFERED", "lines": len(self.buffer)}

    def flush(self) -> list[str]:
        """Drain the buffer. In-flight content always lands, never drops."""
        out = list(self.buffer)
        self.buffer = []
        return out

    def interrupt(self) -> dict:
        """Esc: set the flag. Esc-Esc (rewind) is re-run from last green."""
        self.interrupted = True
        self.buffer = []
        return {"ok": True, "code": "INTERRUPTED"}

    # -- approval ladder --------------------------------------------------
    def set_approval(self, mode: str) -> dict:
        mode = str(mode or "").strip()
        if mode in APPROVALS:
            self.approval = mode
            return {"ok": True, "code": "APPROVAL", "mode": mode}
        return {
            "ok": False,
            "code": "BAD_MODE",
            "detail": "ladder is manual -> acceptEdits -> plan",
        }

    # -- rollback seam (no snapshot store in v1) ---------------------------
    def rollback(self) -> dict:
        """Checkpoint restore over an empty store: ROLLBACK_MISS, once."""
        self._rollback_miss = True
        return {
            "ok": False,
            "code": "ROLLBACK_MISS",
            "detail": "no checkpoints in v1; re-run from the last green gate",
        }

    # -- transcript ---------------------------------------------------------
    def transcript(self) -> list[dict]:
        return [dict(row) for row in self.history]

    def rebuild(self, lines: list[str]) -> list[dict]:
        """Re-parse lines without touching history (restore preview)."""
        return [parse_line(line) for line in (lines or [])]

    def restore(self, data: list[dict]) -> dict:
        """Load transcript rows; caps at 50, drops malformed rows."""
        kept = []
        for row in (data or []):
            if not isinstance(row, dict):
                continue
            line = row.get("line", "")
            kind = row.get("kind", "")
            if not isinstance(line, str) or kind not in (
                "descriptor", "plain", "unknown",
            ):
                continue
            kept.append({
                "line": line[:BUFFER_CHARS],
                "kind": kind,
                "verb": str(row.get("verb", "")),
            })
        self.history = kept[-HISTORY_CAP:]
        return {"ok": True, "code": "RESTORED", "rows": len(self.history)}

    def compact(self) -> dict:
        """Summarize history to free context (cap-honoring)."""
        kept = [row for row in self.history if row.get("kind") == "descriptor"]
        self.history = kept[-HISTORY_CAP:]
        self.compacted += 1
        return {"ok": True, "code": "COMPACTED", "rows": len(self.history)}


def transcript_save(session: Session, path: Path) -> Path:
    """Persist a transcript. Session state is not a ledger."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "spidercaster-ui-transcript/1",
        "approval": session.approval,
        "rows": session.transcript(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def transcript_load(path: Path) -> dict:
    """Read a saved transcript; malformed files refuse closed."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"ok": False, "code": "BAD_TRANSCRIPT"}
    if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
        return {"ok": False, "code": "BAD_TRANSCRIPT"}
    approval = data.get("approval", "manual")
    if approval not in APPROVALS:
        approval = "manual"
    return {"ok": True, "approval": approval, "rows": data["rows"]}


# --------------------------------------------------------------------------
# Ticket face: always rendered, even on FAIL or a missing file
# --------------------------------------------------------------------------


def visual_status(ticket: dict) -> str | None:
    """Visual-critic status across both ticket hands shapes (or None)."""
    hands = ticket.get("hands") if isinstance(ticket, dict) else None
    if not isinstance(hands, list):
        return None
    for row in hands:
        if isinstance(row, dict) and row.get("role") == "visual":
            status = row.get("status")
            return str(status) if status else None
    for row in hands:
        if isinstance(row, dict) and row.get("hand") == "check_site":
            status = row.get("status")
            return str(status) if status else None
    return None


def ticket_ok(ticket: dict) -> bool:
    """True only on zero FAIL (engine ``ok``) plus visual PASS."""
    if not isinstance(ticket, dict):
        return False
    return ticket.get("ok") is True and visual_status(ticket) == "PASS"


def read_ticket(site_dir: Path) -> tuple[dict | None, str | None]:
    """Read crew-ticket.json. Returns (ticket, None) or (None, reason)."""
    path = Path(site_dir) / "crew-ticket.json"
    if not path.is_file():
        return None, f"bad ticket: {path} missing; re-run the crew"
    try:
        ticket = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, f"bad ticket: {path} unreadable"
    if not isinstance(ticket, dict):
        return None, f"bad ticket: {path} is not an object"
    return ticket, None


def render_ticket(site_dir: Path) -> str:
    """Always-rendered ticket panel. Missing files render as ok:false."""
    site_dir = Path(site_dir)
    ticket, reason = read_ticket(site_dir)
    lines = [f"ticket: {site_dir / 'crew-ticket.json'}"]
    if ticket is None:
        lines.append("ok: false")
        lines.append(f"refusal: {reason}")
        lines.append("visual: NOT_RUN (no ticket to read)")
        lines.append("publish: Keith click. This run does not deploy.")
        return "\n".join(lines) + "\n"
    visual = visual_status(ticket) or "NOT_RUN"
    lines.append(f"site: {ticket.get('site')}")
    lines.append(f"mold: {ticket.get('mold')}")
    lines.append(f"ok: {'true' if ticket_ok(ticket) else 'false'}")
    lines.append(f"visual: {visual}")
    hands = ticket.get("hands")
    if isinstance(hands, list) and hands:
        for row in hands:
            if not isinstance(row, dict):
                continue
            name = row.get("role", row.get("hand", "?"))
            lines.append(f"  [{row.get('status', '?')}] {name}: {row.get('detail', '')}")
    else:
        lines.append(f"  note: {ticket.get('note', 'ticket written')}")
    hashes = ticket.get("sha256", ticket.get("hashes"))
    if isinstance(hashes, dict):
        lines.append(f"sha256: {len(hashes)} bound file(s)")
    else:
        lines.append("sha256: none recorded (bad ticket: no sha256/hashes map)")
    lines.append(f"publish: {ticket.get('publish', 'Keith click. This run does not deploy.')}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Ledger face: read-only view over report.json (never a second book)
# --------------------------------------------------------------------------


def _fmt_tokens(value) -> str:
    """Unknown usage stays unknown; offline totals render numeric 0."""
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "unknown"
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    return "unknown"


def read_ledger(site_dir: Path) -> tuple[dict | None, str | None]:
    """Read report.json. Returns (ledger, None) or (None, reason)."""
    path = Path(site_dir) / "report.json"
    if not path.is_file():
        return None, "no ledger yet (run a build first)"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, f"ledger unreadable: {path}"
    if not isinstance(data, dict):
        return None, f"ledger unreadable: {path} is not an object"
    return data, None


def render_ledger(site_dir: Path) -> str:
    """Footer-grade ledger lines: mode/tokens/cost from report.json."""
    site_dir = Path(site_dir)
    data, reason = read_ledger(site_dir)
    lines = [f"ledger: {site_dir / 'report.json'}"]
    if data is None:
        lines.append(reason or "no ledger yet")
        return "\n".join(lines) + "\n"
    tokens = data.get("tokens") if isinstance(data.get("tokens"), dict) else {}
    lines.append(
        "mode={m} provider={p} model={mo}".format(
            m=data.get("mode", "unknown"),
            p=data.get("provider") or "none",
            mo=data.get("model") or "none",
        )
    )
    lines.append(
        "tokens: requests={r} ok={o} in={i} out={t} cost_usd={c}".format(
            r=_fmt_tokens(tokens.get("requests")),
            o=_fmt_tokens(tokens.get("ok")),
            i=_fmt_tokens(tokens.get("in_tokens")),
            t=_fmt_tokens(tokens.get("out_tokens")),
            c=_fmt_tokens(tokens.get("est_cost_usd")),
        )
    )
    attempts = data.get("attempts")
    if isinstance(attempts, list):
        lines.append(f"attempts: {len(attempts)}")
        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue
            known = attempt.get("cost_known")
            if known is False or attempt.get("est_cost_usd") is None:
                cost = "unknown (cost_known:false)"
            else:
                cost = _fmt_tokens(attempt.get("est_cost_usd"))
            lines.append(
                "  {at} {purpose} ok={ok} cost={cost}".format(
                    at=attempt.get("at", "?"),
                    purpose=attempt.get("purpose", "?"),
                    ok=attempt.get("ok", "?"),
                    cost=cost,
                )
            )
    else:
        lines.append("attempts: unknown")
    return "\n".join(lines) + "\n"


def render_footer(site_dir: Path) -> str:
    """One ledger + ticket status line, shown on every screen."""
    site_dir = Path(site_dir)
    data, _ = read_ledger(site_dir)
    ticket, _ = read_ticket(site_dir)
    if data is not None:
        tokens = data.get("tokens") if isinstance(data.get("tokens"), dict) else {}
        ledger_bit = "mode={m} tokens={t} cost={c}".format(
            m=data.get("mode", "unknown"),
            t=_fmt_tokens(tokens.get("requests")),
            c=_fmt_tokens(tokens.get("est_cost_usd")),
        )
    else:
        ledger_bit = "ledger=none"
    if ticket is not None:
        ticket_bit = (
            "ticket ok=" + ("true" if ticket_ok(ticket) else "false")
            + " visual=" + (visual_status(ticket) or "NOT_RUN")
        )
    else:
        ticket_bit = "ticket ok=false visual=NOT_RUN"
    return f"{ledger_bit} | {ticket_bit}\n"


# --------------------------------------------------------------------------
# Publish readiness: print the exact command, never execute it
# --------------------------------------------------------------------------


def bind_command(site: str, mold: str, out: str) -> str:
    """The exact human-publish command the UI prints (never runs)."""
    return (
        "python spidercaster.py library bind --live"
        f" --site {site} --mold {mold} --out {out}"
    )


def verify_for_publish(
    site_dir: Path, site: str = "", mold: str = "", out: str = "",
) -> dict:
    """Arm the human click: verify the live ticket, print the command.

    Refusal strings from ``verify_live_ticket`` are returned verbatim.
    ``executed`` is always False: this face cannot publish by itself.
    """
    from lib.library import LibraryError, verify_live_ticket

    site_dir = Path(site_dir)
    ticket, reason = read_ticket(site_dir)
    if ticket is None:
        return {
            "ok": False,
            "code": "BAD_TICKET",
            "message": reason or "bad ticket",
            "command": "",
            "executed": False,
        }
    site = str(site or ticket.get("site") or "").strip()
    mold = str(mold or ticket.get("mold") or "").strip()
    label = str(out or site_dir).strip()
    command = bind_command(site or "?", mold or "?", label or "?")
    if not site or not mold:
        return {
            "ok": False,
            "code": "BAD_TICKET",
            "message": "bad ticket: site/mold missing; re-run the crew",
            "command": command,
            "executed": False,
        }
    try:
        verify_live_ticket(site_dir, site, mold)
    except LibraryError as exc:
        return {
            "ok": False,
            "code": "REFUSED",
            "message": str(exc),
            "command": command,
            "executed": False,
        }
    return {
        "ok": True,
        "code": "READY",
        "message": "ticket verifies; a human runs the command below",
        "command": command,
        "executed": False,
    }


def render_publish(site_dir: Path, site: str = "", mold: str = "") -> str:
    """Publish-readiness view: validity plus the exact bind command."""
    verdict = verify_for_publish(site_dir, site=site, mold=mold)
    lines = ["publish readiness (this face never executes bind --live):"]
    if verdict["ok"]:
        lines.append(f"status: READY — {verdict['message']}")
    else:
        lines.append(f"status: REFUSED — {verdict['message']}")
    if verdict["command"]:
        lines.append(f"command: {verdict['command']}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Projects screen (step 0): brief present? copy count? last ticket ok?
# --------------------------------------------------------------------------


def list_projects(projects_root: Path, sites_root: Path) -> list[dict]:
    """One row per project dir: brief, copy count, matching site ticket."""
    rows = []
    root = Path(projects_root)
    sites = Path(sites_root)
    if not root.is_dir():
        return rows
    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if not child.is_dir() or child.name.startswith((".", "_")):
            continue
        brief = (child / "brief.md").is_file()
        copy_dir = child / "copy"
        if copy_dir.is_dir():
            count = sum(
                1 for path in copy_dir.rglob("*")
                if path.is_file() and path.suffix.lower() in (".md", ".txt", ".json")
            )
        else:
            count = 0
        ticket, _ = read_ticket(sites / child.name)
        if ticket is None:
            state = "none"
        elif ticket_ok(ticket):
            state = "ok:true"
        else:
            state = "ok:false"
        rows.append({
            "name": child.name,
            "brief": brief,
            "copy_files": count,
            "ticket": state,
        })
    return rows


def render_projects(rows: list[dict]) -> str:
    """Projects screen body (session = project dir; exclusive lock noted)."""
    lines = ["projects (select one; session locks that project dir):"]
    if not rows:
        lines.append("  (none — run: python spidercaster.py init <project>)")
        return "\n".join(lines) + "\n"
    for row in rows:
        lines.append(
            "  {name} brief={b} copy={c} ticket={t}".format(
                name=row["name"],
                b="yes" if row["brief"] else "no",
                c=row["copy_files"],
                t=row["ticket"],
            )
        )
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# /plan dry run (step 0 exit): 0-token offline preview, writes nothing
# --------------------------------------------------------------------------


def plan_preview(project_dir: Path) -> dict:
    """Read-only offline plan: block -> slot map. Zero tokens, no writes.

    Gap FAILs surface as ``FAIL gap section.field`` strings, identical to
    the engine. ``hands_used`` is always empty: the preview calls the
    pure planners directly and never invokes an engine hand.
    """
    from lib import ingest, offline

    project_dir = Path(project_dir)
    try:
        copy = ingest.load_project(project_dir)
        raw = offline.plan_offline(copy, {"brief": copy.brief})
    except SystemExit as exc:
        text = str(exc) or "FAIL gap hero.headline"
        return {"ok": False, "text": text + "\n", "hands_used": []}
    pages = raw.get("pages") if isinstance(raw, dict) else None
    lines = [f"plan dry-run: {project_dir} (0 tokens, writes nothing)"]
    if isinstance(pages, list):
        for page in pages:
            if not isinstance(page, dict):
                continue
            lines.append(f"page: {page.get('file', 'index.html')}")
            for section in (page.get("sections") or []):
                if not isinstance(section, dict):
                    continue
                lines.append(
                    "  {sid} [{stype}] <- {src}".format(
                        sid=section.get("id", "?"),
                        stype=section.get("type", "?"),
                        src=section.get("_source", "copy/"),
                    )
                )
    for warning in getattr(copy, "warnings", []) or []:
        lines.append(f"  [warn] {warning}")
    lines.append("tokens: requests=0 ok=0 in=0 out=0 cost_usd=0")
    return {"ok": True, "text": "\n".join(lines) + "\n", "hands_used": []}


# --------------------------------------------------------------------------
# Stdio loop: `spidercaster.py ui [project]`, plain input()/print()
# --------------------------------------------------------------------------

HELP_TEXT = """spidercaster ui — thin face, zero-token default.
verbs (frozen; parse-only, none execute): /help /plan /diff /check
/ticket /publish /compact /account /tools /model /approval
/rollback /interrupt. plain text talks; `!` never shells; no off/yolo.
screens: projects | ticket | ledger | publish. quit ends the session.
views (read-only engine-room faces, at most one hand each): checks copy assets preview probe.
probe states the layout-probe.json -> visual_probe binding (NOT RUN blocks --release).
"""


def _screen_view(show, base, current, site, builder_name, **kw):
    # Show one ui_render body builder inside the composer loop.
    # Returns the engine hands used (at most one). Steps 2-3 seam:
    # the composer owns the verbs; the screens own the views.
    from lib import ui_render as _screens
    view = _screens.UI(emit=lambda text: show(text, end="\n"),
                       input_fn=lambda *args: "q")
    view.project = current or str(base / "projects" / "demo-local")
    guess = base / "sites" / Path(view.project).name
    if not (Path(site) / "index.html").exists() and (guess / "index.html").exists():
        site = guess  # views target the built site, not the project dir
    view.site = str(site)
    return list(getattr(view, builder_name)(**kw))


def _deferred(verb: str) -> str:
    hints = {
        "/diff": "  /diff lands at step 2+; meanwhile it is display-only.\n",
        "/compact": "",
        "/account": (
            "  account lives TokenCenter side-one; this face shows only the\n"
            "  read-only quota header + the ledger above (fail-closed).\n"
        ),
        "/tools": "  /tools lists the frozen verbs; see /help.\n",
        "/model": (
            "  provider chain: gemini free -> openrouter :free -> openwork;\n"
            "  paid joins only with --allow-paid. run: python spidercaster.py models\n"
        ),
    }
    return hints.get(verb, f"  {verb} is parsed; its screen lands after steps 0-1.\n")


def run_ui(
    project: str | None = None,
    *,
    root: Path | None = None,
    input_fn=None,
    print_fn=None,
) -> int:
    """Stdio UI loop. Every action uses at most one engine hand (here: none).

    ``input_fn``/``print_fn`` default to the builtins so ``ui --selftest``
    can drive the loop with stubbed input. Returns an exit code.
    """
    import builtins

    base = Path(root) if root is not None else Path(__file__).resolve().parent
    read = input_fn if input_fn is not None else builtins.input
    show = print_fn if print_fn is not None else builtins.print
    session = Session()
    current = str(project or "").strip()
    hands_used: list[str] = []

    def site_dir() -> Path:
        if current:
            cand = Path(current)
            if cand.is_dir():
                return cand
            guess = base / "sites" / Path(current).name
            if guess.is_dir():
                return guess
        return base / "sites" / "demo-local"

    show("SpiderCaster ui (stdio; offline-first; human publishes). /help for verbs.")
    if current:
        show(f"project: {current}")
    else:
        rows = list_projects(base / "projects", base / "sites")
        show(render_projects(rows), end="")

    while True:
        try:
            line = read("> ")
        except (EOFError, KeyboardInterrupt):
            show("")
            break
        if line is None:
            break
        action = session.accept(str(line))
        kind = action.get("kind")
        if kind in ("empty",):
            continue
        if kind == "refused":
            show(f"refused [{action.get('code')}]: {action.get('detail')}")
            continue
        if kind == "unknown":
            show(f"{action.get('detail')}")
            continue
        if kind == "plain":
            text = str(action.get("text", "")).strip().lower()
            if text in ("quit", "exit", "^q"):
                break
            if text in ("projects", "ls"):
                show(render_projects(
                    list_projects(base / "projects", base / "sites")), end="")
                continue
            if text in ("checks", "copy", "assets", "preview", "probe"):
                builders = {"checks": "board_text", "copy": "gaps_text",
                            "assets": "assets_text", "preview": "preview_text",
                            "probe": "probe_text"}
                used = _screen_view(show, base, current, site_dir(),
                                    builders[text])
                hands_used.extend(used)
                show(render_footer(site_dir()), end="")
                if len(hands_used) > 1:
                    show("refused [HAND_CAP]: one action used more than one hand.\n")
                    return 1
                continue
            if text in ("ticket", "ledger", "publish"):
                action = {"kind": "descriptor", "verb": "/" + text, "args": ""}
            else:
                show("talk noted (propose-only face; try /plan, /ticket, or /help).")
                continue
        verb = str(action.get("verb", ""))
        args = str(action.get("args", "")).strip()
        if verb == "/help":
            show(HELP_TEXT, end="")
        elif verb == "/plan":
            target = args or current or str(base / "projects" / "demo-local")
            preview = plan_preview(Path(target))
            hands_used.extend(preview["hands_used"])
            show(preview["text"], end="")
        elif verb == "/ticket":
            show(render_ticket(site_dir()), end="")
        elif verb == "/publish":
            show(render_publish(site_dir()), end="")
        elif verb == "/approval" and args:
            verdict = session.set_approval(args)
            if verdict["ok"]:
                show(f"approval: {verdict['mode']}\n")
            else:
                show(f"refused [BAD_MODE]: {verdict['detail']}\n")
        elif verb == "/approval":
            show(f"approval: {session.approval} (ladder: manual -> acceptEdits -> plan)\n")
        elif verb == "/rollback":
            miss = session.rollback()
            show(f"{miss['code']}: {miss['detail']}\n")
        elif verb == "/interrupt":
            show("interrupted; in-flight runs land; re-run from the last green gate.\n")
        elif verb == "/compact":
            verdict = session.compact()
            show(f"compacted: {verdict['rows']} descriptor row(s) kept.\n")
        elif verb == "/check":
            release = args.strip() == "--release"
            used = _screen_view(show, base, current, site_dir(),
                                "board_text", release=release)
            hands_used.extend(used)
        elif verb in ("/diff", "/account", "/tools", "/model"):
            if verb == "/tools":
                verbs = " ".join(v for v, _, _ in DESCRIPTORS)
                show(f"verbs: {verbs}\n")
            elif verb == "/account":
                show(render_ledger(site_dir()), end="")
            show(_deferred(verb), end="")
        else:  # pragma: no cover - frozen verbs above cover every parse
            show("unknown verb; /help lists the frozen set.\n")
        show(render_footer(site_dir()), end="")
        if len(hands_used) > 1:
            show("refused [HAND_CAP]: one action used more than one hand.\n")
            return 1
    return 0


# --------------------------------------------------------------------------
# Selftest: composer semantics + ticket/ledger face + stubbed-input walk
# --------------------------------------------------------------------------


def _assert(cond: bool, message: str) -> None:
    if not cond:
        raise SystemExit(f"ui_composer selftest failed: {message}")


def _selftest_composer() -> None:
    for verb, _, _ in DESCRIPTORS:
        action = parse_line(verb)
        _assert(action["kind"] == "descriptor", f"{verb} parses")
        _assert(action["verb"] == verb, f"{verb} verb kept")
    plain = parse_line("build me a tearoom site")
    _assert(plain["kind"] == "plain", "talk is plain")
    bang = parse_line("!rm -rf /")
    _assert(bang["kind"] == "plain", "`!` never shells")
    for bad in ("/off", "/yolo", "off", "yolo", "/approval off", "/approval yolo"):
        refused = parse_line(bad)
        _assert(
            refused["kind"] == "refused" and refused["code"] == "BAD_MODE",
            f"{bad} refused",
        )
    secret = parse_line("here: api_key=ABCD-1234")
    _assert(secret["kind"] == "refused" and secret["code"] == "SECRET", "secret refused")
    _assert(secret["text"] == "", "secret never echoed")
    unknown = parse_line("/deploy")
    _assert(unknown["kind"] == "unknown", "unknown verb named")

    session = Session()
    for index in range(HISTORY_CAP + 10):
        session.accept(f"/ticket {index}")
    _assert(len(session.history) == HISTORY_CAP, "history caps at 50")
    session.accept("api_key=x")
    _assert(len(session.history) == HISTORY_CAP, "refused lines never stored")
    for _ in range(BUFFER_LINES + 1):
        verdict = session.append_line("x" * 10)
    _assert(verdict == {"ok": False, "code": "BUFFER_FULL"}, "buffer caps at 32")
    session.buffer = []
    long_line = session.append_line("y" * (BUFFER_CHARS + 1))
    _assert(long_line == {"ok": False, "code": "LINE_TOO_LONG"}, "line caps at 4000")
    session.buffer = []
    session.append_line("a")
    _assert(session.flush() == ["a"], "flush drains")
    _assert(session.flush() == [], "flush lands once")

    ladder = Session()
    _assert(ladder.approval == "manual", "manual default")
    _assert(ladder.set_approval("acceptEdits")["ok"], "acceptEdits allowed")
    _assert(ladder.set_approval("plan")["ok"], "plan allowed")
    bad_mode = ladder.set_approval("yolo")
    _assert(not bad_mode["ok"] and bad_mode["code"] == "BAD_MODE", "yolo refused")
    _assert(ladder.approval == "plan", "refused mode never applied")

    miss = ladder.rollback()
    _assert(miss["code"] == "ROLLBACK_MISS", "rollback miss named")
    miss2 = ladder.rollback()
    _assert(miss2["code"] == "ROLLBACK_MISS", "rollback miss stable")

    rows = ladder.transcript()
    rebuilt = ladder.rebuild([row["line"] for row in rows])
    _assert(all(a["kind"] != "refused" for a in rebuilt), "rebuild replays clean")
    fresh = Session()
    verdict = fresh.restore(rows)
    _assert(verdict["rows"] == len(rows), "restore keeps rows")
    _assert(fresh.restore([{"nope": 1}]) == {"ok": True, "code": "RESTORED", "rows": 0},
            "restore drops malformed")

    import tempfile

    ladder.accept("/ticket demo")
    ladder.accept("talk line")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "t.json"
        transcript_save(ladder, path)
        loaded = transcript_load(path)
        _assert(loaded["ok"] and loaded["rows"], "transcript roundtrip")
        _assert(transcript_load(Path(tmp) / "missing")["code"] == "BAD_TRANSCRIPT",
                "bad transcript refuses closed")
        (Path(tmp) / "broken.json").write_text("{nope", encoding="utf-8")
        _assert(transcript_load(Path(tmp) / "broken.json")["code"] == "BAD_TRANSCRIPT",
                "broken transcript refuses closed")


def _write_ticket(
    site_dir: Path, *, ok: bool, visual: str, site: str = "demo.example",
    mold: str = "scratch-one",
) -> dict:
    from lib.hands import _sha_bound

    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "index.html").write_text("<html></html>\n", encoding="utf-8")
    (site_dir / "site.json").write_text('{"site": "x"}\n', encoding="utf-8")
    ticket = {
        "site": site,
        "mold": mold,
        "publish": "Keith click. This run does not deploy.",
        "hands": [
            {"role": "visual", "status": visual, "detail": "checker"},
            {"role": "deployer", "status": "PASS", "detail": "ticket"},
        ],
        "ok": ok,
        "sha256": _sha_bound(site_dir),
    }
    (site_dir / "crew-ticket.json").write_text(
        json.dumps(ticket, indent=2) + "\n", encoding="utf-8")
    return ticket


def _selftest_ticket_face(root: Path) -> None:
    site_dir = root / "face-site"
    _write_ticket(site_dir, ok=True, visual="PASS")
    text = render_ticket(site_dir)
    _assert("ok: true" in text, "green ticket shows ok:true")
    _assert("visual: PASS" in text, "green ticket shows visual PASS")
    _assert("sha256:" in text, "green ticket shows hashes")

    ready = verify_for_publish(site_dir)
    _assert(ready["ok"] and ready["code"] == "READY", "green ticket verifies")
    _assert(ready["executed"] is False, "publish never executes")
    _assert("bind --live" in ready["command"], "readiness prints the command")

    (site_dir / "index.html").write_text("<html>changed</html>\n", encoding="utf-8")
    drifted = verify_for_publish(site_dir)
    _assert(not drifted["ok"] and "hash mismatch" in drifted["message"],
            "1-byte flip refused verbatim")
    _assert(drifted["executed"] is False, "refused publish never executes")
    refused_text = render_publish(site_dir)
    _assert("REFUSED" in refused_text and "hash mismatch" in refused_text,
            "readiness view shows the refusal")
    (site_dir / "index.html").write_text("<html></html>\n", encoding="utf-8")

    _write_ticket(site_dir, ok=False, visual="PASS")
    bad_ok = verify_for_publish(site_dir)
    _assert(not bad_ok["ok"] and '"ok" is not true' in bad_ok["message"],
            "ok:false refused verbatim")

    _write_ticket(site_dir, ok=True, visual="FAIL")
    bad_visual = verify_for_publish(site_dir)
    _assert(not bad_visual["ok"] and "visual is not PASS" in bad_visual["message"],
            "visual FAIL refused verbatim")
    fail_text = render_ticket(site_dir)
    _assert("ok: false" in fail_text, "FAIL ticket still renders with ok:false")

    (site_dir / "crew-ticket.json").unlink()
    missing = verify_for_publish(site_dir)
    _assert(not missing["ok"] and "bad ticket" in missing["message"],
            "missing ticket refused verbatim")
    missing_text = render_ticket(site_dir)
    _assert("ok: false" in missing_text and "refusal:" in missing_text,
            "missing ticket still renders")

    ledger_text = render_ledger(site_dir)
    _assert("no ledger yet" in ledger_text, "missing ledger says so honestly")
    (site_dir / "report.json").write_text(json.dumps({
        "generator": "spidercaster/0.1",
        "mode": "offline",
        "provider": None,
        "model": None,
        "tokens": {"requests": 0, "ok": 0, "in_tokens": 0,
                   "out_tokens": 0, "est_cost_usd": 0},
        "attempts": [],
    }), encoding="utf-8")
    ledger_text = render_ledger(site_dir)
    _assert("mode=offline" in ledger_text, "ledger shows mode")
    _assert("requests=0" in ledger_text, "offline shows numeric 0")
    footer = render_footer(site_dir)
    _assert("ticket ok=false" in footer, "footer carries ticket state")

    (site_dir / "report.json").write_text(json.dumps({
        "mode": "ai",
        "tokens": {"requests": 1, "ok": 0},
        "attempts": [{"at": "t", "purpose": "plan", "ok": False}],
    }), encoding="utf-8")
    unknown_text = render_ledger(site_dir)
    _assert("unknown" in unknown_text, "unknown usage stays unknown")
    _assert("cost_known:false" in unknown_text, "unknown cost flagged")


def _selftest_live_collision(root: Path) -> None:
    from lib.library import Library, LibraryError

    pkg = root / "pkg"
    vault = root / "vault"
    lib = Library(pkg, vault)
    lib.save_mold({
        "id": "face-mold", "origin": "scratch",
        "palette": "#1f6f5b", "type_lead": "serif", "nav": "segmented",
    })
    first = root / "live-one"
    _write_ticket(first, ok=True, visual="PASS",
                  site="one.example", mold="face-mold")
    row = lib.bind("one.example", "face-mold", live=True, site_dir=first)
    _assert(row.get("live") is True, "clean bind ok")
    second = root / "live-two"
    _write_ticket(second, ok=True, visual="PASS",
                  site="two.example", mold="face-mold")
    try:
        lib.bind("two.example", "face-mold", live=True, site_dir=second)
        raise SystemExit("ui_composer selftest failed: live reuse was allowed")
    except LibraryError as exc:
        _assert("already live" in str(exc), "second live mold refused verbatim")


def _selftest_ui_walk(base: Path) -> None:
    script = iter([
        "/help",
        "/plan",
        "/ticket",
        "/publish",
        "projects",
        "talk about the build",
        "/off",
        "/bogus",
        "quit",
    ])
    shown: list[str] = []

    def fake_input(prompt: str = "") -> str:
        shown.append(prompt)
        try:
            return next(script)
        except StopIteration:
            raise EOFError

    code = run_ui(None, root=base, input_fn=fake_input,
                  print_fn=lambda *parts, end="\n": shown.append(
                      " ".join(str(p) for p in parts) + end))
    _assert(code == 0, "stubbed walk exits 0")
    blob = "\n".join(shown)
    for needle in ("verbs", "dry-run", "ticket:", "publish readiness",
                   "projects", "talk noted", "BAD_MODE", "unknown verb"):
        _assert(needle in blob, f"walk shows {needle}")
    _assert("ticket ok=" in blob, "every screen carries the footer")


def _selftest_plan_preview(base: Path) -> None:
    demo = base / "projects" / "demo-local"
    if not demo.is_dir():
        return
    preview = plan_preview(demo)
    _assert(preview["hands_used"] == [], "plan preview uses no hands")
    _assert(preview["ok"], f"demo-local plans: {preview['text'][:200]}")
    _assert("0 tokens" in preview["text"], "preview states zero tokens")
    missing = plan_preview(base / "projects" / "no-such-project")
    _assert(not missing["ok"], "missing project FAILs closed")
    _assert(missing["hands_used"] == [], "failed preview uses no hands")


def main() -> int:
    """Composer + ticket/ledger face battery. Exit 0 required."""
    import tempfile

    _selftest_composer()
    with tempfile.TemporaryDirectory() as tmp:
        _selftest_ticket_face(Path(tmp) / "t1")
        _selftest_live_collision(Path(tmp) / "t2")
    base = Path(__file__).resolve().parent.parent
    _selftest_plan_preview(base)
    _selftest_ui_walk(base)
    print("ui_composer selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
