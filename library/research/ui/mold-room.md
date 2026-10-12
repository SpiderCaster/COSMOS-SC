Mold Room

## 1. Role

Mold Room is the studio screen for one package mold. Its job is to let Keith pick one mold, read that mold's stored palette and type lead, and refuse a new live bind of warmth-authority. It does not generate a palette, does not edit the engine, and does not publish.

## 2. Evidence

Read for this note: `library/research/ui/BRIEF.md`, `library/molds/discover-grid.json`, `library/molds/warmth-authority.json`, `library/molds/clarify-mix.json`, `library/ledger.json`, `library/research/competitors/webflow.md`, `library/research/competitors/wix.md`, the bind and paint paths in `lib/library.py`, `lib/mold_paint.py`, `lib/mold_panel.py`, `lib/compose.py`, and `lib/render.py`, plus the library, compose, and crew commands in `spidercaster.py`. The painted example already on disk is `sites/demo-local-compose`. This note did not run `library bind --live`, did not run compose, and did not publish.

The package has three molds. Doctor expects that count. The one this screen paints is discover-grid.

- discover-grid is a mutation of warmth-authority. Palette `#2a6f8f`, type lead `sans`, nav `top-bar`, template `modern`. The parent is warmth-authority. The note on the file says palette, type lead, and nav all change. That is the save rule for a mutation: exactly one parent, and those three fields must change. It is not an OceanWP or GeneratePress demo.
- warmth-authority is a scratch mold. Palette `#c8923e`, type lead `serif`, nav `segmented`, template `editorial`. No parents. `library/ledger.json` marks it live on movelixir.com.
- clarify-mix is a mix of those two. Palette `#6b4c3b`, type lead `slab`, nav `one-page`. It is not live. It is not the mold this screen paints. A mix cannot wear a vendor frame.

The ledger also has discover-grid as not live on demo-hero.example and on harbor-test.example, and clarify-mix as not live on demo-stage.example. Those names are ledger rows, not copy projects. The only projects with real copy are `projects/demo-local` and `projects/bench-harbor-tearoom`.

`sites/demo-local-compose/structure.json` already records `mold_id` discover-grid, with frame welcome-scroll from an earlier compose. `site.json` stores accent `#2a6f8f`. The built index uses that hex as `theme-color` and as the accent, and each catalog part starts with `[data-sc-part]{font-family: "Segoe UI", system-ui, sans-serif;}`. That is the sans stack in `lib/mold_paint.py`. The page heading and body stack is a different string, chosen from template `modern` inside `build_palette`, not from the type-lead field. `robots.txt` is `Disallow: /`. No sitemap is in that folder.

Paint does two things with the one hex. `compose` copies `palette` onto `theme.accent` and `template` onto the theme. `paint_css` replaces the part token `#14213d` with the mold hex and prefixes the type-lead stack. It refuses a palette that is not `#rrggbb`, a type lead outside serif, sans, slab, and mono-display, a remote `@import` or `url(http…)`, and a palette where neither white nor `#1a1a1a` reaches 4.5:1. It does not invent a second hex. `mold_panel` reads the same tokens and returns `error` `live` if `live` is anything but unset. It does not write and does not go live.

Contrast measured in this note with `lib.render.contrast_ratio`, rounded to two decimals. Not a published audit. `#2a6f8f` on `#ffffff` is 5.57:1, so the painter allows the mold. The same hex on `#1a1a1a` is 3.12:1, under the 4.5 body floor. On the composed page background `#0a0e14` it is 3.47:1. The renderer keeps the raw accent for fills and borders. The accent text already written on that page is `#568ea5`, measured here at 5.35:1 on `#0a0e14`, 4.97:1 on `#111722`, and 4.62:1 on `#161e2c`. Those derived values are the existing renderer. This screen does not generate them and does not offer them as a second palette. A fresh `check` of that folder was not re-run here. A rendered `visit` at 390 and 1280 was not run here. Both stay not public as a new pass.

Webflow, from `library/research/competitors/webflow.md`. Before the page exists, the person starts at Dashboard, New site, AI Site Builder, and a description that can name colors, fonts, purpose, and goal, then Generate. That first Generate is a structure of pages and sections, not finished pages. The person can add a page, drag sections, delete, duplicate, or Change section, then Generate site builds the designs and what the article calls contextually relevant content. Named colors, hex codes, and fonts are mapped onto Webflow's theme rather than copied exactly. On the canvas they can pick or fine-tune a theme, and that change updates colors, typography, sections, and related styles across generated pages. The builder page says to preview before you publish. The publish click path is not on that article. A ban on invented reviews is not public there. SpiderCaster does not map a sentence onto a theme, does not fine-tune a new palette, and does not write starter sentences.

