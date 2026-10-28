# SpiderCaster environment

Measured on this Windows host on 2026-10-01. A second cold machine was not booted. Peer needs are the interpreter and files the static path imports, checked against the tree, `README.md`, and the public snapshot already on this disk. No crew run, no `library bind --live`, and no key file was opened.

`library/resources/INDEX.md` is the hand map (which hand reads which path). This file sits beside it. It does not replace INDEX.md and it does not extend that table.

## Host measured

Commands started in `V:\a\ai\cosmos`, then `Set-Location 'V:\a\Ai\spidercaster\working'`.

| Check | Result |
|---|---|
| `py -3.14 --version` | Python 3.14.0 |
| `py` | `C:\Windows\py.exe` |
| `python --version` | Python 3.13.14 |
| `python` | `C:\Users\Papa\AppData\Local\Programs\Python\Python313\python.exe` |
| `python3` | `C:\Users\Papa\AppData\Local\Microsoft\WindowsApps\python3.exe` (not executed; WindowsApps stub) |
| `requirements.txt`, `pyproject.toml`, `Pipfile` | no |
| `SPIDERCASTER_HOME` | not set (process, user, machine) |
| `SPIDERCASTER_VAULT` | not set (process, user, machine). Code default is `V:\streams\webdev\vendor-vault`, and that folder exists |
| `XAI_API_KEY` | not set |
| `OPENROUTER_API_KEY` | not set |
| `XAI_API_KEY_FILE` | not set |
| `OPENROUTER_API_KEY_FILE` | not set |
| `GEMINI_API_KEY`, `GOOGLE_API_KEY` | not set |
| `FORGE_GEMINI_KEY_FILE` | set. Path not printed |
| `OPENWORK_API_KEY`, `OPENWORK_INFERENCE_BASE_URL`, `FORGE_OPENWORK_MODEL` | not set |
| `Get-Command php` | no |
| `Get-Command wp` | no |
| `Get-Command mariadb` | no |
| `Get-Command mysql` | no |

`README.md` says Python 3.11+ and the standard library only. Both 3.14.0 (`py -3.14`) and 3.13.14 (`python`) meet that floor. There is no pip manifest in the working tree.

CLI verbs from `spidercaster.py` argparse, confirmed by `py -3.14 spidercaster.py --help`:

`init`, `build`, `refine`, `check`, `serve`, `models`, `wallets`, `sections`, `image`, `library`, `crew`.

`library` subcommands: `index`, `list`, `mold`, `bind`, `accept`, `selftest`.

`crew` subcommands: `roles`, `run`, `selftest`.

`image` is in argparse (`--prompt`, `--out`, `--provider xai|openrouter`, default provider `xai`). The module docstring at the top of `spidercaster.py` omits `image` and `wallets`; argparse is the list that ran.

## Run a local crew

The project that already has copy is `projects\demo-local` (`brief.md` plus `copy\overview.md`, `copy\commands.md`, `copy\faq.md`). Static builds default to noindex. `crew` writes `crew-ticket.json` and does not publish. Publish stays `library bind --live`, which this note does not run.

A local proof that uses a temp library and does not write package molds:

```
Set-Location 'V:\a\Ai\spidercaster\working'
py -3.14 spidercaster.py crew selftest
```

A local noindex site from the same project, without calling a provider:

```
py -3.14 spidercaster.py build projects\demo-local --offline --out sites\demo-local
py -3.14 spidercaster.py check sites\demo-local --expect-noindex
py -3.14 spidercaster.py serve sites\demo-local
```

`serve` defaults to port 4173. This session did not start it.

Seven-hand run (also not executed here). Pass `--mold` or `--scratch`. `--scratch` writes a mold under `library\molds`. Do not point it at a live site.

```
py -3.14 spidercaster.py crew run projects\demo-local --site demo-local.example --mold clarify-mix --out sites\demo-local
```

Ledger on disk: `warmth-authority` is `live` on `movelixir.com`. A crew run for any other site with that mold fails uniqueness. `discover-grid` is assigned to `demo-hero.example` with `live` false, so uniqueness does not refuse it. `clarify-mix` has no ledger row. `crew run` does not pass `--live`.

