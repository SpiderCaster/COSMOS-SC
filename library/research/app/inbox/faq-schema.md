STARTED
2026-10-01
Task: emit FAQPage JSON-LD from faq section items already on the page. No invented questions. No publish. No edits to lib/offline.py, lib/ingest.py, mcp_server.py, or stage/.

DONE
2026-10-01
render_page emits a second application/ld+json script with @type FAQPage only when a faq section has items whose q and a are both non-empty. Question name and Answer text are copied from those items. Empty answers are skipped. No complete pairs means no FAQPage script. No aggregateRating, review, or address.

check_site adds faq_schema. If the html contains FAQPage, every Question name in that JSON must appear in the visible text, or the row FAILs. A page with no FAQPage passes. canonical, json_ld, description, one_h1, img_alt, noindex, and ungrounded_claim are unchanged. No publish and no --live.

py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok
