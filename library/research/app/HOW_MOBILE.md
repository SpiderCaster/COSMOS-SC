## Correction 2026-10-01

The findings below were measured before the phone pass landed. They are left as written. This list is only what `lib/render.py` does now. No phone was measured.

- Photo `.hero-visual` is aspect-ratio 16/9 and height auto.
- `.hero-visual.hero-mark` on phones is aspect-ratio auto and max-height 140px.
- No `height:168px`.
- No `about-panel` class.
- Phone `.reveal` is opacity 1.
- `.nav-here` is display block on phones, one truncated line.
- Menu `.dots` are display none under 860px.
- `.hero-cta` is a column and the button is width 100%.
- `summary` is min-height 44px.
- Footer padding includes `env(safe-area-inset-bottom)`.

# How the brochure page sits on a small screen

Read 2026-10-01 from the public pages linked under each rule. A number below is that page's number, or a literal in `lib/render.py` and the same literal in `stage/harbor/out/index.html`. This note did not open a phone, did not run Lighthouse, and did not measure a painted box. No site was built. `lib/render.py` was not edited.

Scope: the CSS that applies when `max-width: 860px` matches. That includes the block that starts `.nav-links{display:none;position:fixed...}`, the two earlier one-line queries for `.contact-grid` and `.about-grid`, and every rule those queries do not override. The three `max-width:860px` queries in `lib/render.py` (`CSS_TEMPLATE`) and in `stage/harbor/out/index.html` are the same text. Harbor's staged sections are hero, about, contact, about (Hours), and menu.

## Viewport and reflow

https://web.dev/articles/responsive-web-design-basics (page last updated 2019-02-12)

A page aimed at more than one screen puts `<meta name="viewport" content="width=device-width, initial-scale=1">` in `<head>`. Without it, mobile browsers lay the page out near `980px` and scale it down. `width=device-width` matches the screen in CSS pixels. `initial-scale=1` keeps a 1:1 CSS-pixel scale when the device rotates, so landscape can reflow instead of zooming a portrait layout. That page says not to set `minimum-scale`, `maximum-scale`, or `user-scalable`, because those can block zoom.

People scroll vertically. A horizontal scrollbar, or a zoom-out just to see the page, is the failure it names. An image with a fixed size that is wider than the viewport causes that scroll. The fix it shows is `img { max-width: 100%; display: block; }`. It still wants `width` and `height` on the `<img>` so the browser can reserve space before the file loads.

Layout should not depend on one viewport width. A column sized in pixels can sit outside the viewport; the page's picture is a two-column float with most of the second column off-screen. Flexbox, grid, and `fr` are the tools it names. One grid demo uses a minimum track of `200px` and lets the count of columns fall as the screen narrows. Breakpoints should follow the content, starting from the narrow layout, not a device name. Its own warning about whitespace: past about `600px`, a row that was fine on a phone can be too wide, and the layout should change. It also says not to hide content only because it does not fit. Screen size does not say what the reader wanted.

Shipped against that page: the harbor document, and the renderer, emit `<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">`. There is no `user-scalable=no`. `img{max-width:100%;display:block}` is in the sheet. `.wrap` caps the column at `--maxw:1120px` with `padding:0 24px`.

## Tap targets

https://web.dev/articles/accessible-tap-targets (page last updated 2020-03-31)

On a mobile viewport that is set correctly, the recommended touch target is about 48 device-independent pixels on each side. A 24px icon can reach that by padding. The page calls 48 by 48 about 9mm, about a fingertip. Targets should also sit about 8 pixels apart, horizontally and vertically, so one press does not land on the neighbor. If a query is used to enlarge targets, test `(any-pointer: coarse)`, not a guessed phone width. A coarse pointer is a touchscreen of any size. A fine pointer is a mouse or trackpad, including a mouse paired to a phone.

https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html

Success criterion 2.5.8 Target Size (Minimum) is Level AA. The target is at least 24 by 24 CSS pixels, except for the spacing, equivalent, inline, user-agent, and essential cases written on that page. Spacing is only the exception for a target under 24 by 24: a 24 CSS pixel circle centered on each undersized box must not hit another target or another such circle. The page says meeting 24 by 24 is the better practice even when spacing would pass, and it points important controls at the stricter 2.5.5 rule.

