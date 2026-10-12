STARTED
2026-10-01
Task: join wrapped plain lines into one paragraph in parse_markdown, and cut plan_offline meta description on the last sentence end inside 160 characters. No publish. No site folder. No edits to render, check, or frames.

DONE
2026-10-01
parse_markdown joins consecutive plain lines with one space. A blank line starts a new paragraph. Bullets, numbered lines, headings, and blockquotes stay out of that paragraph. Question lines stay questions; following plain lines join into the answer until a blank line, the next question, or a non-plain line. plan_offline meta description cuts on the last . ! or ? inside 160 characters, else the last space. No new sentence, award, or review. Demo overview description is 134 characters and ends at "static site." Hero subhead stays the full paragraph. No publish. No site folder. render.py, check.py, and frames.py were not edited.

py -3.14 -m lib.ingest
ingest selftest ok

py -3.14 -m lib.offline
offline selftest ok

py -3.14 -m lib.frames
frames selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok
