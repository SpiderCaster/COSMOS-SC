Studio Shell

## 1. Role

Studio Shell. The one job of this screen is the desk Keith opens instead of a terminal: a project list, the last check, and four doors into plan, parts, preview, and check. The page does not exist yet on this screen. Nothing is generated, painted, or published when the desk opens.

## 2. Evidence

Read on 2026-10-08: `library/research/ui/BRIEF.md`, `library/research/competitors/claude.md` (design canvas and plan pause), and `spidercaster.py` through the command functions and the parser. Also read `lib/serve.py`, `lib/plan_gate.py`, the `compose --plan` branch in `lib/compose.py`, `lib/structure.py`, the `Report` print path and `noindex_status` branch in `lib/check.py`, `visit_site` in `lib/visit_check.py`, `lib/doctor.py`, `library/ledger.json`, the mold note in `library/molds/warmth-authority.json`, the two project briefs, and the directory lists under `projects/` and `sites/`. No command was run. No site was checked. No bind was made. Pass, fail, contrast, and phone-width results for these folders are not public.

What the engine already is: a Python 3.11+ standard-library CLI, `python spidercaster.py`, with no studio screen. `serve` only hosts a finished site folder. It binds `127.0.0.1`, starts at port 4173, and refuses a folder with no `index.html` by printing `no index.html in {site}; run a build first`.

Commands the parser actually registers: `init`, `build`, `compose`, `refine`, `check`, `visit`, `serve`, `models`, `wallets`, `sections`, `image`, `library` (`index`, `list`, `mold`, `bind`, `accept`, `selftest`), `crew` (`roles`, `run`, `selftest`), `doctor`, `shipcheck`, `seat`, `parts` (`scan`, `assemble`, `selftest`), `tools` (`list`, `apply`). The module docstring omits `wallets` and `image`. Those two are real. They are not desk controls.

Projects on disk with `brief.md` and `copy/`: `projects/demo-local` and `projects/bench-harbor-tearoom`. The harbor brief says the fixture is synthetic and must never be indexed, deployed, or linked from a live lane. Fleet domains named in the brief are not folders here. Built folders under `sites/` include `demo-local`, `demo-local-ai`, `demo-local-compose` (has `index.html` and `structure.json`), `demo-local-plan` (`structure.json` only), `bench-harbor-tearoom`, and `assembled`. A folder name is not a join. `compose` defaults `--out` to `sites/<project name>-compose`. `sites/demo-local-plan` is an `--out` someone already chose, not a rule in the parser.

`compose --plan` writes `structure.json` and does not write HTML (`lib/plan_gate.py`). It also does not delete an `index.html` already in that folder. `check` prints every row as `[pass]`, `[FAIL]`, `[warn]`, or `[skip]`, then a count line, and exits 1 only when a row is FAIL. It writes no results file. `report.json` is the build token ledger. `ok()` ignores WARN and SKIP. With no `--project`, the copy rows `ungrounded_claim`, `lone_about`, and `invented_chrome` are not added. With no `--expect-noindex`, `noindex_status` is SKIP, not a pass. `visit` always does a static read. Mode becomes `rendered` only after Playwright launches a browser and measures 390x800 and 1280x800. A missing browser returns mode `static` and is not a failure. That is not a measurement at 360, 390, or 412. Not public as a phone pass.

`library/ledger.json` records `warmth-authority` live on `movelixir.com`. `discover-grid` is on `demo-hero.example` and `harbor-test.example` with `live` false. `clarify-mix` is on `demo-stage.example` with `live` false. `library bind --live` is the human publish. It was not run.

What Claude shows a person before the page exists, from `library/research/competitors/claude.md`: three surfaces, none of them a local project list. Claude Design, in beta, puts a canvas beside a conversation. The documented flow is start, attach or import a design system, add screenshots or a codebase, describe the build, then review the canvas. Review is after the first generation. Nothing on that page requires a human to approve a plan before the canvas exists. `/design` with a brief drafts artboards and publishes the canvas. Outside plan mode, Claude Code publishes a new artifact from the prompt with no permission prompt, unless the publish declares a runtime capability. Plan mode explores without editing source files and asks before the first publish of each artifact. That ask is about publish, not about a multi-page section plan. `/slides` with no brief asks what the deck is about before creating anything. `/slides` with a brief does not. An artifact stays private until Share. That is an audience gate, not a plan gate. The public `frontend-design` skill tells the model to invent copy when the brief has none. Claude Design has no version history. There is no opened requirement for a viewport, a tap size, or a small-screen stylesheet.

The useful slice already named in that note is the pause: write `structure.json` and do not write HTML until a person accepts the file. The desk is that pause as a first screen. It does not copy the canvas, the chat, the private URL, or Share.

## 3. Screen

Keith opens one localhost page. The first paint only reads directories. It does not call `compose`, `build`, `parts assemble`, `tools apply`, `serve`, or `check`.

He sees, in this order:

1. One heading, the parser program name `spidercaster`. No slogan. A skip link goes to the project list.
2. The project list. Each row is a directory under `projects/` that has `brief.md`. Today that is `demo-local` and `bench-harbor-tearoom`. The row shows the path and the file names inside `copy/`. It does not rewrite the brief. A row with no `copy/` files is shown and is not selectable. Fleet names are not rows.
3. The last check, beside the selected project. On a fresh open this block says that this session has not run `check`. It may show `report.json` fields `mode` and `noindex` only when that file is in the selected site folder, and it labels them as the build ledger, not the checker. It does not turn a token line into a pass.
4. Four doors, in this order, for the selected project: Plan, Parts, Preview, Check. A door that cannot run stays visible and says why. A closed drawer does not hold Check.

Controls, named from the parser help, and what each one does:

- Plan opens the plan room with the project path. The only command that room may run from this door is `compose <project> --plan`. Help text: write `structure.json` and do not write HTML. Frame and mold stay empty on this door. Choosing one of the fourteen frame ids, or `discover-grid` or `clarify-mix`, belongs to the plan room after the structure file exists. Returning to the desk shows the structure path. It does not accept the plan and it does not write HTML.
- Parts opens the parts room with the project path. The first commands are `parts scan` and `tools list`. Help text: count every part manifest, and list catalog rows as built or missing. The door does not call `parts assemble` or `tools apply`. Assemble's parser default writes `sites/assembled` from `projects/demo-local`. Apply writes an HTML file. Those stay deeper in the parts room, behind a second explicit control, and they are not the first paint.
- Preview opens the preview room with one site directory. The command is `serve <site>`. Help text: preview a built site. It runs in its own process so the desk stays up. The link uses the bound address `127.0.0.1` and the port `serve` actually took. The desk does not embed the built page in place of the project list.
- Check opens the check room with the site directory and, when a project is selected, `--project` and `--expect-noindex`. The command is `check`. Help text: run built-in checks. `visit` is not a fifth door. The check room may run it and must show `mode`. The printed rows come back to the desk and replace last check, including WARN and SKIP. Exit 1 stays on the screen.

What is refused, with no control drawn for it:

- `compose` without `--plan`, `build`, `build --compose`, and `build --indexable` or `--host`. Those write HTML or an indexable pack. Accepting a plan is not a desk button.
- `library bind`, with or without `--live`. Publish stays that command, typed by a person, not a door.
- The mold `warmth-authority`. The ledger says it is live on `movelixir.com`.
- `refine` without `--offline`, `image`, `models --probe`, and `wallets`. They spend a provider call or read key fingerprints. The desk does not ask for a prompt.
- `init` and `init --force`. The stock brief template is the engine's, but a new project is not this screen, and `--force` will overwrite a brief.
- `crew run`. It builds through seven hands. `crew` does not publish, and it still writes a site. Not a door.
- Any host other than `127.0.0.1`. Any chat field. Any Share control. Any fleet domain. Any sample sentence used as page copy.
- Plan into a directory that already contains `index.html`. `--plan` would leave that old page on disk. Preview would then show a page the new structure file does not claim. The person must pass `--out` to a folder with no `index.html`. `sites/demo-local-plan` is one such folder already. It is not auto-selected.
- Preview when `index.html` is missing. The refusal text is the one `serve` already prints.
- Check with no site directory, or check of the desk document itself. The desk is not a built project page.
- Treating `sites/<name>` as the output of `projects/<name>` unless the path is the compose default `sites/<name>-compose` or an `--out` chosen in this session. Other built folders can be picked by path. They are not labeled as that project's page.

