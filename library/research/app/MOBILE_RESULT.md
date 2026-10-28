# Mobile score

Score only, 2026-10-01. Not published. HTML and lib were not edited.

Paths are under `V:\a\Ai\spidercaster\working`.

`inbox/harbor-mobile.md` and `inbox/demo-mobile.md` were polled every 30 seconds from 16:07:01 through 16:16:31 (20 cycles). At the 16:17:01 timeout read, neither file had a DONE line. Both said STOPPED. A later read of each file contained `STATUS: DONE` after a parent-rebuild note. The pages scored here are `stage/harbor/out/index.html` and `stage/demo/out/index.html`, both last written 2026-10-01 16:20:55. Both are `noindex, nofollow`.

Phone means the `@media(max-width:860px)` sheet. The `@media(min-width:861px)` hero grid does not apply.

## Harbor

A phone gets the picture first, then the heading, then the lede, then one full-width button. The picture is `assets/hero.png`, alt `Harbor Tea Room`, 1280 by 720, `sizes="100vw"`. The box is a full-width 16:9 crop (`object-fit:cover`, `object-position:center`), rounded, with the tea-room photo inside it. The heading is `Harbor Tea Room`. The lede is `A quiet tea room that seats walk-ins by the water.` The button text is `Contact` and the link is `#contact`. Under that: one sentence with no heading (`Loose-leaf, brewed to order; decaf after 4pm on request.`), then Contact (`(555) 014-2288`, `14 Harbor Lane`, lede `Walk-ins only; no reservations needed.`), then Hours (`Open Tuesday to Sunday, 8am to 6pm.` and `Closed Mondays.`), then Menu (`Jasmine Pearl` `$4.50`, `Assam Malt` `$3.75`, `Peppermint Field` `$3.25`, lede `12oz cups, brewed to order.`). Section headings on this template are centered. The hero heading is left-aligned. Dotted menu leaders are `display:none`. Each menu row is a two-column grid, name then price.

The rule that sets that phone hero is the base rule. The 861px sheet replaces it with a fixed height, and a phone does not use that sheet.

```css
.hero-visual{position:relative;overflow:hidden;border-radius:18px;border:1px solid var(--line);aspect-ratio:16/9;height:auto;margin:0 0 18px;background:
radial-gradient(120% 90% at 100% 0%,var(--accent-soft),transparent 55%),
linear-gradient(160deg,var(--surface),var(--bg))}
```

Body copy is not hidden until JS. Nothing on this page uses `class="reveal"`. The phone sheet also sets `.reveal{opacity:1;transform:none}` over the base `.reveal{opacity:0}`.

The header links are hidden until JS. At 860px, `.nav-links{display:none}` until `.nav-links.open`, and only the script adds `open`. The visible labels in that menu are `Contact`, `Hours`, and `Menu`. The menu control has no visible word. Its accessible name is `Menu`.

No empty panel remains. There is no `about-panel` element. The footer `foot-links` div is empty and has no box of its own.

The menu button stays on the header row. The base rule is `.nav{display:flex;align-items:center;gap:12px;min-height:64px;flex-wrap:wrap}`. The phone sheet overrides it:

```css
.nav{flex-wrap:nowrap}
```

The brand is `flex:1 1 auto; min-width:0`, and the button is `flex:none` at 44 by 44. Nowrap keeps the button on that row. An empty `nav-here` span is also on the row (`display:block; flex:1 1 auto`). It shares the free space with the brand, so `Harbor Tea Room` ellipsizes sooner than the title length alone would require.

Low-quality pattern that remains: the about block is one sentence and has no heading, with a full section pad around it. Contact and Hours text are not links. The number is the characters `(555) 014-2288` inside a span.

## Demo

A phone does not get a 16:9 hero. The node is `hero-visual hero-mark`, there is no image, and the only mark is the letter `S` (`aria-hidden="true"`). The same 16:9 rule as Harbor is in the sheet, and the phone query cancels it:

```css
.hero-visual.hero-mark{aspect-ratio:auto;height:auto;max-height:140px}
```

The letter size in that query is `clamp(2.4rem,18vw,4.2rem)`, aligned to the bottom of the gradient. The box is a short bar, at most 140px, not a 16:9 frame.

Under that bar the heading is `SpiderCaster: websites from real copy, on free tokens`. The lede is the overview paragraph already in the hero, and it sits above the button. The button text is `Build` and the link is `#features`. On this template the button is a full-width pill. `Build`, `Iterate`, `Gate and preview`, `House rules the engine enforces`, `Questions about the engine`, and `Why it is cheap` are the menu labels. The menu control's accessible name is `Menu`.

Body copy is not hidden until JS. The feature cards use `class="card reveal"`, and the base rule is `.reveal{opacity:0}`. The phone sheet sets `.reveal{opacity:1;transform:none}`, so those cards are visible without the script adding `in`. About, Iterate, Gate and preview, and the FAQ are not `reveal` nodes. FAQ questions use `details`, which open without JS.

The header links are hidden until JS, same rule as Harbor.

No empty panel remains. About, Iterate, and Gate and preview are body text only. There is no `about-panel`.

The menu button stays on the row, same nowrap override as Harbor. The brand string is the long title, `white-space:nowrap` with an ellipsis, and the empty `nav-here` has the same flex grow as the brand. The name is cut. The button does not wrap off the row.

Low-quality pattern that remains: a hidden letter in a short gradient, then a sentence-length heading, then the full overview paragraph, before the only button. Card lines such as `scaffold a project with brief.md and a copy folder.` are printed as given, starting in lowercase. The six menu labels are the full section titles.

## Engine gaps

1. Under 860px the section links are `display:none` until script adds `open`. There is no way to open that list without JS.
2. The phone sheet shows `.nav-here` at `flex:1 1 auto` while it is empty, so the brand and a blank slot split the row. `flex-wrap:nowrap` keeps the menu button on the row, and the name ellipsizes.
3. A hero with no picture is `.hero-visual.hero-mark`. On a phone that rule sets `aspect-ratio:auto` and `max-height:140px`, which drops the 16:9 frame.
4. `section`, `h1`, and `h2` use `scroll-margin-top:72px`. The sticky header is `padding-top:env(safe-area-inset-top)` plus a 64px bar. On a notched phone, 72px is shorter than that bar, so a jump can sit under the header.
5. The phone number and the address are text in spans. `(555) 014-2288` is not a `tel:` link, and `14 Harbor Lane` is not a link.
