# SpiderCaster tool build — shared brief

Every builder and every judge gets this file unchanged.

SpiderCaster tools are static parts. The spec is `V:\streams\webdev\templates\components\catalog.jsonl` (208 rows). Each row targets spidercaster. `source_ref` is a sighting. `reuse` is reimplement-only. Do not copy HTML, CSS, text, or images from that page.

Parts already on disk: `V:\streams\webdev\tools\parts\`. A catalog id is built when some manifest's `catalog_ids` contains it. The unbuilt rows are `V:\A\Ai\spidercaster\working\library\tools\MISSING.json`. Build only the rows assigned to you. Do not edit a folder that already claims the catalog id.

One folder per row:

`V:\streams\webdev\tools\parts\<family>\<tool_id>\`

Files: `manifest.json`, `part.css`, `snippet.html`, `demo.html`, `README.md`. Add `part.js` only when `needs_js` is true.

Rules:

- Vanilla CSS and JS. No network, no fonts, no images, no libraries, no PHP.
- Class prefix `sc-`. Do not restyle `body`, `a`, or `h1` globally.
- Body text and buttons at least 18px. Chrome at least 16px. Tap targets at least 44px. Text contrast at least 4.5:1.
- Usable at 360px and 1280px. No sideways overflow at 360px.
- Visible words are the part `name`, `summary`, and obvious controls (Menu, Close, Search). No lorem, sample, or placeholder.
- The catalog `outline` is the structure. The markup is new.

`manifest.json` fields: `tool_id`, `family`, `name`, `version` `1.0.0`, `seat` (the route), `catalog_ids` exactly `[catalog_id]`, `targets` `["spidercaster"]`, `files`, `deps` `[]`, `images` `none`, `checks` with `type_floor_min_px` 16, `tap_target_px` 44, and `result` `not-run`.

`demo.html` is a full page: doctype, charset, viewport, title, one style block that is the part CSS, the snippet, and the script if any. `snippet.html` is the fragment only.

A question stops the slice. Judges are read-only and answer KEEP or CHANGE:

- LUNA (MAX) on Codex, sandbox read-only. Not OpenRouter chat.
- GLM 5.3 Flash: `pi.cmd -p --provider zai --model glm-5.3-flash --tools read --no-session`.
- Muse Spark 1.3 contributor (MAX): OpenRouter pin `meta/muse-spark-1.3-contributor`, routing off, allow_fallbacks false, reasoning effort max.

On a split, Luna's line decides. The other two lines stay written beside it.
