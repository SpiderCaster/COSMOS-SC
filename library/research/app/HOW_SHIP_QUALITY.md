# How a static brochure page ships

Read 2026-10-01. Public rules are paraphrased next to the page that states them. A number appears here only when that page states it. File scores are only what is in `stage/harbor/out/index.html` and `stage/demo/out/index.html`. Both files exist. No site was built. No HTML or CSS from those pages, or from the public examples, is copied here as an implementation.

Scope: one static brochure home page, the shape SpiderCaster already renders.

## Title

Google uses the `<title>` element, the main visual title, heading elements such as `<h1>`, the `og:title` meta tag, other large prominent text, other text on the page, anchor text on the page, text in links that point at the page, and `WebSite` structured data. Google may rewrite the title. There is no length limit. The title link is truncated to fit the device. https://developers.google.com/search/docs/appearance/title-link

That page also says: every page has a `<title>`; the text is descriptive and concise; avoid vague labels such as "Home" or "Profile"; avoid keyword stuffing and boilerplate that is the same on every page; the home page is a reasonable place for a longer brand line; other pages should put the site name at the start or the end, with a hyphen, colon, or pipe; one main title should be visually obvious, for example a larger font and the title text in the first visible `<h1>`; use the same language and writing system as the primary content. https://developers.google.com/search/docs/appearance/title-link

A character cutoff, including 60, is **not public** on that page.

## Description

Google builds the snippet from the page content. It sometimes uses `<meta name="description">` when that text describes the page better than the body. There is no length limit. The snippet is truncated to the device. The same page can get different snippets for different queries. https://developers.google.com/search/docs/appearance/snippet

That page also says: unique description per page; a site-level description belongs on the home page; summarize that page (a shop example includes what is sold, hours, and location); a keyword list is the bad example; programmatic descriptions are fine when they stay human-readable and use page-specific facts. To suppress a snippet, `nosnippet`. To cap length, `max-snippet`. To keep a region out of the snippet, `data-nosnippet`. https://developers.google.com/search/docs/appearance/snippet

A character cutoff is **not public** on that page. The opened snippet page does not name `og:description` as a snippet source. **not public** there.

## Target size

WCAG 2.2 success criterion 2.5.8 Target Size (Minimum), level AA: the target for pointer inputs is at least 24 by 24 CSS pixels, unless spacing, an equivalent control, inline text, an unmodified user-agent control, or an essential presentation applies. Undersized targets can still pass if a 24 CSS pixel diameter circle centered on each bounding box does not intersect another target or another such circle. A 24 by 24 square has to fit inside the target. Zoom does not change the CSS pixel size. https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html

That page points at 2.5.5 as the stricter criterion. It does not state 44 there.

WCAG 2.2 success criterion 2.5.5 Target Size (Enhanced), level AAA: the target is at least 44 by 44 CSS pixels, unless an equivalent 44 by 44 control, inline text, an unmodified user-agent control, or an essential presentation applies. https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html

24 is the AA number. 44 is the AAA number. Neither page was checked in a browser render of these two files.

## Contrast

WCAG 2.2 success criterion 1.4.3 Contrast (Minimum), level AA: text and images of text have a contrast ratio of at least 4.5:1. Large-scale text (at least 18 point, or 14 point bold) and images of that text need at least 3:1. Incidental text, text that is not visible, text in a picture that has other visual content, and text in a logo or brand name have no contrast requirement. Do not round a computed ratio up: 4.499:1 does not meet 4.5:1. The ratio is (L1 + 0.05) / (L2 + 0.05) from the relative luminance on that page. 14pt and 18pt are about 18.5px and 24px (`1pt = 1.333px`). Evaluate the colors in the markup, not the anti-aliased pixels. https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

The same page says an uppercase X or a `>` used as a symbol is non-text, and a ratio just above 3:1 passes success criterion 1.4.11 for that kind of mark. https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

7:1 is named on that page as the level AAA ratio in success criterion 1.4.6. It is not the AA bar.

## Skip link

MDN: a skip link is placed as early as possible in `body`, points at the start of the main content, and is usually hidden offscreen until it is focused. The link text in that example is "Skip to main content". It lets keyboard users bypass header navigation that repeats on every page. That matters for switch control, voice command, and mouth sticks or head wands, where walking repeated links is laborious. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a#skip_links

The same idea is on the MDN accessibility how-to: a skip link jumps over the navigation to the main content. The link text in that example is "Skip to content". https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Design_and_accessibility/HTML_features_for_accessibility

MDN on images, same how-to: every image has an `alt` attribute. Decorative images use an empty `alt`. Any other image uses alt text that describes the image for someone who cannot see it. https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Design_and_accessibility/HTML_features_for_accessibility

