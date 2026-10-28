# Environment now

Measured 2026-10-01 for the SpiderCaster app environment. Not a site build. No crew run. No `library bind --live`. No key file was opened. Values of env vars were not printed.

Commands started with `Set-Location 'V:\a\Ai\spidercaster\working'`. The shell cwd resets to `V:\a\ai\cosmos` after each command.

## Docs read

| Path | Present | Read |
|---|---|---|
| `library\resources\ENVIRONMENT.md` | yes | yes |
| `library\resources\ENVIRONMENT_GAPS.md` | no | no such file |
| `library\research\ENVIRONMENT_GAPS.md` | yes | yes |

`ENVIRONMENT.md` is the earlier host note (Python 3.14.0, stdlib only, static crew does not need PHP/WordPress/MariaDB/MySQL or provider keys). `ENVIRONMENT_GAPS.md` is not beside it. The copy under `library\research` is about missing elixir copy packs. It says a local noindex run of `projects\demo-local` is not blocked. This note does not reopen that site gap.

## Pass 1 — 2026-10-01 14:36:49

`py -3.14 --version` → `Python 3.14.0`

| Path | Exists |
|---|---|
| `lib\doctor.py` | no |
| `lib\seatpack.py` | no |
| `lib\sandbox.py` | no |
| `library\resources\SANDBOX.md` | no |
| `library\resources\REQUIREMENTS.md` | no |
| `spidercaster.py` | yes |

Doctor was not run. `lib\doctor.py` was absent. At this instant `spidercaster.py` had no `doctor` verb.

## Wait

`Start-Sleep -Seconds 120`. That command finished at 2026-10-01 14:40:02.

## Pass 2 — 2026-10-01 14:41:03

`py -3.14 --version` → `Python 3.14.0`

| Path | Exists | Bytes |
|---|---|---|
| `lib\doctor.py` | yes | 2606 |
| `lib\seatpack.py` | yes | 1128 |
| `lib\sandbox.py` | yes | 2857 |
| `library\resources\SANDBOX.md` | no | |
| `library\resources\REQUIREMENTS.md` | no | |
| `spidercaster.py` | yes | |

The three modules were absent on pass 1 and present on pass 2. The two markdown files were absent on both passes. Byte sizes are from `Get-Item` after pass 2. File bodies were not copied.

`spidercaster.py` on pass 2 imports `lib.doctor` and `lib.seatpack` and registers verb `doctor`.

## Doctor

Run because `lib\doctor.py` and the CLI verb both existed. No `--live`. No crew.

```
py -3.14 spidercaster.py doctor
```

When: 2026-10-01 14:41:16. Exit code: 0.

```
{"python":"3.14.0","root":"V:\\A\\Ai\\spidercaster\\working","molds":["clarify-mix","discover-grid","warmth-authority"],"frames":14,"seats":[{"id":"architect","skill":true,"wrapper":true},{"id":"content","skill":true,"wrapper":true},{"id":"frontend","skill":true,"wrapper":true},{"id":"graphics","skill":true,"wrapper":true},{"id":"visual","skill":true,"wrapper":true},{"id":"seo","skill":true,"wrapper":true},{"id":"deployer","skill":true,"wrapper":true}],"hands_match":true,"vault_exists":true,"ok":true,"errors":[]}
```

`ok` is true and `errors` is empty, so a present doctor module is not a gap.

## Keys — exist yes/no only

Same result on both passes. Not opened. Not printed.

| Name | Pass 1 and pass 2 |
|---|---|
| `XAI_API_KEY` | unset (process, user, machine) |
| `XAI_API_KEY_FILE` | unset (process, user, machine) |
| `V:\A\Ai\COSMOS\live\config\xai_api_key.txt` | no |
| `OPENROUTER_API_KEY` | unset (process, user, machine) |
| `OPENROUTER_API_KEY_FILE` | unset (process, user, machine) |
| `<your-key-file-dir>\Grok_API_Token-Key.txt` | yes |
| `V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt` | yes |

Existence is not a claim that either file is a usable key. `ENVIRONMENT.md` already says image xAI reads the env vars, then the local-secrets Grok token path, and OpenRouter reads the env vars, then the COSMOS openrouter key path. Offline crew does not need them. This pass did not call `image`.

`SPIDERCASTER_HOME` and `SPIDERCASTER_VAULT` were unset on pass 1 (process, user, machine). Doctor on pass 2 reported `vault_exists` true, which matches the code default vault folder already noted in `ENVIRONMENT.md`.

## Gaps

Still absent after the second measure:

1. `library\resources\SANDBOX.md` — absent both passes. `lib\sandbox.py` is on disk (2857 bytes) with no matching resource note.
2. `library\resources\REQUIREMENTS.md` — absent both passes. There is no cold-machine requirements file under `library\resources`. `ENVIRONMENT.md` remains the only written host note there.

Not gaps:

- `lib\doctor.py`, `lib\seatpack.py`, and `lib\sandbox.py` landed between the two passes.
- `py -3.14 spidercaster.py doctor` exited 0 with `"ok":true`.
- Python 3.14.0 is on `py -3.14` on both passes.
