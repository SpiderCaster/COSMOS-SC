DONE 2026-10-01

`lib/shipcheck.py` `run()` and one `spidercaster.py shipcheck` subcommand beside `doctor`. Not published. No `--live` bind. Did not edit `lib/check.py`, `lib/render.py`, `lib/offline.py`, or `make_public.py`. Did not create `lib/regress.py`.

From `<repo-root>`, one run:

`py -3.14 spidercaster.py shipcheck` exit 2:

```
lib.regress
```

`shipcheck ok` was not printed. `lib.regress` is still absent after the one 90 second wait, so that step is a failed `missing` and the gate is not ship-ready. No step was weakened.
