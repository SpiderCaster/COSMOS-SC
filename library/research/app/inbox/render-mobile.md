STARTED
2026-10-01
Task: raise mobile page quality under 860px. Hero visual 16/9 height auto, no empty about-panel, scroll-margin, reveal visible without JS, nav nowrap, taller menu and contact rows, tighter wrap and section padding, h1 clamp, 16px inputs. No publish. Do not edit lib/check.py, lib/crew.py, or stage/.

DONE
2026-10-01
Phone CSS in lib/render.py. Under 860px the hero visual is aspect-ratio 16/9 and height auto, with object-fit cover and object-position center. height:168px is gone. Desktop min-width 861px hero grid stays, with hero visual heights 320px and 380px. An about section with no panel content renders the body only, full width. The empty about-panel element is not emitted, and the stylesheet no longer contains that class. section, h1, and h2 use scroll-margin-top 72px. At max-width 860px, .reveal is opacity 1 with no translate, .nav is nowrap, .wrap padding is 0 16px, section padding is 40px 0, and hero padding is 28px 0 40px. Menu rows are min-height 48px, the name column can use the row except the price, and prices stay on one line in var(--price). Contact rows are min-height 44px. h1 clamp minimum is 1.7rem. Inputs and textareas use font-size max(16px, 1rem). noindex, canonical, JSON-LD, the skip link, one h1, and local images were not changed. No publish. lib/check.py, lib/crew.py, and stage/ were not edited.

The first hands and crew runs failed check_site on no_empty_panel because the unused .about-panel rule was still in the CSS. That rule was removed. 168px was not put back. regress did not ask for it.

py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 -m lib.regress
regress selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok
