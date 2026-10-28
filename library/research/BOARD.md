# SpiderCaster build board

Coordinator finished. Statuses below are the closing poll, not a history log.

Last poll: cycle 22, then a closing read of inbox/preview.md. Eight inboxes contain DONE. preview still contains only STARTED (2026-10-01 13:53:45). Poll interval was 30 seconds. Stopped because the 12-minute window ended, not because all nine were DONE.

## Ownership

| Agent | Owns | Inbox | Status |
| --- | --- | --- | --- |
| how-pro | library/research/HOW_PRO_BUILDERS.md, inbox/how-pro.md | inbox/how-pro.md | DONE |
| wrappers | library/seats/*/WRAPPER.md, library/research/WRAPPERS_BUILT.md, inbox/wrappers.md | inbox/wrappers.md | DONE |
| environment | library/resources/ENVIRONMENT.md, library/research/ENVIRONMENT_GAPS.md, inbox/environment.md | inbox/environment.md | DONE |
| hands | lib/hands/__init__.py, lib/hands/selftest.py, library/research/HANDS_CHANGELOG.md, inbox/hands.md | inbox/hands.md | DONE |
| patterns | library/research/RESOURCES_PATTERNS.md, inbox/resources-patterns.md | inbox/resources-patterns.md | DONE |
| local | library/research/RESOURCES_LOCAL.md, inbox/resources-local.md | inbox/resources-local.md | DONE |
| visual | library/research/RESOURCES_VISUAL.md, inbox/resources-visual.md | inbox/resources-visual.md | DONE |
| coder | lib/check.py, library/seats/graphics/SKILL.md, library/seats/visual/SKILL.md, library/research/BUILD_STATUS.md, inbox/coder.md | inbox/coder.md | DONE |
| preview | preview/**, library/research/PREVIEW_RESULT.md, inbox/preview.md | inbox/preview.md | STARTED |

## Product rules

- Seven seats: architect, content, frontend, graphics, visual, seo, deployer.
- crew run does not publish. Publish is Keith's library bind --live.
- Package molds only. Vault OceanWP/GeneratePress never exported.
- No invented copy. No stock hotlinks. No secret printing.
- Demo proof project is projects/demo-local. floelixir and recovelixir have briefs only until a copy pack exists.
- Hero convention the hands agent was told to implement: project file assets/hero.png|jpg|jpeg|webp copied into the output. Confirm whether HANDS_CHANGELOG.md actually says that.

## What landed

- visual: RESOURCES_VISUAL.md names floelixir-hero.png as the keeper among four local 2026-10-01 image-test PNGs, records that no image API was called and nothing was published, and says HANDS_CHANGELOG.md did not exist so the proof filename used there is assets/hero.png.
- wrappers: WRAPPERS_BUILT.md says all seven seat WRAPPER.md files were replaced to match lib/crew.py ROLES, with no new hand name, and the deployer wrapper still only writes crew-ticket.json and does not publish.
- local: RESOURCES_LOCAL.md says movelixir.com is the only elixir site already built, flo and reco stay briefs until a copy pack exists, the safe proof project is projects\demo-local, credentials.env was not opened, and publish is out of scope.
- coder: BUILD_STATUS.md says check_site now fails closed on site_header, hero_visual, favicon_link, favicon_svg, and relative_img, graphics SKILL.md now allows one Keith-asked local image save, visual SKILL.md was not edited, and both hands selftest and crew selftest printed ok with exit 0.
- how-pro: HOW_PRO_BUILDERS.md is a 2026-10-01 public-docs read and states the SpiderCaster adoption baseline as seven seats, the named hands, three package molds, and a render that already emits a sticky header, mobile sheet, hero visual, and favicon.svg, with spidercaster.py image outside the crew.
- environment: ENVIRONMENT_GAPS.md says a local noindex run of projects\demo-local is not blocked, while floelixir and recovelixir have briefs but no copy packs, movelixir has built HTML but no engine-readable copy pack and warmth-authority is already live there, and the public snapshot ships only demo-local and bench-harbor-tearoom.
- hands: HANDS_CHANGELOG.md does say the hero convention: before assemble, render copies the first existing project file assets/hero.png, assets/hero.jpg, assets/hero.jpeg, or assets/hero.webp into the output as assets/hero.<ext>, rejects remote and escaping paths, leaves the letter mark if none exist, and the selftest printed hands selftest ok. No new public hand.
- patterns: RESOURCES_PATTERNS.md records opened public docs for sticky positioning, the viewport meta tag, and prefers-reduced-motion, says search snippets were not used as citations, and says not to ship those pages' HTML or CSS.
- preview: not opened. inbox/preview.md never contained DONE, so PREVIEW_RESULT.md was not read.

## Conflicts (two writers, contradictory instructions)

No two-writer overlap and no contradictory instructions across owners. Coordinator wrote only BOARD.md and inbox/coordinator.md.

Timing, not a second writer: visual's first 40 lines say HANDS_CHANGELOG.md did not exist; hands later wrote that file and it does describe the hero copy. Coder's inbox still begins with STARTED and then says Done; this board counts that as DONE. Patterns keeps an earlier STARTED line plus a later DONE line.

## Parent should do next

Do not publish. Do not run library bind --live. Do not build floelixir or recovelixir until a real copy pack exists. Do not apply floelixir-hero.png to a live page.

No selftest needs a rerun from this board. HANDS_CHANGELOG.md quotes `hands selftest ok`. BUILD_STATUS.md quotes `hands selftest ok` and `crew selftest ok`.

Read `V:\a\Ai\spidercaster\working\library\research\PREVIEW_RESULT.md` next. That file is on disk, but inbox/preview.md was still only STARTED at the closing poll, so this board does not mark preview DONE and does not treat the result as confirmed.

A local preview directory does exist and was not confirmed by the inbox. `V:\a\Ai\spidercaster\working\preview\demo-hero-out\` lists index.html, favicon.svg, site.json, and crew-ticket.json. It does not list an assets directory. The sibling source `V:\a\Ai\spidercaster\working\preview\demo-hero\` lists assets\hero.png, brief.md, and copy\. Open the result note before treating index.html as a pass. The proof project named by local research remains projects\demo-local, not this preview folder.

## Parent rerun

After this board closed, the hero hand was already on disk and the preview was built again. `hands selftest ok`, `crew selftest ok`, and `crew run` on `preview\demo-hero` all exited 0. `preview\demo-hero-out\assets\hero.png` is present (223763 bytes) and `index.html` references `src="assets/hero.png"`. Still noindex. Still not published.
