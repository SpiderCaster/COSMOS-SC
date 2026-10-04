STARTED
2026-10-01
Task: Harbor menu renders an h2 "Menu" and then an h3 "Menu". If a menu group name equals the section title, leave the group name empty. Do not emit an h3 when the group name is empty. Keep items and prices. Do not change SEO tags, the hero button rule, or HANDS. No publish. No crew. Do not edit stage/ or projects/.

DONE
2026-10-01
plan_offline leaves a menu group name empty when it equals the section title. Items and prices stay. The renderer emits no h3 when that group name is empty. A group name that differs from the title still gets an h3. Did not publish. Did not run crew. Did not edit stage/ or projects/. Did not change SEO tags, the hero button rule, or HANDS.

py -3.14 -m lib.offline
offline selftest ok

py -3.14 -m lib.hands.selftest
hands selftest ok
