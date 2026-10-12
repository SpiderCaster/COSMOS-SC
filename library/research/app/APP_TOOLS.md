# SpiderCaster app tools

Catalog of what is in `<repo-root>` after the builders landed. Sources: `spidercaster.py` argparse, `mcp_server.py` `TOOLS`, and the `def` lines in `lib/doctor.py`, `lib/seatpack.py`, `lib/sandbox.py`, and `lib/check.py`. All four library files are present. Nothing below is inferred from a missing file. No secrets are quoted.

Publishes means a host deploy. Local files, a localhost preview, or a ledger row are not a publish. Where the code says it does not publish, the answer is no.

## CLI verbs

Top-level commands and their subcommands, from `main()` in `spidercaster.py`. There is no `sandbox` verb.

- **init** — Scaffolds a project with `brief.md` and `copy/`, and refuses a non-empty directory unless `--force` is set. Publishes: no.
- **build** — Builds a local static site from a project or from an existing `site.json`, offline or through the provider chain, and writes HTML plus `site.json` and `report.json`. Publishes: no.
- **refine** — Patches one section of a built site, with an offline path that only flips theme. Publishes: no.
- **check** — Runs `check_site` on a built site and returns nonzero when any check fails. Publishes: no.
- **serve** — Serves a built site on localhost for preview. Publishes: no.
- **models** — Prints the provider chain, and with `--probe` queries live model lists. Publishes: no.
- **wallets** — Prints a fingerprint map of recorded Google wallets, last4 only. Publishes: no.
- **sections** — Lists section types and their data fields. Publishes: no.
- **image** — Prompts xAI or OpenRouter and saves a local image file. Publishes: no (`lib/imagine.py` says neither provider path publishes).
- **library** — Parent verb for the vault, molds, and the live-use ledger. Publishes: no.
- **library index** — Registers OWP and GP catalog names into the vault and does not download photos or theme files. Publishes: no.
- **library list** — Lists package molds, package section frames, and the vault frame count. Publishes: no.
- **library mold** — Saves one scratch, mutation, or mix mold into the package library. Publishes: no.
- **library bind** — Attaches one mold to a site in the ledger, and `--live` only sets that row's live flag. Publishes: no (the method saves the ledger and does not deploy; the crew ticket names this flag as a Keith click the crew run does not perform).
- **library accept** — Records a snapshot directory that already sits in the vault. Publishes: no.
- **library selftest** — Runs the library rule checks in a temporary directory. Publishes: no.
- **crew** — Parent verb for the seven hands. The argparse help says it does not publish. Publishes: no.
- **crew roles** — Prints the seven seats, the hands each may call, and what each does not do. Publishes: no.
- **crew run** — Builds one site through the seven hands and writes `crew-ticket.json`. Publishes: no (`run_job` says it does not publish, and the ticket says this run does not deploy).
- **crew selftest** — Runs the crew against the demo-local project in a temporary directory. Publishes: no.
- **doctor** — Prints the JSON from `lib.doctor.report` (python, molds, frames, seats, and hand order). Publishes: no (the module is a read-only tree check with no site output).
- **seat** — Prints the JSON from `lib.seatpack.pack` for one seat id. Publishes: no (the module says no site output).

## MCP tool names

Names in `TOOLS` in `mcp_server.py`, in dict order. There is no sandbox tool.

- **catalog_read** — Returns the section catalog: types, data fields, icons, templates, and content rules. Publishes: no.
- **tokens_read** — Resolves theme tokens for template, dark, and accent so agents set knobs rather than literals. Publishes: no.
- **pagemodel_read** — Reads a built site's IR (`site.json`). Publishes: no.
- **pagemodel_write** — Writes the IR locally (`mode=full` for builder, `mode=patch` for content or editor). Publishes: no.
- **render_trigger** — Renders the IR to static HTML on disk with zero tokens. Publishes: no.
- **validate_run** — Runs the fleet-aligned checks and returns the rows. Publishes: no.
- **review_write** — Writes an LLM judgment and revision requests under `review/` on the site. Publishes: no.
- **brand_read** — Reads a project brief and copy names, and/or a built site's meta and theme. Publishes: no.
- **brand_write** — Patches brand knobs on a built site's `site.json` (title, description, template, dark, accent). Publishes: no.
- **draft_offline** — Returns a zero-token site IR drafted from a project's real copy, without writing the site. Publishes: no.
- **wallets** — Returns a fingerprint map of recorded Google wallets (last4 and fingerprint only). Publishes: no.
- **crew_roles** — Returns the seven seats, the hands each may call, and what each refuses. Publishes: no.
- **mold_list** — Returns package molds only, not vendor frames. Publishes: no (the result says the crew does not deploy).
- **frame_list** — Lists package section frames, not molds, vendor themes, or photos. Publishes: no.
- **frame_pick** — Loads one package section frame by id, with no vault, photos, or HTML. Publishes: no.
- **env_doctor** — Returns the read-only environment report from `lib.doctor.report`. Publishes: no (the spec says it does not publish and does not read secrets).
- **seat_pack** — Returns the read-only pack for one seat from `lib.seatpack.pack`. Publishes: no (the spec says it does not publish and does not read secrets).

## Library callables

- **attempt_dir** (`lib/sandbox.py`) — Creates `root/name` where `name` is one path segment and the directory stays inside `root`. Publishes: no (the code never publishes; it only makes the directory).
- **release** (`lib/sandbox.py`) — Writes `_released.txt` inside an attempt directory that stays inside `root`, and never deletes the attempt. Publishes: no (a marker file is not a deploy).
- **report** (`lib/doctor.py`) — Returns python version, mold ids, frame count, seat file flags, whether hands match, whether the vault path exists, and errors. Publishes: no (the module says read-only, no secrets, no key files, no site output).
- **pack** (`lib/seatpack.py`) — Returns one seat's id, label, hands, skill path, wrapper path, and `does_not`, or raises `KeyError` for an unknown seat. Publishes: no (the module says no site output).
- **check_site** (`lib/check.py`) — Scans a built site and returns a `Report` of pass, fail, warn, and skip rows, including a nonzero-fail gate the module says can block CI or a deploy. Publishes: no (it returns the report and does not deploy).

`lib/check.py` also defines a `Report` class. That class is the return type of `check_site`, not the `report` callable. `report` is only `lib.doctor.report`.
