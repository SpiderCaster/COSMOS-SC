# SHIP_RESULT

Staged harbor and demo, 2026-10-01. No publish. No `--live`. No `--frame`. `stage/harbor/src` and `stage/demo/src` were already present, so nothing was copied from `projects/`. `stage/harbor/src/assets/hero.png` was left in place. No image was added to the demo. No `lib/` file was edited.

## Commands

Waited 3 minutes, then:

`py -3.14 spidercaster.py shipcheck`

Exit 2. Last line: `lib.regress`

`lib/regress.py` was not on disk. That gate waits 90 seconds once for it. The run lasted about 92 seconds and still printed only the missing step name. `inbox/regress.md` was STARTED at that moment.

`py -3.14 spidercaster.py crew run stage\harbor\src --site harbor-test.example --out stage\harbor\out --mold discover-grid`

Exit 0. Mold discover-grid. No frame. Last lines: `Keith click. This run does not deploy.` and `ticket: stage\harbor\out\crew-ticket.json`.

`py -3.14 spidercaster.py crew run stage\demo\src --site demo-stage.example --out stage\demo\out --mold clarify-mix`

Exit 0. Mold clarify-mix. No frame. Last lines: `Keith click. This run does not deploy.` and `ticket: stage\demo\out\crew-ticket.json`.

After `lib/regress.py` landed, `inbox/regress.md` said DONE and `py -3.14 -m lib.regress` printed `regress selftest ok` (exit 0). A second `shipcheck` then exited 2. Its lines were `lib.hands.selftest` and `spidercaster.py crew selftest`. A direct `py -3.14 -m lib.hands.selftest` printed `check_site FAIL: internal_links` (exit 1). A direct `py -3.14 spidercaster.py crew selftest` printed `crew selftest ok` (exit 0). Replaying the hands fixture after that passed. Final `py -3.14 -m lib.hands.selftest` printed `hands selftest ok` (exit 0). Final `py -3.14 spidercaster.py shipcheck` printed `shipcheck ok` (exit 0).

Shipcheck's last line on the final run: `shipcheck ok`

Crew exit codes: harbor 0, demo 0.

## stage/harbor/out/index.html

| check | result |
| --- | --- |
| noindex | yes |
| one h1 | yes |
| one hero button | yes |
| button text is a real heading | yes |
| no Read on | yes |
| no Built with SpiderCaster | yes |
| no h2 About | yes |
| no h3 Menu under an h2 Menu | yes |
| hero img file exists or letter mark | yes |
| no remote img URL | yes |

`<meta name="robots" content="noindex, nofollow">`. One h1: `Harbor Tea Room`. One hero button: `<a class="btn primary" href="#contact">Contact</a>`. That label is the h2 `Contact`. The header `button.nav-toggle` is the menu control, not a second hero button. No `Read on`. No `Built with SpiderCaster`. No `<h2>About</h2>`. `#about` is a paragraph only. `<h2>Menu</h2>` has menu items as spans, not an `<h3>Menu</h3>`. Hero img `src="assets/hero.png"` and `stage/harbor/out/assets/hero.png` exists. The only `https://` is the JSON-LD `@context`, not an img src.

## stage/demo/out/index.html

| check | result |
| --- | --- |
| noindex | yes |
| one h1 | yes |
| one hero button | yes |
| button text is a real heading | yes |
| no Read on | yes |
| no Built with SpiderCaster | yes |
| no h2 About | yes |
| no h3 Menu under an h2 Menu | yes |
| hero img file exists or letter mark | yes |
| no remote img URL | yes |

`<meta name="robots" content="noindex, nofollow">`. One h1: `SpiderCaster: websites from real copy, on free tokens`. One hero button: `<a class="btn primary" href="#features">Build</a>`. That label is the h2 `Build`. The header `button.nav-toggle` is not a second hero button. No `Read on`. No `Built with SpiderCaster`. No `<h2>About</h2>`. `#about` is a paragraph only. No Menu heading, so there is no `<h3>Menu</h3>` under an `<h2>Menu</h2>`. Hero is a letter mark: `<div class="hero-visual hero-mark" aria-hidden="true"><span>S</span></div>`. No `<img>`. The only `https://` is JSON-LD `@context`. `stage/demo/src/assets` is absent.

Frontend on both tickets said `planned 1 page(s); 2 page(s) written`. `assemble` returns `index.html` and `favicon.svg`. Each out dir has those two files plus `site.json` and `crew-ticket.json`. That is not a second HTML page.

## Still open

none. The first `shipcheck` miss (`lib.regress` absent) and the mid-landing `check_site FAIL: internal_links` do not reproduce. Final shipcheck last line is `shipcheck ok`. No owner file was edited. Tests were not weakened.
