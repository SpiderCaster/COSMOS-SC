# How code builders equip an agent

Read 2026-10-01 from public docs only. A procedure sits next to its URL. If the opened page does not say the step, this file says **not public**. This note is the tool list and the project environment. It does not repeat `library/research/HOW_PRO_BUILDERS.md` (first brief, section catalogs, starter copy, image packs, or the second publish click).

SpiderCaster already exposes CLI verbs in `spidercaster.py` and MCP names in `mcp_server.py` `TOOLS`. The five specs at the end are none of those. They do not call the network, do not publish, and do not load a remote asset.

## v0

**Project.** A VM-backed chat runs in an isolated Vercel Sandbox: project files, the dev server that serves the preview, a terminal, and the agent tools. One chat does not share files, env vars, or processes with another chat. The sandbox is not the production machine. https://v0.app/docs/sandbox

A Project is one app that many chats can share. It shares deployment, hosting, domains, and environment variables. A chat with no Project gets one the first time that chat is published. Folders only group chats; they do not deploy. The folders page also says a Project is "sharing a file system." The sandbox page says chat files do not cross chats. Both sentences are on those pages. How a shared Project filesystem and a per-chat sandbox fit together is **not public**. https://v0.app/docs/projects and https://v0.app/docs/folders

Inside the sandbox: Node.js, and pnpm, npm, yarn, and bun. v0 starts a Next.js, Vite, or generic Node dev server. Environment variables from the connected Vercel project are available to the app and to any agent tool in that sandbox. The filesystem for that chat persists between visits. A pooled sandbox starts with a 30-minute lifetime, keep-alive can add 10 minutes when five or fewer remain, and the cap is 24 hours from creation. Outbound hosts follow Sandbox Network Policy. The default is `allow-all`. Team owners change it in team settings. https://v0.app/docs/sandbox

**Tools the page names.** `Bash` runs in a fresh shell at the project root. The built-in allow list in Auto mode includes read-only inspection (`ls`, `find`, `cat`, `head`, `tail`, `tree`, `wc`, `cd`, `pwd`), search (`grep`, `rg`, `jq`), local git reads, read-only `gh` and `vercel` commands, `echo`, `whoami`, `agent-browser`, and `sleep`. File delete is a separate built-in `Delete` tool. Ask v0 to delete by name so it uses `Delete` rather than `rm -rf`. A full Read or Edit tool schema for v0's own agent is **not public** on the terminal page. https://v0.app/docs/terminal-commands

Other agent actions on the agentic page: web search, browser use (screenshots while it works, including external URLs), automatic fixes for missing files, syntax, runtime errors, and imports, Marketplace tools (Neon, Supabase, Upstash, Stripe, and others) installed from Project menu → Settings → Integrations, and MCP servers. The chat shows tool execution cards. Stop interrupts the agent. https://v0.app/docs/agentic-features

