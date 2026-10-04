STARTED
2026-10-01
Task: join indented wrapped lines into the previous bullet or numbered item in parse_markdown. A blank line ends the item. Do not publish. Do not edit stage/, lib/render.py, or lib/check.py.

DONE
2026-10-01
parse_markdown joins an indented line that is not a new list marker, heading, or blank line onto the previous bullet or numbered item with one space. A blank line ends that item. Those continuation lines are not a separate paragraph. Consecutive plain lines still join into one paragraph. A wrapped price row joins its note onto the price desc. No publish. stage/, lib/render.py, and lib/check.py were not edited.

py -3.14 -m lib.ingest
ingest selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok
