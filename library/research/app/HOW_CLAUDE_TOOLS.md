# How Claude equips an agent with tools

Read 2026-10-01 from public docs only. A procedure claim sits next to its URL. If the opened page does not say the step, this file says **not public**.

This note is the harness: how a tool gets into the agent's hands. The website-builder fields (first input, section model, hero, favicon, publish) are already in `library/research/HOW_PRO_BUILDERS.md` and are not repeated here. This wave is the SpiderCaster app (tools, skills, wrappers, environment). It does not design a page and does not propose page copy.

Three surfaces. Claude Code is a coding harness with a named tool list. Cowork is that agent loop pointed at knowledge work. Claude Design is a canvas on an artifact. They are not one tool catalog.

## Claude Code: tools are the action layer

Without tools, Claude can only answer with text. With tools, each call returns information that feeds the next decision. The loop is gather context, take action, verify. The model reasons; Claude Code is the harness that supplies tools and the context the model sees. https://code.claude.com/docs/en/how-claude-code-works

Built-in tools fall into five categories:

| Category | What the public page says Claude can do |
| --- | --- |
| File operations | Read files, edit code, create files, rename and reorganize |
| Search | Find files by pattern, search content, explore a codebase |
| Execution | Run shell commands, start servers, run tests, use git |
| Web | Search the web, fetch documentation, look up errors |
| Code intelligence | Type errors after edits, go to definition, find references. Inactive until a language-server plugin is installed |

Same URL. Spawning subagents and asking the user questions are extra tools, not a sixth category. The full name list is the tools reference. https://code.claude.com/docs/en/tools-reference

Claude chooses the tool. The person does not name a tool in ordinary chat. Tool name strings are for permission rules, a subagent's `tools` list, and hook matchers. To add a custom tool, connect an MCP server. A skill does not add a tool entry. It runs through the existing `Skill` tool. Same tools-reference URL.

On Windows, `Glob` is in the default tool set. On macOS, Linux, and WSL, `Glob` and `Grep` are absent by default and search goes through `Bash`, unless the session names `Glob` or `Grep`, Bash is removed, or a subagent lists them and leaves Bash out. The PowerShell tool is on automatically when Git Bash is not installed. With Git Bash, it is on by default for claude.ai and Console accounts. Same URL.

`Edit` is exact string replace, not a regex. Three checks: a `Read` deny rule can refuse the path; Claude must have read the file in the conversation (newer models may edit an unread file when the read would not prompt and `Read` is available); `old_string` must match once, or `replace_all` must be set. Same URL.

`Read` is told to take an absolute path. It reads files, not directories. Images come back as visual content. A PDF longer than 10 pages is read in page ranges, up to 20 pages, and needs `pdftoppm`. Same URL.

Permission rules use `ToolName(specifier)`. Examples the tools reference gives: `Bash(npm run *)`, `PowerShell(Get-ChildItem *)`, `Read(~/secrets/**)`, `Edit(/src/**)`, `Skill(deploy *)`, `Agent(Explore)`, `WebFetch(domain:example.com)`, and bare `WebSearch`. Those strings are accepted in settings allow/deny, `--allowedTools` / `--disallowedTools`, the Agent SDK's allow and deny options, a skill's `allowed-tools`, and a hook's `if` field. Hook `matcher` fields use the bare tool name, not the parenthesized form. An `Edit(...)` allow also grants read of that path. A `Read(...)` deny also blocks Edit and Write on that path. Same URL.

In Manual mode, the tools-reference "Permission required" column is whether the tool prompts inside the working directory. `Read`, `Grep`, and `Glob` are marked No and still prompt outside the working directory and extra directories. `Bash` is marked Yes, except a built-in set of read-only commands. In auto mode a classifier decides most prompts. Same URL.

Checkpoints snapshot a file before an edit. Restoring does not undo a remote action. Permission mode is cycled with Shift+Tab: Auto, Manual, Accept edits, Plan. Auto is the built-in start for interactive terminal and VS Code sessions on Claude Code v2.1.283 or later. https://code.claude.com/docs/en/how-claude-code-works

Bash does not keep environment variables between commands. The working directory does carry over inside the project and added directories, unless `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1`. Subagent sessions never carry a `cd`. https://code.claude.com/docs/en/tools-reference

