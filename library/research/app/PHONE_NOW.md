# Phone now

Read-only, 2026-10-01. Not published. Stage HTML, Python, and `lib/` were not edited.

Read: `V:\a\Ai\spidercaster\working\stage\harbor\out\index.html` and `stage\demo\out\index.html`. Both are the sheet rebuilt after the phone passes. A 390px width is inside `@media(max-width:860px)`. `.wrap{padding:0 16px}` leaves a 358px column. `html` is 18px and `body` line-height is 1.6. Widths below are that column plus a Segoe UI measurement of the strings already on the page (the body stack names Segoe UI). This is not a browser capture.

No new copy and no remote image are proposed below.

## Not open

These are already in the rebuilt files.

- Photo hero: `.hero-visual{aspect-ratio:16/9;height:auto}`. Harbor's only image is `<img src="assets/hero.png" ... width="1280" height="720">`.
- Letter mark, inside the phone block: `.hero-visual.hero-mark{aspect-ratio:2/1;height:auto;max-height:120px}`.
- No `height:168px`. No `about-panel`.
- Phone rule: `.reveal{opacity:1;transform:none}`.
- `<a class="skip" href="#main">Skip to content</a>` and `<main id="main">`.
- Harbor `main` order is hero, about, hours, menu, contact. The nav is Hours, Menu, Contact.
- One hero button on each page. Harbor `href="#hours"`. Demo `href="#features"`.
- Harbor `<a class="phone-bar" href="tel:5550142288">(555) 014-2288</a>`. Demo has no `phone-bar` element.
- Phone rules: `section.sec{border-top:1px solid var(--line)}`, `.menu-item{...border-bottom:1px solid var(--line)}` with `.menu-item:last-child{border-bottom:0}`, and `.about-body{border-left:3px solid var(--accent);padding-left:12px}`.

## Defects (6)

### 1. Both — the phone header splits one title in half

Inside `@media(max-width:860px)` both files set `.nav{flex-wrap:nowrap}`, `.brand{flex:1 1 auto;min-width:0}`, and `.nav-here{display:block;flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}`. `.brand-name` is also `white-space:nowrap` with ellipsis. `.nav-toggle` is 44px. `.nav` gap is 12px. The script copies the visible heading into the label:

`var h=en.target.querySelector('h1,h2');here.textContent=h?h.textContent:'';`

On the hero that string is the brand.

- Harbor brand and `h1` are both `Harbor Tea Room`. Measured: brand text 168.6px at 1.05rem bold, plus `.brand-mark` 28px and its 10px gap, plus the label 151.0px, plus the 44px toggle and two 12px gaps. That is about 426px in a 358px row, so both nowrap labels ellipsize.
- Demo brand and `h1` are both `SpiderCaster: websites from real copy, on free tokens` (493.4px bold, 439.1px regular). The two flex items share the 290px left after the toggle and the gaps, so the bar shows two stubs of the same title. The `h1` below repeats it.

`.nav-here:empty{display:none}` does not help. The hero has an `h1`, so the label is not empty on the first screen.

### 2. Both — the phone block never overrides the spacing under short blocks

The phone block sets `section{padding:20px 0}`, `.sec-head{margin-bottom:12px}`, `.card{padding:14px}`, and `.chip{width:32px;height:32px;margin-bottom:8px}`. It does not set these, which are still the base rules:

- `p{margin:0 0 14px}`. Harbor `#about` is one `p` inside `.about-body`, so the accent bar includes a 14px empty tail under the sentence. The same tail sits under the second Hours sentence.
- `.hero .lede{margin-bottom:18px}`. Demo's hero is five `<p class="lede">` in a row, so that 18px repeats five times. Specificity beats the `p` margin.
- `.menu-group{margin-bottom:28px}`. Harbor's menu is one `.menu-group` of three rows. The phone block does not reduce this. Demo's stylesheet has the rule and no `.menu-group` in the body.
- `.grid{display:grid;gap:16px}` and `h3{margin:0 0 12px}`. Demo's phone cards still use both. `.card p{margin:0}` already clears the paragraph margin inside a card.

### 3. Harbor — the copy under the photo is short

`#about` has no `h2` and one sentence: "Loose-leaf, brewed to order; decaf after 4pm on request." Hours is two sentences. The three `.menu-item` rows are `.mi-name` and `.mi-price` only. There is no `.mi-desc`.

### 4. Harbor — there is no second photo

The only `img` is `assets/hero.png`. `#about`, `#hours`, `#menu`, and `#contact` have no `img`.

### 5. Demo — there is no photo

The file has no `img`. The hero is `<div class="hero-visual hero-mark" aria-hidden="true"><span>S</span></div>`.

### 6. Demo — the cards and the two command blocks are short

`#about` has no `h2` and one `p`. Thirteen `.card` blocks (Build 4, House rules the engine enforces 4, Why it is cheap 5) are each one `h3` and one `p`. Iterate and Gate and preview are two `.pt` rows each. Questions about the engine is not in this list. Its five answers are longer than one sentence.

## Next edits

Not done here. No new words. No remote image. Do not publish. Do not remove the borders, the 16/9 photo, the letter-mark cap, or the phone-bar.

1. CSS only, both pages, inside the existing `@media(max-width:860px)` block. Change `.nav-here` from `flex:1 1 auto` to `flex:0 1 auto;max-width:4.5rem`. Keep `display:block`, the ellipsis, and `white-space:nowrap`. Do not set `.nav-here` to `display:none`. Leave `.nav-toggle` at 44px. At the 18px root, 4.5rem is 81px, which is enough for the measured "Contact" label (69.4px) and leaves the Harbor brand its measured width instead of half the row.

2. CSS only, both pages, in that same block. Add `.about-body p:last-child{margin-bottom:0}`, `.hero .lede{margin-bottom:8px}`, `.menu-group{margin-bottom:0}`, `.grid{gap:8px}`, and `.card h3{margin-bottom:4px}`. Leave `section{padding:20px 0}` as it is.

3. Checker only. Fail when the phone block's `.nav-here` rule still contains `flex:1 1 auto`. Fail when that block does not override `.menu-group` margin-bottom and `.hero .lede` margin-bottom. Do not fail because a paragraph is one sentence or because a second image is absent.