## Sticky header

Bootstrap's navbar placement pattern: a navbar can be fixed to the top, fixed to the bottom, stickied to the top, or stickied to the bottom. Sticky to the top scrolls with the page until it reaches the top, then stays there. The class in that example is `sticky-top`. Fixed placement uses `position: fixed`, leaves normal flow, and may need custom CSS such as `padding-top` on `body` so it does not cover other elements. That overlap sentence is about fixed, not sticky. https://getbootstrap.com/docs/5.3/components/navbar/#placement

The same page says a navbar toggler button in its examples carries `aria-expanded`, `aria-controls`, and `aria-label="Toggle navigation"`. https://getbootstrap.com/docs/5.3/components/navbar/#placement

## What the staged files do

Scored 2026-10-01 from the two `index.html` files only. Not a browser render. Not a new build.

### Title and description

Harbor `<title>` is `Harbor Tea Room`. The first visible `h1` is the same string. `og:title` is the same string. The meta description is `A quiet tea room that seats walk-ins by the water.` That sentence is also the hero lede. `html` is `lang="en"`.

Demo `<title>` is `SpiderCaster: websites from real copy, on free tokens`. The first visible `h1` is the same string. `og:title` is the same string. The meta description is `SpiderCaster is a copy-driven static website engine. You give it a brief and real copy files; it returns a self-contained static site.` Those two sentences are the start of the hero lede. `html` is `lang="en"`.

Neither title is "Home". Neither description is a keyword list. Google's pages state no length cutoff, so none is applied here.

### Skip link

Not present on either page. The word skip does not appear. `main` is present on both and has no `id`, so nothing can point at it.

### Focusable controls

Neither file sets `tabindex`. Neither file sets `outline: none`. The only author `:focus` rule is on `.form input` and `.form textarea`. Neither page contains a form, so that rule matches nothing in these documents. Links, the menu button, and `summary` have no author focus rule. This note does not claim the user-agent ring is gone.

Harbor, in source order:

- Link, class `brand`, visible name `Harbor Tea Room`. The letter H is `aria-hidden`.
- `button`, class `nav-toggle`, accessible name `Menu` (`aria-label`). The icon is `aria-hidden`. `aria-expanded="false"` and `aria-controls="site-nav"`. The stylesheet sets `display: none` until `max-width: 860px`, then `display: inline-flex`, with `width: 44px` and `height: 44px`.
- Three nav links: `Contact`, `Hours`, `Menu`. Each has `min-height: 44px`. Under 860px the nav is `display: none` until it has class `open`.
- One hero link, class `btn`, text `Contact`, `href="#contact"`, `min-height: 44px` on `.btn`.
- No `summary`. No footer link. `.foot-links` is empty. The phone and the street are `span` text, not links.

Demo, in source order:

- Link, class `brand`, visible name `SpiderCaster: websites from real copy, on free tokens`. The letter S is `aria-hidden`.
- The same `Menu` button, with the same 44 by 44 CSS pixel box when it is displayed.
- Six nav links, text equal to the six `h2` strings: `Build`, `Iterate`, `Gate and preview`, `House rules the engine enforces`, `Questions about the engine`, `Why it is cheap`. Same `min-height: 44px` and the same narrow-screen hide.
- One hero link, class `btn`, text `Build`, `href="#features"`.
- Five `summary` elements. Each shows the question as its text: `Does the offline build really cost zero tokens?`, `What does an AI build cost?`, `Can the AI invent content?`, `How do I change something without tokens?`, `How does this fit the fleet checks?`
- No footer link. `.foot-links` is empty.

`.brand` also sets `min-height: 44px`. Those declared boxes are at least 24 by 24 CSS pixels in one dimension (the height, or both axes on the menu button). Width of a short nav label was not measured. `summary` has `padding: 16px 18px` and no `min-height`. Its used box was not measured, so it is not scored against 24 or 44.

Both files set `.site-header` to `position: sticky` and `top: 0`. That is the sticky-top behavior on the Bootstrap page, not `position: fixed`. `.nav` sets `min-height: 64px`. The header also adds `padding-top: env(safe-area-inset-top)`. In-page links are fragment hrefs. Neither file sets `scroll-margin`.

### Heading order

Harbor: one `h1` (`Harbor Tea Room`), then a section with a paragraph and no heading, then `h2` `Contact`, `h2` `Hours`, `h2` `Menu`. No `h3` or lower. No level is skipped.

Demo: one `h1` (the title string), then a section with a paragraph and no heading, then `h2` `Build` with four `h3` command lines, `h2` `Iterate` (the two command lines are `b`, not headings), `h2` `Gate and preview` (same, `b` not headings), `h2` `House rules the engine enforces` with four `h3`s, `h2` `Questions about the engine` (the questions are `summary`, not headings), `h2` `Why it is cheap` with five `h3`s. No `h4` or lower. No level is skipped. The `h3` elements follow an `h2` in the same section.

### Button labels

Each page has one `button`. Its accessible name is `Menu`. It is not empty. The hero actions are links with visible text, `Contact` on harbor and `Build` on demo, not buttons.

### Image alt

Harbor has one `img`. Its `alt` is `Harbor Tea Room`, the same string as the `h1` and the `<title>`. It is not empty. The file does not contain a separate caption for that image.

Demo has no `img`. The hero mark is a `span` with `aria-hidden="true"`, not an image, so it has no `alt`. The favicon is a `link`, not an `img`.

### Contrast of the colors those files declare

Computed from the hex in the stylesheets with the sRGB formula on the contrast page above. Not a screenshot. `html` sets `font-size: 18px`, so `1rem` is 18px, which is under the page's about-18.5px line for 14pt bold.

| Pair | Where | Ratio | Against 4.5:1 |
| --- | --- | --- | --- |
| `#e9eef6` on `#0a0e14` | `--text` on `--bg`. Both pages. | 16.60:1 | meets |
| `#e9eef6` on `#111722` | `--text` on `--surface`. Both pages. | 15.41:1 | meets |
| `#9aa7b8` on `#0a0e14` | `--muted` on `--bg`. Lede, about, footer. Both pages. | 7.91:1 | meets |
| `#9aa7b8` on `#111722` | `--muted` on `--surface`. Card text, and demo answer text. | 7.35:1 | meets |
| `#ffffff` on `#2a6f8f` | Harbor button label on `--accent` | 5.57:1 | meets |
| `#ffffff` on `#6b4c3b` | Demo button label on `--accent` | 7.71:1 | meets |
| `#2a6f8f` on `#0a0e14` | Harbor `.mi-price` (`$4.50`, `$3.75`, `$3.25`), weight 700, size `1rem` | 3.47:1 | under 4.5:1 |
| `#6b4c3b` on `#111722` | Demo `summary::after` glyph `+` on the `details` surface | 2.33:1 | under 3:1 as a symbol |

Harbor has no `summary`, so the `+` glyph is not on that page. Demo has no `.mi-price`, so the accent price color is not on that page. Decorative icons are `aria-hidden` and are not scored as text.

## Engine changes

At most six. They use text the page already has, or a control name taken from the MDN skip-link example. They do not add a review, a rating, a slogan, a caption, a street, or a phone number.

1. Put a skip link as early as possible in `body`, hidden offscreen until focused, with the MDN label `Skip to main content`, pointing at `main`. Give `main` an id. Neither staged page has this, and `main` has no id. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a#skip_links

2. Give `a`, `button`, and `summary` an author `:focus-visible` outline, and keep the skip link onscreen while it is focused. Do not set `outline: none`. The only author focus rule in these files matches form fields, and neither page has a form. Use `--text` on `--bg` (16.60:1 above), not `--accent`.

3. Paint price text and the disclosure `+` in `--text`, which already clears 4.5:1 on `--bg` and on `--surface`. Leave the button as white on `--accent`; those two pairs clear 4.5:1 (5.57:1 and 7.71:1). Do not invent a new palette. Harbor prices at 3.47:1 fail the 4.5:1 text bar. The demo `+` at 2.33:1 is under the 3:1 the contrast page cites for a symbol. https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

4. If the copy has no image description, set `alt=""` on the image. Do not copy the `h1` into `alt`, and do not write a caption. Harbor's only `img` uses the title string as `alt`. Demo has no `img` and needs no alt. https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Design_and_accessibility/HTML_features_for_accessibility

5. Keep the header `position: sticky; top: 0`, which is the sticky-top pattern, not fixed. Do not switch it to fixed unless `body` also gets the padding that page names. Add a fragment offset of at least the header block (`.nav` is `min-height: 64px`, plus the safe-area padding already on the header) so `#contact`, `#features`, and the other in-page targets are not covered. Neither file sets `scroll-margin`. https://getbootstrap.com/docs/5.3/components/navbar/#placement

6. Leave heading order as it is: one `h1`, then `h2`, then `h3` only under an `h2`. Do not insert a heading for the untitled paragraph between the `h1` and the first `h2`. That paragraph has no heading in either file, and no level is skipped. Keep `<title>` and the meta description equal to the visible `h1` and a visible sentence, which both files already do. Do not write a second pitch. https://developers.google.com/search/docs/appearance/title-link https://developers.google.com/search/docs/appearance/snippet
