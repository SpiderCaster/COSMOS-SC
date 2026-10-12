# Mobile

Seat card for phone layout. Read from `lib/render.py` and `lib/triggers.py` on 2026-10-01, after the wait. Pack file: `library/rules/mobile.json` (`spidercaster-mobile-rules/1`). A line below is a rule only where that code already does it. `height:168px` is not in the renderer. The 16/9 hero rule is not pending.

Do not publish. Staged pages stay noindex. This card is not a hand.

## Phone width

The phone sheet is `@media(max-width:860px)`. Three blocks use that query.

- `.contact-grid` and `.about-grid` become one column.
- Nav does not wrap. The brand can shrink. `.nav-links` is a fixed sheet from under the header to the bottom of the screen, hidden until `.open`. The menu button is shown. `.nav-here` is hidden. `.wrap` side padding is 16px. Sections use 40px vertical padding. The hero uses 28px on top and 40px on the bottom. `.c2` and `.c3` are one column. `body.nav-open` sets `overflow:hidden`.
- `.reveal` is `opacity:1` with `transform:none`.

The viewport meta is `width=device-width,initial-scale=1,viewport-fit=cover`. The wide hero layout starts at `@media(min-width:861px)`.

## Hero aspect

Base `.hero-visual` sets `aspect-ratio:16/9` and `height:auto`. That is the phone hero. The image is positioned to cover that box. The renderer has no `height:168px`.

At `min-width:861px` the same class sets `aspect-ratio:auto` and `height:320px`. `.hero--bold .hero-visual` sets `height:380px`. Those heights are not the phone rule.

`lib/check.py` `mobile_hero` fails `height:168px` and passes `aspect-ratio:16/9`. `lib/triggers.py` `review` records `phone_hero_short` only when the HTML still contains `height:168px`.

## Tap size

These controls are at least 44px. `.skip`, `.btn`, `.brand`, `.nav-links a`, and `.foot-links a` set `min-height:44px`. `.nav-toggle` is `width:44px` and `height:44px`. `.hero-cta .btn` repeats the 44px minimum.

Not this rule: `.chip` is 40px, `.step-n` is 32px, `.avatar` is 38px, and `.brand-mark` is 28px.

## Scroll margin

`section` and `h1, h2` set `scroll-margin-top:72px` at every width. The phone block changes section padding and does not remove that margin. `h3` has no scroll margin.

`check_site` row `scroll_margin` passes when `scroll-margin-top` is in the index.

## Reveal on phones

Phones do not hide `.reveal`. Inside `@media(max-width:860px)` the rule is `.reveal{opacity:1;transform:none}`. Wider viewports still start at `.reveal{opacity:0}` until the script adds class `in`. `prefers-reduced-motion:reduce` also forces opacity 1.

`mobile_visible` passes when that phone rule sets opacity 1. `review` records `phone_hidden` only when `.reveal{opacity:0` is present and no `max-width:860px` block sets `.reveal{opacity:1`.

## Empty panel

An about section does not emit an empty panel. `_about_panel` returns nothing unless the panel has text or a local image. The section then omits the side column. A remote image is not panel content.

The stylesheet still contains the selector `.about-panel`. `no_empty_panel` fails when the text `about-panel` appears anywhere in `index.html`, including that selector. `review` records `empty_panel` for the same substring. A page from this renderer still hits those two checks. Do not report `no_empty_panel` as a pass.

## Skip link

Every page has `<a class="skip" href="#main">Skip to content</a>` before the header, and `<main id="main">`. The link sits above the viewport until it is focused. `skip_link` passes on `href="#main"`. `review` records `missing_skip` when that href is absent.

## Remote images

A hero image and an about-panel image go through `_local_image_src`. Values that start with `http://`, `https://`, or `//` stay empty. The hero then uses the letter mark. `og:image` is written only for a remaining local hero src. Hero data in `lib/ir.py` clears those same prefixes and a `..` path.

`relative_img` fails an index `img` whose src is `http://`, `https://`, `//`, empty, or missing. `asset_list` fails a remote asset url. `review` records `remote_img` for an `img` src with those three prefixes.

## Noindex while staged

`assemble` defaults to `noindex=True`. The frontend `render` hand calls `assemble` with `noindex=True`. That writes `<meta name="robots" content="noindex, nofollow">` and the comment `SpiderCaster: noindex until approved`. The visual hand expects noindex. Do not pass `--indexable`.

## Not a hand

`lib/triggers.py` `review(html)` returns `ok` and `hits`. It does not fetch, write, or publish. Seat hands do not import it. Every hit uses `fix` `none`, and `ok` is false when any hit is present. Codes: `phone_hero_short`, `phone_hidden`, `empty_panel`, `missing_skip`, `remote_img`.
