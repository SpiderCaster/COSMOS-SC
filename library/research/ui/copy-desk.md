Copy Desk

## 1. Role

Copy Desk is the read-only screen for one staged project. Its job is to show the brief as context, show the copy blocks that are already in files, and show the gap when a package frame names a section those blocks did not produce. It does not write a marketing sentence, fill a missing section, or publish.

## 2. Evidence

Read for this report:

- `library/research/ui/BRIEF.md`. The studio does not exist. `serve` only hosts a finished folder on 127.0.0.1. Visible claims must already be in the project copy. SAMPLE, lorem, placeholder, invented reviews, and awards fail. This work must not run `library bind --live`.
- `projects/demo-local/brief.md`. It is a local test brief for Keith and the free-model seats. It says the page documents the engine, the token rules, and the commands, in a plain factual tone, and that the build stays noindex. That file is context. It is not a section.
- `projects/demo-local/copy/overview.md`, the copy file opened for this desk. Two heading-scoped blocks are in the file. The h1 is "SpiderCaster: websites from real copy, on free tokens", followed by two paragraphs. The h2 is "Why it is cheap", followed by five bullets. The same folder also has `commands.md` and `faq.md`. Those were opened only to see that the saved plan's faq row has a source file. `faq.md` is questions and answers about the engine. None of the three files is a gallery, a contact heading, a testimonial, a review, an award, or a star rating.
- `library/frames/welcome-scroll.json`. Sections, in order: hero, about, features, gallery, faq, contact.
- `sites/demo-local-plan/structure.json`, already on disk. `frame_id` is `welcome-scroll`, `mold_id` is `discover-grid`, and the index sections stored there are hero, about, features, and faq. Gallery and contact are not in that file. Compose was not re-run for this report. That kept list is the stored file, not a new measurement.
- `lib/ingest.py`, `lib/offline.py`, `lib/frames.py` (`apply_frame`), `lib/copy_pack.py`, `lib/part_fill.py`, `lib/check.py`, `lib/hands/__init__.py` (`brief_read`, `frame_pick`, `copy_read`, `copy_gap`), `lib/compose.py`, `lib/plan_gate.py`, `lib/serve.py`, `spidercaster.py` (`init`, `compose --plan`, `check --project`, `seat`, `crew`), and `library/seats/content/SKILL.md`.
- `library/research/competitors/lovable.md`.

What Lovable shows before a page exists: the dashboard box "Ask Lovable to create…". The quick-start prompt asks for a hero, a menu, hours, a location, a visual tone, and the line "Use realistic sample content throughout". Design guidance can show three HTML and Tailwind directions first. Those previews use generic copy and image placeholders. Plan mode can stop for an edited plan, but Build is the default and writes the project without that stop. A ban on invented reviews is not public. A separate prompting page says to avoid lorem ipsum and to type real headlines. Those two pages disagree. The quick start is the default first prompt. SpiderCaster does not show that prompt and does not build those placeholder directions.

The offline planner maps blocks by what the file contains. An overview-style file supplies the hero. Three or more bullets become features. Two or more questions become faq. A contact heading becomes contact. Anything else with paragraphs becomes about. `apply_frame` then keeps planned sections the frame names, in frame order, and returns no new section. Its selftest refuses an invented pricing section. `part_fill` inserts a string only when that string is an exact substring of the joined copy files. It skips empty strings and the exact texts "Read on", "Built with SpiderCaster", and "About". `copy_pack.project_copy_text` joins `.md`, `.markdown`, and `.txt` directly inside `copy/`. It does not read the brief, and it does not read `.json`.

## 3. Screen

The desk is one localhost page. Controls, in order:

1. Address. The page is bound to 127.0.0.1 and no other host. There is no public URL control.
2. Project. A select with two options: `projects/demo-local` and `projects/bench-harbor-tearoom`. A typed fleet domain (iseark, teavital, floelixir, the elixir parks, or any other MochaHost name) is refused. Those folders are not projects here.
3. Brief. A read-only region labeled "Context", filled from `brief.md`. It is not a textarea and it has no save.
4. Blocks. A list, one entry per heading-scoped chunk in `copy/`. Each entry shows the filename, the heading, and the paragraphs, bullets, numbered lines, questions, answers, and prices that file already has. On demo-local the first block is the overview h1 and its two paragraphs. The next block from that file is "Why it is cheap" and its five bullets. The init scaffold `copy/README.md` that starts with "Copy folder" and "Put REAL copy here" is shown as scaffold, not as a client block. demo-local does not have that README.
5. Frame. A select of package frame ids from `library/frames`. Choosing `welcome-scroll` shows that file's six type names. The select does not bind a mold, does not write HTML, and does not offer `warmth-authority`. An empty choice shows "no frame selected" and does not list every known type as missing.
6. Gap. One row per type on the chosen frame. A type that the plan produced is "kept", with the section id from `structure.json` when Plan has been run. A type the plan did not produce is "missing" and the words "not in copy". For the stored welcome-scroll plan, gallery and contact are the missing rows. A missing row has no button.
7. Plan. One button. It runs `python spidercaster.py compose <project> --frame <id> --plan` and then reads `structure.json`. `--plan` writes that file and does not write HTML. The button is refused without a staged project and a known frame id.
8. Check. One button, off until the human points at an existing built site folder. It runs `python spidercaster.py check <site> --project <project> --expect-noindex` and leaves every FAIL row on screen. It does not run when no site folder is chosen, and it does not print a pass that was not in the command output.

Refused on this screen: a sentence field, Save, Generate, Fill sample, "Use realistic sample content", Refine, Publish, `library bind --live`, `build --indexable`, a chat box, a mold bind, and any control that opens catalog HTML or a part fragment as if that text were the project's copy. `crew run` is also refused here. It walks all seven seats and writes a site. The desk does not need that.

If `copy/` has no client blocks, the blocks list is empty and the page says `copy/ has no blocks; nothing was invented to fill them`. Plan stays disabled. No sample page is offered.

## 4. Already here

No studio page does this. A person currently opens `brief.md` and the files under `copy/` outside the engine. `python spidercaster.py serve <site>` hosts a finished folder on 127.0.0.1. It does not read the brief or the gap.

What already enforces the refusal:

- `init` writes a brief stub and the copy README, then stops. It tells the person to fill real copy. It does not invent a page.
- `brief_read` returns the brief text or fails when `brief.md` is empty. The content seat uses that text as context only.
- `copy_read` loads `copy/` through `ingest.load_project` and returns the block count, titles, and `copy/<file>` citations. A block file outside `copy/`, an absolute path, or `..` is a FAIL.
- `copy_gap` FAILs with `copy/ has no blocks; nothing was invented to fill them` when there are no blocks. It does not list frame types the copy never produced. A PASS from `copy_gap` only means at least one cited block exists. It is not proof that gallery or contact is filled. The hand also does not drop the init README. The content skill says that README is not client copy. The screen follows the skill, not a false PASS.
- `frame_pick` loads one package frame and names its section types. An empty id leaves copy order alone. An unknown id FAILs.
- `apply_frame` drops planned sections the frame does not name and never adds a type the plan does not have. `compose` calls it before `structure.json` is written. `python spidercaster.py compose <project> --frame <id> --plan` prints the plan result and does not write HTML (`lib/plan_gate.py`).
- `python spidercaster.py check <site> --project <project>` passes the joined copy files into the checker. Rows that refuse invented text: `no_sample` (SAMPLE, lorem ipsum, demo content, hello world, sample page, under construction, and the related fleet phrases), `no_soft_placeholders` (TODO, TBD, FIXME, XXX, lorem, ipsum, placeholder in visible text), `ungrounded_claim` (the exact phrases testimonial, customer review, and award-winning, plus a number over 5 or a number of stars, when that text is not in the copy join), `invented_chrome` ("Read on" and "Built with SpiderCaster" when the copy join does not contain them), and `lone_about` (an h2 whose text is exactly About when the copy join never uses the word About). Without `--project`, those claim rows are not added.
- `part_fill` will not plant a slot string that is not in that same copy join.
- `python spidercaster.py seat content` prints the content pack. It does not print the project's paragraphs. `crew roles` prints that content "does not fill a gap with invented facts, prices, or quotes."

`python spidercaster.py sections` lists the fourteen type names the engine knows: hero, features, stats, steps, gallery, pricing, testimonials, faq, cta, contact, about, team, menu, logocloud. A frame cannot ask for a type outside that list. The desk uses those names as gap labels. It does not turn a missing name into a paragraph.

## 5. Proposal

The smallest surface is one stdlib script, started by hand, using `http.server` bound to 127.0.0.1 the way `lib/serve.py` is. No new package. No React, Tailwind, shadcn, or remote fetch. It is not `serve` of the built site, and it is not a second publish step.

The script only reads. It reads `brief.md`, the copy files, and `library/frames/<id>.json`. Plan is a subprocess of the existing compose command with `--plan` and an explicit `--out` under `sites/` for that project name. Check is a subprocess of the existing check command. The script does not import a writer, does not edit `lib/`, and does not add a hand.

The gap math is the frame's `sections` list minus the type values stored in `structure.json` after Plan. Until Plan has been run, the missing row still shows, from the frame file, but it is marked "plan not run" so a kept type is not invented. The script never writes `copy/`, `brief.md`, HTML, `robots.txt`, or a sitemap. It never calls `library bind`, `refine`, `build --indexable`, or `crew run`.

