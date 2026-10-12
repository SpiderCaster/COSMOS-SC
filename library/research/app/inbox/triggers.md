STARTED 2026-10-01

Mobile trigger table. `lib/triggers.py` only. Not a site build. No publish. No fetch. No edit to `lib/crew.py`, `lib/render.py`, or `lib/check.py`.

DONE 2026-10-01

`lib/triggers.py` `review(html)` returns `ok` and `hits`. Each hit is `code` and `fix`. `fix` is `none` or `rerender`. `ok` is false when any hit has `fix` `none`.

Case-sensitive text checks:

- `phone_hero_short` — html contains `height:168px`. Fix `none`.
- `phone_hidden` — html contains `.reveal{opacity:0` and no `max-width:860px` media rule sets `.reveal{opacity:1`. Fix `none`. A `prefers-reduced-motion` rule does not clear it.
- `empty_panel` — html contains `about-panel`. Fix `none`.
- `missing_skip` — html does not contain `href="#main"`. Fix `none`.
- `remote_img` — an `img` `src` starts with `http://`, `https://`, or `//`. Fix `none`.

No hits means `ok` true and `hits` `[]`. The module does not fetch a URL and does not write a file.

From `V:\a\Ai\spidercaster\working`:

- `py -3.14 -m lib.triggers` exit 0: `triggers selftest ok`

The selftest asserted a sample with `height:168px` is not ok, and a sample with `aspect-ratio:16/9`, a skip link, and no `about-panel` is ok.
