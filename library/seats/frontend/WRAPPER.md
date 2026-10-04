# frontend wrapper

Load this file, then `SKILL.md`. Seat 3 of 7. Model `upstage/solar-pro4`. If that id is unavailable: `deepseek/deepseek-v4-flash`. Run from `V:\a\Ai\spidercaster\working`.

## Reads

- `py -3.14 spidercaster.py doctor` must be ok before the seat starts
- `py -3.14 spidercaster.py seat frontend` shows this seat's hands
- `library/seats/README.md` and `library/CREW.md`
- the draft mold in `library/molds/<id>.json` (`template`, `palette`)
- the copy blocks content cited
- `<out>/site.json` after the render

## Allowed hands

`plan_offline`, `render`

In that order. No other hand.

## Steps

1. `plan_offline`. Plan from the real copy blocks and the mold template. Stay offline. Do not call a paid planner. A picked frame only reorders sections the plan already has. The hero button names the next section that has a title. It does not say Read on unless the copy says those words. Untitled leftovers do not get an About heading. A menu group with the same name as the section does not render a second heading.
2. `render`. Write the pages to `<out>` with noindex left on, and write `<out>/site.json`. Staged pages stay noindex. Do not pass `--indexable`. A local `assets/hero.png`, `assets/hero.jpg`, `assets/hero.jpeg`, or `assets/hero.webp` is copied into the build. Remote image URLs are rejected. The letter mark is used when no local file exists.

## Pass

- `planned <n> page(s)`
- `<n> page(s) written`
- `<out>/index.html` exists and stays noindex

## Fail

- `offline planner: no copy blocks found; add files under copy/`
- `out is required`
- Stop before `render` if the mold file has no `template` or no `#rrggbb` palette.
- A FAIL stops every later seat except deployer, who still writes `crew-ticket.json`. `crew run` does not publish.

## Does not

- Hotlink a photo or ship a vendor demo as-is. Remote image URLs are rejected. The letter mark is used when no local file exists.
- Invent sections the copy does not support. Untitled leftovers do not get an About heading.
- Label the hero button Read on unless the copy says those words.
- Pass `--indexable` or call a paid planner. Staged pages stay noindex.
- Call `shipcheck`. It is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.

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
