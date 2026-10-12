"""Dirty-op attempt snapshots, logged rollback, and zero-token dry-run diffs.

FINAL arch D2 (3-0): GF38 dirty-ops-only snapshots with G47 guardrails.

- Snapshots live in ``sites/<name>/_attempts/<id>/`` and hold a site.json
  snapshot, the rendered tree (top-level ``*.html`` + ``assets/`` when
  present), the ticket/ledger when present, and a parent pointer.
- Snapshots are written before dirty ops only (AI plan, refine, mold/frame
  rebind, crew runs). The clean offline build stays direct and never
  snapshots; anything that snapshots with a clean-build reason is refused.
- ``_attempts/`` is provenance, not product: it is excluded from release
  hashes (see ``lib.hands._sha_bound`` + :func:`is_attempts_path`).
- Retention cap: keep the last 10 attempts; the oldest are pruned on write.
  The cap is a constant in this module; changing it needs a BOARD motion.
- ``refine --rollback <id>`` is explicit and logged to
  ``_attempts/rollback.log``. Battery: snapshot, mutate, rollback is
  byte-equal on every tracked file.
- ``build --dry-run`` prints a sitemap/IR diff at 0 tokens and writes
  nothing. :func:`dry_run_diff` is a pure function: no providers, no disk.

Stdlib only. Zero tokens. Windows reference paths handled via pathlib.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import secrets
from datetime import UTC, datetime
from pathlib import Path

ATTEMPTS_DIRNAME = "_attempts"
ROLLBACK_LOGNAME = "rollback.log"
MANIFEST_NAME = "manifest.json"
PARENT_NAME = "parent.txt"

#: Retention cap: keep the last N attempts per site. BOARD-motion to change.
RETENTION_CAP = 10

#: Reasons allowed to snapshot. The clean offline build is deliberately
#: absent: it stays direct and snapshot-free.
DIRTY_OPS = ("ai-plan", "refine", "rebind", "crew", "compose", "hand-run")

#: Snapshot payload: the canonical IR, the rendered tree, the ticket/ledger.
TRACKED_TOP = ("site.json", "crew-ticket.json", "report.json", "favicon.svg")


def attempts_dir(site_dir: Path) -> Path:
    """The ``_attempts/`` dir for a built site (created on write)."""
    return Path(site_dir) / ATTEMPTS_DIRNAME


def is_attempts_path(rel: str) -> bool:
    """True when a release-relative path lives under ``_attempts/``."""
    flat = str(rel or "").replace("\\", "/").strip("/")
    return flat == ATTEMPTS_DIRNAME or flat.startswith(ATTEMPTS_DIRNAME + "/")


def is_dirty_op(reason: str) -> bool:
    """True when ``reason`` is a dirty op allowed to snapshot."""
    return str(reason or "").strip().lower() in DIRTY_OPS


def new_id(now: datetime | None = None) -> str:
    """A sortable unique attempt id: ``aYYYYMMDDTHHMMSSffffffZ_<8hex>``.

    Microseconds keep same-second snapshots in creation order so retention
    pruning drops the true oldest; the random tail guards coarse clocks.
    """
    stamp = (now or datetime.now(UTC)).strftime("%Y%m%dT%H%M%S%fZ")
    return f"a{stamp}_{secrets.token_hex(4)}"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(site: dict) -> str:
    return json.dumps(site, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def list_attempts(site_dir: Path) -> list[dict]:
    """Manifests for every attempt, oldest first. Empty when none."""
    base = attempts_dir(site_dir)
    if not base.is_dir():
        return []
    found: list[dict] = []
    for child in sorted(base.iterdir()):
        man = child / MANIFEST_NAME
        if not child.is_dir() or child.name.startswith(".") or not man.is_file():
            continue
        try:
            data = json.loads(man.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("id") == child.name:
            found.append(data)
    return found


def prune(site_dir: Path, cap: int = RETENTION_CAP) -> list[str]:
    """Drop the oldest attempts past ``cap``. Returns removed ids."""
    import shutil

    kept = list_attempts(site_dir)
    if len(kept) <= cap:
        return []
    removed: list[str] = []
    for entry in kept[: len(kept) - cap]:
        target = attempts_dir(site_dir) / str(entry["id"])
        shutil.rmtree(target, ignore_errors=True)
        removed.append(str(entry["id"]))
    return removed


def snapshot(site_dir: Path, *, reason: str, parent: str | None = None) -> dict:
    """Snapshot the current site tree before a dirty op.

    Refuses clean-build reasons (ValueError). Copies the canonical IR, the
    rendered ``*.html`` tree, ``assets/`` when present, and the
    ticket/ledger when present, then prunes past :data:`RETENTION_CAP`.
    Returns the manifest dict.
    """
    clean = str(reason or "").strip().lower()
    if not is_dirty_op(clean):
        raise ValueError(
            f"refusing snapshot for {reason!r}: snapshots are dirty-ops only "
            f"({', '.join(DIRTY_OPS)}); the clean offline build stays direct"
        )
    site_dir = Path(site_dir)
    site_json = site_dir / "site.json"
    if not site_json.is_file():
        raise ValueError(f"no site.json in {site_dir}; run a build first")
    prior = list_attempts(site_dir)
    attempt_id = new_id()
    dest = attempts_dir(site_dir) / attempt_id
    dest.mkdir(parents=True, exist_ok=False)
    files: dict[str, str] = {}
    for name in TRACKED_TOP:
        src = site_dir / name
        if src.is_file():
            (dest / name).write_bytes(src.read_bytes())
            files[name] = _sha_file(dest / name)
    for page in sorted(site_dir.glob("*.html")):
        (dest / page.name).write_bytes(page.read_bytes())
        files[page.name] = _sha_file(dest / page.name)
    assets = site_dir / "assets"
    if assets.is_dir():
        for path in sorted(assets.rglob("*")):
            if not path.is_file():
                continue
            rel = str(path.relative_to(site_dir)).replace("\\", "/")
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
            files[rel] = _sha_file(target)
    if parent is None and prior:
        parent = str(prior[-1].get("id") or "")
    manifest = {
        "id": attempt_id,
        "reason": clean,
        "parent": parent or "",
        "files": files,
        "created": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    (dest / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (dest / PARENT_NAME).write_text((parent or "") + "\n", encoding="utf-8")
    pruned = prune(site_dir)
    manifest["pruned"] = pruned
    return manifest


def rollback(site_dir: Path, attempt_id: str) -> dict:
    """Restore every tracked file from an attempt. Explicit and logged.

    Removes top-level ``*.html`` files the snapshot does not know (a page
    deleted after the snapshot stays deleted on the way back), restores the
    rest byte for byte, and appends one line to ``_attempts/rollback.log``.
    Returns the manifest of the attempt rolled back to.
    """
    site_dir = Path(site_dir)
    attempt_id = str(attempt_id or "").strip()
    if not attempt_id or "/" in attempt_id or "\\" in attempt_id:
        raise ValueError(f"bad attempt id: {attempt_id!r}")
    src = attempts_dir(site_dir) / attempt_id
    man_path = src / MANIFEST_NAME
    if not man_path.is_file():
        known = [entry.get("id") for entry in list_attempts(site_dir)]
        raise ValueError(f"unknown attempt {attempt_id!r}; known: {known}")
    manifest = json.loads(man_path.read_text(encoding="utf-8"))
    wanted: dict[str, str] = manifest.get("files") or {}
    for rel in sorted(wanted):
        blob = (src / rel).read_bytes()
        target = site_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    for page in sorted(site_dir.glob("*.html")):
        if page.name not in wanted:
            page.unlink()
    restored = sorted(wanted)
    line = (
        f"{datetime.now(UTC).isoformat(timespec='seconds')} "
        f"rollback {attempt_id} restored={len(restored)}\n"
    )
    log = attempts_dir(site_dir) / ROLLBACK_LOGNAME
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(line)
    manifest["restored"] = restored
    return manifest


def _ir_lines(site: dict) -> list[str]:
    """Stable value-aware lines per page/section/field for zero-token diffs."""
    lines: list[str] = []
    if not isinstance(site, dict):
        return ["<no site>"]
    meta = site.get("meta") if isinstance(site.get("meta"), dict) else {}
    lines.append("meta title=" + json.dumps(meta.get("title"), ensure_ascii=False))
    theme = site.get("theme") if isinstance(site.get("theme"), dict) else {}
    lines.append(
        "theme "
        + json.dumps(
            {key: theme.get(key) for key in ("template", "dark", "accent")},
            sort_keys=True,
            ensure_ascii=False,
        )
    )
    pages = site.get("pages") if isinstance(site.get("pages"), list) else []
    for page in pages:
        if not isinstance(page, dict):
            continue
        lines.append(
            "page slug=" + json.dumps(page.get("slug"), ensure_ascii=False)
            + " title=" + json.dumps(page.get("title"), ensure_ascii=False)
        )
        for sec in page.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            lines.append("  " + str(sec.get("id")) + ":" + str(sec.get("type")))
            data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
            for key in sorted(data):
                try:
                    rendered = json.dumps(data[key], sort_keys=True, ensure_ascii=False)
                except (TypeError, ValueError):
                    rendered = repr(data[key])
                lines.append("    " + str(key) + "=" + rendered)
    return lines


def dry_run_diff(
    old: dict | None, new: dict, *, label: str = "site", context: int = 3
) -> str:
    """Zero-token unified diff between two IR trees. Pure: no I/O, no calls.

    ``old=None`` means a fresh build (every line added). The sitemap stage
    diff lands with ``lib/sitemap.py``; until then this covers the IR layer
    the sitemap will be derived from.
    """
    before = [] if old is None else _ir_lines(old)
    after = _ir_lines(new)
    if before == after:
        return f"dry-run {label}: no changes (0 tokens spent)\n"
    lines = difflib.unified_diff(
        before, after, fromfile=label + " (current)", tofile=label + " (planned)",
        n=context, lineterm="",
    )
    body = "\n".join(lines)
    return f"dry-run {label}: 0 tokens spent\n{body}\n"


def attempt_snapshot(ctx: dict) -> dict:
    """Frontend-seat hand: snapshot ``ctx['out']`` before a dirty op.

    Hands-compatible ``{status, detail, data}`` triple. PASS with the new
    attempt id, or FAIL (never a crash) when there is nothing to snapshot.
    """
    out = ctx.get("out") if isinstance(ctx, dict) else None
    reason = str((ctx or {}).get("reason") or "hand-run").strip() or "hand-run"
    if not out:
        return {"status": "FAIL", "detail": "out is required", "data": {}}
    try:
        manifest = snapshot(Path(out), reason=reason)
    except ValueError as exc:
        return {"status": "FAIL", "detail": str(exc), "data": {}}
    except OSError as exc:
        return {"status": "FAIL", "detail": f"snapshot failed: {exc}", "data": {}}
    detail = f"attempt {manifest['id']} ({manifest['reason']}, {len(manifest['files'])} files)"
    if manifest.get("pruned"):
        detail += f"; pruned {len(manifest['pruned'])}"
    return {"status": "PASS", "detail": detail, "data": {"attempt": manifest}}
