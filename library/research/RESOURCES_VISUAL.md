# Visual resources — 2026-10-01 image tests

Resource finder 3 of 3. Looked at the four PNGs and their sibling receipts under `library/image-tests/2026-10-01/`. Did not call an image API. Did not publish. Did not copy anything into `V:\streams\webdev\builds\movelixir.com`.

`library/research/HANDS_CHANGELOG.md` does not exist, so the local proof filename below is `assets/hero.png`.

## Keeper

`floelixir-hero.png` is the keeper. The other three stay studies.

## What the pictures actually show

No text, logo, or watermark is visible in any of the four.

**floelixir-hero.png (keeper).** A wide still life. A speckled off-white ceramic cup of amber tea sits on a matching saucer, with a thin column of steam. The saucer rests on the left page of an open notebook; a black pen lies on the right page. The desk is warm wood. Soft daylight comes from a window on the left, with green blur outside. Behind the cup: a dark rectangular box, a stack of closed books, and a dark vase of small dried pale flowers. No person. The cup and steam are the bright subject, sitting a little right of center. The left third is mostly bare wood and the window, so a short hero crop can drop the flowers and still keep the cup, steam, and notebook. FEEDBACK.md is right: this matches a small morning ritual and still reads when the hero is short.

**movelixir-hero.png.** A man in a plum jacket and light shirt walks toward the camera on an empty dusk street, hands in pockets. His face is fully visible and turned slightly toward the lit doorway on the left. Warm light hits the left sidewalk and a potted plant; the sky and shadows are purple; a streetlamp recedes on the right. He is left of center, not parked on the right third. The open road fills the right. A split layout that puts copy on one side will cover him or cut him. FEEDBACK.md says he is centered. Close, but the figure is left-of-center and the quiet space is on the right — the opposite of "subject on the right third, quiet space on the left." The invented, identifiable face is real in the picture. No product bottle.

**recovelixir-hero.png.** A dim living room at night. A person with short dark hair lies on a gray sofa under a chunky knit blanket, head on a pillow, eyes closed. That is sleep, not an upright rest. A warm lamp on the right is the brightest object. A dark window with a few distant lights is on the left. The foreground table holds a dark mug, a small bowl, and a book; a plant sits by the window. The face is small and in shadow. At a short phone crop the lamp would win and the person would nearly disappear. FEEDBACK.md is right on both points, including that "resting" became "asleep." This is a room picture only. It is not a medical claim.

**movelixir-mark.png.** A square icon: one cream serif capital M, centered, on a deep plum rounded square. No photo, no extra letters, no slogan. Usable as a mark study. It is not the live favicon. FEEDBACK.md is right that a photo model should not be asked for a 16px favicon.

## Receipts

All four JSON files name provider `xai`, model `grok-imagine-image-2.0`, and quality `low`. None stores a key. None has a url field. None stores a resolution. FEEDBACK.md says resolution `1k`; that figure is not in the receipts, so it is not confirmed here. On-disk byte lengths match the receipt `bytes` fields.

| file | bytes | aspect | quality |
| --- | ---: | --- | --- |
| floelixir-hero.png | 223763 | 16:9 | low |
| movelixir-hero.png | 252790 | 16:9 | low |
| recovelixir-hero.png | 185764 | 16:9 | low |
| movelixir-mark.png | 116196 | 1:1 | low |

Prompts, as stored:

- floelixir-hero.png: "Intimate still life, no text, no logo, no watermark. Morning window light, a ceramic cup of tea on a wooden desk beside an open notebook, a little steam. Mood of a small ritual before deep work. Not a product ad."
- movelixir-hero.png: "Editorial photograph, no text, no logo, no watermark. A person walking at an easy pace on a quiet dusk street, warm low light, deep plum shadows and cream highlights. Mood of calm authority about everyday movement. Not a product ad and not a supplement bottle."
- recovelixir-hero.png: "Quiet evening interior, no text, no logo, no watermark. A person resting under a blanket on a sofa, one warm lamp, a dark window. Mood of the calm after a hard day. Not a product ad and not a supplement bottle."
- movelixir-mark.png: "Flat app icon, rounded square, one cream capital M centered on a deep plum field. No photograph, no extra letters, no slogan, no watermark."

## Molds (palette, type lead, nav, template, origin only)

| id | origin | palette | type_lead | nav | template |
| --- | --- | --- | --- | --- | --- |
| warmth-authority | scratch | #c8923e | serif | segmented | editorial |
| discover-grid | mutate | #2a6f8f | sans | top-bar | modern |
| clarify-mix | mix | #6b4c3b | slab | one-page | bold |

The mark study is plum and cream because the prompt said so. It is not the warmth-authority accent `#c8923e`, and it is not discover-grid or clarify-mix either.

## How the renderer treats a hero and a favicon

`hero_visual()` in `lib/render.py` prints an `<img>` only when `image` is set and does not start with `http://`, `https://`, or `//`. Anything else becomes the letter mark (`hero-mark`), the first alphanumeric of the brand. `normalize_data()` in `lib/ir.py` also clears those remote forms, and any path that contains `..`, before render.

`favicon_svg()` writes `favicon.svg` itself: a 32-by-32 SVG, rounded rect filled with the accent (fallback `#c8923e` if the accent is not a 6-digit hex), and one Georgia letter. It does not embed the AI mark.

## How a local proof page should refer to the keeper

Do not hotlink `api.x.ai`. Do not point `image` at any remote URL. A remote src is stripped and the page falls back to the letter mark.

1. Copy `library/image-tests/2026-10-01/floelixir-hero.png` into the proof project as `assets/hero.png`. Keep the png extension. `HANDS_CHANGELOG.md` is absent, so no other extension is named.
2. Set the hero image to the relative path only: `assets/hero.png`. A string or `{ "src": "assets/hero.png", "alt": "..." }` both normalize to that src.
3. Alt text should describe the visible still life (ceramic cup, steam, open notebook, morning window). Do not add medical claims or brand facts the picture does not show.
4. Leave `movelixir-mark.png` as a study. The live favicon stays the generated SVG.
5. Leave the test PNGs where they are. Do not apply them to `V:\streams\webdev\builds\movelixir.com`. Do not publish.

Next prompt notes, agreeing with FEEDBACK.md except for the centering nuance above: ask for the subject on the right third and quiet space on the left when the desktop hero is a split; say "no identifiable face" or "seen from behind" unless a real person was supplied; for a short phone hero, ask for a tighter, brighter subject; if the page is a ritual rather than sleep, say "awake, eyes open, sitting."
