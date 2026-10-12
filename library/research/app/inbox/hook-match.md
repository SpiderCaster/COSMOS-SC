# hook-match

STATUS: DONE

Offline `lib/hook_match.py` only. Not a site. No publish. The function does not start a command and does not write a file.

`hook_match(event, tool_name, hooks)` returns `ok`, `error`, `matched`, `ran`. `ran` is always false. An empty or missing matcher matches every `tool_name`. Any other matcher splits on `|` or comma, strips tokens, and compares case-sensitively. `matched` is `{group, type}` rows; `group` is the matcher-group index. Tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`) use `tool_name`. Every other known event ignores `tool_name` and matches every group. Unknown event: `unknown_event`. Wrong shape: `bad_hooks`. Both failures return `matched` `[]` and `ran` false.

From `<repo-root>`:

- `py -3.14 -m lib.hook_match` exit 0: `hook_match selftest ok`

The selftest asserted matcher `Read|Grep` matches `Read`, the command string was not started, and event `NoSuch` fails with `unknown_event`.

Started: 2026-10-01
Done: 2026-10-01 14:52:04
