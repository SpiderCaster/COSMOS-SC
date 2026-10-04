# perm-rule

STATUS: DONE

`lib/perm_rule.py` `perm_rule(tool, arg, allow, deny)` returns `ok`, `error`, `decision`, and `matched_rule`. A rule is `ToolName` or `ToolName(specifier)`. One trailing `*` is a prefix match. Any other `*` is `bad_rule`. Deny wins. No match is `ask` with `matched_rule` null. Failures `empty_tool` and `bad_rule` set `decision` to `deny`. The function does not start a shell and does not write a file.

Selftest (`py -3.14 -m lib.perm_rule`):

```
perm_rule selftest ok
```

Done: 2026-10-01 14:50:47
