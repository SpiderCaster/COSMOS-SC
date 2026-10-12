# Checker status

## Checks added

`lib/check.py` `check_site` now fails closed on the built `index.html` and the favicon beside it. Existing type floors were not in this file (none to lower). Contrast checks were not in this file. `noindex_status` is unchanged. `internal_links` still walks `href` only; img src is a separate row, so a remote image does not double-fail that rule. A letter-mark hero has no `img` and passes `relative_img`.

| code | fail when |
| --- | --- |
| `site_header` | index has no class token `site-header`, or no script `classList.toggle` / `classList.add` of `is-stuck` |
| `hero_visual` | index has no class token `hero-visual` (CSS `.hero-visual` alone does not pass) |
| `favicon_link` | no single `<link>` with `rel="icon"` and `href="favicon.svg"` |
| `favicon_svg` | `favicon.svg` is missing beside `index.html`, or the file has no `<svg` |
| `relative_img` | index has an `img` whose src is `htt<local-path>`, `https://`, `//`, empty, or missing. No `img` passes. |

A missing `favicon.svg` also fails the existing `internal_links` row (`index.html: favicon.svg`), because that href does not resolve. That overlap was left in place.

Local probe (temp dir, not a publish): letter-mark page passed all five new rows and `noindex_status`. A relative `assets/hero.png` passed `relative_img` and `internal_links` with the file absent. `https://` and `//` img src failed only `relative_img`. Dropping the robots meta still failed `noindex_status`.

## Skill line fixed

`library/seats/graphics/SKILL.md`

- Start step 2 no longer says the project cannot be written. Vault stays unwritten. The only project write is one Keith-asked local image file.
- Risk tier no longer says "No downloads." A Keith-asked `python spidercaster.py image` may save one local file. The crew still must not hotlink, paste a provider URL, copy vault photos, or run image generation on every build.

`library/seats/visual/SKILL.md` was not edited. Its sentences stay true: `check_site` with `--expect-noindex`, any FAIL stops the crew.

## Commands and output (quote the ok lines or the error)

After `Start-Sleep -Seconds 90`, from `<repo-root>`:

```
hands selftest ok
HANDS_EXIT:0
crew selftest ok
CREW_EXIT:0
```

No second run. Neither command failed.

## Left for the parent (bugs you did not own)

- No render, hands, crew, or wrapper bug turned up. Those files were not edited.
- `lib/check.py` still has no type-floor row and no contrast row. Render still ships a few sizes under 1rem (`.8rem` form note, `.85rem` avatar, `.92rem` footer). Not changed.
- A missing `favicon.svg` fails both `favicon_svg` and `internal_links`. Remote img src does not.
