# Builder patterns for SpiderCaster

Date: 2026-10-01. Public docs only, plus the live engine named in the brief. No benchmark numbers. Where a page was not fetched cleanly, that is said.

Live order in `lib/crew.py` `ROLES` and `library/CREW.md` is architect, content, frontend, graphics, visual, seo, deployer. The brief lists visual, then SEO, then graphics. This report does not recommend reordering `ROLES`.

Template rule used below: OceanWP and GeneratePress frames and photos stay in the private vault. One vendor frame per site, as-is only. Package molds are scratch, mutate, or mix. A mold or frame already live is refused on a second live site. `Library.package_manifest` reports `vendor_frames: 0`.

## Claude Code

**Mechanism.** A skill is a folder with `SKILL.md`. The description loads up front; the body loads only when the skill is used. `allowed-tools` pre-approves named tools for the turn that invokes the skill. It does not hide other tools. `disallowed-tools` removes tools while the skill is active, then clears on the next user message. A subagent file under `.claude/agents/` has its own prompt and a `tools` allowlist. Omit `tools` and the subagent inherits the subagent tool pool. A tool left off that list is not in the subagent session. `PreToolUse` hooks can deny a call, including when permission mode would otherwise skip prompts. Bundled `/verify` builds and drives the app. It does not treat tests or type checks as proof. It runs only when a person invokes it, so it cannot be preloaded into a subagent.

**Example.** Official skill frontmatter is `allowed-tools: Read Grep`. Official subagent frontmatter is `tools: Read, Grep, Glob, Bash` for a researcher that cannot edit. A subagent `PreToolUse` hook on Bash exits 2 to block a write. `/verify` may write a recipe to `.claude/skills/verify/SKILL.md`; at the repo root that file replaces the bundled skill (Claude Code v2.1.200+).

https://code.claude.com/docs/en/skills
https://code.claude.com/docs/en/sub-agents
https://code.claude.com/docs/en/hooks-guide

**Copy.** Put each seat behind a `tools` allowlist, not an `allowed-tools` grant. Run `check_mod.check_site` in `lib/crew.py` before `crew-ticket.json` can be `ok`. A model sentence is not the gate. A `PreToolUse` deny can block `library bind --live` even if the harness is in bypass mode.

**Do not copy.** Do not treat a skill body as a lock. Do not preload a verify skill and call that done. Do not ship a skill whose supporting files are OceanWP or GeneratePress theme source. Do not let a subagent inherit MCP tools by omitting `tools`.

## Claude Cowork

**Mechanism.** Cowork is the same agent loop as Claude Code, without a terminal. On desktop it reads and writes only folders you connect. Local files, browser actions, and computer use need the desktop app even when the session runs in the cloud. Plugins bundle skills, connectors, and sub-agents. Scheduled tasks are saved prompts. The help center says they run remotely and "can't be tied to a folder on your computer." The same article says a scheduled task that requires local files or apps runs only locally. Projects hold folders, instructions, and memory. Dispatch is one conversation that splits work into child tasks. Each child goes to one Code workspace or one Cowork project. Child tasks do not spawn further children. Cowork and cloud sessions do not read `~/.claude/skills/` on the machine. They load skills enabled on the claude.ai account.

The phrase "one-seat-one-lane" does not appear in the Cowork docs read for this report. The closest documented rule is: one child task, one project or workspace, and no grandchild agents.

https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork
https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork
https://claude.com/docs/cowork/guide/dispatch
https://claude.com/docs/cowork/guide/projects
https://code.claude.com/docs/en/skills

**Copy.** One site directory per `crew run`. Do not mount the vendor vault for content, frontend, visual, SEO, or deployer. The vault is a library-admin path (`Library.accept_snapshot` must stay inside the vault). Dispatch's "children do not spawn children" matches a seat that cannot call another seat's hands. `ROLES` in `lib/crew.py` is that lane list.

**Do not copy.** Do not schedule `library bind --live`. A cloud scheduled task cannot be the publisher and must not be pointed at the vault. Do not give a seat computer use or a browser so it can open a demo site and copy it. Do not rely on a personal `SKILL.md` inside Cowork. Do not run parallel sub-agents that all write the same `sites/` tree. Cowork deletion still asks a person; SpiderCaster publish stays a person, in `library bind --live`, not a permission prompt the model can click.

## Perplexity

**Mechanism.** Perplexity searches, then answers. Each answer has numbered citations to the sources it retrieved. Pro Search reads multiple sources. Research runs dozens of searches and reads hundreds of sources, then writes a report (Help Center: about 2–4 minutes). "Create files and apps" (Pro and above) uses browsing, code execution, and chart or image creation to build reports, spreadsheets, dashboards, and simple web apps, including HTML. The assets help page says specific slide or document templates are "Not currently" supported. Publishing a Computer-built site is a separate step to a `pplx.app` URL, with visibility chosen after the preview. It is not DNS work.

Labs is the older name. The 2025-05-29 launch post was not fetched directly on 2026-10-01 (the URL returned a challenge page). A search-index excerpt of that post says Labs does self-supervised work of about 10 minutes or more, writes code, stores files under Assets, and can deploy simple web apps under the query. The Help Center page above is the current description of that job. No official page read here says Labs locks a design system or refuses invented copy.

https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work
https://www.perplexity.ai/help-center/en/articles/12528830-creating-assets-with-perplexity-overview
https://www.perplexity.ai/help-center/en/articles/20260711-publishing-your-website-to-the-web
https://www.perplexity.ai/hub/blog/introducing-perplexity-labs

**Copy.** No pages until sources exist. For SpiderCaster the sources are `copy/` files, not the web. `lib/ingest.py` `Block` already stores `file`. The content hand should name those files. Empty `copy.blocks` is already a FAIL in `run_job`. Preview before publish matches Computer: the ticket is the preview record; live is a later click.

**Do not copy.** Do not add web search to the content seat. Do not let Research or Labs invent prices, quotes, or hours. Do not generate a one-shot HTML app with no mold. Do not publish to a host from the crew. Do not treat "templates not supported" as permission to freestyle CSS.

## Wix

**Mechanism.** A site starts from one template, or from the AI Website Builder, which asks for purpose and features and generates a design. After that, edits are sections, text, images, and the site theme. Site Design sets a color theme and a text theme. Themed elements follow that theme. Colors can be entered as HEX, RGB, or HSB. Official help: you cannot switch the template of a site that already exists. You start a new site and copy content across. You also cannot switch an existing template site over to the AI builder, and an AI-built site cannot be changed to a different template. Wix Vibe no longer creates new sites. Existing Vibe sites can still be edited. New AI work is Wix Harmony. Vibe's editor adds sections between sections and can apply a theme. Its chat can also restyle many elements at once. That chat is wider than SpiderCaster's mold knobs.

https://support.wix.com/en/article/switching-your-site-template
https://support.wix.com/en/article/wix-editor-creating-an-ai-generated-site
https://support.wix.com/en/article/wix-editor-customizing-your-sites-theme-and-design
https://support.wix.com/en/article/wix-editor-using-and-customizing-your-color-theme
https://support.wix.com/en/article/wix-vibe-an-overview
https://support.wix.com/en/article/wix-vibe-about-the-wix-vibe-editor

**Copy.** Architect binds one mold, then later seats edit sections and tokens. Mold fields already are the theme: `palette` (`#rrggbb`), `type_lead`, `nav`, and `template` in `modern|editorial|bold` (`lib/library.py` `save_mold`, `lib/ir.py` `TEMPLATES`). A live mold is not restyled into a second site. `Library.bind(..., live=True)` already refuses a second live owner.

**Do not copy.** Do not regenerate a vendor frame in place. Do not put a Wix, OceanWP, or GeneratePress theme file in `library/molds`. Do not let a chat prompt set arbitrary CSS. Do not use Wix AI image tools as a stand-in for owned photos. Media on a Wix site is uploaded into that account. SpiderCaster graphics stay on local files. `lib/ingest.py` already drops `htt<local-path>` and `https://` asset URLs.

## Peer: Relume

**Mechanism.** Relume Site Builder is three passes. A short prompt becomes a sitemap (pages and section prompts). The sitemap becomes unstyled wireframes made of library components, with generated copy. A style guide then sets color, type, and UI, and Design View applies that guide across the wireframes. Relume's own docs say to edit the sitemap before generating wireframes, because the section title and description choose the component. The style guide is not the wireframe. Export targets are Figma and Webflow, using Relume's own library, not a vendor demo theme. The sitemap doc URL redirects to `relume.ai`. This report uses the indexed text of that doc plus the style-guide and July 2025 release pages.

https://www.relume.ai/resources/docs/building-a-sitemap-with-ai
https://www.relume.io/style-guide
https://www.relume.io/whats-new/july-2025-release

**Copy.** Structure, then tokens, then render. Architect picks one mold and only sections that `copy/` can fill. Frontend calls `offline.plan_offline` and `render.assemble`. Palette, type-lead, and nav change together on a mutation. That is already `save_mold`.

**Do not copy.** Do not let the model write the page copy. Relume does. Do not import the Relume or Webflow component library into the package. Do not shuffle a new look onto a mold that is already live.

## Peer: v0

**Mechanism.** The v0 API (Vercel, 2026-08-05) creates one chat per app. The chat reads, edits, and runs files in a Vercel Sandbox and returns a preview URL. Follow-ups continue that chat. v0 checks the running app and can fix errors. A design system is stored as a skill (components, tokens, setup, starter app). A request takes at most three skills. Deploy to Vercel is a separate API call, `v0.chats.deploy`. An agent can be given only some operations, for example create, send, resolve, and get preview, and not deploy.

https://vercel.com/blog/introducing-the-new-v0-api

**Copy.** One build, one mold, one output directory. Verify against the rendered files (`check_site`), not against the prompt. The design-system skill should be a package mold JSON plus `tokens_read`, not a downloaded theme. The deployer seat can write `crew-ticket.json` and must not be given a deploy operation.

