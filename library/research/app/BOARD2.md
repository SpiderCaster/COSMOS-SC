# SpiderCaster app board — wave 2

Coordinator running. Statuses below are the latest poll, not a history log.

Last poll: cycle 14 at 2026-10-01 15:02:24. Seventeen inboxes said DONE. skill_read had no inbox file, and `lib/skill_read.py` was already on disk. Cycles 5 through 13 were the same seventeen DONE and skill_read WAITING. Window ended 15:02:24.

A read at 15:02:40 found `inbox/skill-read.md` with a DONE line. All 18 listed inboxes now say DONE. Polling stopped. No further cycle.

## Ownership

| Agent | Owns | Inbox | Status |
| --- | --- | --- | --- |
| skill_read | lib/skill_read.py | inbox/skill-read.md | DONE |
| hook_match | lib/hook_match.py | inbox/hook-match.md | DONE |
| perm_rule | lib/perm_rule.py | inbox/perm-rule.md | DONE |
| tool_search_local | lib/tool_search_local.py | inbox/tool-search.md | DONE |
| seat_tools | lib/seat_tools.py | inbox/seat-tools.md | DONE |
| seat_gate | lib/seat_gate.py | inbox/seat-gate.md | DONE |
| layer_read | lib/layer_read.py | inbox/layer-read.md | DONE |
| code_refuse | lib/code_refuse.py | inbox/code-refuse.md | DONE |
| mold_panel | lib/mold_panel.py | inbox/mold-panel.md | DONE |
| session_mark | lib/session_mark.py | inbox/session-mark.md | DONE |
| seo-engine | lib/render.py, lib/check.py | inbox/seo-engine.md | DONE |
| how-seo | library/research/app/HOW_SEO.md | inbox/how-seo.md | DONE |
| stage-harbor | stage/harbor, library/research/app/STAGE_HARBOR.md | inbox/stage-harbor.md | DONE |
| stage-demo | stage/demo, library/research/app/STAGE_DEMO.md | inbox/stage-demo.md | DONE |
| content-quality | library/research/app/CONTENT_QUALITY.md | inbox/content-quality.md | DONE |
| seo-stage | library/research/app/SEO_STAGE.md | inbox/seo-stage.md | DONE |
| find-photos | library/research/app/RESOURCES_PHOTOS.md | inbox/find-photos.md | DONE |
| coder2 | library/research/app/APP_STATUS2.md | inbox/coder2.md | DONE |

## Product rules

- App first. Staged sites are engine tests, not a launch.
- Staged pages stay noindex.
- No library bind --live.
- No invented reviews.
- Photos are local files or a letter mark. No stock hotlink.
- Seven seats stay architect, content, frontend, graphics, visual, seo, deployer.
- Crew does not bind the library live.

## What landed

A deliverable is opened only after that owner's inbox says DONE. A mention of the word DONE inside a STARTED note is not a completion. One sentence below is the first sentence in the first 25 lines of that deliverable.

- skill_read (`lib/skill_read.py`): Read one SKILL.md.
- hook_match (`lib/hook_match.py`): Match a Claude Code hooks object.
- perm_rule (`lib/perm_rule.py`): Match permission rules.
- tool_search_local (`lib/tool_search_local.py`): In-memory tool catalog search.
- seat_tools (`lib/seat_tools.py`): Offline subagent tool allowlist.
- seat_gate (`lib/seat_gate.py`): Refuse a hand unless the caller is that seat.
- layer_read (`lib/layer_read.py`): Read the first page layer list from out/site.json.
- code_refuse (`lib/code_refuse.py`): Refuse to emit a code file.
- mold_panel (`lib/mold_panel.py`): Read one mold's package tokens.
- session_mark (`lib/session_mark.py`): Append one local session line.
- seo-engine (`lib/render.py`): Deterministic renderer: site IR -> static HTML.
- how-seo (`library/research/app/HOW_SEO.md`): Read 2026-10-01 from public Google Search Central and MDN.
- stage-harbor (`library/research/app/STAGE_HARBOR.md`): Quality notes for one draft crew run.
- stage-demo (`library/research/app/STAGE_DEMO.md`): Quality read of the staged SpiderCaster build.
- content-quality (`library/research/app/CONTENT_QUALITY.md`): Scored after a three-minute wait on 2026-10-01.
- seo-stage (`library/research/app/SEO_STAGE.md`): Scored after a three-minute wait on 2026-10-01.
- find-photos (`library/research/app/RESOURCES_PHOTOS.md`): Measured 2026-10-01.
- coder2 (`library/research/app/APP_STATUS2.md`): Code-check only.

## Conflicts

content-quality finished while `stage/harbor/out/index.html` was absent, so that score does not cover a harbor page. seo-stage, scored later, found both `stage/harbor/out/index.html` and `stage/demo/out/index.html`. stage-harbor reports a draft crew exit 0. The harbor page was not on disk for the content score and was on disk for the SEO score. No file was overwritten by this coordinator.

coder2's `APP_STATUS2.md` records `lib.skill_read` missing on its pass and its one retry. The module and `inbox/skill-read.md` arrived after that check.

`inbox/index-skill.md` is not one of these 18. It was STARTED and waiting on `lib/skill_read.py` for an INDEX row. It is not counted here.

Inbox names on disk use hyphens. Coordinator writes only BOARD2.md and inbox/coordinator2.md.

## Parent should do next

Read `APP_STATUS2.md` before trusting the skill_read row: that check ran while the module was still absent. Leave stage/harbor and stage/demo as noindex engine tests. Do not bind the library live.
