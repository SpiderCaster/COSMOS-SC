# Stage demo

Quality read of the staged SpiderCaster build after the bullet fix and the chrome fix. Not published. `--live` was not passed. `--frame` was not passed. HTML was not hand-edited. `lib/` and `projects/` were not edited. No image was added.

`inbox/restage-demo2.md` and `inbox/chrome.md` were polled every 20 seconds starting 15:14:19. `restage-demo2.md` contained a DONE section by 15:14:39. `chrome.md` was missing until 15:19:39 (STARTED), then contained a DONE section at 15:23:00, inside the 10-minute cap. `stage/demo` was not overwritten while `restage-demo2` was still running.

- Source copy: `stage/demo/src` (copy of `projects/demo-local`; SHA256 match on `brief.md`, `copy/commands.md`, `copy/faq.md`, `copy/overview.md`)
- Images in that copy: none
- Output: `stage/demo/out/index.html`
- Site: `demo-stage.example`
- Mold: `clarify-mix`
- Frame: none (planner uses copy order). No frame retry.
- Ticket: `stage/demo/out/crew-ticket.json` (`ok` true). Also written: `site.json`, `favicon.svg`. One HTML page. Crew exit 0.

## Seat lines

```
[PASS] architect: brief read (303 chars); no frame selected; planner uses copy order; mold clarify-mix (mix, slab, one-page); bound demo-stage.example -> clarify-mix (draft)
[PASS] content: 8 block(s) from copy/commands.md, copy/faq.md, copy/overview.md; 8 block(s) from copy/commands.md, copy/faq.md, copy/overview.md
[PASS] frontend: planned 1 page(s); 2 page(s) written
[PASS] graphics: 0 local asset(s); no stock CDN; no parent frames
[PASS] visual: checker 0 FAIL, noindex on
[PASS] seo: one mold on this site; a second live use will be refused; 1 page(s)
[PASS] deployer: ticket written; publish is a Keith click (library bind --live)
```

Publish line: `Keith click. This run does not deploy.`

## Checks

- "JSON-repair" appears in the same card as "One-call AI builds", not as a lone lede: yes
- the page does not contain the exact button text Read on: yes
- the page does not contain Built with SpiderCaster: yes
- the page does not contain an h2 that is only About: yes
- noindex: yes
- one h1: yes
- description ends with "static site.": yes

The cheap-card markup is `<h3>One-call AI builds</h3><p>a single compact planning call produces the whole site shape, with at most one JSON-repair retry.</p>`. The hero lede does not contain `JSON-repair`.

The only primary button is `<a class="btn primary" href="#about">SpiderCaster is a</a>`. The string `Read on` is absent. The string `Built with SpiderCaster` is absent. The footer line is `(c) 2026 SpiderCaster: websites from real copy, on free tokens`.

Headings: one `h1` (`SpiderCaster: websites from real copy, on free tokens`). The `h2` texts are Build, Iterate, Gate and preview, House rules the engine enforces, Questions about the engine, and Why it is cheap. Section `id="about"` has a paragraph and no `h2`.

`<meta name="robots" content="noindex, nofollow">` is present, with the comment `SpiderCaster: noindex until approved`. The meta description is `SpiderCaster is a copy-driven static website engine. You give it a brief and real copy files; it returns a self-contained static site.`