MCP availability and approval are separate. Remote MCP (or a custom server's enabled state) decides whether the tool exists. Ask, Auto, or Full then decides whether the call runs. Full skips allow, ask, and deny rules for both shell and MCP. https://v0.app/docs/MCP and https://v0.app/docs/terminal-commands

The human Code viewer is read-only. Search matches file names and contents. A line comment added to the next prompt carries the file path, the selected lines, the captured code, and the comment. It does not send by itself. A message Diff tab can comment added or removed lines. Writing code is still a chat prompt. https://v0.app/docs/code-editing

Pre-installed agents: open the sandbox terminal and run `claude`. That process can read, edit, and create files in the project, and it can read Vars. Enterprise leaves this off until an admin opts in. Installing other agents in the sandbox is unsupported. https://v0.app/docs/pre-installed-agents

An outside agent can be given `@v0-sdk/ai-tools`. Named groups include chat tools (`createChat`, `sendMessage`, `getChat`, `findChats`, `deleteChat`) and project tools (`createProject`, `getProject`, `findProjects`, `updateProject`, `deleteProject`). Deployment tools exist on that page. The exact deployment function names were not copied here. https://v0.dev/docs/api/platform/packages/ai-tools

Platform file API, not the in-chat tool list: `PATCH /v2/chats/{chatId}/files` creates, updates, or deletes files. `content: null` deletes. Paths are project-relative. Invalid base64 returns 422 before any file changes. https://v0.app/docs/api/v2/reference/chats/update-chat-files

File locks: `locked: true` on a file passed to chat init, or `lockAllFiles: true` on a repo init. Locked files stay readable and are not modified by generation. Lock status persists across sessions. A person can still change a locked file through the API. https://v0.app/docs/api/platform/guides/lock-files-from-ai-changes

**Instructions.** Account instructions: prompt bar +, Instructions, New Instruction, title, rule text, Add. Presets include Be Concise and Plan Mode. Plan Mode writes a plan and waits for approval before code changes. Checked instructions stay on until unchecked. https://v0.app/docs/instructions

The current Projects settings page documents Vercel Project, Integrations, environment variables, GitHub, Template, and Domains. A project Rules or Sources tab is **not public** on that page. https://v0.app/docs/projects

**Permission.** Composer + menu, then the permissions submenu: Ask, Auto (default), or Full. The choice persists across new chats. Rules are three JSON arrays, `allow`, `deny`, and `ask`, shaped as `Bash(<pattern>)` with an optional `:*`. User rules and team rules (team owners only) merge with the built-in list. The longest matching pattern wins. Equal specificity with two verdicts becomes ask. A compound command takes the most restrictive of deny, ask, unmatched, allow. A built-in deny matches a command that begins with the exact `rm -rf` token sequence. Full mode does not apply it. Reset to default restores the built-in list. Settings → Agent Permissions. https://v0.app/docs/terminal-commands

The messages API surfaces a blocked tool as a `tool-call` part with `suggestedPermissions`. Approving sends those objects back unchanged as `confirmed-permissions`. A mismatch returns 409. Reject by sending a normal follow-up instead. https://v0.app/docs/api/v2/guides/handling-agent-interactions

v0 roles in the product are Builder, Creator, and Viewer. They are not the sandbox tool names. https://v0.app/docs/enterprise

## Bolt

**Project.** Bolt runs on StackBlitz WebContainers, a browser runtime for Node.js. No local install is required for that runtime. https://support.bolt.new/concepts/glossary and https://support.bolt.new/faqs/troubleshooting/guide

The project the agent sees is the file tree in that WebContainer, plus chat, plus preview. Code view (code icon) opens, edits, creates, and deletes files. Save or Ctrl+S, then Bolt builds, then Preview shows it. In Safari, Code view is read-only and the preview is hosted. A hosted preview is not the published site. https://support.bolt.new/building/using-bolt/code-view and https://support.bolt.new/concepts/supported-technologies

The terminal sits in Code view. A person can run `npm run build`, `npx knip --production --fix --allow-remove-files`, or `npx depcheck` there. Those terminal runs do not spend tokens. A named agent shell-tool schema is **not public**. https://support.bolt.new/building/using-bolt/code-view and https://support.bolt.new/best-practices/manage-context

Bolt Cloud can create a database, with a table view, logs, edge functions, secrets, users, and auth, or the project can be connected to Supabase. Database controls are not on the mobile client. How the agent calls the database is **not public** beyond "Bolt creates a database automatically when your project needs one." https://support.bolt.new/concepts/glossary and https://support.bolt.new/concepts/supported-technologies

**Tools the pages name.** Chat `@` inserts a project file or folder path. Select adds a preview element to the prompt. In Code view, right-click Target file limits the agent to those files. Lock file or Lock all excludes a file or directory. Highlight code and Ask Bolt to attach that selection. https://support.bolt.new/building/chat-tools and https://support.bolt.new/building/using-bolt/code-view

`.bolt/ignore` lists paths, including `*` wildcards, that are left out of the AI context. Create it under `.bolt` in Code view if it is missing. Hidden files are invisible to the agent, not deleted. https://support.bolt.new/faqs/troubleshooting/guide

Connectors (MCP), including Notion, Linear, and GitHub, plus a custom MCP URL and transport, let the chat read or edit those apps. Auto-enable for all projects is a separate switch. The tool names a connector exposes are **not public** on the connect page. https://support.bolt.new/building/using-bolt/connect-mcp

Two agents: Standard (every plan) and Max (paid). The project remembers the choice. Bolt picks the model. https://support.bolt.new/building/using-bolt/agents

**Instructions.** `agents.md` in the project is found automatically. The file name is required. It may point at other files, but the main instructions have to be in `agents.md`. Attach it from the chat plus menu, or it can already be in the tree. Project knowledge is a separate text field for goals, features, and design principles. It survives `/clear`. After `/clear`, the codebase remains and the recent chat does not. https://support.bolt.new/best-practices/manage-context

**Permission.** Plan mode in an open project answers from the codebase and recent messages and does not change code. Implement this plan switches to Build mode and applies the change. Plan mode on the homepage is different: it first creates the base structure of the app, then shows a plan. Plan mode may search the web and list sources. Discussion mode belonged to the retired v1 agent. https://support.bolt.new/best-practices/plan-mode and https://support.bolt.new/release-notes

A Bolt allow, ask, or deny command grammar is **not public** on the pages opened. Lock file and `.bolt/ignore` are the public write and context limits.

## Lovable

**Project.** One project is one app in one workspace: project chat, preview, code, version history, and settings (name, URL, domains, knowledge). Edits become versions automatically. The code editor (Code tab) browses that tree. Paid plans can download the tree as a zip. One file can be downloaded on any plan. https://docs.lovable.dev/features/projects/overview and https://docs.lovable.dev/features/code-mode

Search code is the box at the top of the file panel, or Cmd+Shift+F / Ctrl+Shift+F. Reference in chat, the file toolbar button, or `@` puts a pill such as `Button.tsx:42` on the next message. `@` in that chat only sees the current project. Another project in the same workspace is a separate `@` mention. https://docs.lovable.dev/features/code-mode and https://docs.lovable.dev/features/agent-mode

A file-generation request can run Python 3, Node, Bun, Deno, Bash, pandas, NumPy, SciPy, DuckDB, matplotlib, Pillow, psql, curl, jq, and other Unix tools in an isolated Linux environment. That script run does not change project source. On Cloud, database access during that run exists only when Read database and Change data are Always allow. https://docs.lovable.dev/features/generate-files

**Tools the pages name.** Build mode (formerly Agent mode) explores the repo, edits files, and shows an activity card. The card names search, web fetch, and image generation. Details → Timeline lists tool calls. Details → Changes lists file diffs. Verification tools named: browser testing, frontend tests, and edge function verification. Most of those run only when asked. A complete function schema is **not public**. https://docs.lovable.dev/features/agent-mode

Subagents are temporary and read-only. They can search the project, inspect files, run read-only lookups, browse the web, and review against the prompt. They cannot create, edit, or delete files. They do not see the whole chat. Only the briefing Lovable passes is in scope. Two kinds: generic, and Explore. The main agent is the only writer. Several may run at once. They do not talk to each other. https://docs.lovable.dev/features/subagents

Chat connectors are MCP servers, personal to the member. App connectors go through a gateway. Tokens are not shown in project settings. Custom MCP does not use that gateway unless an Enterprise static-IP option is on. Connector tool names are per server and are **not public** as one Lovable list. https://docs.lovable.dev/integrations/introduction and https://docs.lovable.dev/integrations/security

Lovable's own MCP, for an agent outside Lovable, includes project tools (`list_projects`, `get_project`, `create_project`), knowledge tools (`get_workspace_knowledge`, `set_workspace_knowledge`, `get_project_knowledge`, `set_project_knowledge`), skill tools (`list_workspace_skills`, `get_workspace_skill`, `create_workspace_skill`), and code tools (`get_diff`, `list_files`, `read_file`, `list_edits`). `get_project` can include a screenshot. `create_project` takes an `initial_message`. https://docs.lovable.dev/integrations/lovable-mcp-server

**Instructions.** Workspace knowledge and project knowledge are plain text, each capped at 10,000 characters. Knowledge is always in context. Skills load when the request matches the skill description. Only owners and admins edit workspace knowledge. Anyone who can edit the project can edit its knowledge. On a conflict, project knowledge is supposed to win. Root `AGENTS.md` is always read, including in a long session. `CLAUDE.md` and connector knowledge files are also read. Changes to workspace knowledge apply on the next message. https://docs.lovable.dev/features/knowledge

**Permission.** Three chat modes. Chat mode does not plan and does not change code. Plan mode investigates and writes a plan the person edits and approves before building. Build mode changes the project. Stop keeps completed edits. Undo drops them. A Build message can run up to 10 hours and pauses at the credit check-in (20 credits unless changed). https://docs.lovable.dev/features/agent-mode

A shell allow/deny grammar like v0's is **not public** on the pages opened. The public write limit is mode plus read-only subagents.

## Framer

**Project.** The in-product agent does not get a Node sandbox on the pages opened. The project is the Framer file: canvas, layers, components, and CMS. Open Agent in the right-hand panel, or the Agent tab on a new project, and type in Ask Framer…. The agent reads the current canvas and places the result on the page. Select a layer before the next prompt to keep the edit on that layer. Select CMS rows or cells and choose Add to Agent before a collection prompt. https://www.framer.com/help/articles/how-to-use-agents/ and https://www.framer.com/help/articles/how-to-add-content-to-your-cms-with-framer-agents/

Branching is a project environment for unsafe edits: branch menu, Create branch, review Changes, Apply to main. Work on a branch does not change main. https://www.framer.com/help/articles/how-to-build-a-website-from-scratch-with-framer-agents/

**Tools.** Named function calls for the canvas agent are **not public**. The help pages describe effects: generate or update layout, text, interactions, and code on the canvas; create a CMS collection and fields; add items; connect collection lists and detail pages, with manual review when the layout is custom. https://www.framer.com/help/articles/how-to-use-agents/ and https://www.framer.com/help/articles/how-to-add-content-to-your-cms-with-framer-agents/

External agents are separate. Run `npx @framer/agent setup`, then connect a harness that can use Skills and local tools (Claude Code, Codex in ChatGPT, Cursor, Gemini CLI, Windsurf). The first use opens a browser allow prompt and asks for an API key. Framer does not require an MCP server for this path. https://www.framer.com/help/articles/use-external-agents-with-framer/

Through the Framer Agent CLI and Server API, an external agent can work with project sessions and project context, page and canvas structure, CMS collections and items, code files and code components, color and text styles, assets and files, localization, project metadata, screenshots and SVG exports, and publishing information and publishing actions. The exact operations depend on the project, permissions, and the beta surface. CMS read and write includes create, update, and delete of items. The person still controls what is published. https://www.framer.com/help/articles/what-you-can-do-with-local-agents/ and https://www.framer.com/help/articles/use-external-agents-with-framer/

The same external-agent article says they cannot yet update some settings (project names and domains), assign overrides to nodes, or access analytics. A recommended order is inspect, propose, review, apply, summarize, then review in Framer before publishing. https://www.framer.com/help/articles/what-you-can-do-with-local-agents/

**Instructions and permission.** A project instruction file inside the Framer document is **not public** on the pages opened. The public scope control is the canvas selection, Add to Agent, and the browser allow on first external connect. Enterprise can disable AI for a workspace. The click path is **not public** here. The index only names the article. https://www.framer.com/help/ai/

## Webflow

**Project.** Two environments. Data tools hit the site through the remote MCP server `https://mcp.webflow.com/mcp` and do not need the Designer open. Designer-session tools need the Designer open and the MCP Bridge App connected from the Apps panel. Those session tools read or change the current selection, page, mode, branch, canvas, and breakpoints, and they can snapshot an element. Everything else on the overview works headlessly. One authorization is one Workspace. The agent cannot change site or Workspace access. https://developers.webflow.com/mcp/reference/overview and https://developers.webflow.com/mcp/reference/how-it-works and https://help.webflow.com/hc/en-us/articles/52536616701971-Connect-your-AI-tools-to-the-Webflow-MCP-server

**Tools the docs name.** Designer session: `asset_tool` action `upload_image_by_url` (a public image URL into the asset library), `designer_tool` (current page, mode, branch, selection, breakpoints, select element, switch page, component view, create a page folder), and `element_snapshot_tool` action `get_element_snapshot` (a visual check that does not publish). Other asset work is named as `data_assets_tool` without its action list on the page opened. Every Designer action also needs `siteId`. Granting a tool grants all of its actions. https://developers.webflow.com/mcp/tools/designer-tools

The overview, without a full function index: elements, classes, components, variables, GSAP interactions, custom code, uploaded font files, and Enterprise page branches. Classic interactions are invisible to the agent. Secrets are not accepted or returned. Localized CMS cannot be created, only read or updated. Google and Adobe fonts that stay remote are not managed by MCP. https://developers.webflow.com/mcp/reference/overview

Inside the Designer, the AI Assistant is a separate surface from the external MCP client. Drag a section from the Add panel, pick or search a layout, and the assistant applies the site's classes and variables. The top-bar assistant answers from the Help Center (100 questions per 31 days in that beta) and does not spend AI credits. Generate with AI on a component writes a React component from the site's styles and variables. App Gen under Site settings → Webflow Cloud prompts for an app and can attach CMS collections and components. A single tool schema for that in-product assistant is **not public**. https://help.webflow.com/hc/en-us/articles/34205154436243-Modify-page-designs-with-the-Webflow-AI-Assistant and https://help.webflow.com/hc/en-us/articles/33961195523603-Get-contextual-help-using-Webflow-with-the-Webflow-AI-Assistant and https://help.webflow.com/hc/en-us/articles/51168990228499-Build-AI-code-components and https://help.webflow.com/hc/en-us/articles/46332369065875-Build-full-stack-web-apps-with-Webflow-AI

**Instructions.** Stored on the site. Skills are task guidance (`SKILL.md` plus optional supporting files). Rules are short and apply to every action. Both are off until toggled On. Create them from the Instructions panel, or import a zip of `.md` and `.mdc` only. References in an instruction resolve to live variables, components, assets, pages, CMS items, and other instructions. Agents should read rules before any action and skills when relevant. Site managers and Designers can edit. Marketers and Content editors can read. Reviewers cannot read them. MCP can list, create, update, and delete them. https://help.webflow.com/hc/en-us/articles/52536649709971-Create-and-manage-AI-agent-instructions

**Permission.** The agent's Webflow role is the person's existing site role. Workspace settings → General can turn all of Webflow AI off. https://developers.webflow.com/mcp/reference/overview and https://help.webflow.com/hc/en-us/articles/49786374523923-Enable-or-disable-Webflow-AI

## Relume

**Project.** Site Builder keeps a sitemap and wireframes in the Relume project, then a style guide, then Design View. A section on the sitemap is the same section on the wireframe. Delete one and the other goes. The section title and description are the prompt that picks a library component. Drag a section by its handle. A global section stays in sync. Design View applies the style guide across that project. It is not a Figma-style editor. Export is a later handoff to Figma or Webflow, not a local dev server. https://www.relume.io/resources/docs/building-a-sitemap-with-ai and https://www.relume.io/resources/docs/how-to-create-and-edit-wireframes-in-the-relume-site-builder and https://www.relume.io/whats-new/july-2025-release

**Tools.** On a wireframe, select text or a section and choose Ask AI. The page says rewrite options exist (shorter, longer, a line count, and others). The full option list is **not public** on the opened text. There is no public Node sandbox, terminal, or file lock for Site Builder. https://www.relume.io/resources/docs/how-to-create-and-edit-wireframes-in-the-relume-site-builder

Relume Library MCP is a second environment: an editor the person already uses, plus the remote server. The marketing page says sign in once, the setup adds a path alias, Tailwind preset, and icons, the assistant searches the real library, and it fetches that component's code by slug into the project as editable React. The MCP URL is `https://relume-library-mcp.relume.io/mcp`. Named tool functions are **not public** on that page. The setup guide is a Notion link. This note did not open it. https://www.relume.ai/relume-library-mcp

The July 2026 release says wireframe generation now picks from the library using the section title and description, including a content count, and can reuse a component across pages. It does not name tool calls. https://www.relume.io/whats-new/july-2026-release

**Instructions and permission.** A Site Builder rules file is **not public**. The public instruction is the sitemap prompt plus each section's title and description, edited before wireframes are generated. https://www.relume.io/resources/docs/building-a-sitemap-with-ai

## Durable

**Project.** The public product page is a hosted site plus a drag-and-drop editor, not a repo the agent clones. Answer three questions (industry, business name, goals). The editor then changes layouts, images, headings, and fonts. A code sandbox, terminal, or project file tree is **not public**. https://durable.com/ai-website-builder

The launch post says fonts and colors stay consistent after you pick them, a new page can be added by describing it, and generated assets live in Studio. AI Partner is a chat that already knows the business, contacts, invoices, and goals. It can run research, draft marketing, and follow presets. No tool schema is on that post. https://durable.com/blog/launch

The help index has an Agents collection: automate reviews, website inquiries, and blog content. It has 13 articles. The index fetch did not list their URLs, so the click procedures inside them are **not public** here. Studio is a separate collection (7 articles), also not opened. https://help.durable.com/en/

Pricing names two agents and an image tool, as quotas, not as functions: Blog Writer agent, Lead agent, and image generation. https://durable.com/pricing

**Instructions and permission.** A project instruction file, an allow list, and a plan mode that refuses writes are **not public** on the pages opened.

## What the tool pages agree on

v0, Bolt, and Lovable put the agent in a project that already has files, a preview that is not the publish step, and a way to point at one file or one line range. v0 names `Bash` and `Delete` and a JSON allow/ask/deny list. Bolt and Lovable do not publish that grammar. They publish lock or ignore, and a mode that does not write (Bolt Plan inside a project, Lovable Chat and Plan). Lovable's writers are one main agent. Subagents stay read-only.

Framer and Webflow equip the agent with the site model (canvas, CMS, components, variables), not with a Node tree, unless the person is in an external editor. Webflow splits headless data tools from Designer-session tools, and it stores skills and rules on the site, off until enabled. Relume's Site Builder equips the agent with a sitemap whose section text picks a library component. Its MCP fetches that component by slug into someone else's editor. Durable's public pages equip a business account (editor, Studio, AI Partner, Blog Writer, Lead agent) and do not document a file tool.

Do not copy from these pages into SpiderCaster: v0's default `allow-all` network, `Bash`, browser use, or web search. Bolt's `npx` cleanup. Lovable's curl, image generation, or web fetch. Webflow's `upload_image_by_url`. Framer's publishing actions. Relume's remote component fetch. Durable's image and blog agents. None of those is a local stdlib read.

## Five SpiderCaster tools

Not CLI verbs. Not MCP names. Not `catalog_read`, `crew_roles`, `mold_list`, `frame_list`, `frame_pick`, `image`, or `check`. Not the hands in `lib/hands/__init__.py` `HANDS`. Offline stdlib only (`pathlib`, `os`, text reads). No socket, no URL open, no publish, no `library bind --live`. Code for all five belongs in `lib/sandbox.py`. Each one returns a dict. A fail dict is `{"ok": false, "error": "<reason>"}` and includes no file body.

### 1. perm_gate

- Caller: `run_job` in `lib/crew.py`, before it calls `HANDS[name]`.
- Inputs: `seat` (architect, content, frontend, graphics, visual, seo, or deployer), `hand` (string).
- Output keys: `ok`, `allow`, `seat`, `hand`.
- Fail: unknown seat, or `hand` not in that seat's `ROLES` list. `allow` is false. The runner does not call the hand. No ledger write. No publish.
- Target file: `lib/crew.py` (read `ROLES` only).

### 2. skill_read

- Caller: the seat named in `seat`, and only that seat.
- Inputs: `seat`.
- Output keys: `ok`, `path`, `chars`, `text`.
- Fail: seat not one of the seven, file missing, not UTF-8, or the file is longer than 32000 characters. On fail, `text` is absent.
- Target file: `library/seats/<seat>/SKILL.md`.

### 3. project_list

- Caller: architect.
- Inputs: `project` (a directory name under the engine `projects/`).
- Output keys: `ok`, `root`, `count`, `files`. Each file has `rel`, `bytes`, `suffix`.
- Fail: the directory is missing, the resolved path is not inside that one project, a symlink resolves outside it, depth would pass 3, or the walk would pass 200 files. On those fails, `files` is absent. Bodies are never read. The vault is never listed.
- Target file: `projects/<project>/` (the directory itself).

### 4. span_read

- Caller: architect when `rel` is `brief.md`. Content when `rel` is `copy/<one-file>.md`. Any other caller fails.
- Inputs: `project`, `rel`, `start`, `end` (1-based, inclusive).
- Output keys: `ok`, `path`, `start`, `end`, `lines`.
- Fail: missing project, `rel` absolute, `rel` containing `..`, `rel` containing a scheme (`http:`, `https:`, `file:`), `rel` not `brief.md` or a single file under `copy/` ending in `.md`, file missing, not UTF-8, `start` < 1, `end` < `start`, or the span longer than 80 lines. On fail, `lines` is absent.
- Target file: `projects/<project>/brief.md` or `projects/<project>/copy/<file>.md`.

### 5. lock_list

- Caller: frontend, before `render`.
- Inputs: `project`.
- Output keys: `ok`, `present`, `locks` (relative paths).
- Fail: `lock.txt` exists and any non-empty line is absolute, contains `..`, contains a scheme, or is not a relative path that stays inside that project. On fail, `locks` is absent. A missing `lock.txt` is not a fail: `present` is false and `locks` is `[]`. The tool does not create the file and does not write HTML.
- Target file: `projects/<project>/lock.txt`.
