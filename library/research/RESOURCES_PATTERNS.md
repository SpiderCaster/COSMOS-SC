# Header, hero, and favicon resources

Date: 2026-10-01. Method: the pages below were opened. Search snippets were not used as the citation. `library/research/PATTERN_SOURCES.md` was read first. Its table is not repeated. None of the URLs below are in that table.

Squarespace Help, "Build your site header" (`https://support.squarespace.com/hc/en-us/articles/360000667707-Build-your-site-header`), opened as a title-only shell. No article body. Not used.

Shopify names below are section names and one sticky setting from public JSON or from a docs page that names the theme files. Theme CSS and Liquid were not opened. No theme zip.

Do not ship their HTML/CSS.

## Sources

### `position: sticky`

Title: position CSS property.  
URL: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position

A sticky element stays in normal flow until its containing block crosses a threshold, then it is stuck. At least one inset, such as `top`, must be a value other than `auto`, or that axis behaves as relative. It sticks to the nearest ancestor that has a scrolling mechanism (`overflow` of `hidden`, `scroll`, `auto`, or `overlay`), even when that ancestor is not the one actually scrolling.

Do not ship their HTML/CSS.

### Viewport meta

Title: `<meta name="viewport">`.  
URL: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/viewport

The page's recommended tag is `width=device-width`. It says `initial-scale=1` is often unnecessary, and that locking zoom with `user-scalable=no` blocks low-vision readers. `viewport-fit=cover` fills a notched display, and the page says to use the safe-area inset variables so important content stays on screen. Without a viewport tag, some mobile browsers lay out at about 980px and shrink the page.

Do not ship their HTML/CSS.

### `prefers-reduced-motion`

Title: prefers-reduced-motion CSS media feature.  
URL: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion

When the visitor has asked the device to reduce motion, non-essential animation should be removed, reduced, or replaced. Scaling and panning of large objects are called out as vestibular triggers. The value to test is `reduce`. The page's example replaces a scale animation rather than leaving it running.

Do not ship their HTML/CSS.

### Link icon

Title: rel HTML attribute.  
URL: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel

`rel="icon"` on a `link` is the favicon. If several icons are listed, the browser picks using `media`, `type`, and `sizes`, uses the last one when they tie, and tries the next if a format is unsupported. The page says iOS does not use `rel="icon"` for a home-screen icon. It uses `apple-touch-icon`. The `shortcut` token is non-conforming and must not be used.

Do not ship their HTML/CSS.

### Tap targets (web.dev)

Title: Accessible tap targets.  
URL: https://web.dev/articles/accessible-tap-targets

Opened page, last updated 2020-03-31. It recommends about 48 device-independent pixels on a site with a proper mobile viewport, and about 8 pixels of space between targets. A 24px icon is the example of a graphic that is too small until padding brings the target up to 48px. It also says to enlarge targets for a coarse pointer, not only for a narrow viewport. This page does not say 24px is the minimum target.

Do not ship their HTML/CSS.

### Responsive images (web.dev)

Title: Responsive images.  
URL: https://web.dev/learn/design/responsive-images

Opened page, last updated 2021-12-09. Constrain images so they cannot be wider than the container, keep the aspect ratio, and use `object-fit: cover` plus `object-position` when a crop must keep the subject. Put `width` and `height` on the image so the layout does not jump. Do not lazy-load a hero that is above the fold. Set `fetchpriority="high"` only on an image that is truly the main one. Offer `srcset` and `sizes` so a small screen does not download the large file. Decorative images use an empty `alt`. A missing `alt` is not the same thing.

Do not ship their HTML/CSS.

### Tap targets (Chrome)

Title: Tap targets are not sized appropriately.  
URL: https://developer.chrome.com/docs/lighthouse/seo/tap-targets

Opened page, last updated 2019-05-02. This Lighthouse SEO audit flags a target only when it is smaller than 48 by 48 px and at least 25 percent of the area within 48 px of its center overlaps another target. A target that is 48 by 48 px never fails that audit. Spacing of 8 px is called a starting point, not a guarantee. Same note as web.dev: 24px is not the size this page uses.

Do not ship their HTML/CSS.

### Contrast 4.5:1

Title: Understanding Success Criterion 1.4.3 Contrast (Minimum).  
URL: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

Level AA. Text needs a contrast ratio of at least 4.5:1. Large-scale text, about 18pt (24px) or 14pt bold (about 18.5px), needs at least 3:1. Do not round 4.499 up to 4.5. Logos are exempt. Text that is only brand color, and is not a logo, is not exempt. The ratio is between the text color and the background color in the stylesheet, not a screenshot.

Do not ship their HTML/CSS.

### Target size 24px (WCAG AA)

Title: Understanding Success Criterion 2.5.8 Target Size (Minimum).  
URL: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html

Level AA, WCAG 2.2. The target is at least 24 by 24 CSS pixels, unless spacing, an equivalent control, inline text, a user-agent control, or an essential presentation applies. The page says 24px is a minimum, that tiny targets can still pass if nothing is adjacent, and that important controls should aim at the stricter 44px criterion below. This is the page that states 24px. The web.dev and Chrome pages opened above still say about 48px.