**Do not copy.** Do not add `v0.chats.deploy` or any host publish tool to `mcp_server.py` `TOOLS`. Do not pass a vendor snapshot in as the starter app. Do not let the agent pull skills from the public web (`skills.sh` is allowed by v0; it is not a source of SpiderCaster molds).

## What to build into SpiderCaster

These eight items name files that already exist, or one settings file whose job is a deny hook. None of them copy OceanWP or GeneratePress source into the package.

1. **Seat allowlists are `tools`, not grants.** In `mcp/HARNESS_CONFIGS.md`, replace the prose role table with one subagent-style allowlist per `ROLES` id in `lib/crew.py`. Architect: `catalog_read`, `tokens_read`, `brand_read`, `mold_list`, `draft_offline`. Content: `brand_read`, `pagemodel_read`, `pagemodel_write`. Frontend: `tokens_read`, `pagemodel_read`, `pagemodel_write`, `render_trigger`. Graphics: `brand_read` only. Visual: `validate_run` only. SEO: `mold_list`, `validate_run`. Deployer: no SpiderCaster tool. Do not add a live-bind tool to `mcp_server.py` `TOOLS`. `allowed-tools` on `SKILL.md` must not be the only fence.

2. **Checker owns `ok`.** Keep `lib/crew.py` `_finish` setting `ok` only from hand statuses, and keep the visual hand calling `check_mod.check_site(..., expect_noindex=True)`. In `SKILL.md`, state that a seat may not say done unless `crew-ticket.json` shows visual PASS and names zero FAIL rows. Do not add a model-writable `ok` field.

3. **Deny publish and vault export in the harness.** Add `<repo-root>\.claude\settings.json` with a `PreToolUse` command hook on Bash. Deny a command that contains `bind` and `--live`, and deny a command that copies `SPIDERCASTER_VAULT` or `vendor-vault` into `library\molds` or `library/molds`. Official hooks: one `deny` wins, including in bypass mode. The hook does not publish anything.

4. **Content cites `copy/` files.** In `lib/crew.py`, the content PASS detail lists each `Block.file` from `ingest.load_project`. A block whose file is not under that project's `copy/` is a content FAIL. Do not add a web-search tool to the content seat in `mcp_server.py`.

5. **Frontend edits tokens and sections, not a new theme.** `pagemodel_write` already limits `role=content` and `role=editor` to patch mode, same section types, no new pages (`mcp_server.py` `TOOL_SPECS`). Keep builder-only `mode=full`. Theme writes go through mold fields in `lib/library.py` `save_mold` (`palette`, `type_lead`, `nav`, `template`) and `tokens_read`. Do not add a tool that reads a vault snapshot and writes CSS.

6. **Graphics stays local.** Do not add an image-generation tool or a stock-URL tool to `TOOLS`. Keep the hotlink drop in `lib/ingest.py` `load_project` and the `no_hotlink` row in `lib/check.py` `check_site`. `Library.accept_snapshot` stays off the MCP tool list. It already refuses a directory outside the vault.

7. **SEO reads the live ledger. It does not bind live.** The SEO hand keeps calling the same rule as `Library.live_conflict` and `Library.bind` (second live owner raises `LibraryError`). Do not call `bind(..., live=True)` from `run_job`. The only live write remains the CLI `library bind --live`, which is the human click documented in `library/CREW.md`.

8. **Package list stays mold-only.** `tool_mold_list` in `mcp_server.py` already returns `package_manifest()["molds"]`. Keep it that way. Do not add `frames.json` or vault photo paths to that tool. A mutation still has to change palette, type-lead, and nav (`save_mold`). A mix still cites two or more parents and is not an as-is frame.

`<local-path>` maps seats to models. It is not a tool allowlist. Do not implement a lane by changing the model name.

## Sources

- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/hooks-guide
- https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork
- https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork
- https://claude.com/docs/cowork/guide/dispatch
- https://claude.com/docs/cowork/guide/projects
- https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work
- https://www.perplexity.ai/help-center/en/articles/12528830-creating-assets-with-perplexity-overview
- https://www.perplexity.ai/help-center/en/articles/20260711-publishing-your-website-to-the-web
- https://www.perplexity.ai/hub/blog/introducing-perplexity-labs
- https://support.wix.com/en/article/switching-your-site-template
- https://support.wix.com/en/article/wix-editor-creating-an-ai-generated-site
- https://support.wix.com/en/article/wix-editor-customizing-your-sites-theme-and-design
- https://support.wix.com/en/article/wix-editor-using-and-customizing-your-color-theme
- https://support.wix.com/en/article/wix-vibe-an-overview
- https://support.wix.com/en/article/wix-vibe-about-the-wix-vibe-editor
- https://www.relume.ai/resources/docs/building-a-sitemap-with-ai
- https://www.relume.io/style-guide
- https://www.relume.io/whats-new/july-2025-release
- https://vercel.com/blog/introducing-the-new-v0-api

Local engine, not public docs: `<repo-root>\lib\crew.py`, `lib\library.py`, `lib\ingest.py`, `lib\check.py`, `mcp_server.py`, `library\CREW.md`, `SKILL.md`.
