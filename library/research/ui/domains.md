Domain Staging

## 1. Role

Domain Staging. This screen shows Keith which owned names may become a local noindex SpiderCaster site, and which must not. It does not write a page for a blocked name.

## 2. Evidence

Read on 2026-10-08:

- `library/research/ui/BRIEF.md`. Real copy exists only in `projects/demo-local` and `projects/bench-harbor-tearoom`. Those are the only sites a later build may compose. Fleet names are not SpiderCaster projects. Do not invent pages. Do not deploy. Do not bind `warmth-authority`.
- `projects/` listed in this working tree. Two directories, and nothing else.
- `projects/demo-local/brief.md` plus `copy/commands.md`, `copy/faq.md`, `copy/overview.md`. The brief says the build stays noindex.
- `projects/bench-harbor-tearoom/brief.md` plus `copy/contact.md`, `copy/hours.md`, `copy/menu.md`, `copy/overview.md`. The brief says the business is synthetic: never index, never deploy, never link from live lanes.
- `V:\streams\webdev\START_HERE.md` section 3, the fleet table only (status as written there, not re-measured live today). The kinds line above that table calls bradleybrandfurniture.com, buyfigs.com, iseark.com, chopncut.com, rareplantbid.com, the Soft five, and teavital.com full WordPress sites, and calls the parks single static landing pages.
- `library/research/ENVIRONMENT_GAPS.md` (measured 2026-10-01). floelixir and recovelixir have no project and no `copy/` here. movelixir.com has already-built HTML and no copy pack.
- `library/ledger.json`. `movelixir.com` / `warmth-authority` / `live` true. The other rows are `*.example` and `live` false. They are not copy packs.
- `lib/copy_pack.py`, `lib/ingest.py`, `lib/offline.py`, `lib/compose.py`, `lib/serve.py`, and the `init`, `compose`, `serve`, and `library bind` parsers in `spidercaster.py`.
- One competitor file: `library/research/competitors/webflow.md`.

What Webflow shows before the page exists: Dashboard, New site, AI Site Builder, a description, then Generate. That first result is a structure of pages and sections, not finished pages. The person edits that structure, then Generate site builds designs and "contextually relevant content." A custom domain is not required for that step. Later, Site settings can turn indexing off on the `webflow.io` staging host, separate from the production domain. Publish is a later click. Webflow also does not retrofit a site it did not build.

That is the wrong order for this screen. SpiderCaster must show the owned-name list first and stop, before any structure or HTML, when the name has no copy pack. It must not generate content to fill a fleet domain, and it must not import iseark or teavital because they are WordPress sites this engine did not build.

## 3. Screen

Actions, in order:

1. Open the staging list on this machine. The window title is Staging list. Two groups are on the page: May stage, then Blocked.
2. Read May stage. The only enabled rows are `projects/demo-local` and `projects/bench-harbor-tearoom`. Each row names its copy files. It does not paste the copy.
3. On an enabled row, press Plan or Compose local. Plan runs `compose <project> --plan` and writes `structure.json` only. Compose local runs `compose <project>` with no `--indexable` and no `--host`, into `sites/<project-name>-compose`.
4. Press Preview only after that folder has `index.html`. Preview runs `serve` on that folder. The server already binds `127.0.0.1`.
5. Read Blocked. Every fleet row shows the name and a reason in the row. There is no button on a blocked row.

Controls that exist: Staging list, May stage, Blocked, Plan, Compose local, Preview.

Refused, with the reason left on screen:

- Any press on a blocked name. No Plan, no Compose local, no Preview, no Init.
- New site, Generate, Connect domain, Publish, and `library bind --live`.
- `build --indexable` and any `--host` that is a fleet origin.
- `init` pointed at a fleet domain or at a new `projects/<domain>/`. `init` writes a generic brief and `copy/README.md`. That README is not a copy pack.
- Binding `warmth-authority`.
- Importing a WordPress docroot, database, or theme.
- Writing HTML whose claims are not already in that row's `copy/` files.

## 4. Already here

Nothing in the CLI lists owned domains or blocks them by name.

What does exist:

