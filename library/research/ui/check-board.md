Check Board

## 1. Role

Check Board. One job: turn the checker's pass, fail, warn, and skip rows into a fix list Keith can work on a phone, and stop the next step while any fail is still open.

This screen does not write copy, paint a mold, or publish. It shows the rows a built site already earned.

## 2. Evidence

Read on 2026-10-08:

- `library/research/ui/BRIEF.md`. The floors are Copy, Contrast, Chrome, Crawl, and Plus. Offline build spends no tokens. `library bind --live` was not run and is not this screen.
- `library/research/competitors/shopify.md`, in heading order: 1. Product, 2. Code libraries, 3. Mobile, 4. SEO, 5. Dynamic behavior, 6. Already in SpiderCaster, 7. Worth building, 8. Sources. No vendor HTML, Liquid, or CSS was copied.
- `lib/check.py`, only far enough to name `Report` rows. `Report.add` stores `name`, `status`, `detail`, and, when the checker has them, `failures`, `unmeasured`, and `inventory`. Status is `PASS`, `FAIL`, `WARN`, or `SKIP`. `ok()` is true only when the fail count is zero. Warn and skip do not clear a fail, and they are not a pass.
- The product command in `spidercaster.py`: `check` prints each row and `result: N pass / N fail / N warn / N skip`, then exits 0 only when `ok()` is true. `visit` and `serve` are separate commands. The visual hand in `lib/hands/__init__.py` calls the same `check_site` with `expect_noindex=True` and the project's copy text. In `lib/crew.py` a `FAIL` from that hand sets `stopped`, so the next seat does not run.

What Shopify shows a person before the page exists: nothing they approve as a plan. Heading 1 says theme generation makes up to three draft themes, then the person picks one with Try theme. Text and blocks are reviewed after they land in the editor. The person may edit, then Save. Save is not publish. The same heading says generated text can invent a product fact, generated code can miss accessibility or performance practice, and the person must review before anything is applied. No automated visual critic is named. Publish is a later, separate action. A new store starts private.

Heading 2 names Theme Check, the Liquid and JSON linter, also run as `shopify theme check`. A development theme is not the published theme. The merchant editor groups the page into Header, Template, and Footer. That is not a pass, fail, warn, and skip list, and it is not Copy, Contrast, Chrome, Crawl, and Plus.

Heading 3 states authoring floors: touch targets at least 44 by 44 px, a skip link, one h1, headings in sequence, contrast 4.5:1 for smaller text and 3:1 for larger text and icons. Those are requirements written for Theme Store themes. They are not a measured score of the Horizon demo store. A numeric Lighthouse floor was not on the excerpt opened, so that score is not public.

SpiderCaster already differs in one place. The checker is the critic, and it runs only after `index.html` exists. There is still no review surface. The CLI prints the rows and stops.

Row names `check_site` can emit, in the order the function adds them when every gate is on:

- Always, once `index.html` is present: `files_present`, `no_sample`, `no_soft_placeholders`, `no_hotlink`, `meta_basics`, `noindex_status`, `internal_links`, `site_header`, `hero_visual`, `favicon_link`, `favicon_svg`, `relative_img`, then the index phone rows `mobile_hero`, `mobile_visible`, `no_empty_panel`, `skip_link`, `scroll_margin`, and `phone_bar` only when the index has a `phone-bar` link.
- Then: `canonical`, `json_ld`, `description`, `one_h1`, `heading_order`, `img_alt`, `missing_file`, `faq_schema`, `type_floor`, `contrast`, `tap_target`, `sideways_scroll`, `mobile_nav_drawer`, `mobile_visibility`.
- Then, when the extra gates run: `slug_shape`, `photo_luma`, `svg_photo`, and `grey_tile`. A thrown gate adds `gate_error` instead of hiding it.
- Then: `token_ledger`.
- Only when copy text was passed and a hit exists: `ungrounded_claim`, `lone_about`, `invented_chrome`. A clean copy adds none of those names. Empty copy text adds none either. Absence is not a stored pass.

`mobile_spec` is added only when a spec path is passed into `check_site`. `python spidercaster.py check` does not pass one. `reproducible` is a different entry, `python -m lib.check --reproducible`. It is not a row on this board.

If `index.html` is missing, the only row is `files_present` with status `FAIL`, and the function returns. Later groups were not run. They are not passes.

