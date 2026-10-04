# How a static brochure page states SEO in HTML

Read 2026-10-01 from public Google Search Central and MDN. A rule is paraphrased next to its URL. If the opened page does not say the rule, this file says **not public**. No site was built. Nothing here is a ranking trick beyond those pages.

Scope: one static brochure, a home page plus a few HTML files, the shape SpiderCaster already renders. Not a shop, a news site, or a video site.

Google's starter guide says useful, original, up-to-date copy matters more than the other suggestions on that page. It also says Google Search does not use the keywords meta tag, keyword stuffing is spam, and there is no magical word-count target. https://developers.google.com/search/docs/fundamentals/seo-starter-guide

## Title

Google uses several sources for the title link. The ones named on the title-link page are: the `<title>` element, the main visual title, heading elements such as `<h1>`, the `og:title` meta tag, other large prominent text, other text on the page, anchor text on the page, text in links that point at the page, and `WebSite` structured data (that last one is the site-name feature, documented on the site-names page). Google may rewrite the title. There is no length limit. The title link is truncated to fit the device. https://developers.google.com/search/docs/appearance/title-link

Rules that page does state:

- Every page has a `<title>`.
- The text is descriptive and concise. Avoid vague labels such as "Home" or "Profile". Avoid keyword stuffing and boilerplate that is the same on every page, including a long title that changes by only one token.
- Put the site name at the start or the end, with a hyphen, colon, or pipe, rather than repeating a long brand sentence on every page. The home page is the reasonable place for a longer brand line.
- Make one main title visually obvious. One example on that page is a larger font and the title text in the first visible `<h1>`.
- Write the title in the same language and writing system as the primary content.
- Do not use `robots.txt` as a way to control the title. A blocked page can still be indexed from another site's link, and Google then builds the title from off-page text. To keep a URL out of Search, use `noindex`.

MDN: `<title>` sits in `<head>`, contains text only, and both tags are required. Its SEO notes say a longer descriptive title beats a one- or two-word title, that engines often show about the first 55–60 characters, and that titles should be unique on the site. For screen readers it says put the page purpose first and the site name after. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/title

The 55–60 character figure is MDN, not Google. Google says there is no limit. Do not treat 60 as a Google cutoff.

## Meta description

Google builds the snippet from the page content. It sometimes uses `<meta name="description">` when that text describes the page better than the body. There is no length limit. The snippet is truncated to the device. The same page can get different snippets for different queries. https://developers.google.com/search/docs/appearance/snippet

Rules that page does state:

- Unique description per page. A site-level description belongs on the home page or another aggregation page. Other pages get their own. If time is short, write the home page and the important URLs first.
- Summarize that page. A shop example on the page includes what is sold, hours, and location. A keyword list is the bad example. The same sentence on every article is the bad example.
- Programmatic descriptions are fine when they stay human-readable and use page-specific facts. A long keyword string is less likely to be shown.
- To suppress a snippet, `<meta>` `nosnippet`. To cap length, `max-snippet`. To keep a region out of the snippet, `data-nosnippet` on a `span`, `div`, or `section`. Those three are specified on the robots meta page. https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag
- A "read more" deep link is less likely if the target text is behind an expandable section or a tab, or if script on load forces scroll position or strips the URL hash.

MDN defines `name="description"` as a short accurate summary and points at that same Google snippet section. `name` metadata applies to the whole page. `content` holds the value. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name

MDN also lists `keywords` as a standard meta name. Google says it does not use that tag. Do not add it for Google. https://developers.google.com/search/docs/fundamentals/seo-starter-guide

The opened snippet page does not name `og:description` as a snippet source. **not public** there.

## Canonical

For duplicate or near-duplicate URLs, Google lists signals in this strength order: redirects (strong), `rel="canonical"` link annotations (strong), sitemap inclusion (weak). None is required. If you state none, Google picks a canonical itself. Using more than one method can stack. Do not point different methods at different URLs. Do not canonicalize a fragment. Do not use `robots.txt` or the URL removal tool as a canonical. Do not use `noindex` to choose among duplicates on one site; `rel="canonical"` is the preferred tool for that. https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls

The HTML rule on that page:

- A `<link rel="canonical" href="...">` in `<head>`.
- The same element on the canonical page itself (self-referential).
- An absolute URL. Relative URLs are supported and not recommended. The bad example is `/dresses/green/green-dress.html`. The good example is `https://www.example.com/dresses/green/green-dress.html`.
- The element is ignored for canonicalization if it also carries `hreflang`, `lang`, `media`, or `type`.
- `<head>` has to be valid HTML or the element is not accepted.
- Prefer one method. An HTML element and a `Link` HTTP header at the same time are supported and easier to get wrong.
- Internal links should use the canonical URL. Google prefers HTTPS over HTTP unless the certificate, mixed content, or an HTTP redirect conflicts.

MDN: `rel="canonical"` is valid on `<link>` only, not on `<a>`. It is the preferred URL for the current document. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel

The starter guide repeats that duplicate URLs are not a spam penalty, and that search engines can often pick a canonical without help. https://developers.google.com/search/docs/fundamentals/seo-starter-guide

A required self-canonical on a brochure that already has one URL per page is **not public**. The page says the site will likely be fine without one, and also says to include the self-reference when you do specify a canonical.

## Structured data

Structured data is in-page markup that describes the content of that same page. It can make a page eligible for a rich result. It does not guarantee one. A structured-data manual action removes the rich result. The policies page says that does not change how the page ranks in web search. Do not mark up facts that are not visible. Do not invent reviews, ratings, or a business identity. Put the data on the page it describes. JSON-LD, Microdata, and RDFa are all accepted. JSON-LD is the one Google recommends. The HTML shape in the intro is a `<script type="application/ld+json">` in `<head>` whose body is a JSON object with `@context` of `https://schema.org` and an `@type`. https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data https://developers.google.com/search/docs/appearance/structured-data/sd-policies

MDN's `<script type>` page does not name `application/ld+json`. It says any valid MIME type that is not a JavaScript type is a data block, and the browser does not run it. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script/type

Two types match a brochure. Nothing else was opened as a required type.

**Site name (`WebSite`), home page only.** Google shows a site name separately from the per-page title link. To state a preference, put `WebSite` structured data on the home page. The system also considers `og:site_name`, `<title>`, headings, and other home-page text. `WebSite` is the important one if you want to state a preference. Required properties are `name` and `url`. `alternateName` is optional. One name per domain or subdomain. A subdirectory such as `https://example.com/news` cannot have its own site name. The `url` is the root, for example `https://example.com/`, not a path like `https://example.com/de/index.html`. The home page must be crawlable: not blocked by robots.txt, `noindex`, or a login. Duplicate home pages (HTTP and HTTPS, www and non-www) repeat the same block. Do not add a second `WebSite` block if one already exists. Site names are not in the Rich Results Test. JSON-LD example on that page:

```html
<script type="application/ld+json">
{
  "@context" : "https://schema.org",
  "@type" : "WebSite",
  "name" : "Example",
  "url" : "https://example.com/"
}
</script>
```

https://developers.google.com/search/docs/appearance/site-names

**Local business (`LocalBusiness` or a more specific type such as `Restaurant`).** Required properties on that page are `name` and `address`. `address` is a `PostalAddress`. The page says to include as many of `streetAddress`, `addressLocality`, `addressRegion`, `postalCode`, and `addressCountry` as possible. Recommended, not required: `geo` (latitude and longitude to at least five decimal places), `openingHoursSpecification` (`opens` and `closes` as `hh:mm:ss`, `dayOfWeek` as schema.org day URLs), `telephone` (country code and area code), `url` (a working fully qualified URL of that location), `priceRange` (shorter than 100 characters), `menu` for a food business, and `image` in the examples. `review` and `aggregateRating` are recommended only for a site that captures reviews about other businesses, and they must follow the review-snippet rules. Do not mark a brochure's own testimonials up as those properties. Put the block on a page that shows the business. https://developers.google.com/search/docs/appearance/structured-data/local-business

A preferred image can also be `WebPage` with `primaryImageOfPage`, or an `image` on the main entity. The URL has to be crawlable. Do not use the logo, an image that is mostly text, or an extreme aspect ratio for that preferred image. https://developers.google.com/search/docs/appearance/google-images

FAQ rich-result eligibility was not opened. It is **not public** in this note. Do not add it from memory.

## Image alt

Google finds images in the `src` of an `<img>`, including an `<img>` inside `<picture>`. It does not index CSS background images. Supported types named on that page: BMP, GIF, JPEG, PNG, WebP, SVG, and AVIF. Always give `<picture>` an `<img src>` fallback. `srcset` needs that same `src` fallback. https://developers.google.com/search/docs/appearance/google-images

Alt text is the attribute that page calls the most important image metadata. Google uses it with the nearby text and the rest of the page. Rules stated there:

