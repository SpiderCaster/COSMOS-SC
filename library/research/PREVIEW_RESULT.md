# Preview result

Local noindex proof only. Nothing was published. `--live` was not passed. `library bind` was not invoked as its own command. No image API was called. Demo copy was not rewritten. This is a style study on DEMO copy, not a floelixir.com site.

Inbox stamp before the wait: `STARTED 2026-10-01 13:53:45` in `library/research/inbox/preview.md`. Working directory for every command: `V:\a\Ai\spidercaster\working`.

## Engine selftest

Waited `Start-Sleep -Seconds 120` (`SLEEP_DONE`, exit 0) before the selftest.

Command:

```
py -3.14 spidercaster.py crew selftest
```

Stdout (stderr was merged with `2>&1`; no separate error text):

```
crew selftest ok
EXIT_CODE=0
```

No retry. Not an assertion failure.

## Demo hero build

`library/research/HANDS_CHANGELOG.md` was absent after the wait, and still absent immediately before the copy. The hero convention file was absent. The study photo was still copied to `assets/hero.png`.

`projects\demo-local` was copied as files only (no venv present): `brief.md`, `copy/commands.md`, `copy/faq.md`, `copy/overview.md`. Then:

```
Copy-Item -LiteralPath 'library\image-tests\2026-10-01\floelixir-hero.png' -Destination 'preview\demo-hero\assets\hero.png' -Force
```

`preview\demo-hero\assets\hero.png` is 223763 bytes, the same length as the source PNG. The source photo was not applied to a floelixir.com site.

`spidercaster.py` takes a positional project, not `--project`. Real flags used (`--frame` exists; `library/frames/welcome-scroll.json` exists):

```
py -3.14 spidercaster.py crew run preview\demo-hero --site demo-hero.example --out preview\demo-hero-out --mold discover-grid --frame welcome-scroll
```

Stdout:

```
  [PASS] architect: brief read (303 chars); frame welcome-scroll (hero, about, features, gallery, faq, contact); mold discover-grid (mutate, sans, top-bar); bound demo-hero.example -> discover-grid (draft)
  [PASS] content: 8 block(s) from copy/commands.md, copy/faq.md, copy/overview.md; 8 block(s) from copy/commands.md, copy/faq.md, copy/overview.md
  [PASS] frontend: planned 1 page(s); 2 page(s) written
  [PASS] graphics: 0 local asset(s); no stock CDN; no parent frames
  [PASS] visual: checker 0 FAIL, noindex on
  [PASS] seo: one mold on this site; a second live use will be refused; 1 page(s)
  [PASS] deployer: ticket written; publish is a Keith click (library bind --live)
Keith click. This run does not deploy.
  ticket: preview\demo-hero-out\crew-ticket.json
EXIT_CODE=0
```

The architect hand recorded a draft row in `library/ledger.json`: site `demo-hero.example`, mold `discover-grid`, `vendor_frame` null, `live` false. That is not a publish.

Files under `preview\demo-hero-out`:

- `index.html` exists (21768 bytes)
- `favicon.svg` exists (227 bytes)
- `site.json` (4978 bytes)
- `crew-ticket.json` (1309 bytes)
- `assets/hero.png` beside the html: absent
- `hero.png` beside the html: absent

`index.html` string checks:

- `hero-visual`: present (CSS and the hero div)
- `site-header`: present (`<header class="site-header">` and CSS)
- `is-stuck`: present in CSS (`.site-header.is-stuck`) and in the scroll script (`classList.toggle('is-stuck', ...)`). The header element is not given `is-stuck` in the initial markup.
- `rel="icon"`: present, `<link rel="icon" href="favicon.svg" type="image/svg+xml">`
- `noindex`: present, `<meta name="robots" content="noindex, nofollow">`

Hero markup has no `img` and no `hero.png` src. It is the letter mark:

```
<section id="hero" class="hero hero--modern"><div class="wrap hero-stage"><div class="hero-visual hero-mark" aria-hidden="true"><span>S</span></div>...
```

Graphics reported `0 local asset(s)`. The project file `preview\demo-hero\assets\hero.png` was not copied into the output. That is the build result. The renderer was not changed.

## Flo and reco

`V:\streams\webdev\spidercaster_local\sites\floelixir.com.md` exists (5109 bytes). `V:\streams\webdev\spidercaster_local\sites\recovelixir.com.md` exists (5754 bytes). Both are brief and build-plan notes, not SpiderCaster `copy/` packs.

No `copy/` directory for floelixir or recovelixir was found under `V:\a\Ai\spidercaster` or `V:\streams\webdev\builds`. The only `copy/` directories under spidercaster were `projects\demo-local\copy`, `projects\bench-harbor-tearoom\copy`, and the same two under `cosmos-sc-public`. `V:\streams\webdev\builds` contains `movelixir.com` only. `credentials.env` was not read. No Cloudflare ids are copied here.

flo and reco cannot be built without inventing copy; not built.

## Worked / did not

Worked:

- Crew selftest exited 0 with `crew selftest ok`.
- A local noindex build exists at `preview\demo-hero-out\index.html`, with `favicon.svg`, `rel="icon"`, `site-header`, `hero-visual`, `is-stuck` in CSS/script, and robots `noindex, nofollow`.
- Crew run exited 0, mold `discover-grid`, frame `welcome-scroll`, and printed that the run does not deploy. The ledger row for `demo-hero.example` is draft (`live` false).

Did not:

- `HANDS_CHANGELOG.md` never appeared, so the hero filename convention was not confirmed by that file.
- `preview\demo-hero\assets\hero.png` was not copied beside the html. `index.html` has no hero `img` src; the hero is the letter mark `S`.
- Flo and reco were not built. There is no copy pack.
- Nothing was published.

## Rerun after the hero hand landed

The first build above ran while `HANDS_CHANGELOG.md` was still absent, so the page kept the letter mark. After `render` learned the `assets/hero.png` convention, the same project was built again. Nothing was published.

```
py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok

py -3.14 spidercaster.py crew run preview\demo-hero --site demo-hero.example --out preview\demo-hero-out --mold discover-grid --frame welcome-scroll
```

Every seat passed. Graphics reported `1 local asset(s)`. Visual reported `checker 0 FAIL, noindex on`. The ticket still says publish is a Keith click.

`preview\demo-hero-out\assets\hero.png` is 223763 bytes. `index.html` contains `src="assets/hero.png"`, `fetchpriority="high"`, `viewport-fit=cover`, `hero-visual`, `site-header`, `is-stuck`, `rel="icon"`, and `noindex`. `favicon.svg` is beside the html. This remains demo copy with the flo study photo. It is not floelixir.com.