- `projects/` is the allow list. Today it contains only the two folders above. `project_copy_text` joins `copy/*.md`, `copy/*.markdown`, and `copy/*.txt` and returns an empty string when `copy/` is missing. It does not know fleet names.
- `load_project` warns "no copy/ directory; site will be structure only" or "copy/ has no .md/.txt/.json files" and still returns. It does not refuse iseark, teavital, or an elixir host.
- `init` scaffolds any path the person types. It refuses to overwrite a non-empty folder unless `--force` is passed. It does not check the fleet table.
- `compose` plans from the project's real copy, can stop at `structure.json` with `--plan`, and does not write `library/ledger.json`.
- The offline planner states that nothing in means nothing rendered. The checker fails visible SAMPLE, lorem, placeholder, invented reviews, and awards.
- `serve` prints a localhost URL and listens on `127.0.0.1`. It exits if `index.html` is missing.
- `check --expect-noindex` is how a finished local folder is judged. A noindex build writes `robots.txt` with `Disallow: /` and does not write a sitemap.
- `library bind --live` is the publish command. This screen does not call it. The ledger already marks `warmth-authority` live on `movelixir.com`.

`sites/demo-local`, `sites/demo-local-compose`, `sites/demo-local-ai`, `sites/demo-local-plan`, `sites/bench-harbor-tearoom`, and `sites/assembled` are output folders. They are not extra domains and they are not a second allow list.

## 5. Proposal

The smallest surface is one localhost page, stdlib only, no new package. It shells out to the commands above. It does not open MochaHost, Cloudflare, or a registrar. It does not create a project folder.

May stage (the only rows with Plan, Compose local, and Preview):

| Project | Why it may be staged | Still refused |
| --- | --- | --- |
| `projects/demo-local` | `brief.md` and a copy pack: `commands.md`, `faq.md`, `overview.md`. | Indexable build, a fleet host, deploy, `library bind --live`. Stays noindex. |
| `projects/bench-harbor-tearoom` | `brief.md` and a copy pack: `contact.md`, `hours.md`, `menu.md`, `overview.md`. | Same, and the brief already forbids index, deploy, and links from live lanes. Local compose only. |

Blocked. The UI shows every row. The reason is the block. No control.

| Name | Reason |
| --- | --- |
| iseark.com | WordPress. Fleet table: active live news site. No `projects/iseark` and no copy pack. Do not invent a page. |
| teavital.com | WordPress (OceanWP in the fleet table). Active tool sandbox, noindex. No copy pack. Do not restage the yoga build as a SpiderCaster page. |
| bradleybrandfurniture.com | WordPress in the kinds line. Fleet table: paused, live. No copy pack. |
| buyfigs.com | WordPress in the kinds line. Fleet table: paused, live. No copy pack. |
| chopncut.com | Fleet table: paused live WooCommerce store, files-only. No copy pack. |
| rareplantbid.com | Fleet table: paused, pull only, never test. No copy pack. |
| fruitaholics.com | Fleet table: paused, live noindex. One of the five live-noindex rows. No copy pack. |
| jackcancode.com | Fleet table: paused, live noindex. No copy pack. |
| lucentoils.com | Fleet table: paused, live noindex. No copy pack. |
| lmnator.com | Fleet table: paused, live noindex, on the do-not-test list in that row. No copy pack. |
| janustea.com | Fleet table: paused, live noindex. No copy pack. |
| figidk.com | Fleet table: paused park. The FigIDK app is local-only and not deployed. Not a SpiderCaster project. |
| figpollen.com | Fleet table: paused park, closed. No copy pack. |
| buypollen.com | Fleet table: paused park, closed. No copy pack. |
| okoils.com | Fleet table: paused park stub, hold until owned photos exist. No copy pack. Do not invent a page to fill the hold. |
| mdrater.com | Fleet table: paused park stub. No copy pack. |
| modelraters.com | Same row as mdrater. Park stub. No copy pack. |
| floelixir.com | Elixir. Fleet table: paused, empty, local template tests only. No SpiderCaster copy pack. Those tests are not `projects/floelixir/copy`. |
| elitelixirs.com | Elixir hub on the same paused row. No copy pack. |
| Seven elixir parks | Same paused row. Frozen until floelixir passes a checker, as that row writes it. The table does not name the seven hosts. No copy pack. Do not invent the pages or the hostnames. |
| recovelixir.com | Named in `ENVIRONMENT_GAPS.md`, not as its own fleet-table row. No project and no copy pack. The table's short name `recov` is not verified here as this hostname. Blocked either way. |
| movelixir.com | No copy pack. `library/ledger.json` has `warmth-authority` live on this host. Do not stage it and do not bind that mold again. The fleet table lists short name `mov` under empty domains and does not spell this host. Not verified as the same name. Blocked either way. |
| adapt, bang, biom, boost, gain, immun, max, metab, mobil, mov, pow, prim, recov, thriv, trim | Fleet table: 15 empty elixir names, unassigned, no pages until Keith decides. The table does not spell full hosts. No copy pack. This screen does not decide for him by generating a page. |
| figsale.com | Fleet table: empty, no pages until Keith decides. No copy pack. |
| pcoir.com | Fleet table: empty, no pages until Keith decides. No copy pack. |
| webuymaga.com | Fleet table: empty, no pages until Keith decides. No copy pack. |
| weseark.com | Fleet table: empty, no pages until Keith decides. No copy pack. |
| wesearch.com | Fleet table: empty, no pages until Keith decides. No copy pack. |
| bbfur.com | Fleet table: paused. "Content staged" in that row is the old builder, not a SpiderCaster copy pack. No `projects/bbfur/copy`. |
| bradleylumbercompany.com | Fleet table: paused. Same "content staged" wording. Public DNS for bradleylumber.com is undecided in that row. Neither name has a copy pack. |
| salineriverworkshop.com | Fleet table: paused. No copy pack. |
| figroots.com | Fleet table: hands off, never edit, DNS and registrar only. |
| slpwow.com | Fleet table: hands off, never edit. |
| wowtherapies.com | Fleet table: hands off, never edit. |
| dailyscar.com | Fleet table: paused, no owner named. No copy pack. |