Wix theme colors, from `library/research/competitors/wix.md`. On the description door the person may add colors and style, then Generate Site builds pages, layouts, colors, and starter content in one pass. A separate plan approved before that pass is not public on the creation article. The ChatGPT door is the one that shows a description to review before Create Site. Brand is one kit in the Site Brand panel. The owner picks nine colors: Base 1 and 2, Shade 1 to 3, Accent 1 to 4. Switching the brand kit changes all nine. Semantic colors follow that palette until edited. The Wix doc publishes hex values for fixed system colors (success, error, alert, default dark, default light). Those hex values are not copied here. They are not a measured contrast result. An AI Harmony site cannot be switched onto another template. SpiderCaster is the smaller rule: one stored `#rrggbb`, one type lead, and no second live use of a mold that is already live.

## 3. Screen

The human actions, in order. One mold is selected at a time. The paint this screen is for is discover-grid.

1. Open Mold Room on 127.0.0.1. The page is the form, not a public site.
2. Project. A select with two options only: `projects/demo-local` and `projects/bench-harbor-tearoom`. Fleet domains are not listed. Paint stays refused until one project is chosen.
3. Package mold. A radio group fed by the package molds: discover-grid, clarify-mix, warmth-authority. Vendor frames are not in the group. The selected radio for this screen is discover-grid.
4. Palette. A read-only field. For discover-grid it shows `#2a6f8f`. It is not an input. There is no Suggest, no swatch generator, and no second hex.
5. Type lead. A read-only field. For discover-grid it shows `sans`, and beside it the stack the painter writes: `"Segoe UI", system-ui, sans-serif`. The other leads stay the fixed local stacks already in the painter (serif, slab, mono-display). No font is downloaded.
6. Live use. A text status, not a color by itself. discover-grid reads as not live. The ledger drafts on demo-hero.example and harbor-test.example stay visible so they are not mistaken for a live owner. warmth-authority reads: mold warmth-authority is already live on movelixir.com.
7. Plan. Writes `structure.json` only, for the chosen project and the one selected mold. The result shows `mold_id` and the output path before any HTML. It does not pass a frame, does not pass `--indexable`, and does not pass a host.
8. Paint. Builds the noindex site from that project's real `copy/` and paints the one mold. It does not change Live use. It does not bind the ledger. It does not add the section names stored on the mold. discover-grid lists hero, features, steps, faq, and contact. Those names are not pages and not copy. Sections stay whatever the copy already produced.
9. Preview. Serves the painted folder on 127.0.0.1 only, after Paint has an `index.html`.
10. Live bind. A separate button, never pressed by Plan, Paint, Preview, or this research. If the selected mold is warmth-authority, the button does not submit. The visible line is `bind refused: mold warmth-authority is already live on movelixir.com`. Selecting warmth-authority still shows its palette `#c8923e` and type lead `serif`, so the refusal is about a new live use, not about hiding the mold.

Also refused on this screen: a typed or generated palette, `library mold` (that command saves a new mold), a fourth mold, a vendor frame, a fleet domain, more than one mold on the same paint, `--live` on the paint command, `--indexable`, a sitemap host, and `mold_panel` with `live` set. Crew does not publish. A crew job whose mold is already live fails the bind hand with the same already-live sentence and does not continue.

## 4. Already here

There is no studio screen. These commands and files are the screen's parts.

- List. `python spidercaster.py library list` prints each package mold's id, origin, type lead, and nav. It does not print the palette. The hex is the `palette` field in `library/molds/<id>.json`. `mold_panel` returns `palette` and `type_lead` and fails with `live` if asked to go live. `package_manifest` also carries the hex, for package molds only.
- Choose and paint. `python spidercaster.py compose projects/demo-local --mold discover-grid` loads that JSON, sets the accent and the template, and runs `paint_css` on each inserted part. `--plan` writes `structure.json` and no HTML. The default folder is `sites/<project name>-compose`. `compose` does not write the ledger. `python spidercaster.py tools apply CATALOG_ID --page PAGE --out OUT --mold discover-grid` passes palette and type lead through for one part. It is not the whole-page paint.
- Refuse the second live use. `python spidercaster.py library bind --site SITE --mold warmth-authority --live` calls `Library.bind`. If another ledger row has that mold with `live` true, it raises `mold warmth-authority is already live on movelixir.com` before it saves. The CLI prints `bind refused:` plus that sentence and exits 2. The same owner check refuses any mold or vendor frame already live on a different site. Binding the same site again is not a second site. This note did not run the command.
- Crew. `run_job` sets `live` false and still asks `live_conflict` before the bind hand. warmth-authority fails that hand. The deployer does not publish. The publish sentence on the ticket is a Keith click: `library bind --live`. No seat is given that command.
- Preview. `python spidercaster.py serve <site folder>` listens on 127.0.0.1. The default port is 4173. `check` and `visit` judge the built folder. They do not choose a mold.

`library list` showing type lead without the hex is why the screen reads the mold file. Guessing a color from the list line would invent a palette.

## 5. Proposal

