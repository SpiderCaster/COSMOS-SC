#!/bin/sh
# SpiderCaster cold-start launcher (Unix) — make executable once, then run it.
#   chmod +x start-spidercaster.sh && ./start-spidercaster.sh
# Gates on doctor, builds the offline demo (0 tokens), opens the studio desk.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export SPIDERCASTER_HOME="$HERE"
if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi
exec "$PY" "$HERE/spidercaster.py" start "$@"
