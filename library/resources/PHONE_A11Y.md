# Phone accessibility

Seat card for pages below 860px. The rule file is `library/rules/phone-a11y.json` (`spidercaster-phone-a11y/1`). A rule is enforced only when `lib/render.py` already emits the CSS or HTML. All eight are enforced. The 44px size is W3C Understanding SC 2.5.5 Target Size (Enhanced), at least 44 by 44 CSS pixels: https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html

- skip_link — enforced — a skip link href="#main" and main id="main"
- target_44 — enforced — buttons, nav toggle, and nav links min-height 44px
- summary_44 — enforced — details > summary min-height 44px
- focus_visible — enforced — :focus-visible outline, not only outline on inputs
- safe_area_header — enforced — header padding-top env(safe-area-inset-top)
- safe_area_footer — enforced — footer padding-bottom env(safe-area-inset-bottom)
- reduced_motion — enforced — prefers-reduced-motion sets .reveal opacity 1 and kills transitions
- no_remote_img — enforced — hero and gallery img src values that start with http://, https://, or // are dropped