The smallest surface is one localhost form, standard library only, same bind as `lib/serve.py`: 127.0.0.1, not 0.0.0.0. No new package. No React, no Tailwind, no theme kit, no chat. It does not edit `lib/`. It shells out to the commands above.

The form is not the site preview. It uses another port on 127.0.0.1 so Preview can keep port 4173 for the built folder. The form's only write paths are the compose output Keith has just been shown, and, only if Live bind is actually pressed for a mold that is not already live, the ledger. This research presses neither.

On each radio change the form reads `library/molds/<id>.json` and fills Palette and Type lead. It does not call `readable`, `build_palette`, or `library mold`. It does not add background, text, or link hexes. Wix's nine colors and Webflow's theme fine-tune stay off this screen.

Plan runs `python spidercaster.py compose <project> --mold <id> --plan --out <shown folder>`. Paint runs the same command without `--plan`. Neither command receives `--frame`, `--indexable`, `--host`, or `--live`. The destination is on the form before the click. For demo-local the existing folder `sites/demo-local-compose` already holds this mold plus frame welcome-scroll. Painting it again with no frame would replace that file. The form names that path so the overwrite is not silent.

Live bind is not on those buttons. For warmth-authority it is refused in the form, with the CLI sentence visible, and a submit is not sent. If a submit were sent anyway, the CLI exits 2 and does not save. For a mold that is not live, the button remains a separate Keith click, `python spidercaster.py library bind --site <site> --mold <id> --live`, with an empty site refused. This screen does not invent the site name and does not press the button.

Preview runs `python spidercaster.py serve <shown folder>` only after `index.html` exists.

## 6. 4Cs+ test

Phone-width window, the form itself, at 360, 390, and 412. No sideways overflow. One h1, the room name. A skip link lands on Package mold. The header sticks. Body text is 18px. Labels and the refusal line are at least 16px. Project, each mold radio, Plan, Paint, Preview, and Live bind are at least 44px. The refusal is text in the column, not a color and not a line inside a closed drawer. Palette `#2a6f8f` as text must clear 4.5:1 on the form background, or the form uses the page text color that already clears it. Measured page text `#e9eef6` on `#0a0e14` is 16.6:1. Do not put the raw accent on `#1a1a1a` and call it body text. That pair measured 3.12:1. The form is not a composed marketing page. It does not grow a hero, a review, or a sitemap in order to look like one.

Built page, after Paint of discover-grid on one of the two copy projects. `python spidercaster.py check <folder> --expect-noindex --project <project>` is the judge. Copy: visible claims come from that project's `copy/` only. No SAMPLE, lorem, placeholder, invented review, or award. Contrast: 4.5:1, large text 3:1. The part fill `#2a6f8f` on white measured 5.57:1 here. White on that fill measured 5.57:1. The raw accent on the dark page background does not clear 4.5:1. The check fails the page if the rendered text misses the floor. Chrome: body 18px, chrome 16px, tap 44px, sticky header, skip link, hero visual, favicon. Crawl: one h1, no skipped heading level outside a catalog part, relative canonical, WebSite JSON-LD, no aggregateRating, description present. Plus: no sideways overflow at 360, 390, and 412, and the mobile drawer opens and closes. `python spidercaster.py visit <folder>` measures 390 and 1280 only when Playwright launches. If it does not, the result stays static. A static result is not those two widths. Rendered visit was not run in this note. That measurement is not public. The noindex paint writes `robots.txt` with `Disallow: /` and does not write a sitemap. `structure.json` must show the one `mold_id` that was selected. A second mold id is a fail for this screen.

## 7. Risks

A palette box, a Suggest control, or a call to `readable` or `library mold` would invent a design system. The mold's own section list would invent steps or contact the copy does not have. Painting a fleet domain, or any folder that is not one of the two copy projects, would invent a site.

`compose` does not read the ledger. Paint of warmth-authority can succeed offline and still not be a live bind. If the status line flips to available after Paint, the live refusal is hidden. Live bind on a second site name would mark that mold live there. The CLI blocks it only when `--live` is set and the owner is a different site. A draft bind without `--live` still writes the ledger and can look like a second assignment. This screen has no draft-bind button. Crew fails the already-live mold and then stops. Treating that FAIL as a warning and continuing would hide it. `mold_panel` with `live` set returns not ok. Showing the tokens and a success anyway would hide `error` `live`.

Overwriting `sites/demo-local-compose` without showing the path drops the frame already recorded there. Passing `--indexable` or a host would leave noindex and could write a sitemap. Binding the preview on 0.0.0.0 would expose it beyond localhost. `serve` prints a localhost URL. The listener in code is 127.0.0.1. The form must use that listener.

`library list` omits the hex. Filling Palette from memory, from the Wix nine, or from Webflow's mapped theme would be a generated palette. The fixed Wix system hexes were not measured and are not used. A full checker pass and a rendered visit of the existing compose folder were not re-run here. Citing them as a fresh pass would hide that gap.
