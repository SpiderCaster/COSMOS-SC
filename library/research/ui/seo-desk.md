SEO Desk

Date: 2026-10-08. This screen shows index control on a site that already exists on disk. It does not promise a Google rank, a visibility score, or that a crawler has fetched the page.

## 1. Role

SEO Desk is the studio surface for one job: show Keith whether a built folder is noindex, what `robots.txt` says, whether `sitemap.xml` exists, where the meta description came from, and the heading order. A sitemap stays refused until he types an origin and explicitly clears noindex. Clearing noindex is a local file change. It is not `library bind --live`, and it was not run for this note.

## 2. Evidence

Read for this note: `library/research/ui/BRIEF.md`, `library/research/competitors/durable.md` (opened as competitor notes dated 2026-10-08), `lib/seo_pack.py`, `lib/seo_pack_selftest.py`, `lib/heading_rank.py`, `lib/render.py` (description and robots meta), `lib/compose.py` (description copy and the forced noindex pack), `lib/offline.py` and `lib/ir.py` (description fallbacks), `lib/check.py` (the crawl rows), `lib/hands/__init__.py` (`uniqueness`, `meta_basics`), `library/seats/seo/SKILL.md`, `spidercaster.py` (`build`, `check`, `serve`), `lib/serve.py`, `projects/demo-local/copy/overview.md`, `sites/demo-local-compose/` (`index.html`, `site.json`, `robots.txt`). No `sitemap.xml` is under `sites/`. A read-only `python spidercaster.py check sites/demo-local-compose --expect-noindex --project projects/demo-local` returned 35 pass, 0 fail, 0 warn, 1 skip. The skip is `grey_tile`, a rendered photo check, not an index result.

Durable, before a page exists: the product page asks three questions. The FAQ names industry, business name, and goals, then Durable generates a site. A different help article asks business type, city and country, and business name, then generates a blank site. Neither article shows a plan the person approves first. SEO title, meta description, per-page noIndex, Remove from sitemap, and the SEO status panel are editor controls after a site exists. That panel lists LLM readability, website indexability, mobile responsiveness, H1 tags, image alt text, and page titles. Nothing opened says the panel blocks Publish. "Get found on Google and ChatGPT", Visibility Score, and "often 90+" are product claims. They were not measured. Customer `robots.txt` directives are not public. Foundational SEO says a published site serves `sitemap.xml` and `robots.txt`, and that noIndex also drops the page from the sitemap. The free plan is described as a private preview; a custom domain that can be found on Google is paid packaging, not a measured robots rule. Description length 110 to 160 is their writing advice, not a rank rule. A single-H1 rule is not public. Indexing is documented as days to weeks, not instant.

SpiderCaster shows the opposite order. The page is built locally from real copy and stays noindex. The desk reads that state. It does not generate a business, a description, or a score before the HTML exists.

## 3. Screen

The person acts in this order. Nothing on the screen writes until the last control, and that control stays refused until both gates are filled.

1. Site. A folder that already has `index.html`. The only project names offered are `projects/demo-local` and `projects/bench-harbor-tearoom`. Fleet domains are not listed. If the folder has no `index.html`, the screen shows the checker failure `files_present` and stops. `compose --plan` has no HTML, so this screen shows no meta tag and no sitemap, and it does not invent either.

2. Check again. Runs `python spidercaster.py check <site> --expect-noindex`, plus `--project <project>` when the folder belongs to one of those two projects. Read-only.

3. Noindex. A readout, not a score. On when the page has `<meta name="robots" content="noindex, nofollow">`, which is what `render.assemble` writes when noindex is on. The readout also shows `report.json` field `noindex` and the checker row `noindex_status`. Default copy is the build line already printed by the CLI: NOINDEX. Mismatch between the meta tag, `report.json`, and `robots.txt` is shown as a mismatch. It is not smoothed into one green state.

4. robots.txt. The file text, or the words "missing". A noindex pack is `User-agent: *` and `Disallow: /`. An indexable pack with no origin is `User-agent: *` and `Allow: /`, with no Sitemap line. An indexable pack with an accepted origin adds `Sitemap: {origin}/sitemap.xml`. The screen does not call Allow a submission.

5. Sitemap. "Absent" or "Present", from whether `sitemap.xml` is in the folder. Absent is the normal state. Present lists only filenames that are already `.html` on disk. The engine writes `loc` and `lastmod` from the file time. It does not write `<priority>`. The screen does not add priority, and it does not open Search Console.

6. Description source. For each HTML page, the meta description that is already in the file, then one source label, in this order, without writing a new sentence. A `Description:` line in `copy/<stem>.md` (or the only copy file when the site has one page) is the source when compose stored it on that page. Staged copy for `demo-local` and `bench-harbor-tearoom` has no `Description:` line. Otherwise the source is `site.json` `meta.description`. Offline planning sets that from the hero block's first paragraph, cut at 160 characters on a sentence end, or `{brand} - local build` when that paragraph is empty. `normalize_site` fills an empty meta description with `{brand} - local build by SpiderCaster`, cut at 155. Render prints the page description when it is non-empty, otherwise the site meta description, into both `meta name="description"` and `og:description`. On `sites/demo-local-compose` the meta content equals `site.json` `meta.description`, which is that hero-paragraph cut of `projects/demo-local/copy/overview.md`. The checker row `description` passes when the content is non-empty. Length is shown as a count. A 110 to 160 band is not a fail.

7. Heading order. The outline from `heading_levels`: h1 through h6 that sit outside `data-sc-part`. A skip is the checker string, such as `h1 to h3`, from `heading_skips`. The row `heading_order` passes when there is no skip. `one_h1` is shown beside it. On this compose sample both passed: index has 1 h1, and `heading_order` passed for 1 page. Headings inside a catalog part are not part of this outline. The list is not an H1 score and not a rank.

8. Origin. A text field, empty. The accepted shape is the engine rule: an origin such as `https://example.com`, with no path. Empty stays empty. The screen does not invent a hostname.

9. Clear noindex. A control that defaults off. The label says it drops the noindex meta on a later local build. It does not say the page will be found on Google. It does not call `library bind --live`.

10. Write sitemap. Refused, with the reason in text, until Origin is an accepted origin and Clear noindex is on. Refused reasons the screen states: no origin; noindex still on; origin has a path; this folder was composed (`compose` calls `write_pack` with `indexable=False`, and `build --compose` returns before `--indexable` and `--host` are read); every HTML file still contains the letters noindex, which makes `write_pack` write `Disallow: /` and delete `sitemap.xml`. When both gates are on, the only command is `python spidercaster.py build <project> --offline --indexable --host <origin> --out <folder the human named>`. The button does not run `compose`, `shipcheck`, or `library bind --live`.

## 4. Already here

`python spidercaster.py build <project> --offline` leaves noindex on. It prints `NOINDEX (default; pass --indexable to flip)` and calls `write_pack`. That writes `robots.txt` with `Disallow: /` and deletes `sitemap.xml` if one is there. `build --indexable --host https://origin` is the command that omits the robots meta and may write the sitemap. `--host` is documented as used only with `--indexable`. A bad host raises `SeoPackError`: host must be an origin like `https://example.com`. No host, or no HTML page left after the noindex-text skip, means robots without a Sitemap line and no sitemap file.

`python spidercaster.py compose <project>` always renders `noindex=True` and calls `write_pack(out, indexable=False)`. `sites/demo-local-compose/robots.txt` is `User-agent: *` / `Disallow: /`. The same command is the one that reads `Description:` lines onto page descriptions. Plain `build` does not.

`python spidercaster.py check <site> --expect-noindex` already judges `noindex_status`, `meta_basics`, `description`, `one_h1`, `heading_order`, `canonical`, and `json_ld`. It does not print `robots.txt` or look for `sitemap.xml`. The desk reads those two files next to the rows.

`python spidercaster.py seat seo` is read-only. The seat hands are `uniqueness`, then `meta_basics`. `meta_basics` runs the checker with `expect_noindex=True` and only returns the `meta_basics` and `no_sample` rows. The seat skill forbids `--indexable` and `library bind --live`. `uniqueness` is a mold-draft check, not an index check. `serve` only hosts an existing folder on `127.0.0.1`. `refine` keeps whatever noindex state is already in `index.html` and does not call `write_pack`, so the desk must keep showing file against meta.

## 5. Proposal

The smallest surface is one localhost page, standard library only. Bind it to `127.0.0.1` the way `lib/serve.py` does. Do not add a package. Do not use React, Tailwind, or shadcn. Do not put a chat control on it. Do not replace `serve`. `serve` still previews the built site. This page is the desk beside that preview.

The page shells out to the two commands above and reads `robots.txt`, `sitemap.xml`, `report.json`, `site.json`, and the project `copy/` directory. Description source uses the existing `Description:` rule and the existing meta fallback. It does not add a sentence. Heading order uses the existing `heading_rank` rules. Write sitemap stays disabled in the form until Origin and Clear noindex are both set, then it runs only `build --offline --indexable --host` into an output folder the human names. It does not point that command at a compose folder by default, because a plain offline build does not keep composed catalog parts, and the compose command cannot emit a sitemap today.

## 6. 4Cs+ test

Phone-width window, for the desk page once it exists. Judge at 360, 390, and 412. No sideways overflow. Body text 18px, chrome 16px, tap targets 44px, including Origin, Clear noindex, Check again, and Write sitemap. One h1. Contrast 4.5:1, large text 3:1. Refusal text is visible without a hover. The desk is not a catalog page: it does not need a mold, a hero visual, or a drawer. That phone-width pass is not measured, because the desk page is not built. Not public.

Built page, measured this session on `sites/demo-local-compose` with `--expect-noindex` and `--project projects/demo-local`. Copy: `no_sample` pass, `no_soft_placeholders` pass. Crawl: `meta_basics` pass, `description` pass, `one_h1` pass, `heading_order` pass, `canonical` pass, `json_ld` pass (WebSite, no aggregateRating), `noindex_status` pass. The meta tag is noindex, nofollow. `robots.txt` is Disallow. Sitemap is absent. Chrome and Plus rows that the same command printed also passed, including tap floor 44px and no sideways overflow at 360, 390, and 412. `grey_tile` was skipped. `visit` was not run, so a Playwright measure at 390 and 1280 is not public. None of these rows is a rank.

After a human later supplies an origin and clears noindex, the same screen is judged again with `check <site> --expect-indexable`. `noindex_status` must match. `robots.txt` may then Allow, and a sitemap may exist only if the origin was accepted and at least one HTML file was not skipped. This note did not run that build. Not public.

## 7. Risks

Inventing copy. Filling a missing `Description:` line, rewriting the meta with a model, or failing a short or long description as if 110 to 160 were a rank rule. The fallbacks `{brand} - local build` and `{brand} - local build by SpiderCaster` are engine strings when the source paragraph is empty. The desk labels them as fallbacks. It does not treat them as a new claim, and it does not hide an empty meta behind one.

Deploying. Enabling Write sitemap from the SEO seat, passing `--indexable` by default, calling `library bind --live`, or calling `shipcheck`. Binding `warmth-authority`. Writing pages for fleet domains. Submitting a sitemap to Google or Bing. A sitemap file is not indexing. Indexing time on Durable's help is days to weeks and was not measured here. Not public.

Hiding a failure. Showing a single "indexable" badge when the meta, `report.json`, and `robots.txt` disagree. Leaving a deleted sitemap looking present after a noindex pack. Running `build --offline --indexable` over `sites/demo-local-compose` and dropping the composed parts. Treating `build --compose --indexable --host` as success when compose never reads those flags. Calling Allow, or an absent sitemap, a Search Console result. Showing Durable's Visibility Score or "often 90+" as a SpiderCaster result. Adding `llms.txt`, whose body is not public. Adding `<priority>`. Loosening one h1 or the heading-order skip so the desk matches Durable's undocumented H1 check.
