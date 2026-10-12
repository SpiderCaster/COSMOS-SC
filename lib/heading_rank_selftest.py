"""Prove heading skips ignore catalog parts. Run: python lib/heading_rank_selftest.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.heading_rank import heading_skips


def main() -> int:
    good = "<h1>A</h1><h2>B</h2><h3>C</h3>"
    if heading_skips(good):
        raise SystemExit("clean outline failed")
    bad = "<h1>A</h1><h3>C</h3>"
    if heading_skips(bad) != ["h1 to h3"]:
        raise SystemExit("skip missed")
    part = '<h1>A</h1><div data-sc-part="x"><h3>Part</h3></div><h2>B</h2>'
    if heading_skips(part):
        raise SystemExit("part heading counted")
    print("heading_rank selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
