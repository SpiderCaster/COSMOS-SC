# Seven hands

One site, seven seats, in this order. A seat calls only its hands. No seat publishes.

Seat wrappers and skills: `library/seats/`. Hand functions: `lib/hands/` (`HANDS`). Resource map: `library/resources/INDEX.md`. Why the seats are shaped this way: `library/research/BUILDER_PATTERNS.md`. Harness allowlists: `mcp/HARNESS_CONFIGS.md`.

| # | Seat | Hands | Stops when |
|---|---|---|---|
| 1 | Architect | read the brief, `frame_pick` (or leave copy order), pick one mold, bind it as a draft | the brief is empty, the named frame is missing, or the mold is already live on another site |
| 2 | Content | read `copy/` and cite each block file | there is nothing to say, or a block file sits outside `copy/`; it does not invent the missing facts |
| 3 | Frontend | offline plan, then render | the planner has no copy blocks |
| 4 | Graphics | local assets only | an asset url is remote |
| 5 | Visual critic | `check` with noindex | any FAIL |
| 6 | SEO | one mold for this site, not live yet | the checker failed meta or sample rules |
| 7 | Deployer | write `crew-ticket.json` | never uploads; `library bind --live` is the Keith click |

## Where the other builders pointed

Claude Code and Cowork win by giving an agent a short allowlist and making it verify before it claims done. Perplexity wins by reading sources before it draws a structure. Wix wins by starting from one template and then editing sections, not by restyling a demo in place. SpiderCaster keeps those three and drops the part that ships the vendor demo.

## Templates

* Vendor frames (OceanWP, GeneratePress) and their photos live in the vault (`SPIDERCASTER_VAULT`, default `V:\streams\webdev\vendor-vault`). They are not in this package.
* A site wears at most one vendor frame, and only as the parent of a mutation. A mix cites two or more parents and is not an as-is frame.
* The package ships molds we made: `scratch`, `mutate`, or `mix`. A mutation records a new palette, type-lead, and nav.
* A mold or frame that is live on one site is refused on a second live site.

```
python spidercaster.py library index
python spidercaster.py library mold --id bistro-sans --origin mutate --parent owp:restaurant --palette #1f6f5b --type-lead sans --nav top-bar
python spidercaster.py crew run projects\demo-local --site demo-local.example --scratch --out sites\demo-local-crew
python spidercaster.py library bind --site demo-local.example --mold demo-local-example --live
```

The last command is the one that marks a site live. It fails if that mold is already live somewhere else.

`crew run` calls the hand functions in `lib/hands/`. It stops at the first FAIL and still writes the ticket. Deployer stays last, because that hand writes the ticket. When cDeck has saved a seven-seat workflow, `crew run` reads it from `SPIDERCASTER_PROFILE_ENGINE` or from `live\state\profiles\website\engine.json`. A missing file keeps the package order. The selftest passes an explicit order so it does not follow that file.
