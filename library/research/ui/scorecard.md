4Cs+ Scorecard

# 1. Role

The 4Cs+ Scorecard is the studio screen that rates a page after it exists. Its one job is to show the existing checker's own words for Copy, Contrast, Chrome, Crawl, and Plus. It does not grade, score, or average. A row is PASS only when every checker row under it is PASS. Any other checker word blocks PASS. WARN and SKIP stay WARN and SKIP. They are not relabeled FAIL, and they are not a pass.

# 2. Evidence

Read on 2026-10-08:

- `library/research/ui/BRIEF.md` names the five floors and limits staged sites to `projects/demo-local` and `projects/bench-harbor-tearoom`.
- `library/resources/MOBILE.md` is the phone sheet at `@media(max-width:860px)`: one column, 16px side padding, 44px targets on skip, button, brand, nav links, and footer links, a nav sheet hidden until `.open`, `body.nav-open` with `overflow:hidden`, skip link `href="#main"`, and noindex while staged. It says `lib/check.py` `mobile_hero` fails `height:168px` and passes `aspect-ratio:16/9`.
- `library/resources/PHONE_A11Y.md` lists eight enforced phone rules, including skip link, 44px targets, visible focus, safe-area header and footer, reduced motion, and no remote image. The 44px floor is the checker's floor. A 40px floor is not used.
- `library/research/competitors/wix.md`, Mobile and SEO. Harmony shows a person a generated site before they have a page. Three doors: Aria drafts a description and Generate Site builds pages, layouts, colors, and starter content in one pass (a separate plan before that pass is not public); a recommended template, then Edit; or ChatGPT, where the human reviews a description and then Create Site. That third door is the only documented path that approves a plan before the page exists. Afterward, Preview and Publish sit on the top bar. Publishing is what visitors get. Harmony is described as automatically responsive. The human designs on desktop and may open a mobile view. Pixel breakpoints are not public. A measured check at 360, 390, or 412 is not public. A horizontal or vertical header menu becomes a hamburger; cart and logo can stay out. Aria is absent in the mobile view and does not edit it. A minimum tap size is not public. The 40px section-row minimum is a grid rule, not a tap rule. Published system-color hex values are not a measured contrast result. Index defaults to on until a human turns a per-page toggle off. A ban on invented reviews is not public. Canonical on Harmony is not public on the Harmony SEO article. Aggregate rating is not named as a Harmony default.

SpiderCaster does not show starter copy before a page exists. The card stays unrated until `index.html` is on disk. `compose --plan` writes `structure.json` and no HTML, so it is not a rated page.

Checker source for the words below: `lib/check.py` `check_site`, `lib/visit_check.py` `visit_site`, `lib/seo_pack.py` `write_pack`, `lib/heading_rank.py`, `lib/copy_pack.py` `project_copy_text`, and `spidercaster.py` `cmd_check`, `cmd_visit`, `cmd_build`, and `_run_compose`. This report did not run a build. Pass or fail of either staged site is not public.

# 3. Screen

The human acts in this order. Controls are named as they should appear. Nothing on this screen writes copy.

1. Project. Two choices only: `demo-local` and `bench-harbor-tearoom`. Any other name is refused, including fleet domains.
2. Out. A local folder, default `sites/<project>-compose`. A path outside the working tree is refused.
3. Compose. Optional. Runs offline compose for that project only. It does not rate the page.
4. Check. Refused when `index.html` is missing. The checker then has a single `files_present` FAIL and returns. The five rows are not filled in as PASS.
5. Visit. Same folder. Does not install a browser.
6. The five rows. Under each row, every child line keeps the checker's `name`, `status`, and `detail`.

Refused, and not drawn: Publish, `library bind --live`, `--indexable`, `--host`, an AI build, refine that rewrites copy, Generate Site, an Aria or chat control, binding `warmth-authority`, and any control that edits `copy/`.

`check` exit code stays the checker's. `Report.ok` is false when any row status is FAIL, including rows that are not one of the five labels. The card prints that exit code. It does not replace it with a percent.

# 4. Already here

There is no studio screen. These commands already do the rating.

Check, from `spidercaster.py` `cmd_check`:

`python spidercaster.py check <out> --expect-noindex --project <project>`

`--project` loads `project_copy_text`. That function joins only `copy/*.md`, `copy/*.markdown`, and `copy/*.txt` directly inside `copy/`, in file name order. It does not read `brief.md`. Empty `copy_text` adds no claim row. The CLI passes `expect_noindex=True` only with `--expect-noindex`. Without that flag, `noindex_status` is SKIP.