`grey_tile` is always `SKIP`. The detail says a grey tile standing in for a photo is a rendered condition and static CSS cannot prove it absent. The status stays `SKIP`. It is never a pass and never a fail.

Other skips that must stay skips: `photo_luma` when Pillow is not installed (`not-run`), `mobile_nav_drawer` when no page has a nav landmark (`not-run`), `mobile_spec` when the spec has no usable phone profile, and `noindex_status` when the caller did not say whether noindex was expected. This screen always says expected noindex, so that last skip is the path it refuses to take.

Warn is a real status. `contrast` warns when text was not measurable. `tap_target` warns when a box only straddles 44 px. Mobile rows warn when something is not measurable or is only an inventory review. `photo_luma` warns when a raster file will not open. `token_ledger` warns when `report.json` is missing or unreadable. `noindex_status` warns only if the caller expected an indexable site and the pages are still noindex. Warn is not a pass. The engine still treats `ok()` as true when the fail count is zero.

`failures` on a row is the untruncated list. The printed `detail` is clipped (about six or eight items, then a count). The fix list uses `failures` when the row has them, and does not invent the lines the detail dropped.

This pass did not run `check` or `visit` on a built site. No site is claimed to pass or fail. Those results are not public.

## 3. Screen

The board is one localhost page. Keith works top to bottom. The five group headings are Copy, Contrast, Chrome, Crawl, and Plus, in that order. Rows keep the order `check_site` emitted them inside the group.

Controls, in order:

1. Site. A built folder that already has, or is supposed to have, `index.html`. The list is the site folders already under `sites/` for the two projects that have copy: `sites/demo-local`, `sites/demo-local-compose`, `sites/demo-local-ai`, and `sites/bench-harbor-tearoom`. `sites/demo-local-plan` is only a `structure.json` from `compose --plan`. It is not offered. `sites/assembled` is the catalog, not a project site. It is not offered. Fleet domains are not offered.
2. Project. `projects/demo-local` or `projects/bench-harbor-tearoom`, matched by name to the site. The pair is required. The control has no empty choice.
3. Check. Runs `python spidercaster.py check <site> --project <project> --expect-noindex`. The page shows the same counts the command prints.
4. The five groups, then the fix list. The first fail in group order is marked Current.
5. Re-check. The same command again. Nothing is marked fixed until this returns.
6. Look. Runs `python spidercaster.py serve <site>` on 127.0.0.1, default port 4173. Preview only. Look is not the next step. It stays available while a fail is open so the failure can be seen.
7. Measure. Under Plus. Runs `python spidercaster.py visit <site>`. It does not change Report rows or the counts.
8. Next. Leaves this board for a later studio step. It does not run a command that publishes.

How a row becomes a fix:

- `PASS` stays in its group. It is not a fix. It does not enable Next by itself.
- `FAIL` becomes one fix. The item shows the group, the row name, the detail, and every `failures` entry the row stored (`file`, selector, measured, required). `unmeasured` stays attached as not a pass. The first fail in the order below is Current. A fail stops the next step: Next stays disabled while any fail remains. Later fails stay on the list so they are not hidden. Clicking a later fail does not make it Current. Only Re-check can move Current, and only if that row is no longer `FAIL`.
- `WARN` stays in its group, labeled not a pass. It is not a fix. It does not stop Next. It is not painted as `PASS`.
- `SKIP` stays in its group as skip. It is not a fix. It does not stop Next. It is not painted as `PASS`. `grey_tile` is this case on every run. The board does not offer a photo, a tile color, or a "mark passed" control for it.

If the only row is `files_present` `FAIL`, that item is the whole fix list. The other four groups say they were not run. They are not filled with passes.

Copy claims are different from a skip. `ungrounded_claim`, `lone_about`, and `invented_chrome` appear only as fails. When the project was passed and those names are absent, the Copy group says no claim row, which means the checker found no hit. When the project was not passed, those names are also absent, and that is not the same fact. This screen refuses Check without a project so the two cannot be confused.

Group membership:

