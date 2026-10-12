STARTED

Regression selftest for the offline plan and assemble path. Fixture is a tiny temp project (no network). Asserts live in lib/regress.py. Do not publish. Do not edit stage/ or projects/. Do not edit lib/render.py or lib/check.py.

DONE

lib/regress.py builds a temp project and calls hands plan_offline, then render.assemble. The engine already met the asserts, so offline.py, ingest.py, and ir.py were not edited. Did not publish. Did not edit stage/, projects/, lib/render.py, or lib/check.py.

py -3.14 -m lib.regress
regress selftest ok
