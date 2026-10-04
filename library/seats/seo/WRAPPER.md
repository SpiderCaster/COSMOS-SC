# seo wrapper

Load this file, then `SKILL.md`. Seat 6 of 7. Model `deepseek/deepseek-v4-flash`. If that id is unavailable: `deepseek/deepseek-v4-flash-0731`. Run from `V:\a\Ai\spidercaster\working`.

## Reads

- `py -3.14 spidercaster.py doctor` must be ok before the seat starts
- `py -3.14 spidercaster.py seat seo` shows this seat's hands
- `library/seats/README.md` and `library/CREW.md`
- `library/ledger.json`
- the visual checker rows for `meta_basics` and `no_sample`

## Allowed hands

`uniqueness`, `meta_basics`

In that order. No other hand.

## Steps

1. `uniqueness`. This site has one mold. Stop if that mold is already `"live": true` on another site. Do not bind.
2. `meta_basics`. Read the checker rows for this `<out>` with noindex on. Staged pages stay noindex. Stop if `meta_basics` or `no_sample` is `FAIL`. Do not edit titles or body text to clear them. A `no_soft_placeholders` FAIL already stopped the crew at visual. Do not reopen it here.

## Pass

- `one mold on this site; a second live use will be refused`
- the `meta_basics` detail, or `meta basics present`
- the ledger row for this site is still a draft

## Fail

- `mold <id> is already live on <other>`
- `meta or sample checks failed`
- `no mold` or `out is required`
- A FAIL here still lets deployer write `crew-ticket.json`. `crew run` does not publish.

## Does not

- Reuse a mold or vendor frame that is already live.
- Run `library bind --live` or pass `--indexable`. Staged pages stay noindex.
- Call `shipcheck`. It is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.

## Mobile

Staged pages stay noindex. One h1. The description is a full sentence.
