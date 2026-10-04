# SpiderCaster app board — wave 3

Coordinator running. Statuses below are the latest poll, not a history log.

Last poll: cycle 0 at 2026-10-01 15:05:48. Four inboxes said DONE. Six said WAITING.

## Ownership

| Agent | Owns | Inbox | Status |
| --- | --- | --- | --- |
| prose | lib/ingest.py `parse_markdown`; lib/offline.py `plan_offline` description cut | inbox/prose.md | WAITING |
| restage-harbor | stage/harbor engine test | inbox/restage-harbor.md | WAITING |
| restage-demo | stage/demo engine test | inbox/restage-demo.md | WAITING |
| faq-schema | lib/render.py FAQPage JSON-LD; lib/check.py `faq_schema` | inbox/faq-schema.md | DONE |
| seo-stage2 | library/research/app/SEO_STAGE2.md | inbox/seo-stage2.md | WAITING |
| content-quality2 | report path not named in the inbox yet | inbox/content-quality2.md | WAITING |
| coder3 | report path not named in the inbox yet | inbox/coder3.md | WAITING |
| index-skill | library/resources/INDEX.md | inbox/index-skill.md | DONE |
| skill-read | lib/skill_read.py | inbox/skill-read.md | DONE |
| mcp-wave2 | mcp_server.py read-only tools | inbox/mcp-wave2.md | DONE |

## Product rules

- The app is the product. Staged sites are engine tests, not a launch.
- Staged pages stay noindex.
- No library bind --live.
- No invented reviews.
- Seven seats stay architect, content, frontend, graphics, visual, seo, deployer.
- Coordinator writes only BOARD3.md and inbox/coordinator3.md. No Python, no stage output, no skills.

## What landed

A deliverable is opened only after that owner's inbox says DONE. A mention of the word DONE inside a STARTED note is not a completion. One sentence below is from the first 20 lines of that deliverable.

- faq-schema (`lib/check.py`): FAQPage JSON-LD, when present, must use only question strings that are also visible; a page with no FAQPage passes faq_schema.
- index-skill (`library/resources/INDEX.md`): A seat calls only its hands.
- skill-read (`lib/skill_read.py`): Read one SKILL.md.
- mcp-wave2 (`mcp_server.py`): SpiderCaster MCP server - stdio transport, stdlib only (no pip deps).

## Conflicts

mcp-wave2's DONE note says skill_read returns isError missing because lib.skill_read was not on disk. `lib/skill_read.py` is on disk now, `inbox/skill-read.md` says DONE, and `library/resources/INDEX.md` has a `skill_read` row. `mcp_server.py` `tool_skill_read` imports `lib.skill_read` and returns the import error only when that import fails. No file was overwritten by this coordinator.

`lib/render.py` first 20 lines do not mention FAQPage. The faq-schema sentence above is from `lib/check.py`, which the inbox also names. `lib/render.py` emits FAQPage later in the file.

## Parent should do next

Read this board again after the poll window. Leave stage/harbor and stage/demo as noindex engine tests. Do not bind the library live. Do not treat a WAITING row as finished.
