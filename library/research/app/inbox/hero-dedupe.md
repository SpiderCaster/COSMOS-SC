STARTED
2026-10-01
Task: Harbor hero has two identical Contact buttons, both href #contact. When the secondary matches the primary href or label, set secondary to None. Keep a secondary that goes somewhere else. No publish. No --live. No --frame. Do not edit stage/demo or projects/. Do not copy a hero image.

DONE
2026-10-01
plan_offline drops a secondary that repeats the primary href or label. A secondary that points somewhere else stays. Did not publish. Did not pass --live. Did not pass --frame. Did not edit stage/demo or projects/. Did not copy a hero image. Did not edit lib/render.py.

py -3.14 -m lib.offline
offline selftest ok

py -3.14 spidercaster.py crew run stage\harbor\src --site harbor-test.example --out stage\harbor\out --mold discover-grid
exit 0. Mold discover-grid. No frame. 0 local assets. Ticket says this run does not deploy.

Harbor hero has one button. No second Contact button.

<a class="btn primary" href="#contact">Contact</a>
