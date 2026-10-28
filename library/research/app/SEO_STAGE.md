# SEO_STAGE

Scored after a three-minute wait on 2026-10-01. Read-only. No publish. No page or engine edits. No crew.

Paths are under `V:\a\Ai\spidercaster\working`. Both folders were present. Neither page is missing.

Checks are yes/no from the HTML only. A missing `aggregateRating` is correct. Do not add reviews, stars, or extra keywords to clear a gap.

## stage/harbor/out/index.html

Title: `Harbor Tea Room`

Description: `A quiet tea room that seats walk-ins by the water.`

| Check | Result |
| --- | --- |
| noindex (required while staged) | yes. `<meta name="robots" content="noindex, nofollow">`. Comment: `SpiderCaster: noindex until approved`. |
| exactly one h1 | yes. One: `Harbor Tea Room`. |
| non-empty meta description | yes. The string above is a finished sentence. |
| rel=canonical | no. No `<link rel="canonical">`. |
| json-ld WebSite, and no aggregateRating | no. No `application/ld+json` and no `WebSite` object. `aggregateRating` is absent, which is correct. |
| every img has alt | yes. One image: `<img src="assets/hero.png" alt="Harbor Tea Room" ...>`. |
| no remote img or og:image URL | yes. The image src is relative. No `og:image`. No `http://` or `https://` in the file. |
| title contains the brand | yes. Title is the brand `Harbor Tea Room`. |
| lang attribute | yes. `<html lang="en">`. |

## stage/demo/out/index.html

Title: `SpiderCaster: websites from real copy, on free tokens`

Description: `SpiderCaster is a copy-driven static website engine. You give it a brief and`

| Check | Result |
| --- | --- |
| noindex (required while staged) | yes. `<meta name="robots" content="noindex, nofollow">`. Comment: `SpiderCaster: noindex until approved`. |
| exactly one h1 | yes. One: `SpiderCaster: websites from real copy, on free tokens`. |
| non-empty meta description | yes. The string is non-empty. It is not a finished sentence. |
| rel=canonical | no. No `<link rel="canonical">`. |
| json-ld WebSite, and no aggregateRating | no. No `application/ld+json` and no `WebSite` object. `aggregateRating` is absent, which is correct. |
| every img has alt | yes. Zero `<img>` elements, so none lack alt. |
| no remote img or og:image URL | yes. No `<img>`, no `og:image`, no `http://` or `https://`. Hero is a text mark `S` with `aria-hidden="true"`. |
| title contains the brand | yes. Title begins with `SpiderCaster`. |
| lang attribute | yes. `<html lang="en">`. |

## Engine gaps visible in the HTML

At most five. These are holes in what the renderer emits. They are not a request to stuff keywords or to invent reviews.

1. The head never emits `<link rel="canonical">` on either page.
2. The head never emits JSON-LD. A `WebSite` object is missing on both pages. `aggregateRating` is also missing. Leave ratings out.
3. Open Graph stops at `og:title`, `og:description`, and `og:type`. There is no `og:url` and no `og:image`. Remote image URLs are correctly absent. Harbor's only image stays a relative `assets/hero.png`. Demo emits no image.
4. A non-empty description can still be cut mid-clause. On demo, the meta description, `og:description`, and the hero lede all end at `You give it a brief and`. The About body is the next three source lines as separate paragraphs, and the last one stops at `the Gemini`.
5. FAQ copy is only `<details>` and `<summary>`. There is no machine-readable FAQ object. Do not fill that hole with `aggregateRating` or review markup.
