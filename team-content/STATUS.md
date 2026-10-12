# HERO BUILDER MAX — retire FAQPage JSON-LD (Google removed FAQ rich result) — 2026-10-12 (UTC)

Source: `P:/SpiderCaster_Nest/seo-research/schema.md` section 1 (browser-verified
2026-10-12: FAQPage dev doc URL redirects to the Search updates page; restricted
2023-08-08 to gov/health, removed by May 2026). Rule: never emit
`FAQPage`/`Question`/`Answer` markup; visible FAQ sections stay (good content,
zero rich-result payoff for the markup).

## Changes (4 files, stdlib only, no new imports)

- `lib/render.py` — deleted `_faq_pairs` + `faq_jsonld` and the `{faq_ld}` slot
  in `render_page`. Pages now emit WebSite JSON-LD only. Visible `faq` sections
  (`render_section` kind `faq`, native `<details>`) untouched.
- `lib/check.py` — `faq_schema` row now FAILs any page whose JSON-LD carries
  `@type FAQPage` ("FAQPage retired ... remove JSON-LD, keep visible FAQ") and
  PASSes ("no FAQPage") otherwise. Replaced `_question_names`/`_faq_questions`/
  `_faq_schema_gaps` (visibility check, obsolete) with `_has_faqpage`.
  `json_ld` valid-or-absent logic unchanged; comments no longer bless FAQPage.
  Row name kept stable for `lib/studio.py` GROUPS + board/scorecard consumers.
- `library/research/ui/check-board.md`, `library/research/ui/scorecard.md` —
  `faq_schema`/`json_ld` descriptions updated to the retired rule.
- Article/BreadcrumbList/LocalBusiness per schema.md required/recommended
  fields: no emission exists in the pipeline today (only WebSite was ever
  emitted), so "keep" is a no-op — nothing added, nothing broken.

## Deliberately untouched (history + external catalogs + stale build outputs)

- `library/research/app/*` (BOARD3, SEO_STAGE2, inbox/faq-schema etc.),
  `library/research/competitors/*.md`, `bench/results/*`: dated research/stage
  reports describing the old conditional emission. Rewriting them falsifies
  history; they are superseded by this entry + schema.md.
- `sites/assembled/parts.json` (`hooks-blocks-schema-faqpage-001`,
  `kit-faq-accordion`): external fleet/kit part catalog, not SpiderCaster
  emission. Left for the parts-lane owner.
- `sites/*/*.html` committed build outputs still contain old FAQPage blocks.
  They are stale artifacts — the next rebuild drops the markup (and the new
  `faq_schema` row will FAIL them until rebuilt, by design).

## Verification (all PASS)

- `python -m py_compile lib/render.py lib/check.py` — ok.
- Functional (temp objects, tree never written): page with a full faq section
  renders zero `FAQPage` but keeps visible `<details>` Q/A; `_has_faqpage`
  False on new output, True on a legacy FAQPage fixture.
- No selftest references `faq_schema`/`FAQPage`/`faq_jsonld` (grep over
  `lib/*selftest*.py`, `lib/hands/`, `lib/ui_*`, `spidercaster.py` — zero
  hits), so no selftest needed edits; behavior proven by the functional probe.
- 6Cs on touched lines: `ruff check lib/render.py` clean; `lib/check.py`
  ruff 136 = pre-existing coder-lane debt, zero hits on new lines;
  `pycodestyle --max-line-length=100`: no E501 on any new line (nearest hit is
  pre-existing `render.py:827` bullets line); whole-file black/flake8/mypy
  debt untouched per lane convention (no reformats, no behavior churn).
- `python lib/shipcheck.py` — ok (`shipcheck ok`, 16/16 steps).

---

# HERO CLOSER — engine lib lint (MAX pack) — 2026-10-11 (UTC)

Scope: `V:/A/Ai/spidercaster/working/lib/` ONLY. No toy dirs touched.
Rule: `ruff --fix` safe fixes only (never `--unsafe-fixes`). No behavior changes.
Method: baseline board -> targeted safe fixes on engine-owned files ->
`py_compile` + affected selftests + `shipcheck` -> re-board.
Result: ruff 222 -> 221. All other gates unchanged (residuals owner-listed below).

## Safe fixes applied (2, engine-owned only)

- `lib/attempts_selftest.py` — I001 import-block sort (import reorder only).
- `lib/ir.py:245` — SIM114 combined same-arm `isinstance` branches with `or`
  (byte-identical semantics). This exposed SIM101 on the merged line
  (merge into one `isinstance` tuple call) — ruff marks it unsafe, so per the
  safe-only rule it is LEFT and listed under engine residual.

Deliberately untouched: `lib/check.py` (coder lane, actively edited, 136 hits),
`lib/ai_chain/*` (vendored upstream, 24 hits), `lib/ui_*` + `lib/ui_hands/`
(UI lane FINAL; their 8x RUF100 dead-`noqa` are a documented convention).

## Verification (post-fix, all PASS)

- `python -m py_compile lib/ir.py lib/attempts_selftest.py` — ok
- `python lib/attempts_selftest.py` — ok (attempts + tel + mobile_block)
- `python lib/part_pick_selftest.py` — ok (ir consumer)
- `python lib/shipcheck.py` — ok

## Bench board (`python tools/pycheckers/run.py lib` + manual counts)

| gate | verdict | count / detail |
|---|---|---|
| ruff | FAIL | 221 (was 222): coder 136 / vendor 24 / engine+ui 61 |
| pycodestyle (100) | FAIL | 593: E501 x534, E402 x37, E203 x11, E741 x3, E702 x2, E303 x2, E127 x2, E731 x1, E305 x1 |
| flake8 (100) | FAIL | 596 (pycodestyle set + F841/E731-class singles) |
| black --check | FAIL | 81 files would reformat (whole-file churn, not applied) |
| mypy | FAIL | 224 errors / 37 files |
| pylint (errors only) | FAIL | `check.py` E1136 + E0102 + E0401-PIL; `visit_check.py` E0401-playwright |
| bandit | FAIL | 261 low + 5 med (assert-driven per project style) |
| vulture | FAIL | ~8 names (`ui_composer.compacted`, `ui_hands.indexable_command`, `ui_orchestrator.screen_order`/`advance`, `ui_render.CDECK_TAB`/`CDECK_SIDEBAR`/unreachable, `visit_check.handle_data`) |
| pytest-collect | PASS | 17 tests |
| pip-audit | PASS | No known vulnerabilities |
| detect-secrets | PASS | empty results |

## Owner table (residuals — none safe-auto-fixable in scope)

- engine: ruff BLE001 x~21 / FLY002 x9 / PLW1510 x5 / S110 x4 / PIE810 x4 /
  TRY004 x2 / RUF012 x2 / S112 x1 / F841 x1 (`studio.gap_rows`) /
  RUF034 x1 / ISC004 x2 / SIM101 x1 (new, from SIM114 merge — manual fold into
  one tuple call if desired); visit_check E0401-playwright (optional dep);
  E501 payload lines; E402 sys.path bootstraps (tree convention); E203
  black-slice style; black whole-file; mypy 224; bandit asserts; vulture
  `visit_check.handle_data`.
- coder (`lib/check.py`, lane-active): ruff 136 (FURB167 x71, UP037 x20,
  BLE001 x23, SIM114 x3, SIM102 x2, B023 x2, + singles incl. F841/E731);
  pylint E1136/E0102/E0401-PIL. Untouched — coder lane.
- vendor (`lib/ai_chain/sc_ai_chain.py`): ruff 24 (BLE001 x10, FURB167 x5,
  UP045 x4, S110 x2, UP035/UP007/RUF100 x1); E702 semicolons, E127 indents.
  Untouched — upstream style.
- ui/hands lanes: RUF100 x8 dead-`noqa` (their documented convention);
  hands E501 x~5; vulture ui_* names; mypy `ui_composer`/`ui_selftest` rows.
  Untouched — UI/hands lanes.

## Bench delta (this session)

Before: FAIL ruff(222)/pycodestyle/flake8/black/mypy/pylint/bandit/vulture;
  PASS pytest-collect/pip-audit/detect-secrets.
After: FAIL ruff(221)/pycodestyle/flake8/black/mypy/pylint/bandit/vulture;
  PASS pytest-collect/pip-audit/detect-secrets.
Net: ruff 222 -> 221 (-I001, -SIM114, +SIM101-unsafe listed). Zero behavior
change (2 same-semantics hunks; compile + 2 selftests + shipcheck green).
All-PASS not reachable by safe fixes — remainder is manual/owner work above.

---

# HERO BUILDER MAX — jobs 1+2: ARCHITECTURE.json + agents.md — 2026-10-11 (UTC)

Scope: repo root ONLY. Two smallest-job-first commits on `wip/sc-catchup-2026-10-03`.
Playbook: `P:/SpiderCaster_Nest/specs/AGENTIC_ARCHITECTURE_PLAYBOOK.md` sections 0/1 (job 1), 2 (job 2).

## Job 1 — `ARCHITECTURE.json` (commit 2f23c18)

Machine-readable topology: base = playbook section 1 sample, extended with the
section 0 real-module rows the sample omits (`tools_nest`, `sessions_cosmos` boundary).
Grounded against the live tree before writing:

- engine `lib/` + root `spidercaster.py` exist; live interface is `mcp_server.py`
  TOOLS — `mcp/` holds only `HARNESS_CONFIGS.md`, so `mcp/schema.json` is recorded
  as the interface with a `live_interface` note (formalization = playbook section 3 job).
- seats: 7 lanes verified, each with `SKILL.md` + `WRAPPER.md`
  (architect, content, deployer, frontend, graphics, seo, visual).
- parts: `V:/streams/webdev/tools/parts/` verified, `manifest.json` per part
  (spot-checked `sidebars/sidebars-ad-slot-001/`), `catalog.json` per family
  (spot-checked `popups_callouts/catalog.json`).
- tools/nest: `tools/` + `P:/SpiderCaster_Nest/` verified present.

## Job 2 — `agents.md` (commit 4a9e3ee)

Lane rules verbatim from playbook section 2 (no file-hopping, zero
cross-imports, localized tests, gates over sentences).

## Verification (both jobs, all PASS)

- `python -c "json.load(open('ARCHITECTURE.json'))"` — parses ok (5 modules).
- `python lib/shipcheck.py` — ok (run after each commit).
- 6Cs: touched files are JSON + Markdown (no Python lint surface); JSON parse
  is the syntax gate, shipcheck is the selftest gate. No Python files touched,
  so ruff/pycodestyle/flake8/black/mypy deltas are zero by construction.
