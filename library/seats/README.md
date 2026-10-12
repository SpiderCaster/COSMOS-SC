# SpiderCaster seats

Seven seats, one site, in this order. Hands and stop rules: [CREW.md](../CREW.md). Commands run from `V:\a\Ai\spidercaster\working`. Load that seat's `WRAPPER.md`, then its `SKILL.md`.

| # | Seat | Model | Hands |
|---|---|---|---|
| 1 | architect | `upstage/solar-pro4` | brief_read, frame_pick, mold_pick, library_bind |
| 2 | content | `upstage/solar-pro4` | copy_read, copy_gap |
| 3 | frontend | `upstage/solar-pro4` | plan_offline, render |
| 4 | graphics | `google/gemma-4-31b-it` | asset_list, vault_photos |
| 5 | visual | `google/gemma-4-31b-it` | check_site |
| 6 | seo | `deepseek/deepseek-v4-flash` | uniqueness, meta_basics |
| 7 | deployer | `deepseek/deepseek-v4-flash` | ticket_write |

No seat publishes. Do not put secrets, key values, or account tokens in any file.

## Vault vs package

Vendor OceanWP and GeneratePress demos and photos live only in the private vault `V:\streams\webdev\vendor-vault` (`SPIDERCASTER_VAULT`). Never copy them into this package.
A site wears at most one vendor frame, and only as the parent of a mutation. A mix cites two or more parents and is not an as-is vendor frame. Scratch has no vendor parent.
Package molds are scratch, mutate, or mix. A mutation changes palette (`#rrggbb`), type-lead (`serif`, `sans`, `slab`, `mono-display`), and nav (`segmented`, `top-bar`, `sidebar`, `one-page`, `footer-only`).
A mold or vendor frame already live on one site is refused on a second live site. The human publish click is in CREW.md.
