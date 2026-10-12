# Phone type

Seat card for type size. Read-only record of `CSS_TEMPLATE` in `lib/render.py` on 2026-10-01. Machine rules: `library/rules/phone-type.json`, schema `spidercaster-phone-type/1`. No new hands. Seat skills were not edited. Python, `stage/`, and `lib/` were not edited. This card does not publish.

Root is `html{font-size:18px}`. **1rem = 18px.** The `@media (max-width:860px)` block does not change these sizes. `.hero--bold h1` uses the same 1.7rem floor.

## Measured

| What | In the template | Arithmetic | About |
| --- | --- | --- | --- |
| html font-size | `18px` | given | 18px |
| body line-height | `1.6` | `1.6 × 18` | 28.8px line box |
| h1 clamp | `clamp(1.7rem, 5.5vw, 3.9rem)` | `1.7 × 18 = 30.6`; `3.9 × 18 = 70.2` | 30.6px to 70.2px |
| h1 bold clamp | `clamp(1.7rem, 8vw, 4.2rem)` | `1.7 × 18 = 30.6`; `4.2 × 18 = 75.6` | 30.6px to 75.6px |
| h2 clamp | `clamp(1.6rem, 3vw, 2.3rem)` | `1.6 × 18 = 28.8`; `2.3 × 18 = 41.4` | 28.8px to 41.4px |
| .lede size | `1.08rem` | `1.08 × 18 = 19.44` | 19.44px |
| .lede measure | `max-width:62ch` | present | 62ch |
| button font-size | `.btn` `1rem` | `1 × 18 = 18` | 18px |
| footer font-size | `.site-footer` `1rem` | 1 times 18 = 18 | 18px (was .92rem, raised 2026-10-03) |
| inputs | `font:inherit; font-size:max(16px,1rem)` | `max(16, 18) = 18` | 18px |

`5.5vw` drops under `1.7rem` once the viewport is under `30.6 / 0.055 = 556px`. A phone then sits on the 30.6px h1 floor, not on `5.5vw`. `3vw` stays under the h2 floor until `28.8 / 0.03 = 960px`, so a phone h2 is 28.8px.

## Rules

Seven rules. **Enforced 7. Pending 0.** A rule is enforced only when this template already matches.

- `root_18` enforced. `html{font-size:18px}` is present.
- `body_line_height` enforced. `1.6` is at least `1.5`.
- `h1_phone_floor` enforced. Both h1 clamp minima are `1.7rem`, not above `2rem`, so a long title can fit. `h1` also sets `overflow-wrap:anywhere`.
- `lede_measure` enforced. `.lede` has `max-width:62ch`.
- `button_18` enforced. Buttons are `1rem` (18px).
- `footer_floor` enforced. `.site-footer` and `.credit` are `1rem` = 18px (raised 2026-10-03 from `.92rem` = 16.56px; no text in the template is under 18px). `.credit` no longer uses opacity.
- `input_16` enforced. Inputs set `font:inherit` and `font-size:max(16px,1rem)`. `font:inherit` counts as enforced because the root is 18px. `max(16px, 1rem)` is 18px, so a phone does not zoom the page on focus.

## Public

`https://design-system.service.gov.uk/styles/typography/` was opened on 2026-10-01. It returned a page-not-found page. **Not public.** No quote from that address.

Opened `https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html` (Understanding SC 1.4.12 Text Spacing, Level AA). The success criterion lists: "Line height (line spacing) to at least 1.5 times the font size." The same page says content is not required to use those spacing values; the requirement is that an override must not lose content or functionality. This card does not claim a WCAG audit. The template's authored body line-height is already `1.6`.

## Seats

Frontend renders this CSS through `render`. Visual may read the rule file. This card adds no hand and does not change a seat skill.
