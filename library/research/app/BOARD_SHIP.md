# SpiderCaster ship board

Coordinator stopped. Statuses below are the latest poll, not a history log.

Last poll: cycle 21 at 2026-10-01 15:56:32. All eight inboxes say DONE. Poll stopped early. Window would have ended 15:56:48.

## Ownership

| Agent | Owns | Inbox | Status |
| --- | --- | --- | --- |
| how-fast | library/research/app/HOW_FAST.md | inbox/how-fast.md | DONE |
| how-quality | library/research/app/HOW_SHIP_QUALITY.md | inbox/how-quality.md | DONE |
| regress | lib/regress.py | inbox/regress.md | DONE |
| check-ship | lib/check.py | inbox/check-ship.md | DONE |
| shipcheck | lib/shipcheck.py and spidercaster.py shipcheck | inbox/shipcheck.md | DONE |
| public-snapshot | make_public.py | inbox/public-snapshot.md | DONE |
| skills-ship | seven library/seats SKILL.md and WRAPPER.md files | inbox/skills-ship.md | DONE |
| ship-run | library/research/app/SHIP_RESULT.md | inbox/ship-run.md | DONE |

## Product rules

- Ship-ready means the package selftests pass and the staged examples pass.
- It does not mean a site is published.
- library bind --live stays Keith's click.
- No invented reviews.
- Coordinator writes only BOARD_SHIP.md and inbox/coordinator-ship.md. No Python, no seats, no stage output, no make_public.py.

## What landed

A deliverable is opened only after that owner's inbox says DONE. A mention of the word DONE inside a STARTED note is not a completion. One sentence below is from the first 25 lines of that deliverable.

- how-fast (`library/research/app/HOW_FAST.md`): `lib/render.py` says the page is one file: inline CSS, inline JS, a system font stack, inline SVG icons.
- how-quality (`library/research/app/HOW_SHIP_QUALITY.md`): File scores are only what is in `stage/harbor/out/index.html` and `stage/demo/out/index.html`.
- regress (`lib/regress.py`): Builds a tiny temp project from copy files and calls the crew hands: plan_offline, then render.assemble.
- check-ship (`lib/check.py`): A relative img src must name a file beside that HTML; a page with no img passes missing_file.
- shipcheck (`lib/shipcheck.py`): Subprocess selftests only.
- public-snapshot (`make_public.py`): The public snapshot is replaced only when that check is clean.
- skills-ship (`library/seats/architect/SKILL.md`): Use when a real brief must become one new package mold and a draft bind for this site, not when the brief is empty, that mold is already live elsewhere, or the task is copy, HTML, images, the checker, SEO, or publish.
- ship-run (`library/research/app/SHIP_RESULT.md`): Shipcheck's last line on the final run: `shipcheck ok`.

## Conflicts

`inbox/shipcheck.md` records only the first `py -3.14 spidercaster.py shipcheck` exit 2, last line `lib.regress`, from when `lib/regress.py` was absent. `library/research/app/SHIP_RESULT.md` records that same miss, then a second shipcheck exit 2 whose lines were `lib.hands.selftest` and `spidercaster.py crew selftest`, and a direct `py -3.14 -m lib.hands.selftest` that printed `check_site FAIL: internal_links` (exit 1). That file says those misses do not reproduce. Final shipcheck last line is `shipcheck ok`. This coordinator did not re-run the commands and did not edit Python.

## Parent should do next

Do not run `library bind --live`. Ship-ready here means the package selftests passed and the staged harbor and demo examples passed. It does not mean a site is published. `make_public.py` staging the public snapshot is not that click.

`library/research/app/SHIP_RESULT.md` names these failing steps. They are not still open in that file, and the final shipcheck last line is `shipcheck ok`:

- First `py -3.14 spidercaster.py shipcheck` exited 2. Last line: `lib.regress`. `lib/regress.py` was not on disk.
- Second `py -3.14 spidercaster.py shipcheck` exited 2. Lines: `lib.hands.selftest` and `spidercaster.py crew selftest`.
- Direct `py -3.14 -m lib.hands.selftest` exited 1 and printed `check_site FAIL: internal_links`.

Harbor crew and demo crew both exited 0. The page-check rows in that file are yes for both `stage/harbor/out/index.html` and `stage/demo/out/index.html`. Still open in that file: none.
