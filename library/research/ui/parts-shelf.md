Parts Shelf expert

## 1. Role

Parts Shelf is the studio screen for choosing one built catalog part and putting it on a page that already exists. Its one job is to list parts whose kind is header, hero, card, faq, cta, or footer, then apply or replace that one part through the tools command. It does not fetch remote component HTML. It does not plan a site, and it does not publish.

## 2. Evidence

Read on 2026-10-08, from disk, not from a new vendor fetch:

- `library/research/ui/BRIEF.md`. Studio gap, the 208 catalog parts, and the 4Cs+ floors.
- `library/research/competitors/v0.md`. What v0 shows before a page exists.
- `lib/part_pick.py`. Which kinds compose auto-picks, and which it never picks.
- `lib/tools_index.py`, `lib/tools_apply.py`, `lib/part_swap.py`, `lib/part_fill.py`, `lib/compose.py`, `lib/mold_paint.py`, `lib/heading_rank.py`, `lib/serve.py`, and the `tools`, `parts`, `compose`, `check`, and `serve` parsers in `spidercaster.py`.
- The local catalog file named in `lib/tools_index.py` (`<local-path>`), joined to built part folders the same way `load_catalog` and `built_dirs` already join them. That join was run on this machine. `tools apply`, `check`, and `visit` were not run. Pixel widths of a studio window were not measured.

The join on this machine: 208 catalog rows, 208 built, 0 missing. Routes: `tools-hooks-blocks` 80, `tools-headers` 44, `tools-popups-callouts` 43, `tools-sidebars-widgets` 41. Rows whose kind is one of the six shelf filters: header 12, hero 11, card 14, faq 8, cta 10, footer 12. That is 67. The other 141 built rows are not on this screen. `cta-bar` is 2 and is not `cta`. `sticky-header` is 5 and is not `header`. `feature-grid` is 2 and is not `card`. `lib/part_pick.py` says feature-grid is unused because card is the kind for the card-like sections.

v0, from `v0.md`, is the competitor file for this shelf. Before the page exists, a person sees a chat or an empty project and types a prompt. The usual path is prompt, then a generated app, then iteration. Plan Mode is optional. The default starter is a Next.js app with shadcn/ui and Tailwind, not a section catalog inside one static theme. A registry can be opened by URL (`v0.dev/chat/api/open`). Named items in the public starter include `hero` and `brand-header`. Those are files the model can be handed. They are not a local list of 208 parts, and v0 does not publish a map from the word "hero" to a filename. The preview is the review. Publish is a later control and it deploys. This screen does not copy that path.

`sites/assembled/catalog.html` is a different list. Its title says "Parts library (383)". That number was not re-counted here. That page is a built noindex site from `parts assemble`. It is not this shelf.

## 3. Screen

The human acts in this order. The window is one column. The list is catalog ids, not component HTML.

1. Site. Three choices: `sites/demo-local` with project `projects/demo-local`, `sites/demo-local-compose` with project `projects/demo-local`, and `sites/bench-harbor-tearoom` with project `projects/bench-harbor-tearoom`. Page and Out are that folder's `index.html`. Project is filled from the choice. It is not a free path.
2. Kind. Six controls, one selected: Header, Hero, Card, FAQ, CTA, Footer. The list stays empty until one is selected. The match is the catalog kind string, exact, lowercase.
3. The list. One radio per built row of that kind. Each row shows `catalog_id`, kind, route, and status `built`. Nothing else. No snippet, no thumbnail, no iframe, no name turned into a sentence.
4. Mold. None, `discover-grid`, or `clarify-mix`. None means the command gets no `--mold`.
5. Apply. Runs `tools apply` with that catalog id, `--page`, `--out`, and `--project`. No `--replace`. A zero exit means the part was appended immediately before `</body>`. It does not mean the part was moved into a hero, card, faq, cta, header, or footer section.
6. Replace. Same command plus `--replace`. A zero exit means the style and div already marked with that same catalog id were swapped. It does not remove a different id.
7. Result. Shows the exit code and the command text. On exit 0, runs `check` on that site folder with `--project` and `--expect-noindex`, and shows the checker text, including failures. The line "applied" is not a check pass.
8. Serve. Only after the human asks, and only for that site folder. It runs `serve`, which binds `127.0.0.1`. It is a preview. It is not a pass, and it is not publish.

A reload reads the catalog join again. It does not apply.

Refused, with no control and no hidden path:

