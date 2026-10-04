# Local photos for the quality tests

Measured 2026-10-01. Working tree `V:\A\Ai\spidercaster\working`. No image API. Nothing published. No hotlink. No site edit. No image copied. No credential file opened. No Cloudflare id copied.

## Files in `library/image-tests/2026-10-01`

Lengths are from `Get-Item`. Each PNG length matches the `bytes` field in its sibling JSON. Every receipt names provider `xai`, model `grok-imagine-image-2.0`, and quality `low`. None stores a key. None stores a URL. None stores a resolution. `FEEDBACK.md` says resolution `1k`. That figure is not in the receipts, so it is not confirmed here.

| file | bytes |
| --- | ---: |
| FEEDBACK.md | 1447 |
| floelixir-hero.json | 395 |
| floelixir-hero.png | 223763 |
| movelixir-hero.json | 443 |
| movelixir-hero.png | 252790 |
| movelixir-mark.json | 321 |
| movelixir-mark.png | 116196 |
| recovelixir-hero.json | 395 |
| recovelixir-hero.png | 185764 |

Receipt aspects: the three heroes are `16:9`. The mark is `1:1`.

## What was read

`FEEDBACK.md`. `projects/bench-harbor-tearoom/brief.md` plus `copy/` (overview, hours, menu, contact). `projects/demo-local/brief.md` plus `copy/` (overview, commands, faq). The four PNGs were opened and not copied.

## Match

Neither brief has a matching PNG.

**bench-harbor-tearoom.** Synthetic fixture, frozen in the brief: a quiet tea room that seats walk-ins by the water. Copy adds loose-leaf, Tuesday–Sunday 8am–6pm, three priced teas, and 14 Harbor Lane. The project has no `assets/` directory, no `assets.json`, and no markdown image.

| PNG | Honest match |
| --- | --- |
| floelixir-hero.png | no |
| movelixir-hero.png | no |
| recovelixir-hero.png | no |
| movelixir-mark.png | no |

`floelixir-hero.png` is the only tea picture. It is a desk still life: speckled cup, steam, saucer on an open notebook, black pen, morning window, stacked books, dried flowers in a dark vase. No water, no seats, no tea room, no harbor. `FEEDBACK.md` is right that it matches the floelixir ritual prompt (a small ritual before deep work). That prompt is not this brief. Using the file here would show a work desk the copy never describes.

`movelixir-hero.png` is a man walking a dusk street, face visible, left of center. Not the tea room. `FEEDBACK.md` already flags the invented face and the crop.

`recovelixir-hero.png` is a person asleep under a blanket on a sofa, lamp on the right. Not the tea room. `FEEDBACK.md` is right that resting became sleep.

`movelixir-mark.png` is one cream capital M on a plum rounded square. It is not a photograph, and it is not the letter for Harbor Tea Room.

**demo-local.** The brief is the engine: what it does, the token rules, and the commands. Tone is plain and factual. The project has no `assets/` directory, no `assets.json`, and no markdown image. Copy forbids hotlinked stock photos. It names no place and no product photograph.

| PNG | Honest match |
| --- | --- |
| floelixir-hero.png | no |
| movelixir-hero.png | no |
| recovelixir-hero.png | no |
| movelixir-mark.png | no |

None of the four shows the engine, a command, or a token ledger. The M mark is the wrong letter.

`preview\demo-hero\assets\hero.png` and `preview\demo-hero-out\assets\hero.png` are each 223763 bytes, the same length as `floelixir-hero.png`. That is the study still life, already sitting on a demo-copy preview. It does not depict this brief. It was not copied again.

## Letter mark

Both briefs must keep the letter mark. No honest local photo exists for either.

`hero_visual()` in `lib/render.py` prints an `img` only when `image` is set and does not start with `http://`, `https://`, or `//`. Otherwise it emits `hero-mark`, the first alphanumeric of the brand. That letter is **H** for Harbor Tea Room and **S** for the SpiderCaster title. `favicon_svg()` draws the same letter into `favicon.svg`. `movelixir-mark.png` does not replace it. `FEEDBACK.md` says not to ask the photo model for the favicon.

`library/research/HANDS_CHANGELOG.md`: if the project has no `assets/hero.png`, `assets/hero.jpg`, `assets/hero.jpeg`, or `assets/hero.webp`, the letter mark stays. Neither quality-test project has one of those files.

The built pages were not edited. `sites\bench-harbor-tearoom\index.html` (17006 bytes) and `sites\demo-local\index.html` (24695 bytes) each have a text hero, zero `img` tags, and zero `hero-mark` strings. Their `site.json` hero objects have no image field. A later render that finds no local hero file should keep the letter mark, not one of these PNGs.

## Vault

Default vault `V:\streams\webdev\vendor-vault` exists. `SPIDERCASTER_VAULT` was unset in the process and user environments. `frames.json` is 23525 bytes: 82 frames, every `photos` value `not-pulled`, no snapshot set, and zero image files under the vault. The note says names only, until a snapshot is accepted. Those rows are not local photos. Nothing was copied out of the vault.

## Leave them

Do not hotlink. Do not point either quality test at these PNGs. Do not copy `floelixir-hero.png` onto the harbor bench or onto `projects/demo-local`. Do not publish. Leave the test files in `library/image-tests/2026-10-01/`.