https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html

Success criterion 2.5.5 Target Size (Enhanced) is Level AAA. The target is at least 44 by 44 CSS pixels, except equivalent, inline, user-agent control, and essential, as that page defines them. Inline links in a sentence or a block of text are excluded. The page says a larger size than 44 still helps when the control is frequent, hard to undo, near the screen edge, or part of a sequence.

Shipped on the controls that set a 44px box: `.btn` and `.hero-cta .btn` use `min-height:44px`. `.brand` uses `min-height:44px`. `.nav-links a` uses `min-height:44px`. `.nav-toggle` is `width:44px;height:44px`. `.skip` uses `min-height:44px`. `.foot-links a` uses `min-height:44px`. Those heights are the AAA figure, which is also above the AA 24px figure. They are not the about-48px figure on the web.dev page. The sheet has no `(any-pointer: coarse)` query. The 44px sizes are not limited to the 860px block.

The open drawer sets `gap:0` on `.nav-links`. Stacked links are full width and at least 44px tall, with a 1px bottom border inside that box (`box-sizing:border-box` is on `*`). They meet the 44px AAA size on both axes. They do not have the about-8px separation from the web.dev page. That spacing sentence is not a WCAG failure for a target that is already 44 by 44.

## viewport-fit and safe area

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/viewport (page modified 2026-09-23)

`viewport-fit` is `auto`, `contain`, or `cover`. `auto` leaves the initial layout viewport alone and the whole page viewable. `contain` scales the viewport to the largest rectangle inside the display. `cover` scales the viewport to fill the display. For `cover`, that page says it is highly recommended to use the safe-area inset variables so important content does not land outside the display. Its example is `content="width=device-width, viewport-fit=cover"`.

https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/env (page modified 2026-09-12)

`env(safe-area-inset-top)`, `env(safe-area-inset-right)`, `env(safe-area-inset-bottom)`, and `env(safe-area-inset-left)` are the safe distance from each edge of the viewport. Content inside that rectangle is not cut off by a non-rectangular display. On a rectangular viewport with nothing else occupying the space, the four values are `0`. Otherwise each is a `px` length greater than `0`. The second argument is an optional fallback, used when the name is missing or unsupported. If the substitution is invalid and the fallback is omitted, the property uses its initial or inherited value. The page's footer example pads the bottom with `safe-area-inset-bottom` so a device UI at that edge does not cover the buttons. On a desktop rectangle that inset is `0`.

https://developer.apple.com/design/human-interface-guidelines/layout

That page says a layout should adapt when the device rotates, the window resizes, or the display changes, by respecting system safe areas, margins, and guides where they exist. A safe area is the part of the window not covered at the edge by hardware or by another view such as a toolbar, tab bar, or status bar. Respecting it is how system UI and hardware such as the Dynamic Island stay off content and controls. It also says to choose layout from the space available, not from a device name or an orientation. Important items go near the top and the leading side. When artwork is scaled to a different display, do not change the artwork's aspect ratio; scale it so it fills. That last sentence is about filling without stretching the art. It is not a measured crop on this page.

Shipped: `viewport-fit=cover` is on the viewport meta. `.site-header` sets `padding-top:env(safe-area-inset-top)`. The 860px drawer sets `top:calc(64px + env(safe-area-inset-top))` and `padding:8px 18px calc(18px + env(safe-area-inset-bottom))`. None of those `env()` calls pass a fallback.

## Image box

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img (page modified 2026-09-11)

`height` is the intrinsic height in pixels, an integer with no unit. `width` is the matching width. Including both lets the browser compute the aspect ratio before the file loads and reserve the box, which reduces or prevents a layout shift. Both are recommended on every image, and they matter more when `loading="lazy"` is set, because an unloaded lazy image otherwise has used width and height `0`.

https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/aspect-ratio (page modified 2026-07-21)

