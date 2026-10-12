# SpiderCaster mobile board

Coordinator stopped. Statuses below are the latest poll, not a history log.

Last poll: cycle 14 at 2026-10-01 16:18:48. Nine inboxes say DONE. Four do not. The window ended. Polling stopped. It did not stop early.

## Ownership

| Agent | Owns | Inbox | Status |
| --- | --- | --- | --- |
| how-mobile | library/research/app/HOW_MOBILE.md | inbox/how-mobile.md | DONE |
| elite-mobile | library/research/app/ELITE_MOBILE.md | inbox/elite-mobile.md | STARTED |
| how-loops | library/research/app/HOW_LOOPS.md | inbox/how-loops.md | DONE |
| render-mobile | lib/render.py | inbox/render-mobile.md | DONE |
| triggers | lib/triggers.py | inbox/triggers.md | DONE |
| crew-loop | lib/crew.py | inbox/crew-loop.md | DONE |
| check-mobile | lib/check.py | inbox/check-mobile.md | DONE |
| mobile-rules | library/resources/MOBILE.md and library/rules/mobile.json | inbox/mobile-rules.md | DONE |
| skills-mobile | library/seats/architect/SKILL.md and the other six seat skills and wrappers | inbox/skills-mobile.md | DONE |
| mobile-selftest | lib/mobile_selftest.py | inbox/mobile-selftest.md | DONE |
| harbor-mobile | staged Harbor page (crew not run; HARBOR_MOBILE.md was not written) | inbox/harbor-mobile.md | STOPPED |
| demo-mobile | staged demo page (crew not run; DEMO_MOBILE.md was not written) | inbox/demo-mobile.md | STOPPED |
| mobile-result | library/research/app/MOBILE_RESULT.md | inbox/mobile-result.md | STARTED |

## Product rules

- Phone layout is under 860px.
- Staged pages stay noindex.
- No library bind --live.
- No invented copy.
- Coordinator writes only BOARD_MOBILE.md and inbox/coordinator-mobile.md. No Python, no stage output, no skills.

## What landed

A deliverable is opened only after that owner's inbox says DONE. A mention of the word DONE inside a STARTED note is not a completion. One sentence below is from the first 20 lines of that deliverable.

- how-mobile (`library/research/app/HOW_MOBILE.md`): Scope: the CSS that applies when `max-width: 860px` matches.
- how-loops (`library/research/app/HOW_LOOPS.md`): Scope: how a professional system decides to try again, stop, or only record, and what a six-row cap would mean for SpiderCaster.
- render-mobile (`lib/render.py`): Single-file pages (inline CSS + JS), system font stacks, inline SVG icons, gradient visuals.
- triggers (`lib/triggers.py`): Does not fetch a URL.
- crew-loop (`lib/crew.py`): No hand publishes.
- check-mobile (`lib/check.py`): Index text rows for the phone layout: height:168px fails mobile_hero and aspect-ratio:16/9 passes it.
- mobile-rules (`library/resources/MOBILE.md`): Read from `lib/render.py` and `lib/triggers.py` on 2026-10-01, after the wait.
- skills-mobile (`library/seats/architect/SKILL.md`): Use when a real brief must become one new package mold and a draft bind for this site, not when the brief is empty, that mold is already live elsewhere, or the task is copy, HTML, images, the checker, SEO, or publish.
- mobile-selftest (`lib/mobile_selftest.py`): Builds a tiny temp project and calls the crew hands the way lib/regress.py does: plan_offline, then render.assemble.

## Conflicts

This coordinator did not edit Python, stage output, or skills, and did not re-run the commands named in the inboxes.

`inbox/mobile-selftest.md` records `py -3.14 -m lib.mobile_selftest` exit 2. The lines it quotes are `missing aspect-ratio:16/9`, `still present height:168px`, and `still present about-panel`. That DONE note is from cycle 7 (16:15:26). `inbox/render-mobile.md` said DONE later, at cycle 12 (16:17:57), and says `height:168px` is gone, the `.about-panel` class is gone from the stylesheet, and `lib.hands.selftest`, `lib.regress`, and `spidercaster.py crew selftest` printed ok.

`inbox/mobile-rules.md` says the stylesheet still contains the selector `.about-panel`, so `no_empty_panel` and `empty_panel` still match that text. `inbox/render-mobile.md` says the stylesheet no longer contains that class. Those two DONE notes disagree. This coordinator did not re-read the stylesheet.

`inbox/harbor-mobile.md` and `inbox/demo-mobile.md` stopped at about 16:15 because `inbox/render-mobile.md` was still STARTED. Render-mobile said DONE at 16:17:57, after those waits ended. Neither inbox says the staged page was rebuilt. `inbox/mobile-result.md` is still STARTED and is waiting until both of those say DONE.

`inbox/skills-mobile.md` says a Mobile section is on each seat skill and wrapper. The sentence above is from the first 20 lines of `library/seats/architect/SKILL.md`, which is the seat description, not that Mobile section. The rerender loop is not in the first 20 lines of `lib/crew.py`. The phone CSS under 860px is not in the first 20 lines of `lib/render.py`.

## Parent should do next

Leave staged pages noindex. Do not bind the library live. Do not treat STARTED or STOPPED as DONE. Phone layout stays under 860px. No invented copy.

Inboxes still not DONE:

- elite-mobile — STARTED. It names `library/research/app/ELITE_MOBILE.md`. The inbox has no DONE line.
- harbor-mobile — STOPPED. It polled `inbox/render-mobile.md` from 16:06:59 through 16:15:00 and never saw DONE. Crew was not run. `HARBOR_MOBILE.md` was not written. `stage/harbor/src/assets/hero.png` was left in place.
- demo-mobile — STOPPED. It polled `inbox/render-mobile.md` from 16:07:02 through 16:15:02 and never saw DONE. Crew was not run. `DEMO_MOBILE.md` was not written. No image was added.
- mobile-result — STARTED. It waits until both `inbox/harbor-mobile.md` and `inbox/demo-mobile.md` say DONE, then writes `library/research/app/MOBILE_RESULT.md`. Neither of those says DONE.
