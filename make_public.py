#!/usr/bin/env python3
"""Build a sanitized PUBLIC variant of siteforge for publishing.

Copies the tree to a staging dir with redactions applied:
  - excludes WALLETS.md (private wallet ledger)
  - genericizes internal paths (V:\\Research4\\.secrets and recorded key
    filenames) to neutral placeholders
  - verifies the result: zero hits for internal emails, wallet names, key
    fingerprints/last4s, and key-material patterns

Staging only - nothing is committed or pushed by this script. Publish flow:
review the staging dir, init/push it to a PUBLIC repo as its own commit.

Usage: python make_public.py [--out ../cosmos-sc-public]
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE = {"WALLETS.md", "make_public.py"}

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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT.parent / "cosmos-sc-public"))
    args = ap.parse_args()
    out = Path(args.out)

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    copied = skipped = 0
    for src in ROOT.rglob("*"):
        rel = src.relative_to(ROOT)
        if ".git" in rel.parts:  # never copy VCS metadata into a public variant
            continue
        if any(part in EXCLUDE for part in rel.parts):
            skipped += 1
            continue
        if "__pycache__" in rel.parts or src.suffix == ".pyc":
            continue
        dst = out / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}:
            shutil.copy2(src, dst)
            copied += 1
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        for rx, repl in REDACTIONS:
            text = rx.sub(repl, text)
        dst.write_text(text, encoding="utf-8", newline="\n")
        copied += 1

    # verification pass: no forbidden pattern may survive
    hits = []
    for f in out.rglob("*"):
        if not f.is_file() or f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for rx in FORBIDDEN:
            m = rx.search(text)
            if m:
                hits.append(f"{f.relative_to(out)}: {rx.pattern[:40]} -> {m.group(0)[:30]}")

    print(f"staged: {out}")
    print(f"files copied: {copied} | excluded: {skipped}")
    if hits:
        print("LEAK CHECK FAILED:")
        for h in hits:
            print("  " + h)
        return 1
    print("leak check: CLEAN (no internal emails, wallet names, project numbers, or key material)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
