# Cold machine

Measured on this Windows host on 2026-10-01. Commands started in `V:\a\ai\cosmos`, then `Set-Location 'V:\a\Ai\spidercaster\working'`. No crew run. No `library bind --live`. `credentials.env` was not opened. No key file was opened. No Cloudflare id is in this list.

## Interpreter

`py -3.14 --version` printed:

```
Python 3.14.0
```

`py` is `C:\Windows\py.exe`.

Python 3.14 via `py -3.14`. Standard library only. No pip manifest. These files are absent from the working tree: `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `setup.cfg`. `spidercaster.py`, `lib/doctor.py`, `lib/seatpack.py`, and `lib/sandbox.py` import only the standard library (plus this package).

## Commands that must work with no network

```
py -3.14 spidercaster.py doctor
py -3.14 spidercaster.py seat architect
py -3.14 spidercaster.py crew selftest
```

`doctor` and `seat` were run here. `crew selftest` was not.

`doctor` is read-only. It prints one JSON object and does not take a vault argument. This run exited 0. The object had `"python": "3.14.0"`, `"vault_exists": true`, `"ok": true`, and `"errors": []`. `SPIDERCASTER_VAULT` was unset in the process. The vault path is optional. When that variable is unset or blank, `lib/doctor.py` uses its default directory `V:\streams\webdev\vendor-vault` and reports only the boolean `vault_exists`. A missing vault does not by itself make `ok` false. The command does not print the vault path, a secret, or a key.

`seat` prints one seat pack as JSON. `seat architect` exited 0. The object `id` was `architect`. An unknown seat id prints `unknown seat` and exits 2. Seat ids are `architect`, `content`, `frontend`, `graphics`, `visual`, `seo`, and `deployer`.

`crew selftest` is on `py -3.14 spidercaster.py --help`. `lib/crew.py` `selftest` uses a temporary directory and `projects\demo-local`. That function does not open a network client. This note did not run it, so there is no pass or fail quote for it. It must still succeed on a cold machine with no network.

`doctor` and `seat` do not need PHP, `wp`, MariaDB, a key, or a network.

## Not required for the static app

`Get-Command` found no `php`, no `wp`, and no `mariadb` (also no `mysql`). They are not required for this static app, and not for `doctor`, `seat`, or `crew selftest`.
