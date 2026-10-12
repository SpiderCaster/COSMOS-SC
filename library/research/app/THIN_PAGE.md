# Thin page causes that remain

Read-only, 2026-10-01. Not published. No crew. No `--live`. HTML, Python, stage, and lib were not edited.

Paths are under `<repo-root>`.

Read: `stage/harbor/out/index.html` (present), `stage/demo/out/index.html` (present), and the phone CSS in `lib/render.py` (`CSS_TEMPLATE`, `@media(max-width:860px)` plus `.hero-visual`, `.reveal`, `.about-panel`, `.nav-here`).

Staged CSS is the older sheet (`hero-visual` height 168px, phone `section` padding 48px, `.reveal` still opacity 0 until `.in`). `lib/render.py` already has the assigned phone rules. Causes below are what is still true after those assigned rules land. Nothing here is an award, a review, or new copy.

## Already assigned

Not main findings. A renderer owner is already required to change these:

- hero height 168px becomes `aspect-ratio:16/9` and `height:auto`
- remove empty about-panel
- scroll-margin-top
- `.reveal` opacity 1 under 860px
- nav nowrap
- taller menu and contact rows
- tighter wrap and section padding
- h1 clamp floor
- inputs at least 16px

Staged harbor and demo still show the pre-change sheet, including empty `<div class="about-panel" aria-hidden="true"></div>` on harbor `#about` and `#hours`, and on demo `#about`, `#iterate`, and `#gate-and-preview`. The current renderer `_about_panel` returns nothing when panel content is empty. That removal is the assigned item.

## Remaining causes (6)

### 1. `.nav-here{display:none}` on phones

The dynamic header label is hidden under 860px. The span and the script that writes it are still there.

Renderer, inside `@media(max-width:860px)`:

`.nav-here{display:none}`

Same rule in the staged sheet of harbor and of demo.

HTML on harbor and demo, and in `render_page`:

`<span class="nav-here" aria-live="polite"></span>`

The script still does `document.querySelector('.nav-here')` and sets `here.textContent` from the visible section heading. `display:none` keeps that label off the phone header. Nav nowrap is a different rule (`.nav{flex-wrap:nowrap}`) and does not undo this.

Shown on: renderer, harbor, demo.

### 2. Letter-mark hero in a tall 16/9 box

After the assigned 16/9 rule, a page with no photo still gets a letter sitting in an empty gradient.

Renderer default (the phone rule; the `min-width:861px` block sets a fixed height instead):

`.hero-visual{position:relative;overflow:hidden;border-radius:18px;border:1px solid var(--line);aspect-ratio:16/9;height:auto;margin:0 0 18px;background:radial-gradient(120% 90% at 100% 0%,var(--accent-soft),transparent 55%),linear-gradient(160deg,var(--surface),var(--bg))}`

`.hero-mark{display:flex;align-items:flex-end;padding:18px}`

`.hero-mark span{font-family:Georgia,'Times New Roman',serif;font-size:4.2rem;line-height:.8;color:var(--accent)}`

No-image branch in `hero_visual`:

`<div class="hero-visual hero-mark" aria-hidden="true"><span>{letter}</span></div>`

Demo hero (no `img`):

`<div class="hero-visual hero-mark" aria-hidden="true"><span>S</span></div>`

Harbor does not show this. Its hero is `<div class="hero-visual"><img src="assets/hero.png" alt="Harbor Tea Room" width="1280" height="720" ...>`. The `.hero-mark` rules are in the harbor stylesheet only. The element is not in the harbor body.

Shown on: renderer, demo. Not the harbor hero.

### 3. Menu row flex: `.mi-desc` width 100% plus `.dots`

Taller rows (`min-height:48px`) do not fix the flex. The description is `width:100%` and the dotted leader is a sibling in the same row.

Renderer:

`.menu-item{display:flex;align-items:center;gap:10px;padding:7px 0;min-height:48px}`

`.menu-item .mi-desc{color:var(--muted);font-size:1rem;width:100%}`

`.menu-item .dots{flex:0 1 1.5rem;border-bottom:2px dotted var(--line);min-width:12px}`

