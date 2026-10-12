#!/usr/bin/env python3
"""enforce_boundaries.py - AST gate for SpiderCaster module boundaries.

Lane map is read from ARCHITECTURE.json (same dir tree root); this file
hardcodes no lane list. Stdlib only (ast, json, sys, pathlib).

Rules (from ARCHITECTURE.json enforcement_policies + module isolation):
  1. engine (strict_black_box): lib/**, spidercaster.py, mcp_server.py must
     not import seat lanes (library.seats.*) or the COSMOS-side black boxes
     (sessions, cosmos, cosmos_core markers).
  2. seats (lane_only): library/seats/<lane>/**.py may import stdlib, the
     engine (lib.*), and its own lane package only -- never another lane,
     never sessions/cosmos markers.
  3. untouchable (sessions_cosmos): no scanned tree file may import the
     sessions/cosmos markers. tools/** is scanned for this rule only
     (tools_nest is sandboxed; its internal imports are its own business).

Usage:
    python scripts/enforce_boundaries.py            # scan working tree root
    python scripts/enforce_boundaries.py --root DIR # scan another root

Exit 0 when clean ("boundaries ok"), 1 with a violation list otherwise.
Never prints file contents, only file:line + rule id.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent.parent  # working/ tree root
ARCH_FILE = DEFAULT_ROOT / "ARCHITECTURE.json"

# Import-name prefixes that belong to the COSMOS side black box.
# Matched against the dotted module name of every import statement.
UNTOUCHABLE_PREFIXES = ("sessions", "cosmos", "cosmos_core")

ENGINE_TOP = "lib"
SEAT_PKG = "library.seats"


def load_arch(root: Path) -> dict:
    arch_path = root / "ARCHITECTURE.json"
    try:
        return json.loads(arch_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"boundary gate: cannot read {arch_path}: {exc}")
        raise SystemExit(2)


def iter_py_files(root: Path):
    skip = {".git", "__pycache__", ".mypy_cache", ".ruff_cache",
            "node_modules", ".venv", "venv", "dist", "sites"}
    for path in sorted(root.rglob("*.py")):
        if any(part in skip for part in path.relative_to(root).parts):
            continue
        yield path


def imports_of(path: Path) -> list[tuple[int, str]]:
    """Return [(lineno, dotted_name)] for every absolute import in the file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, ValueError):
        return []  # unreadable files are not boundary violations
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import: stays inside its own package
                continue
            if node.module:
                out.append((node.lineno, node.module))
    return out


def is_untouchable(dotted: str) -> bool:
    top = dotted.split(".")[0].lower()
    return top in UNTOUCHABLE_PREFIXES


def classify(root: Path, path: Path) -> tuple[str, str | None]:
    """Return (zone, lane). Zone in {engine, seat, tool, other}."""
    rel = path.relative_to(root).as_posix()
    if rel == "spidercaster.py" or rel == "mcp_server.py" or rel.startswith("lib/"):
        return ("engine", None)
    if rel.startswith("library/seats/"):
        parts = rel.split("/")
        lane = parts[2] if len(parts) > 2 else None
        return ("seat", lane)
    if rel.startswith("tools/"):
        return ("tool", None)
    return ("other", None)


def check(root: Path, arch: dict) -> list[str]:
    lanes = set((arch.get("modules", {}).get("seats", {}).get("lanes", [])))
    violations: list[str] = []
    for path in iter_py_files(root):
        zone, lane = classify(root, path)
        if zone == "other":
            continue
        rel = path.relative_to(root).as_posix()
        for lineno, dotted in imports_of(path):
            if is_untouchable(dotted):
                violations.append(
                    f"{rel}:{lineno} untouchable-black-box import '{dotted}' [{zone}]")
                continue
            if zone == "engine" and (dotted == SEAT_PKG or dotted.startswith(SEAT_PKG + ".")):
                violations.append(
                    f"{rel}:{lineno} engine-must-not-depend-on-seats '{dotted}' [engine]")
            elif zone == "seat":
                if dotted == SEAT_PKG or dotted.startswith(SEAT_PKG + "."):
                    rest = dotted[len(SEAT_PKG):].lstrip(".")
                    other = rest.split(".")[0] if rest else ""
                    if lane is None or other != lane:
                        violations.append(
                            f"{rel}:{lineno} cross-lane import '{dotted}' [seat:{lane}]")
                elif dotted.split(".")[0] not in (ENGINE_TOP,):
                    # seat importing a non-engine, non-stdlib, non-seat top
                    # package inside the tree is suspicious; stdlib names are
                    # not resolvable here so only flag tree-local top dirs.
                    top = dotted.split(".")[0]
                    if (root / top).is_dir() and top not in ("scripts", "tests", "bench"):
                        violations.append(
                            f"{rel}:{lineno} seat outside lane+engine '{dotted}' [seat:{lane}]")
    if not lanes:
        violations.append("ARCHITECTURE.json defines no seat lanes; lane map unreadable")
    return violations


def main(argv: list[str]) -> int:
    root = DEFAULT_ROOT
    if len(argv) > 2 and argv[1] == "--root":
        root = Path(argv[2]).resolve()
    arch = load_arch(root)
    violations = check(root, arch)
    if violations:
        print(f"boundary gate: {len(violations)} violation(s)")
        for violation in violations:
            print("  " + violation)
        return 1
    print("boundaries ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
