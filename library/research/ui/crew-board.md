Crew Board

## 1. Role

Crew Board. One local screen shows the seven seats so a person sees who acted and who is refused. The seats, in order, are architect, content, frontend, graphics, visual, seo, and deployer. The deployer does not publish from this screen. `seat_gate` already refuses a hand that is not on that seat. This report does not edit the engine and does not publish.

## 2. Evidence

Read on 2026-10-08: `library/research/ui/BRIEF.md`, `library/CREW.md`, `library/seats/README.md`, each seat `WRAPPER.md`, `library/research/competitors/bolt.md`, `library/research/BUILDER_PATTERNS.md`, `library/ledger.json`, and the current crew path in `lib/crew.py`, `lib/seat_gate.py`, `lib/seatpack.py`, `lib/hands/__init__.py`, `lib/doctor.py`, and `spidercaster.py` (`crew`, `seat`, `serve`). `library/research/PREVIEW_RESULT.md` is an earlier local print from 2026-10-01. It was not re-run for this report.

What the engine already records:

- `ROLES` in `lib/crew.py` is the board. Each seat has an id, a label, a hand list, and a `does_not` line. `crew roles` prints that. `seat <id>` prints one pack (id, label, hands, skill path, wrapper path, `does_not`) and prints `unknown seat` for anything else. `doctor` reports the same seven ids and whether each `SKILL.md` and `WRAPPER.md` is on disk. It does not build a site.
- `run_job` walks those seats with `live` false. The only door to a hand is `_call_hand`, which calls `seat_gate(role_id, role_id, name)` first. A refused gate is status `FAIL`, the gate `error` string, and the hand is not called. The three errors are `unknown seat`, `caller differs from seat`, and `unknown hand`. The selftest already refuses architect calling `render`, content calling architect `frame_pick`, and architect calling `frame_list`. `frame_list` is not a seat hand.
- The first `FAIL` stops later seats. Deployer still runs last and still writes `<out>/crew-ticket.json`. Seats that never started are absent from `hands`, not marked `PASS`. After the visual row, `_rerender_once` may append a second frontend row and a second visual row when `<out>/index.html` exists and a trigger hit has `fix` `rerender`. Those extra rows stay in the ticket. They do not replace an earlier `FAIL`.
- A seat status is `FAIL` if any of its hands failed, `SKIP` only if every hand on that seat is `SKIP`, otherwise `PASS`. Graphics can pass the seat while `vault_photos` says `SKIP` (`snapshot not in vault for ...`). The joined detail still contains that sentence. Deployer's detail is the same sentence on pass and fail: `ticket written; publish is a Keith click (library bind --live)`. The status word is the difference. `ok` is true only when every hand status is `PASS`. `publish` is always `Keith click. This run does not deploy.`
- Architect `library_bind` is a draft ledger row (`bound <site> -> <mold> (draft)`). Before that hand, a mold already `"live": true` on another site fails the seat and does not bind. `library/ledger.json` has `warmth-authority` live on `movelixir.com`. `discover-grid` and `clarify-mix` are on the ledger with `live` false. `live_conflict` only looks at live rows.
- `serve` hosts an existing site folder on `127.0.0.1` only, after `index.html` exists. The printed URL says `localhost`. It does not publish.

What Bolt shows a person before the page exists, from `library/research/competitors/bolt.md` (help center opened 2026-10-08, not re-measured here): a chat prompt, then Build now. Plan mode is optional. Inside an open project, Plan mode does not change code until the person chooses Implement this plan. Homepage Plan mode is different: it creates the base structure before the plan is approved. The preview is not the published site. Publish is a second explicit action, and a chat prompt can also be told to publish. There is no public seven-seat board and no public section catalog. What Bolt's model must not invent is not public. SpiderCaster does not copy the chat, the homepage plan that builds first, or a publish control.

## 3. Screen

The board is empty of results until a person acts. Every visible status word comes from a command or from `crew-ticket.json`. The screen does not write a slogan, a review, or a page sentence.