- Any kind other than those six, including `sticky-header`, `comparison`, `table`, `feature-grid`, `cta-bar`, `schema-jsonld`, `popup`, `sidebar`, and the rest of the 141.
- A row whose status is not `built`, an empty catalog id, or an id typed by hand.
- Fetching component HTML, a registry URL, a shadcn file, or a skill from skills.sh. The shelf never requests those.
- Showing `snippet.html` or `template.html` in the window. Those files can hold words that are not project copy.
- Replace of a different catalog id, or a control named for a section type (`features`, `about`, `contact`, and the rest).
- A second `*.html` name in the site folder. `check` reads every html file there.
- `sites/assembled`, `sites/demo-local-ai`, a fleet domain, or any project other than the two copy projects.
- Mold `warmth-authority`.
- `compose`, `parts assemble`, `build --indexable`, a sitemap, `library bind --live`, or a chat box.
- Serve of any host other than `127.0.0.1`, and serve when Apply or Replace did not exit 0.

## 4. Already here

`python spidercaster.py tools list` prints each catalog row as catalog id, route, status, and part folder when built. It does not print kind. Kind is a field on the catalog row. `lib/tools_index.py` does not put kind on the list record. The shelf can filter only by reading that local catalog and joining it to the list. That read is the file the index already uses. It is not a fetch of component HTML.

`python spidercaster.py tools apply CATALOG_ID --page PAGE --out OUT [--replace] [--mold ID] [--project DIR]` writes one HTML file. With `--replace` absent, the part is wrapped and inserted immediately before `</body>`. With `--replace`, `replace_part` swaps the existing `data-sc-tool` style and `data-sc-part` div for that same id, and leaves every other part. The command refuses a missing or not-built id, a part with no `snippet.html` or `template.html`, a part with no `part.css`, a missing page, a page with no `</body>` on append, a replace when that id is not on the page (`part not on page`), a destination listed in the project's `lock.txt`, and a write that would drop noindex, the favicon link, or the site header. The wrapper is local. The fragment preference is `snippet.html`, then `template.html`. No network.

`--mold` reads `library/molds/<id>.json` and passes palette and type lead only. `paint_css` recolors `#14213d` and sets a system font stack on `[data-sc-part]`. It refuses a bad palette, a contrast pair that fails 4.5:1 against both white and `#1a1a1a`, and CSS that contains `@import` or `url(http`. It does not bind a mold live.

`bind_hashes` rewrites an `href="#..."` whose id is not on the page to `href="#main"` when `id="main"` exists. That is a link rewrite, not a copy fill. This report did not measure whether `check` flags those rewritten links.

`tools apply` does not call `part_fill`. The fragment is written as stored, aside from that hash rewrite and an optional mold paint of the CSS. `fill_fragment` and `copy_block` run on the compose path only, and only for strings that are already exact substrings of project copy.

`pick_part` and `pick_chrome` are not this screen. They choose the smallest built catalog id for a section type or a chrome slot. Section route `tools-hooks-blocks`: hero to `hero`; features, stats, steps, gallery, testimonials, about, team, and logocloud to `card`; pricing to `comparison`, then `table`; faq to `faq`; cta and contact to `cta`; menu to `table`. Chrome route `tools-headers`: header to `header`, then `sticky-header`; footer to `footer`. An override wins for any built id, even off kind. `schema-jsonld`, `popup`, and `sidebar` are never auto-picked, and those routes are not searched. The `compose` command does not pass `part_overrides`. A human cannot aim compose at one of the 67 shelf ids. A later compose to the same folder plans again and can overwrite the page this shelf just wrote.

`parts scan` and `parts assemble` index manifests and build a noindex site that lists them. They do not apply one catalog id. `serve` only hosts a folder that already has a site. `lib/tools_selftest.py` expects 208 rows. That selftest was not run for this report.

## 5. Proposal

The smallest surface is one localhost page, standard library only, same bind as `lib/serve.py` (`127.0.0.1`, no new package, no React, no Tailwind, no shadcn). It is not `serve` of the site folder. It does not live inside the site output. It does not edit the engine, the catalog, or part folders.

It shells out only to `python spidercaster.py tools list`, `tools apply`, `check`, and, when the human uses Serve, `serve`. Kind comes from the local catalog file joined by catalog id to the list rows. A row the join cannot prove as one of the six kinds is not shown and is not passed to apply. The screen does not add a `--kind` flag. The screen does not open snippet files to paint a preview.

Apply and Replace are the two write commands in section 3. Both pass `--project` so `lock.txt` is consulted. Out is the existing `index.html` only. The screen does not copy the site to a new folder and does not invent a second page. After a zero exit it runs `python spidercaster.py check SITE --project PROJECT --expect-noindex` and prints the report. A checker failure stays on screen. There is no revert command, so the screen does not pretend to undo the write. Serve is the existing preview command and nothing more.

