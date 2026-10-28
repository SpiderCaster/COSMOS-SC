# Phone thinness that remains

Read-only, 2026-10-01. Not published. Stage HTML, Python, and `lib/` were not edited.

Read: `V:\a\Ai\spidercaster\working\stage\harbor\out\index.html` and `stage\demo\out\index.html`. Both are the sheet rebuilt after the phone CSS pass. A 390px width is inside `@media(max-width:860px)`. From that sheet, `.wrap{padding:0 16px}` leaves a 358px column. `html` is 18px and `body` line-height is 1.6. That is stylesheet arithmetic, not a browser capture.

No new copy, prices, or reviews are proposed below. Words in quotes are already on the page.

## Not open

These are already in the rebuilt files. They are not remaining reasons.

- No `height:168px`. `.hero-visual` is `aspect-ratio:16/9;height:auto`.
- No `about-panel` class and no empty about panel in the body.
- The phone rule is `.reveal{opacity:1;transform:none}`. It overrides the base `.reveal{opacity:0}`.
- The skip link is present: `<a class="skip" href="#main">Skip to content</a>`.
- The harbor hero image has `width="1280"` and `height="720"`.

`.nav-here` is `display:block` under 860px, not hidden. Harbor's hero is a photo, not a letter. Demo has no Contact, Hours, or Menu section, so the contact-order reason is harbor only.

## Remaining reasons (8)

### Both

1. Class rule `section{padding:32px 0}`, and no divider.

Inside `@media(max-width:860px)` both files set `section{padding:32px 0}`. That is 32px above and 32px below the block. The only `border-top` in either file is `.site-footer`. There is no `hr` and no rule on `section` or `.sec` that draws a line. `.sec-head{margin-bottom:28px}` is outside the phone query, so a heading adds another 28px. On a one-sentence or two-sentence block, the padding is taller than the text, and the sections run together.

Harbor headings that carry `.sec-head`: Contact, Hours, Menu. Demo headings that carry it: Build, Iterate, Gate and preview, House rules the engine enforces, Questions about the engine, Why it is cheap.

### Harbor

2. No second image under `.hero-visual`.

The only `img` is the hero:

`<img src="assets/hero.png" alt="Harbor Tea Room" width="1280" height="720" sizes="100vw" fetchpriority="high" decoding="async">`

`#about`, `#contact`, `#hours`, and `#menu` have no `img`. The body has no `.gallery` and no `.tile`. The 16/9 box is a photo. Everything under it is type. The staged harbor assets folder has `hero.png` only. There is no second local image to place.

3. Heading Contact comes before Hours and Menu.

Section order in `main`: `hero`, `about`, `contact`, `hours`, `menu`. The nav matches: Contact, then Hours, then Menu. On a 390px phone the first headed block after the short about is Contact, not the menu.

4. The blocks under the photo are short text.

- `#about` has no `h2`. Class `.about-body` is one sentence: "Loose-leaf, brewed to order; decaf after 4pm on request."
- Heading Hours. The same class `.about-body` is two sentences: "Open Tuesday to Sunday, 8am to 6pm." and "Closed Mondays."
- Heading Menu. Three `.menu-item` rows, each `.mi-name` and `.mi-price` only: Jasmine Pearl, Assam Malt, Peppermint Field. The file has no `.mi-desc`. Phone CSS sets `.menu-item .dots{display:none}`, so each row is the name and the price.

Body class `tpl-modern` centers `.sec-head`, so Hours and Menu sit as a centered heading over those short lines. Those words are the copy. They are not a missing paragraph to invent.

### Demo

5. Class `.hero-mark` is the letter S, not a photo.

`<div class="hero-visual hero-mark" aria-hidden="true"><span>S</span></div>`

The file has no `img`. `stage/demo/out/` has no image file. The phone rule `.hero-visual.hero-mark{aspect-ratio:auto;height:auto;max-height:140px}` caps the box. The first screen is a letter on the gradient, then the heading.

6. Class `.lede` is one long paragraph.

The hero has one `<p class="lede">` under the `h1`. It starts "SpiderCaster is a copy-driven static website engine." and runs on through "Paid models join only when explicitly allowed." Five sentences, one block. The hero has no bullets and no picture.

7. Class `.card` is a single sentence, thirteen times.

The phone rule `.c3,.c2,...{grid-template-columns:1fr}` stacks them to the full column. Each card is class `card` (`padding:22px`) plus a `.chip` (40px) plus one `p`.

- Heading Build: 4 cards. Example `h3` "forge init PROJECT" and "scaffold a project with brief.md and a copy folder."
- Heading House rules the engine enforces: 4 cards.
- Heading Why it is cheap: 5 cards.

8. `#about` and the two point sections are one short stack each.

- `#about` has no `h2`. Class `.about-body` is one paragraph, starting "The engine follows the WebDev package rails".
- Heading Iterate: class `.points`, two `.pt` rows.
- Heading Gate and preview: class `.points`, two `.pt` rows.

Heading Questions about the engine is not in this list. Its five `details` answers are longer than one sentence. That section is not a remaining thin reason.

## Next edits

Not done here. At most five. No new sentences, prices, or reviews. No remote image. Do not publish.

1. CSS only, inside the existing `@media(max-width:860px)` block on both pages. Lower `section{padding:32px 0}`. Add `section.sec{border-top:1px solid var(--line)}`. Lower `.sec-head` `margin-bottom` in that same block. `--line` is already on the page. Do not change any words.

2. Harbor markup order only. Move the existing `#contact` section so it follows `#menu`, and move the Contact nav link to after Menu. Keep the heading Contact, the phone, the address, and the lede that are already there.

3. CSS only, demo, inside `@media(max-width:860px)`. Reduce `.card` padding and the `.chip` box so a one-sentence card is not mostly chrome. Leave every `h3` and `p` as written. Leave the one-column phone grid.

4. Demo hero `.lede` only. Split that paragraph into the sentences already in it. Do not add words. Do not replace `.hero-mark` with an image URL. There is no local image in `stage/demo/out/`.

5. CSS only, demo, inside `@media(max-width:860px)`. Reduce `.points` `margin-top` (it is 16px) so Iterate and Gate and preview do not add a second gap on top of the section padding. Do not add commands. Do not add an About heading on either page. The copy has no About title. Do not write menu descriptions. Harbor's three prices stay as they are.