- Copy. `no_sample`, `no_soft_placeholders`, `no_hotlink`, and, only when emitted, `ungrounded_claim`, `lone_about`, `invented_chrome`. These are the claim and placeholder rows. Visible text must already be in the project copy. Sample, lorem, placeholder, a testimonial, a customer review, award-winning, a star rating, a lone About, and the chrome phrases the checker already names are fails, not a prompt to write new lines.
- Contrast. `contrast` only. Floor is 4.5:1, and 3:1 for large text. A warn here means something was not measurable. It stays a warn.
- Chrome. `type_floor`, `tap_target`, `site_header`, `skip_link`, `scroll_margin`, `hero_visual`, `mobile_hero`, `mobile_visible`, `no_empty_panel`, `favicon_link`, `favicon_svg`, `phone_bar` when present, `relative_img`, `missing_file`, `svg_photo`, `photo_luma`. Body floor is 18 px. The other text floor is 16 px. Tap floor is 44 px. `photo_luma` skip (Pillow missing) stays a skip, same rule as grey tile: not a pass, and not an install button.
- Crawl. `files_present`, `meta_basics`, `description`, `one_h1`, `heading_order`, `canonical`, `json_ld`, `faq_schema`, `img_alt`, `internal_links`, `slug_shape`, `noindex_status`. One h1 on the index. `heading_order` fails a skipped level outside `data-sc-part`. Canonical is relative. JSON-LD is WebSite with no `aggregateRating`. Description must be present. With `--expect-noindex`, a missing noindex meta is a fail, not a skip.
- Plus. `sideways_scroll`, `mobile_nav_drawer`, `mobile_visibility`, `grey_tile`, `token_ledger`, `gate_error`, and `mobile_spec` only if a future caller actually passed a spec. Any row name this list does not know also lands here, still counted, so a new fail cannot vanish. `grey_tile` stays skip. `token_ledger` reads the build's `report.json`. A warn there is not a reason to start a build. Measure's visit result sits beside this group and is not mixed into the counts.

`sideways_scroll` is the static overflow row at 360, 390, and 412. `mobile_nav_drawer` is the drawer row: more than four primary nav links need a toggle that opens and closes in the checker's static simulation. No nav is a skip, and it stays a skip. Visit, when its mode is `rendered`, is the separate measure at 390 and 1280. When Playwright does not launch, visit stays `static` and that is not a failure and not a rendered pass. Those widths are then not public.

The checker does not emit a `robots.txt` row or a sitemap row. Plus does not invent one. A noindex build's `Disallow: /` and the missing sitemap are a property of the build writer, not a pass printed by Check.

Refused on this screen:

- Publish, `library bind --live`, `build --indexable`, `--host`, and `--expect-indexable`.
- Next while any row is `FAIL`, while Check has not been run, or while the site and project pair do not match.
- A fix button, a generate button, a rewrite of `copy/`, or any sentence written to clear `ungrounded_claim`, `no_sample`, or `lone_about`.
- Turning `grey_tile` or any other skip into a pass, a fail, or a photo task.
- Turning a warn into a pass, or hiding a warn.
- Filling groups that did not run after `files_present` failed.
- Marking a fail fixed without Re-check.
- Install Pillow. Install Playwright. A chat button. React, Tailwind, shadcn, Liquid, or Theme Check.
- `shipcheck` as a ready light. `python -m lib.check --reproducible`. `--mobile-spec`. Both can run a second build or judge a foreign capture. They are not Check.
- Fleet domains, `warmth-authority`, and any site that is not one of the four folders named above.

## 4. Already here

`python spidercaster.py check <site> [--expect-noindex | --expect-indexable] [--project <dir>]` is the command. It prints every row and the four counts. It does not write a fix list and it does not write `report.json`. The file `report.json` in a site folder is the build ledger. `token_ledger` only reads it.

`check_site` in `lib/check.py` is the function. The visual hand calls it with noindex expected and with copy from `projects/<name>/copy/`. The MCP tool `tool_validate_run` calls it quietly and returns `ok`, `counts`, and `checks` (the rows). A fail there is the same fail as on the CLI.

`python spidercaster.py visit <site>` returns `ok`, `mode`, and `failures`. Missing Playwright leaves `mode` static and is not a failure. `python spidercaster.py serve <site>` only hosts the folder on localhost.

`lib/crew.py` already stops the next seat when the visual hand returns `FAIL`. The deployer row is then `FAIL` as well. The ticket is not `ok`. This board is the human view of those rows. It does not add a second checker.

`python spidercaster.py shipcheck` runs the app's own selftests. It does not list site rows. It is not the fix list.

Module-only flags (`--typography-only`, `--tap-only`, `--mobile-only`, `--mobile-spec`, `--reproducible`) are not on `spidercaster.py check`. The board does not grow them.

