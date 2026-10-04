# SpiderCaster app tree

Working tree: `V:\a\Ai\spidercaster\working`. This is the app (modules, CLI verbs, seats, molds, frames, resources). Not a site map. No crew run. No site build. No key file opened. `credentials.env` was not read. Vendor-vault photos were not walked. No secret values and no Cloudflare ids are recorded here.

`lib/*.py` was listed, then refreshed after a 90-second wait on 2026-10-01. The second list is the one below.

## lib/*.py

One line each: the export a tool or CLI verb actually calls. Def lines were read. Private helpers are omitted.

| File | After 90s | What a tool calls |
|---|---|---|
| `__init__.py` | present | Package marker only. No def. Nothing calls it. |
| `check.py` | present | `check_site(site_dir, expect_noindex=None, quiet=False, copy_text="")` returns `Report`. MCP `validate_run` calls it. Hands `check_site` and `meta_basics` call it. CLI `check` calls it. Non-empty `copy_text` can add an `ungrounded_claim` row; empty `copy_text` adds none. |
| `check_claims_selftest.py` | present | Not an MCP tool. `main()` calls `check.check_site` on a temp page and asserts one `ungrounded_claim` FAIL, none when the phrase is in the copy, and none when `copy_text` is empty. Run as `py -3.14 lib\check_claims_selftest.py`. |
| `crew.py` | present | `ROLES` is what MCP `crew_roles` returns (id, order, hands, refusal). CLI `crew run` calls `run_job`. CLI `crew selftest` calls `selftest`. `run_job` dispatches `lib.hands.HANDS`. |
| `doctor.py` | absent | Not on disk after the refresh. |
| `frames.py` | present | MCP `frame_list` calls `list_frames()`. MCP `frame_pick` calls `load_frame(frame_id)` and surfaces `FrameError`. Hand `plan_offline` calls `apply_frame` (reorder sections the copy already has; it does not invent one). |
| `imagine.py` | present | CLI `image` calls `generate(prompt, dest, provider, model, aspect_ratio, quality)` and catches `ImagineError`. Not imported by the MCP server. The receipt it returns has no key. |
| `ingest.py` | present | `load_project(project_dir)` returns `Copy` (`Block` list plus warnings). MCP `draft_offline` calls it. Hands `brief_read`, `copy_read`, `copy_gap`, and `asset_list` call it. CLI `build` uses it. |
| `ir.py` | present | MCP `catalog_read` reads `SECTION_TYPES`, `SECTION_DOCS`, `ICON_NAMES`, `TEMPLATES`. `tokens_read` uses `TEMPLATES` and `hex6`. `pagemodel_write`, `brand_write`, and `draft_offline` call `normalize_site`. |
| `library.py` | present | `Library` methods: MCP `mold_list` calls `package_manifest`. Hand `mold_pick` calls `load_mold` or `save_mold`. Hand `library_bind` and CLI `library bind` call `bind`. Hand `vault_photos` calls `frames`. Hand `uniqueness` calls `live_conflict`. Also `frame_by_id`. CLI `library` also calls `index_catalogs`, `list_molds`, `accept_snapshot`, and `selftest`. Rule breaks raise `LibraryError`. |
| `offline.py` | present | `plan_offline(copy, opts)` builds a raw IR from ingested copy only (zero tokens). MCP `draft_offline` calls it. The frontend hand `plan_offline` calls it, then `frames.apply_frame` and `ir.normalize_site`. |
| `providers.py` | present | CLI `build`, `refine`, and `models` call `resolve_chain`, `complete`, `Ledger`, and `PROVIDERS` (`gemini`, `openrouter`, `openwork`). `extract_json` parses the planner object. The MCP server does not import this module. The ledger stores counts and env-var names, not key values. |
| `render.py` | present | MCP `render_trigger` and the frontend hand `render` call `assemble(site, noindex=True)`. MCP `tokens_read` calls `build_palette` and reads names out of `CSS_TEMPLATE`. CLI `build` and `refine` call `assemble`. |
| `sandbox.py` | absent | Not on disk after the refresh. |
| `seatpack.py` | absent | Not on disk after the refresh. |
| `serve.py` | present | `serve(site_dir, port=4173, attempts=20)` returns the local preview server and the port it bound. CLI `serve` calls it. Not an MCP tool. |

`lib/hands/` is a package, not a `lib/*.py` file. `lib/hands/__init__.py` exports `HANDS`, the fifteen callables `crew.run_job` is allowed to run: `brief_read`, `frame_pick`, `mold_pick`, `library_bind`, `copy_read`, `copy_gap`, `plan_offline`, `render`, `asset_list`, `vault_photos`, `check_site`, `uniqueness`, `meta_basics`, `ticket_write`. `lib/hands/selftest.py` exports `main` only.