`aspect-ratio` sets the preferred width-to-height ratio of the element's box. The browser keeps that ratio when the parent or the viewport changes, but only if at least one of width or height is an automatic size. If both are set, the preferred ratio does not change the box. For a replaced element, `auto` with a ratio uses the ratio until the resource loads, then the resource's own ratio.

Shipped on the harbor hero `<img>`: `width="1280"` `height="720"`, `fetchpriority="high"`, `decoding="async"`, no `loading="lazy"`. The renderer writes `width` and `height` only when both `image_w` and `image_h` are greater than 0. `.tile` sets `aspect-ratio:4/3`. The hero frame does not.

## Sticky target offset

https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/scroll-padding-top (page modified 2026-04-20)

`scroll-padding-top` offsets the top of the scrollport's optimal viewing region, the region used as the target when something is placed in view. The reason on that page is to exclude a region obscured by other content, such as fixed-positioned toolbars or sidebars, or to leave space between the target and the edge of the scrollport. Initial value `0`.

The `scroll-margin-top` page opened with it defines an outset for the scroll snap area. It does not, on the text returned, mention fragment links. This note does not treat that page as the anchor rule. https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/scroll-margin-top

## What the 860px block already changes

Inside `@media(max-width:860px)`:

- `.nav-links` is `display:none` until `.open`, then `display:flex`. Open, it is `position:fixed` from `left:0` and `right:0` to `bottom:0`, with the top and bottom insets above, `flex-direction:column`, `align-items:stretch`, `overflow:auto`.
- Each link in that list is `width:100%` with a bottom border.
- `.nav-toggle` becomes `inline-flex`. It is 44 by 44 in the base rule and `display:none` until this query.
- `.nav-here` is `display:none`.
- `section` padding changes from `72px 0` to `48px 0`.
- `.c2` and `.c3` become `grid-template-columns:1fr`.
- `body.nav-open` sets `overflow:hidden`.

Separate queries at the same width set `.contact-grid` and `.about-grid` to one column. Wider than 860px, those two stay `1.1fr .9fr` and `1.2fr .8fr`.

The hero's larger frame is not in this block. It is in `@media(min-width:861px)`: `.hero-visual` becomes `height:320px`, and `.hero--bold .hero-visual` becomes `height:380px`. Under 861px the base rule stands.

`@media(prefers-reduced-motion:reduce)` sets `.reveal{opacity:1;transform:none;transition:none}`. That query is not the 860px block.

## Suspects

### Nav flex-wrap — shipped

Base `.nav` is `display:flex;flex-wrap:wrap;min-height:64px`. Base `.nav-links` is also `flex-wrap:wrap`. The 860px block takes `.nav-links` out of that header row (`display:none`, and `position:fixed` when open) and hides `.nav-here`. The harbor bar then has the brand and the 44px toggle. The brand has `min-width:0`, and `.brand-name` ellipsizes on one line. The links are not a wrapping row in the 64px bar.

Leftover, not a second row on this page: the 860px rule never sets `flex-wrap:nowrap`. The open list is a column that still inherits `flex-wrap:wrap`, inside a fixed top and bottom. Harbor's open list is three links (`Contact`, `Hours`, `Menu`). This note did not count a wrap on those three.

### Hero height 168px — still true

`.hero-visual{height:168px}` is the rule under 861px. The 860px block does not change it. `.hero-visual img` is `width:100%;height:100%;object-fit:cover`. Both axes of that image box are set, so a preferred `aspect-ratio` would not move it. The harbor file's `1280` and `720` attributes are on the tag. The used frame is the 168px-tall box, and it stays that tall while the viewport widens up to 860px. `object-fit:cover` crops; it does not stretch the pixels. The Apple sentence about not changing artwork aspect ratio is the fill-without-distortion rule, not a pixel count for this crop.

### `.reveal` starts at opacity 0 — still true

