STATUS: STARTED 2026-10-01

Next renderer pass after the phone owner finishes. Write library/research/app/RENDER_NEXT.md. Do not edit lib/render.py or any Python. Do not edit stage/. Do not publish. No secrets. No crew run.

STATUS: DONE 2026-10-01

Wrote library/research/app/RENDER_NEXT.md. Three changes, with selectors and values: letter-mark heroes (`.hero-visual.hero-mark`) stay short under 860px while photo `.hero-visual` stays `aspect-ratio:16/9` and `height:auto`; phone menu stacks `.mi-col` with `.mi-price` on the `.mi-name` line, `.mi-desc` underneath, `.dots` hidden, row `min-height:48px`; `.nav-here` returns as one truncated line, and the `.nav-links` sheet and 44px `.nav-toggle` stay. Small additions: `a, button, summary` `:focus-visible` outline, and `.site-footer` padding-bottom with `env(safe-area-inset-bottom)`. The editor must not start until library/research/app/inbox/render-mobile.md contains DONE, then re-run `py -3.14 -m lib.hands.selftest`, `py -3.14 -m lib.regress`, and `py -3.14 spidercaster.py crew selftest`. No `--live`. No Python edits. No stage edits. No publish.
