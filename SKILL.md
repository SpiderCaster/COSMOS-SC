---
name: spidercaster
description: >-
  use this to build static sites from the SpiderCaster tree (V:\a\ai\spidercaster\working) from REAL copy with zero or
  free-tier AI tokens (offline draft, Gemini free tier, OpenRouter :free) — not
  for live deploys, domain/CF work, or inventing content
---
# SpiderCaster

## When not to use
- Live deploys, DNS, Cloudflare zones, Softaculous, or any push to a host —
  SpiderCaster only builds local static output. Deploys stay with the OWP seats
  and the GROUP_ENV rails.
- Inventing content. The engine is copy-driven: if the copy/ folder does not
  contain the facts, the site does not show them.
- Sites that need WordPress/DB. Use the `owp sandbox` toolchain instead.

## Start
1. Confirm the project exists under `SpiderCaster\projects\<name>\` with a
   `brief.md` and real copy in `copy\` (md/txt/json). If not, scaffold it:
   `python spidercaster.py init projects\<name>` and fill the files first.
2. Check the provider chain if AI is wanted: `python spidercaster.py models --probe`.
   Free tiers first; paid models only when explicitly allowed.

## Steps
1. Zero-token draft (always safe):
   `python spidercaster.py build projects\<name> --offline --out sites\<name>`
2. Gate it: `python spidercaster.py check sites\<name> --expect-noindex`
   (fleet-aligned: no_sample markers, hotlink blocklist, links, meta, noindex).
   Fix to 0 fail before anything else.
3. Optional AI polish (free chain, 1-2 calls):
   `python spidercaster.py build projects\<name> --out sites\<name>`
   Falls back to offline automatically if every provider fails; the ledger in
   `report.json` records each attempt with the actionable error.
4. Iterate cheaply:
   - `python spidercaster.py refine sites\<name> "instruction"` (one small call)
   - `python spidercaster.py refine sites\<name> "light theme" --offline` (0 tokens)
   - hand-edit `sites\<name>\site.json`, then
     `python spidercaster.py build --from sites\<name>\site.json --out sites\<name>` (0 tokens)
5. Preview: `python spidercaster.py serve sites\<name>` (localhost only).

## Inputs vs constants
- **INPUTS (variable):** project dir (brief.md, copy/, assets.json), out dir,
  `--template modern|editorial|bold`, `--dark|--light`, `--pages`, `--brand`,
  `--provider`, `--model`, `--indexable`.
- **Constants (fixed unless Keith overrides):** noindex by default; no
  invented content; no hotlinking (external stock URLs dropped at ingest);
  secrets by env var name only (GEMINI_API_KEY, OPENROUTER_API_KEY,
  OPENWORK_API_KEY) or `FORGE_GEMINI_KEY_FILE` pointing at a recorded key
  file (e.g. `V:\Research4\.secrets\vertex_medicineman_key.txt`) — never
  print or paste key values; token ledger written to report.json every run.

## Confirm before consequential
- `--indexable` (removes noindex): only after a gate is signed. Ask first.
- Any deploy of SpiderCaster output to a host: out of scope here; hand back.

## Exit
Return the build/check summary and the token ledger line. Stop after report.

## Do not
- Do not fabricate copy, prices, names, quotes or stats to fill sections.
- Do not write key values anywhere; env names only.
- Do not treat a SpiderCaster build as deploy-ready; the fleet checker and the
  content gate still apply before anything goes live.

## Risk tier
Tier 0 local file work + read-only HTTP to model providers. No live targets.
