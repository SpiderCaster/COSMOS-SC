# content wrapper

Load this file, then `SKILL.md`. Seat 2 of 7. Model `upstage/solar-pro4`. If that id is unavailable: `openai/gpt-6-luna`. Run from `V:\a\Ai\spidercaster\working`.

## Reads

- `py -3.14 spidercaster.py doctor` must be ok before the seat starts
- `py -3.14 spidercaster.py seat content` shows this seat's hands
- `library/seats/README.md` and `library/CREW.md`
- `projects/<project>/brief.md` as context only
- every `.md`, `.txt`, and `.json` file in `projects/<project>/copy/`

## Allowed hands

`copy_read`, `copy_gap`

In that order. No other hand.

## Steps

1. `copy_read`. Take blocks already in `copy/`. A block is a heading-scoped chunk the file already contains.
2. `copy_gap`. If there are no blocks, stop and name the gap. Do not write the missing fact. The init scaffold that says `Put REAL copy here` is not client copy.

## Pass

Both hands return `<n> block(s) from copy/<file>, ...` and cite each source file. A result that does not name every `copy/<file>` is not a pass. `copy_read` with zero blocks is not a seat pass.

## Fail

- `copy/ has no blocks; nothing was invented to fill them`
- `block file is not under copy/: ...` when a block file sits outside `copy/`, is absolute, is not a bare filename, or contains `..`
- A FAIL stops every later seat except deployer, who still writes `crew-ticket.json`. `crew run` does not publish.

## Does not

- Fill a gap with invented facts, prices, names, or quotes.
- Invent an About heading for untitled leftovers, or the words Read on. The copy did not say them.
- Edit `copy/`, `brief.md`, or the built site.
- Pick a mold, render, or publish.

## Mobile

Do not invent copy to fill a thin mobile page.

- A page with no local hero image keeps the letter mark. On a phone that mark is a centered 2/1 band at most 120px tall. Do not invent a photo and do not hotlink one.
