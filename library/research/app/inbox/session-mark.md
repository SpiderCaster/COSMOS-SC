# session-mark

STATUS: STARTED

Building lib/session_mark.py. Local append to out/session.jsonl only. No site. No publish. No live bind. No crew-ticket.json. No edit to lib/hands.

Started: 2026-10-01

STATUS: DONE

`lib/session_mark.py` `session_mark(out, root, seat, hand, status, detail, restore=None)` returns `ok`, `error`, `path`, `seq`, `seat`, `hand`, `status`. Appends one JSON object as a line to `out/session.jsonl`. Does not rewrite earlier lines. `seq` is the new line count. Does not create `out` (`error` is `missing`). Does not delete. Does not restore. Does not write `crew-ticket.json`. Does not bind live. Does not edit `lib/hands`.

Fail closed: seat not one of the seven; hand not in that seat's `lib.crew.ROLES` hands; status not `PASS`, `FAIL`, or `SKIP`; detail contains `http://` or `https://`; `out` missing, escapes root, or contains `..`; `restore` is not None.

From `V:\a\Ai\spidercaster\working`:

`py -3.14 -m lib.session_mark` exit 0:

```
session_mark selftest ok
```

Done: 2026-10-01