## 4. Already here

| Desk piece | What exists today | What does not |
| --- | --- | --- |
| Open a screen | Nothing. The person types `python spidercaster.py` and a subcommand. | A localhost desk. |
| Project list | `projects/demo-local` and `projects/bench-harbor-tearoom`, each with `brief.md` and `copy/`. | A list command. `doctor` reports molds, frames, seats, and hands. It does not list projects. |
| Last check | `check` prints rows and a count. `report.json` stores mode, noindex, files, warnings, and tokens. | A saved checker report. A fresh desk has no last check. Whether any current site passes is not public. |
| Plan | `compose <project> --plan`, optional `--out`, `--frame`, `--mold`. Writes `structure.json` only. Schema `spidercaster-structure/1` records `frame_id`, `mold_id`, and each section `id`, `type`, and `part_id`. | A pause screen. The CLI writes the file and returns. It does not wait. |
| Parts | `parts scan`, `parts assemble`, `tools list`, `tools apply`. The brief's catalog count is 208 parts, routes hooks-blocks 80, headers 44, popups 43, sidebars 41. This note did not re-count them. That count is not public as a new measurement. | A parts room. Scan and list are printouts. |
| Preview | `serve <site> --port` default 4173, bound to `127.0.0.1`, static files only. | A preview of a plan. No `index.html`, no server. |
| Check | `check <site> --project --expect-noindex` or `--expect-indexable`. `visit <site>` for static checks plus a rendered measure when a browser launches. | A place those lines stay after the terminal scrolls. |

`build --offline` and a full `compose` also write a site. They are the wrong command for this screen because they write HTML in the same step. The frame file `library/frames/local-desk.json` is a section frame id, `local-desk`. It is not this screen. Wiring that frame to the shell would reorder a site, not open a desk.

## 5. Proposal

The smallest surface is one more localhost listener, stdlib only, same pattern as `lib/serve.py`: `http.server` and `ThreadingTCPServer` bound to `127.0.0.1`, never `0.0.0.0`. It is not the site server. Site preview keeps port 4173 and its own process. The desk port is whatever free port that second listener takes. No port for it exists in the parser today. No new package. No React, Tailwind, shadcn, CDN script, or hotlinked font. The page is one HTML document with a system font stack and a short style block in the response. The engine files are not edited by this research. A later build can add the listener beside the CLI. It calls the existing commands as subprocesses so flags cannot be skipped by an import.

GET reads `projects/` and `sites/` and paints the desk. GET never runs a command, so a refresh does not build. POST is the only way through a door, and only the four commands in section 3. The response after POST is the desk again, with stdout under last check or under the door that ran. JSON from `compose --plan` is shown as the file path and `plan_only`, not as a success banner that hides `ok: false`.

The rooms connect by the selected paths, not by a chat transcript:

- Desk holds the selected project and, once chosen, one site directory.
- Plan receives the project and an `--out` that has no `index.html`. It returns the `structure.json` path. The desk stores that path on the row. It does not store acceptance.
- Parts receives the project. It returns scan and list text. It does not change the site directory.
- Preview receives only a site directory that has `index.html`. The desk links to the preview process and stays where it is.
- Check receives the site directory and the project. It returns the checker print, which becomes last check. `visit` output, if the room ran it, is a second block with `mode`. Mode `static` is labeled not measured at 390 and 1280. Not public as a rendered pass.
- Every room has a way back to the desk that runs no command.

