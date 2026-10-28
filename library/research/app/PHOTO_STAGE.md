# Photo stage

Review only, 2026-10-01. Not published. No image generated. HTML and lib were not edited. No menu was written.

Paths are under `V:\a\Ai\spidercaster\working`.

## What is on disk

| Path | On disk |
| --- | --- |
| `stage/harbor/src/assets/hero.png` | no. `stage/harbor/src/assets/` exists and is empty |
| `stage/harbor/out/assets/hero.png` | no. `stage/harbor/out/assets/` exists and is empty |
| `stage/harbor/out/index.html` | yes |
| `projects/bench-harbor-tearoom/brief.md` | yes |
| `library/image-tests/2026-10-01/FEEDBACK.md` | yes |
| `library/image-tests/2026-10-01/floelixir-hero.png` | yes, 223763 bytes. Not in the stage folders |

`Test-Path` on both staged `hero.png` paths was false. A force listing of `stage/harbor` found no `hero.png`.

## What I see

Nothing. There is no staged picture to look at. I did not open `floelixir-hero.png` and treat it as the harbor hero. I did not generate a replacement.

## Brief

`projects/bench-harbor-tearoom/brief.md` is a synthetic quiet tea room that seats walk-ins by the water. One page. Never index, never deploy, never link from live lanes. A fair stand-in would have to be that room, or be labeled as something else.

A missing file is not a fair stand-in for that tea room. It shows no water, no seats, and no room.

## Alt on the built page

`stage/harbor/out/index.html` has one image:

`<img src="assets/hero.png" alt="Harbor Tea Room" width="1600" height="900" fetchpriority="high" decoding="async">`

The alt is not honest. It names Harbor Tea Room. The file that `src` points at is not in `stage/harbor/out/assets/`. The width and height claim 1600 by 900 for bytes that are not there. The hero lede beside it, `A quiet tea room that seats walk-ins by the water.`, is the brief, not a description of a picture.

## Borrowed still life

`library/research/app/STAGE_HARBOR.md` says `library/image-tests/2026-10-01/floelixir-hero.png` was copied to `stage/harbor/src/assets/hero.png`. That copy is not on disk now, so this pass cannot confirm the staged bytes.

`FEEDBACK.md` describes `floelixir-hero.png` as cup, steam, notebook, and a morning window: a ritual study, not this brief. If that file is what the page was built to show, it is a borrowed still life, not a photo of the harbor room. `alt="Harbor Tea Room"` would still be a false caption for that study. The letter mark would have been the honest hero while no local photo of the room exists.

## Quality

No crop, light, or sharpness score. There are no staged pixels. As a hero, the page fails: one local `img`, broken `src`, and an alt that claims a place the asset does not show.
