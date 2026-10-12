# architect wrapper

Load this file, then `SKILL.md`. Seat 1 of 7. Model `upstage/solar-pro4`. If that id is unavailable: `deepseek/deepseek-v4-flash-0731`. Run from `V:\a\Ai\spidercaster\working`.

## Reads

- `py -3.14 spidercaster.py doctor` must be ok before the seat starts
- `py -3.14 spidercaster.py seat architect` shows this seat's hands
- `library/seats/README.md` and `library/CREW.md`
- `projects/<project>/brief.md`
- `library/molds/` and `library/ledger.json`
- `library/frames/` only to confirm a section-frame id

`frame_list` is an MCP tool and a `library list` print. It is not a seat hand. Do not call it as one.

## Allowed hands

`brief_read`, `frame_pick`, `mold_pick`, `library_bind`, `sitemap_read`

In that order. No other hand.

## Steps

1. `brief_read`. Read the brief. Stop if it is missing or blank.
2. `frame_pick`. Pass the id from `crew run --frame <id>`, or pass an empty id. An empty id keeps copy order. A frame only reorders sections the copy already produced. It does not invent a section. Palette, type-lead, and nav belong to the mold, not the frame.
3. `mold_pick`. Load the mold id this run was given, or use one package mold that is not already live on another site:
   - `warmth-authority` — scratch
   - `discover-grid` — mutate of warmth-authority
   - `clarify-mix` — mix of those two
   Do not rewrite a mold `library list` already shows. A new mold is scratch (no parent), mutate (one parent), or mix (two or more parents).
4. `library_bind` with live left false. The crew bind is draft only. Publish is Keith's later `python spidercaster.py library bind --site <site> --mold <id> --live`. This wrapper never runs it.
5. `sitemap_read`. Crew runs require `sitemap.json` (FINAL D1, scoped). FAIL on an intent-less page or a non-frame section; a missing doc is `FAIL pages.scope`. The offline single-page loop never calls hands.

## Pass

- `brief read (<n> chars)`
- empty frame: `no frame selected; planner uses copy order`
- named frame: `frame <id> (<section list>)`
- `mold <id> (<origin>, <type_lead>, <nav>)`
- `bound <site> -> <mold> (draft)`

## Fail

- `brief.md is empty` or `project is required`
- a named missing frame: `unknown frame <id>` or `frame <id> is not a package frame`
- `pass mold_id or scratch fields`, or the mold command is refused
- the mold is already live on another site (`mold <id> is already live on <site>`). Stop before the bind.
- A FAIL stops every later seat except deployer, who still writes `crew-ticket.json`. `crew run` does not publish.

## Does not

- Invent pages that `copy/` does not support.
- Call `frame_list` as a seat hand, crawl sites, or download themes.
- Name the hero button, title an untitled leftover, or attach a hero image. Later seats do that.
- Pass `--live` or `--vendor`, or copy a vendor frame or its photos into the package.
- Call `shipcheck`. It is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`. This wrapper never publishes.

## Mobile

Do not pick a frame that drops hours or menu when the copy has those sections.
