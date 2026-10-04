STARTED 2026-10-01 14:49:12 -05:00

`lib/code_refuse.py` only. Match `code_refuse` in HOW_WIX_SHOPIFY_TOOLS.md. No website. No publish. Do not edit `lib/hands`. Writes nothing.

`code_refuse(kind)` returns `ok`, `kind`, `refused`, `reason`, `error`. Empty kind fails. `liquid`, `velo`, `javascript`, `css`, `custom_element`, and any kind containing `http://` or `https://` are `refused` true and `ok` false. A `lib.ir.SECTION_TYPES` kind is `refused` true and `ok` true; the reason says the type stays in the catalog and no code file is emitted. Any other kind is `ok` false, `error` `unknown_kind`, `refused` true.

From `V:\a\Ai\spidercaster\working`:

`py -3.14 -m lib.code_refuse` exit 0: `code_refuse selftest ok`

DONE 2026-10-01 14:50:28 -05:00
