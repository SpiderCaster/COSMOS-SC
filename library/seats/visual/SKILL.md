---
name: spidercaster-visual
description: >-
  Use when a built site must be machine-checked with noindex and any FAIL must stop the crew, not when the task is approving the design by eye, making pages indexable, or publishing.
---

# spidercaster-visual

## When not to use

- There is no `<out>/index.html` yet.
- The task is to restyle, rewrite, or clear a FAIL by editing.
- Someone asks to drop noindex or to publish.

## Start

1. Read `library/seats/README.md` and `library/CREW.md`.
2. Run the command from `V:\a\Ai\spidercaster\working`.
3. Call only `check_site`. The checker is the gate.
4. Read-only orientation, not hands:

   `py -3.14 spidercaster.py doctor`

   `py -3.14 spidercaster.py seat visual`

## Steps

1. **check_site.** From `V:\a\Ai\spidercaster\working`:

   `python spidercaster.py check <out> --expect-noindex`

   `check_site` passes the project's copy text into the checker. A page that says testimonial, customer review, award-winning, or a star rating that the copy files do not contain fails as `ungrounded_claim`. Do not invent copy.

   Staged pages stay noindex. The hero visual is a local image or the letter mark. A remote image URL fails. Read every row. If any status is `FAIL`, stop and quote the row names. Do not pass `--expect-indexable`. Do not edit HTML, `site.json`, or copy to make a row pass.

## Exit

Return the pass / fail / warn / skip counts and the FAIL names, if any. Stop.

## Do not

- Approve your own design. The checker is the gate.
- Invent copy, or treat a clean visual impression as a pass.
- Flip noindex off, or publish. Staged pages stay noindex. `crew run` does not publish.
- Call `shipcheck`. It is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.

## Risk tier

Tier 0 read-only check.

## Mobile

Fail height 168px, hidden reveal, empty about-panel, and a missing skip link.

- Photo heroes stay 16/9. Letter-mark heroes (.hero-visual.hero-mark) stay at max-height 140px on phones.
- The primary button is full width under 860px.
- The current-section label (.nav-here) stays visible as one truncated line.
- Phone menu rows hide the dotted leader.
- Contact is the last section. The hero has one button, and its label is the next titled section.
- A hero lede is one paragraph per sentence already in the copy.
- On a phone, .about-body has an accent left border, and each .menu-item has a bottom border except the last.
- On a phone, a contact number already in the copy is also a fixed .phone-bar link. The label is that number. Pages with no phone number get no bar.
- On a phone the current-section label stays at most 4.5rem wide. While it repeats the brand name, the label is cleared so the header shows the name once.
- On a phone, headings balance their lines, menu prices use tabular figures, and cards do not jump on touch.
- On a phone, a card icon sits beside its heading, and a group of cards shares one bordered list.
