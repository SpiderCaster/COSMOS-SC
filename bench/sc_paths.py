#!/usr/bin/env python3
r"""Path resolver for SpiderCaster bench tools (stdlib only, read-only).

No bench file should hard-code a machine path. Each resource is resolved in this order:
  1. explicit CLI value (passed in by the caller)
  2. environment variable (existing engine names first, then the proposed bench name)
  3. config value from bench/bench_paths.json (optional; keys = resource names below)
  4. repo-relative fallback (inside the checkout)
  5. legacy machine default (the old hard-coded KC-PC path), used ONLY if it exists,
     and always reported as source "legacy-default" so runs stay honest.
If nothing exists, resolve() returns (None, reason) and the caller must report SKIP.

Resources:
  parts       env SPIDERCASTER_PARTS (read by lib/parts_lib.py), SPIDERCASTER_PARTS_DIR (proposed)
  kit         env SPIDERCASTER_KIT (read by lib/parts_lib.py)
  components  env SPIDERCASTER_COMPONENTS_DIR (proposed; no engine reader yet)
  catalog     env SPIDERCASTER_CATALOG (proposed; lib/tools_index.py has no env hook yet)
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = HERE / "bench_paths.json"
EXIT_SKIP = 3  # bench convention: resource truly absent -> SKIP (not pass, not crash)
_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")

SPECS = {
    "parts": {
        "env": ("SPIDERCASTER_PARTS", "SPIDERCASTER_PARTS_DIR"),
        "repo": ("tools/parts", "library/parts"),
        "legacy": r"V:\streams\webdev\tools\parts",
    },
    "kit": {
        "env": ("SPIDERCASTER_KIT",),
        "repo": ("tools/kit", "library/kit"),
        "legacy": r"V:\streams\webdev\kits\SPIDERCASTER_KIT\sc-tools",
    },
    "components": {
        "env": ("SPIDERCASTER_COMPONENTS_DIR",),
        "repo": ("library/components", "templates/components"),
        "legacy": r"V:\streams\webdev\templates\components",
    },
    "catalog": {
        "env": ("SPIDERCASTER_CATALOG",),
        "repo": ("library/components/catalog.jsonl", "templates/components/catalog.jsonl"),
        "legacy": r"V:\streams\webdev\templates\components\catalog.jsonl",
    },
}


def _config() -> dict:
    if not CONFIG.is_file():
        return {}
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def resolve(name: str, cli: str | None = None, root: Path | None = None,
            allow_legacy: bool = True) -> tuple[Path | None, str]:
    """Return (path, source) when found, else (None, reason). Never raises for a missing path."""
    spec = SPECS[name]
    root = Path(root) if root else ROOT
    tried = []
    if cli:
        p = Path(cli)
        if p.exists():
            return p, f"cli:{p}"
        return None, f"--{name}-dir given but absent: {p}"
    for var in spec["env"]:
        val = os.environ.get(var)
        if val:
            p = Path(val)
            if p.exists():
                return p, f"env {var}"
            tried.append(f"env {var} (absent)")
    val = _config().get(name)
    if val:
        p = Path(val)
        if not p.is_absolute():
            p = root / p
        if p.exists():
            return p, f"config {CONFIG.name}:{name}"
        tried.append(f"config {name} (absent)")
    for rel in spec["repo"]:
        p = root / rel
        if p.exists():
            return p, f"repo-relative {rel}"
        tried.append(f"repo {rel}")
    if allow_legacy and spec.get("legacy"):
        p = Path(spec["legacy"])
        try:
            if (os.name == "nt" or not _DRIVE.match(spec["legacy"])) and p.exists():
                return p, f"legacy-default {p}"
        except OSError:
            pass
        tried.append("legacy default (absent on this host)")
    return None, f"{name} not found; tried: " + ", ".join(tried)


if __name__ == "__main__":
    for key in SPECS:
        path, src = resolve(key)
        print(f"{key:<11} {'FOUND ' + str(path) if path else 'MISSING'}  [{src}]")
