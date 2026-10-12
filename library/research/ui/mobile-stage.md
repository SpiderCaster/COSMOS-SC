Mobile Stage

## 1. Role

Mobile Stage is the phone-width screen. Its one job is to show a page that is already built, at 360, 390, and 1280, and to list overflow, tap, type, and drawer failures in words. Keith reads the page. He does not read a terminal log.

The stage does not build, compose, refine, or publish. It does not invent a sentence for the site.

## 2. Evidence

Read on 2026-10-08 from `<repo-root>`. Nothing here was published. `library bind --live` was not run. The bench was not run, so a pass or fail of a live capture is not public.

- `library/research/ui/BRIEF.md` — studio rules, the 4Cs+, and this outline.
- `library/research/competitors/framer.md` — what Framer shows before publish. Mobile section especially.
- `bench/mobile_bench.py` — rendered gates and the default viewports.
- `bench/fixtures/mobile/README.md` — one fixture, one broken gate.
- `lib/check.py` — static floors and the failure lines.
- `lib/visit_check.py` — what `visit` measures.
- `lib/serve.py` and `spidercaster.py` — `serve`, `check`, and `visit`.
- `library/resources/MOBILE.md`, `PHONE_TYPE.md`, `PHONE_A11Y.md`, and `library/rules/mobile.json` — phone sheet, 18px root, 44px targets. Those cards describe the renderer. They are not this screen.

Framer, before a page exists, shows a prompt and then a canvas. Ask Framer takes the subject, the sections, and the style in one field. The how-to article prefers one section at a time. Neither article shows a plan the person must approve before the first layer. Breakpoints are separate canvas widths named Desktop, Tablet, and Phone or Mobile. Default pixel widths for those breakpoints are not public. Preview is Play (Command-P, or Ctrl-P on Windows), a resized viewport, or the breakpoint that is selected. It is a look, not a score. No pass or fail number is published. The from-scratch review list is human and happens before publish: content, images, layout, links, and responsive behavior. A phone breakpoint that does not fill the screen is blamed on fixed widths. Horizontal scroll is blamed on fixed widths, large min-width, absolute position, animated offsets, and fit width. Hiding overflow is discouraged because it can break sticky elements. A minimum body size, a minimum tap size, and a required drawer are not public. The code-component skill's sample paragraph is 15px and its sample button is 14px. Those samples are not a floor and were not measured on a live Framer site.

SpiderCaster does not copy that. The page has to exist as files before this screen can show it. `serve` refuses a folder with no `index.html`. The floors Framer does not publish are already in `lib/check.py`: body text 18px (`BODY_FLOOR_PX`), other text 16px (`TYPE_FLOOR_PX`), tap 44px (`TAP_MIN_PX`). More than four primary nav links at a phone width need a drawer (`MOBILE_NAV_INLINE_MAX`).

Checker windows in `lib/check.py`: `(360, 740)`, `(390, 844)`, `(412, 915)`, and desktop `(1280, 800)`. Type and contrast use all four. Tap, sideways scroll, and the drawer use the three phone widths. `visit` measures only `(390, 800)` and `(1280, 800)`, and only after Playwright launches. The bench default string is `360x800,390x844,412x800,1280x800`. Those heights do not all match. Which height would change a verdict was not measured, so it is not public.

Bench fixtures, from `bench/fixtures/mobile/README.md`. Each bad page is written to break one gate. `clean.html` is written to pass every gate at every viewport. Photos `photo-320.png` and `photo-640.png` are generated gradients.

| Fixture | Gate it breaks |
| --- | --- |
| `clean.html` | nothing |
| `overflow.html` | `overflow_x` — a 600px strip; fails at 360, 390, and 412; fits at 1280 |
| `tap30.html` | `tap_target_rendered` — a 30px-tall button |
| `text12.html` | `type_floor_rendered` — body font-size 12px |
| `no_viewport.html` | `viewport_meta` |
| `grey_tile.html` | `grey_tile_rendered` |
| `nav_broken.html` | `nav_toggle` — menu button, no script, `aria-expanded` never flips; mobile only |
| `nav_clipped.html` | `nav_toggle` — menu opens into a fixed 26px-tall strip, so 48px links are cut off; mobile only |
| `sticky_tall.html` | `sticky_25` — sticky bar at 40vh |
| `img_nosrcset.html` | `img_srcset` |

The four lists on this screen are overflow, tap, type, and drawer. They map to checker rows `sideways_scroll`, `tap_target`, `type_floor`, and `mobile_nav_drawer`, plus the `sideways` lines from `visit`. The other fixture gates stay in the bench. This screen does not pretend it ran them.

## 3. Screen

The stage is one local page. Three controls, then three pictures, then four lists. No fifth control.

1. **Built site.** A select of folders under `sites/` that already contain `index.html`. From this tree that is `sites/assembled`, `sites/bench-harbor-tearoom`, `sites/demo-local`, `sites/demo-local-ai`, and `sites/demo-local-compose`. `sites/demo-local-plan` has `structure.json` only, so it is not in the list. The select does not accept a typed path.