- Put the image next to text about the same subject.
- `alt` describes the picture in context. The best example on the page is "Dalmatian puppy playing fetch". "puppy" is only better. A missing `alt` is the bad example. A keyword list in `alt` is the bad example.
- The filename can be a light clue (`my-new-black-kitten.jpg`, not `IMG00023.JPG`). That is not a ranking formula.
- For an inline `<svg>`, the page says to use a `<title>` inside the SVG, not an `alt` attribute.
- To name which image should be the result preview: `og:image` with an absolute URL, or the schema.org image properties above.

The starter guide repeats: alt is a short description of how the image relates to the page, via the `alt` attribute. https://developers.google.com/search/docs/fundamentals/seo-starter-guide

MDN: `alt` is the replacement text when the image is not shown. Use a useful value whenever possible. `alt=""` means the image is decoration or a tracking pixel, and non-visual browsers may skip it. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img

An image sitemap is optional and was not required by the page for images that are already in HTML. **not public** as a requirement for a small brochure.

## Headings

Google's title-link page lists heading elements, especially `<h1>`, as one source for the title link, and says the main title should stand out, for example as the first visible `<h1>`. https://developers.google.com/search/docs/appearance/title-link

The starter guide says headings help people navigate, and then says this directly: heading order does not matter for Google Search, and there is no ideal number of headings on a page. Semantic order is for screen readers. https://developers.google.com/search/docs/fundamentals/seo-starter-guide

MDN says the opposite about document structure, and it is not a Google ranking rule. Do not skip levels. Start at `<h1>`. Prefer one `<h1>` that describes the page. Do not use headings only to resize text. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/Heading_Elements

A missing `<h1>`, or more than one, is therefore not a Google Search defect on the page that was opened. It is an MDN document-structure preference.

## noindex

Google: put `<meta name="robots" content="noindex">` in `<head>` to keep that page out of search results. `name` and `content` are case-insensitive. `nofollow` means do not follow the links on that page. `none` means both. Comma form and two meta tags are equivalent:

```html
<meta name="robots" content="noindex, nofollow">
```

If `noindex` is absent, the page may be indexed. The crawler has to be allowed to fetch the page. A `robots.txt` disallow hides the meta tag, so the `noindex` is ignored. `X-Robots-Tag` is the same rules for a non-HTML response. `noarchive` and `nocache` are on Google's unused list and are ignored. https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag

MDN: `noindex` asks a cooperative crawler not to index. `nofollow` asks it not to follow links. `index` and `follow` are the defaults. The meta tag still requires a fetch. A `robots.txt` block can stop the crawler from seeing `noindex`, and a blocked URL can still be indexed from other links. `noindex` applies only after a later visit. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/robots

MDN still lists `noarchive` as used by Google. Google's own robots page lists it as unused. Follow the Google page.

`noindex` is the draft switch. It is not a canonical tool. See the canonical section.

## Core Web Vitals

The Search Central Core Web Vitals page names three metrics and three targets, and no HTML element:

- Largest Contentful Paint within 2.5 seconds.
- Interaction to Next Paint under 200 milliseconds.
- Cumulative Layout Shift under 0.1.

It says good vitals are recommended for Search and line up with what the core ranking systems seek to reward, and it points at the page-experience doc and at web.dev. It does not state an HTML rule. An HTML recipe from those linked guides is **not public** on the page that was opened. https://developers.google.com/search/docs/appearance/core-web-vitals

The concrete HTML rule is on MDN's `<img>` page, and it is about layout shift, not a ranking formula:

- `width` and `height` are the intrinsic pixel size, integers with no unit. Together they let the browser reserve the box before the file loads, which reduces layout shift.
- `loading="lazy"` defers the fetch until the image is near the viewport. Width and height matter more on a lazy image, because an unloaded image otherwise has a width and height of 0 and the layout can jump.
- `loading="eager"` is the default and loads immediately.
- `fetchpriority="high"` or `"low"` is only a fetch hint relative to other images. The page does not say to put `high` on the LCP image.
- `decoding="async"` means the next paint need not wait for decode. The page says the effect on a static image is often hard to see.

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img

## What SpiderCaster already emits

Read from `lib/render.py` `render_page` and the section renderers, and from `lib/check.py` `check_site`. Canonical was not in that head. `WebSite` JSON-LD was not in that file.

`render_page` writes, in order:

