# Stage harbor

Quality notes for the draft crew restage after the chrome fix. Not published. No `--live`. HTML was not rewritten by hand. No photo was added.

Polled `inbox/chrome.md` every 20 seconds from 15:14:27. The file was missing through 15:18:47, then STARTED only through 15:22:28. A line that is `DONE` was present at 15:22:48. The crew ran after that, not on a half-written renderer.

`projects/bench-harbor-tearoom` brief and copy were copied onto `stage/harbor/src`. SHA256 matched for `brief.md`, `copy/contact.md`, `copy/hours.md`, `copy/menu.md`, and `copy/overview.md`. `stage/harbor/src/assets` stayed empty. No hero png was copied.

No `--frame` (house-menu drops hours). No `--live`.

Command (cwd `<repo-root>`):

`py -3.14 spidercaster.py crew run stage\harbor\src --site harbor-test.example --out stage\harbor\out --mold discover-grid`

Exit 0. Ticket: `stage/harbor/out/crew-ticket.json`. Publish line: `Keith click. This run does not deploy.` All seven seats PASS. `ok` true. Graphics: 0 local assets.

## index.html

Read `stage/harbor/out/index.html`. Not hand-edited.

- noindex: present. `<meta name="robots" content="noindex, nofollow">` and the comment `SpiderCaster: noindex until approved`.
- one h1: yes. The only `<h1>` is `Harbor Tea Room`.
- hours present: yes. The hours section has `Open Tuesday to Sunday, 8am to 6pm.` and `Closed Mondays.`
- description is the full walk-ins sentence: meta description, og:description, JSON-LD description, and the hero lede are `A quiet tea room that seats walk-ins by the water.`
- phone: `site.json` contact `phone` is `(555) 014-2288`. In the HTML that number sits in its own contact row. The contact lede is only `Walk-ins only; no reservations needed.` The number is not glued onto that sentence.
- no button whose text is exactly `Read on`. The primary control text is `A quiet tea`. The other control text is `Contact`.
- no `Built with SpiderCaster`. The footer line is `(c) 2026 Harbor Tea Room`.
- no h2 that is only `About`. The h2 texts are `Contact`, `Hours`, and `Menu`. The leftover overview paragraph is in `#about` with an empty title and no h2: `Loose-leaf, brewed to order; decaf after 4pm on request.`
- hero is the letter H. The hero visual is `<span>H</span>` inside `hero-mark`. `site.json` hero `image` is empty. No hero file was staged.
