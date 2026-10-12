# How a static brochure stays fast

Read 2026-10-01 from the public pages linked under each rule. A number below is that page's number, or a literal in `lib/render.py`. This note did not run Lighthouse, CrUX, or a page load, and it does not claim an LCP, CLS, or byte size for SpiderCaster. No site was built. `lib/render.py` was not edited.

Scope: the single HTML file `render_page` writes. Server cache headers, CDN distance, and TTFB were not read.

## What the renderer already emits

`lib/render.py` says the page is one file: inline CSS, inline JS, a system font stack, inline SVG icons. No external request, no hotlink, no build step.

Shipped:

- The hero picture, when the IR has a relative `src`, is an `<img>` in the first HTML, not a script-built node. Attributes on that tag: `width="1600"`, `height="900"`, `fetchpriority="high"`, `decoding="async"`. It does not set `loading="lazy"`. `htt<local-path>`, `https://`, and `//` hero sources are dropped. The box around it has a CSS height (`168px`, and `320px` or `380px` from the `min-width: 861px` rules).
- CSS is one `<style>` block in `<head>`. There is no `<link rel="stylesheet">`.
- Fonts are `ui-sans-serif, system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`, plus Georgia and Times New Roman for an editorial heading and the letter mark. There is no `@font-face` and no font file URL.
- The only executable script is one inline function at the end of `<body>`. It has no `src`. It is not a framework. It toggles the menu, marks the sticky header, writes the current section title, builds a `mailto:` link, and adds `.in` to `.reveal`.
- `application/ld+json` blocks are also emitted. This note does not score them.

`decoding="async"` is on the hero. None of the pages opened below score that attribute.

## Fast load and LCP

https://web.dev/articles/optimize-lcp (page last updated 2025-03-31)

LCP is the time from the start of the navigation until the largest image or text block in the viewport is rendered. That page's target is an LCP of 2.5 seconds or less for at least 75% of page visits. The figure on the page marks a good value at 2.5 seconds or less and a poor value at greater than 4.0 seconds. Those are the page's targets. They are not a SpiderCaster result.

The same page splits one LCP time into four parts with no overlap: time to first byte, resource load delay, resource load duration, and element render delay. It prints a guideline mix of about 40%, under 10%, about 40%, and under 10%. It says that mix is not a strict rule, and it says not to turn those percentages into millisecond budgets. The two parts with "delay" in the name should be as close to zero as possible. If the LCP element is text in a system font, resource load delay and resource load duration are 0.

Four rules from that page, in its order:

1. The LCP resource starts loading as early as possible. The preload scanner can see an `<img>` whose `src` or `srcset` is in the initial HTML. It cannot see an image created by script, an image whose real URL is in `data-src`, or a CSS background that is not preloaded. Do not put `loading="lazy"` on the LCP image. Hint the likely LCP image with `fetchpriority="high"`. More than one or two high-priority images makes the hint useless. A resource on another origin pays for a new connection. The page's preference is to serve the critical image from the same origin as the HTML. A `<link rel="preload">` is the tool when the image is not an `<img>` in the HTML (a CSS background, or a URL that appears only in an external file).

2. The LCP element can paint as soon as its resource has loaded. A stylesheet blocks rendering of the content that follows it. Inlining the sheet avoids a second request. Inlining is recommended only when the sheet is small, because inlined CSS is not cached for the next page. If the sheet is large, shrink it instead: remove unused CSS, defer non-critical CSS, minify and compress. Do not put a synchronous external script in `<head>`. A script that must run early should be inlined, and only if it is very small. Hiding the LCP element until JavaScript finishes does not get faster when the image gets smaller. The saved time moves into element render delay. Static HTML generated ahead of the request is described as generally better for performance than rendering the application on each request.

3. Shorten the LCP resource load without throwing away quality. The page names three image guides for that: serve the optimal image size, use a modern format, compress. Its own example of a smaller format is AVIF or WebP. For a web font, a `font-display` value other than `auto` or `block` keeps the text visible during the font load, so LCP is not blocked on that request.

4. Send the HTML quickly. Redirect chains and uncached origin trips are the causes it names. This note did not measure that.

Shipped against those rules: hero `<img>` with a same-document relative `src` and `fetchpriority="high"`, no lazy load on that image, no `data-src`, no framework, CSS inlined, no external script in `<head>`, system fonts so a text LCP has no font request. A preload of that same hero URL is not missing. The page uses preload when the scanner cannot see an `<img>`. Adding one here would be a second request for a URL the scanner already has.

## Width and height on images

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img

`height` is the intrinsic height in pixels, an integer with no unit. `width` is the matching intrinsic width. Including both lets the browser compute the aspect ratio before the file loads and reserve the box, which reduces or prevents a layout shift. Both attributes are recommended on every image. They matter more on a lazy-loaded image: until it loads, its used width and height are 0, so content in the viewport can reflow while someone is reading. The same page points at `srcset` and `sizes` as the responsive-image hints.

Shipped on the hero: both attributes are present. They are the literals 1600 and 900 in `hero_visual`, not a value read from the file. CSS then sets that image to `width:100%` and `height:100%` with `object-fit:cover` inside the sized `.hero-visual` box.

