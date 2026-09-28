# Siteforge - a website building engine on free and nearly-free tokens

Copy-driven static site engine for the WebDev fleet. Real copy in, self-contained
static site out. The structure, layout and assembly are deterministic code, so
the bulk of every build costs **zero tokens**. AI is optional and rides the free
chain; paid models join only on an explicit flag.

Built to the WebDev package rails: no invented content, noindex by default, no
hotlinking, secrets by env var NAME only, Python 3.11+ stdlib only (no pip deps),
and a token ledger on every run.

## Install

None. Python 3.11+ with stdlib only.

```
cd siteforge
python forge.py --help
```

## Token economics

| path | tokens | what happens |
|---|---|---|
| `build --offline` | 0 | copy files mapped to sections by rules; renderer assembles |
| `build --from site.json` | 0 | re-assemble after hand edits |
| `refine ... --offline` | 0 | theme flips (template/dark/light/#hex) |
| `build` (AI) | 1-2 calls | one compact planning call (+1 JSON-repair retry max) |
| `refine "..."` (AI) | 1 small call | one section patched, not the whole site |

Provider chain (cost order): Gemini free tier (AI Studio, then Vertex express
with the same key) -> OpenRouter `:free` models -> OpenWork org inference.
`--allow-paid` unlocks paid OpenRouter models; the ledger prices them from a
small list-price table. Every attempt (ok or failed) lands in `report.json`
with token counts - never key values.

## Quickstart

```
python forge.py init projects/myproj          # scaffold brief.md + copy/
# fill projects/myproj/brief.md and projects/myproj/copy/*.md with REAL copy
python forge.py build projects/myproj --offline --out sites/myproj
python forge.py check sites/myproj --expect-noindex
python forge.py serve sites/myproj            # http://localhost:4173
```

AI polish when a provider is configured:

```
python forge.py models --probe                # what is reachable right now
python forge.py build projects/myproj --out sites/myproj
python forge.py refine sites/myproj "tighten the hero" --section hero
```

Hand-edit path (zero tokens): edit `sites/myproj/site.json`, then

```
python forge.py build --from sites/myproj/site.json --out sites/myproj
```

## Copy mapping rules (offline planner)

Everything on the site comes from `copy/` files. Nothing is invented.

- First content block of `overview.md` (else `index/home/main/intro/about.md`,
  else the first file) becomes the hero: headline, lead paragraph, bullets.
- A block with 3+ bullets becomes a `features` section (icons guessed from
  keywords).
- Question paragraphs followed by answers become a `faq` section.
- Bullet lines shaped like `Name - $12` become `pricing` or `menu` rows.
- A heading matching contact becomes the `contact` section; email/phone are
  picked up from the text.
- Everything else becomes `about`-style text sections.
- Images only from local files listed in `assets.json`
  (`{"images": {"name": "path/relative/to/project.jpg"}}`). External stock
  URLs are dropped with a warning (download-only / no-hotlink rails).

## Checks (fleet-aligned)

`python forge.py check SITE [--expect-noindex|--expect-indexable]`

- `no_sample` - the same fleet patterns as
  `WebDev/tools/owp-tools/scripts/website_checker.py` (SAMPLE, lorem ipsum,
  hello world, under construction, ...), grepped on raw HTML.
- `no_soft_placeholders` - TODO/TBD/FIXME/lorem/placeholder in visible text.
- `no_hotlink` - the fleet stock-CDN blocklist.
- `meta_basics` - doctype, title, description, viewport per page.
- `noindex_status` - matches the build flag (default noindex).
- `internal_links` - every `#anchor` and `page.html` link resolves.
- `token_ledger` - mode + token totals from report.json.

Exit code is nonzero on any FAIL, so it can gate a deploy conversation.

## Commands

```
init      scaffold a project (brief.md + copy/README.md)
build     project dir -> static site        [--offline | AI chain | --from site.json]
refine    patch one section of a built site [--offline for theme flips]
check     run the built-in checks
serve     preview on localhost (default port 4173, auto-increments)
models    show the provider chain           [--probe queries live]
sections  list section types and data fields
```

Build flags: `--out DIR`, `--template modern|editorial|bold`, `--dark/--light`,
`--pages N`, `--brand NAME`, `--indexable`, `--max-copy-chars N`,
`--provider gemini|openrouter|openwork`, `--model ID`, `--allow-paid`,
`--max-tokens N`, `--no-fallback`.

## Output layout

```
sites/<name>/
  index.html      self-contained page(s): inline CSS + JS, system fonts,
                  inline SVG icons, gradient visuals; no external requests
  <slug>.html     extra pages (AI planner may create them)
  site.json       the IR - hand-editable, rebuild with --from
  site.json.bak   previous IR after a refine
  report.json     mode, provider/model, token ledger, warnings
  assets/         local images copied from the project
```

## Section types

hero, features, stats, steps, gallery, pricing, testimonials, faq, cta,
contact, about, team, menu, logocloud - see `python forge.py sections`.

## Extending

Add a section type in three steps:

1. `lib/ir.py`: add the type to `SECTION_TYPES`, a `normalize_data` branch,
   and its data fields to `SCHEMA_PROMPT` + `SECTION_DOCS`.
2. `lib/render.py`: add a `render_section` branch.
3. `lib/offline.py`: optionally add a copy-mapping rule so the zero-token
   planner can produce it.

## Provider setup

| provider | env vars | notes |
|---|---|---|
| Gemini | `FORGE_GEMINI_KEY_FILE` (path to a key file; wins over env vars, fails closed if unreadable), else `GEMINI_API_KEY` / `GOOGLE_API_KEY` | free tier; tries AI Studio then Vertex express. Recorded fleet keys live in `V:\Research4\.secrets\` (e.g. `vertex_medicineman_key.txt`, `vertex_fruitaholics_key.txt`, `vertex_patriotfuelstop_key.txt`). Point the engine at one without pasting values: `$env:FORGE_GEMINI_KEY_FILE = 'V:\Research4\.secrets\vertex_medicineman_key.txt'`. If you get `Agent Platform API has not been used in project ...`, enable the API in the Google console for that project. |
| OpenRouter | `OPENROUTER_API_KEY` | `:free` models by default; `--allow-paid` for paid |
| OpenWork | `OPENWORK_API_KEY` + `OPENWORK_INFERENCE_BASE_URL` + `FORGE_OPENWORK_MODEL` | org-provided inference |

Model lists are overridable: `FORGE_GEMINI_MODELS`, `FORGE_OPENROUTER_MODELS`,
`FORGE_OPENWORK_MODEL` (comma-separated).

## Status (2026-09-28)

- Offline build, checks, offline refine, rebuild-from-IR, serve: working.
- AI chain: wired and correct, currently blocked upstream - the provided
  Google key reaches Vertex but the Vertex AI API is not enabled on its
  project (HTTP 403 with the enable-API console URL). One console click by
  Keith unblocks it; the engine picks it up automatically and falls back to
  offline until then. OpenRouter/OpenWork keys are not set in this
  environment; the chain skips unconfigured providers.
