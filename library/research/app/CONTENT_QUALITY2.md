# CONTENT_QUALITY2

Scored on 2026-10-01 after `inbox/restage-harbor.md`, `inbox/restage-demo.md`, and `inbox/prose.md` each had a real DONE line. The first poll matched the word DONE inside the restage waiting sentences; those files were still STARTED. A second poll, every 30 seconds, waited for a line that is `DONE` or `STATUS: DONE`.

Both restage notes say they built before `prose.md` showed DONE. `prose.md` is DONE now. This score is the HTML on disk, not a new render. No publish. No HTML, lib, or copy edits.

Paths are under `<repo-root>`.

## What was on disk

| Path | On disk |
| --- | --- |
| `stage/demo/out/index.html` | yes |
| `stage/demo/src/copy/` (`overview.md`, `commands.md`, `faq.md`) | yes |
| `stage/harbor/out/index.html` | yes |
| `stage/harbor/src/copy/` (`overview.md`, `hours.md`, `menu.md`, `contact.md`) | yes |

`restage-harbor.md` says the HTML was not rewritten and that `prose.md` never showed DONE before that build. The harbor page below is the file that is present. `restage-demo.md` says the same about prose, and the demo page matches that note: description length 134, and two cheap bullets plus two house-rule bullets still split or cut.

## stage/demo/out/index.html

No copy file is absent. `overview.md`, `commands.md`, and `faq.md` all appear. The empty top heading `Commands` does not. Some wrapped bullets are split, and two wraps are missing.

### Sentences from the copy

Visible in full:

- Overview heading, title, `h1`, and brand: `SpiderCaster: websites from real copy, on free tokens`.
- First overview paragraph, as the hero lede, including every sentence through `Paid models join only when explicitly allowed.`
- Second overview paragraph, as the About body: `The engine follows the WebDev package rails: it never invents facts, prices or claims; output stays noindex until approved; secrets are read from environment variable names only; and every run writes a token ledger so the cost is auditable.`
- Cheap bullets that are one source line: `Deterministic assembly: layout, CSS, icons and pages are code, not tokens.` `Offline mode: a full draft with zero tokens, mapped straight from your copy.` `Hand edits are first-class: edit site.json directly and rebuild for free.`
- All four `## Build` lines, both `## Iterate` lines, and both `## Gate and preview` lines. Each is split on the colon into a heading and a body. Example body: `scaffold a project with brief.md and a copy folder.`
- House-rule lines that are one source line: `Noindex by default: pass --indexable only after a gate is signed.` `No hotlinking: external stock-photo URLs are dropped at ingest.`
- FAQ heading `Questions about the engine` and all five questions and answers, in the page and in the FAQPage JSON-LD. Example answer phrase: `No model is called.`

Visible only as a detached section lede, not inside the bullet:

- Cheap bullet wrap, used as the lede under `Why it is cheap`: `shape, with at most one JSON-repair retry.` The card stops at `produces the whole site`.
- House-rule wrap, used as the lede under `House rules the engine enforces`: `and the offline planner only uses text it was given.` The card stops at `your source copy,`.

Not on the page:

- Cheap bullet wrap: `few hundred tokens instead of a full build.` The card stops at `a revision costs a`.
- House-rule wrap: `OPENWORK_API_KEY. Values are never written to disk by the engine.` The card stops at `OPENROUTER_API_KEY,`.
- Nav label cuts the heading to `House rules the engine`. The `h2` itself is the full heading.

### Meta description

Yes. It is taken from the copy and it ends on a sentence. It is the first two sentences of `overview.md`, 134 characters, ending at `static site.` The same text is `og:description` and the WebSite JSON-LD description. Later sentences of that paragraph stay in the hero lede only.

### Invented award, review, or price

No award. No review. No quote block is filled. JSON-LD has no `aggregateRating`. No price was added. `zero dollars` in the FAQ is already in `faq.md`.

Chrome that is not in the copy, and is not an award, review, or price: heading `About`, button `Read on`, footer `(c) 2026` plus the overview title, and `Built with SpiderCaster`.

## stage/harbor/out/index.html

No copy file is absent. `overview.md`, `hours.md`, `menu.md`, and `contact.md` all appear. Hours are on the page.

### Sentences from the copy

Visible in full:

- Overview heading, title, `h1`, and brand: `Harbor Tea Room`.
- First overview sentence, as the hero lede: `A quiet tea room that seats walk-ins by the water.`
- Second overview sentence, as the About body: `Loose-leaf, brewed to order; decaf after 4pm on request.`
- Hours: `Open Tuesday to Sunday, 8am to 6pm.` and `Closed Mondays.`
- Menu lede: `12oz cups, brewed to order.`
- Menu rows, name and price split: `Jasmine Pearl` `$4.50`, `Assam Malt` `$3.75`, `Peppermint Field` `$3.25`.
- Contact lines: `14 Harbor Lane` in the address row, `(555) 014-2288` in the phone row, and `Walk-ins only; no reservations needed.`

The walk-ins sentence is visible, but the contact lede glues the phone onto it with only a space: `(555) 014-2288 Walk-ins only; no reservations needed.` The phone is also in its own row. The section heading `Menu` is repeated as an `h3`.

### Meta description

Yes. It is one complete sentence from the copy: `A quiet tea room that seats walk-ins by the water.` The same text is `og:description` and the WebSite JSON-LD description.

### Invented award, review, or price

No award. No review. No quote block is filled. JSON-LD has no `aggregateRating`. The three prices are the three lines in `menu.md`. No other price was added.

Chrome that is not in the copy, and is not an award, review, or price: heading `About`, button `Read on`, footer `(c) 2026 Harbor Tea Room`, and `Built with SpiderCaster`. The second button label `Contact` is the copy heading.

## Engine changes

These keep facts inside the copy. They do not add marketing lines. At most five.

1. Join an indented continuation into the open bullet before planning. Do not store that wrap as a paragraph, do not use it as the section lede, and do not drop a later wrap. On the demo page the lost tails are `few hundred tokens instead of a full build.` and `OPENWORK_API_KEY. Values are never written to disk by the engine.`
2. Do not title an untitled overview paragraph `About`. Neither copy file has that heading.
3. Do not emit `Read on`, a copyright year, or `Built with SpiderCaster` unless the copy states them.
4. On contact, do not join the phone paragraph to the next sentence. `Walk-ins only; no reservations needed.` is already its own line, and the phone already has a row.
5. Nav labels should keep the full copy heading. The 28-character cut turns `House rules the engine enforces` into `House rules the engine`.
