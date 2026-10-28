STARTED

Offline seat tool filter. Not a site build. No publish. No crew. No agent spawn.

`lib/seat_tools.py` `seat_tools(parent, tools, disallowed)`.

Started: 2026-10-01

DONE

`seat_tools(parent, tools, disallowed)` returns `ok`, `error`, `granted`, `unresolved`. Null `tools` and null `disallowed` grant `parent` in parent order. A `disallowed` entry strips a trailing `(...)` suffix and removes that tool name. `tools` then keeps names still in the pool, in `tools` order. Names not left in the pool, including a name listed in both, go to `unresolved` and are not granted. A non-empty `tools` list that grants nothing returns `ok` false, `error` `zero_tools`, `granted` `[]`. A non-string list item returns `ok` false, `error` `bad_list`. No spawn, no publish, no file write.

From `V:\a\Ai\spidercaster\working`:

- `py -3.14 -m lib.seat_tools` exit 0: `seat_tools selftest ok`

Done: 2026-10-01
