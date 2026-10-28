# SEO_STAGE2

Scored on 2026-10-01 after both restage inbox files had a DONE line. Harbor line: `STATUS: DONE`. Demo line: `DONE 2026-10-01`. Neither restage was missing. Read-only. No publish. No HTML, lib, or copy edits. No crew. No --live.

Paths are under `V:\a\Ai\spidercaster\working`. Both `stage/harbor/out/index.html` and `stage/demo/out/index.html` were present.

Checks are yes/no from those two files. A missing `aggregateRating` is correct. Do not add reviews, stars, or rating markup.

## stage/harbor/out/index.html

Title: `Harbor Tea Room`

Description: `A quiet tea room that seats walk-ins by the water.`

| Check | Result |
| --- | --- |
| noindex | yes. `<meta name="robots" content="noindex, nofollow">`. Comment: `SpiderCaster: noindex until approved`. |
| exactly one h1 | yes. One: `Harbor Tea Room`. |
| meta description ends on a sentence | yes. The description ends with `.` |
| rel=canonical | yes. `<link rel="canonical" href="index.html">`. The href is the page filename, not a domain. |
| JSON-LD WebSite | yes. One block, `@type` `WebSite`, `name` and `description` only. `url` is absent. |
| aggregateRating absent | yes. The string `aggregateRating` is not in the file. |
| FAQPage only if the visible page has those questions | yes. No FAQPage block. The visible page has no question list. |
| every img has alt and the file exists beside the html | yes. No `<img>` elements, so none lack alt or a file. |
| no remote URL | yes for assets. No `img` src, `og:image`, stylesheet, or script points off the page. The only absolute URL is JSON-LD `@context` `https://schema.org`. |
| letter mark or a real local image | yes. Hero is a letter mark `H` inside `hero-mark`, `aria-hidden="true"`. `favicon.svg` is beside `index.html`. `assets/` has no image file. The page does not reference `hero.png`. |

## stage/demo/out/index.html

Title: `SpiderCaster: websites from real copy, on free tokens`

Description: `SpiderCaster is a copy-driven static website engine. You give it a brief and real copy files; it returns a self-contained static site.`

| Check | Result |
| --- | --- |
| noindex | yes. `<meta name="robots" content="noindex, nofollow">`. Comment: `SpiderCaster: noindex until approved`. |
| exactly one h1 | yes. One: `SpiderCaster: websites from real copy, on free tokens`. |
| meta description ends on a sentence | yes. The description ends with `.` |
| rel=canonical | yes. `<link rel="canonical" href="index.html">`. The href is the page filename, not a domain. |
| JSON-LD WebSite | yes. One block, `@type` `WebSite`, `name` and `description` only. `url` is absent. |
| aggregateRating absent | yes. The string `aggregateRating` is not in the file. |
| FAQPage only if the visible page has those questions | yes. A second block is `@type` `FAQPage` with five questions. The same five questions and the same answer text are in the visible `#faq` details. |
| every img has alt and the file exists beside the html | yes. No `<img>` elements, so none lack alt or a file. |
| no remote URL | yes for assets. No `img` src, `og:image`, stylesheet, or script points off the page. The only absolute URL is JSON-LD `@context` `https://schema.org`, once on WebSite and once on FAQPage. |
| letter mark or a real local image | yes. Hero is a letter mark `S` inside `hero-mark`, `aria-hidden="true"`. `favicon.svg` is beside `index.html`. No image file is referenced. |

## Left as they are

`aggregateRating` stays absent on purpose. Do not add reviews, stars, or rating markup to either staged page. Both pages stay noindex. This note does not publish.
