# Competitor research brief

Date of this brief: 2026-10-08. Same text for every research hero. One hero, one competitor. Write only your own report file. Do not edit the engine, the catalog, part folders, ledger, or another hero's report.

## What SpiderCaster already is

Engine: `V:\A\Ai\spidercaster\working`. Python 3.11+ standard library. Offline build spends zero tokens. A site stays noindex until a human runs `library bind --live`. The crew does not publish. Do not invent copy. Do not copy vendor HTML, CSS, or marketing text into a report beyond package names, file roles, and short public identifiers.

Commands that exist: `init`, `build`, `refine`, `check`, `serve`, `compose`, `visit`, `tools list`, `tools apply`, `parts scan`, `parts assemble`, `crew`, `library`, `doctor`, `shipcheck`, `seat`, `sections`, `image`.

`compose` plans from real `copy/` files, applies a package frame only by reordering sections the copy already produced, paints one mold, and inserts one catalog part per section plus a header and a footer. It writes `structure.json`, `site.json`, and `report.json`. Frame `welcome-scroll` plus mold `discover-grid` on `projects/demo-local` checked 34 pass, 0 fail, 0 warn, 1 skip (grey tile still needs a rendered photo).

Parts: 208 catalog rows, all built, under `V:\streams\webdev\tools\parts`. Routes: hooks-blocks 80, headers 44, popups-callouts 43, sidebars-widgets 41. `tools apply` can append, replace, paint a mold, and refuse a path listed in `lock.txt`.

Checker floors already in `lib/check.py`: body text 18px, chrome 16px, contrast 4.5:1 (large text 3:1), tap 44px, no SAMPLE/lorem/placeholder, no hotlinked images, relative canonical, one h1, WebSite JSON-LD and no aggregateRating, FAQ text visible when FAQPage is present, skip link, scroll-margin, sticky header, mobile drawer, no sideways overflow at 360/390/412. `visit` measures at 390 and 1280 when Playwright is installed.

Crew seats, in order: architect, content, frontend, graphics, visual, seo, deployer. The SEO seat's hands today are only `uniqueness` and `meta_basics`. `seat_gate` refuses a hand that is not on that seat. Molds: `discover-grid`, `clarify-mix`, `warmth-authority`. Do not bind `warmth-authority` live. It is already live on movelixir.com. Fourteen package frames live in `library/frames`.

Notes gathered 2026-10-01. Treat them as a head start, not as current fact. If a live page disagrees, the live page wins and the report says what changed:

- `library/research/HOW_PRO_BUILDERS.md`
- `library/research/BUILDER_PATTERNS.md`
- `library/research/ENVIRONMENT_GAPS.md`
- `library/research/app/HOW_CLAUDE_TOOLS.md`
- `library/research/app/HOW_CODE_BUILDERS_TOOLS.md`
- `library/research/app/HOW_WIX_SHOPIFY_TOOLS.md`
- `library/tools/LOOP_CONTRACT.md`

## Report outline

Use these headings, in this order.

1. Product. What it builds, the first input, and whether a human approves a plan before the page exists.
2. Code libraries. Named packages, registries, CSS systems, theme or token files, and component models. Say how a section is stored. If the source is closed, say not public. Do not paste vendor source.
3. Mobile. What the docs require or generate for small screens.
4. SEO. Sitemap, robots, canonical, title and description, Open Graph, JSON-LD types, heading order, internal links, page speed, and index controls. Separate a documented feature from a ranking promise. If a page does not say it, write not public.
5. Dynamic behavior. CMS, accounts, forms, or client JavaScript. Name the runtime.
6. Already in SpiderCaster. Which of the above the engine already does.
7. Worth building. Only items that stay static HTML, stdlib, real copy, noindex until a human publishes, and reimplemented rather than imported. No React, Tailwind, or shadcn runtime. No fake reviews. No chat button that deploys.
8. Sources. URL and the date you opened it. One line each. Marketing blogs are not a procedure.

## Contract line

Public docs and public code only. First line of the report is the competitor name. Unmeasured claims stay marked not public.
