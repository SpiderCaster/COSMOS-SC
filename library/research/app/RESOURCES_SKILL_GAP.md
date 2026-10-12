# Skill gap — seats vs ROLES

Resource finder. Compared `lib/crew.py` `ROLES` with every `library/seats/<id>/SKILL.md` and `WRAPPER.md`. Did not edit seats. Did not build a site. Did not run crew. Did not open credentials.

Second read is after a two-minute wait (clock `2026-10-01 14:41:16` local, then the files were read again). Other agents had edited the seat files during the wait. The second read is the record. It is aligned. No hand gap remains.

A gap would be a hand list that differs between `ROLES`, the skill, and the wrapper. Doctor and `seat` are named as read-only orientation, not as hands. `ungrounded_claim` is a checker row, not a hand.

## First read (before the wait)

Hand lists already matched `ROLES` on all seven seats. None of the fourteen files mentioned `spidercaster.py doctor` or `spidercaster.py seat`. Visual skill and visual wrapper did not mention `ungrounded_claim`. Those mentions were the only difference. They are present on the second read, and the hand lists did not change.

## Second read — hands

| seat | ROLES hands | skill hands | wrapper hands | second read |
| --- | --- | --- | --- | --- |
| architect | brief_read, frame_pick, mold_pick, library_bind | same, that order | same, that order | aligned |
| content | copy_read, copy_gap | same, that order | same, that order | aligned |
| frontend | plan_offline, render | same, that order | same, that order | aligned |
| graphics | asset_list, vault_photos | same, that order | same, that order | aligned |
| visual | check_site | check_site | check_site | aligned |
| seo | uniqueness, meta_basics | same, that order | same, that order | aligned |
| deployer | ticket_write | ticket_write | ticket_write | aligned |

Names that show up and are not hands, on both the skill and the wrapper:

- architect: `frame_list` is an MCP tool and a `library list` print. Both files say it is not a seat hand.
- graphics: `python spidercaster.py image` is outside the crew. The skill says it is not a hand. The wrapper says not to call it on every build.
- doctor and `seat` on every seat: read-only orientation, listed apart from the allowed hands.

## Doctor and seat commands

Second read: both commands are mentioned in all seven skills and all seven wrappers.

Skill form, under Start, labeled read-only orientation, not hands:

- `py -3.14 spidercaster.py doctor`
- `py -3.14 spidercaster.py seat <id>` with that seat's id (architect, content, frontend, graphics, visual, seo, deployer)

Wrapper form, under Reads, not under Allowed hands:

- `py -3.14 spidercaster.py doctor` must be ok before the seat starts
- `py -3.14 spidercaster.py seat <id>` shows this seat's hands

They are not in `ROLES["hands"]`. That is not a mismatch.

## visual and ungrounded_claim

Second read: visual mentions `ungrounded_claim`.

- Skill, `check_site` step: `check_site` passes the project's copy text into the checker. A page that says testimonial, customer review, award-winning, or a star rating that the copy files do not contain fails as `ungrounded_claim`. Do not invent copy.
- Wrapper, Fail: code `ungrounded_claim` when the page has a testimonial, customer review, award-winning, or a star rating that is not in the copy files.

The visual hand is still only `check_site`. Seo skill also names `ungrounded_claim`, as a FAIL that already stopped the crew at visual, not as an seo hand. Seo hands stay `uniqueness`, `meta_basics`.

## Verdict

Aligned. No hand gap between `ROLES`, the seven skills, and the seven wrappers on the second read.
