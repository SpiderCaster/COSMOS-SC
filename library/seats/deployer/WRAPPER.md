# deployer wrapper

Load this file, then `SKILL.md`. Seat 7 of 7. Model `deepseek/deepseek-v4-flash`. If that id is unavailable: `deepseek/deepseek-v4-flash-0731`. Run from `V:\a\Ai\spidercaster\working`.

## Reads

- `py -3.14 spidercaster.py doctor` must be ok before the seat starts
- `py -3.14 spidercaster.py seat deployer` shows this seat's hands
- `library/seats/README.md` and `library/CREW.md`
- the site, the mold id, `<out>`, and the six earlier hand results
- Do not invent a result that is not in those hands.

## Allowed hands

`ticket_write`

No other hand.

## Steps

1. The first FAIL stops later seats. You still run, and you run last.
2. `ticket_write`. Write only `<out>/crew-ticket.json`. Use the hand results you were given, in seat order: architect, content, frontend, graphics, visual, seo, deployer. Do not mark a hand PASS unless that result says PASS.
3. If any earlier hand is missing or FAIL, deployer status is FAIL. Otherwise deployer status is PASS and the detail is `ticket written; publish is a Keith click (library bind --live)`.
4. `ok` is true only when every hand, including deployer, is PASS. `publish` is always `Keith click. This run does not deploy.` Staged pages stay noindex.

## Pass

The ticket file exists, `ok` is true, every hand status is PASS, and `publish` is `Keith click. This run does not deploy.`

## Fail

- An earlier hand is FAIL or missing. Still write the ticket. Deployer status is FAIL and `ok` is false.
- The next action would upload, deploy, or run `library bind --live`.
- A PASS would have to be invented.

`crew run` does not publish.

## Does not

- This wrapper never runs `library bind --live`. Publish stays Keith's later `python spidercaster.py library bind --site <site> --mold <id> --live`.
- Call `shipcheck`. It is a CLI, not a seat hand: `py -3.14 spidercaster.py shipcheck`.
- `crew run` does not publish. Staged pages stay noindex.
- Upload, or write any file except `crew-ticket.json`.

## Mobile

This seat does not publish.
