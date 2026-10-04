# graphics wrapper

Load this file, then `SKILL.md`. Seat 4 of 7. Model `google/gemma-4-31b-it`. If that id is unavailable: `inclusionai/ling-3.0-flash-vl`. Run from `V:\a\Ai\spidercaster\working`.

## Reads

- `py -3.14 spidercaster.py doctor` must be ok before the seat starts
- `py -3.14 spidercaster.py seat graphics` shows this seat's hands
- `library/seats/README.md` and `library/CREW.md`
- `projects/<project>/assets.json` if it exists
- every `![alt](src)` in `copy/`
- vault parent snapshots by name only (`SPIDERCASTER_VAULT`, default `V:\streams\webdev\vendor-vault`)

## Allowed hands

`asset_list`, `vault_photos`

In that order. No other hand.

## Steps

1. `asset_list`. Keep local paths. A local `assets/hero.png`, `assets/hero.jpg`, `assets/hero.jpeg`, or `assets/hero.webp` is a local asset. Frontend copies the first of those that exists into the build. This seat only lists it. Remote image URLs are rejected. The letter mark is used when no local file exists. A src that starts with `http://` or `https://`, or that names unsplash, freepik, pixabay, or pexels, fails this hand. Do not download it.
2. `vault_photos`. Count photo names when a parent snapshot is already in the vault. Do not copy those files into `library/`, the project, or `<out>`.
3. Do not generate an image inside the crew loop. Outside this loop, when Keith asks for one picture: `python spidercaster.py image --prompt "<words>" --out <project>/assets/<name>.png`. It saves a local file and a receipt. A hero file the build can copy is `assets/hero.png`, `assets/hero.jpg`, `assets/hero.jpeg`, or `assets/hero.webp`. The receipt stores neither the key nor the provider URL. Default provider is xAI. `--provider openrouter` is the other choice. Do not put a provider URL in the page. Do not run it on every build. The letter mark is used when no local file exists.

## Pass

- `asset_list`: `<n> local asset(s); no stock CDN`. Zero local files and zero remote srcs is a pass.
- `vault_photos`: `no parent frames`, or `<n> vault photo(s)`. A missing snapshot is `SKIP` (`snapshot not in vault for ...`), not a fail.

## Fail

- `remote asset urls are not allowed`
- `assets.json unreadable (...)`
- `no mold` from `vault_photos`
- A FAIL stops visual and seo. Deployer still writes `crew-ticket.json`. `crew run` does not publish.

## Does not

- No hotlink. Do not pull a stock CDN url into the page.
- No vault copy into `library/`, the project, or `<out>`.
- The image CLI is outside the crew and only when Keith asks. Do not call `python spidercaster.py image` on every build.

## Mobile

Local hero only, real pixel size, no hotlink.

- A page with no local hero image keeps the letter mark. On a phone that mark is a centered 2/1 band at most 120px tall. Do not invent a photo and do not hotlink one.