`.menu-item .mi-col{display:flex;flex-direction:column;flex:1;min-width:0}`

Menu emitter, when an item has a desc:

`<div class="menu-item"><div class="mi-col"><span class="mi-name">…</span><span class="mi-desc">…</span></div><span class="dots" aria-hidden="true"></span><span class="mi-price">…</span></div>`

`width:100%` on `.mi-desc` and `.dots` at `flex:0 1 1.5rem` share that row. A long desc keeps the column wide; the dots stay a short stub.

Harbor and demo stylesheets still have the older pair:

`.menu-item .mi-desc{color:var(--muted);font-size:1rem;width:100%}`

`.menu-item .dots{flex:1;border-bottom:2px dotted var(--line);transform:translateY(-4px);min-width:24px}`

Harbor menu HTML has `.dots` and no `.mi-desc`. The three rows are Jasmine Pearl, Assam Malt, and Peppermint Field, each name plus price only. Demo has the selectors and no `.menu-item` in the body.

Shown on: renderer (CSS and the emitter). Selector also in harbor and demo CSS. Neither staged menu row combines `.mi-desc` with `.dots`.

### 4. Section padding still large on a short phone

The assigned tighter padding is already the renderer phone rule. It is still 40px on the top and 40px on the bottom, and there is no shorter or `max-height` query.

Renderer, inside `@media(max-width:860px)`:

`section{padding:40px 0}`

Also in that block: `.hero{padding:28px 0 40px}` and `.wrap{padding:0 16px}`. Base rule outside the query remains `section{padding:72px 0}`. Eighty pixels of vertical padding per section is most of a one-line block on a short phone. Harbor `#about` is one sentence: `Loose-leaf, brewed to order; decaf after 4pm on request.`

Staged harbor and demo still say `section{padding:48px 0}` inside `@media(max-width:860px)`. That 48px is the value the assigned tighter-padding change replaces. It is not an extra cause.

Shown on: renderer (the 40px rule that remains). Staged pages still show the pre-change 48px.

### 5. Cards that are a border and one sentence

`.card` is a bordered surface. Demo feature cards put a chip, an `h3`, and one `<p>` in it.

Renderer and both staged sheets:

`.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;...}`

`.card p{color:var(--muted);margin:0}`

Features emitter:

`<div class="card reveal"><span class="chip">…</span><h3>…</h3><p>…</p></div>`

Demo, 13 cards, each with one sentence. Sections: `#features` (4), `#features-2` (4), `#features-3` (5). Example from `#features`:

`<div class="card reveal">…<h3>forge init PROJECT</h3><p>scaffold a project with brief.md and a copy folder.</p></div>`

Same shape on the other twelve: one heading, one `<p>`. Harbor body has no `class="card"`.

Shown on: demo, renderer. Not harbor.

### 6. Gallery `img` src is not limited to a local path

No remote image is in either staged page. The renderer can still write one from a gallery item.

Harbor’s only `img`:

`<img src="assets/hero.png" alt="Harbor Tea Room" width="1280" height="720" fetchpriority="high" decoding="async">`

Demo has no `img` and no `src=` attribute. The only `https://` in either file is `"@context": "https://schema.org"` inside JSON-LD, not an image.

Hero and about images go through `_local_image_src`, which returns empty for `htt<local-path>`, `https://`, and `//`. Gallery does not:

`<img src="{esc(it["src"])}" alt="…" loading="lazy">`

A gallery item whose `src` is `http`, `https`, or `//` is emitted as-is. Neither staged page has a gallery.

Shown on: renderer. Not on harbor or demo.

## Checked, not remaining

Footer credit / “Built with”. Stylesheet rule on the renderer, harbor, and demo:

`.credit{margin-top:10px;font-size:.92rem;opacity:.85}`

No element uses `class="credit"`. Neither footer contains “Built with”. Harbor footer text is `(c) 2026 Harbor Tea Room`. Demo footer text is `(c) 2026 SpiderCaster: websites from real copy, on free tokens`. The renderer prints `site['footer']['text']` only.

Skip link. Not missing. Renderer, harbor, and demo:

`<a class="skip" href="#main">Skip to content</a>`

`<main id="main">`
