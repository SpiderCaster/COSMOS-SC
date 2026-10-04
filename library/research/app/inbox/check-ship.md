STARTED
2026-10-01
Task: fail closed on missing local img files, a lone About h2, and invented Read on / Built with SpiderCaster chrome. No publish. No edits to lib/render.py, lib/offline.py, lib/ingest.py, or stage/.

DONE
2026-10-01
check_site adds missing_file. A relative img src must be a file beside that HTML. A letter-mark page with no img passes. Remote and non-file schemes are not that row. canonical, json_ld, description, one_h1, img_alt, noindex, faq_schema, and ungrounded_claim were not weakened.

When copy_text is non-empty, an h2 whose text is exactly About fails lone_about if the word About is not in the copy (any case). The same non-empty copy fails invented_chrome when visible text contains "Read on" or "Built with SpiderCaster" and that exact phrase is not in the copy. Empty copy_text adds neither row. No publish and no --live. render.py, offline.py, ingest.py, and stage/ were not edited.

py -3.14 lib\check_claims_selftest.py
claims selftest ok

py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok
