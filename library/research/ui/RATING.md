# Studio rating

Date: 2026-10-08. This rating is the checker, the rendered visit, and a phone-width measure of the studio shell. It does not assign a Google rank. Nothing was published. `library/ledger.json` was not written. `library bind --live` was not run.

The twelve screen reports are in `library/research/ui/`. The chair note is `DISCUSSION.md`. The improve loop below is the parent reading the staged pages and changing the engine, then painting again through the studio.

## What the first paint got wrong

The first studio paint of both projects passed the old checker: `demo-local-studio` 35 pass / 0 fail / 0 warn / 1 skip, and `bench-harbor-tearoom-studio` 36 pass / 0 fail / 0 warn / 1 skip. `visit` was mode `rendered`, exit 0. That pass missed the catalog sentences inside `data-sc-part`.

Visible examples on the harbor page: "Hero: full-bleed dark band", "Table: basic data table", the Shift / Desk / Field rows, and "Quick links". The real menu and the real hero sat beside that demo text. Heading order ignores headings inside `data-sc-part`, so the old checker did not see them.

A second look showed each section twice. After the demo sentences were stripped, `copy_block` still printed the section copy in an `sc-fill` dump above the renderer block.

Harbor hours were also missing. `hours.md` says "Open Tuesday to Sunday, 8am to 6pm." and "Closed Mondays." `hours-stack` keeps hero, menu, features, faq, and contact. The planner had stored Hours as its own block, and the frame dropped it.

## What changed

`ground_fragment` fills a slot only from copy, then drops catalog demo text. A short token that merely occurs inside a copy line, such as "Hours" inside "# Hours", is dropped. `check --project` adds `part_demo` FAIL when visible text inside `data-sc-part` is not in the project copy. A clean page adds no `part_demo` row.

A part with no grounded text and no media is recorded on the plan and is not inserted. The renderer already shows that section. `tools apply` still writes the stored snippet. A later `check --project` fails `part_demo` if that demo text is still on the page.

`hours-stack` still does not invent an hours section. Sentences from a dropped Hours block are copied onto the contact row when that row has no hours line of its own.

## Second paint

Both sites were planned, accepted, and painted again through the studio on `127.0.0.1`.

| Project | Frame | Mold | Out |
| --- | --- | --- | --- |
| demo-local | welcome-scroll | discover-grid | sites/demo-local-studio |
| bench-harbor-tearoom | hours-stack | discover-grid | sites/bench-harbor-tearoom-studio |

Plan folders hold `structure.json` only. Older folders `sites/demo-local`, `sites/demo-local-compose`, `sites/demo-local-ai`, and `sites/bench-harbor-tearoom` were not overwritten.

`check --project --expect-noindex` after this paint:

| Site | Pass | Fail | Warn | Skip |
| --- | --- | --- | --- | --- |
| bench-harbor-tearoom-studio | 36 | 0 | 0 | 1 |
| demo-local-studio | 35 | 0 | 0 | 1 |

The skip on both is `grey_tile`. Static CSS cannot prove a grey tile is absent. That skip blocks a Plus word of PASS. It does not stop Next. There is no FAIL.

Copy, Contrast, Chrome, and Crawl are PASS on both. Claim rows `ungrounded_claim`, `lone_about`, `invented_chrome`, and `part_demo` are absent, which means no claim failure. Contrast on both is "lowest 4.40:1" and passes under the large-text rule (3:1). Body type is 18px. Harbor has one extra pass, `phone_bar`, because the copy includes a phone.

`visit` on both is mode `rendered`, exit 0, at 390x800 and 1280x800. A rendered visit is a measure. It is not the same test as the three studio iframes.

Both `robots.txt` files are:

```
User-agent: *
Disallow: /
```

Neither folder has `sitemap.xml`. Both pages carry `noindex`. Report mode is offline and the token ledger is 0.

The harbor page shows Harbor Tea Room, the three teas with prices, the phone, 14 Harbor Lane, and "Open Tuesday to Sunday, 8am to 6pm. Closed Mondays." The demo-local page shows the engine overview, the build cards, and the questions from `faq.md`. Catalog demo sentences and `sc-fill` dumps are gone. `data-sc-part` is absent because those shells had no grounded markup.

## Gaps that stay gaps

`welcome-scroll` also names gallery and contact. `projects/demo-local` has no copy for those sections, so the plan keeps hero, about, features, and faq. The missing two were not invented.

`hours-stack` also names features and faq. Harbor copy does not produce them. The plan keeps hero, menu, and contact. Hours text is on the contact row.

The plan still names a catalog part for each kept section (`hero-dark-band-072`, and the card, faq, table, and cta ids). Those snippets are demo text with no `data-sc-slot`. Compose does not paste them onto the customer page. The visible page is the renderer with the discover-grid accent `#2a6f8f`.

`grey_tile` was not run as a rendered photo check. There is no photo in either copy pack.

Fleet names stay blocked. iseark and teavital stay WordPress. No page was built for them.

## Studio shell

The desk is stdlib on `127.0.0.1`. Twelve rooms: Desk, Copy, Plan, Mold, Parts, Mobile, Check, SEO, Crew, Preview, Domains, Score. No chat, no textarea, no publish control. Crew says the seats are not run. SEO says it does not clear noindex and does not write a sitemap. `warmth-authority` is refused.

`studio_selftest`, `part_fill_selftest`, and `frames` selftest exited 0 after the fixes.

Playwright measured all 12 rooms at 360, 390, 412, and 1280. Failures: 0. Each room had one `h1`, body font at least 18px, no sideways overflow, and every visible button and nav or header link at least 44 by 44.

