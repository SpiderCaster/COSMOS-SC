# Phone cards

Read-only, 2026-10-01. Not applied. Not published. Stage HTML, Python, and `lib/` were not edited.

Read: `V:\a\Ai\spidercaster\working\stage\demo\out\index.html`. It contains `h1,h2{text-wrap:balance;overflow-wrap:break-word}` inside `@media(max-width:860px)`, so this pass did not stop. A 390px width is inside that block. `.wrap{padding:0 16px}` leaves a 358px column. `box-sizing` is `border-box`. A full-width `.card` is 358px, with 14px padding and a 1px border, so the content box is 328px. `html` is 18px. `h3` is 1.12rem (20.16px) at line-height 1.15. Body line-height is 1.6. This is not a browser capture.

Thirteen `.card` blocks are one `h3` and one `p`, each already wrapped by a `.chip` that holds an inline `svg.icon`. Build has 4, House rules the engine enforces has 4, Why it is cheap has 5. Phone rules already set `.card{padding:14px}`, `.card:hover{transform:none;box-shadow:none}`, `.chip{width:32px;height:32px;margin-bottom:8px}`, `.grid{gap:8px}`, `.card h3{margin-bottom:4px}`, and `.c3{grid-template-columns:1fr}`. `--radius` is 22px. `.card p` is already `color:var(--muted);margin:0`. No new sentence, no new icon, and no photo.

Opened https://design-system.service.gov.uk/components/summary-list/. That page loaded. It says a summary list is a short key plus its value, that borders join the information on each row, and that several lists of the same kind can sit under a heading or inside a summary card. No vendor stylesheet is copied below.

## Ideas (4)

All four belong in the existing `@media(max-width:860px)` block, after the card rules already there. Desktop cards stay as they are.

### 1. Sit the existing chip beside the two lines

The chip is already in the card. On a 328px content box it currently stacks above the heading, so a one-sentence card is a 32px badge over a short pair and empty corners.

```css
.card:has(.chip){display:grid;grid-template-columns:32px minmax(0,1fr);column-gap:12px;align-items:start}
.card:has(.chip) .chip{grid-row:1 / span 2;margin-bottom:0}
.card:has(.chip) h3,.card:has(.chip) p{grid-column:2}
```

The text column is 284px (328 minus the 32px chip and the 12px gap). `:has(.chip)` leaves a card with no chip as a single column. The page already uses `:has` for `.phone-bar`. Do not add an icon.

### 2. Make each `.grid.c3` one summary shell

Eight pixels of gap plus a 22px radius on every short card reads as thirteen separate lozenges. The section `h2` is already the group label.

```css
.grid.c3{gap:0;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.grid.c3 .card{background:transparent;border:0;border-radius:0;box-shadow:none}
.grid.c3 .card + .card{border-top:1px solid var(--line)}
```

12px matches `.chip` and `.nav-toggle`. One shared edge joins a heading to its sentence. Section rules, `.about-body`, and `.menu-item` borders stay.

### 3. Balance the card heading the way `h1,h2` already do

`text-wrap:balance` is on `h1,h2` only. Card titles such as `forge build --from SITE/site.json` are long enough to wrap in the 284px column from idea 1.

```css
.card h3{text-wrap:balance;overflow-wrap:break-word}
.card p{text-wrap:pretty}
```

`overflow-wrap:break-word` is the same companion already used on `h1,h2`. `text-wrap:pretty` only changes the wrap of the sentence that is already in the `p`.

### 4. Close the pair with the existing line color

The phone block sets `.card h3{margin-bottom:4px}`. Four pixels and no edge leaves the sentence looking unattached. Place this after that rule.

```css
.card h3{margin-bottom:0}
.card p{margin-top:8px;padding-top:8px;border-top:1px solid var(--line)}
```

With idea 1, the line stays in column 2 and does not cut the chip. The color is the `--line` token already on the page.
