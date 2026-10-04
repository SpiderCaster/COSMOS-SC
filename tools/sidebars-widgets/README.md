# sidebars-widgets

Static sidebar layouts and sidebar widgets for SpiderCaster sites. Each item is plain HTML, CSS and, where needed, a small script. Items work inside OceanWP and GeneratePress pages and on static SpiderCaster output.

Slice owner: SC Tools Sidebars Widgets. Headers, menus, footers, hooks and blocks belong to other builders and are not here.

## Layout

```
sidebars-widgets/
  sidebars/<slug>/    layout items
  widgets/<slug>/     widget items
  _lib/               test harness, test contexts, measurement script (not shipped to sites)
  catalog.json        machine catalog, written by run_all.py
  CATALOG.md          readable catalog
  COUNTS.md           built / tested / failed
  PLAN.md             conventions found and build plan
  run_all.py          run every test, update status and catalogs
  selftest.py         negative controls for the harness
```

Each item folder holds:

| File | Purpose |
|---|---|
| `manifest.json` | name, slug, kind, purpose, inputs, files, test command, status, size, notes |
| `<slug>.html` | fragment with `{{token}}` fields |
| `<slug>.css` | styles, every selector starts with `.sc-` |
| `<slug>.js` | optional, no network calls, no innerHTML |
| `fixture.json` | test data only, never shipped to a site |
| `test.behavior.js` | scripted checks that run in the page |
| `test.py` | runs the shared harness for this item |
| `demo/` | generated test pages for both contexts, open in a browser |

## Template syntax

- `{{name}}` inserts an escaped value.
- `{{{name}}}` inserts HTML as given (slots such as `main`, `aside`, `ad_code`).
- `<!--each list-->...<!--/each-->` repeats for each entry; `{{@index}}` counts from 1.
- `<!--if name-->...<!--/if-->` and `<!--unless name-->...<!--/unless-->` show a block by value. No nesting.

SpiderCaster fills the tokens from page data. In WordPress, paste the rendered HTML into a Custom HTML widget and load the CSS and JS once.

## Run

```
python run_all.py                 all items, writes status
python run_all.py --only toc,search
cd widgets/search; python test.py one item
python selftest.py                proves the tests can fail
```

Needs Python 3.9+ and Chrome or Edge. Set `SC_CHROME` to a browser path if none is found. With no browser the tests run the static checks and report `static-only`, never `pass`. Set `SC_NO_BROWSER=1` to force that.

## What a pass means

Static: manifest keys, slug shape, tokens declared and used, balanced HTML, labels on fields, alt text and size on images, no inline style or handlers, no remote assets, no `rem` units, no font under 16 px, scoped selectors, no unsafe JS APIs, node syntax check, no secrets, size budget.

Browser, at 360 px and 1280 px, in an OceanWP-like context (root font 62.5%) and a GeneratePress-like context: no horizontal overflow, text at 16 px (18 px for paragraphs, buttons and fields), 4.5:1 contrast on rendered colors, tap targets of 44 px, and the item's own scripted behavior.

## Limits

- The two contexts are written for these tests. They approximate theme base rules and are not vendor CSS. No item has run on a live OceanWP or GeneratePress install.
- Headless Chrome here draws no animation frames, so native scroll timing is not covered. `back-to-top` sends a synthetic scroll event.
- Demo and fixture text exists only for tests. Nothing in an item ships sample copy, thumbnails or art.
- Theme CSS that sets `overflow:hidden` on a parent breaks sticky. See `sidebar-sticky-right`.

## Style variables

Items read these custom properties and fall back to built-in values: `--sc-fg`, `--sc-muted`, `--sc-accent`, `--sc-line`, `--sc-bg` (drawer), `--sc-max`, `--sc-side`, `--sc-sticky-top`. Set them on a parent such as `.site` to match a site palette. Keep text at 4.5:1 against its background.
