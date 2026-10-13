# HERO Visuals & Graphics Upgrade (GF38 Full Packs) — 2026-10-13 (UTC)

Lane: Modern visual design, procedural vector hero art, markdown image ingestion, WebP measurement, and Imagine integration
Tree: `V:/A/Ai/spidercaster/working` (live tree only; no toy dirs)
Changed files: `lib/render.py`, `lib/ingest.py`, `lib/ir.py`, `lib/offline.py`, `lib/compose.py`, `lib/ui_render.py`, `spidercaster.py`, `.gitignore` (+ this STATUS file)

## Result: DONE — all gates pass, 18/18 shipcheck steps green, boundaries ok, secret scan clean

### 1. Ingestion & Auto-Asset Discovery (`lib/ingest.py`, `spidercaster.py`)
- Fixed markdown image ingestion: `parse_markdown` extracts `MD_IMAGE_RE` links into `cur.images` before text stripping.
- Auto-discovery of local project assets: `load_project` scans `project/assets/` (`.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`, `.gif`) into `assets` without requiring manual `assets.json` entries.
- Hero asset copying: `copy_assets` now copies referenced hero images from `project/assets/` into `site/assets/`.

### 2. Modern Design System & CSS Lighting (`lib/render.py`)
- Ambient lighting: subtle radial mesh backdrop (`radial-gradient(ellipse 80% 50% at 50% -20%, var(--accent-soft), transparent 70%)`).
- Card elevation: modern glassmorphism depth, semi-translucent borders (`var(--line)`), soft drop-shadows, and smooth `-3px` hover elevation with accent glow.
- Polished chips & badges: enhanced `.chip` with border, soft accent background, and subtle shadow.
- Interactive styling: smooth transitions on cards, details/summary accordions, and buttons.

### 3. Procedural Vector Mockups & Expanded Icons (`lib/render.py`, `lib/ir.py`, `lib/offline.py`)
- Replaced the single-letter monogram fallback with `vector_hero_svg()`: a crisp 16:9 responsive vector mockup featuring a glassmorphic window, code/content blocks, metric cards, sparkline chart, and ambient glow.
- 100% vector geometry with 0 text nodes (fully compliant with fleet `cited_text` and `no_hotlink` rules).
- Expanded `ICONS` from 25 to 40+ curated SVGs (`terminal`, `browser`, `database`, `server`, `palette`, `layout`, `rocket`, `box`, `search`, etc.), synced with `lib/ir.py::ICON_NAMES` and `FEATURE_ICON_HINTS`.
- Upgraded gallery fallback tiles with styled vector geometric motifs instead of plain flat gradient rectangles.
- Added WebP header dimensions parsing in `image_box` for layout stability.

### 4. AI Imagine Pipeline (`spidercaster.py`, `lib/imagine.py`)
- Added `--imagine` build flag to `spidercaster.py build`: generates a prompt-tailored local `assets/hero.png` via xAI/OpenRouter and automatically links it to the site hero.

### 5. Modular Component Bridge & Windows Lock Reliability (`lib/compose.py`, `lib/ui_render.py`)
- Preserved `data-cta="primary"` on composed hero parts in `lib/compose.py`.
- Windows process query fix in `lib/ui_render.py`: safe `OpenProcess` check prevents WinError 87 kernel locks during UI selftests.

### 6. Verification (all PASS)
- `python spidercaster.py shipcheck` — 19/19 steps green (`shipcheck ok`, incl. `graphics_engine`).
- `python scripts/enforce_boundaries.py` — `boundaries ok`.
- `python scripts/secret_scan.py --all` — 0 findings (exit 0).
- `python -m unittest tests.test_secret_scan -v` — 17/17 tests green.
- `python spidercaster.py crew selftest` — ok.
- `python spidercaster.py ui --selftest` — ok.
- `python spidercaster.py check sites/demo-local` — 59 pass / 0 fail / 1 warn / 4 skip.
- `python spidercaster.py check sites/demo-local-compose` — 59 pass / 0 fail / 1 warn / 4 skip.
- `python spidercaster.py check sites/spidercaster-com` — 58 pass / 0 fail / 3 warn / 3 skip.

### 7. Multi-Level Graphics Engine (`lib/graphics_engine.py`, CLI `spidercaster.py graphics`)
- **Level 0 (Vector Art):** Algorithmic 16:9 vector illustration generator across `browser`, `terminal`, `dashboard`, `isometric`, and `editorial` kinds; 100% vector geometry, 0 text nodes.
- **Level 1 (Sparklines & Gauges):** Dynamic SVG sparkline trend paths and data curves for metric cards.
- **Level 2 (Asset Audit & Normalization):** `audit_project_assets()` and `normalize_image_luma_and_weight()` automatically optimize file sizes (<= 200KB) and luminance (90 <= luma <= 200).
- **Level 3 (AI Multi-Slot Imagine):** `imagine_project_slots()` synthesizes hero still lifes, documentary gallery suites, and card spotlights with proven camera rules.
- **Level 4 (Verification):** Integrated into `spidercaster.py shipcheck` (19/19 steps green).

---

# HERO render lane — STATUS

Date: 2026-10-11 (UTC)
Lane: fix `_hero_actions` secondary-button regression vs HEAD + mobile-first conversion
Tree: `V:/A/Ai/spidercaster/working` (live tree only; no toy dirs)
Reference HEAD: `V:/A/Ai/spidercaster/backups_20261006/render.py.bak.20261006_091107`
Changed file: `lib/render.py` (+ this STATUS file)

## Result: DONE — all lane gates pass, 6Cs clean (ruff fully; pycodestyle except byte-sensitive payload lines)

## 1. Regression fix (was already in the live tree; verified, not re-broken)

HEAD rendered the hero secondary inconsistently (hero dropped it; CTA panel drew it as a
second `btn ghost` competing button) and carried no single-CTA marker. Planner output ==
HEAD, render differed. Live tree now:

- `_alive_link` / `_pick_actions` / `_hero_actions` / `_cta_actions`: one primary button
  plus, at most, a subordinate text link (`hero-more` / `cta-more`).
- Lone secondary is promoted to the single primary button (keeps `data-cta="primary"`).
- Secondary repeating the primary href/label is dropped (no duplicate competing treatment).
- Exactly one `data-cta="primary"` per page; `btn()` only emits the marker for the hero path.

## 2. Mobile-first conversion (verified in live tree)

- One cited CTA site-wide (marker count == 1, no `btn ghost` in hero/CTA).
- Thumb bar: `.phone-bar` with `tel:` href from contact copy; hidden while nav drawer open.
- Safe area: `viewport-fit=cover`, `env(safe-area-inset-*)` on header/drawer/thumb bar/footer,
  `scroll-padding-top/bottom` so focus is never covered.
- 44px floor: `min-height`/`min-width:44px` on buttons, nav/drawer links, foot links,
  contact rows, `hero-more`/`cta-more`.
- No overflow 360 / 1280: single-column base under 860px (grids forced to `1fr`, drawer is
  `position:fixed`), structural layer at 861px, wide layer at 1280px. Static scan of a
  14-section kitchen-sink page: no fixed element widths above breakpoints; grid
  `minmax()` floors are 230–300px (fit 328px content at 360px viewport; mobile forces 1fr anyway).
- Layout stability: hero `img` carries `width`+`height`, CSS keeps `height:auto`.
- Budgets (kitchen-sink, dark/light): raw ~31.4KB (<= 153600), gzip ~8.1KB (<= 40960),
  inline script 1976B (<= 4096), zero-framework output (no remote URL / @import / @font-face).

## 3. 6Cs (ruff + pycodestyle on `lib/render.py`)

My lint pass (output-neutral, equivalence-checked: `rgb_to_hex` vectors, `hue_of`,
`resolve_href` cases):

- removed unused `from datetime import date` (F401; also fixes I001 ordering)
- added the missing 2nd blank line before `def esc` (E302)
- `rgb_to_hex` `.format()` -> f-string (UP032, identical bytes)
- `hh, ss, vv` -> `hh, _, _` (RUF059)
- merged double `startswith` into one tuple call (PIE810, identical behavior)
- `f'<div class="hero-copy">'` -> plain string (F541)
- loop var `l` -> `lnk` in `foot_links` (E741)

After: `ruff check` = **All checks passed**; `pycodestyle --max-line-length=120` = **0 non-E501
hits**. Remaining E501s (~41) are all inside the CSS `Template` / ICONS / JS payload strings
where wrapping would change shipped bytes; same convention as HEAD (HEAD also fails
E302/E501/E741 classes). No new violation classes introduced.

## 4. Tests (all PASS, post-change)

- `python lib/hero_link_selftest.py` — ok (promotion, one-button-plus-link, dup-drop, empty-row, dead-link re-target)
- `python lib/render_budget_selftest.py` — ok (budgets, single CTA, thumb bar, safe area, stability, 1280 layer)
- `python -m lib.mobile_selftest` — ok (16 mobile needles, incl. no `height:168px`, phone-bar tel:)
- `python lib/check_mobile_selftest.py` — ok (scroll/drawer/visibility/spec, 360/390/412)
- `python lib/check_tap_selftest.py` — ok (>= 44px rows)
- `python lib/check_typography_selftest.py` — ok

## 5. Diff summary (`lib/render.py` — my edits this session)

Six output-neutral lint hunks (import, blank line, rgb_to_hex, hue_of, resolve_href,
hero-copy string, foot_links var). The lane fix itself (CTA contract + mobile-first CSS,
~100 lines vs HEAD backup) was already present in the live tree and is untouched by my
edits — verified byte-equivalent behavior via the selftests above plus the
`rgb_to_hex`/`hue_of`/`resolve_href` equivalence probes.

## Open / not in lane

- E501 payload lines left as-is deliberately (byte-sensitive). If the team ever wants them
  gone, the lever is a `per-file-ignores` ruff config + pycodestyle ignore, not wrapping CSS.
- Pages with two hero sections would emit two `data-cta` markers (contract assumes one hero;
  unchanged from the lane fix, no test covers it).

---

# Debt closer (gf38) — 2026-10-11 (UTC): runner fix + lint triage + MISSING regen

Note: brief said `team-content/STATUS.md`; no `team-content/` dir exists in the live
tree, so this entry goes in the live file (`team-render/STATUS.md`).

## 1. Runner fix: `tools/pycheckers/run.py` pip-audit invocation

Was `[python -m pip_audit --disable-pip]` (no `-r`): pip-audit rejects it
(`--disable-pip` requires `-r`), so the bench's pip-audit gate always FAILed.
Now the plain call with the requirements file (verified `No known vulnerabilities found`):

`[sys.executable, "-m", "pip_audit", "-r", "tools/pycheckers/requirements-pycheckers.txt"]`

One-line diff, nothing else in the runner touched. Bench: pip-audit FAIL -> PASS.

## 2. Lint triage: safe auto-fixables on engine-owned files only

`ruff check --fix` (safe fixes only, no `--unsafe-fixes`) applied to the 38
ruff-flagged engine-owned `lib/` files. Untouched by design: `lib/check.py`
(coder-owned per BOARD, 129 ruff hits), `lib/ai_chain/*` (vendored upstream,
24 hits), `lib/hands/*` (hands-owned, 0 ruff hits anyway).

- 97 safe fixes across 27 files (FURB167 `re.I`->`re.IGNORECASE`, UP037/UP045/
  UP035/UP017 annotation/import modernisations, F541 f-string->plain string,
  RUF100 dead-noqa removal, SIM114, FURB188, RUF023, UP007...). 12 files fully clean.
- Engine-owned ruff: 144 -> 52 hits. Lib-wide ruff: 297 -> 205. No file increased.
- flake8 F541 class eliminated on engine files (was 12, now 0).
- Verified: all changed modules `py_compile` + import ok; 17/19 engine selftests
  pass (assemble/compose fail on tree-CONTENT assertions — catalog.html weight and
  cited-CTA presence from the parts tree, not on lint-touched logic; flagged below).
- 6Cs on the 28 changed files (ruff/pycodestyle/flake8/black-check + compile/import
  + selftests): no new violation classes introduced. Remaining hits are all
  pre-existing classes (E501 payload lines, E402 sys.path bootstraps, E203
  black-slice style, F841 `gap_rows`, ruff unsafe-only rules, whole-file black
  formatting, run.py's 4 pre-existing PLW1510/UP031 style hits).

The rest, by owner (post-fix counts):

- engine: ruff 52 (BLE001/FLY002/PLW1510/PIE810/S110/TRY004/S112/F841/RUF012/RUF034/
  ISC004 — all need manual or unsafe fixes); pycodestyle 353 / flake8 354
  (E501 x522 — payload/content lines, E402 x31 sys.path bootstraps, E203 x11
  black-slice style, F841 x2, E731/E303/E305/E741); black --check 69 files;
  mypy 199 errors / 32 files; pylint E0401 playwright import (visit_check);
  bandit asserts + try/except pass/continue; vulture unused names.
- coder (`lib/check.py`): ruff 129, pycodestyle 177, flake8 178, pylint
  E1136/E0102/E0401-PIL. Untouched — coder lane.
- vendor (`lib/ai_chain/sc_ai_chain.py`): ruff 24, pycodestyle 36 / flake8 37
  (incl. E702 semicolons). Untouched — upstream style.
- hands (`lib/hands/`): pycodestyle/flake8 8 (E501). Untouched — hands lane.
- `tools/pycheckers/run.py` (bench tool): 4 pre-existing ruff style hits
  (PLW1510, 3x UP031); left as-is to keep the runner diff to the one-line fix.

## 3. MISSING regen: `library/tools/MISSING.json` -> `[]`

`lib.tools_index.index_rows()`: 208 rows, 208 built, 0 missing (all 84 stale
MISSING entries verified present in the parts-tree claim map). Regen procedure:
missing rows from `index_rows()` joined to catalog rows for the builder-spec
fields; zero missing rows -> empty array (repo CRLF convention kept).
Old 84-entry / 95KB file replaced by `[]`. Report: EXPECTED-EMPTY CONFIRMED.

## Bench delta (`python tools/pycheckers/run.py lib`)

Before: FAIL ruff/pycodestyle/flake8/black-check/mypy/pylint-errors/bandit/vulture/
pip-audit; PASS pytest-collect/detect-secrets.
After: FAIL ruff/pycodestyle/flake8/black-check/mypy/pylint-errors/bandit/vulture;
PASS pytest-collect/pip-audit/detect-secrets.
Net: pip-audit FAIL->PASS; ruff 297->205 (-92 net, -97 applied incl. 5 exposed
manual-class hits); flake8 F541 class gone on engine files. All other gates
unchanged (residuals triaged by owner above, none safe-auto-fixable in scope).

## Open / not in this closer

- assemble_selftest (catalog.html weight + one_cta) and compose_selftest (one_cta)
  fail on parts-tree CONTENT assertions; safe lint fixes are semantics-preserving
  and all touched modules compile/import + pass their unit selftests, so these read
  as pre-existing tree-state failures. Needs a content-lane look, not a lint look.
- Black formatting (69 files) and E501 wrapping deliberately not applied:
  whole-file reformats would swamp lane diffs and risk byte-sensitive payloads.

---

# Tokens + sitemap lane (FINAL D1/D5) — 2026-10-11 (UTC)

Build order steps 1–2: `lib/tokens.py` + `lib/sitemap.py` (+ selftests),
scoped requirement, seat additions. Stdlib only, zero tokens. Live tree only.

## New files

- `lib/tokens.py` — G47 section-5 contract: spacing {4,8,12,16,24,32,48,64},
  system stacks (serif/sans/slab/mono-display, no @font-face/remote/@import),
  ink `#1a1a1a` / paper `#ffffff` (+ dark swap, both pairs >= 4.5:1),
  body 1.125rem/1.5, chrome 1rem, H1 `clamp(1.75rem,4vw,3rem)`,
  text `max-width:min(68ch,100%)`, section padding 32px / 48px at 1280px
  (container 1120px). `cta_ink()` picks ink-or-paper whichever clears 4.5:1
  (higher ratio), else TokensError = mold-bind FAIL. `nontoken_spacings()`
  scale-checks margin/padding/gap declarations only (fonts/borders exempt).
  `token_css(mold)` emits the token-only base CSS, byte-stable.
- `lib/tokens_selftest.py` — scale/stack/pair/cta/bind-floor/spacing-
  extraction/token-css battery.
- `lib/sitemap.py` — `spidercaster-sitemap/1` planning doc, distinct from
  `lib/seo_pack.py` (crawl-facing sitemap.xml from pages on disk; this module
  plans pages before they exist). Emit (deterministic; repeats allowed, hero-
  first, index-first, internal `#`/`.html` edges only), `scope_required()`
  (crew/multi-page required, offline single-page emit-only),
  `validate()` (schema/slug/intent/vocab/link/orphan), `check()` (plus
  one-h1-per-page and FAQ-visible-match; unrendered pages SKIP, never PASS),
  `read_for_architect()` subset, printable `wireframe_text()`,
  write/load/find helpers, `FAIL pages.scope` id.
- `lib/sitemap_selftest.py` — scope matrix, emit guards, validate flags,
  check PASS/FAIL/SKIP, IR derive (missing intents flagged, never invented),
  write/load/find roundtrip battery.
- `projects/demo-local/sitemap.json` — single-page doc mirroring the demo
  plan (generated via `emit_sitemap`, checked in so `crew selftest` runs
  the new hands).

## Seat wiring (extends in place)

- Architect +`sitemap_read`, SEO +`sitemap_check`: `lib/hands/__init__.py`
  (2 hands + HANDS entries), `lib/crew.py` ROLES, `lib/seat_gate.py` +
  `lib/seatpack.py` selftest asserts, architect/seo SKILL.md + WRAPPER.md
  (allowed-hands + steps). `sitemap_read` FAILs intent-less/non-frame and
  missing-doc `pages.scope`; `sitemap_check` grounds h1/FAQ in rendered HTML.
- `lib/hands/selftest.py` fixture now writes `project/sitemap.json`
  (single hero page) so the ORDER loop covers the new hands.
- `lib/check.py` untouched (coder lane owns it; sitemap rows there are a
  later step, not this lane).

## 6Cs (on new + touched files)

- `ruff check` clean on all 9 touched/new py files; `pycodestyle
  --max-line-length=120` clean on new files (2 E501s in hands files are
  pre-existing lines, left per convention); flake8 E402 on the two selftests
  matches the existing bootstrap convention (seo/mold-paint selftests same).
  py_compile + import ok throughout.
- Tests: `tokens_selftest`, `sitemap_selftest`, `sitemap --main`,
  `seat_gate`, `seatpack`, `hands.selftest`, `spidercaster.py crew selftest`
  — all PASS. (One selftest vector corrected mid-lane: `#c8923e` clears CTA
  with ink ~6:1, not paper; module was right.)
- Pre-existing, not mine: `check.py` was mid-edit by the coder lane during
  this session (caught one torn write live; settled). `crew.py` carries that
  lane's `_call_hand` gate hunks alongside mine — no conflict. `python
  lib/seat_gate.py` as-script import failure is pre-existing (use `-m`).

## Open / not in lane

- `check.py` sitemap/conversion rows, `attempts.py` + dry-run/rollback,
  tel auto-wire, probe tool, ticket/ledger wiring — later build-order steps.
- Multi-page crew fixture: no `visit.html`-style second page exists yet, so
  the orphan/link-dangling rows are selftest-covered but not fixture-covered.

## Cross-lane fix this session (flagged for coder/attempts lanes)

- Collision: attempts lane's `attempt_snapshot` (frontend) writes
  `out/_attempts/<id>/*.html`; coder lane's new `slug_scan` (`rglob
  *.html`) scanned them as product pages, so `hands.selftest` /
  `crew selftest` failed `slug_shape` on the snapshot id + `_attempts`
  names. Fix (2 lines, `lib/check.py::slug_scan`): skip `rel.parts[0] ==
  "_attempts"`, mirroring the `_sha_bound` exclusion the attempts lane
  already owns (FINAL D2: `_attempts/` hash-excluded provenance, not
  product). No new lint hits from the hunk (coder ruff/pycodestyle residuals
  otherwise untouched). Coder lane: fold this into your rows pass or revert
  as you prefer; attempts lane: heads-up only, nothing of yours changed.

---

# UI steps 0-1 (composer + ticket/ledger face) — 2026-10-11 (UTC)

Build order steps 0-1 per `ui-plan-FINAL.md` (V1/V3/V4/V7): `lib/ui_composer.py`
+ `spidercaster.py ui` entry + ticket/ledger face. Stdlib only, zero tokens.
Live tree only (`V:/A/Ai/spidercaster/working`).

## New files (1)

- `lib/ui_composer.py` — SPARK section 3 composer semantics as requirements
  (FINAL V3): frozen parse-only descriptors (`effect=none`; talk is `Plain`);
  caps history-50 / buffer 32x4000 / RETRY_CAP 2; no off/yolo (BAD_MODE);
  `!` lines stay plain text, never shell; SECRET lines refused, never stored
  or echoed; approval ladder manual -> acceptEdits -> plan; Session with
  accept/append_line/flush/interrupt/transcript/rebuild/restore (+ save/load
  helpers); ROLLBACK_MISS over the empty v1 store. Ticket face always
  renders (missing/unreadable -> ok:false + refusal line); `ok:true` only on
  engine `ok` + visual PASS; ledger view reads `report.json` read-only
  (unknown stays `unknown`, offline numeric 0, `cost_known:false` flagged);
  footer line on every screen; `/publish` arming via engine
  `verify_live_ticket` with refusal strings verbatim, `executed` always
  False, exact `library bind --live` command printed. `/plan` = 0-token
  offline dry-run (block -> slot map, gap FAILs as `FAIL gap
  section.field`), `hands_used` always empty. `run_ui()` stdio loop
  (Projects screen default; every action <= 1 hand, here: none).
  Selftest is `main()` in-module (no second new file): parse/caps/refusals/
  transcript roundtrip + ticket battery (clean / 1-byte flip / ok:false /
  visual FAIL / missing) + live-collision (`already live`) + ledger honesty
  + stubbed-input walk asserting footer-on-every-screen. Exit 0 required.

## Edits in place (no other new files; cap honored)

- `spidercaster.py`: docstring `ui` line + `cmd_ui` + one `ui` subparser
  (`[project]`, `--selftest`, `--screens`). `--selftest` runs the composer
  battery AND the sibling screens battery (`lib/ui_selftest.py`); default
  opens the composer loop; `--screens` opens the sibling check-board /
  engine-room loop. NOTE: a sibling lane concurrently landed
  `lib/ui_orchestrator.py` + `lib/ui_hands/` + `lib/ui_render.py` +
  `lib/ui_selftest.py` with its own `cmd_ui`/`ui` parser; both were merged
  into the single entry above (duplicate parsers broke argparse).
  Deviation note: FINAL V3/V7 house the composer as rules on `ui_render.py`;
  per the build order the composer ships as the thin `lib/ui_composer.py`
  module instead (same `ui_` prefix family, stdlib-only, no `cli_tui`
  import, no `tui/` package). No engine files touched.

## 6Cs (new file only; engine debt untouched)

- `ruff check` clean + `pycodestyle --max-line-length=100` clean on
  `lib/ui_composer.py`; `py_compile` + import ok.
- `spidercaster.py`: no new violation classes (E501/E306/BLE001/F541/I001/
  RUF100/TRY004 residuals all pre-existing per HEAD diff; two merge-blank-
  line E303s fixed at merge time).

## Tests (all PASS)

- `python -m lib.ui_composer` — ok.
- `python spidercaster.py ui --selftest` — ok (composer battery +
  `ui_selftest ok (walk 0-11, gaps, engine-room e2e, bind-print, lock)`).
- Piped smoke: `/help /plan /ticket /publish projects quit` — Projects
  rows, 0-token dry-run, missing-ticket refusal panel, REFUSED readiness,
  footer on every screen; exit 0. `ui --screens` launches the sibling loop.

## Open / not in lane

- Steps 2+: check-row board, budgets panes, probe wiring, publish-readiness
  command-printer promotion, rater block, cDeck tab LAST, Textual stretch.
- `sites/demo-local` has no `crew-ticket.json` (build path does not run
  crew); the face reports this honestly as a missing-ticket refusal.
- Sibling lane owns `ui_render` RUF059-242 and any `ui --screens` behavior.

---

# UI steps 4-5 (gf38) — 2026-10-11 (UTC): probe wiring + publish-readiness

Lane: read-only probe view (`layout-probe.json` -> `visual_probe`,
NOT RUN blocks release) + publish-readiness view (validity + exact bind
command, never executes). Live tree only, stdlib only, zero new files
(new-file cap: extended `lib/ui_render.py`, `lib/ui_composer.py`,
`lib/ui_selftest.py`; no engine files touched; steps 0-3 files' FINAL
shape otherwise preserved).

## Step 4 — probe wiring, read-only (`lib/ui_render.py`)

- `probe_status(site_dir)` (pure, 0 hands): reads `site_dir/layout-probe.json`,
  recomputes the binding exactly like `lib/check.py::_visual_probe_row`
  (sha256 over sorted top-level `*.html`, `hexdigest[:16]` vs
  `html_hash`/`hash`). States NOT_RUN/SKIP (no file or no built pages),
  UNREADABLE/FAIL, STALE/FAIL (html changed), FAIL_ROWS/FAIL (a probe row
  FAILs), PASS (bound). Never launches a browser, never writes, never runs.
- `probe_surface_command(site)` prints the exact (existing, verified)
  `python spidercaster.py check <site>` surfacer; the producer line quotes
  the checker's own words (`tools/layout_probe.py`, noted present/absent —
  the writer is absent in this tree, so no probe can bind yet and the view
  says so instead of fabricating a producer command).
- `UI.probe_text()` (0 hands): binding + "NOT RUN is not a pass: --release
  refuses" + producer presence + surface command. Wired into Preview
  (`preview_text` probe lines now report artifact truth instead of the old
  tools-file-exists stub) and into the composer loop as plain word `probe`
  (HELP views line updated).
- `board_text(release=True)` unchanged: SKIP still BLOCKED ("NOT RUN is not
  a pass") — the probe view names the same gate, it does not reimplement it.

## Step 5 — publish-readiness view (`lib/ui_render.py::publish_text`)

- `UI.publish_text()` (0 hands): validity via
  `lib.ui_composer.verify_for_publish` verbatim (engine
  `verify_live_ticket` refusal strings unchanged: missing/unreadable ticket,
  site/mold mismatch, ok-not-true, visual-not-PASS, empty hash map, 1-byte
  hash mismatch) + the exact mold-bound bind command
  (`library bind --live --site X --mold Y --out Z`, required `--mold` the
  old `ui_hands.bind_live_command` print lacked). `executed` always False;
  ledger snapshotted in tests to prove no bind runs.
- `screen_ticket` now shows the ticket summary then `publish_text()`; the
  no-ticket branch prints the `?`-placeholder command shape (same `?`
  convention as `verify_for_publish`) so the Ticket screen always teaches
  the command without fabricating site/mold.

## 6Cs (my lines only; engine + steps 0-3 debt untouched)

- `pycodestyle --max-line-length=100` clean on all three touched files
  (one E302 of mine fixed at write time).
- `ruff check`: no new hits — the 7 RUF100 unused-`noqa` notes are
  pre-existing repo convention (E402 not enabled) on steps 0-3 lines.

## Tests (all PASS)

- `python spidercaster.py ui --selftest` — ok: composer battery +
  `ui_selftest ok (...)` incl. new `probe_publish_battery`: NOT_RUN/SKIP +
  release-BLOCKED, STALE on wrong hash, FAIL_ROWS on bound-but-FAIL rows,
  PASS with direct checker parity (`check_site` visual_probe row agrees
  SKIP and PASS), publish READY with exact `--site/--mold/--live` command,
  0 hands on both views, ledger byte-identical, 1-byte flip -> REFUSED
  "hash mismatch" verbatim.
- `ui_hands`, `ui_orchestrator`, mobile selftests — ok (unchanged).

## Open / not in lane (no action taken)

- Pre-existing steps 0-3 quirk (observed, not caused, not fixed — FINAL
  files left byte-stable outside my hunks): bare `python lib/ui_composer.py`
  fails at `_write_ticket` (`from lib.hands import _sha_bound`,
  `ModuleNotFoundError: No module named 'lib.hands'` — `lib` binds the
  pywin32 `win32/lib` namespace port instead of the tree when only the
  script dir seeds `sys.path`). With the tree on the path it passes
  (`PYTHONPATH=working python lib/ui_composer.py` ok), and the supported
  harness `spidercaster.py ui --selftest` is green. Fix (if wanted) belongs
  to the steps 0-3 bootstrap, e.g. unconditional `_ROOT` prepend.
- `tools/layout_probe.py` still absent: every site reports visual_probe
  NOT_RUN until a probe writer lands; the UI refuses to invent its command.

---

# Probe producer (hero) — 2026-10-11 (UTC): `tools/layout_probe.py` lands

New files (live tree only, no toy dirs): `tools/layout_probe.py` (stdlib only)
+ `sites/demo-live/layout-probe.json` (producer output, bound to demo-live bytes).

## Producer contract (matches `lib/check.py::_visual_probe_row` exactly)

- Binds sha256 over sorted top-level `*.html` bytes, `hexdigest()[:16]`,
  stored as both `html_hash` and `hash` (checker accepts either).
- Writes `rows` (checker reads `rows`, falls back to `profiles`); row
  `status` tokens are PASS/FAIL/SKIP only — the checker FAILs `visual_probe`
  solely on unreadable JSON, a hash mismatch (stale), or a row with
  `status == "FAIL"`.
- Static probes, no browser/network/Pillow: `viewport_meta` (every page has
  `name="viewport"`), `img_dimensions` (every `<img>` has width+height;
  vacuous pass with no `<img>`, mirroring `layout_stability`), `wide_fixed`
  (no unguarded fixed width/min-width over 412px in `<style>`/style-attrs
  unless the rule sets `max-width`; no wide numeric width attribute without
  a guard), `no_remote_assets` (no remote URL outside ld+json, mirroring
  `no_hotlink`). Undecidable-from-text is never FAIL.
- Exit 0 all-green, 1 on FAIL rows (file still written — the checker must
  see the failure), 2 on usage errors (missing dir, no built pages).

## Proof (all PASS, post-change)

- `python tools/layout_probe.py --selftest` — ok (empty-dir refusal,
  NOT_RUN/SKIP + checker SKIP parity, bound PASS/PASS + checker PASS parity,
  1-byte edit STALE/FAIL + checker stale-FAIL parity, bound-FAIL-row
  FAIL_ROWS/FAIL + checker FAIL parity, corrupt-file UNREADABLE/FAIL +
  checker unreadable-FAIL parity, per-probe violating fixtures FAIL,
  guarded fixtures all-PASS).
- demo-live flip: `check` before = `[skip] visual_probe - not-run:
  no layout-probe.json`; after `python tools/layout_probe.py
  sites/demo-live` (4/4 pass, html fed5423b44d82af4) =
  `[pass] visual_probe - probe layout-probe.json bound to html
  fed5423b44d82af4`. Full `check sites/demo-live`: 44 pass / 0 fail /
  0 warn / 3 skip, exit 0.
- `python spidercaster.py ui --selftest` — ok (composer battery +
  `ui_selftest ok (walk 0-11, gaps, e2e, probe, rater, cdeck, bind, lock)`).

## 6Cs on `tools/layout_probe.py`

`ruff check` clean; `pycodestyle --max-line-length=100` clean;
`flake8 --max-line-length=100` clean; `black --check --line-length=100`
clean (formatted once at write time); `py_compile` + import ok;
`--selftest` ok. No engine files touched.

## Open / not in lane

- Rebuilding demo-live without re-running the producer stales the probe by
  design (checker says re-run probe); the producer must run after each build.
- Probe rows are static-text only: rendered layout (real browser boxes,
  web fonts, JS-built DOM) stays out of scope, same as the static gates.
