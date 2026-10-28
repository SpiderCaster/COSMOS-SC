STATUS: STARTED 2026-10-01

Read `lib/render.py` only. Did not edit Python, `stage/`, or `library/rules/mobile.json`. `library/resources/MOBILE.md` was not on disk, so there is no contradiction to record.

- skip_link enforced. `render_page` emits `<a class="skip" href="#main">Skip to content</a>` and `<main id="main">`.
- target_44 enforced. `.btn` and `.nav-links a` set `min-height:44px`. `.nav-toggle` sets `width:44px;height:44px` (border-box), not the property `min-height`. The 44px target is already in the emitter.
- summary_44 pending. `summary` is padding `16px 18px` with no `min-height`.
- focus_visible pending. The only author outline is `.form input:focus,.form textarea:focus`. There is no `:focus-visible` rule. `.skip:focus` only sets `top`.
- safe_area_header enforced. `.site-header` sets `padding-top:env(safe-area-inset-top)`. The 860px block does not remove it.
- safe_area_footer pending. `.site-footer` is `padding:32px 0`. `env(safe-area-inset-bottom)` is on the 860px `.nav-links` drawer, not the footer.
- reduced_motion enforced. `@media(prefers-reduced-motion:reduce)` sets `.reveal{opacity:1;transform:none;transition:none}` and `transition:none` on `.site-header` and `.btn`.
- no_remote_img pending. `_local_image_src` drops `http://`, `https://`, and `//` for the hero and the about panel. Gallery still writes `it["src"]` with no remote check.

Opened https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html (SC 2.5.5, 44 by 44 CSS pixels).

STATUS: DONE
enforced: 4
pending: 4