## 5. Proposal

The smallest surface is one page on 127.0.0.1, standard library only, no new package.

The page is not the customer site. `serve` keeps hosting the built folder and nothing else. A second localhost handler, also stdlib, does three things the CLI already does:

- Check calls `check_site` the way the visual hand does: the chosen site, `expect_noindex=True`, quiet, and copy text from the matched project. It shows `rows` and `counts()`. The button's caption is the CLI line so Keith can run the same command in a terminal.
- Look starts `serve` for that folder only.
- Measure calls `visit_site` and shows `mode` and `failures` beside Plus, separate from the counts.

The handler does not write HTML into the site, does not write `copy/`, and does not write a ticket. Re-check replaces the rows on the page. It does not patch them.

Next has no command behind it. When the latest Re-check has zero fails, Next only says the check passed and the site is still noindex. Passing Check is not publish.

No React, no Tailwind, no shadcn, no chat control, no theme generator.

## 6. 4Cs+ test

Judge the board on a phone-width window, and judge a built page only by the checker.

Phone window, 360, 390, and 412 px wide:

- The five headings stack. The fix list is above the fold. Current is the first fail and is visible without sideways scroll.
- Next, while stopped, still shows the word that it is stopped. The stopped state is text, not color alone.
- Look, Check, and Re-check are at least 44 px. Body text on this page is at least 18 px. Chrome labels are at least 16 px. Contrast of that text meets 4.5:1.
- A skip, including `grey_tile`, stays readable as the word skip. It is not a grey rectangle standing in for a result.
- Warn stays the word warn.

None of those phone measures have been taken. The studio page does not exist yet. Until Check and, if a browser launches, visit are run on that page, the phone result is not public.

Built page:

- The board does not edit `sites/demo-local`, `sites/demo-local-compose`, `sites/demo-local-ai`, or `sites/bench-harbor-tearoom`.
- A built page passes this screen only when Check on that folder, with its matching project and `--expect-noindex`, returns zero fails. That run was not done here. Outcomes for those folders are not public.
- Plus on the built page is `sideways_scroll` and `mobile_nav_drawer` from that same Check. Visit's 390 and 1280 numbers count only when `mode` is `rendered`. A static visit is not that measure.
- `grey_tile` on that run is still skip. A built page is not failed for it, and it is not passed for it.
- Crawl on the built page includes one h1, `heading_order`, a relative canonical, WebSite JSON-LD, no `aggregateRating`, and a description. The board does not add a sitemap to make Crawl look finished.

## 7. Risks

- Writing a sentence to clear a fail invents copy. `ungrounded_claim`, `no_sample`, `no_soft_placeholders`, `lone_about`, and `invented_chrome` are cleared only by removing text that is not in `copy/`, or by text the human already put in `copy/` outside this screen. The board has no field for that.
- Generating a photo, or painting a tile, to clear `grey_tile` hides a skip. The row stays skip. `photo_luma` skip is the same trap if someone installs Pillow from the board and calls the new result a pass without reading it.
- Omitting `--project` hides claim fails, because those rows are never added. The empty Copy group would look calm. Check without a project is refused.
- Omitting `--expect-noindex` leaves `noindex_status` as skip even when the pages are indexable. The screen always sends it. `--expect-indexable` would warn or pass an indexable site and is refused.
- Showing only the clipped `detail` hides the rest of a long `failures` list. The fix list uses the list on the row when it is there. Where the checker stored only a clipped detail, the board shows that clip and does not guess the missing lines.
- Treating warn as pass hides unmeasured contrast, taps, and overflow. Warn stays on the group.
- Painting later groups as pass after `files_present` fails hides that they were not run.
- Disabling Look as well as Next would hide the failure on the page itself. Look stays. Next stops.
- A green Next that calls `library bind --live`, `build --indexable`, or `shipcheck` would deploy or pretend the app is ready. Next calls none of them. Passing Check does not publish. `warmth-authority` stays unbound.
- Pairing a site with the other project's copy would fail or clear claims for the wrong text. The site and project must match by name.
- Counting visit's static mode as a pass at 390 and 1280 would publish an unmeasured claim. Static visit is not that pass.
- A `robots.txt` or sitemap line marked pass would invent a row the checker does not emit.
- Running `--reproducible` or a token build from this screen to clear `token_ledger` spends a build the checker did not ask for. `token_ledger` warn does not start a build.
