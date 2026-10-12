Plan Room expert

## 1. Role

Plan Room is the studio screen for the structure file a human accepts before any HTML exists. Its one job is to list the pages and sections `compose --plan` already wrote, then let the human drop or reorder only those sections. It does not add a section, and it does not paint a page.

## 2. Evidence

Read on 2026-10-08, from disk, not from a new vendor fetch:

- `library/research/ui/BRIEF.md`. Studio gap, `compose --plan`, and the 4Cs+ floors.
- `library/research/competitors/10web.md`. What 10Web shows before generation.
- `library/research/competitors/relume.md`. What Relume shows before a wireframe.
- `sites/demo-local-plan/structure.json`. The only file in that folder.
- `library/frames/welcome-scroll.json`. Frame order the plan is allowed to start from.
- `lib/compose.py`, `lib/plan_gate.py`, `lib/structure.py`, `lib/frames.py`, `lib/serve.py`, and the `compose` / `serve` parsers in `spidercaster.py`. Not a live run. Check and visit were not run. Pixel widths of a studio window were not measured.

`sites/demo-local-plan/structure.json` is schema `spidercaster-structure/1`, frame `welcome-scroll`, mold `discover-grid`, one page `index`, and four sections in this order: `hero` / `hero-dark-band-072`, `about` / `card-collection-item-with-meta-181`, `features` / `card-compact-row-089`, `faq` / `faq-bootstrap-accordion-flush-195`. There is no title, description, prompt, or sentence in the file. Header and footer are not rows. The folder has no `index.html`, `site.json`, `report.json`, `robots.txt`, or sitemap. `welcome-scroll` also names `gallery` and `contact`. Those two names are not rows in this file, so this screen must not offer them.

10Web, from `10web.md`, is the competitor file for the gate. Before the page exists, a human can see a structure preview of pages and the sections on each page. Customize structure can add a page, add a section, edit the section name, edit the section prompt, run Enhance with AI on that prompt, or remove a section, then Save and start building. Generation creates the design, content, and layout only after that. Reorder inside that structure editor is not public. An older ecommerce article says the person can rearrange, delete, or modify sections on a schematic, then Generate. A Planner Agent can be rewritten, approved, or, in onboarding only, skipped, and a skip still builds. Whether that plan is the same screen as the structure editor is not public. The plan file format is not public. The ecommerce path generates sample products.

Relume, also read because this task names it, shows a sitemap before the wireframed page exists. Generation builds Home and waits. The person can edit page names, section names, and section descriptions before wireframes, because that text is the prompt that picks the component and the generated copy. The person can add a section, drag it by the handle, or swap a variant. Ask AI can rewrite wireframe text. Reset Copy replaces a page with latin filler. A second sitemap can sit beside the first. The Site Builder project file format is not public.

## 3. Screen

The human acts in this order. The window is one column. The only data on it is the open structure file.

1. Plan. Chooses `projects/demo-local` or `projects/bench-harbor-tearoom`, a package frame, and a mold that is not a live bind, then runs `compose --plan` into an output folder. If `sites/demo-local-plan/structure.json` is already the file, this step is skipped and the file is read. A browser reload reads the file again. It does not run compose.
2. The list. Read-only lines: schema, frame id, mold id. Then one group per `pages[].slug`, in file order. Each section row shows `id`, `type`, and `part_id`, in file order. Nothing else. No copy, no prompt, no thumbnail of HTML.
3. Move earlier. Swaps that row with the previous row on the same page. The `id`, `type`, and `part_id` stay one object.
4. Move later. Swaps that row with the next row on the same page. Same rule.
5. Drop. Removes that one object from that page. Allowed for every listed row, including `hero` and including the last row.
6. Accept. Writes the same `structure.json` and stops. The status line is "plan accepted, no HTML". It is not a check result.

A drag handle may reorder rows on a wide window. It is not the contract. Move earlier, Move later, and Drop are the controls, including at phone width. The handle cannot drop a row onto another page, onto a new page, or onto a list of types.

Refused, with no control and no hidden path:

- Add section, including a frame name that is not already a row, a second copy of a listed type, or a new id.
- Add page, delete page, rename a slug, or reorder pages.
- Move a section onto a different page.
- Edit `id`, `type`, `part_id`, `frame_id`, `mold_id`, or schema.
- A section name field, a section prompt, Enhance with AI, Ask AI, or Reset copy.
- Skip, Generate, Start building, or any paint action.
- Chat, a plugin install, or a publish sheet.
- `serve` of the plan folder, `build --indexable`, a sitemap, or `library bind --live`.
- Discard and replan, unless the human uses that separate control. It calls `compose --plan` again, replaces the file, writes no HTML, and says that drops and order changes are gone.

Accept does not enable paint. There is no command that reads the edited file and writes the page from it.

## 4. Already here

`python spidercaster.py compose PROJECT --plan [--frame ID] [--mold ID] [--out DIR]` is the plan command. Default output is `sites/<project name>-compose`. `--plan` is stored as `plan_only`. `compose_project` still plans from `copy/`, applies the frame with `apply_frame`, and picks one part per section plus a header and a footer in memory. When `plan_only` is true it writes only `structure.json`, through `save_structure`, and returns `plan_only_result`. It does not write the HTML, `site.json`, or `report.json`. The printed result can list header and footer part ids. The file does not.

`apply_frame` keeps planned sections the frame names, in frame order, and does not invent a section. That reorder already happened before the file exists. Plan Room is the later, narrower edit of the rows that remain.

