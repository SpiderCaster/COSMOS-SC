# Phone header

Read 2026-10-01. `lib/render.py` was read only and was not edited. Nothing was published. No vendor stylesheet was copied. A property name below is a fact from that file or from a page that opened. It is not a skin to paste.

Phone layout in this file is the block `@media(max-width:860px)` that sets the nav sheet. Two earlier `@media(max-width:860px)` rules only stack `.contact-grid` and `.about-grid`. They do not touch the header.

## What the renderer already emits

Selectors and declarations are from the CSS string in `lib/render.py`.

- `.site-header` is `position:sticky` with `top:0`, and it pads the notch with `padding-top:env(safe-area-inset-top)`. That rule sits outside the 860px block. `.site-header.is-stuck` only swaps the background and shadow after scroll.
- `.nav` uses `flex-wrap:wrap`, with `display:flex`, `align-items:center`, `gap:12px`, and `min-height:64px`. That is the base rule, outside the 860px block.
- `.nav-here` outside the 860px block is already one truncated line: `min-width:0`, `overflow:hidden`, `text-overflow:ellipsis`, `white-space:nowrap`. Inside `@media(max-width:860px)`, `.nav-here` is `display:none`, so the current-section label disappears on a phone.
- `.nav-toggle` is 44px on the base rule: `width:44px` and `height:44px`. The base rule also sets `display:none`. The 860px block shows it with `display:inline-flex`. The link sheet is `.nav-links` inside that same block: `position:fixed`, `display:none` until `.nav-links.open` sets `display:flex`. The sheet is inset with `left:0`, `right:0`, `bottom:0`, and `top:calc(64px + env(safe-area-inset-top))`.

The same 860px block already sets `.nav` to `flex-wrap:nowrap` and `.brand` to `flex:1 1 auto` with `min-width:0`. The current render owner is already changing `.nav` to nowrap. That is a file fact, not the proposal below.

The inline script at the end of the same file writes `.nav-here` from the intersecting `main section` heading (`h1` or `h2`). Hiding the node on a phone throws away a label the script already fills. The brand is one mark: `.brand` plus `.brand-mark`. There is no second logo in this header.

## Public pages

### GOV.UK header

https://design-system.service.gov.uk/components/header/

Opened 2026-10-01. The page calls this the GOV.UK masthead. It tells users they are on a GOV.UK service and gives them GOV.UK-wide tools. A service on `gov.uk/[myservice]`, `[myservice].service.gov.uk`, or `[myblog].blog.gov.uk` must use it at the top of every page. A service that is not on those domains must not use it. The page points that case at the Generic header.

The default header should show only the GOV.UK logo and GOV.UK-wide links and tools. The page says not to add the menu of GOV.UK topic links to the service header. It also says the header is no longer the place for a service name or for navigation links. Those belong in the Service navigation component. The February 2026 row (GOV.UK Frontend v6.0.0) records that the parameters for service name and navigation were removed. One logo stays in the header. Links to sections of the service are a separate surface.

This is a government masthead, not a SpiderCaster skin. Do not copy its markup. The part that applies here is the split: one brand mark in the bar, and the section links somewhere else, not a second logo.

### WCAG 2.5.5 Target Size

https://www.w3.org/WAI/WCAG21/Understanding/target-size.html

Opened 2026-10-01. This is the W3C understanding page for Success Criterion 2.5.5 Target Size, Level AAA, in WCAG 2.1. The criterion says the target for pointer inputs is at least 44 by 44 CSS pixels, except when an equivalent control on the same page is already 44 by 44 CSS pixels, the target is inline in a sentence or block of text, the user agent sets the size and the author does not change it, or a particular presentation is essential.

The intent on that page is that a small target is hard to hit with a tremor, limited dexterity, or a finger. Touch is a coarse pointer. The page says this is sharper on responsive and mobile sites that must work with both a mouse and a touchscreen. The sufficient technique it names is C44: use CSS so targets are at least 44 by 44 CSS pixels.

The phone control already matches that size. `.nav-toggle` is `width:44px` and `height:44px`. The later pass keeps that size. It does not shrink the toggle to make room for the section line.

## One rule for a later renderer pass

Do not publish. Do not add a second logo. Do not restate nowrap. The 860px block already sets `.nav` to `flex-wrap:nowrap`, and the render owner is already changing that.

On a phone (`max-width:860px`), keep `.site-header` sticky with `padding-top:env(safe-area-inset-top)`, keep `.nav-toggle` at 44 by 44 CSS pixels, and keep section links only in the fixed `.nav-links` sheet. Do not set `.nav-here` to `display:none`. Leave the existing one-line truncation on `.nav-here` (`overflow:hidden`, `text-overflow:ellipsis`, `white-space:nowrap`) so the current section stays visible as a single truncated line between the one brand and the toggle.