`demo-hero.example`, `demo-stage.example`, and `harbor-test.example` are ledger rows with `live` false. They are not folders under `projects/` and they are not fleet domains. The list does not enable them.

A new allow row appears only after a real copy pack exists under `projects/<name>/copy/` as `.md`, `.txt`, or `.json` that is not the `init` README. This report does not add that folder.

## 6. 4Cs+ test

On a phone-width window (360, 390, and 412):

- One column. The reason wraps under the name. No sideways overflow.
- Body text 18px. Chrome 16px. Plan, Compose local, and Preview are at least 44px. Blocked rows have no control, so a tap cannot start a build.
- Contrast 4.5:1 for the reason text. A red row alone is not the block. The words of the reason are the block.
- One h1, "Staging list". A skip link moves to Blocked. If a sticky header shows the two counts, it stays within the chrome floor.

On a built page:

- A blocked name produces no HTML, no `structure.json`, and no `sites/` folder. That absence is the pass. An `index.html` for a blocked name is the fail.
- After Compose local on an allowed project only: `check <out> --expect-noindex` must pass, and `visit` measures 390 and 1280 when Playwright is installed. Expect `robots.txt` with `Disallow: /`, no sitemap, one h1, relative canonical, WebSite JSON-LD, no aggregateRating, and no claim that is not in that project's copy. The harbor bench stays unlabeled as a real business. Those check scores were not re-run for this report. Not public as a new measurement.

## 7. Risks

- Calling `init` on a fleet name, then building it. The generic brief and `copy/README.md` would become visible text. That is invented structure, not a copy pack.
- Reading "content staged" on bbfur.com or bradleylumbercompany.com as permission to compose. It is not this engine's copy.
- Treating floelixir local template tests, or movelixir.com's existing HTML, as a copy pack.
- Generating "contextually relevant content" the way the Webflow builder does, which would invent a page for an empty elixir name.
- Hiding the reason in a tooltip, a collapsed row, or a color. On a phone the name would look available.
- A failed `compose` that still shows Preview. Preview must stay off until `index.html` exists, and the CLI error must stay on the row.
- `serve` described as localhost while a future change binds a public interface. Today's `serve` uses `127.0.0.1`. This screen must not change that.
- `library bind --live`, `build --indexable --host`, or a host push. Any of those turns a staging list into a deploy. They are not on this screen.
- Binding `warmth-authority` while picking a mold for an allowed project. The ledger already has it live on movelixir.com.