Not shipped on a gallery image. The tag is `src`, `alt`, and `loading="lazy"` only. `.tile` sets `aspect-ratio:4/3`, which is a stylesheet box, not the file's pixel size.

## font-display

https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@font-face/font-display (page modified 2026-09-10)

`font-display` is a descriptor on `@font-face`. It controls how text renders while a downloadable font is not ready. The values are `auto` (the user agent decides; this is the initial value), `block`, `swap`, `fallback`, and `optional`. During the block period, text that wants the missing face is drawn with an invisible fallback. During the swap period, text is drawn with a visible fallback, then swapped if the face arrives. `block` is a short block period and an infinite swap period. `swap` is an extremely small block period and an infinite swap period. `fallback` is an extremely small block period and a short swap period. `optional` is an extremely small block period and no swap period. The MDN example uses `fallback`.

The LCP page above is the speed rule: if the LCP resource is a web font, do not use `auto` or `block`, so the text stays visible and LCP is not waiting on the font request.

Shipped. `build_palette` sets system stacks only. The CSS template contains no `@font-face`, so there is no descriptor to set and no font request to block the first text. A later font file would need a value other than `auto` or `block` before this stays true.

## content-visibility

https://web.dev/articles/content-visibility (published 2020-08-05)

This page does recommend the property. `content-visibility: auto` is the value it says gives an immediate improvement. If a large portion of the content is off-screen, skipping layout and paint of those elements makes the initial load faster. Off-screen content stays in the DOM and in the accessibility tree, unlike `visibility: hidden`. The page's own travel-blog demo reports a rendering time from 232ms to 30ms, which it calls a 7x boost, and an expected rendering-cost cut of 50% or more. Those figures are that demo. They are not a SpiderCaster measurement.

The same page says the win needs size containment. Without a height, an off-screen block lays out as empty and can be 0 height, so the scrollbar jumps. The fix it shows is `contain-intrinsic-size` as a placeholder (their example is `1000px` on a story). `contain-intrinsic-size: auto 300px` remembers the last rendered size instead of sticking to the placeholder. It also says a landmark that is `display: none` or `visibility: hidden` can still show up in the accessibility tree while off-screen, and to set `aria-hidden="true"` on those if that clutter matters.

Not in `lib/render.py`. No `content-visibility` and no `contain-intrinsic-size`. For a short brochure the page's own condition (a large off-screen portion) may not hold. Copying the property without a placeholder size is the failure mode the page describes.

## No unused JavaScript

https://docs.astro.build/en/concepts/islands/

Astro's default is to render a UI component to HTML and CSS and strip all client-side JavaScript. The page says that default is what keeps the sites fast and stops unused JavaScript from being sent by accident. Client JavaScript is loaded only for a component marked with a `client:*` directive. It says JavaScript is one of the slowest assets per byte, so every byte counts. The rest of the page stays static HTML.

Shipped: no React, Preact, Vue, Svelte, or other framework runtime. The page is static HTML plus one inline script.

Not shipped: that script is not cut down to the widgets the page has. The menu button and the header exist on every page, so those listeners match a real control. The `mailto` handler and the `.reveal` observer are still in the source when the page has no form and no `.reveal` node.

## Engine gaps still true in lib/render.py

At most these six. Each one is still in the file that was read.

1. Hero `width` and `height` are the constants 1600 and 900, not the file's intrinsic pixels. Gallery images, which are the lazy ones, have neither attribute. MDN's rule is the file's intrinsic size on every image, and especially on a lazy image. CSS does reserve a hero height and a 4/3 tile, so the attributes are not the only box on the page. That CSS box is not a measurement of the file.

2. One `src` per image. No `srcset`, no `sizes`, no `<picture>`, and no second file in a smaller format. `lib/imagine.py` and `lib/hands/__init__.py` do not resize or recompress. The LCP page's load-duration step is a smaller, modern, compressed image (it names AVIF or WebP as the format example). A `.webp` already chosen as the `src` can pass through. The renderer does not make one. Gallery `src` is not run through the hero check, so a remote gallery URL is still emitted. The hero path rejects `htt<local-path>`, `https://`, and `//`.

3. `.reveal` is `opacity:0` until the inline script adds `.in`. That class is on feature cards, steps, gallery tiles, price cards, quotes, and team cards. It is not on the hero. The LCP page's render-delay case is an element kept hidden until JavaScript runs. `prefers-reduced-motion: reduce` forces `.reveal` to `opacity:1` with no transition. A visitor who does not match that query still waits on the script for those blocks.

4. `content-visibility: auto` is not set. The page that recommends it also requires `contain-intrinsic-size` when the skipped region would otherwise be 0 height. The 7x and the 232ms-to-30ms pair belong to that article's demo only.

5. The whole CSS template is inlined on every page, including rules for sections that page does not use. Inlining the sheet is the shipped half of the LCP page's advice (no second request). The other half is still open: unused rules are not removed, and the next HTML file cannot reuse a cached sheet. This note did not measure the sheet.

6. The inline script is one block on every page. Astro's rule is to ship no client JavaScript except the island that needs it. The menu and header code match markup that is always there. The form handler and the reveal observer are not removed when the page has nothing for them to find. This is not a framework bundle. It is still unused script on a page that is only a hero, a menu, and a FAQ.