Copy on the desk is limited to paths, file names, parser help, and the process output. The brief file may be shown as stored. It is not edited. The harbor row keeps the brief's own limit visible: synthetic, never deploy. No field asks the desk to write a headline.

## 6. 4Cs+ test

This screen is the desk window. The built project page is a different document, judged only after the check door runs. This note did not open a narrowed window and did not run `check` or `visit`. Every pass below is a rule to apply, not a result. Not public as a measured pass.

On a phone-width window, judge the desk at 360, 390, and 412:

- The four doors stack in one column. Paths wrap. Nothing scrolls sideways. A long Windows path is the likely overflow. Wrapping is the fix, not a smaller font.
- Body text 18px. Door labels, paths, and checker rows 16px. Each door and the project row is at least 44px tall. The skip link is present. One `h1`, the program name.
- A sticky bar holds that heading and the skip link only. Four sticky doors at 44px would cover the project list. Check is not inside a closed drawer. On this screen a drawer is not required to prevent overflow, and a drawer that hides the failure list would fail the point of last check.
- Contrast of text against the desk background meets 4.5:1, large text 3:1. The pair is not `warmth-authority`. The checker has not measured the desk, so a chosen pair is not public as a pass until `check` or an equivalent measure is run on this document.
- No hero image and no favicon borrowed from a project. Those chrome rules belong to a built page. Inventing a hero for the desk would invent a visual the copy pack does not have.
- No motion. The built renderer already reduces motion for sites. The desk does not add a second animation runtime.
- Focus is visible on the doors. Keyboard order is skip link, project rows, Plan, Parts, Preview, Check, then last check.

On a built page, the desk does not grade by eye:

- The check door runs `check` with `--project` and `--expect-noindex`. Copy rows appear only because `--project` was passed. Without it, a quiet copy floor is not a pass. Not public.
- Contrast, type, tap size, sticky header, skip link, one h1, heading order, canonical, WebSite JSON-LD, description, and no `aggregateRating` are rows on that built site. The desk reprints them. It does not restyle the site to make them pass.
- Sideways overflow at 360, 390, and 412, and the mobile drawer opening and closing, are checker floors on the built page. `visit` adds 390 and 1280 only when `mode` is `rendered`. Mode `static` stays marked not public as that measure.
- A noindex build's `robots.txt` is `Disallow: /` and there is no sitemap. The desk does not offer the flag that writes one.
- Crawl tags are not painted onto the desk to satisfy a site checker. Running `check` against the desk folder would demand a public-page shape this screen must not have.

## 7. Risks

- Opening the desk by running `compose` without `--plan`, or `build`, writes HTML before anyone accepts `structure.json`. That skips the pause. Claude asks only in plan mode, and it asks before publish. This screen has to be stricter than that, because the page should not exist yet.
- Running `--plan` into `sites/<name>-compose` when that folder already has `index.html` leaves the old page. Preview would show it. The door refuses that `--out`.
- Showing `report.json` or a zero FAIL count as last check hides WARN, SKIP, and missing copy rows. `ok()` is only "no FAIL". The count line without the `[FAIL]` lines hides the reason.
- `parts assemble` and `tools apply` on the first click write HTML. Assemble's default output is easy to hit by accident. They are not on the desk.
- A mold menu that includes `warmth-authority`, or any `library bind --live` control, is a publish path. The ledger already has that mold live.
- A chat box, or a blank project that the desk fills, is the Claude path that can publish with no plan and the skill path that invents copy. The harbor fixture and the fleet list are the same trap if the desk treats a name as a site.
- Catching `serve`'s missing-`index.html` refusal and drawing a sample layout invents a page. The refusal stays as text.
- Running `serve` inside the desk process blocks the desk. Binding `0.0.0.0` leaves the machine. Both are refused.
- Calling `init --force`, or `refine` without `--offline`, writes copy or spends a model call from a screen that was only supposed to list projects.
- Guessing that `sites/demo-local` is the page for `projects/demo-local` can preview the wrong build. The join is the compose default or an `--out` the person chose.
- Marking `visit` mode `static` as a phone-width pass claims a measure that did not run. Not public.
