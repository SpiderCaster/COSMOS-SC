# COUNTS

Updated 2026-10-03 21:06 Central Daylight Time by run_all.py.

| Measure | Count |
|---|---|
| Items built | 30 (7 sidebar layouts, 23 widgets) |
| Tested, pass (static and browser) | 30 |
| Tested, fail | 0 |
| Static checks only, no browser run | 0 |
| Not yet tested | 0 |

A pass means every check passed: manifest, tokens, HTML, CSS and JS lint, secret scan, size budget, then headless Chrome at 360 px and 1280 px in two theme-like contexts (tap targets 44 px, text 16 px and 18 px floors, 4.5:1 contrast, no horizontal overflow, scripted behavior).
The contexts are approximations written for these tests. No item has run on a real OceanWP or GeneratePress install yet.