- `<!doctype html>` and `<html lang="...">`. Language comes from `site.meta.lang`, or `en`.
- `<meta charset="utf-8">`.
- `<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">`.
- `<title>`. If the page title equals the brand, the title is the page title. Otherwise it is `{page title} - {brand}` (hyphen, page purpose first).
- `<meta name="description">` from `site.meta.description`. The same string is used on every page.
- Only when `noindex` is true: `<meta name="robots" content="noindex, nofollow">` and an HTML comment that the page stays noindex until approved. When the flag is false, that meta tag is omitted, which matches Google's "no rule means the page may be indexed."
- `<meta property="og:title">` set to the raw page title, not the branded `<title>` string.
- `<meta property="og:description">` set to the same site description.
- `<meta property="og:type" content="website">`. The opened Google pages do not describe `og:type`.
- `<meta name="theme-color">` from the palette accent. MDN defines that as UI chrome, not as a search field.
- `<link rel="icon" href="favicon.svg" type="image/svg+xml">` and `<link rel="apple-touch-icon" href="favicon.svg">`. `assemble` also writes `favicon.svg`.

Not in that head: `rel="canonical"`, `og:url`, `og:image`, `og:site_name`, `hreflang`, a keywords meta, `nosnippet`, `data-nosnippet`, and any `<script type="application/ld+json">`.

Body, from the section renderers:

- The brand link points at `index.html`. Nav links are real `href`s. The current page gets `aria-current="page"`.
- A hero with a local image emits `<img>` with `alt` from `image_alt` or, if that is missing, the brand name, plus `width="1600"` `height="900"` `fetchpriority="high"` `decoding="async"`. It is not lazy. A hero without an image is a letter mark with `aria-hidden="true"`, not a CSS photo.
- The only `<h1>` is the hero headline. Section titles and the call-to-action title are `<h2>`. Feature cards, steps, prices, team names, and menu groups are `<h3>`.
- A gallery item with `src` is an `<img>` with `alt` from `alt`, else `label`, else `""`, and `loading="lazy"`. No `width` or `height`. A gallery item without `src` is a colored `<div>`, which Google will not index as an image.
- Contact email, phone, address, and hours are visible text rows. They are not structured data.
- FAQ answers sit in `<details>`, so they are not visible until opened.

`check_site` in `lib/check.py`:

- `meta_basics` fails a page that lacks a doctype in the first 64 characters, a non-empty `<title>`, a non-empty description meta, or a viewport meta. It does not read the description text.
- `noindex_status` looks for `name="robots" content="noindex` in the HTML of every page concatenated. One page with the tag makes the whole directory look noindexed.
- It also checks favicon link and file, relative image `src` (remote `src` fails), and internal links. It does not check alt text, image dimensions, canonical, or JSON-LD.

## Engine gaps

Still missing after that read. Canonical and `WebSite` JSON-LD were not in the file, so they are listed. Eight items.

1. No `<link rel="canonical">` in `<head>`, and no absolute self-referential URL. `render_page` has no public origin to build one. https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
2. No home-page `WebSite` JSON-LD with `name` and `url`, and no `og:site_name`. The site-name page calls `WebSite` the preference signal. https://developers.google.com/search/docs/appearance/site-names
3. One site description is copied onto every page, including `og:description`. Google asks for a page-level description off the home page. https://developers.google.com/search/docs/appearance/snippet
4. No preferred image. A hero `<img>` does not produce `og:image` or `primaryImageOfPage`. https://developers.google.com/search/docs/appearance/google-images
5. Alt does not have to describe the image. Gallery can emit `alt=""`, which MDN reserves for decoration. Hero alt falls back to the brand name. https://developers.google.com/search/docs/appearance/google-images https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img
6. Gallery `loading="lazy"` images have no `width` or `height`. Hero always writes `width="1600"` and `height="900"`, not the file's intrinsic size. The Search Central Core Web Vitals page states no HTML rule. This item is the MDN `img` rule only. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img
7. No `<script type="application/ld+json">`. A visible business name and location are plain text. `LocalBusiness` requires `name` and a `PostalAddress`, and the contact block stores one address string, not those parts. Do not invent street, city, region, postal code, country, reviews, or coordinates. https://developers.google.com/search/docs/appearance/structured-data/local-business https://developers.google.com/search/docs/appearance/structured-data/sd-policies
8. `meta_basics` does not fail a missing canonical, a shared description, or an empty `alt`. `noindex_status` treats every page as one string, so a single noindex page satisfies the check for the directory. `lib/check.py`.