1. Open the board. It is a localhost page. Before any HTML site exists, it lists seven rows from `crew roles`, deployer last. Each row shows the number, id, label, hands, and `does_not`. Status on every row is the words `not run`. No row is `PASS`.
2. Read doctor. Control: `Doctor`. If `ok` is false, the error strings stay on the page and `Run crew` stays refused.
3. Choose the project. Control: `Project`, two choices only: `projects/demo-local` and `projects/bench-harbor-tearoom`. Any other path, including a fleet domain, is refused. The board does not create a project and does not edit `brief.md` or `copy/`.
4. Type the site host. Control: `Site`, required, starts empty. The board does not prefill `movelixir.com` or a fleet domain. An empty site is refused before a run (`crew run` requires `--site`).
5. Choose one mold or scratch. Control: `Mold`. Choices that may run: `discover-grid`, `clarify-mix`, or `Scratch`. `warmth-authority` is shown and refused, because the ledger marks it live on `movelixir.com`. Scratch uses the existing `crew run --scratch` knobs only: palette, type-lead, nav, template. There is no free CSS field. A missing mold and no scratch is refused with `pass --mold or --scratch`.
6. Choose a frame or leave copy order. Control: `Frame`, default `copy order` (no `--frame`). The other choices are the fourteen ids in `library/frames`. A missing id is refused later by `frame_pick`. The control does not call `frame_list` as a hand.
7. Accept the plan. Control: `Accept plan`. This only unlocks the next control. It does not write HTML, does not bind, and does not publish. This is the in-project Bolt rule (plan, then a separate implement), not homepage Plan mode.
8. Run the crew. Control: `Run crew`. It stays refused until doctor is ok, the project is one of the two, `Site` is non-empty, the mold is not `warmth-authority`, and `Accept plan` is on. The command is `crew run` with `--mold` or `--scratch`, optional `--frame`, and `--out`. It does not pass `--live`, `--indexable`, or `--vendor`. The out path is shown before the click.
9. Read the ticket. The page draws all seven seat ids even when the ticket omits some. A row whose id is absent is `did not run`, not `PASS`. A row in `hands` shows `PASS`, `FAIL`, or `SKIP`, then the detail, uncut. A second frontend row and a second visual row, if the ticket has them, stay visible after the first visual row and before deployer. Deployer is last. Its status word is shown before the Keith-click sentence. `ok` and the `publish` line stay on the page. There is no Publish control.
10. Look at the built page only after a ticket exists and `index.html` is on disk. Controls: `Check` (`check <out> --expect-noindex`), `Visit` (`visit <out>`), `Preview` (`serve <out>`). `Check` with `--expect-indexable` is refused. `Preview` is refused when `index.html` is missing (`no index.html in <out>; run a build first`). `Preview` is the existing serve, bound to `127.0.0.1`.

A hand that is not on that seat is not a control. The allowlist on the row is the seat pack. If a run still returns a gate error, that row shows `FAIL` and the error (`unknown seat`, `caller differs from seat`, or `unknown hand`). The screen does not call the hand anyway.

Other refusals the rows must show, in the seat's own words:

- Architect: empty brief (`brief.md is empty`), missing frame, `pass mold_id or scratch fields`, or `mold <id> is already live on <site>`. A draft bind line is not a publish.
- Content: `copy/ has no blocks; nothing was invented to fill them`, or `block file is not under copy/`. The screen does not fill the gap.
- Frontend: `offline planner: no copy blocks found; add files under copy/`, or `out is required`.
- Graphics: `remote asset urls are not allowed`. A vault `SKIP` stays in the detail. The screen does not download a photo and does not offer `image`.
- Visual: the failed check names, comma-joined, or `out is required`. `WARN` does not fail the hand. The screen does not edit the HTML to clear a row.
- SEO: `mold <id> is already live on <site>`, or `meta or sample checks failed`. The screen does not bind.
- Deployer: status `FAIL` when any earlier hand is `FAIL` or missing from the ticket. It still only writes `crew-ticket.json`. Upload, `library bind --live`, and `shipcheck` are refused. `shipcheck` is not a seat hand.

## 4. Already here

No studio page exists. `serve` only hosts a finished site folder. These commands are the board:

- `python spidercaster.py doctor` shows the seven seats and whether the tree is ok. It writes no site.
- `python spidercaster.py crew roles` prints the seven labels, hands, and `does_not` lines.
- `python spidercaster.py seat <id>` prints one pack. Unknown id: `unknown seat`, exit 2.
- `python spidercaster.py library list` lists package molds and package frames. It does not bind.
- `python spidercaster.py crew run <project> --site <host> --mold <id> --out <dir>` runs the seats, writes the site and `crew-ticket.json`, prints `[STATUS] role: detail`, then the publish sentence and the ticket path. Exit 0 when `ok` is true, exit 1 when it is not. Exit 2 when the mold is missing or scratch is refused, before a ticket. `live` in the job context is false. Deployer does not upload.
- `python spidercaster.py check <out> --expect-noindex` and `python spidercaster.py visit <out>` judge a built page. `python spidercaster.py serve <out>` previews it on `127.0.0.1`.

`seat_gate` is a library function and an MCP tool. It is not a CLI verb. The crew already calls it. This screen does not add a second gate and does not change the function.

The saved workflow file (`SPIDERCASTER_PROFILE_ENGINE`, else `V:\A\Ai\COSMOS\live\state\profiles\website\engine.json`) was not opened for this report. When that file has a valid seven-id list, `run_job` uses it and still forces deployer last. Otherwise the package order stands. The board must show the order the run will use, not a second order.

## 5. Proposal

The smallest surface is one stdlib page on `127.0.0.1` only. No new package. No React, Tailwind, shadcn, or chat field. The page shells out to the commands in section 4 and reads `crew-ticket.json`. It does not import a new publisher and it does not call `library bind`.

`Accept plan` is a control on that page, not a new engine flag and not a new project file. Until it is on, the page does not start `crew run`, so no HTML is written. `Run crew` is the implement step. It is the only control that writes the site. Architect may still write a draft ledger row, because that is what `crew run` already does. The page shows the `(draft)` detail and the sentence `Keith click. This run does not deploy.` It never passes `--live`.

The page always paints seven seats. Ticket rows fill the ones that acted. Absent ids stay `did not run`. Extra rerender rows stay extra. `Preview` calls the existing `serve` and does not bind the studio to `0.0.0.0`.

Do not add a Publish button, a prompt box, an image button, a copy editor, `crew selftest`, or `shipcheck`. Do not copy Bolt homepage Plan mode, which builds the app before the person accepts the plan.

## 6. 4Cs+ test

Phone-width window, the board itself, at 360, 390, and 412. One `h1`. A skip link to the seat list. A sticky header that keeps the seven ids visible. Body text 18px, chrome (labels, status, hands) 16px, every control at least 44px. Contrast 4.5:1 on the status words, 3:1 if a status is large text. Seats stack in one column. No sideways overflow. Status is the word `PASS`, `FAIL`, `SKIP`, `not run`, or `did not run`, not color alone. The board is a localhost tool. It does not get a sitemap, and it is not a stand-in for the built page's JSON-LD.

Built page, only after `Run crew`, and only for a project that already has copy. The visual row must show `checker 0 FAIL, noindex on` or the failed check names. The person judges that page with `Check` (`--expect-noindex`) and, when they want the widths, `Visit`. `visit` measures 390x800 and 1280x800 only after Playwright launches a browser. A missing browser is not a pass. Whether Playwright is installed on this machine was not measured here. The built page stays noindex. Copy on that page is whatever `copy/` already said. This screen adds none. `Preview` is `serve` on `127.0.0.1`. It is not a live host.

## 7. Risks

Inventing copy. A chat box, a "fill the gap" control, or a project other than `demo-local` and `bench-harbor-tearoom` would write facts the files do not have. Bolt's prompt and stock images are that risk. The content failure `nothing was invented to fill them` must stay on the row. The board must not clear it by writing `copy/`.

Deploying. A Publish control, `library bind --live`, `--indexable`, or a chat line that says publish would leave this screen. A draft bind and the deployer sentence look like success if the status word is hidden. `warmth-authority` on a second site must stay refused. `serve` on anything but `127.0.0.1` would widen a preview into a host. `crew selftest` is not a go-live button. It is not on this screen.

Hiding a failure. Painting a missing seat `PASS`, folding a later rerender over an earlier `FAIL`, or showing the deployer sentence without `FAIL` would hide who was refused. A vault `SKIP` hidden inside a green graphics row would hide a missing snapshot. A gate error swallowed, or a doctor error replaced with an empty board, would hide a refused hand. Exit 2 (`pass --mold or --scratch`, `scratch mold refused`, `unknown seat`) happens before a ticket. The page must show that text. It must not look like a clean run.