2. **Show page.** Starts the existing preview server for that folder and fills three frames. The frames stay on screen together. Their titles are `360`, `390`, and `1280`. Frame sizes are the checker windows for those widths: 360×740, 390×844, and 1280×800. There is no device menu and no single resizable pane. A width cannot be turned off.

3. **Read failures.** Runs the existing check and the existing visit against that same folder, then fills four headings: **Overflow**, **Tap**, **Type**, **Drawer**. Each heading shows the row status in a word: pass, fail, warn, or skip. Under it, every failure and every warn is one full line, the same line the checker already prints. Nothing is cut off after four or six items. The summary count is not the list.

4. The person opens and closes the menu with the built page's own control, inside the 360 frame and the 390 frame. The stage has no Menu button and does not inject one. The Drawer list is still the checker's words, not a note typed from what the picture looked like.

Refused, and not drawn:

- Publish, Bind, Indexable, Deploy, Compose, Build, Refine, and Ask.
- A text field of any kind.
- A path outside `sites/`, a fleet domain, or a project that has copy but no built `index.html`.
- Binding `warmth-authority`.
- A control that marks skip, warn, or "not run" as pass.
- A control that writes into the site folder, strips `noindex`, or writes `sitemap.xml`.
- Hiding overflow on the built page. The frame does not scale. `transform: scale` is refused because a 600px strip would look as if it fit.

On a wide window the three frames sit in a row when the window can hold them. On a narrow window they stack. The stage document itself does not scroll sideways. A frame that is wider than the stage window sits in a slot; only that slot scrolls. The slot is labeled with its width so a sideways slide is not mistaken for the page fitting.

## 4. Already here

`python spidercaster.py serve <site>` calls `lib/serve.py`. The socket binds `127.0.0.1`, default port 4173, then the next free port, up to 20 tries. It prints a localhost URL and serves the folder. If `index.html` is missing it prints `no index.html in <site>; run a build first` and exits 1. That is the picture. It is one width: the browser window. It lists no failures.

`python spidercaster.py check <site>` calls `check_site` and prints every row. Failure lines are the words this screen repeats.

- Overflow. Row `sideways_scroll`. Line shape from `_mob_line`: file, selector, measured width, static, element, then `at 360,390,412px` (only the widths that failed). A box past the viewport, a wide table, a `pre` or `nowrap` line, or an unbreakable word of 25 characters or more.
- Tap. Row `tap_target`. Line shape from `_tap_line`: file, selector, `measured WxHpx (needs >= 44px)`, static, element and its text, `at` the phone widths. Judged at 360, 390, and 412. An inline link in a sentence is exempt. A size that only might be under 44px is a warn, and a warn is not a pass.
- Type. Row `type_floor`. Line shape from `failure_line`: file, selector, `font-size` measured against `>= 16px` or `>= 18px` for body copy, the element and a quote of its text, and the widths. Full check uses 360, 390, 412, and 1280. `python -m lib.check <site> --mobile-only` drops 1280 for type. This screen does not use `--mobile-only`.
- Drawer. Row `mobile_nav_drawer`. Same `_mob_line` shape. Words already include hidden links with no toggle, too many inline links, a toggle that is not a button, missing `aria-expanded` or `aria-controls`, no accessible name, a toggle under 44px, a drawer that does not hold the links, a drawer shown by default, no script to open it, an open simulation that leaves it hidden, and no close mechanism.

`check_site(..., quiet=True)` keeps those rows and does not print them. The command today does not pass `quiet`, so the words go to the terminal. The last line is only `result: N pass / N fail / N warn / N skip`.

`python spidercaster.py visit <site>` calls `visit_site`. Static mode always runs: missing header, missing `id="main"`, broken `#` links, missing viewport, and CSS wider than 1280px (or `min-width` over 400px on `html` or `body`). Rendered mode, only if Playwright launches a browser, adds sideways scroll when `scrollWidth` is greater than `clientWidth + 1`, and a missing visible header, at 390×800 and 1280×800. It does not measure tap, type, or the drawer, and it does not click the menu. If the browser is missing, the docstring says that is not a failure. The mode stays `static`. The bench says the opposite for its own gates: missing Playwright is not-run, never pass. This screen follows the bench on that point. A static visit is not a rendered pass.

`python bench\mobile_bench.py` serves a copy, then renders with Playwright at the four default viewports. Gate evidence is already a sentence (`scrollWidth` against `innerWidth` and `clientWidth`, controls under 44px, text under the floors, `aria-expanded` false then true then false). It writes `bench\results\mobile-latest.md` and files under `<local-path>`. That is still a log. The run also does a cold start. This screen does not start that run.

Built folders a later compose may use are only `projects/demo-local` and `projects/bench-harbor-tearoom`. This screen does not compose them. Whether any current `sites/` folder fails these four rows was not measured, so it is not public.

## 5. Proposal

The smallest surface is one extra localhost page, standard library only, bound to `127.0.0.1`, on its own port. It is not a file inside the built site, so `serve` cannot ship it. No package install. No React, Tailwind, or shadcn. No change to `lib/`, `spidercaster.py`, the catalog, or a mold.

The page calls the three commands by calling the functions they already call.