Before the wait, `check_claims_selftest.py` was not in `lib/`. `doctor.py`, `seatpack.py`, and `sandbox.py` were absent both times.

## CLI verbs

Source: `argparse` subparsers in `spidercaster.py`. The module docstring lists a shorter set and omits `image` and `wallets`. The parser is the verb list.

| Verb | What it does | Lib it calls |
|---|---|---|
| `init` | Scaffold a project | none of `lib/` (writes `brief.md` and `copy/`) |
| `build` | Build from a project dir, or rebuild from `site.json` with `--from` | `ingest.load_project`, `offline.plan_offline`, `ir.normalize_site`, `render.assemble`, `providers.complete` unless `--offline` or `--from` |
| `refine` | Patch one section of a built site | `ir`, `render`, `providers` (offline is theme flips only) |
| `check` | Run built-in checks | `check.check_site` |
| `serve` | Preview a built site on localhost | `serve.serve` |
| `models` | Show the provider chain; `--probe` queries live lists | `providers.resolve_chain`, `providers.PROVIDERS` |
| `wallets` | Fingerprint map of recorded Google wallets (last4 only) | no `lib/` module; this map did not open that directory |
| `sections` | List section types | `ir.SECTION_TYPES` |
| `image` | Prompt xAI or OpenRouter and save a local image | `imagine.generate` |
| `library` | Vault, molds, and the live-use ledger | `library.Library` |
| `crew` | Seven hands; does not publish | `crew.ROLES`, `crew.run_job` |

`library` subverbs: `index` (`index_catalogs`), `list` (`list_molds` plus vault frame count), `mold` (`save_mold`), `bind` (`bind`), `accept` (`accept_snapshot`), `selftest` (`library.selftest`).

`crew` subverbs: `roles` (print `ROLES`), `run` (`run_job` on one project), `selftest` (`crew.selftest` against `demo-local`).

## MCP tools

`mcp_server.py` exposes these names. Each row is the lib call, if any.

| Tool | Lib call |
|---|---|
| `catalog_read` | `ir.SECTION_TYPES`, `SECTION_DOCS`, `ICON_NAMES`, `TEMPLATES` |
| `tokens_read` | `ir.hex6`, `ir.TEMPLATES`, `render.build_palette`, `render.CSS_TEMPLATE` |
| `pagemodel_read` | none (reads `site.json`) |
| `pagemodel_write` | `ir.normalize_site` |
| `render_trigger` | `render.assemble` |
| `validate_run` | `check.check_site` |
| `review_write` | none (writes `review/*.review.json`) |
| `brand_read` | none (reads `brief.md` and copy filenames) |
| `brand_write` | `ir.normalize_site` |
| `draft_offline` | `ingest.load_project`, `offline.plan_offline`, `ir.normalize_site` |
| `wallets` | none (last4 and a short fingerprint only; files not opened for this map) |
| `crew_roles` | `crew.ROLES` |
| `mold_list` | `Library.package_manifest` |
| `frame_list` | `frames.list_frames` |
| `frame_pick` | `frames.load_frame` |

## library/seats

Seven seat ids, in crew order. Each directory has `SKILL.md` and `WRAPPER.md`. `library/seats/README.md` is the index, not a seat.

| # | id | Hands |
|---|---|---|
| 1 | `architect` | `brief_read`, `frame_pick`, `mold_pick`, `library_bind` |
| 2 | `content` | `copy_read`, `copy_gap` |
| 3 | `frontend` | `plan_offline`, `render` |
| 4 | `graphics` | `asset_list`, `vault_photos` |
| 5 | `visual` | `check_site` |
| 6 | `seo` | `uniqueness`, `meta_basics` |
| 7 | `deployer` | `ticket_write` |

No seat publishes.

## library/molds ids

Three package molds.

| id | origin | parents | template | nav |
|---|---|---|---|---|
| `warmth-authority` | scratch | none | editorial | segmented |
| `discover-grid` | mutate | `warmth-authority` | modern | top-bar |
| `clarify-mix` | mix | `warmth-authority`, `discover-grid` | bold | one-page |

## library/frames count

14 JSON files. The same 14 ids are `_PACKAGE_IDS` in `lib/frames.py`: `service-counter`, `shop-shelf`, `kitchen-board`, `proof-letter`, `local-desk`, `catalog-front`, `house-menu`, `project-index`, `visit-book`, `welcome-scroll`, `hours-stack`, `practice-intro`, `trust-lane`, `maker-shelf`.

## library/resources files

Two files.

| File | What it is |
|---|---|
| `INDEX.md` | Hand map: which hand calls which module, which path it reads, which seat owns it. |
| `ENVIRONMENT.md` | Host notes for the interpreter and which env names are set or unset. Values are not copied into this tree map. |
