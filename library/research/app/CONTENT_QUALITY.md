# CONTENT_QUALITY

Scored after a three-minute wait on 2026-10-01. Only files on disk. No publish. No HTML, lib, or copy edits.

Paths are under `V:\a\Ai\spidercaster\working`.

## What was on disk

| Path | On disk |
| --- | --- |
| `stage/demo/out/index.html` | yes |
| `stage/demo/src/copy/` (`overview.md`, `commands.md`, `faq.md`) and `stage/demo/src/brief.md` | yes |
| `stage/harbor/out/index.html` | no. `stage/harbor/out/` is absent |
| `stage/harbor/src/copy/` and `stage/harbor/src/brief.md` | yes, source only |
| `projects/demo-local/brief.md` plus `copy/` | yes. Same text as `stage/demo/src` |
| `projects/bench-harbor-tearoom/brief.md` plus `copy/` | yes. Same text as `stage/harbor/src` |

`stage/harbor` is not an empty folder. It has no staged page, so it is not scored as a page.

## stage/demo/out/index.html

Included prose is from the copy files. It is cut on the source line wraps, and later copy is dropped. No invented award, review, or price. The page body has no quote block and no price block. The stylesheet defines those components; this page does not fill them.

### Sentences from the copy

Partly.

- Title, `h1`, and brand: `SpiderCaster: websites from real copy, on free tokens`. That is the overview heading.
- Meta description, `og:description`, and the hero lede are the first physical line of the overview, not a finished sentence: "You give it a brief and".
- The About body is the next three physical lines of that same paragraph, still mid-sentence. First line of that body: "real copy files; it returns a self-contained static site." Last line stops at "the Gemini". The copy continues "free tier first, then OpenRouter free models…" and that remainder is not on the page.
- The second overview paragraph (WebDev rails, noindex, token ledger) is not on the page.
- `## Why it is cheap` and its five bullets are not on the page.
- Features are the four `## Build` lines from `commands.md`, split on the colon. Example body: "scaffold a project with brief.md and a copy folder."
- `## Iterate`, `## Gate and preview`, and `## House rules` are not on the page.
- FAQ heading and all five questions and answers match `faq.md`. Example answer phrase: "No model is called."

### Invented award, review, or price

No award. No review. No price. "Zero dollars" in the FAQ is already in `faq.md`. It is not a new price.

Chrome that is not in the copy, and is not an award, review, or price:

- Heading and nav label "About".
- Button label "Read on".
- Footer "(c) 2026" plus the overview title. The year is not in the brief or the copy.
- Footer line "Built with SpiderCaster".

### Heading

Mixed.

- Specific, from copy: the `h1` above, the features heading "Build", and "Questions about the engine".
- Generic: "About". The overview has no About heading.

### Description

Not a placeholder string. Not a real sentence. It is the overview's first wrapped line, cut before the sentence ends. Quoted phrase: "You give it a brief and".

The first complete sentence in `overview.md` is "SpiderCaster is a copy-driven static website engine." The page description runs past that sentence and stops at the line wrap.

## stage/harbor

No staged page. `stage/harbor/out/index.html` was absent after the wait. Nothing to check for invented awards, reviews, or prices.

Source only, same words as `projects/bench-harbor-tearoom`. Not a rendered score. The brief calls the business synthetic and says never index, never deploy. Copy on disk, unused by a page:

- Heading in the overview: "Harbor Tea Room".
- First sentence: "A quiet tea room that seats walk-ins by the water."
- Hours: "Open Tuesday to Sunday, 8am to 6pm." and "Closed Mondays."
- Menu line with a price already in the copy: "Jasmine Pearl - $4.50" (also Assam Malt $3.75, Peppermint Field $3.25). Those prices are source text. They are not on a page.
- Contact: "14 Harbor Lane", "(555) 014-2288", "Walk-ins only; no reservations needed."

## Engine changes

These keep facts inside the copy. They do not add marketing lines.

1. Set the meta description and the hero lede to the first complete sentence of the overview. Do not stop at a source line wrap.
2. Join soft-wrapped lines into paragraphs before placing them. Split on blank lines or sentence ends, not on the authoring width.
3. If a paragraph does not fit a slot, carry every remaining sentence into the body. Do not drop the tail after a fixed number of physical lines. On this demo page the cut was one line for the lede and three lines for About.
4. Do not title leftover overview text "About" unless the copy has that heading. Use the copy heading that introduced the text, or leave the section untitled.
5. Emit a section for every copy heading that was ingested. On this demo page that includes "Why it is cheap", "Iterate", "Gate and preview", and "House rules", using only the lines already in those sections.
6. Do not invent a button label. If the copy has no call to action, omit the button. "Read on" is not in the copy.
7. Do not stamp a copyright year unless the brief or the copy states one.
8. When a harbor page is rendered, take hours, each menu line and its stated price, and the contact lines from those copy files. Do not add an award, a review, or a price that is not already written there. Description rule stays the same: the first real sentence of the overview.
