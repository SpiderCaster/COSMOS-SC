# SpiderCaster local resources

Measured 2026-10-01 13:55:29 from disk. Exists flags below are from directory listings and `Test-Path`. File bodies were not copied. `credentials.env` was not opened. Site markdown under `spidercaster_local\sites` was not opened. Provider, account, zone, and token identifiers are omitted.

## Scope

movelixir.com is the only elixir site already built. flo and reco are briefs until a copy pack exists. A crew must not invent copy. The safe project for a proof run is `projects\demo-local`. Live rebuild of movelixir is out of scope. Publish is out of scope.

Crew project path: `V:\a\Ai\spidercaster\working\projects\demo-local`

## Working tree

`V:\a\Ai\spidercaster\working` — exists: yes. Copy-driven static site engine (CLI, library, projects, built output).

Top-level names only:

| Name | Exists | What it is |
|---|---|---|
| `.git` | yes | Git metadata for this working tree. |
| `.gitignore` | yes | Ignore rules for the tree. |
| `__pycache__` | yes | Python bytecode cache. |
| `antigravity_seat.py` | yes | Seats an Antigravity SDK agent on `mcp_server.py` with role tool policies. |
| `forge.py` | yes | Compat shim; forwards to `spidercaster.py`. |
| `lib` | yes | Engine package: hands, crew, frames, render, offline plan, library, checks, imagine. |
| `library` | yes | Molds, frames, seats, research, resources, image tests, crew and seed notes. |
| `make_public.py` | yes | Builds a sanitized public copy of the tree. |
| `mcp` | yes | Directory; contains `HARNESS_CONFIGS.md` (not opened). |
| `mcp_server.py` | yes | Stdio MCP server over the engine. |
| `plugin` | yes | Directory; contains `cosmos.json`, the plugin contract. |
| `projects` | yes | Source projects. Children measured: `demo-local`, `bench-harbor-tearoom`. |
| `README.md` | yes | Engine overview: real copy in, static site out; publish stays a human click. |
| `sites` | yes | Built output. Children measured: `demo-local`, `demo-local-ai`, `bench-harbor-tearoom`. |
| `SKILL.md` | yes | Skill card: build from real copy; do not invent content; not for live deploys. |
| `spidercaster.py` | yes | CLI (`init`, `build`, `refine`, `check`, and related commands). |
| `WALLETS.md` | yes | Wallet metadata map. Header says no key values are stored in the file. Not a copy source. |

