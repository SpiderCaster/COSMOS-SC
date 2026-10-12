STATUS: STARTED 2026-10-01

Read the `@media(max-width:860px)` block in `lib/render.py` and the top of `library/research/app/HOW_MOBILE.md`. Add a dated correction above the old findings. Do not delete those findings. Do not paste a stylesheet. Do not edit Python or stage HTML. Do not publish. Do not claim a phone was measured.

STATUS: DONE

2026-10-01. A correction dated 2026-10-01 is at the top of `library/research/app/HOW_MOBILE.md`. It states that the findings below were measured before the phone pass landed. Every item below is in the current `lib/render.py`, so all ten are listed: photo `.hero-visual` is aspect-ratio 16/9 and height auto; `.hero-visual.hero-mark` on phones is aspect-ratio auto and max-height 140px; no `height:168px`; no `about-panel` class; phone `.reveal` is opacity 1; `.nav-here` is display block on phones, one truncated line; menu `.dots` are display none under 860px; `.hero-cta` is a column and the button is width 100%; `summary` is min-height 44px; footer padding includes `env(safe-area-inset-bottom)`. The old findings were not deleted. No stylesheet was pasted. `lib/render.py` and stage HTML were not edited. No publish. No phone was measured.