Visit, from `cmd_visit`:

`python spidercaster.py visit <out>`

`visit_site` always runs static checks. Rendered checks run only after Playwright launches Chrome or bundled Chromium. A missing browser leaves `mode` as `static`. The module says that is not a failure. It is also not a rendered measurement.

Compose, from `_run_compose` and `lib/compose.py`, is offline, `noindex=True`, zero tokens, and calls `write_pack(out, indexable=False)`. Default out is `sites/<project>-compose`. `build --offline` is the other noindex path: `assemble(..., noindex=True)` and `write_pack` unless `--indexable` is passed. This screen does not offer `--indexable`.

`serve` only hosts a finished folder on `127.0.0.1`. It does not rate.

# 5. Proposal

The smallest surface is one localhost page from the standard library, bound to `127.0.0.1` the way `lib/serve.py` binds. No new package. The page is not a SpiderCaster site and is not published.

The page POSTs to the same process. Check calls `check_site(out, expect_noindex=True, copy_text=project_copy_text(project))`. Visit calls `visit_site(out)`. Compose, if used, calls the existing compose path and does not pass a mold of `warmth-authority`. The process does not import a publisher and does not call `library bind`.

The page sets `<meta name="robots" content="noindex, nofollow">` and a viewport of `width=device-width, initial-scale=1`. It is one column. Body text is 18px. Labels are 16px. Check, Visit, Compose, and the project choices are at least 44px by 44px. Primary navigation stays at four links or fewer so the checker's drawer rule is not triggered by the card itself. Text is the renderer's near-black `#1a1a1a` on `#ffffff`. Those two colors already appear in `lib/mold_paint.py`. The contrast ratio of this screen is not public until the page exists.

The five rows are a grouping of checker rows. They are not a filter. Every other checker row is listed under the five, with its own status, so a FAIL cannot disappear.

# 6. 4Cs+ test

Phone widths the checker already uses: 360×740, 390×844, and 412×915. Type and contrast also run at 1280×800. Visit, when rendered, measures the index at 390×800 and 1280×800. The built-page phone sheet remains `@media(max-width:860px)`. Harmony's unpublished breakpoints are not used. A 40px tap floor is not used.

## How a row gets its word

PASS only when every child listed for that row is PASS, with one exception under Copy. FAIL on any child makes the row FAIL. WARN or SKIP on any child makes the row that word and blocks PASS. The order used when a row is mixed is FAIL, then WARN, then SKIP, then PASS. Child lines still show each checker's own status. This is not a new scale.

Claim rows `ungrounded_claim`, `lone_about`, and `invented_chrome` are added only when `copy_text` is non-empty and a hit exists. After `check --project`, their absence is clear, not a hidden PASS row. Without `--project` they were not judged, so Copy is not PASS.

A checker exception on type, contrast, tap, or the mobile scan is FAIL. The checker fails closed.

## Copy

Visible claims must already be in the project copy. The row does not invent a wider ban than the checker.

- `no_sample` — raw HTML. FAIL on SAMPLE, "placeholder disclaimer", "demo content", "hello world", "sample page", "SAMPLE labels mean placeholder", "under construction", or "lorem ipsum".
- `no_soft_placeholders` — visible text only, script and style skipped. FAIL on TODO, TBD, FIXME, XXX, lorem, ipsum, or placeholder.

Only with `--project`, and only emitted on a hit:

- `ungrounded_claim` — visible "testimonial", "customer review", or "award-winning", or a star rating (`N/5` or `N star` / `N stars`), when that phrase is not in the copy text. Bare "review" is not a claim. A page that says "award" without "award-winning" is not this row.
- `lone_about` — an h2 whose text is exactly "About" when the copy does not contain the word About.
- `invented_chrome` — visible "Read on" or "Built with SpiderCaster" when that exact phrase is not in the copy.

Copy is PASS only when `no_sample` and `no_soft_placeholders` are PASS, `--project` was passed, and the three hit-only rows are absent. A hit on any of them is FAIL.

`no_hotlink` is not Copy. It is printed with the other rows.

## Contrast

One checker row: `contrast`.

FAIL when measured text is under 4.5:1, or under 3:1 for large text. Large is 24px or more, or 18.66px or more at weight 700 or more. The cascade is static CSS at 360, 390, 412, and 1280. It is not a browser. Each failure names the file, the selector, and the measured value. If nothing fails but some text is not measurable, or the scan has notes, the status is WARN. WARN is never a pass, so Contrast is not PASS.

## Chrome

PASS only when all of these are PASS.

- `type_floor` — text under 16px fails. Body text under 18px fails. Chrome keeps the 16px floor: header, nav, footer, label, figcaption, caption, small, summary, th, legend, select, option, and roles navigation, banner, contentinfo, tab, menuitem, tablist. Headings need 16px. Buttons and links are body text and need 18px. Same four viewports as contrast.
- `tap_target` — at 360, 390, and 412, every `a[href]`, button, input, select, textarea, summary, and role button, link, tab, or menuitem needs a box of at least 44px by 44px. FAIL when the upper bound is under 44px. WARN when the bounds straddle 44px. An inline link inside a sentence is exempt. WARN blocks Chrome PASS.
- `site_header` — index has class `site-header`, and a script sets `is-stuck`.
- `skip_link` — `href="#main"`.
- `hero_visual` — index has class `hero-visual`.
- `favicon_link` — `rel="icon"` and `href="favicon.svg"`.
- `favicon_svg` — `favicon.svg` beside `index.html` contains `<svg`.

Printed under the card, not folded into the Chrome PASS word, because the brief's Chrome list does not name them. A FAIL on any of them still makes `check` exit 1:

- `scroll_margin` — PASS when `scroll-margin-top` is in the index.
- `mobile_hero` — FAIL on `height:168px`. PASS on `aspect-ratio:16/9`. `min-height:168px` is not the failure.
- `mobile_visible` — `.reveal` at opacity 0 fails unless a `max-width:860px` rule sets `.reveal` to opacity 1.
- `no_empty_panel` — FAIL when the text `about-panel` appears anywhere in `index.html`, including a selector. On this read, `lib/render.py` does not contain `about-panel`. Whether a later page passes is not public until `check` runs. Do not report this row as a pass without that run.
- `phone_bar` — added only when a `phone-bar` link exists. PASS when the `tel:` digits match the link text and there are at least 7 digits. A leading `+` is not a digit.

## Crawl

PASS only when all of these are PASS.

- `one_h1` — the index has exactly one `h1`. Other pages are not this count.
- `heading_order` — no skipped level, such as an h1 followed later by an h3 with no h2. Headings inside `data-sc-part` are catalog-part chrome and are ignored. The checker does not retag text and does not add headings.
- `canonical` — every page has a relative canonical link. A domain or a protocol-relative href does not count.
- `json_ld` — every page has a WebSite JSON-LD script, and the html contains no `aggregateRating`.
- `description` — every page has a non-empty meta description.

`meta_basics` (doctype, title, description, viewport) is printed beside Crawl. It is not a second description grade. A FAIL still fails the exit code. `faq_schema` is also printed: a page with no FAQPage passes; any page emitting FAQPage JSON-LD fails (Google removed the FAQ rich result 2023-2026 — keep the visible FAQ section, drop the markup). `img_alt` and `missing_file` are printed the same way. A page with no img passes both.

## Plus

Overflow, drawer, and noindex. PASS only when all three checker rows are PASS.

- `sideways_scroll` — at 360, 390, and 412, FAIL when a resolved box ends to the right of the viewport, unless an ancestor below body clips or scrolls it. Causes the checker already names include a fixed width or min-width in px, vw or percent over 100, a negative right margin past the gutter, an img, iframe, video, or svg width with no max-width, a wide table, pre or nowrap text, and a long unbreakable word. WARN is not a pass.
- `mobile_nav_drawer` — more than 4 primary nav links at a phone width need a `button` (or `role=button`) with `aria-expanded="false"`, `aria-controls` pointing at an existing id, an accessible name, and a 44px box. The drawer holds the nav links, is hidden by default, opens in a static simulation of the page's own script, and has a close mechanism (the toggle flips back and stays visible, a close control inside, Escape, or a native dialog or popover). Four or fewer links can pass with no toggle. No nav landmark on any page is SKIP, "not-run", and Plus is not PASS.
- `noindex_status` — PASS only with `--expect-noindex` when the pages contain `name="robots" content="noindex`. Without the flag the row is SKIP. `--expect-indexable` while pages are noindex is WARN. This screen always passes `--expect-noindex`.

`mobile_visibility` is printed under Plus and is not part of the three-row PASS word. Content hidden on phones is WARN. An `h1` or `main` hidden at a phone width is FAIL, and that FAIL still fails `check`. The drawer and its toggle are exempt.

Visit is printed under Plus. It is not folded into the checker word.

- Static, always: `missing_header`, `missing_main`, `broken_hash`, `missing_viewport`, and `sideways` from CSS widths on the index.
- Rendered, only when a browser launches: the index at 390×800 and 1280×800. `sideways` when `scrollWidth` is greater than `clientWidth` plus 1. `missing_header` when no header is visible. Remote http and https requests are aborted.
- `mode: static` means the rendered widths were not measured. That is not a checker failure and not a rendered pass. The card prints `static`. The 390 and 1280 result is not public.
- `mode: rendered` with `ok` false is a visit failure. It does not rewrite `sideways_scroll`. Both results stay on the card.

`robots.txt` and `sitemap.xml` are not checker rows. `check` does not read them. The card prints the file fact and does not assign it PASS or FAIL.

- A noindex compose, and a noindex build, call `write_pack` with `indexable=False`. That writes `User-agent: *` and `Disallow: /`, and deletes `sitemap.xml` if one is there.
- A sitemap is written only when the build is indexable, the host is an origin like `https://example.com` with no path, and at least one html file does not contain the word noindex. `robots.txt` then allows `/` and names `Sitemap: <origin>/sitemap.xml`.
- This screen does not run that indexable path. A file that disagrees with the noindex pack is shown as a mismatch. It does not change the Plus checker word, and it does not count as a checker pass.

## Phone-width window of this screen

The card itself, at 360, 390, and 412, is one column: the five rows stack, the side does not scroll, controls stay at least 44px, body text stays at least 18px, and labels stay at least 16px. Contrast uses the same 4.5:1 and 3:1 floors. There is no second mobile document and no control that exists only on the phone. Those measurements of this proposed page are not public until the page exists. The built page is judged only by the checker and visit results above.

## Later builds

Only these two projects. Copy on disk today, not quoted here:

- `projects/demo-local/copy/` — `commands.md`, `faq.md`, `overview.md`. The brief says the build stays noindex.
- `projects/bench-harbor-tearoom/copy/` — `contact.md`, `hours.md`, `menu.md`, `overview.md`. The brief says synthetic, never index, never deploy.

A later rating, not run for this report:

`python spidercaster.py compose projects/demo-local`

`python spidercaster.py check sites/demo-local-compose --expect-noindex --project projects/demo-local`

`python spidercaster.py visit sites/demo-local-compose`

The same three commands with `projects/bench-harbor-tearoom` and `sites/bench-harbor-tearoom-compose`.

Compose stays noindex and does not publish. Do not pass `--indexable` or `--host`. Do not run `library bind --live`. Do not bind `warmth-authority`. An AI build is not this rating, because it can invent copy. `build --offline` without `--indexable` is the other noindex path; this screen still prefers compose. Results of those commands are not public here.

# 7. Risks

- Painting PASS when a child is WARN, SKIP, or missing. Unmeasured contrast, an unmeasured tap, a drawer SKIP, a noindex SKIP, and a static visit are not passes. Calling them passes hides a failure.
- Running `check` without `--project`. Claim rows never appear, so an invented testimonial, "award-winning", or a star rating would not be judged. Copy must stay not PASS.
- Running `check` without `--expect-noindex`. `noindex_status` is SKIP. Plus must stay not PASS.
- Treating `visit` mode `static` as proof at 390 and 1280. The rendered result is not public.
- Inventing a checker row for `robots.txt` or `sitemap.xml`. Print the file. Do not mint a status. Do not write a sitemap for a noindex build.
- Offering Generate, Aria, refine-with-a-model, or an empty prompt. That invents copy. Harmony does this before the page exists. This card must not.
- A per-page index toggle, `--indexable`, or `library bind --live` on this screen. Offline output stays noindex until a human publishes, and this work does not publish. Harbor is synthetic and must not be deployed. Fleet domains have no copy pack here.
- Hiding `no_empty_panel`, `mobile_visibility`, `meta_basics`, or any other FAIL because it is not one of the five labels. The exit code is any FAIL. The five labels are headings, not a mask.
- Folding visit's `sideways` into `sideways_scroll` so one line replaces the other. They are different measurements. Both stay visible.
- A 40px control, a chat button, or a mobile-only block that hides `h1` or `main`. The checker already fails the last of those. The screen does not add the first two.