`projects\bench-harbor-tearoom` also has `brief.md` plus `copy\` (`overview.md`, `menu.md`, `hours.md`, `contact.md`). It is not the proof project.

## projects\demo-local

`V:\a\Ai\spidercaster\working\projects\demo-local` — exists: yes. Local noindex test project about the engine itself.

| Path | Exists | What it is |
|---|---|---|
| `brief.md` | yes | Brief for a local engine test. Audience is Keith and the free-model seats. Tone is plain. Stays noindex. |
| `copy\overview.md` | yes | Copy: what SpiderCaster is and that AI is optional. |
| `copy\commands.md` | yes | Copy: command facts (`init`, offline `build`). |
| `copy\faq.md` | yes | Copy: questions on zero-token offline build versus an AI build. |

No other files were in that project listing.

Already-built local output (not the crew input): `V:\a\Ai\spidercaster\working\sites\demo-local` contains `index.html`, `site.json`, `site.json.bak`, `report.json`. HTML was not read.

## library\molds

Directory exists: yes. Three package JSON files. Id is the `id` field.

| File | Exists | Id | What it is |
|---|---|---|---|
| `library\molds\warmth-authority.json` | yes | `warmth-authority` | `origin=scratch`, `package=true`. Serif editorial mold. Note says first live use is movelixir.com. Not an OceanWP or GeneratePress demo. |
| `library\molds\discover-grid.json` | yes | `discover-grid` | `origin=mutate`, `package=true`. Mutation of warmth-authority. Card-grid discover pages. Not an OceanWP or GeneratePress demo. |
| `library\molds\clarify-mix.json` | yes | `clarify-mix` | `origin=mix`, `package=true`. Mix of warmth-authority and discover-grid. FAQ-forward. Not an OceanWP or GeneratePress frame. |

## library\frames

Directory exists: yes. Fourteen package frame JSON files (`schema` key present on each). Id is the `id` field. Section order is the one-line shape; frames were not dumped.

| File | Exists | Id | What it is |
|---|---|---|---|
| `catalog-front.json` | yes | `catalog-front` | Shop homepage: hero, features, gallery, cta. |
| `hours-stack.json` | yes | `hours-stack` | Food page: hero, menu, features, faq, contact. |
| `house-menu.json` | yes | `house-menu` | Cafe or restaurant: hero, menu, gallery, testimonials, about, faq, contact. |
| `kitchen-board.json` | yes | `kitchen-board` | Food or drink menu from copy only: hero, about, menu, gallery, faq, contact. |
| `local-desk.json` | yes | `local-desk` | Local service: hero, features, stats, about, testimonials, faq, contact. |
| `maker-shelf.json` | yes | `maker-shelf` | Maker page: hero, gallery, logocloud, about, cta. |
| `practice-intro.json` | yes | `practice-intro` | Practice intro: hero, about, team, features, testimonials, contact. |
| `project-index.json` | yes | `project-index` | Portfolio: hero, gallery, about, steps, cta. |
| `proof-letter.json` | yes | `proof-letter` | Long quiet page: hero, about, steps, testimonials, faq, contact. |
| `service-counter.json` | yes | `service-counter` | Local service, one offer: hero, features, steps, faq, contact. |
| `shop-shelf.json` | yes | `shop-shelf` | Small catalog, no remote product feed: hero, logocloud, features, pricing, testimonials, cta. |
| `trust-lane.json` | yes | `trust-lane` | Quote-led service: hero, stats, steps, pricing, faq, contact. |
| `visit-book.json` | yes | `visit-book` | Booking practice: hero, features, steps, pricing, testimonials, faq, cta. |
| `welcome-scroll.json` | yes | `welcome-scroll` | Single scrolling page: hero, about, features, gallery, faq, contact. |

## library\seats

`library\seats` exists: yes. Seven seat directories. Both files exist in every seat.

| Seat | SKILL.md | WRAPPER.md | What it is |
|---|---|---|---|
| architect | yes | yes | Brief to one package mold and a draft bind. Stops if the brief is empty or the mold is already live elsewhere. |
| content | yes | yes | Reads real `copy\` blocks and names gaps. Does not invent facts. |
| frontend | yes | yes | Offline plan and noindex HTML from real copy blocks. |
| graphics | yes | yes | Local image files only. Remote asset URLs are rejected. Vendor photos stay in the vault. |
| visual | yes | yes | Machine-check with noindex. A FAIL stops the crew. |
| seo | yes | yes | Confirms the draft mold is unique and meta or sample checks are already clean. |
| deployer | yes | yes | Writes `crew-ticket.json`. Does not upload. `library bind --live` is out of scope. |

`library\CREW.md` exists and states the same order: architect, content, frontend, graphics, visual, seo, deployer. No seat publishes.

## library\image-tests\2026-10-01

Directory exists: yes. Sizes are file lengths in bytes. These are Grok Imagine tests (`grok-imagine-image-2.0`), not a publish. Receipt JSON keys measured: `provider`, `model`, `prompt`, `file`, `bytes`, `aspect_ratio`, `quality`. No key field and no provider URL field. Prompts were not copied. `FEEDBACK.md` says the page favicon stays the built SVG.

| File | Exists | Bytes | What it is |
|---|---|---|---|
| `FEEDBACK.md` | yes | 1447 | Notes from the 2026-10-01 test. Names `floelixir-hero.png` as the keeper. Says the PNGs are not a publish. |
| `floelixir-hero.png` | yes | 223763 | Test hero. Feedback: cup, steam, notebook, morning window. Keeper. Not applied to a page. |
| `floelixir-hero.json` | yes | 395 | Receipt for that PNG. |
| `movelixir-hero.png` | yes | 252790 | Test hero. Feedback: walker is centered. Not a live rebuild. |
| `movelixir-hero.json` | yes | 443 | Receipt for that PNG. |
| `movelixir-mark.png` | yes | 116196 | Mark study. Feedback: one cream M on plum. Not the live favicon. |
| `movelixir-mark.json` | yes | 321 | Receipt for that PNG. |
| `recovelixir-hero.png` | yes | 185764 | Test hero. Feedback: a room and a dim face; not applied. |
| `recovelixir-hero.json` | yes | 395 | Receipt for that PNG. |

A filename search under the working tree for floelixir or recovelixir found only these four image-test files. No flo or reco project directory.

## V:\streams\webdev

| Path | Exists | What it is |
|---|---|---|
| `V:\streams\webdev\START_HERE.md` | yes | Web-fleet handover index. 48554 bytes, last write 2026-09-28 19:45:33. Head only was read. Account and zone identifiers omitted. Not a SpiderCaster copy pack. |
| `V:\streams\webdev\spidercaster_local\sites\floelixir.com.md` | yes | 5109 bytes. Name only. Not opened. |
| `V:\streams\webdev\spidercaster_local\sites\movelixir.com.md` | yes | 2680 bytes. Name only. Not opened. |
| `V:\streams\webdev\spidercaster_local\sites\recovelixir.com.md` | yes | 5754 bytes. Name only. Not opened. |
| `V:\streams\webdev\builds\movelixir.com` | yes | The only child of `builds`. Static HTML already on disk. Not read. |
| `V:\streams\webdev\builds\floelixir.com` | no | No build directory. |
| `V:\streams\webdev\builds\recovelixir.com` | no | No build directory. |
| `V:\streams\webdev\vendor-vault` | yes | Private vault. Top-level listing only: `README.md` (247 bytes) and `frames.json` (23525 bytes). No subdirectories at the vault root. Photo binaries were not recursed and none were at the root. README says OceanWP and GeneratePress frames and photos are private and not part of the package. `frames.json` was not opened. |

movelixir.com HTML filenames only (not read): `about.html`, `athletes.html`, `contact.html`, `index.html`, `novices.html`, `nutrition.html`, `recovery.html`, `research.html`, `thesis.html`.

## Usable now

Paths a builder can use today for a proof run:

- `V:\a\Ai\spidercaster\working` — engine (`spidercaster.py`, `lib`, `library`).
- `V:\a\Ai\spidercaster\working\projects\demo-local` — the only project a crew run should use. `brief.md` exists. Copy exists: `copy\overview.md`, `copy\commands.md`, `copy\faq.md`.
- `V:\a\Ai\spidercaster\working\library\molds\` — `warmth-authority`, `discover-grid`, `clarify-mix`.
- `V:\a\Ai\spidercaster\working\library\frames\` — the fourteen frame ids listed above.
- `V:\a\Ai\spidercaster\working\library\seats\` — all seven seats have `SKILL.md` and `WRAPPER.md`.
- `V:\a\Ai\spidercaster\working\sites\demo-local` — existing local output for that project. Not a new publish.
- `V:\a\Ai\spidercaster\working\library\image-tests\2026-10-01\*.png` — local test images only. Not published and not a copy pack.

Do not use for this proof: live rebuild of `V:\streams\webdev\builds\movelixir.com`, anything under `vendor-vault`, and publish (`library bind --live`).

## Missing for flo and reco

flo and reco have briefs and hero image tests. They do not have a copy pack, and they do not have a build.

Absent:

- No project directory for either site under `V:\a\Ai\spidercaster\working\projects` (no `brief.md`, no `copy\`).
- No `V:\streams\webdev\builds\floelixir.com`.
- No `V:\streams\webdev\builds\recovelixir.com`.

Present but not enough to build:

- Unopened briefs: `V:\streams\webdev\spidercaster_local\sites\floelixir.com.md` and `recovelixir.com.md`.
- Unapplied test heroes: `library\image-tests\2026-10-01\floelixir-hero.png` and `recovelixir-hero.png`, plus their receipt JSON.

A crew must not invent the missing copy. movelixir.com already has HTML under `builds\movelixir.com`; rebuilding or publishing it is out of scope.
