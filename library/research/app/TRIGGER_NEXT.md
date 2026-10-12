# Next mobile triggers

Read 2026-10-01 from `lib/triggers.py` only. This note does not edit Python. It does not publish. It does not bind a live site. It does not call an image API.

`review(html)` is present. It returns `{"ok", "hits"}`. Each hit is `code` and `fix`. `ok` is false when any hit has `fix` `none`. No hit in this function uses `fix` `rerender`.

## Codes `review()` already returns

| code | phone-page condition | fix |
| --- | --- | --- |
| `phone_hero_short` | the html contains `height:168px` | none |
| `phone_hidden` | the html contains `.reveal{opacity:0` and no `@media` rule whose prelude contains `max-width:860px` sets `.reveal{opacity:1` inside that rule. A `prefers-reduced-motion` rule does not clear it | none |
| `empty_panel` | the html contains `about-panel` | none |
| `missing_skip` | the html does not contain `href="#main"` | none |
| `remote_img` | an `img` `src` starts with `htt<local-path>`, `https://`, or `//` | none |

Fix `none` must not loop. `_rerender_once` returns without another render when no hit has `fix` `rerender`. These five codes must not start a second render.

A rerender trigger may fire once. This file does not add one. A second render of the same page would match the same text again, so none of the rows below ask for it.

## Proposed codes

These six names are not returned by `review()`. Each may be recorded once. None publishes, binds live, calls an image API, or retries.

| code | condition a phone page would fail | fix | max times |
| --- | --- | --- | --- |
| `nav_here_hidden` | phone CSS sets `.nav-here{display:none}` | none | 1 |
| `letter_mark_tall` | a `.hero-mark` exists and the phone hero is `aspect-ratio` `16/9` (empty slab) | none | 1 |
| `menu_desc_flex` | `.mi-desc{width:100%}` and `.dots` exist in the base CSS with no phone override that stacks the row | none | 1 |
| `summary_short` | `summary` has no `min-height` `44px` | none | 1 |
| `footer_safe_area` | `footer` has no `safe-area-inset-bottom` | none | 1 |
| `focus_missing` | no `:focus-visible` rule | none | 1 |

Fix `none` on every new row must not loop. If a later code uses `fix` `rerender`, that trigger may fire once and must not fire again. No row here is that code.
