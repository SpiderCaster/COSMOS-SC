# SpiderCaster loop contract

Same spec for every builder. Stdlib only. No network. No publish. No git. No ledger write. No `library bind`. Do not edit `keys`, the vendor vault, `catalog.jsonl`, or any folder under `V:\streams\webdev\tools\parts`. Do not invent copy. Visible prose added by this loop must be an exact substring of the project's `copy/` files. Allowed chrome words already in the part files stay. Do not add the phrases `Read on` or `Built with SpiderCaster`. Do not add an h2 whose text is exactly `About` unless that word is in the copy.

Engine root: `V:\A\Ai\spidercaster\working`. Run commands from that directory.

A row is built when `lib.tools_index.index_rows` says `status == built`. Catalog kinds and routes come from `lib.tools_index.load_catalog`. Section types are `lib.ir.SECTION_TYPES`.

## Pick (`lib/part_pick.py`)

```python
def pick_part(section_type: str, used: set[str] | None = None, override: str = "") -> dict:
def pick_chrome(slot: str, used: set[str] | None = None, override: str = "") -> dict:
```

Return `{"ok": bool, "catalog_id": str, "part_dir": str, "kind": str, "route": str, "error": str}`.

Section kinds, in order, route must be `tools-hooks-blocks`:

- hero: hero
- features, stats, steps, gallery, testimonials, about, team, logocloud: card
- pricing: comparison, then table
- faq: faq
- cta, contact: cta
- menu: table

Chrome, route must be `tools-headers`:

- header: header, then sticky-header
- footer: footer

Skip ids in `used`. Among matches, pick the lexicographically smallest `catalog_id`. `override` may be any built id and wins. Unknown type or no match: `ok` false and empty ids. Do not pick popups or sidebars. Do not pick `schema-jsonld`.

## Fill (`lib/part_fill.py`)

```python
def fill_fragment(fragment: str, slots: dict[str, str], copy_text: str) -> str:
def copy_block(section: dict, copy_text: str) -> str:
```

`fill_fragment` replaces the text of an element that has `data-sc-slot="key"` only when `slots[key]` is a non-empty exact substring of `copy_text`. Otherwise leave the element. No new elements. Escape the new text.

`copy_block` returns `<div class="sc-fill">...</div>` or `""`. Walk the section `data` dict and keep only string values that are exact substrings of `copy_text`. Skip empty strings and skip `Read on`, `Built with SpiderCaster`, and a lone `About`. Escape HTML. No extra words.

## Structure (`lib/structure.py`)

```python
def make_structure(site: dict, frame_id: str, mold_id: str, picks: dict) -> dict:
def save_structure(path: Path, data: dict) -> None:
def load_structure(path: Path) -> dict:
def validate_structure(data: dict, planned_types: list[str]) -> list[str]:
```

Shape: `{"schema": "spidercaster-structure/1", "frame_id": str, "mold_id": str, "pages": [{"slug": str, "sections": [{"id": str, "type": str, "part_id": str}]}]}`. `validate_structure` returns errors. Every section type must be in `planned_types`. No extra section types. `save_structure` writes UTF-8 JSON with a trailing newline.

## Paint (`lib/mold_paint.py`)

```python
def paint_css(css: str, mold: dict) -> str:
```

`mold` has `palette` (`#rrggbb`) and `type_lead` (`serif`, `sans`, `slab`, `mono-display`). Replace `#14213d` with the palette, case insensitive. Leave `#1a1a1a` and `#ffffff`. Prepend a font stack on `[data-sc-part]`:

- serif: Georgia, "Iowan Old Style", "Palatino Linotype", Palatino, serif
- sans: "Segoe UI", system-ui, sans-serif
- slab: Rockwell, "Rockwell Nova", Georgia, serif
- mono-display: "Cascadia Mono", Consolas, monospace

Use `lib.render.contrast_ratio`. If white on the palette is under 4.5 and `#1a1a1a` on the palette is under 4.5, raise `MoldPaintError`. No `@import`. No `url(http`. No remote font.

## Swap (`lib/part_swap.py`)

```python
def wrap_part(catalog_id: str, css: str, fragment: str) -> str:
def replace_part(html: str, catalog_id: str, css: str, fragment: str) -> str:
def bind_hashes(html: str) -> str:
```

`wrap_part` returns a style tag `data-sc-tool="ID"` plus `<div data-sc-part="ID">fragment</div>`. CSS is escaped so it cannot close the style tag.

`replace_part` replaces the existing style and div for that id. If either marker is missing, raise `PartSwapError` with `part not on page`.

`bind_hashes` rewrites `href="#missing"` to `href="#main"` when `id="main"` exists and the target id does not.

