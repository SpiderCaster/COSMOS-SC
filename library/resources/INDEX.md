# Hand resources

A seat calls only its hands. Hands call library code. They do not publish, and they do not download OceanWP, GeneratePress, or photos.

Vault: `V:\streams\webdev\vendor-vault` (override `SPIDERCASTER_VAULT`).
Package molds: `V:\a\Ai\spidercaster\working\library\molds`.
A run's ledger is `ledger.json` next to the molds it was given. Tests use a temp library, not the package ledger.

Photos are not pulled yet. Vault frames are names only until `library accept`.

| Hand | Module | Reads | Seat |
|---|---|---|---|
| brief_read | `ingest.load_project` | `<project>\brief.md` | architect |
| frame_pick | `frames.load_frame` | `library/frames/<id>.json` | architect |
| mold_pick | `Library.load_mold` or `Library.save_mold` | `<library>\molds\<id>.json` | architect |
| library_bind | `Library.bind` (live only if `ctx["live"]`) | `<library>\ledger.json` | architect |
| copy_read | `ingest.load_project` | `<project>\copy\`; PASS cites each block file | content |
| copy_gap | `ingest.load_project` | `<project>\copy\`; a file outside that folder is FAIL | content |
| plan_offline | `offline.plan_offline`, `frames.apply_frame`, `ir.normalize_site` | copy blocks; a loaded frame reorders those sections and does not invent one; returns the IR, does not write HTML | frontend |
| render | `render.assemble` | site IR; writes `<out>\*.html` and `<out>\site.json` | frontend |
| asset_list | `ingest.load_project` | `<project>\assets.json` and copy image urls | graphics |
| vault_photos | `Library.frames` | `<vault>\frames.json`; snapshot filenames if a snapshot is already there | graphics |
| check_site | `check.check_site` | `<out>\*.html` (noindex) | visual |
| uniqueness | `Library.live_conflict` | `<library>\ledger.json` | seo |
| meta_basics | `check.check_site` | `<out>\*.html` | seo |
| ticket_write | writes `crew-ticket.json` | `<out>\crew-ticket.json` | deployer |
| frame_list | MCP tool `frame_list`; library `frames.list_frames` | `library/frames/*.json` | not a seat hand |
| doctor | `doctor.report` | python, mold ids, frame-file count, seat skill and wrapper files, hand order; CLI `spidercaster.py doctor` | not a seat hand |
| seat | `seatpack.pack` | one role from `ROLES` and paths under `library/seats/<id>/`; CLI `spidercaster.py seat <id>` | not a seat hand |
| sandbox | `sandbox.attempt_dir`, `sandbox.release` | creates `<root>\<name>` inside an existing root; `release` writes `_released.txt` and does not delete | not a seat hand |
| skill_read | `skill_read.skill_read` | `<root>\<rel>` (one SKILL.md); writes nothing | not a seat hand |
| hook_match | `hook_match.hook_match` | in-memory hooks object; writes nothing | not a seat hand |
| perm_rule | `perm_rule.perm_rule` | allow and deny rule strings in memory; writes nothing | not a seat hand |
| tool_search_local | `tool_search_local.tool_search_local` | in-memory catalog of name and description; writes nothing | not a seat hand |
| seat_tools | `seat_tools.seat_tools` | parent, tools, and disallowed lists in memory; writes nothing | not a seat hand |
| seat_gate | `seat_gate.seat_gate` | caller, seat, and hand against `ROLES`; does not call the hand; writes nothing | not a seat hand |
| layer_read | `layer_read.layer_read` | first page of `<out>\site.json`; writes nothing | not a seat hand |
| code_refuse | `code_refuse.code_refuse` | one kind string; writes nothing | not a seat hand |
| mold_panel | `mold_panel.mold_panel` | `<root>\library\molds\<id>.json`; writes nothing | not a seat hand |
| session_mark | `session_mark.session_mark` | appends `<out>\session.jsonl`; does not publish | not a seat hand |

`copy_gap` fails when `copy/` has no blocks. It does not invent copy.
`vault_photos` lists filenames already in the vault. A missing snapshot is SKIP. It does not fetch.
`asset_list` fails on an `http` or `https` asset url.
`uniqueness` fails when that mold is already live on another site.
`ticket_write` never uploads. Publish remains `library bind --live`.
`frame_list` is not in `HANDS`. `lib.hands.frame_list` calls `frames.list_frames` and is not registered. Architect hands are `brief_read`, `frame_pick`, `mold_pick`, `library_bind`.
`doctor`, `seat`, and `sandbox` are not in `HANDS`. `sandbox` has no CLI verb. `release` does not delete the attempt.
`skill_read`, `hook_match`, `perm_rule`, `tool_search_local`, `seat_tools`, `seat_gate`, `layer_read`, `code_refuse`, and `mold_panel` write nothing. `session_mark` appends `<out>\session.jsonl` and does not publish. None of these is a seat hand.

## Phone

These files are resources, not new seat hands. Architect hands stay `brief_read`, `frame_pick`, `mold_pick`, `library_bind`.

- `library/resources/MOBILE.md` — seat card for the phone layout already in the renderer
- `library/resources/PHONE_TYPE.md` — seat card for phone type size against `CSS_TEMPLATE`
- `library/resources/PHONE_A11Y.md` — seat card for accessibility on pages below 860px
- `library/rules/mobile.json` — machine phone-layout rules (`spidercaster-mobile-rules/1`)
- `library/rules/phone-type.json` — machine type-size rules (`spidercaster-phone-type/1`)
- `library/rules/phone-a11y.json` — machine accessibility rules below 860px (`spidercaster-phone-a11y/1`)
- `library/research/app/HOW_MOBILE.md` — how a brochure page sits on a small screen
- `library/research/app/ELITE_MOBILE.md` — public pages read at a 390 by 844 phone layout
- `library/research/app/HOW_LOOPS.md` — loops and triggers that raise output quality
- `library/research/app/HOW_PHONE_SPEED.md` — how a small static page stays fast on a phone
- `library/research/app/HOW_PHONE_HEADER.md` — phone header behavior under max-width 860px
- `library/research/app/HOW_PHONE_MENU.md` — menu-row markup the renderer emits, including at 360px
- `library/research/app/THIN_PAGE.md` — thin-page causes that remain after the assigned phone rules
- `library/research/app/RENDER_NEXT.md` — the renderer pass after the mobile render inbox
- `library/research/app/TRIGGER_NEXT.md` — next mobile trigger notes from `lib/triggers.py`
- `library/research/app/RESOURCES_MOBILE.md` — resource finder for a phone-layout pass
