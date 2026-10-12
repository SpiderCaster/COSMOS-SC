# APP_STATUS

Code-check only. No site. No `--live`. No `crew run`. Working directory: `<repo-root>`.

First pass ran before `lib.doctor`, `lib.seatpack`, `lib.sandbox`, and the `doctor` / `seat` CLI were on disk. Those five commands were run once more after 60 seconds. The retry is the result below. `check_claims_selftest`, hands selftest, and crew selftest passed on the first pass. Hands and crew were confirmed again after `inbox/hands.md` said DONE.

## Commands

`py -3.14 -m lib.doctor` (retry, exit 0)

```
doctor selftest ok
```

`py -3.14 -m lib.seatpack` (retry, exit 0)

```
seatpack selftest ok
```

`py -3.14 -m lib.sandbox` (retry, exit 0)

```
sandbox selftest ok
```

`py -3.14 lib\check_claims_selftest.py` (exit 0)

```
claims selftest ok
```

`py -3.14 -c "import mcp_server; assert 'env_doctor' in mcp_server.TOOLS; print('mcp tools ok')"` (retry, exit 0)

```
mcp tools ok
```

`py -3.14 spidercaster.py doctor` (retry, exit 0)

```
{"python":"3.14.0","root":"<repo-root>","molds":["clarify-mix","discover-grid","warmth-authority"],"frames":14,"seats":[{"id":"architect","skill":true,"wrapper":true},{"id":"content","skill":true,"wrapper":true},{"id":"frontend","skill":true,"wrapper":true},{"id":"graphics","skill":true,"wrapper":true},{"id":"visual","skill":true,"wrapper":true},{"id":"seo","skill":true,"wrapper":true},{"id":"deployer","skill":true,"wrapper":true}],"hands_match":true,"vault_exists":true,"ok":true,"errors":[]}
```

`py -3.14 spidercaster.py seat visual` (retry, exit 0)

```
{"id":"visual","label":"Visual critic","hands":["check_site"],"skill":"<repo-root>\\library\\seats\\visual\\SKILL.md","wrapper":"<repo-root>\\library\\seats\\visual\\WRAPPER.md","does_not":"approve its own design; the checker is the gate"}
```

`py -3.14 -m lib.hands.selftest` (exit 0, confirmed again after hands DONE)

```
hands selftest ok
```

`py -3.14 spidercaster.py crew selftest` (exit 0, confirmed again after hands DONE)

```
crew selftest ok
```

## Fixes

none

## Still open

none
