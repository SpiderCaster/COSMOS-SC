STARTED

`lib/seat_gate.py` `seat_gate(caller, seat, hand)`. Not a site build. No publish. No crew edit. Does not call the hand. Does not read secrets.

Started: 2026-10-01

DONE

`seat_gate` returns `seat`, `hand`, `allowed`, `ok`, `error`. Allowed only when `caller` equals `seat` and `hand` is on that seat's `ROLES` list. Unknown seat, a different caller, and an unknown hand (including `frame_list`) are `allowed` false and `ok` false. Architect hands stay `brief_read`, `frame_pick`, `mold_pick`, `library_bind`. `lib/crew.py` was not edited.

From `<repo-root>`:

`py -3.14 -m lib.seat_gate` exit 0:

```
seat_gate selftest ok
```

Done: 2026-10-01
