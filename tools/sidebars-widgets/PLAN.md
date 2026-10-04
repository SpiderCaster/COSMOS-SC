# Plan: sidebars and widgets slice

Date: 2026-10-03. Owner: SC Tools Sidebars Widgets.

## Conventions found

- Toolkit root `V:\streams\webdev` holds kits, skills, templates and handovers. The SpiderCaster engine and its tools live in `V:\A\Ai\spidercaster\working` (`lib`, `library`, `tools`, `bench`). Only `tools\a11y_scan.py` existed in `tools`. It is a standalone stdlib script with a docstring and exit code 1 on FAIL. This slice follows that style and sits in `tools\sidebars-widgets`.
- Wrapper rules (`kits\SPIDERCASTER_KIT\WRAPPER.md`, `skills\spidercaster\SKILL.md`): type floors 18 px body and buttons, 16 px menus and labels, contrast 4.5:1 on rendered pixels, px not rem on OceanWP (root is 62.5%), no invented content, no lorem or SAMPLE, secrets by name only, free-model discipline of small steps with a checker after each.
- Engine rules: Python 3.11+ stdlib only, offline, deterministic output, noindex by default. The bench (`bench\coldstart_bench.py`) reports PASS or FAIL with exact output per step. The harness here does the same per check.
- Library seeds name `sidebar` as a nav value. No sidebar or widget catalog existed. Sibling slices (headers, hooks and blocks, components and layouts) had no output folders yet, so no shared manifest schema was found. This slice defines its own and keeps field names plain so a later merge is a rename.
- Theme markup used for contexts: OceanWP `#right-sidebar.sidebar-container.widget-area` with `#right-sidebar-inner` (from the OceanWP `sidebar.php` in the session closeout copy); GeneratePress `#right-sidebar.widget-area` with `.inside-right-sidebar` and `aside.widget`.

## Build

1. Shared harness `_lib/harness.py`: lint, render, headless Chrome at 360 and 1280 px, two theme-like contexts, scripted behavior.
2. Sidebar layouts: right, left, three column, sticky right, sticky left, collapsible groups, mobile drawer.
3. Widgets: recent, popular, categories, archives, tags, search, TOC, author, related, newsletter stub, ad slot, social, share, contact, hours, call to action, post nav, back to top, tabs, FAQ, link list, notice, skip link.
4. Each item: manifest, fragment, CSS, optional JS, fixture, behavior test, test.py.
5. `run_all.py` runs all, writes status into manifests, and regenerates `catalog.json`, `CATALOG.md`, `COUNTS.md`.
6. `selftest.py` injects defects to show the tests fail when they should.

## Rules held

No thumbnails or art. No brand icons. Short active copy, no exclamation points. No keys or credentials. File weight budget per item, stated in the manifest. Nothing touches a live site.
