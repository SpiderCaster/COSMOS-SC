STARTED 2026-10-01

Read-only mold panel. Not a site build. No mold write. No ledger write. No download. No publish.

DONE 2026-10-01

`lib/mold_panel.py` `mold_panel(root, mold_id, live=None)` reads `library/molds/<id>.json` under the given root only. It does not write a mold, a ledger, or the vault, and it does not download a parent. `live` other than None fails. Missing file, origin outside scratch|mutate|mix, a palette that is not `#` plus six hex digits, or any string containing `htt<local-path>` or `https://` fails. `parents` is a list, empty when absent.

From `<repo-root>`:

- `py -3.14 -m lib.mold_panel` exit 0: `mold_panel selftest ok`