`.reveal{opacity:0;transform:translateY(14px)}` is not inside the 860px block and is not overridden there. `.reveal.in{opacity:1}`. The reduced-motion query is the one that forces `opacity:1` without waiting for `.in`. The harbor document has the class in the stylesheet and in the script that adds `.in`. It has no element with `class` containing `reveal`, so this staged page does not hide a section with that rule. The renderer still puts `reveal` on feature cards, step cards, gallery tiles, quote cards, and team cards. The web.dev "do not hide content just because it does not fit" sentence is about screen size. This rule is not a `max-width` hide. It is still `opacity:0` at 860px until `.in` or reduced motion.

### Empty about-panel — still true

`.about-panel` is an empty box: `min-height:260px`, a gradient, a border, no child in the markup. The about renderer always closes the grid with `<div class="about-panel" aria-hidden="true"></div>`. Harbor has that node on About and on Hours. Both sections are `"type": "about"` in `stage/harbor/out/site.json`. The 860px query makes `.about-grid` one column and does not set the panel to `min-height:0` or `display:none`. On a narrow screen the empty 260px box stacks under the copy. The Apple layout page says to put the important items near the top. This box is not content. It still takes 260px after the stack.

### Section scroll-margin — still true, absent

Neither file contains `scroll-margin` or `scroll-padding`. The header is `position:sticky;top:0`, with `.nav` `min-height:64px` plus `padding-top:env(safe-area-inset-top)` and a 1px bottom border. Harbor's in-page links are `#contact`, `#hours`, and `#menu`. At 860px, `section` padding is `48px 0`, which is less than the 64px nav bar before the safe-area padding. The MDN `scroll-padding-top` page names fixed toolbars. This header is sticky, not fixed. Nothing in the CSS offsets the target region by that bar.

## Gaps still true under max-width 860px

At most the ones that are still in the CSS. Not a device log.

1. The hero frame stays `height:168px` for the whole `max-width:860px` range. `320px` and `380px` start at `min-width:861px`. The image is `width:100%` and `height:100%` with `object-fit:cover`, so the 1280 by 720 attributes do not keep the frame at that ratio. The strip gets wider and stays 168px tall up to 860px.

2. `.about-panel` keeps `min-height:260px` after `.about-grid` becomes one column. Harbor renders two of those empty boxes (About and Hours).

3. No `scroll-padding-top` and no `scroll-margin-top`. The sticky header is at least 64px plus the top safe-area padding. Section padding at this breakpoint is 48px. In-page links can scroll their target under that bar. The MDN page cited above is the fixed-toolbar wording; the header here is sticky.

4. `viewport-fit=cover` is set, and MDN says `cover` should use the safe-area variables so important content stays on the display. The sheet reads `safe-area-inset-top` on the header and on the drawer top, and `safe-area-inset-bottom` on the open drawer only. It never reads `safe-area-inset-left` or `safe-area-inset-right`. `.wrap` padding stays `0 24px`. `.site-footer` padding is `32px 0` with no bottom inset. `.skip:focus{top:12px}` does not add the top inset. No `env()` call has a fallback; MDN says an invalid `env()` with no fallback uses the property's initial or inherited value.

5. The 860px block forces one column for `.c2`, `.c3`, `.contact-grid`, and `.about-grid` only. These tracks stay `repeat(auto-fit,minmax(...))` or `repeat(auto-fill,minmax(...))`: `.steps` and `.gallery` 240px, `.pricing` 250px, `.team-grid` 230px, `.quotes` 280px. `.wrap` adds 24px on each side. `280px + 24px + 24px` is 328px, which is wider than a 320px viewport. The web.dev page says a pixel-sized column that does not fit causes horizontal scrolling. Harbor's staged page has no `.quotes` node. The rule is still in the sheet.

6. `.reveal` still starts at `opacity:0` when the 860px query matches. Only `prefers-reduced-motion: reduce` turns that off. Harbor's HTML does not use the class. Other section types in the renderer do.

7. Inside the 860px block, the open `.nav-links` set `gap:0`. The web.dev tap-target page asks for about 8px between targets and about 48px for the target. The drawer links are full width and `min-height:44px`, and the toggle is 44 by 44, so they meet WCAG 2.5.8's 24px AA floor and 2.5.5's 44px AAA size. They do not meet the web.dev 48px or 8px figures. There is no `(any-pointer: coarse)` rule.
