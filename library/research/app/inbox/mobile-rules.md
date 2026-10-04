STARTED
2026-10-01
Task: SpiderCaster mobile rule pack for the seats. Seat card library/resources/MOBILE.md. Rule file library/rules/mobile.json, schema spidercaster-mobile-rules/1. After this note, wait 2 minutes, then read lib/render.py at @media (max-width:860px) and lib/triggers.py if it exists. Only state a rule the renderer actually enforces. If height:168px is still in the renderer, the hero size rule stays pending. Do not edit Python. Do not publish. No crew. No secrets. Never delete.

STATUS: STARTED

DONE
2026-10-01
Waited 2 minutes, then read lib/render.py and lib/triggers.py. Did not edit Python. Did not publish. No crew. No secrets. Did not delete.

lib/triggers.py exists. review(html) returns ok and hits. It does not write a file. Seat hands do not import it.

After the wait, .hero-visual is aspect-ratio:16/9 and height:auto. height:168px is not in the renderer. The 16/9 rule is not pending. At min-width:861px the hero leaves that ratio (height 320px, bold 380px).

@media(max-width:860px) is the phone sheet. It sets .reveal{opacity:1;transform:none}. section and h1,h2 set scroll-margin-top:72px. Skip, button, brand, nav links, and footer links are min-height 44px. The menu button is 44 by 44. _about_panel omits an empty side column. The stylesheet still contains the selector .about-panel, so check no_empty_panel and review empty_panel still match that text. Remote hero and panel images are dropped. assemble defaults to noindex. Staged render stays noindex.

Wrote library/resources/MOBILE.md and library/rules/mobile.json (spidercaster-mobile-rules/1).