- **Show page** calls `serve(site_dir)` and sets each frame's address to `htt<local-path><port>/`. Not `localhost`, and not `0.0.0.0`. Whether those names differ on this Windows machine was not measured.
- **Read failures** calls `check_site(site_dir, quiet=True)` and `visit_site(site_dir)`. It does not shell the full bench.

The four lists print `failure_line` for each failure, and `failure_line(..., warn=True)` for each warn. Overflow also prints each `visit` item whose code is `sideways` or `missing_viewport`, with the word `visit` in front of the detail the command already uses. If `visit` mode is `static`, Overflow gets this line and no pass: `Rendered visit at 390 and 1280 was not run.`

Empty and not-run stay visible. A pass row says pass and shows the checker's own detail, including the widths. A drawer skip says the checker's not-run text (no nav with links). A warn is labeled warn. The page never draws a single "site passed" mark.

Check still judges 412. There is no 412 frame. Widths in the lines are not edited, so a 412 failure remains in the words.

If any other check row failed, or `visit` returned a code other than `sideways` or `missing_viewport`, one line says how many, and that this screen does not list them. That line is not a pass. Copy, contrast, crawl, skip link, sticky header, and favicon stay on `check`. They are not rewritten here.

The stage page's own text is only the control names, the three widths, the status words, and the checker lines. It adds no site sentence.

## 6. 4Cs+ test

Judge the stage window, then judge the built page in the frames. Neither result was measured in this session. Both are the test, not a recorded pass.

Stage window at 360 wide, then 390, then 412:

- The document does not scroll sideways. The 1280 frame may scroll inside its own slot. The slot's label still says 1280.
- **Built site**, **Show page**, and **Read failures** are each at least 44 by 44px. Failure sentences are at least 18px. Labels are at least 16px. Text contrast is at least 4.5:1.
- One `h1`: Mobile stage. A skip link points at the Overflow list. The stage is not a published page: no sitemap, no `bind`, and noindex on the built site is left as the build wrote it.
- The four lists wrap. A long selector does not force the stage document wider than the window.
- Pass, fail, warn, and skip are words, not color alone.

Built page, after Show page and Read failures:

- The 360 frame is 360 CSS pixels wide, the 390 frame is 390, and the 1280 frame is 1280. The picture is the served `index.html`, not a fixture and not a screenshot from the bench.
- Overflow lists every `sideways_scroll` failure in words, including 412 when that width failed, plus visit's sideways lines at the sizes visit actually measured.
- Tap lists every control under 44px in the checker's words. A warn stays a warn.
- Type lists every text under 16px, and every body text under 18px, including a failure that appears only at 1280.
- Drawer lists every `mobile_nav_drawer` failure in words. On the 360 and 390 frames the person can open the real menu and close it again. The list does not change because the menu moved. If the row is skip or warn, the screen does not say the drawer passed.
- A green frame with an empty list is allowed only when that row's status is pass. Static visit with no browser is not that status for rendered overflow.

`clean.html`, `overflow.html`, `tap30.html`, and `text12.html` are the bench's proof shapes for the first three lists. `nav_broken.html` is the shape for a drawer that never opens. They are not a default Built site. Pointing the stage at `bench/fixtures/mobile` is refused.

## 7. Risks

Inventing copy. An Ask field, a Fix button, or Compose on this screen would write sentences the copy pack does not contain. Defaulting the frames to a bench fixture would show fixture sentences as if they were a project. The select stays on folders that already have `index.html`.

Deploy. Publish, Bind, `--indexable`, or a listen address other than `127.0.0.1` leaves the machine. The stage must not call `library bind --live`. It must not write the failure list into the site folder. That file would ship with the site.

Hiding a failure. Several tools already can:

- The check command's last line is a count. A count with no lines hides which control, which word, and which width.
- `--mobile-only` omits type at 1280. A desktop-only type failure would vanish.
- `visit` treats a missing browser as not a failure. Rendered overflow at 390 and 1280 would look like a pass. The stage has to say not run.
- The check detail string keeps only the first few failures and then says "+N more". The row's `failures` list is complete. The screen must use the list, not the shortened detail.
- `overflow-x: hidden` on the frame, or a CSS scale, makes `overflow.html`'s 600px strip look fine. Framer's own note says hiding overflow can break sticky elements. The checker also records when `html` or `body` already clips overflow. The stage must not add a clip to the built page.
- `nav_clipped.html` is a drawer that opens and then cuts the links off at 26px. That is a rendered bench gate. `visit` does not click the menu. Whether the static drawer row fails that file was not run, so it is not public. The 360 and 390 frames are how a person sees the clip. The stage must not mark Drawer pass from the picture, and must not invent a clip sentence the checker did not emit.
- Static `grey_tile` is an explicit not-run. A flat grey hero can show in the frame and have no line in these four lists. The frame is not a grey-tile pass. That gap stays visible; this screen does not invent the missing line.
- A site-level pass painted from these four lists would hide a copy, contrast, or crawl failure. The extra line of other failures exists so that cannot read as success.

No measured pass or fail of `sites/demo-local`, `sites/bench-harbor-tearoom`, or the other built folders is public.
