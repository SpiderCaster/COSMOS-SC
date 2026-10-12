# Next renderer pass

This is the pass after `library/research/app/inbox/render-mobile.md`. It is not that pass.

Do not edit `lib/render.py` until that inbox contains a line `DONE`. A mention of the word DONE inside a STARTED note is not a completion. On this read the file is `STARTED` / `2026-10-01` and does not contain `DONE`. Re-read `CSS_TEMPLATE` in `lib/render.py` after the gate opens, then edit only that template.

Do not edit `stage/`. Do not publish. No `--live`. No secrets. Do not change menu item text. Do not add a remote image.

Selectors below match `CSS_TEMPLATE` as read for this note. The photo 16/9 rule is the base `.hero-visual` declaration (`aspect-ratio:16/9;height:auto`), not a rule inside `@media(max-width:860px)`. Desktop sizes stay in `@media(min-width:861px)`: `.hero-visual` is `aspect-ratio:auto;height:320px`, and `.hero--bold .hero-visual` is `height:380px`.

## Already in the current pass

Do not redo that owner's set: phone photo hero 16/9 and height auto, no empty about-panel, scroll-margin-top at least 72px, phone `.reveal` opacity 1, `.nav` nowrap under 860px, menu rows at least 48px, contact rows at least 44px, wrap padding 16px, section padding 40px 0, tighter hero padding, h1 clamp floor, inputs at least 16px.

## 1. Letter-mark heroes

Photo and letter mark share `.hero-visual` today, so the base `aspect-ratio:16/9;height:auto` turns a mark with no photo into a 16/9 slab. Split them.

Photo markup from `hero_visual()` is `<div class="hero-visual"><img ...></div>` when the image is a local path. Keep that box on the base rule:

- `.hero-visual` — `aspect-ratio:16/9; height:auto`
- `.hero-visual img` — `position:absolute; inset:0; width:100%; height:100%; object-fit:cover; object-position:center`

Do not add a base `.hero-visual:not(.hero-mark)` aspect-ratio rule. That selector is more specific than `@media(min-width:861px) .hero-visual` and would undo the desktop `height:320px` and `.hero--bold .hero-visual` `height:380px` rules.

Letter markup is `<div class="hero-visual hero-mark" aria-hidden="true"><span>letter</span></div>` when there is no local image. No `<img>`. No `url()`. No `http` or `https`. Leave `hero_visual()` on that path.

Phone only, inside the existing `@media(max-width:860px)` block:

- `.hero-visual.hero-mark` — `aspect-ratio:auto; height:auto; max-height:140px; container-type:inline-size`
- `.hero-visual.hero-mark span` — `font-size:clamp(2.4rem, 22cqi, 4.2rem); line-height:.8`

`.hero-visual.hero-mark` beats the base `.hero-visual` 16/9 rule and does not apply at `min-width:861px`, so desktop marks stay on the existing 320px / 380px heights. `22cqi` scales the glyph with the box width. `max-height:140px` is the cap that stops the empty slab. Keep the existing `.hero-mark` rule `display:flex; align-items:flex-end; padding:18px`. The gradient on `.hero-visual` is local CSS, not a remote image. Leave it.

## 2. Menu rows under 860px

Markup stays:

`<div class="menu-item"><div class="mi-col"><span class="mi-name">…</span><span class="mi-desc">…</span></div><span class="dots" aria-hidden="true"></span><span class="mi-price">…</span></div>`

Do not change the name, description, or price strings.

Above 860px the row stays as it is. Base `.menu-item` is `display:flex; align-items:center; gap:10px; padding:7px 0; min-height:48px`. `.dots` stays visible. `.mi-price` stays at the end of the row. `.mi-col` stays `display:flex; flex-direction:column; flex:1; min-width:0`.

Inside `@media(max-width:860px)` only:

- `.menu-item` — `display:grid; grid-template-columns:minmax(0, 1fr) auto; align-items:center; column-gap:10px; row-gap:2px; min-height:48px`
- `.menu-item .mi-col` — `display:contents`
- `.menu-item .mi-name` — `grid-column:1; grid-row:1; min-width:0`
- `.menu-item .mi-price` — `grid-column:2; grid-row:1; justify-self:end; white-space:nowrap`
- `.menu-item .mi-desc` — `grid-column:1 / -1; grid-row:2; width:100%`
- `.menu-item .dots` — `display:none`

`display:contents` is what puts `.mi-price` on the same line as `.mi-name`. A `.mi-col` at `width:100%` in the flex row would push the price under the whole column. The description is the full-width second row. Set the grid lines. Source order is name, description, dots, price, so auto-placement would put the description in the price cell. Minimum row size stays 48px.

## 3. `.nav-here` on phones

Inside `@media(max-width:860px)` the template sets `.nav-here{display:none}`. Remove that declaration.

Replace it in that same block:

- `.nav-here` — `display:block; flex:1 1 auto; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap`

That is one truncated line. Keep the base color and `font-size:1rem` on `.nav-here`.

Leave the link sheet. `.nav-links` stays `display:none` and `position:fixed` until `.nav-links.open` sets `display:flex`. Do not change those selectors.

Leave the toggle. `.nav-toggle` stays `width:44px; height:44px; flex:none`, and under 860px it stays `display:inline-flex`.

## Small additions

Not part of the three changes.

- `:focus-visible` outline. There is no author `:focus-visible` rule. The only focus outline is `.form input:focus, .form textarea:focus`. Add a base rule, not only under 860px: `a:focus-visible, button:focus-visible, summary:focus-visible` — `outline:2px solid var(--text); outline-offset:2px`. Do not set `outline:none`. Do not replace the form `:focus` rule. `.skip:focus{top:12px}` already brings the skip link onscreen. Leave it.

- Footer home-indicator inset. `.site-footer` padding is `32px 0`. Change that value to `32px 0 calc(32px + env(safe-area-inset-bottom))`. Do not remove `padding-top:env(safe-area-inset-top)` on `.site-header`, or the safe-area padding already on `.nav-links`. The viewport meta already has `viewport-fit=cover`.

## After the edit

From `<repo-root>`, run:

- `py -3.14 -m lib.hands.selftest`
- `py -3.14 -m lib.regress`
- `py -3.14 spidercaster.py crew selftest`

No `--live`. Do not start until `library/research/app/inbox/render-mobile.md` contains `DONE`.
