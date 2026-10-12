# Phone pass 2

Read-only, 2026-10-01. Not published. Stage HTML, Python, and `lib/` were not edited.

`stage/demo/out/index.html` contains `.points .pt + .pt{border-top:1px solid var(--line)}`, so this pass did not stop. `stage/harbor/out/index.html` has the same declaration. A 390px width is inside `@media(max-width:860px)`. `.wrap{padding:0 16px}` leaves a 358px column. `html` is 18px. This is stylesheet arithmetic, not a browser capture.

No new words. No publish.

## Closed

These are in the current HTML. They are not open defects.

- Photo hero, both stylesheets: `.hero-visual{...aspect-ratio:16/9;height:auto...}`. Harbor's only image is `<img src="assets/hero.png" alt="Harbor Tea Room" width="1280" height="720" ...>`.
- Letter mark, inside the phone block: `.hero-visual.hero-mark{aspect-ratio:2/1;height:auto;max-height:120px}`. Demo hero is `<div class="hero-visual hero-mark" aria-hidden="true"><span>S</span></div>`.
- Neither file contains `height:168px` or `about-panel`.
- Phone rule: `.reveal{opacity:1;transform:none}`. Skip link: `<a class="skip" href="#main">Skip to content</a>` and `<main id="main">`.
- Harbor `main` order is hero, about, hours, menu, contact. One hero button on each page. Harbor `href="#hours"`. Demo `href="#features"`.
- Harbor has `<a class="phone-bar" href="tel:5550142288">(555) 014-2288</a>`. Demo has the `.phone-bar` rule and no `phone-bar` element.
- Phone `.nav-here{display:block;flex:0 1 auto;max-width:4.5rem;...}` and `.nav-here:empty{display:none}`. The script clears the label when it matches the brand: `if(brand&&label===brand.textContent)label='';here.textContent=label;`
- Phone `h1,h2{text-wrap:balance;overflow-wrap:break-word}`, `.mi-price{font-variant-numeric:tabular-nums}`, and `.card:hover{transform:none;box-shadow:none}`.
- Phone `.card:has(.chip){display:grid;grid-template-columns:32px minmax(0,1fr);...}` and `.grid.c3{gap:0;...border:1px solid var(--line);...}` with `.grid.c3 .card + .card{border-top:1px solid var(--line)}`.
- Phone `.points{gap:0;...border:1px solid var(--line);...}` and `.points .pt + .pt{border-top:1px solid var(--line)}`.

## Defect

None. The phone CSS defects listed above are closed. Nothing else in the current HTML makes a 390px page look broken: no second nowrap label splitting the header, no fixed hero height, no empty panel, no hover jump on cards, no separate card shells, no separate point rows.

The remaining thinness is the copy length.

Harbor, under the one photo: `#about` is one sentence, "Loose-leaf, brewed to order; decaf after 4pm on request." Hours is two sentences. Menu is three `.menu-item` rows, `.mi-name` and `.mi-price` only. There is no `.mi-desc`. There is no second `img`.

Demo: no `img`. Thirteen `.card` blocks are one `h3` and one `p`. Iterate and Gate and preview are two `.pt` rows each. Questions about the engine is not part of that thinness. Its five answers are longer than one sentence.

## Next CSS edits

None.
