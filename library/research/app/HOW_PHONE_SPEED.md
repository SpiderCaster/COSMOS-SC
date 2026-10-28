# How a small static page stays fast on a phone

Read 2026-10-01. Public pages only. `lib/render.py` was read and not edited. No page was loaded, and no Lighthouse or CrUX number was taken. A number below is from a page that opened, or from that file. This note does not claim an LCP, CLS, or INP for SpiderCaster.

## Sources

All four requests returned a public page. None is marked "not public".

- https://web.dev/articles/lcp — opened. The page says last updated 2025-09-04.
- https://web.dev/articles/cls — opened. The page says last updated 2023-04-12.
- https://web.dev/articles/inp — opened. The page says last updated 2025-09-02.
- https://developer.mozilla.org/en-US/docs/Web/CSS/content-visibility — opened. The text returned is the MDN property page at https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/content-visibility. That page says it was last modified on Jul 26, 2026.

## What those pages say

### Largest Contentful Paint

https://web.dev/articles/lcp

LCP is the render time of the largest image, text block, or video visible in the viewport, counted from when the user navigated. A good score is 2.5 seconds or less. The page says to judge that at the 75th percentile of page loads, split by mobile and desktop. The figure caption on the page states the good value and does not state a poor cutoff in the text that was returned.

Elements that can win are an `img` (first frame for an animated image), an `image` inside an `svg`, a `video` (poster or first frame, whichever is earlier), an element with a CSS `url()` background, and a block that contains text. An element with opacity 0 is excluded because the user cannot see it. An element that covers the whole viewport can be treated as background rather than content. A low-entropy placeholder image can be excluded too.

For an image resized away from its intrinsic size, the reported size is the visible size or the intrinsic size, whichever is smaller. Margins, padding, and borders are not part of the size. Only the element's first size and position in the viewport count. A later move does not create a new candidate.

Text that is waiting on a web font during the font block period is not treated as rendered yet. A smaller element can be reported until the larger one actually paints. On a phone, the thing in the first screen is usually the hero picture or the heading. If that picture is late, or the heading is invisible, LCP waits.

### Cumulative Layout Shift

https://web.dev/articles/cls

CLS is the largest burst of unexpected layout-shift scores over the life of the page. A burst is a session window: shifts less than 1 second apart, and the window lasts at most 5 seconds. A good score is 0.1 or less. Poor is greater than 0.25. The same 75th percentile, split by mobile and desktop, is the threshold the page names.

The page names three common causes: images or videos with unknown dimensions, a font that renders larger or smaller than its fallback, and third-party ads or widgets that resize themselves. The score is impact fraction times distance fraction. In the page's first worked example, the impact fraction is 0.75 and the distance fraction is 0.25, so the score is 0.1875.

A shift within 500 milliseconds of user input can be flagged `hadRecentInput` and left out. A picture that arrives with no reserved box is not that case. The person is reading, and the text moves. The page says to animate with `transform` rather than by changing height, width, or the top, right, bottom, or left offsets, and to respect `prefers-reduced-motion`.

On a phone the viewport is the whole layout. An unreserved hero is a large fraction of that viewport, so one jump is a large score.

### Interaction to Next Paint

https://web.dev/articles/inp

The page says Chrome usage data shows that 90% of a user's time on a page is spent after it loads. INP watches click, tap, and keypress for the whole visit. The value is the longest interaction, except that one worst interaction is ignored for every 50 interactions. Scrolling and hovering are not counted. A good score is 200 milliseconds or less. Above 200 milliseconds and at or under 500 milliseconds needs improvement. Above 500 milliseconds is poor. Again the page uses the 75th percentile, split by mobile and desktop.

A tap on a phone is pointer events plus a click. The latency is input delay, then event-handler time, then the wait until the next paint. The page says long tasks on the main thread are a cause of input delay. The metric is not the later network work. It is how long the next paint is blocked. A small static page stays fast when the main thread is not busy at the moment of the tap.

### content-visibility

https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/content-visibility

