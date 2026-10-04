---
name: spidercaster-frontend
description: >-
  Use when real copy blocks must be planned offline and rendered to noindex HTML under the chosen mold, not when copy/ has no blocks or the task is mold choice, image sourcing, the checker, SEO, or publish.
---

# spidercaster-frontend

## When not to use

- `copy/` has no real blocks (content seat stopped).
- The task is picking a mold, judging photos, running `check`, SEO, or publish.
- Someone asks for an indexable build.

## Start

1. Read `library/seats/README.md` and `library/CREW.md`.
2. Run commands from `V:\a\Ai\spidercaster\working`.
3. Call only `plan_offline`, then `render`. The mold id is the draft the architect bound.
4. Read-only orientation, not hands:

   `py -3.14 spidercaster.py doctor`

   `py -3.14 spidercaster.py seat frontend`

## Steps

1. **plan_offline.** Read `library/molds/<id>.json` for `template` (`editorial`, `modern`, or `bold`) and `palette`. Confirm `projects/<project>/copy/` has real blocks. A picked frame only reorders sections the plan already has. The hero button names the next section that has a title. It does not say Read on unless the copy says those words. Untitled leftovers do not get an About heading. A menu group with the same name as the section does not render a second heading. Stay offline. Do not call a paid planner. Stop if there are no copy blocks.
2. **render.** Write the pages to `<out>` and write `<out>/site.json`. `theme.template` stays the mold template and `theme.accent` stays the mold palette. Change no other field. Staged pages stay noindex. Do not pass `--indexable`. A local `assets/hero.png`, `assets/hero.jpg`, `assets/hero.jpeg`, or `assets/hero.webp` is copied into the build. Remote image URLs are rejected. The letter mark is used when no local file exists.

## Exit

Return the page filenames, the mold accent, and that noindex stayed on. Stop.

## Do not

- Hotlink a photo or ship a vendor demo as-is. Remote image URLs are rejected. The letter mark is used when no local file exists.
- Pass `--indexable`, invent sections the copy does not support, or call a paid planner. Staged pages stay noindex.
- Label the hero button Read on unless the copy says those words. Untitled leftovers do not get an About heading.
- Publish. `crew run` does not publish. `shipcheck` is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.

## Risk tier

Tier 0 local site files. Default remains noindex.

## Mobile

Phone layout is under 860px. The hero is 16/9. Content is visible without waiting for JavaScript.

- Photo heroes stay 16/9. Letter-mark heroes (.hero-visual.hero-mark) stay at max-height 140px on phones.
- The primary button is full width under 860px.
- The current-section label (.nav-here) stays visible as one truncated line.
- Phone menu rows hide the dotted leader.
- Contact is the last section. The hero button names the next titled section, and the hero shows that one button.
- A hero lede is split into the sentences already in the copy. No words are added.
- On a phone, a contact number already in the copy is also a fixed .phone-bar link. The label is that number. Pages with no phone number get no bar.
- On a phone the current-section label stays at most 4.5rem wide. While it repeats the brand name, the label is cleared so the header shows the name once.
- On a phone, headings balance their lines, menu prices use tabular figures, and cards do not jump on touch.
- On a phone, a card icon sits beside its heading, and a group of cards shares one bordered list.