## What is a tool, and what only looks like one

Extensions plug into different parts of the loop. They are not all tools. https://code.claude.com/docs/en/features-overview

| Piece | Public role | Becomes a new tool name? |
| --- | --- | --- |
| CLAUDE.md | Full text loaded every session. "Always do X." Not a workflow trigger. | No |
| Output style | Role, tone, and format for the session. One active at a time. | No |
| Skill | Markdown instructions. You type `/name`, or Claude loads it when the description matches. Body loads on use. | No. Invoked through `Skill`. |
| MCP | External tools and data. Tool names load at session start. Full JSON schemas stay deferred until a tool is needed. | Yes. One callable per server tool. |
| Hook | Your script, HTTP request, MCP tool call, prompt, or subagent at a lifecycle event. | No. It fires beside a tool call. |
| Subagent | Own loop, own context, returns a summary. Parent does not see intermediate tool calls. | No. Started through `Agent`. Its own tool list is a filter. |
| Plugin | Packages skills, hooks, subagents, and MCP servers. Plugin skills are namespaced (`/my-plugin:review`). | Only the MCP servers inside it add tool names. |

Same features-overview URL. The public order for adding them: a repeated convention goes in CLAUDE.md; a repeated prompt becomes a skill; data Claude cannot see becomes an MCP server; a side task that floods the transcript becomes a subagent; something that must happen every time becomes a hook; a second repo that needs the same setup becomes a plugin.

Skills versus MCP, in that page's words: MCP provides the tools; a skill teaches how to use them. Skills versus hooks: a hook always fires on its event; a skill is instructions Claude interprets. "Never edit `.env`" in CLAUDE.md or a skill is a request. A `PreToolUse` hook that blocks the edit is the enforcement. Same URL.

Context cost, same page: CLAUDE.md is in every request. Skill descriptions load at start, full content when used, unless `disable-model-invocation: true`. MCP tool names load at start; schemas wait. Hooks load nothing unless they return text. A subagent's tool calls stay out of the parent window.

MCP tool search is on by default. Idle MCP tools stay cheap because schemas are deferred. `/mcp` shows connection status. https://code.claude.com/docs/en/features-overview and https://code.claude.com/docs/en/mcp

The Agent SDK page says tool search withholds definitions, gives the agent a summary, and loads up to five matching tools per search by default. Core built-ins such as Bash, Read, and Edit stay loaded and do not count toward the deferral threshold. https://code.claude.com/docs/en/agent-sdk/tool-search

`ToolSearch` is the built-in that loads deferred tools. `WaitForMcpServers` appears only when tool search is off. https://code.claude.com/docs/en/tools-reference

## Skills: instructions, not a new callable

Create `SKILL.md`. Claude adds it to the toolkit and uses it when relevant, or the person invokes `/skill-name`. The body loads only when used. Custom commands are skills now: `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`. https://code.claude.com/docs/en/skills

Where a skill file loads, same URL:

| Scope | Path |
| --- | --- |
| Enterprise | `.claude/skills/<skill-name>/SKILL.md` in the managed settings directory |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` |
| Project | `.claude/skills/<skill-name>/SKILL.md` |
| Nested | `<subdir>/.claude/skills/<skill-name>/SKILL.md` (loads once Claude works on files there) |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md`, invoked as `/plugin-name:skill-name` |
| claude.ai account | Skills enabled on the account. Cowork, cloud sessions, and terminal sessions signed in with that account |

Personal skills on disk are not what Cowork reads. Cowork and cloud sessions do not read `~/.claude/skills/`. They load skills enabled on the claude.ai account. Cloud sessions also load project skills committed in the repo. Same URL.

Write procedure, same page: make the directory, write `SKILL.md` with YAML frontmatter between `---` lines and markdown after, start `claude`, either ask in words that match `description` or type `/name`. The opening `---` must be the first line. If the YAML does not parse, the skill still loads with no fields set. A field Claude Code does not recognize is ignored with no error.

Frontmatter that matters for tools, same page:

- `allowed-tools` grants those tools without a permission prompt for the turn that invoked the skill. The grant clears on the next user message. It does not remove other tools. Permission settings still govern tools that are not listed. A project skill's `allowed-tools` applies even in a folder that was never trusted, including `claude -p`.
- `disallowed-tools` removes those tools from the pool while the skill is active. The restriction clears on the next user message.
- `disable-model-invocation: true` means only the person can invoke it. The description is not in context until then. Claude Code blocks a model attempt and tells Claude not to reproduce the steps another way.
- `user-invocable: false` hides it from the `/` menu. Claude can still invoke it.
- `context: fork` runs the skill in a subagent. The subagent does not see the parent conversation. `agent` picks the subagent type. If omitted, the forked skill uses `general-purpose`.
- `hooks` registers hooks for the rest of the session once the skill is invoked.

Claude Code-only frontmatter is rejected on a claude.ai upload. The upload path allows `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. An extra key fails the upload. Dynamic context lines (a line that runs a shell command and inlines its output) do not function in claude.ai chat or through the API. Same URL.

Supporting files sit beside `SKILL.md`. The public tip is to keep `SKILL.md` under 500 lines and point at the other files. A bundled script is executed, not loaded as prompt text. Same URL.

Across Claude products, a skill is a folder of instructions, scripts, and resources, loaded when relevant. That requires code execution to be enabled. Skills and MCP are different: MCP connects services; skills are the procedure for using them. https://support.claude.com/en/articles/12512176-what-are-skills

In Cowork, installed skills can be opened from Customize. Type `/` or click `+` to see plugin skills. https://support.claude.com/en/articles/13837440-use-plugins-in-claude

How Cowork turns a skill folder into a tool schema internally: **not public**. The public statement is that Claude reviews available skills, loads relevant ones, and applies the instructions. https://support.claude.com/en/articles/12512176-what-are-skills

## Hooks: a gate on a tool, not a tool

A hook is a user-defined command Claude Code runs at a lifecycle point so the action does not depend on the model choosing it. Add a `hooks` object to a settings file. The `/hooks` menu is read-only. Confirm there, then edit JSON or ask Claude to edit it. https://code.claude.com/docs/en/hooks-guide

First hook procedure, same page: open `~/.claude/settings.json`, add a `Notification` hook whose `matcher` is `""` and whose `type` is `command`, type `/hooks`, select the event, then trigger a permission prompt. An empty matcher fires on every occurrence of that event. `Edit|Write` fires only for those tool names. A comma works the same way as `|`. Matchers are case-sensitive.

Locations and scope, same page:

| Location | Scope |
| --- | --- |
| `~/.claude/settings.json` | All projects on that machine |
| `.claude/settings.json` | One project, shareable |
| `.claude/settings.local.json` | One project, not shared |
| Managed policy settings | Organization |
| Plugin `hooks/hooks.json` | While the plugin is enabled |
| Skill frontmatter | Rest of the session after that skill is invoked |
| Subagent frontmatter | While that subagent runs |

Hooks merge. Every registered hook for a matching event fires, whatever its source. https://code.claude.com/docs/en/features-overview

Events the guide lists include `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `SubagentStart`, `SubagentStop`, `Stop`, and `SessionEnd`. The full table is on that guide. `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, and `PermissionDenied` match on tool name. `SubagentStart` and `SubagentStop` match on agent type (`general-purpose`, `Explore`, `Plan`, or a custom name). https://code.claude.com/docs/en/hooks-guide

Input is JSON on stdin. For a tool event the fields include `session_id`, `cwd`, `hook_event_name`, `tool_name`, and `tool_input`. Exit 0 on `PreToolUse` does not approve the call; the normal permission flow still runs. Exit 2 blocks the action; stderr is the reason. Any other exit code is a non-blocking error unless stdout is a valid decision object. Structured control is exit 0 plus JSON. On `PreToolUse`, `permissionDecision` inside `hookSpecificOutput` is `allow`, `deny`, `ask`, or, in non-interactive `-p`, `defer`. `deny` cancels the call and sends the reason to Claude. `allow` skips the interactive prompt and does not override a deny rule. Same URL.

`PreToolUse` runs before the permission-mode check, including `bypassPermissions`. A hook `deny` still blocks. A hook `allow` cannot loosen a settings deny. When several `PreToolUse` hooks speak, the most restrictive wins: `deny`, then `defer`, then `ask`, then `allow`. Sibling hooks still run; one deny does not stop the others. Same URL.

Hook types: `command` (shell), `http` (POST the same JSON), `mcp_tool` (call a configured MCP tool), `prompt` (one model turn returns `ok`), `agent` (experimental subagent, up to 50 tool turns). A command hook cannot itself trigger a `/` command or a tool call. Same URL.

MCP tools in a matcher use `mcp__<server>__<tool>`. A plugin-bundled server is `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`. https://code.claude.com/docs/en/hooks-guide and https://code.claude.com/docs/en/mcp

`"disableAllHooks": true` turns hooks off at the settings layer that wins. Managed hooks still run unless the managed file also sets it. https://code.claude.com/docs/en/hooks-guide

Cowork hook configuration screens, separate from Claude Code settings files: **not public**. The public Cowork fact is below, under plugins.

## Subagents: a filtered copy of the tool list

A subagent is a markdown file with YAML frontmatter and a system prompt as the body. It has its own context, its own tool access, and its own permissions. Claude delegates when the description matches. The parent sees the final result, not the intermediate tool calls. https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/tools-reference

Create procedure, sub-agents page: ask Claude to write the file, or write it yourself. As of v2.1.198, `/agents` no longer opens a creation wizard. It tells you to edit the directory. Put a personal agent in `~/.claude/agents/<name>.md` or a project agent in `.claude/agents/<name>.md`. Restart only if that `agents` directory did not exist when the session started. Then ask Claude to use the agent by name. The transcript row looks like `code-improver(Suggest code improvements)`.

Scope priority, highest first: managed settings, the `--agents` CLI flag for this session, `.claude/agents/`, `~/.claude/agents/`, then a plugin's `agents/` directory. Same name: the higher scope wins. Identity is the `name` field, not the filename. A `name` that contains `:` does not load. A file with no `name` is treated as documentation. A `name` with no `description` is skipped. YAML that does not parse is skipped. Same URL.

Required frontmatter is `name` and `description`. `tools` is an allowlist (comma-separated or a YAML list). Omit it and the subagent inherits every tool available to subagents. `disallowedTools` removes tools from that pool. If both are set, `disallowedTools` wins: a tool listed in both is removed. A specifier such as `Bash(git push *)` still removes the whole tool, not one command. To block one command and keep Bash, use a permission deny rule instead. If every `tools` entry fails to match a usable tool, the Agent tool returns an error and does not launch the subagent. Same URL.

Built-in Explore and Plan are read-only: Write and Edit are denied. They also skip CLAUDE.md and the git status snapshot. General-purpose gets every tool available to subagents. Same URL.

Some tools are never granted to a non-fork subagent, even if listed: `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ScheduleWakeup`, `WaitForMcpServers`, `Workflow`, and `ExitPlanMode` unless `permissionMode` is `plan`. `Agent` is removed at the depth limit. Background subagents, which is the default, keep MCP tools plus a fixed built-in set (`Read`, `Grep`, `Glob`, `LSP`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, and others named on that page). Forks skip those filters and receive the parent's tool pool. Same URL.

MCP servers can be scoped to one subagent with `mcpServers` in its frontmatter: an inline definition or the name of a server the parent already has. Inline servers connect when the subagent starts and disconnect when it finishes. Plugin subagents ignore `hooks`, `mcpServers`, and `permissionMode`. Same URL.

Launching the subagent does not itself prompt. Each of its tool calls is checked against permission rules as it runs. https://code.claude.com/docs/en/tools-reference

Skills listed in the subagent `skills` field are preloaded in full at launch. A skill with `disable-model-invocation: true` cannot be preloaded. Unlisted skills can still be invoked through `Skill` unless that tool is removed. https://code.claude.com/docs/en/sub-agents

A skill with `context: fork` is the other direction: the skill body is the task, and the agent type supplies the system prompt. https://code.claude.com/docs/en/skills

## MCP: the only public way to add a tool name

MCP servers give Claude Code tools, databases, and APIs. Browse reviewed connectors in the Anthropic Directory. Add a listed remote server with `claude mcp add`. Trust the server before connecting. https://code.claude.com/docs/en/mcp

Install procedures, same page:

- Remote HTTP: `claude mcp add --transport http <name> <url>`. A JSON entry with a `url` and no `type` is an error. Claude Code skips it. `streamable-http` is an alias of `http`.
- Remote SSE: deprecated. `claude mcp add --transport sse <name> <url>`, or `--transport http` on v2.1.265 or later, which tries HTTP and then SSE.
- Local stdio: `claude mcp add --transport stdio <name> -- <command> [args...]`. Everything after `--` is the server command. Claude Code sets `CLAUDE_PROJECT_DIR` in the server process to the project root.
- WebSocket: `claude mcp add-json` with `"type": "ws"`. `--transport` does not accept `ws`.

Check with `claude mcp list`, `claude mcp get <name>`, and, inside a session, `/mcp`. A successful add prints `Added ...`, which means the config was written, not that the server connected. Status lines include `Connected`, `Needs authentication`, and `Failed to connect`. A project server from `.mcp.json` stays `Pending approval` until an interactive `claude` session approves it. A cloned repo cannot approve its own servers. Same URL.

Scopes, highest precedence first: local (`~/.claude.json` under that project), project (`.mcp.json`, shareable), user (`~/.claude.json`, all projects). Plugin servers and claude.ai connectors rank below those. The whole entry comes from the winning scope. Fields are not merged. Same URL.

Tool names from a user-configured server are `mcp__<server>__<tool>`. A plugin-bundled server is `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`, with characters outside letters, digits, `_`, and `-` replaced by `_`. Use that full string in permission rules, `allowed-tools`, a subagent `tools` list, and hook matchers. A matcher on the bare server key does not fire for a plugin server. Same URL.

Reserved server names Claude Code will not let you take include `workspace`, `claude-in-chrome`, `computer-use`, `Claude Preview`, and `Claude Browser`. `claude mcp add` rejects them. Same URL.

Output over 10,000 tokens warns. The default cap is 25,000 tokens (`MAX_MCP_OUTPUT_TOKENS` raises the cap; the warning threshold stays). A main-conversation MCP call still running after two minutes becomes a background task on v2.1.212 or later. Subagent MCP calls are not backgrounded that way. Same URL.

How an MCP tool's JSON schema is rendered into the model prompt, field by field: **not public** beyond "tool names at session start, full schemas on demand." https://code.claude.com/docs/en/features-overview

## Cowork: same loop, different doors

Cowork uses the same agentic architecture as Claude Code, with no terminal required. https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork

Start procedure on that page: open Claude on the web, desktop, or mobile; in the message box select Cowork; describe the task; review the approach; let it run. If the message box has no Chat and Cowork choice, that step is gone: any conversation can take the task. https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude

When a task starts, the public sequence is: analyze the request and create a plan; break complex work into subtasks; run code and shell in an isolated environment on Anthropic's servers; coordinate parallel workstreams; deliver outputs to the session. https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork

Where that runs, for an admin audience, the architecture is the same on every plan. Cloud is the default: the agent loop and code execution run in a per-session sandbox on Anthropic's servers, destroyed when the session ends. Connector authorization tokens never enter the sandbox. Connector calls are made on the server side. A cloud session reaches a local file or the browser only through the Claude Desktop app, only for folders the person connected, and only while that app is online. Each local tool call is checked against the member's permissions before it runs. https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview

Local sessions, same page: the agent loop runs on the device (conversation, file reads and writes in connected folders, web fetches, local plugin MCP servers). Shell commands and code Claude writes run in a Linux VM (Apple Virtualization.framework on macOS, Hyper-V on Windows). If the VM cannot start, file and web tools keep running; shell and code execution report "workspace unavailable."

The internal names of Cowork's file, shell, and web tools: **not public**.

Computer use, when enabled, is the fallback, not the first choice. Order: (1) a connector such as Gmail, Google Drive, Microsoft 365, or Slack, if one is connected; (2) the built-in desktop browser, or Chrome through Claude in Chrome if that is the preferred browser; (3) screen interaction (click, type, desktop apps). Enablement: latest Claude Desktop, Settings > General under Desktop app, turn on Enable computer use, open Cowork or Claude Code, ask for something that uses a local app. Claude asks before each application. Some apps are off-limits by default. Computer use is in beta on Pro and Max. Team and Enterprise do not have it on the page that was opened. The desktop must be awake and the desktop app open. There is no sandbox between computer use and the applications. https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork

Connectors are the Cowork-facing MCP door. Web connectors work on Claude, Cowork, Claude Desktop, and Claude Mobile. Add them from Customize > Connectors, or a custom remote MCP connector. A custom connector lets Claude access that service and take action in it. Local connectors and plugins that include local MCP servers work through the desktop app only. https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities and https://support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile

Permission modes in the Cowork message box, against each connector tool's own setting. https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork

| Mode | Always allow | Needs approval | Blocked |
| --- | --- | --- | --- |
| Manual | Approved | Asks | Denied |
| Auto | Read-only tools approved. For write or delete, Claude decides. | Claude decides | Denied |
| Skip | Approved | Approved | Denied |

The new Claude experience offers Auto and Manual, with Manual as the default. Auto still runs a safety check and can block an action or fall back to asking. Skip checks nothing. Auto spends more of the usage limit. Same URL.

Plugins bundle skills, connectors, and sub-agents. Adding one saves it to the account, so it is also there in chat and in Claude Code signed in with the same account. Skills and commands from the plugin work in all of those places. Hooks and sub-agents run in Cowork and Claude Code, not in chat, where they show grayed out. A plugin's local MCP server runs in Cowork and Claude Code, not in chat. https://support.claude.com/en/articles/13837440-use-plugins-in-claude

Global instructions: Settings > Cowork, Edit next to Global instructions, type, Save. In the new experience those instructions are part of Instructions for Claude and apply to every conversation. Folder instructions apply when a local folder is selected on desktop. https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork

Scheduled tasks: type `/schedule` in a Cowork task, or use Scheduled in the sidebar. They run in the cloud and have the same connectors, skills, and plugins as a normal Cowork task. https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork

Deletion: Cowork asks before permanently deleting files. The person must select Allow. https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork

MDM can set `isLocalDevMcpEnabled` false to disable plugin-bundled and locally configured MCP servers, and `isDesktopExtensionEnabled` false to block MCPB and DXT extensions. With local MCP disabled, a cloud session that comes through that desktop app keeps only the folder-limited desktop file tools. https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview

## Claude Design: a canvas, not a published tool list

Claude Design is a template an artifact can start from. Use it in a chat, in Claude Code, or from the Artifacts tab. In a conversation, ask for a design or select Output > Design. In Claude Code, ask, or use `/design` to create, edit, and sync designs. `/design-sync` pulls in a design system so Claude Design builds from existing components. https://support.claude.com/en/articles/14604416-get-started-with-claude-design

The public flow on that page is a conversation beside a canvas: start, attach or import a design system, add screenshots or a codebase, describe the build, review the canvas, refine by chat, inline comments, or direct edits, then export or share. A new project inherits the organization's design system. Claude checks its output against that system and corrects it before the person sees it. Naming a component ("Use the Primary Button component") is a prompt instruction, not a documented tool call.

A list of tool names Claude Design gives the model (file tools, shell, MCP, or otherwise): **not public**. Whether Design runs hooks or subagents: **not public**. Whether the canvas editor is itself a tool call: **not public**.

Export formats and the Share button are on that same page. They are delivery of a design, not an agent tool catalog, and they are already covered as publish behavior in `HOW_PRO_BUILDERS.md`. This file does not restate them.

Artifacts in general require Cloud code execution and file creation. Templates (Design, Slides, Docs) are a paid-plan beta. https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them

## What SpiderCaster should copy

Copy the split, not the network. A skill is a markdown file a caller reads. A tool is a named function with a dict in and a dict out. A hook decides before the call and does not do the work. A seat receives an allowlist resolved against a parent pool, and a list that resolves to nothing fails closed. MCP is how Claude adds a tool name; SpiderCaster already has its MCP tool table in `mcp_server.py`. Do not add Bash, WebFetch, WebSearch, computer use, browser use, or a connector. Those need a shell or a network. Claude Design's tool list is not public, so do not invent a canvas tool.

Do not add a second roster of the seven seats. `crew_roles` already returns that. The five callables below are missing.

Each one is stdlib Python only. It stays offline. It does not open a socket. It does not publish. It does not run a shell. It does not delete. A builder creates the file named on the spec and does not wire it to `--live`.

### 1. skill_read

- Caller: library function.
- File: `lib/skill_read.py`.
- Inputs: `root` (directory path), `rel` (relative path of one `SKILL.md` under `root`).
- Output dict keys: `ok`, `error`, `name`, `description`, `allowed_tools`, `disallowed_tools`, `user_invocable`, `disable_model_invocation`, `context`, `body_sha256`.
- Behavior: read one UTF-8 file. If the first line is `---`, parse only flat scalars and flat lists until the next `---`. `allowed_tools` and `disallowed_tools` become lists of strings. `body_sha256` is the SHA-256 hex of the bytes after the frontmatter. Do not run a `` !`command` `` line. Do not follow a symlink that leaves `root`.
- Fail: `ok` false, `error` set, every other key `null` except the two tool lists, which are `[]`. Errors: `escape` if `rel` leaves `root`; `missing` if the file is not there; `not_file`; `bad_frontmatter` if the YAML is not a flat subset; `unsupported_value` if a value is a nested map. Write nothing.

### 2. hook_match

- Caller: library function.
- File: `lib/hook_match.py`.
- Inputs: `event` (string), `tool_name` (string), `hooks` (dict already in memory, shaped like Claude Code's `hooks` object: event to a list of `{matcher, hooks:[{type, command}]}`).
- Output dict keys: `ok`, `error`, `matched`, `ran`.
- Behavior: `ran` is always false. This function never starts `command`. An empty matcher or a missing matcher matches every `tool_name`. Otherwise split the matcher on `|` or comma, strip tokens, and compare to `tool_name` case-sensitively. `matched` is a list of `{group, type}` for hits. Known events are the names in the hooks-guide table cited above. A tool event uses `tool_name`. Any other known event ignores `tool_name` and matches every group.
- Fail: `ok` false, `matched` `[]`, `ran` false. Errors: `unknown_event`, `bad_hooks` if the dict shape is wrong. No file write.

### 3. perm_rule

- Caller: library function.
- File: `lib/perm_rule.py`.
- Inputs: `tool` (string), `arg` (string, may be empty), `allow` (list of rule strings), `deny` (list of rule strings).
- Output dict keys: `ok`, `error`, `decision`, `matched_rule`.
- Behavior: a rule is `ToolName` or `ToolName(specifier)`. A bare name matches that tool for any `arg`. A specifier may end in one `*`, and then `arg` must start with the text before the star. No other `*` is accepted. Deny wins over allow. No matching rule yields `decision` `ask`. `matched_rule` is the winning rule string, or `null` when the decision is `ask`.
- Fail: `ok` false, `decision` `deny`, `matched_rule` null. Errors: `empty_tool`, `bad_rule` (unbalanced parentheses, a star that is not trailing, or an empty rule). No file write. This does not grant a real shell.

### 4. tool_search_local

- Caller: library function.
- File: `lib/tool_search_local.py`.
- Inputs: `query` (string), `catalog` (list of dicts, each with string `name` and string `description`).
- Output dict keys: `ok`, `error`, `hits`, `limited`.
- Behavior: casefold substring. A name hit outranks a description hit. `hits` holds at most five `{name, description}` dicts. `limited` is true when more than five entries matched. Skip a catalog row that is not a dict or has an empty `name`. Do not import a server, do not read the network, do not call MCP.
- Fail: `ok` false, `hits` `[]`, `limited` false. Errors: `empty_query`, `bad_catalog` if `catalog` is not a list, `no_match` if nothing matched. No file write.

### 5. seat_tools

- Caller: library function.
- File: `lib/seat_tools.py`.
- Inputs: `parent` (list of tool-name strings), `tools` (list of strings, or null), `disallowed` (list of strings, or null).
- Output dict keys: `ok`, `error`, `granted`, `unresolved`.
- Behavior: copy the public subagent filter, offline. Null `tools` and null `disallowed` grants `parent` in parent order. A `disallowed` entry strips any `(...)` suffix and removes that whole tool name from the pool. Then, if `tools` is a list, `granted` is the names in `tools` that remain in the pool, in `tools` order. Names in `tools` that are not in the pool go to `unresolved`. A name listed in both `tools` and `disallowed` is not granted.
- Fail: if `tools` is a non-empty list and `granted` is empty, `ok` false, `error` `zero_tools`, `granted` `[]`. Also `ok` false, `error` `bad_list`, if any input list contains a non-string. Do not spawn an agent. Do not publish. No file write.
