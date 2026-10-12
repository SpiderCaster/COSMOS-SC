DONE 2026-10-01

Renderer head now emits a relative canonical link (the page html filename, no domain), a WebSite JSON-LD script whose name and description are copied from site meta (no aggregateRating, review, address, or telephone), and og:image only when the page hero already has a local relative image. noindex stays when the caller passes it. The homepage hero stays the only h1. A hero or gallery img with no alt text on the IR gets a non-empty alt so the new row can pass.

check_site adds fail-closed rows canonical, json_ld, description, one_h1, and img_alt. A page with no img still passes img_alt. Header, hero, favicon, remote image, noindex, and ungrounded_claim are unchanged. copy_text stays optional. Staged pages stay noindex. No publish and no --live.

py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok

py -3.14 lib\check_claims_selftest.py
claims selftest ok
