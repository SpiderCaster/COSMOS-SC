#!/usr/bin/env python3
"""Build a sanitized PUBLIC variant of SpiderCaster for publishing.

Copies the tree into a temp directory with redactions applied:
  - excludes WALLETS.md (private wallet ledger), credentials, .env, and key files
  - excludes stage, preview, _delme, image-tests, __pycache__, and .git
  - genericizes internal paths (V:\\Research4\\.secrets and recorded key
    filenames) to neutral placeholders
  - verifies the temp tree: zero hits for internal emails, wallet names, key
    fingerprints/last4s, and key-material patterns

The public snapshot is replaced only when that check is clean. A failed check
leaves the existing public tree untouched and exits 2. Never deletes the
working tree.

Staging only - nothing is committed or pushed by this script. Publish flow:
review the staging dir, init/push it to a PUBLIC repo as its own commit.

Usage: python make_public.py [--out ../cosmos-sc-public]
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE = {
    "WALLETS.md",
    "make_public.py",
    "vendor-vault",
    "image-tests",
    "stage",
    "preview",
    "_delme",
    "__pycache__",
    ".git",
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}
KEY_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".keystore", ".jks"}
_KEY_NAME = re.compile(
    r"(?i)(^|[._-])(api[_-]?key|secret[_-]?key|private[_-]?key|id_rsa|id_dsa|id_ecdsa|id_ed25519)([._-]|$)"
)
_KEY_FILE = re.compile(r"(?i)(^|[._-])key\.(txt|json|pem|bin|env)$")

REDACTIONS = [
    (re.compile(r"V:[/\\]Research4[/\\]\.secrets", re.I), "<your-key-file-dir>"),
    (re.compile(r"vertex_medicineman_key\.txt", re.I), "gemini_key.txt"),
    (re.compile(r"vertex_fruitaholics_key\.txt", re.I), "gemini_key2.txt"),
    (re.compile(r"vertex_patriotfuelstop_key\.txt", re.I), "gemini_key3.txt"),
    (re.compile(r"vertex_coding_key\.txt", re.I), "gemini_key4.txt"),
    (re.compile(r"vertex_key\.txt", re.I), "gemini_key5.txt"),
    (re.compile(r"recorded fleet keys live in `[^`]*`\(e\.g\.[^)]*\)\.", re.I),
     "point FORGE_GEMINI_KEY_FILE at any Gemini/Vertex API key file."),
    (re.compile(r"`V:[/\\]Research4[^`]*`", re.I), "a local key-file directory"),
    # Path rules above miss a bare drive name. The forbid list still rejects it.
    (re.compile(r"Research4", re.I), "local-secrets"),
]

# nothing in this list may survive into the staging tree
FORBIDDEN = [
    re.compile(r"Research4", re.I),
    re.compile(r"medicineman|fruitaholic|patriotfuelstop", re.I),
    re.compile(r"[A-Za-z0-9._%+-]+@gmail\.com"),
    re.compile(r"orders\.ggn|joanna\.bbf|ranny\.bbf|keith\.bbf", re.I),
    re.compile(r"\b(?:last4|fp)=?\s*[:=]?\s*[\"']?[A-Za-z0-9_]{4}\b.{0,3}(?:fp|last4)", re.I),
    re.compile(r"\bAQ\.|AIza[0-9A-Za-z_-]{10,}|ghp_[A-Za-z0-9]{10,}|gho_[A-Za-z0-9]{10,}|sk-[A-Za-z0-9]{10,}"),
    re.compile(r"456875530590|953760228233|571047330544|252939746739|475026348209"),
]


def _resolved(path: Path) -> Path:
    return path.resolve()


def _unsafe_to_destroy(path: Path) -> bool:
    """True when deleting path would delete the working tree."""
    path = _resolved(path)
    root = _resolved(ROOT)
    return path == root or root in path.parents or path in root.parents


def _blocked_name(name: str) -> bool:
    lower = name.lower()
    if lower == ".env" or lower.startswith(".env.") or lower.endswith(".env"):
        return True
    if "credential" in lower:
        return True
    if Path(lower).suffix in KEY_SUFFIXES:
        return True
    if _KEY_NAME.search(lower) or _KEY_FILE.search(lower):
        return True
    return False


def _copy_tree(dest: Path) -> tuple[int, int]:
    copied = skipped = 0
    for src in ROOT.rglob("*"):
        rel = src.relative_to(ROOT)
        if any(part in EXCLUDE or _blocked_name(part) for part in rel.parts):
            skipped += 1
            continue
        if src.suffix == ".pyc":
            skipped += 1
            continue
        dst = dest / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in IMAGE_SUFFIXES:
            shutil.copy2(src, dst)
            copied += 1
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        for rx, repl in REDACTIONS:
            text = rx.sub(repl, text)
        dst.write_text(text, encoding="utf-8", newline="\n")
        copied += 1
    return copied, skipped


def _leak_hits(tree: Path) -> list[str]:
    hits = []
    for f in tree.rglob("*"):
        if not f.is_file() or f.suffix.lower() in IMAGE_SUFFIXES:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for rx in FORBIDDEN:
            m = rx.search(text)
            if m:
                hits.append(f"{f.relative_to(tree)}: {rx.pattern[:40]} -> {m.group(0)[:30]}")
    return hits


def _replace_public(stage: Path, out: Path) -> None:
    if _unsafe_to_destroy(out) or _unsafe_to_destroy(stage):
        raise RuntimeError("refusing to replace the working tree")
    out.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if out.exists():
        backup = out.with_name(f".{out.name}.prev-{os.getpid()}")
        if _unsafe_to_destroy(backup):
            raise RuntimeError("refusing to replace the working tree")
        if backup.exists():
            shutil.rmtree(backup)
        out.rename(backup)
    try:
        stage.rename(out)
    except Exception:
        if backup is not None and backup.exists() and not out.exists():
            backup.rename(out)
        raise
    if backup is not None and backup.exists():
        if _unsafe_to_destroy(backup):
            raise RuntimeError("refusing to delete the working tree")
        shutil.rmtree(backup)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT.parent / "cosmos-sc-public"))
    args = ap.parse_args()
    out = Path(args.out)
    if _unsafe_to_destroy(out):
        print("refusing to replace the working tree")
        return 2

    stage_parent = out.parent
    if _resolved(stage_parent) == _resolved(ROOT) or _resolved(ROOT) in _resolved(stage_parent).parents:
        stage_parent = Path(tempfile.gettempdir())
    stage = Path(tempfile.mkdtemp(prefix=".cosmos-sc-stage-", dir=str(stage_parent)))
    try:
        if _unsafe_to_destroy(stage):
            print("refusing to stage inside the working tree")
            return 2
        copied, skipped = _copy_tree(stage)
        hits = _leak_hits(stage)
        print(f"files copied: {copied} | excluded: {skipped}")
        if hits:
            print("LEAK CHECK FAILED:")
            for h in hits:
                print("  " + h)
            return 2
        _replace_public(stage, out)
    finally:
        if stage.exists() and not _unsafe_to_destroy(stage):
            shutil.rmtree(stage)

    print(f"staged: {out}")
    print("leak check: CLEAN (no internal emails, wallet names, project numbers, or key material)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