`load_structure` reads the file. `validate_structure` checks schema, string fields, and that every section type is in a caller-supplied `planned_types` list. A missing type is not an error. An extra page whose types are in that list is not an error (`lib/structure_selftest.py` asserts the extra page). So the validator does not enforce this screen. The allow-list is the set of section objects loaded from the file.

`serve` binds `127.0.0.1` and refuses a folder with no `index.html`. A plan folder fails that check. `is_plan_file` is true only for a real file named `structure.json`. Nothing in the CLI loads an edited structure and paints it. A later `compose` without `--plan` plans again from copy and the frame and overwrites the file. That gap is open. This report does not close it in the engine.

## 5. Proposal

The smallest surface is one localhost page, standard library only, same bind as `lib/serve.py` (`127.0.0.1`, no new package, no React, no Tailwind, no shadcn). It is not `serve` of the site folder. It does not live inside the site output.

It shells out only to `python spidercaster.py compose ... --plan`. Plan runs that command when the human asks for a new file. The page then reads `structure.json` and keeps the original section objects in memory. Move earlier, Move later, and Drop change only that list. Accept writes the file in the `save_structure` shape: UTF-8 JSON, indent 2, trailing newline, the loaded schema, frame id, and mold id unchanged, pages and slugs in the loaded order, each page's sections the surviving objects in the new order. Accept does not call compose again.

The allow-list is those loaded objects, compared by `id`, `type`, and `part_id` together. A write that adds an object, changes any of the three fields, moves an object to another page, or adds a page is refused before the file is touched. `validate_structure` may be called with the types from the loaded file, and a pass is not enough to save.

Discard and replan is the only other command, and only after a typed confirmation that the current file will be replaced. It is still `--plan`. There is no button that runs compose without `--plan`.

Projects with no copy pack are not in the project control. Fleet domains are not in it. `warmth-authority` is not in the mold control. The screen does not bind a mold.

## 6. 4Cs+ test

This screen is judged as studio chrome on a phone-width window. It is not judged as the site. No studio page was measured here. The floors below are the pass rule for a later check of this window, not a result.

Phone-width window, at 360, 390, and 412:

- Copy. Visible text is the file's ids, types, part ids, slugs, frame id, and mold id, plus the control names in section 3. No SAMPLE, lorem, placeholder, review, award, section prompt, or sentence written for the site.
- Contrast. 4.5:1 for text, 3:1 for large text. Not measured here.
- Chrome. Body 18px, chrome 16px, tap targets 44px for Move earlier, Move later, Drop, and Accept. One studio h1, the words Plan Room. A skip link to the first page group. No site hero is required on this window, because the site page does not exist. A sticky bar is refused if it covers a row or leaves a target under 44px.
- Crawl. This window is not the site. It does not write a canonical, WebSite JSON-LD, `robots.txt`, or a sitemap for the project. It stays on 127.0.0.1.
- Plus. No sideways overflow at those three widths. The three row controls stay on the row without a horizontal scroller. Drag is optional and is not the only way to reorder.

Built page, after a human has a site from some later command this screen does not run:

- Accept's success line does not say the page passed. There is no page yet, so `check` and `visit` are not run from this screen.
- When a page does exist, `check` is the judge: claims only from project copy, contrast floors, body 18px, chrome 16px, tap 44px, sticky header, skip link, hero visual, favicon, one h1, no skipped heading outside a catalog part, relative canonical, WebSite JSON-LD, no aggregateRating, description present, no sideways overflow at 360, 390, and 412, drawer opens and closes. `visit` measures 390 and 1280 only when Playwright is installed. A noindex build writes `robots.txt` with `Disallow: /` and does not write a sitemap.
- The built section order must match the accepted file. A dropped id must be absent. If the builder ignored the file, that is a failure, and Plan Room must not show a pass over it.
- Dropping `hero` stays visible on the plan as "no hero". The screen does not invent a hero to satisfy the later floor.

## 7. Risks

- An Add control, a frame checklist, or a catalog picker would invent a section the plan does not have. `gallery` and `contact` on `welcome-scroll` are the trap on this file.
- A section prompt, Enhance with AI, Ask AI, or Reset copy would invent sentences. 10Web's onboarding skip and its sample products do that. Relume's description field and latin filler do that. This screen has none of those.
- `validate_structure` will accept an extra page and will accept a new row whose type was already planned. Treating a clean validator result as Accept would hide an added section.
- Compose without `--plan`, or Plan run again by a browser reload, rewrites `structure.json` from the copy and the frame. The human's drops and order vanish, and the in-memory HTML that `compose_project` already builds could be written. Accept must not call that path. The screen must not render that in-memory HTML as a preview.
- `serve` on the plan folder fails today because there is no `index.html`. Opening a stub page so serve succeeds would pretend the site exists.
- A green Accept that reads like `check` passed would hide a missing hero, a missing h1, or a later builder that ignored the file.
- Editing `part_id` or moving a row across pages is an add by another name.
- Listing header or footer as sections would drop chrome the structure file does not own. They stay off this list.
- `library bind --live`, `build --indexable`, or a sitemap control would publish. `warmth-authority` is already live on movelixir.com and is not a choice here.
- A chat button, a React studio, or a Tailwind skin is out of the engine. The page stays static HTML from the standard library, on localhost, noindex until a human bind that this screen cannot start.