There is no form field whose value is prose. The only submitted values are the project id and the frame id, both from the selects. A request that includes any other text is refused with `nothing was invented to fill them`, and nothing is written.

## 6. 4Cs+ test

Phone-width window, the desk itself, at 360, 390, and 412:

- Copy. The only sentences on the page are from `brief.md` and from client files in `copy/`, plus the fixed labels Context, scaffold, kept, missing, and "not in copy". Those labels are desk chrome. They are not written into a site. The page does not show SAMPLE, lorem, placeholder, a review, an award, or a star rating unless that exact text is already in the open copy file. overview.md does not contain them. A missing gallery row is the word gallery and "not in copy", not a fake caption.
- Contrast. Body text at least 4.5:1. Large text at least 3:1. The missing state is the word "missing", not color alone.
- Chrome. Body text 18px. Labels and the select text 16px. The Project select, Frame select, Plan, and Check are at least 44px. A skip link goes to the blocks list. One h1: Copy Desk. The header can stick. It carries the project path, not a new slogan. No hero photo is added. If the project has no local hero file, the desk does not invent one and does not hotlink one.
- Crawl. This page is localhost and stays noindex. It writes no sitemap. One h1. No `aggregateRating`.
- Plus. One column. The selects, blocks, and gap rows wrap. Nothing scrolls sideways at those three widths. There is no multi-link nav, so there is no drawer. If a later header grows a second destination, that drawer has to open and close. A drawer is not an excuse to add links the copy does not have.

Built page, only after a compose that this screen does not start by default:

- Plan must leave the site folder without new HTML. That is the `--plan` contract. A page that appears after Plan is a failure of this screen.
- A later built page is judged by `check --project --expect-noindex`, not by the desk marking itself green. The built page must not contain a section the gap list called missing, and must not contain a sentence that was not in the copy blocks.
- The same check floors apply: no SAMPLE or lorem or placeholder, claims grounded in the copy join, no invented "Read on" or "Built with SpiderCaster", no About h2 the copy never used, contrast 4.5:1 (large text 3:1), body 18px, chrome 16px, tap 44px, one h1, no skipped heading level outside a catalog part, relative canonical, WebSite JSON-LD, no aggregateRating, description present, sticky header, skip link, hero visual only from a local file the project already had, favicon, no sideways overflow at 360, 390, and 412, and a drawer that opens and closes if the built page has the mobile nav.
- `visit` measures 390 and 1280 when Playwright is installed. Whether Playwright is installed on this machine was not measured. That result is not public. This report did not run `visit` or `check`.

## 7. Risks

- Treating `copy_gap` PASS as a filled frame. The hand passes when any block exists. Gallery can still be missing. Hiding that row would hide the failure.
- Treating the init README as client copy. The skill refuses it. The hand does not. Showing those mapping rules as the site's sentences would publish scaffold text.
- Promoting the brief onto the page. `init` says the site comes from the brief plus `copy/`. The checker and `part_fill` ground claims in the copy join only. A sentence that exists only in `brief.md` is context. Writing it into a section invents a claim the checker's copy text does not hold.
- A JSON file under `copy/`. Ingest will load it as blocks. `project_copy_text` will not. The desk can show the block and must say the check join does not include `.json`. Filling a page from that block can fail `ungrounded_claim` or be dropped by `part_fill`. The fix is not a new sentence. It is the human's own `.md` or `.txt`, which this screen does not write.
- Planner labels that the file never said. The offline planner can set a button label "Contact", an empty about title, or the faq fallback "Questions". The blocks pane shows file text only. Those labels stay out of the copy list. `part_fill` already drops "About", "Read on", and "Built with SpiderCaster".
- Catalog leftovers. A full compose can leave part-fragment text in place when the slot is not grounded. That text is not a copy block. The desk must not open it in the blocks list. Check catches the sample, placeholder, review, award, star, and chrome phrases. It does not catch every leftover word. Showing the fragment as copy would launder it.
- Plan pointed at the wrong command. Dropping `--plan` writes HTML. Adding `--indexable`, `bind --live`, or a chat publish deploys or invites indexing. The button's argument list is fixed. A mold control is not on this screen, so `warmth-authority` cannot be bound from here.
- An editor, including Refine. Any box that saves a new headline, a review, a price, or a "sample" paragraph invents copy. Lovable's quick start asks for that sample. This desk refuses the ask.
- A green desk when Plan was not run, when Check was not run, or when Check FAILed. Unrun stays unrun. FAIL stays visible. No stored pass is invented. Fresh compose, check, and visit results are not public until those commands are run.