## Lock (`lib/lock_file.py`)

```python
def read_locks(project: Path) -> dict:
def assert_unlocked(project: Path, dest: Path) -> None:
```

`read_locks` reads `project/lock.txt`. Missing file: `{"ok": True, "present": False, "locks": [], "error": ""}`. A non-empty line that is absolute, contains `..`, or contains `http:`, `https:`, or `file:` fails: `ok` false, empty `locks`, `error` set. Good lines are relative paths.

`assert_unlocked` raises `LockError` when `dest` resolves inside `project` and its relative path is locked. A missing lock file does not raise. Do not create `lock.txt`.

## Visit (`lib/visit_check.py`)

```python
def visit_html(html: str) -> dict:
def visit_site(site_dir: Path) -> dict:
```

Return `{"ok": bool, "mode": "static"|"rendered", "failures": [{"code": str, "detail": str}]}`. Static failures:

- `missing_header`: no `site-header` and no `<header`
- `missing_main`: no `id="main"`
- `broken_hash`: `href="#id"` whose id is not in the page (`#main` must exist)
- `missing_viewport`: no viewport meta
- `sideways`: a style or element sets a fixed width greater than 1280px, or `min-width` greater than 400px on `body` or `html`

`visit_site` reads `index.html`. If `playwright` imports, also measure at 390 and 1280: fail `sideways` when `scrollWidth > clientWidth + 1`, and fail `missing_header` when no header element is visible. If playwright is missing or the browser fails to launch, keep the static result and set `mode` to `static`. No network. No publish.

## Copy (`lib/copy_pack.py`)

```python
def project_copy_text(project: Path) -> str:
```

Concat `project/copy/*` for suffixes `.md`, `.markdown`, `.txt`, sorted by file name, UTF-8, separated by newlines. Missing dir returns `""`. Do not read `keys`. Do not include the brief.

## Crew gate

`lib/crew.py` only. Before every `HANDS[name](ctx)`, call `seat_gate(role_id, role_id, name)` from `lib.seat_gate`. A refused hand becomes status FAIL and stops the seat. Call the gate for `ticket_write` as seat `deployer`. Do not pass `live=True`. Do not bind.

## Compose (`lib/compose.py`)

```python
def compose_project(project: Path, out: Path, frame_id: str = "", mold_id: str = "", part_overrides: dict | None = None) -> dict:
```

Return `{"ok": bool, "site_dir": str, "structure": str, "part_ids": list[str], "error": str}`.

Steps:

1. `assert_unlocked(project, out)` when `out` is inside `project`.
2. `ingest.load_project`, then `offline.plan_offline`. No AI. No tokens.
3. If `frame_id` is set, `frames.load_frame` and `frames.apply_frame` on the first page. Do not add a section the plan does not have.
4. If `mold_id` is set, load `library/molds/<id>.json` and set `theme.accent` and `theme.template` from the mold. Do not write the ledger.
5. `ir.normalize_site`, then `render.assemble` with `noindex=True`, write the files, `site.json`, and `favicon.svg`.
6. Pick a header, a footer, and one part per section. Honor `part_overrides` keyed by section id or by `header` / `footer`.
7. Paint CSS when a mold was loaded. `fill_fragment` then append `copy_block` inside the part div. `bind_hashes`. Insert the header block inside the first `site-header` element. Insert the footer block inside the first `footer`. Insert each section block just inside the matching `<section id="...">`. Do not remove the renderer markup.
8. Save `structure.json` beside `index.html`.
9. On success `ok` is true. On failure write nothing new after the error and return `ok` false. Do not publish.

## Apply kwargs

`apply_part(catalog_id, page, out, rows=None, *, replace=False, mold=None, project=None)`.

`replace=False` still appends before `</body>`, using `wrap_part`. `replace=True` uses `replace_part` and raises if the part is not on the page. `mold` is passed to `paint_css`. `project` is passed to `assert_unlocked` for `out`. Keep the noindex, favicon, and site-header guards. Keep hash binding.

## CLI

`spidercaster.py` only.

- `build --compose --offline [--frame] [--mold] [--out]` calls `compose_project`. Default build without `--compose` stays as it is.
- `compose PROJECT [--out] [--frame] [--mold]` calls `compose_project`. Default out is `sites/<slug>-compose`.
- `check SITE [--project DIR]` passes `project_copy_text` into `check_site` as `copy_text`. Without `--project`, `copy_text` stays empty.
- `visit SITE` prints `visit_site` and exits 1 when `ok` is false.
- `tools apply ID --page --out [--replace] [--mold MOLD_ID] [--project DIR]`.

No `--live`. No deploy.
