# Harbor photo score

Score only, 2026-10-01. Not published. No image API. HTML, lib, and the image were not edited.

Paths are under `V:\a\Ai\spidercaster\working`.

`inbox/harbor-photo.md` was polled every 30 seconds from 15:35:15 through 15:44:45 (20 cycles, 10-minute window). The header stayed `STATUS: STARTED`. The sentence that mentions waiting for another inbox to contain DONE was not treated as completion. The timeout read at 15:45:16 contained a later line, `STATUS: DONE`. The page and the picture were read after that.

## What I see

`stage/harbor/out/assets/hero.png` is a wide interior. A rough wooden table fills the foreground. On it sit a speckled light ceramic teapot and a matching cup. I do not see liquid, steam, or anyone drinking. To the left, a dark vase holds leafy branches on a low wooden bench with one gray cushion. A wood-framed opening looks onto calm water, a rocky shore, trees, and hazy hills. A sheer curtain hangs on the right. Warm light crosses the table in stripes.

The room is unoccupied. No person, face, hands, or crowd. No sign, menu, price, award, or other readable lettering in the picture.

## Empty tea room by the water

Yes. It matches an empty tea room by the water: no guests, tea ware on the only table, seating is the bench, and the water is in the frame rather than implied. It is a synthetic still, not a photograph of a real shop. It is a fair stand-in for the brief’s quiet tea room that seats walk-ins by the water.

## Text or face invented

No text in the picture. No face in the picture. Nothing in the pixels spells a menu item, a price, an award, or a street address.

## Page facts

Read from `stage/harbor/out/index.html` after the inbox said DONE.

| Check | Result |
| --- | --- |
| img alt | `Harbor Tea Room` |
| file local | yes. `<img src="assets/hero.png" ...>`. `og:image` is `assets/hero.png`. Not an http(s) image URL |
| noindex | yes. `<meta name="robots" content="noindex, nofollow">`. Comment: SpiderCaster: noindex until approved |
| hero button label | `Contact`. `<a class="btn primary" href="#contact">Contact</a>` |

The only `https` in that HTML is the schema.org `@context` in JSON-LD, not the hero.

On-disk file: `stage/harbor/out/assets/hero.png`, 261195 bytes, 1280×720, last write 2026-10-01 15:38:06. The img attributes say `width="1600"` `height="900"`. Same 16:9 ratio; the attributes overstate the pixel size. The alt names the place and matches a tea room, but it does not describe the table, pot, cup, or water.

## Score

Pass as a local, unoccupied tea-room-by-water hero. No invented face. No invented text in the picture. noindex is set. The hero button says Contact. The alt is a place name, not a scene description, and the declared 1600×900 is larger than the 1280×720 file.
