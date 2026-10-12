DONE 2026-10-01

check_site gained optional copy_text="". Empty copy_text adds no row. Non-empty copy_text fails ungrounded_claim when visible page text has a star rating (digit, optional decimal, /5, or a number then star/stars), or the phrase testimonial, customer review, or award-winning, and that same phrase is absent from copy_text (case-insensitive). Bare review is not a claim. Header, hero, favicon, remote-img, noindex, and type checks are unchanged.

py -3.14 lib\check_claims_selftest.py
claims selftest ok

py -3.14 -m lib.hands.selftest
hands selftest ok