There is no browser panel in this session. The rendered visit and the studio measure used Playwright. They launched.

## Improve cycle, same day

A rendered pass of both studio sites at 360, 390, 412, and 1280 found two defects the checker did not name.

Harbor's hero action row was empty at every width. The planner had pointed the hero at Hours. `hours-stack` drops that block and keeps the hours sentences on the contact row. The hero primary was cleared, and the hero drew only the primary, so the Contact button already stored on the hero never appeared. On a phone the nav links sit in the drawer, so the hero had no action.

The hero now draws primary and secondary, and omits the row when both are empty. When a frame drops the hero target, primary becomes the next section title already on the page. Harbor's hero is Menu and Contact. Both words are the section titles. No new sentence was written.

At 1280 the demo nav label "Build" measured 40 by 44. Nav links now have a 44px minimum width as well as height. Phone links were already full width.

Both sites were planned, accepted, and painted again through the studio. `check --project --expect-noindex` is unchanged: harbor 36 pass / 0 fail / 0 warn / 1 skip, demo-local 35 pass / 0 fail / 0 warn / 1 skip. The skip is still `grey_tile`. Contrast is still "lowest 4.40:1", a large-text pass. `visit` is mode `rendered`, exit 0, on both. The same rendered pass is clean at 360, 390, 412, and 1280: no empty hero row, no page overflow, no tap under 44, no body type under 18. `hero_link_selftest` and `studio_selftest` exited 0.

Header ellipsis on the long demo title and on the scroll-spy label is the one-line header doing its job. The full title is the h1. Catalog parts are still named on the plan and still omitted when the snippet has no grounded text. That remains the next product hole. It is not a new sentence and it is not a rank.

## Part bind, same day

The named parts now land on the page. A catalog snippet has no `data-sc-slot`, so filling slots left the demo sentences, and grounding then removed them. Compose recorded the part id and inserted nothing. The renderer showed the copy by itself.

`bind_fragment` rebuilds the snippet from section fields that are present in the project copy after whitespace is collapsed. Repeating rows, details, articles, and item blocks are cloned from the first row. Short tokens that only occur inside a longer copy line are still dropped, including a `data-label` of "Hours". The part then replaces that section's body. The wrap and any `hero-visual` stay. The renderer's heading and rows are not left beside the part. The first heading in a hero part is the page `h1`.

`part_demo` compares collapsed lines. The harbor hours sentence is two copy lines joined with a space, and that joined line sits inside the contact part. A clean check still has no `part_demo` row.

A one-button part has no gap of its own. Harbor's second action was cloned flush against the first. The compose floor now gives adjacent links inside a part a 12px start margin, the same gap as the renderer hero row.

Both sites were planned, accepted, and painted again through the studio on `127.0.0.1`. Same frames and molds: demo-local `welcome-scroll` + `discover-grid`, bench-harbor-tearoom `hours-stack` + `discover-grid`. Plan folders hold `structure.json` only. `sites/demo-local`, `sites/demo-local-compose`, `sites/demo-local-ai`, and `sites/bench-harbor-tearoom` were not overwritten.

`check --project --expect-noindex`:

| Site | Pass | Fail | Warn | Skip |
| --- | --- | --- | --- | --- |
| bench-harbor-tearoom-studio | 36 | 0 | 0 | 1 |
| demo-local-studio | 35 | 0 | 0 | 1 |

The skip is still `grey_tile`. The checker's contrast line is still "lowest 4.40:1", a large-text pass. Body type is 18px. Harbor's extra pass is still `phone_bar`. There is no `part_demo` row.

`visit` on the painted pages is mode `rendered`, exit 0, on both.

demo-local-studio has four `data-sc-part` blocks: `hero-dark-band-072`, `card-collection-item-with-meta-181`, `card-compact-row-089`, and `faq-bootstrap-accordion-flush-195`. One `h1`. The hero action is Build, and it points at `#features`. The FAQ block has the five questions and answers from `faq.md`. Opening the first question shows the answer.

bench-harbor-tearoom-studio has three: `hero-dark-band-072`, `table-basic-152`, and `cta-button-group-primary-secondary-201`. The hero actions are Menu and Contact. The table has Jasmine Pearl $4.50, Assam Malt $3.75, and Peppermint Field $3.25. The contact part has the walk-in line, 14 Harbor Lane, "Open Tuesday to Sunday, 8am to 6pm. Closed Mondays.", and `tel:5550142288`. The phone bar uses the same digits.

Playwright measured both pages at 360, 390, 412, and 1280. Failures: 0. Computed contrast was lowest 5.57:1. No page overflow, no tap under 44, no empty hero row. Harbor's two hero actions have a gap at every width. The phone drawer opens. Each hero link lands on its section below the sticky header. The phone bar does not cover the footer. At 1280 the phone bar stays hidden, which is the existing desktop rule.

Both `robots.txt` files still disallow `/`. Neither folder has `sitemap.xml`. Both pages are `noindex`. Report mode is offline and the token ledger is 0.

`part_fill_selftest` exited 0 after the gap rule.

Sections the copy does not produce are still absent. demo-local has no gallery or contact copy. Harbor copy does not produce features or faq. `grey_tile` was not run as a rendered photo check. Header and footer catalog parts stay off the page: those slots have no copy fields, and the site header and the copyright line are already there. `tools apply` still writes the stored snippet. This is not a Google rank. Nothing was published. `library/ledger.json` was not written.
