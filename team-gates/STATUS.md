# UI steps 6-7 (SC-side) — 2026-10-11 (UTC): rater verdicts + cDeck-last

Lane: SpiderCaster-side remainder of UI FINAL steps 6-7. Steps 0-5 shape
preserved; no engine files touched; stdlib only; zero new modules (stayed
within the `ui_` trio: `lib/ui_render.py`, `lib/ui_hands/`,
`lib/ui_selftest.py`; fixtures live in temp dirs inside the battery).

## Step 6 — rater verdict block, read-only (`lib/ui_render.py`)

- `rater_status(site_dir)` (pure, 0 hands): reads `site_dir/rater.json`
  beside the built pages. Each verdict row names its own `part` (built
  section/part id), `judge` (who rated it), `verdict`
  (`PASS/FAIL/WARN/SKIP`), and `cites` (copy sources judged against).
  States mirror the probe face: `NOT_RUN/SKIP` (no pages or no
  `rater.json` — unjudged is not a pass), `UNREADABLE/FAIL`,
  `STALE/FAIL` (optional `html_hash`/`hash` bound exactly like the probe
  binding), `FAIL_ROWS`/`SKIP_ROWS`/`WARN_ROWS`/`PASS`. Unknown verdict
  tokens, non-object rows, and empty row lists FAIL loudly as producer
  bugs. Never judges, never writes, never runs.
- `UI.rater_text()` (0 hands): renders the block (one line per row:
  part, judge, cites + detail) plus the exact surface command
  (`python spidercaster.py check <site>`, printed never run). Wired into
  Checks (screen 7, both board and gaps branches) and SEO (screen 8);
  both screens stay at <= 1 hand.
- The judge producer lives out-of-tree (same posture as step 4, whose
  `tools/layout_probe.py` writer is absent here): the face reports
  NOT RUN honestly instead of fabricating verdicts.

## Step 7 — cDeck-last wiring, read-only (`lib/ui_render.py` + `lib/ui_hands/`)

- `cdeck_contract()` (pure): `(tab, sidebar)` from `plugin/cosmos.json`
  (`website`, left sidebar); `unknown` when absent, never invented.
- `cdeck_status()` (pure, 0 hands): package order from `lib.crew.ROLES`,
  saved override from the engine's own `_saved_order` reader (env or the
  cDeck-owned `engine.json`), effective order with deployer forced last
  (`_ordered_roles`), workflow source, contract, and the deployer-last
  lock verdict via `ui_orchestrator.check_order` verbatim.
- `UI.cdeck_text()` (0 hands): contract + effective order + source +
  lock line (`LOCKED (deployer stays last…)`) + command-printer buttons
  (verify command, cDeck-sidebar reorder pointer). Lives on Import
  (screen 11, the last tab). Never writes a workflow, never executes.
- `lib/ui_hands/` printers (0 hands, never execute): `rater_surface_command`
  (existing `check` surfacer), `cdeck_verify_command` (existing
  `crew roles` verifier — no CLI applies an order, cDeck sidebar owns
  it), `cdeck_workflow_path` (env-override-wins pointer),
  `cdeck_order_preview` (dep-order lock verdict, `check_order` verbatim).

## 6Cs (my lines only; steps 0-5 debt untouched)

- `pycodestyle --max-line-length=100` clean on all three touched files.
- `flake8 --max-line-length=100` clean on all three touched files.
- `ruff check`: no new hits — the 7 RUF100 unused-`noqa` notes are the
  pre-existing steps 0-3 convention (E402 not enabled), on untouched lines.
- Whole-file `black` formatting left alone deliberately: it flags every
  region of these files including pre-existing steps 0-5 code, so
  reformatting would churn FINAL files (same call as the steps 4-5 lane).

## Tests (all PASS)

- `python spidercaster.py ui --selftest` — ok: composer battery +
  `ui_selftest ok (walk 0-11, gaps, e2e, probe, rater, cdeck, bind, lock)`.
- `python -m lib.ui_hands` — ok (incl. new printer + lock asserts).
- `python -m lib.ui_orchestrator` — ok (unchanged).
- New `rater_cdeck_battery` (temp-dir fixtures only, tree never written):
  NOT_RUN/SKIP + 0 hands, STALE on wrong hash, FAIL rows render
  part/judge/verdict/cites, SKIP/WARN map checker-like, bad-token/empty/
  non-object FAIL, bound green PASS with cites kept, Checks+SEO carry the
  block at <= 1 hand, package order is the seven seats with deployer last,
  lock green, contract `website`/left, cdeck face 0 hands on Import,
  deployer-first refused, env pointer wins and writes nothing, ledger
  byte-identical throughout.

## Open / not in lane (no action taken)

- No `rater.json` producer in this tree: every built site reports rater
  NOT RUN until the judging rail lands its writer (same as the step-4
  probe posture).
- `V:\A\Ai\COSMOS\live\state\profiles\website\engine.json` unreadable from
  here: effective order falls back to package order and the face says so.
- Remaining UI FINAL stretch item per prior STATUS: Textual port (not
  SC-side stdio work).

---

# HERO playbook §3-5: schema + AST gate + CI — 2026-10-11 (UTC)

Lane: engine interface formalization + boundary enforcement, live tree only.
Three files landed, all green in place; shipcheck green.

## Landed

- `mcp/schema.json` — generated from the live `mcp_server.py` TOOL_SPECS
  (26 tools). Envelope carries SERVER_INFO name/version
  (`spidercaster-mcp/0.1.0`) + stdio transport note; `tools[]` equals
  server TOOLS exactly (asserted, not hand-copied).
- `scripts/enforce_boundaries.py` — stdlib `ast` gate; lane map read from
  `ARCHITECTURE.json` at runtime (no hardcoded lanes). Rules: engine
  (lib/**, spidercaster.py, mcp_server.py) must not import seat lanes or
  sessions/cosmos markers; seats lane-only (own lane + engine only);
  sessions_cosmos untouchable tree-wide (tools/ scanned for this rule
  only). Exit 0 `boundaries ok`, 1 with file:line + rule list.
- `.github/workflows/boundary_gatekeeper.yml` — CI on push/PR: boundary
  gate + schema==TOOLS assert + secret_scan --all + shipcheck.

## 6Cs (this lane's lines only)

- schema consistency assert: TOOLS == schema tools[] == TOOL_SPECS,
  26 tools, version match — PASS.
- `python scripts/enforce_boundaries.py` — `boundaries ok` on live tree.
- Negative probe (scratch fixtures, tree untouched): engine->seats import
  + seat->sessions import both caught, exit 1 with rule ids — gate is not
  vacuous.
- `python spidercaster.py shipcheck` — ok.
- stdlib only in the gate; no engine files modified (additive files only).

## Open / not in lane (no action taken)

- Seats remain markdown-only (SKILL.md/WRAPPER.md per lane); the seat
  branch of the gate is armed but has no .py to scan yet.
- Parts root (`V:/streams/...`) lives outside this tree: data_only is
  declared in ARCHITECTURE.json, not AST-scanned here.