Do not ship their HTML/CSS.

### Target size 44px (WCAG AAA)

Title: Understanding Success Criterion 2.5.5 Target Size (Enhanced).  
URL: https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html

Level AAA. Custom targets are at least 44 by 44 CSS pixels, with exceptions for an equivalent larger control, inline text, user-agent sizing, and essential presentation. The page says larger than 44 is better for frequent controls, controls that are hard to undo, and controls near the screen edge.

Do not ship their HTML/CSS.

### Dawn and Horizon header names

Title: Dawn `sections/header-group.json` and Horizon `sections/header-group.json` (public raw JSON, names only).  
URLs: https://raw.githubusercontent.com/Shopify/dawn/main/sections/header-group.json and https://raw.githubusercontent.com/Shopify/horizon/main/sections/header-group.json

Dawn's header group, in order, is the section types `announcement-bar` then `header`. The header's sticky setting in that file is `on-scroll-up`. Horizon's header group, in order, is the section types `header-announcements` then `header`. The header's blocks are `_header-logo` and `_header-menu`. Horizon's sticky setting in that file is `always`. The idea to copy is a short announcement, then a header that can stay available, not their settings object.

Do not ship their HTML/CSS.

### Dawn and Horizon hero names

Title: Don't use CSS background-image for LCP content.  
URL: https://shopify.dev/docs/storefronts/themes/best-practices/performance/avoid-background-images-hero

The page says a homepage hero that is the largest first paint should be an `img` in the HTML, not a CSS background, so the browser can discover it while parsing. The first hero is eager and may use high fetch priority. Later copies of that section can be lazy. It names Dawn's image-banner stylesheet and Horizon's `hero` section as the themes that cover the hero with that image and stack the text above it. Those theme files were not opened.

Do not ship their HTML/CSS.

### Wix header

Title: Wix Editor: Customizing Your Site Header.  
URL: https://support.wix.com/en/article/wix-editor-customizing-your-site-header

The header is the top strip with the menu and logo, and it repeats across pages. Design it in two states, regular and scroll, so color, border, or shadow can change after the visitor scrolls. Scroll behavior on this page is one of four: scrolls away with the page, freezes and stays on top, disappears until the visitor scrolls up, or fades out and returns near the top. The freeze tip is to keep that bar short so it does not cover the page.

Do not ship their HTML/CSS.

## Already shipped

Read from `lib/render.py`. These match the notes above and are not gaps.

- The header is `position: sticky` with `top: 0`. After 8px of scroll it gets `is-stuck`, a solid background, and a shadow. That is the Wix regular-versus-scroll idea, and it matches Horizon's "always" rather than Dawn's "on-scroll-up".
- The viewport tag sets `width=device-width` and `initial-scale=1`. Zoom is not locked.
- `favicon.svg` is linked as `rel="icon"` with an SVG type, and again as `apple-touch-icon`.
- `prefers-reduced-motion` already turns off the reveal motion, smooth scrolling, and the header's color transition.
- The homepage hero is a real `img` with `object-fit: cover` when a local image is set, or a letter mark when it is not. It is not a CSS background.
- Nav links, the menu button, and hero buttons are at least 44px. That meets the WCAG 2.5.5 page and is above the 24px AA page. The mobile menu is a full-screen layer, `nav-open` stops the page from scrolling behind it, and the header and menu use `safe-area` padding. Root type is 18px.

## Gaps versus current SpiderCaster

1. Accent text on buttons is chosen by a luminance split at 0.5, not by a 4.5:1 test. Using the luminance function already in `lib/render.py`, white on several built-in accents is under 4.5:1, and some are under 3:1 (`#818cf8` about 3.0, `#f472b6` about 2.7, `#0ea5e9` about 2.8, `#6366f1` about 4.5 only if rounded). Button labels are 18px, which is below the large-text size on the contrast page. Body text and the muted pairs checked (`#9aa7b8` on `#0a0e14`, `#5c6572` on `#f7f8fa`) are above 4.5:1.

2. The hero `img` has no `width` or `height`, no `srcset` or `sizes`, and no `fetchpriority`. The crop is `object-fit: cover` with no `object-position`. On a narrow screen the frame is a fixed 168px card, so the subject can be cut off and the file is not chosen for the slot.

3. Safe-area padding is already on the header and the mobile menu, but the viewport tag does not set `viewport-fit=cover`. The viewport page says those insets are how a covered, notched screen keeps content visible. Without that hint the insets often stay zero, so the padding does nothing on a notch.

4. Reduced motion does not stop the button or card hover transforms. Those are still movement after the visitor has asked for less.

5. The brand home link and the footer links have no minimum size. The web.dev and Chrome pages opened here still describe about 48 CSS pixels, with about 8 pixels of space. The 44px nav, menu button, and hero buttons are already shipped and are not this gap.