`content-visibility` lets the browser skip an element's layout and paint until that work is needed. The page says that can make the initial load much faster. `visible` is the initial value and changes nothing. `hidden` skips the contents and takes them out of find-in-page and tab order. `auto` turns on layout, style, and paint containment, and skips contents that are not relevant to the user, while leaving them available to find-in-page, tab order, focus, and the accessibility tree.

The page's long-page example puts `auto` on each `section`, with `contain-intrinsic-size: auto 500px` so an off-screen section still has a 500px placeholder. After a section has been rendered, the page says it keeps that rendered size. Without a placeholder size, the off-screen block can collapse and the scrollbar jumps. The same example says the skip helps both load and interactions. The property is not a win for a short page whose sections are already on screen. Baseline on that page is 2024, newly available since September 2024, and it may be missing on older phones.

## What `lib/render.py` already does

`render_page` builds one string, `css = CSS_TEMPLATE.substitute(pal)`, and places it in a single style element:

```
<style>
{css}
</style>
```

There is no second style element and no `link` with `rel="stylesheet"`. That is the one inlined CSS block.

Hero width and height come from the section data, and only when both are positive:

```
w, h = int(d.get("image_w") or 0), int(d.get("image_h") or 0)
box = f' width="{w}" height="{h}"' if w > 0 and h > 0 else ""
```

`hero_visual` then writes one `img` with that `box`, plus `fetchpriority="high"` and `decoding="async"`. If either number is missing or not positive, the attributes are omitted. `image_box` can read a PNG or JPEG header, but nothing in this file calls it, so the tag does not measure the file itself.

The hero source is one local path. `_local_image_src` returns the string only when it does not start with `http://`, `https://`, or `//`. Otherwise it returns `""`, and `hero_visual` draws a letter mark instead of an `img`.

There is no `srcset` and no `sizes` on that tag, or anywhere else in the file. There is no `content-visibility`.

Fonts are assigned, not downloaded. `build_palette` sets `font_body` to `ui-sans-serif, system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`. `font_head` is that same stack, or Georgia and Times New Roman when the template is editorial. The CSS template has no `@font-face` and no font-file URL.

`.reveal` does start at opacity 0. The phone rule inside `@media(max-width:860px)` sets the same selector back to opacity 1. These are the only two CSS lines quoted in this note:

```
.reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.reveal{opacity:1;transform:none}
```

The reduced-motion block also forces `.reveal` visible and drops its transition. The inline script still adds the class `in` when an observed `.reveal` intersects, or immediately when `IntersectionObserver` is missing. The hero section itself does not use the class `reveal`. Later cards do.

The viewport meta is `width=device-width, initial-scale=1, viewport-fit=cover`.

## Allowed changes

| change | why it helps a phone | already in render.py (yes/no) |
| --- | --- | --- |
| set width and height | The CLS page says an image with unknown dimensions moves other content. On a small viewport that move is a large share of the screen. The attributes are written only when `image_w` and `image_h` are both positive. | yes |
| keep one local image | LCP is the largest image or text in the viewport. `hero_visual` emits one `img`, and only for a relative source. A second picture is another download before that paint. | yes |
| sizes="100vw" on the hero | None of the four opened pages name this attribute. The LCP page says a resized image is scored by the smaller of its visible size and its intrinsic size. On a phone the hero is the viewport width, so the attribute would say that. This file has no `srcset`, so the attribute would not choose a second file. | no |
| do not start .reveal at opacity 0 | The LCP page excludes an element whose opacity is 0, so a hidden start cannot be the largest content until something paints it. The base rule still starts at opacity 0. The max-width 860px rule sets opacity 1, so a phone does not keep the hidden start. | yes |
| skip content-visibility until a section is long | MDN says `auto` skips layout and paint for content that is not relevant, which speeds the first load and helps interactions, and that a long page is the case it shows. The same page uses a 500px placeholder so the scrollbar does not jump. A short page has little off-screen work to skip. The property is absent here. | yes |
| do not add a web font | The LCP page says text is not rendered during the web-font block period, so a smaller element can win until the face arrives. The CLS page says a face that is larger or smaller than the fallback shifts the page. The assigned stacks are already on the phone, and this file has no font-file URL. | yes |