`discover-grid` and `clarify-mix` are the only mold ids the control can pass. `warmth-authority` is not in the control. The screen does not call `compose`, so it does not bind a mold and it does not auto-pick.

## 6. 4Cs+ test

Two judgments. The studio window is not the site. The built page is the site after Apply or Replace. No studio window was measured here. The floors below are the pass rule, not a result.

Phone-width window, at 360, 390, and 412:

- Copy. Visible text is catalog ids, the six kind names, route, status, the three site names, the two mold ids, and the control names in section 3. No SAMPLE, lorem, placeholder, review, award, or sentence taken from a part file.
- Contrast. 4.5:1 for text, 3:1 for large text. Not measured here.
- Chrome. Body 18px, chrome 16px, tap targets 44px for the six kind controls, each part radio, Apply, Replace, and Serve. One studio h1, the words Parts Shelf. A skip link to the list. No site hero is required on this window. A sticky kind bar is refused if it covers a row or leaves a target under 44px.
- Crawl. This window is not the site. It does not write a canonical, WebSite JSON-LD, `robots.txt`, or a sitemap. It stays on 127.0.0.1.
- Plus. No sideways overflow at those three widths. Kind controls wrap. They are not a horizontal scroller. The part id may wrap. The window does not load remote HTML to do it.

Built page, after Apply or Replace writes `index.html`:

- `check` with `--project` and `--expect-noindex` is the judge. Claims must already be in that project's copy. Contrast floors, body 18px, chrome 16px, tap 44px, sticky header, skip link, hero visual, favicon, one h1, no skipped heading outside a catalog part, relative canonical, WebSite JSON-LD, no aggregateRating, description present, no sideways overflow at 360, 390, and 412, drawer opens and closes. Headings inside `data-sc-part` are catalog chrome, not the copy outline (`lib/heading_rank.py`).
- `visit` measures 390 and 1280 only when Playwright is installed. It was not run. Not measured here.
- A noindex build's `robots.txt` is `Disallow: /` when that build wrote one. This screen does not write `robots.txt` and does not write a sitemap. The page must still say noindex. Apply already refuses a write that drops it. Check is still required.
- Appended markup sits before `</body>`. A check that expected the part inside a named section must fail in the open if the section does not contain it. The shelf must not report that as a placed hero, card, faq, cta, header, or footer.
- Sample text, lorem, a placeholder, a hotlinked image, or a remote CSS import that survives into the page is a check failure. The shelf shows it. It does not strip the snippet to hide it.
- Harbor Tea Room is a synthetic bench. A pass on that folder is still noindex. It is not a license to index or deploy.

## 7. Risks

- Calling Replace what is really Apply. Apply appends a second part and leaves the old one. The page can show two heroes. The result line must say "appended before </body>" and must not say the old part was removed.
- `--replace` on an id that is not wrapped on the page exits with `part not on page` and writes nothing. Treating that as a successful swap, or retrying without `--replace`, hides the refusal.
- `tools apply` will append any built id, including popup and sidebar parts. The command is wider than this screen. The screen must not pass an id that failed the six-kind join. A hand-typed id is that bypass.
- The fragment is not filled from copy. A shelf preview of the snippet, or a quiet apply, can put SAMPLE, lorem, or other ungrounded words on the page. v0's generated copy and its registry fetch do that kind of invention. This screen has no preview and no fetch. Check is what makes the bad words visible. A green "applied" with the checker hidden is the failure.
- `bind_hashes` can turn a missing in-page link into `#main`. That can look like a fixed link. It was not measured as a check row. The result must not call it a link pass.
- `compose` to the same folder after a chosen apply picks the smallest id again and can overwrite the file. The screen does not run compose. It also does not add a `part_overrides` flag. That flag is not on the command, and an override would accept an off-kind id.
- Writing `applied.html` beside `index.html` makes `check` judge a second page. That is refused so a broken extra file cannot be ignored, and so a new page is not invented.
- There is no undo. After a zero exit the old `index.html` is gone. The screen must not offer a backup it does not write, and it must not restore from a snippet by rewriting the page itself.
- `parts assemble` and the 383-title catalog are a different set. Applying from that list would use the wrong ids.
- Painting `warmth-authority` uses the mold that is live on movelixir.com. It is not a choice. `library bind --live`, `build --indexable`, and a sitemap control would publish. Harbor must not be indexed.
- A chat button, a React studio, a Tailwind skin, or a fetched shadcn block is the v0 path. The page stays a standard-library form on localhost. The part HTML stays the local file `tools apply` already reads.
