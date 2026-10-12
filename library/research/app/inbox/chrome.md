STARTED
2026-10-01
Task: remove invented chrome. Full nav headings, no Read on, no About on untitled leftovers, contact body drops exact phone/email/address, no Built with SpiderCaster line. No publish. No ingest.py. No stage/.

DONE
2026-10-01
Nav labels keep the full heading. Header links may wrap. Hero primary uses the next section title, or the first three words of the hero subhead when that title is empty. "Read on" is not hardcoded. Leftover hero paragraphs keep an empty title, and an empty title does not render an h2. Contact body drops a paragraph that is exactly the chosen phone, email, or address; the phone stays in the phone field. The visible "Built with SpiderCaster" line is gone. The noindex comment stays. Canonical, JSON-LD, one h1, and FAQPage were not weakened. No reviews invented. No publish. ingest.py and stage/ were not edited.

normalize_data was still rewriting an empty about title to About, and an empty nav was title-casing the id "about". Those two lines in lib/ir.py were cleared so the empty heading stays empty. Frame repair no longer title-cases an empty heading into the nav.

py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok
