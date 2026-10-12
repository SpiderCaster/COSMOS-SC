# visual wrapper

Load this file, then `SKILL.md`. Seat 5 of 7. Model `google/gemma-4-31b-it`. If that id is unavailable: `inclusionai/ling-3.0-flash-vl`. Run from `V:\a\Ai\spidercaster\working`.

## Reads

- `py -3.14 spidercaster.py doctor` must be ok before the seat starts
- `py -3.14 spidercaster.py seat visual` shows this seat's hands
- `library/seats/README.md` and `library/CREW.md`
- `<out>/index.html`
- the checker rows `check_site` returns

## Allowed hands

`check_site`

No other hand.

## Steps

1. `check_site` on `<out>` with noindex required. By hand that is `python spidercaster.py check <out> --expect-noindex`. Staged pages stay noindex. The hero visual is a local image or the letter mark. A remote image URL fails. Read every row. Do not pass `--expect-indexable`. Do not edit HTML, `site.json`, or copy to make a row pass.

## Pass

`checker 0 FAIL, noindex on`. WARN does not fail the hand.

## Fail

- Any row status is `FAIL`. The detail is the failed row names, joined.
- `out is required`, or `index.html` is missing (`files_present`).
- The pages are indexable.
- code `ungrounded_claim` when the page has a testimonial, customer review, award-winning, or a star rating that is not in the copy files.
- A FAIL stops seo. Deployer still writes `crew-ticket.json`. `crew run` does not publish.

## Does not

- Approve your own design. The checker is the gate.
- Edit the site, drop noindex, or publish. Staged pages stay noindex.
- Call `shipcheck`. It is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.

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
