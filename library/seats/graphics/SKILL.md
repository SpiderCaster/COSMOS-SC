---
name: spidercaster-graphics
description: >-
  Use when a project's images must be confirmed as local files and vendor photos left in the vault, not when an asset URL is remote or the task is copy, HTML, the checker, SEO, or publish.
---

# spidercaster-graphics

## When not to use

- The task is to hotlink a photo, or to paste a provider URL into HTML.
- The task is copy, molds, HTML, `check`, SEO, or publish.
- Filling the gap would copy a vendor demo out of the vault.

## Start

1. Read `library/seats/README.md` and `library/CREW.md`.
2. Stay inside the project plus a read of the vault. Do not write the vault. The only project write is one Keith-asked local image file.
3. Call only `asset_list`, then `vault_photos`.
4. Read-only orientation, not hands:

   `py -3.14 spidercaster.py doctor`

   `py -3.14 spidercaster.py seat graphics`

## Steps

1. **asset_list.** Read `projects/<project>/assets.json` if it exists (`images` map of name to path). Read every `![alt](src)` in `copy/`. A local `assets/hero.png`, `assets/hero.jpg`, `assets/hero.jpeg`, or `assets/hero.webp` counts as a local asset. Frontend copies the first of those that exists into the build. This seat only lists it. Remote image URLs are rejected. The letter mark is used when no local file exists. A src that starts with `http://` or `https://`, or that names unsplash, freepik, pixabay, or pexels, is a failed hand. Stop. Do not download it.
2. **vault_photos.** Vendor frame photos stay in `V:\streams\webdev\vendor-vault` (`SPIDERCASTER_VAULT`). You may see that they are not in the package. You may not copy them into `library/`, the project, or `<out>`. A photo the project does not already have stays missing.
3. **A asked-for picture.** Image generation is not every build, and this is not a hand. When Keith asks for one image, one `python spidercaster.py image --prompt "<words from the brief>" --out <project>/assets/<name>.png` may save a local file. A hero file the build can copy is `assets/hero.png`, `assets/hero.jpg`, `assets/hero.jpeg`, or `assets/hero.webp`. Default provider is `xai` (Grok Imagine on the SGH Console key). `--provider openrouter` prompts OpenRouter instead. No hotlinks, no provider URLs, no vault photo copies. The letter mark is used when no local file exists.

## Exit

Return the count of local paths and any remote src you refused. Zero local files and zero remote srcs is a pass. Stop.

## Do not

- Pull a stock-CDN URL into the page.
- Copy vault photos or theme files into the package or the site.
- Publish. `crew run` does not publish.

## Risk tier

Tier 0 except one asked-for local save. No hotlink, no provider URL in the page, no vault photo copy, and no image generation on every build. A Keith-asked `python spidercaster.py image` may save one local file.

## Mobile

Local hero only, real pixel size, no hotlink.

- A page with no local hero image keeps the letter mark. On a phone that mark is a centered 2/1 band at most 120px tall. Do not invent a photo and do not hotlink one.
