STARTED
2026-10-01
Task: fail a page that is still the old low-quality phone layout. Rows on index.html text: mobile_hero, mobile_visible, no_empty_panel, skip_link, scroll_margin. No publish. Do not edit lib/render.py.

DONE
2026-10-01
check_site reads index.html text and adds five rows. Existing rows are unchanged. A letter-mark page can pass. These are CSS and markup rules, not content rules.

mobile_hero FAILs when the html contains height:168px, including when aspect-ratio:16/9 is also present. It PASSes on aspect-ratio:16/9. It FAILs when that ratio is missing. mobile_visible FAILs when a base .reveal rule is opacity 0 and no max-width:860px rule sets .reveal to opacity 1. It PASSes when that phone rule is present, or when .reveal is never opacity 0. .reveal.in does not count. no_empty_panel FAILs when about-panel appears and PASSes otherwise. skip_link FAILs when href="#main" is missing and PASSes when it is present. scroll_margin FAILs when scroll-margin-top is missing and PASSes when it is present.

lib/render.py was not edited. No publish and no --live.

The first selftest run failed while the renderer still emitted about-panel. The row was no_empty_panel. The check was not weakened. After 60 seconds the retry passed.

py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok
