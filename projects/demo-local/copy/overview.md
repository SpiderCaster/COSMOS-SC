# SpiderCaster: websites from real copy, on free tokens

SpiderCaster is a copy-driven static website engine. You give it a brief and
real copy files; it returns a self-contained static site. The structure,
layout, styling and assembly are deterministic code, so the bulk of every
build costs zero tokens. AI is optional and rides the free chain: the Gemini
free tier first, then OpenRouter free models, then OpenWork inference. Paid
models join only when explicitly allowed.

The engine follows the WebDev package rails: it never invents facts, prices
or claims; output stays noindex until approved; secrets are read from
environment variable names only; and every run writes a token ledger so the
cost is auditable.

## Why it is cheap

- Deterministic assembly: layout, CSS, icons and pages are code, not tokens.
- Offline mode: a full draft with zero tokens, mapped straight from your copy.
- One-call AI builds: a single compact planning call produces the whole site
  shape, with at most one JSON-repair retry.
- Refine instead of rebuild: edits touch one section, so a revision costs a
  few hundred tokens instead of a full build.
- Hand edits are first-class: edit site.json directly and rebuild for free.
