---
name: spidercaster-architect
description: >-
  Use when a real brief must become one new package mold and a draft bind for this site, not when the brief is empty, that mold is already live elsewhere, or the task is copy, HTML, images, the checker, SEO, or publish.
---

# spidercaster-architect

## When not to use

- The brief is missing, empty, or only the `init` placeholder.
- The mold id is already `"live": true` on another site in `library/ledger.json`.
- The task is copy, HTML, assets, `check`, SEO, or `library bind --live`.

## Start

1. Read `library/seats/README.md` and `library/CREW.md`.
2. Run commands from `V:\a\Ai\spidercaster\working`.
3. Call only `brief_read`, `frame_pick`, `mold_pick`, `library_bind`.
4. Read-only orientation, not hands:

   `py -3.14 spidercaster.py doctor`

   `py -3.14 spidercaster.py seat architect`

## Steps

1. **brief_read.** Read `projects/<project>/brief.md`. Stop if it is missing or blank.
2. **frame_pick.** A frame is a section order, not a mold. Read `library/frames/` and pass one id, or leave it empty so the planner keeps copy order. `frame_list` is an MCP tool and a `library list` print. It is not a seat hand. Do not call it as one. The frame nav and template are hints. The mold still owns palette, type-lead, and nav. `crew run --frame <id>` sets that id. Do not crawl sites or download themes.
3. **mold_pick.** Run `python spidercaster.py library list`. Read `library/ledger.json` and the mold JSON under `library/molds/`. Do not reuse an id that is already live, and do not rewrite a mold `library list` already shows. Save a new mold. Quote the palette so PowerShell does not treat `#` as a comment:

   `python spidercaster.py library mold --id <id> --origin scratch|mutate|mix --palette "#rrggbb" --type-lead serif|sans|slab|mono-display --nav segmented|top-bar|sidebar|one-page|footer-only --template editorial|modern|bold`

   - scratch: no `--parent`.
   - mutate: exactly one `--parent`. Palette, type-lead, and nav all differ from that parent. A vendor parent is `owp:<slug>` or `gp:<slug>` already named in the vault. If the command says `unknown parent frame`, stop. Do not download a demo.
   - mix: two or more `--parent` flags. A mix is not an as-is vendor frame.
4. **library_bind.** `library_bind` in the crew is draft only. If any other ledger row has this mold id and `"live": true`, stop. Otherwise:

   `python spidercaster.py library bind --site <site> --mold <id>`

   Do not pass `--live` or `--vendor`. Stop if the command says `refused`. Publish is Keith's `library bind --live`. `crew run` does not publish.

## Exit

Return the mold id, origin, palette, type-lead, nav, and the draft bind line. Stop. Do not render the site.

## Do not

- Invent pages that `copy/` does not support.
- Call `frame_list` as a seat hand, crawl sites, or download themes.
- Name the hero button, title an untitled leftover, or attach a hero image. Later seats do that.
- Pass `--live`, copy a vendor frame or its photos into the package, or publish. `shipcheck` is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.

## Risk tier

Tier 0 local files. The draft bind writes `library/ledger.json` with `"live": false`. Publish is not this seat.

## Mobile

Do not pick a frame that drops hours or menu when the copy has those sections.
