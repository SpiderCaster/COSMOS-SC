# APP_STATUS2

Code-check only. No site. No publish. No `--live`. No image API. No secrets. Working directory: `<repo-root>`.

First pass ran after a 180 second wait. `lib.skill_read`, `lib.hook_match`, `lib.layer_read`, and `lib.session_mark` were missing. Those four commands were run once more after 60 seconds. The retry is the result for those four. The other ten passed on the first pass. No owner file was edited. `lib/skill_read.py` and `inbox/skill_read.md` were still absent at 2026-10-01 14:53:21 local, so this is not a one-line bug in a finished module.

## Commands

`py -3.14 -m lib.skill_read` (first pass and one retry, exit 1)

```
C:\Users\Papa\AppData\Local\Programs\Python\Python314\python.exe: No module named lib.skill_read
```

`py -3.14 -m lib.hook_match` (retry, exit 0)

```
hook_match selftest ok
```

`py -3.14 -m lib.perm_rule` (exit 0)

```
perm_rule selftest ok
```

`py -3.14 -m lib.tool_search_local` (exit 0)

```
tool_search selftest ok
```

`py -3.14 -m lib.seat_tools` (exit 0)

```
seat_tools selftest ok
```

`py -3.14 -m lib.seat_gate` (exit 0)

```
seat_gate selftest ok
```

`py -3.14 -m lib.layer_read` (retry, exit 0)

```
layer_read selftest ok
```

`py -3.14 -m lib.code_refuse` (exit 0)

```
code_refuse selftest ok
```

`py -3.14 -m lib.mold_panel` (exit 0)

```
mold_panel selftest ok
```

`py -3.14 -m lib.session_mark` (retry, exit 0)

```
session_mark selftest ok
```

`py -3.14 -m lib.hands.selftest` (exit 0)

```
hands selftest ok
```

`py -3.14 spidercaster.py crew selftest` (exit 0)

```
crew selftest ok
```

`py -3.14 lib\check_claims_selftest.py` (exit 0)

```
claims selftest ok
```

`py -3.14 spidercaster.py doctor` (exit 0)

```
{"python":"3.14.0","root":"<repo-root>","molds":["clarify-mix","discover-grid","warmth-authority"],"frames":14,"seats":[{"id":"architect","skill":true,"wrapper":true},{"id":"content","skill":true,"wrapper":true},{"id":"frontend","skill":true,"wrapper":true},{"id":"graphics","skill":true,"wrapper":true},{"id":"visual","skill":true,"wrapper":true},{"id":"seo","skill":true,"wrapper":true},{"id":"deployer","skill":true,"wrapper":true}],"hands_match":true,"vault_exists":true,"ok":true,"errors":[]}
```

## Fixes

none

## Still open

`lib/skill_read.py` is not on disk. `py -3.14 -m lib.skill_read` failed on the first pass and on the one retry with `No module named lib.skill_read`. Owner inbox `inbox/skill_read.md` was not present and did not say DONE.
