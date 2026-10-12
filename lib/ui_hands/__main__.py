"""Run the ui_hands package selftest: python -m lib.ui_hands."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.ui_hands import main  # noqa: E402

raise SystemExit(main())