`projects\bench-harbor-tearoom` also has `brief.md` and four files under `copy\`. It is a second local project, not an elixir site.

## What is already on disk

| Path | Present |
|---|---|
| `V:\a\Ai\spidercaster\working` | yes |
| `V:\a\Ai\spidercaster\working\projects\demo-local` | yes |
| `V:\a\Ai\spidercaster\working\sites\demo-local\index.html` | yes. Path exists. `check` was not re-run |
| `V:\a\Ai\spidercaster\working\library\molds` | yes. `clarify-mix.json`, `discover-grid.json`, `warmth-authority.json` |
| `V:\a\Ai\spidercaster\working\library\frames` | yes. 14 json files: `catalog-front`, `hours-stack`, `house-menu`, `kitchen-board`, `local-desk`, `maker-shelf`, `practice-intro`, `project-index`, `proof-letter`, `service-counter`, `shop-shelf`, `trust-lane`, `visit-book`, `welcome-scroll` |
| `V:\a\Ai\spidercaster\cosmos-sc-public` | yes (directory). Contains `spidercaster.py`, `lib`, the same three molds, 14 frame json files, `projects\demo-local` (brief and copy), and `sites\demo-local\index.html` |
| `V:\streams\webdev\vendor-vault` | yes. `frames.json` yes. `README.md` yes. Photo binaries were not listed |
| `V:\streams\webdev\spidercaster_local\sites\movelixir.com.md` | yes. Brief contains provider ids — omitted |
| `V:\streams\webdev\spidercaster_local\sites\floelixir.com.md` | yes. Brief contains provider ids — omitted |
| `V:\streams\webdev\spidercaster_local\sites\recovelixir.com.md` | yes. Brief contains provider ids — omitted |
| `<your-key-file-dir>\Grok_API_Token-Key.txt` | yes. Not opened |
| `V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt` | yes. Not opened |
| `V:\A\Ai\COSMOS\live\config\xai_api_key.txt` | no |

`lib\imagine.py` reads `XAI_API_KEY`, else `XAI_API_KEY_FILE`, else `<your-key-file-dir>\Grok_API_Token-Key.txt`. OpenRouter reads `OPENROUTER_API_KEY`, else `OPENROUTER_API_KEY_FILE`, else `V:\A\Ai\COSMOS\live\config\openrouter_api_key.txt`. It does not read `xai_api_key.txt`. File contents were not checked, so this note does not claim either file is a usable key.

Image tests at `library\image-tests\2026-10-01` (filename and byte size only):

| File | Bytes |
|---|---|
| `FEEDBACK.md` | 1447 |
| `floelixir-hero.json` | 395 |
| `floelixir-hero.png` | 223763 |
| `movelixir-hero.json` | 443 |
| `movelixir-hero.png` | 252790 |
| `movelixir-mark.json` | 321 |
| `movelixir-mark.png` | 116196 |
| `recovelixir-hero.json` | 395 |
| `recovelixir-hero.png` | 185764 |

The public snapshot does not contain `library\image-tests`, `WALLETS.md`, `vendor-vault`, or `make_public.py`.

Copy packs found under `working\projects`, `spidercaster_local`, and `builds` (depth 4): only `projects\bench-harbor-tearoom\copy` and `projects\demo-local\copy`. No `floelixir`, `recovelixir`, or `movelixir` directory exists under `working\projects`. `V:\streams\webdev\builds` contains `movelixir.com` only (html, css, img, js). That tree has no `copy` directory. These sandbox folders exist under `V:\streams\webdev\environments\owp-sandbox\sites` and each has `public` and no `copy` directory: `floelixir-gp-marketer`, `floelixir-gp-restored-v2`, `floelixir-owp-restored-v2`, `floelixir-owp-simpleblog`. They are not copy packs. `floelixir-gp-marketer` and `floelixir-owp-simpleblog` also contain `site.json`, `import.log`, and `server.log`.

## What a peer install needs

- Python 3.11 or newer, standard library only. On this host use `py -3.14` or `python` (3.13.14). No pip install.
- The working tree, or the snapshot `V:\a\Ai\spidercaster\cosmos-sc-public`. The engine root is the directory that contains `spidercaster.py` (`ROOT` in that file). Set `SPIDERCASTER_HOME` only when frames should load from another tree; if that variable is unset, or the candidate `library\frames` directory is missing, frames load from the package next to the code.
- A project directory with `brief.md` and real blocks in `copy\`. `projects\demo-local` is the one shipped for a local noindex run. Empty `copy\` fails the content hand and the offline planner. Neither invents copy.
- Nothing else for `build --offline`, `check`, `serve`, or `crew` on a package mold. A missing vault `frames.json` is read as an empty frame list. Scratch and package molds have no `owp:` or `gp:` parents, so `vault_photos` passes without a snapshot.

Do not copy the three elixir briefs onto a peer. They contain provider ids. Do not copy `vendor-vault`.

## Explicitly not required for static crew

- PHP, WordPress (`wp`), MariaDB, and MySQL. `Get-Command` did not find them. They belong to a snapshot-all or sandbox stack, not to this static engine.
- A populated vendor vault, OceanWP or GeneratePress photos, and `library index`.
- `SPIDERCASTER_VAULT` on this host, because the code default folder is present. A peer running only package molds does not need that folder.
- `XAI_API_KEY`, `OPENROUTER_API_KEY`, Gemini env vars, or OpenWork env vars. Those serve `image` and the optional AI `build` / `refine` path. Offline crew and `build --offline` do not call them.
- `V:\A\Ai\COSMOS\live\config\xai_api_key.txt`. Image xAI does not look there.
- The hero files under `library\image-tests`. They are not wired into `projects\demo-local`.
- `library bind --live`, DNS, or the Cloudflare notes inside the elixir briefs.
