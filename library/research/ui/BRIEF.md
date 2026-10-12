# SpiderCaster studio brief

Date: 2026-10-08. Same brief for every UI hero. You are a UX and research expert, not a cold coder. Read this file before you write. Write only your own report. Do not edit the engine, the catalog, part folders, ledger, or another hero's file. Do not publish. Do not bind a mold live. Do not invent copy.

## Who this is for

Keith runs SpiderCaster from Windows. Today the product is a Python 3.11+ standard-library CLI at `<repo-root>`. The command is `python spidercaster.py`. There is no studio screen. `serve` only hosts a finished site folder on 127.0.0.1. That is the gap.

## What already works

Offline build spends zero tokens. Sites stay noindex until a human runs `library bind --live`. That command was not run for this work and must not be run.

Commands: `init`, `build`, `refine`, `check`, `serve`, `compose`, `visit`, `tools list`, `tools apply`, `parts`, `crew`, `library`, `doctor`, `shipcheck`, `seat`.

`compose` plans from real `copy/` files, applies a frame only by reordering sections the copy already produced, paints one mold, and inserts one catalog part per section plus a header and a footer. `compose --plan` writes `structure.json` and no HTML.

Checker floors, called the 4Cs+ in this brief:

- Copy. Visible claims must be in the project copy. No SAMPLE, lorem, placeholder, invented reviews, or awards.
- Contrast. 4.5:1, large text 3:1.
- Chrome. Body 18px, chrome 16px, tap 44px, sticky header, skip link, hero visual, favicon.
- Crawl. One h1, no skipped heading level outside a catalog part, relative canonical, WebSite JSON-LD, no aggregateRating, description present.
- Plus. No sideways overflow at 360, 390, and 412. Mobile drawer opens and closes. `visit` measures 390 and 1280 when Playwright is installed. A noindex build writes `robots.txt` with `Disallow: /` and does not write a sitemap. A sitemap exists only for `build --indexable --host https://origin`.

208 catalog parts are built. Routes: hooks-blocks 80, headers 44, popups 43, sidebars 41. Molds: discover-grid, clarify-mix, warmth-authority. Do not bind warmth-authority. It is live on movelixir.com. Fourteen frames are in `library/frames`.

Projects that have real copy: `projects/demo-local` and `projects/bench-harbor-tearoom`. Those are the only staged sites a later build may compose. Fleet domains (iseark, teavital, floelixir, the elixir parks, and the rest of the MochaHost list) are not SpiderCaster projects. They have no copy pack here. Do not invent pages for them. Do not deploy.

Competitor notes from 2026-10-08 are in `library/research/competitors/`. Read the one named in your task. The engine stays static HTML. Do not propose React, Tailwind, shadcn, or a chat button that publishes.

## Report outline

1. Role. Who you are and the one job of this screen.
2. Evidence. What you read, including one competitor file, and what that product shows a person before the page exists.
3. Screen. The human actions, in order. Name the controls. Say what is refused.
4. Already here. Which CLI command or file does this today.
5. Proposal. The smallest studio surface that calls those commands. Stdlib only. Localhost only. No new package install.
6. 4Cs+ test. How this screen is judged on a phone-width window and on a built page.
7. Risks. What would invent copy, deploy, or hide a failure.

First line of the report is your role name. Unmeasured claims stay marked not public.
