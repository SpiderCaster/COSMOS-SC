# SpiderCaster app board

Coordinator running. Statuses below are the latest poll, not a history log.

Last poll: cycle 1 at 2026-10-01 14:38:15. Fifteen inboxes say STARTED. Three inboxes are not on disk yet (WAITING). None say DONE. Poll interval is 30 seconds. Window ends 14:49:45. Stop early only if all 18 inboxes say DONE.

## Ownership

| Agent | Owns | Inbox | Status |
| --- | --- | --- | --- |
| how-claude | library/research/app/HOW_CLAUDE_TOOLS.md | inbox/how-claude.md | STARTED |
| how-wix | library/research/app/HOW_WIX_SHOPIFY_TOOLS.md | inbox/how-wix.md | STARTED |
| how-code | library/research/app/HOW_CODE_BUILDERS_TOOLS.md | inbox/how-code.md | STARTED |
| tool-doctor | lib/doctor.py, lib/seatpack.py, spidercaster.py | inbox/tool-doctor.md | WAITING |
| tool-claims | lib/check.py, lib/check_claims_selftest.py | inbox/tool-claims.md | STARTED |
| tool-mcp | mcp_server.py | inbox/tool-mcp.md | STARTED |
| tool-sandbox | lib/sandbox.py | inbox/tool-sandbox.md | WAITING |
| hands | lib/hands/__init__.py, lib/hands/selftest.py | inbox/hands.md | STARTED |
| skills | library/seats/*/SKILL.md | inbox/skills.md | STARTED |
| wrappers | library/seats/*/WRAPPER.md | inbox/wrappers.md | WAITING |
| env-index | library/resources/INDEX.md | inbox/env-index.md | STARTED |
| env-sandbox | library/resources/SANDBOX.md, library/resources/REQUIREMENTS.md | inbox/env-sandbox.md | STARTED |
| find-mcp | library/research/app/RESOURCES_MCP_GAP.md | inbox/find-mcp.md | STARTED |
| find-skills | library/research/app/RESOURCES_SKILL_GAP.md | inbox/find-skills.md | STARTED |
| find-tree | library/research/app/RESOURCES_APP_TREE.md | inbox/find-tree.md | STARTED |
| find-env | library/research/app/RESOURCES_ENV_NOW.md | inbox/find-env.md | STARTED |
| coder | library/research/app/APP_STATUS.md | inbox/coder.md | STARTED |
| docs | library/research/app/APP_TOOLS.md | inbox/docs.md | STARTED |

## Product rules

- Seven seats: architect, content, frontend, graphics, visual, seo, deployer.
- Crew does not publish. Publish is Keith's library bind --live.
- No invented copy. No stock hotlinks. No secret printing.
- This wave builds tools, skills, wrappers, and environment only. No site. No flo. No reco.

## What landed

None yet. A deliverable is opened only after that owner's inbox says DONE. A mention of the word DONE inside a STARTED note is not a completion.

## Conflicts

None recorded. Coordinator writes only BOARD.md and inbox/coordinator.md.
