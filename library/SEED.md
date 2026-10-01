# SpiderCaster Library — seed

Live root: `V:\streams\webdev`. Paths below are relative to that root.

Unique templates are the SEO rule. A fleet of sites on one host must not wear one OceanWP demo or one GeneratePress starter. The vendor catalogs under `templates/owp` and `templates/gp` stay on disk as frames to permute. They are not the library, and they are not pulled further.

The library grows when a build diverges: palette, type-lead, and nav pattern, then a checker pass. Record the new permutation here. Do not snapshot the 160 OceanWP demos or the 50 GeneratePress starters.

Machine list: `seed.json`.

## Seeds

| Id | What it is | Where | Used by |
|---|---|---|---|
| warmth-authority | Static mold. Serif, teal/amber, segmented audience nav. | `templates/static-molds/mold-warmth-authority` and the pages in `builds/movelixir.com` | movelixir.com |
| teavital-owp | OceanWP yoga frame, permuted onto teavital. Checker pass 2026-09-27 17:39. Later live origin and public check failed. | `environments/owp-sandbox/sites/teavital-owp` | teavital.com |
| teavital-gp | GeneratePress Lifestyle frame. Checker pass 2026-09-27 17:25. Local only. | `environments/owp-sandbox/sites/teavital-gp` | teavital.com (not the live face) |
| teavital-block | Block theme, pages from copy. Checker pass 2026-09-27 17:25. | `environments/owp-sandbox/sites/teavital-block` | none yet |

## On disk, not yet a permutation

These still wear the parent demo. They become seeds when palette, type, and nav diverge and the checker passes.

- `floelixir-gp-marketer` — GeneratePress Marketer
- `floelixir-owp-simpleblog` — OceanWP simpleblog
- `owp-photos` — OceanWP photos, checker failed

`floelixir-gp-restored-v2`, `floelixir-owp-restored-v2`, `clone-test-simpleblog`, and `master` are restore and clone machinery. `template-cardhub`, `template-split`, `template-story`, and `template-wellness` are empty directories.

## Next entry

One new site, one new permutation. Append a row and a `seeds` object. Name the parent frame and the three things that changed.
