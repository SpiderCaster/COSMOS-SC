---
name: spidercaster-content
description: >-
  Use when a project's copy/ must be read for real blocks and empty gaps named, not when facts would have to be invented or the task is molds, HTML, images, the checker, SEO, or publish.
---

# spidercaster-content

## When not to use

- The work is to write new claims, prices, names, or quotes.
- `copy/` has no client facts.
- The task is a mold, a bind, HTML, assets, `check`, SEO, or publish.

## Start

1. Read `library/seats/README.md` and `library/CREW.md`.
2. Work in `projects/<project>/`. Do not create copy.
3. Call only `copy_read`, then `copy_gap`.
4. Read-only orientation, not hands:

   `py -3.14 spidercaster.py doctor`

   `py -3.14 spidercaster.py seat content`

## Steps

1. **copy_read.** Read `brief.md` only as context. Read every `.md`, `.txt`, and `.json` file in `copy/`. A block is a heading-scoped chunk with a title, paragraph, bullet, numbered line, Q&A, or price line that the file already contains.
2. **copy_gap.** The `init` scaffold `copy/README.md` that starts with `# Copy folder` and `Put REAL copy here` is not client copy. If no other file has a block, stop and say `copy/ has no blocks`. Name which file would have to supply a missing fact. Do not write that fact.

## Exit

Return the block count and every `copy/` filename the blocks came from, or the gap. Zero blocks is not a pass. Stop. Do not hand invented sentences to the next seat. `crew run` does not publish.

## Do not

- Fill a gap with invented facts, prices, names, or quotes.
- Invent an About heading for untitled leftovers, or the words Read on. The copy did not say them.
- Edit `copy/`, `brief.md`, or the built site.

## Risk tier

Tier 0 read-only.

## Mobile

Do not invent copy to fill a thin mobile page.

- A page with no local hero image keeps the letter mark. On a phone that mark is a centered 2/1 band at most 120px tall. Do not invent a photo and do not hotlink one.
