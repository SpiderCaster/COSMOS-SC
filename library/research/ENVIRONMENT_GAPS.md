# Environment gaps

Only gaps that block a local noindex site or a distributable static run. Measured 2026-10-01 on this Windows host. `projects\demo-local` has `brief.md` and three copy files, Python 3.14.0 is on `py -3.14`, and the public snapshot contains that demo. A local noindex run of the demo is not blocked. These are.

## Blockers

1. Floelixir has a brief and no copy pack. `<local-path>` exists (provider ids omitted). There is no `floelixir` project under `<repo-root>\projects`, no `copy` directory beside that brief, and no floelixir folder under `<local-path>`. Sandbox directories `floelixir-gp-marketer`, `floelixir-gp-restored-v2`, `floelixir-owp-restored-v2`, and `floelixir-owp-simpleblog` each have `public` and no `copy` directory. The content hand and the offline planner refuse to invent copy, so this site cannot be built until a real `copy\` pack exists.

2. Recovelixir is the same blocker. `<local-path>` exists (provider ids omitted). No recovelixir project, no `copy` directory, and no build folder were found in those trees.

3. Movelixir cannot be rebuilt by this engine from a copy pack either. `movelixir.com.md` exists (provider ids omitted). `<local-path>` is already-built HTML, css, img, and js, and it has no `copy` directory. That HTML is not a pack the content hand reads. `warmth-authority` is already live on `movelixir.com` in `library\ledger.json`, which blocks a second live use of that mold, separate from the missing copy.

4. A distributable static run cannot produce flo or reco. `<local-path>` has `demo-local` and `bench-harbor-tearoom` only. The snapshot does not add the missing copy packs.

## Not blockers

These were measured and do not block a static noindex crew of `demo-local`, or a peer run of that shipped demo.

- `snapshot-all` was not run. PHP, `wp`, MariaDB, and MySQL are absent. The static engine does not need them.
- `SPIDERCASTER_VAULT` is unset. The default vault folder exists here. Package molds do not need it.
- `XAI_API_KEY` and `OPENROUTER_API_KEY` are unset. `xai_api_key.txt` under the COSMOS live config is absent. The Grok token file and `openrouter_api_key.txt` exist and were not opened. Image prompting is optional. Offline build and crew do not need those keys.
- `library\image-tests` is absent from the public snapshot. `demo-local` does not reference those files.
- No fifth runtime blocker showed up for the demo. The elixir gap is the missing copy, not the interpreter.
