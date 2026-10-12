STARTED 2026-10-01

Verify the SpiderCaster app wave. No site. No publish. No --live. No image API. No secrets. Do not weaken tests. Never delete. Fixes only after the owner inbox says DONE and a rerun shows a one-line bug. Prefer writing the failure over editing.

Wait 180 seconds, then from <repo-root>:

py -3.14 -m lib.skill_read
py -3.14 -m lib.hook_match
py -3.14 -m lib.perm_rule
py -3.14 -m lib.tool_search_local
py -3.14 -m lib.seat_tools
py -3.14 -m lib.seat_gate
py -3.14 -m lib.layer_read
py -3.14 -m lib.code_refuse
py -3.14 -m lib.mold_panel
py -3.14 -m lib.session_mark
py -3.14 -m lib.hands.selftest
py -3.14 spidercaster.py crew selftest
py -3.14 lib\check_claims_selftest.py
py -3.14 spidercaster.py doctor

If a module is missing, wait 60 seconds and retry that one command once.

DONE 2026-10-01

Thirteen commands passed. `py -3.14 -m lib.skill_read` failed on the first pass and on the one retry: `No module named lib.skill_read`. `lib/skill_read.py` was still absent at 14:53:21. No owner file edited. See library/research/app/APP_STATUS2.md.
