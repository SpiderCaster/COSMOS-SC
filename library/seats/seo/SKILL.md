---
name: spidercaster-seo
description: >-
  Use when this site's one draft mold must be confirmed unique and the meta and sample checks must already be clean, not when those checks failed, the mold or frame is already live, or the task is publish.
---

# spidercaster-seo

## When not to use

- Visual reported a FAIL on `meta_basics`, `no_sample`, `no_soft_placeholders`, or `ungrounded_claim`.
- The mold or vendor frame is already live on another site.
- The task is to index the site or to publish.

## Start

1. Read `library/seats/README.md` and `library/CREW.md`.
2. Run commands from `V:\a\Ai\spidercaster\working`.
3. Call only `uniqueness`, then `meta_basics`.
4. Read-only orientation, not hands:

   `py -3.14 spidercaster.py doctor`

   `py -3.14 spidercaster.py seat seo`

## Steps

1. **uniqueness.** Read `library/ledger.json`. This site has one assignment. Its `live` value is false. No other row has the same `mold`, or the same non-null `vendor_frame`, with `"live": true`. If one does, stop. Do not bind.
2. **meta_basics.** Read the visual seat's checker rows. If that run is missing, run `python spidercaster.py check <out> --expect-noindex`. Staged pages stay noindex. Stop if `meta_basics` or `no_sample` is `FAIL`. A `no_soft_placeholders` or `ungrounded_claim` FAIL already stopped the crew at visual. Do not reopen it. Do not edit titles or body text, and do not invent copy.

## Exit

Return the mold id, that the bind is still a draft, and the `meta_basics` and `no_sample` statuses. Stop.

## Do not

- Reuse a mold or vendor frame that is already live.
- Pass `--live` or `--indexable`. Staged pages stay noindex. `crew run` does not publish.
- Call `shipcheck`. It is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.

## Risk tier

Tier 0 read-only. Publish is not this seat.

## Mobile

Staged pages stay noindex. One h1. The description is a full sentence.
