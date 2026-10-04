# layer-read

STARTED 2026-10-01 14:49:51 -05:00

`lib/layer_read.py` `layer_read(out, root, write=None)`. Read only. Not a site build. No publish. No hands edit.

Match `HOW_WIX_SHOPIFY_TOOLS.md` layer_read. The function lives in this module, not `lib/hands`.

DONE 2026-10-01 14:51:25 -05:00

`layer_read` returns `ok`, `error`, `layers`, `page`. `layers` is `{index, id, type}` from the first page in `out/site.json`, in file order. `page` is that page's slug, or empty. It fails when `site.json` is missing or not JSON, a section type is outside `lib.ir.SECTION_TYPES`, `out` escapes `root` or contains `..`, or `write` is not None. It does not reorder and it does not write.

From `V:\a\Ai\spidercaster\working`:

- `py -3.14 -m lib.layer_read` exit 0: `layer_read selftest ok`
