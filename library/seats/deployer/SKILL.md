---
name: spidercaster-deployer
description: >-
  Use when the seven hand results must be written to crew-ticket.json and nothing uploaded, not when a hand result is missing and would have to be invented or the task is library bind --live.
---

# spidercaster-deployer

## When not to use

- The task is to upload, deploy, or mark the site live.
- Prior hand results were not supplied and are not on disk to read.
- The task is to rebuild, rewrite copy, or re-pick a mold.

## Start

1. Read `library/seats/README.md` and `library/CREW.md`.
2. You need the site, the mold id, the out dir, and the six earlier hand results.
3. Call only `ticket_write`.
4. Read-only orientation, not hands:

   `py -3.14 spidercaster.py doctor`

   `py -3.14 spidercaster.py seat deployer`

## Steps

1. **ticket_write.** Write only `<out>/crew-ticket.json`. Use the hand results you were given, in seat order: architect, content, frontend, graphics, visual, seo, then deployer. Do not mark a hand PASS unless that result says PASS. If any earlier hand is missing or FAIL, deployer status is FAIL. Otherwise deployer status is PASS and its detail is `ticket written; publish is a Keith click (library bind --live)`.

   `ok` is true only when every hand, including deployer, is PASS. `publish` is always `Keith click. This run does not deploy.` Staged pages stay noindex. `crew run` does not publish.

## Exit

Return the ticket path and the `ok` value. Stop. Do not run a bind.

## Do not

- Publish. That is Keith's `library bind --live`, not this seat.
- Call `shipcheck`. It is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.
- Upload, or write any file except `crew-ticket.json`. Staged pages stay noindex.

## Risk tier

Tier 0 one local JSON file. Live bind is outside this seat.

## Mobile

This seat does not publish.
