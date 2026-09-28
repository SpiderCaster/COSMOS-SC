# Commands

## Build

- forge init PROJECT: scaffold a project with brief.md and a copy folder.
- forge build PROJECT --offline: zero-token build mapped from your copy.
- forge build PROJECT: AI build on the free chain, with offline fallback.
- forge build --from SITE/site.json: rebuild after hand edits, zero tokens.

## Iterate

- forge refine SITE "instruction": patch one section, small token cost.
- forge refine SITE "light theme" --offline: theme flips cost nothing.

## Gate and preview

- forge check SITE: fleet-aligned checks (no_sample, links, noindex, meta).
- forge serve SITE: preview on localhost before anything goes anywhere.

## House rules the engine enforces

- No invented content: the AI prompt is hard-restricted to your source copy,
  and the offline planner only uses text it was given.
- Noindex by default: pass --indexable only after a gate is signed.
- No hotlinking: external stock-photo URLs are dropped at ingest.
- Secrets by env var name only: GEMINI_API_KEY, OPENROUTER_API_KEY,
  OPENWORK_API_KEY. Values are never written to disk by the engine.
