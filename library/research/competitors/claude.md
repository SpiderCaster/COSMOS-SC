Claude Code, Claude Design, and artifacts

## 1. Product

Three surfaces, not one site builder. None of the opened docs describe a multi-page marketing site with a section catalog.

Claude Code publishes an artifact: one live page at a private URL on claude.ai. The first input is a plain-language request that names the feature or the visual output. Claude may also publish an artifact on its own when the output suits a page. Unless a path is named, it writes HTML or Markdown in a temporary directory outside the project, then publishes. The page updates in place. Each publish is a version. The opened examples are a pull-request walkthrough, a dashboard, side-by-side options, a checklist, and a connector-backed status board. It is not a hosted app. The docs say to deploy a real internal tool elsewhere.

A human does not approve a plan before that page exists, unless the session is already in plan mode. Plan mode explores and proposes a plan without editing source files. In plan mode, Claude Code asks before the first publish of each artifact. Outside plan mode, a new artifact from a prompt the person typed publishes with no permission prompt and no classifier review, unless the publish declares runtime capabilities (connector calls or a file download). Turning feature-flag fetching off also forces that ask, or a classifier review in auto mode. Auto mode, not a human plan, is the built-in start for interactive terminal and VS Code sessions on Claude Code v2.1.283 or later. After a public share, Claude Code asks once per conversation before changing the page, or the classifier reviews the change in auto mode. The page stays private to the author until Share. That is an audience gate, not a plan gate.

`/design` with a brief drafts Claude Design artboards and publishes the canvas. `/slides` with a brief creates a deck. `/slides` with no brief asks what the deck is about before creating anything. Claude Docs is a claude.ai connector (`claude.ai Claude Docs` in `/mcp`), not a slash command. A README stays a file in the repo.

Claude Design, in beta on paid plans, builds designs, interactive prototypes, one-pagers, and other visual work on a canvas beside a conversation. Use it from a chat (or Output > Design), the Artifacts tab, Claude Code (`/design`, `/design-sync`), or the standalone app at claude.ai/design. The documented flow is: start, attach or import a design system, add screenshots or a codebase, describe the build, review the canvas, refine, then export or share. A landing-page prompt in the guide is an example, not a required block set. Claude may ask clarifying questions. Nothing on that page requires the human to approve a plan before the canvas exists. Review is after the first generation. An accessibility, contrast, hierarchy, and usability review is something the person can ask for. It is not a gate. Designs start private. Share chooses who can open one and whether they can view, comment, or edit. Claude Design does not have version history. Asking to save the current direction and try another is a chat instruction, not a version list.

Chat artifacts (separate from the Claude Code page) can be a document, a code snippet, a single-page site, an image, a diagram, a dashboard, or a small interactive tool. Templates are Design, Slides, and Docs. They are a paid-plan beta, on by default for Pro, Max, and Team, off on Enterprise until an owner enables each one. Creating an ordinary artifact in chat is also on Free. Templates and Claude Code publish both require the capabilities setting for cloud code execution and file creation. Legacy chat artifacts are those made before 16 September 2026. They still open. New ones of that older kind are not created. Cowork artifacts made before 19 August 2026 are a separate live-artifact path. They keep working and cannot be edited in place. That path was not re-researched here.

October 2026-10-01 notes still match the live Claude Code page on the single HTML page, the private URL, and plan mode. They do not match the live Design page on version history (now stated as absent) or on the export list (now longer; see Sources).

## 2. Code libraries

### Skill files

A skill is a folder. `SKILL.md` is required: YAML frontmatter between `---` lines, then Markdown. The opening `---` must be the first line. The body loads when the skill is used. Supporting files sit beside it. The docs say to keep `SKILL.md` under 500 lines and point at the other files. A bundled script is executed, not loaded as prompt text. Custom commands are skills: `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`.

Load paths: enterprise managed settings, `~/.claude/skills/`, project `.claude/skills/`, nested `<subdir>/.claude/skills/` once Claude works in that directory, a plugin `skills/` directory as `/plugin-name:skill-name`, and skills enabled on the claude.ai account. Cowork and cloud sessions do not read `~/.claude/skills/` on the machine. They load account skills. Cloud sessions also load project skills committed in the repo. Account skills download into `~/.claude/skills/synced/`. The folder name `synced` is reserved. `anthropic-skills` is reserved for that sync namespace.

Claude Code skills follow the Agent Skills open standard and add Claude Code fields. Uploads to claude.ai, the Skills API, and `package_skill.py` in `anthropics/skills` allow only `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. Any other key fails the upload. The public registry command is `/plugin marketplace add anthropics/skills`, then `document-skills` or `example-skills` from `anthropic-agent-skills`. The repo README says the copy in git can differ from what Claude runs. Treat the repo as the public recipe, not as proof of the closed built-in skill.

`allowed-tools` pre-approves named tools for the turn that invoked the skill. It does not remove other tools. `disallowed-tools` removes tools while the skill is active. Both clear on the next user message. A skill does not add a tool name. It runs through the existing `Skill` tool. MCP is how a new tool name appears.

### Public design and artifact skills

These are files in public git. They are not the Claude Design canvas, and the docs do not say the built-in artifact design skill is any of them. That built-in skill's source is not public.

| Public skill | File role |
| --- | --- |
| `skills/frontend-design/SKILL.md` | One instruction file. It tells the model to plan a compact token set (color, type, layout, principles), review that plan against the brief, then write the page. It also tells the model to invent copy when the brief has none. |
| `skills/web-artifacts-builder/` | `SKILL.md`, `scripts/init-artifact.sh`, `scripts/bundle-artifact.sh`, `scripts/shadcn-components.tar.gz`. Init scaffolds a project. Bundle writes `bundle.html` with CSS and JavaScript inlined. The tarball was not unpacked. |
| `skills/theme-factory/` | `SKILL.md`, `theme-showcase.pdf`, and ten `themes/<slug>.md` files. Each theme file has a color list, header and body type roles, and a use note. The skill says to show the PDF and wait for a choice. |
| `skills/brand-guidelines/SKILL.md` | Anthropic's own colors and two font families with fallbacks, for styling an artifact. No separate token file. |
| `skills/canvas-design/` | `SKILL.md` plus a `canvas-fonts/` directory. Output is a philosophy `.md` and a `.pdf` or `.png`. Not HTML. |
| `knowledge-work-plugins/design/` | A Cowork and Claude Code plugin, installed as `design@knowledge-work-plugins`. Skills are instruction files only: `design-system`, `design-critique`, `design-handoff`, `ux-copy`, `accessibility-review`, `user-research`, `research-synthesis`. The design-system skill describes token categories in prose (color, type, spacing, borders, shadows, motion) and component fields (variants, states, sizes). It does not ship a token schema. |

The artifact builder script names this stack: React 18, TypeScript, Vite (`react-ts` template; Vite 5.4.11 on Node 18, latest on Node 20+), Parcel, Tailwind CSS 3.4.1, PostCSS, Autoprefixer, `tailwindcss-animate`, `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react`, `next-themes`, and shadcn/ui. Radix packages are one `@radix-ui/react-*` module per primitive the script installs. Other named packages: `sonner`, `cmdk`, `vaul`, `embla-carousel-react`, `react-day-picker`, `react-resizable-panels`, `date-fns`, `react-hook-form`, `@hookform/resolvers`, `zod`. Bundle-time packages: `parcel`, `@parcel/config-default`, `parcel-resolver-tspaths`, `html-inline`. `components.json` points at the shadcn schema and records the Tailwind entry `src/index.css` plus aliases for components, ui, lib, and hooks. Components are extracted into `src/` from the tarball. The script's public inventory is accordion, alert, aspect-ratio, avatar, badge, breadcrumb, button, calendar, card, carousel, checkbox, collapsible, command, context-menu, dialog, drawer, dropdown-menu, form, hover-card, input, label, menubar, navigation-menu, popover, progress, radio-group, resizable, scroll-area, select, separator, sheet, skeleton, slider, sonner, switch, table, tabs, textarea, toast, toggle, toggle-group, tooltip. A section in that recipe is a React component in the one bundled file. The product page still says an artifact cannot serve multiple routes. The skill's "routing" claim does not override that.

### What the product page allows a published artifact to load

The viewer source is not public. The page is one `.html`, `.htm`, or `.md` file, UTF-8 or little-endian UTF-16 with a byte-order mark. Claude Code wraps it in an HTML shell and serves it from a sandboxed `*.claudeusercontent.com` origin under a strict CSP. Markdown renders as a styled document. The rendered page must be 16 MiB or smaller.

External scripts may come only from cdnjs, unpkg, the Tailwind CDN, the jQuery CDN, and selected jsDelivr paths such as `/npm/`. The docs name React or a charting library as examples of what those hosts are for. The only external font host is Google Fonts. Any other face is inlined as a `@font-face` data URI, with a fallback stack. The CSP blocks every external image. Other images are data URIs. All other CSS and JavaScript is inlined. `fetch`, XHR, and WebSocket may reach only the page origin and the Google Fonts hosts. Connector calls are not a page fetch. claude.ai makes them. A path that names a network host is refused unread. The mapped-drive exception is on a linked errors page that was not opened, so it is not restated.

There is no public component registry inside the viewer. There is no documented shadcn install on the product page. The CDN allowlist is the product constraint. The git skill is one way to produce a file that fits it.

### Design-system files

For a Claude Code artifact, a built-in design skill picks palette, type, and layout, and looks for an existing design system in the project first. Record tokens where Claude can read them. The documented places are `CLAUDE.md` or a theme file in the repo. The example is a short Markdown list of color, type, and spacing roles. The page says any clear list works. Precedence: the person's prompt, then that recorded system, then the skill. The theme file's required extension and schema are not public.

For Claude Design, a new project inherits the organization's design system. The system is itself an artifact, managed in Settings > Design systems. Create it from a chat, or run `/design-sync` in Claude Code when the system is already React components. `/design-sync` reads tokens and components from that code. Other inputs the setup guide names: a GitHub repo, design files, Figma, decks, logos, fonts, screenshots, and raw uploads. Claude extracts a color palette, typography, components (buttons, cards, navigation, and other patterns), and layout patterns (spacing, grid, page structure). It checks output against that system and corrects it before the person sees it. Naming a component in the prompt ("Use the Primary Button component") is an instruction, not a documented tool call. Migrated systems from claude.ai/design become artifacts. The cleanup banner covers a guide, tokens, and components. The on-disk layout of that artifact is not public. Third-party posts that name a manifest JSON or a `.design-sync/` config are not official docs and are not treated as the format.

A section is not a catalog row. In an HTML artifact, multi-section content is in-page anchors, because relative links do not resolve and nothing is deployed beside the page. In Claude Design, a section is an artboard on one canvas, or an element the person drags on that canvas. Direct edits save automatically. Export of a design is a zip, PDF, PPTX, standalone HTML, or a send to another tool. Google Slides export is only at claude.ai/design. The send list on the live guide is Adobe Experience Manager, Adobe for Creativity, Adobe Journey Optimizer, Base44, Canva, Gamma, HubSpot, Hyperframes, Lovable, Miro, Netlify, Replit, v0, Vercel, and Wix, plus a handoff to Claude Code (local agent or Claude Code on the web). What is inside the zip is not public. The October notes listed a shorter send list. The live guide is the longer one above.

## 3. Mobile

No opened doc requires a viewport, a breakpoint, a tap size, or a generated small-screen stylesheet.

Claude Design's guide says to mention whether the design needs to work on mobile, tablet, and desktop, or only one of those. That is prompt advice. Hero is an example prompt, not a required block. The phone apps can ask for a design, a deck, or a doc and show it in the Artifacts tab. Editing the canvas and changing sharing need the web or desktop app. The guide lists that as a limitation.

The public `frontend-design` skill says to build responsive down to mobile, with visible keyboard focus, reduced motion respected, and accessible color. The repo disclaimer says Claude's running behavior may differ. It is not a measured breakpoint spec. The artifact product page does not repeat those rules.

Whether the viewer shell sets a viewport meta tag is not public.

## 4. SEO

Documented facts are separated from ranking claims. Nothing opened promises a ranking.

| Item | What the opened pages say |
| --- | --- |
| Sitemap | Not public. |
| robots.txt | Not public. |
| Canonical | Not public. |
| Title and description | Claude picks an artifact title and an emoji, and can pick a tab icon. The person can ask for a specific title, emoji, or icon. A meta description is not public. |
| Open Graph | Not public. |
| JSON-LD | Not public. No type is named. |
| Heading order | Not public. No h1 rule is stated. |
| Internal links | Relative links do not resolve. Multi-section content uses in-page anchors. That is a one-file limit, not a link graph. |
| Page speed | The rendered page must be 16 MiB or smaller. The docs suggest SVG or CSS instead of large raster data URIs to cut tokens. No Core Web Vitals number and no ranking claim. |
| Index controls | An artifact is private until Share. On Team and Enterprise, public sharing is off until an Owner turns on External sharing. Turning that off blocks existing public links. Search-engine indexing of a public URL is not public. |

Two live pages disagree on who can open a public link. The Claude Code artifacts page says a public link can be opened with no claude.ai sign-in, and a signed-out viewer, or a viewer outside the organization, sees the label `Content is user-generated and unverified` instead of the author's name. The help-center share article, which says it covers Claude Code, says everyone needs a Claude account except a legacy artifact published from a chat. October notes followed the Claude Code page. Both pages were open on 2026-10-08. The sign-in rule is not settled here.

Sharing levels that are documented: view, commenter, and edit, depending on the artifact type. Commenters and editors on an organization share can comment. People whose only access is the public link do not see comments. That is access control, not an index control.

## 5. Dynamic behavior

The Claude Code artifact runtime is a static page in the sandboxed viewer. It has no backend of its own and cannot authenticate viewers. Client behavior is HTML, CSS, and inline JavaScript, plus scripts from the CDN hosts in section 2. Sliders, toggles, and inputs are in that page. A form has nowhere documented to post. There is no CMS and no account system on the page.

Two optional runtimes sit behind claude.ai, not in the page:

- Connector calls, on Pro, Max, Team, and Enterprise, Claude Code v2.1.209 or later. The publish declares which claude.ai connectors the page may call. The call uses the viewer's connection, after that viewer approves. A viewer who declines still sees the page without the live sections. A signed-out public viewer does not get connector calls. The page may refresh on an interval or a control. Responses cache in the browser, then update. Local MCP servers from `.mcp.json` can feed the build. The published page cannot call them. Actions with side effects also use the viewer's account.
- File download, as a declared capability. The page cannot start its own download, including `data:` and `blob:` links.

Chat artifacts, on the help-center page, add two more runtimes. An artifact can call Claude on Anthropic's infrastructure. Viewers sign in and use their own plan limits. New artifacts ask the first time. Storage, on Pro and above, on web and desktop, is personal or shared, text only, 20 MB per artifact. That is not a CMS. Whoever builds the artifact chooses which data is shared. Legacy storage works only after publish, and unpublishing deletes it. New artifacts can store without being published.

Claude Design's runtime is the canvas editor: chat, inline comments, and direct drag, resize, and align. Multi-person editing is described as basic and unreliable. Inline comments sometimes fail to stick. The documented workaround is to paste the note into chat. Export and handoff are file or tool transfers, not a live site runtime.

No opened page names a marketing-site account, a blog CMS, or a deployed chat widget.

## 6. Already in SpiderCaster

`compose` reads real `copy/` files, plans offline, reorders sections only with a package frame, paints one mold, and inserts one catalog part per section plus a header and a footer. It writes the HTML in that same call, with `noindex` true, then writes `structure.json`, `site.json`, and `report.json`. There is no pause for a human to approve the plan before the page exists. The human gate is later: `library bind --live`. That is stricter than Claude's private URL, which can appear with no prompt, and weaker than plan mode, which asks before the first publish. The engine does not publish from compose.

Sections are catalog rows. A frame reorders sections the copy already produced. A mold supplies a palette accent and a template. That is a closed local model, not a React component tree and not an artboard. The 208-part catalog, fourteen frames, and three molds stay in the engine. Claude's CDN stack, shadcn archive, and design-system artifact are not imported.

The checker already requires body text 18px, chrome 16px, contrast 4.5:1 (large text 3:1), a 44px tap target, no sideways overflow at 360, 390, and 412, a skip link, scroll-margin, a sticky header, and a mobile drawer. `visit` measures at 390 and 1280 when Playwright is installed. `lib/render.py` includes a visible `focus-visible` outline and a `prefers-reduced-motion` reduction. Claude does not document those floors. The public frontend-design skill only names the same ideas as advice.

On-page tags the checker already covers, and Claude does not document: a relative canonical, a title, one h1, WebSite JSON-LD with no aggregateRating, and FAQPage only when the questions are visible. `lib/render.py` also writes `og:title` and `og:description`. The index page links `favicon.svg`, and the checker requires that file. A noindex meta tag follows the build flag until a human marks the build indexable. No sitemap and no `robots.txt` turned up in the Python sources. A skipped-heading rule was not found. Dead links are dropped when a frame is applied. That is not a sitewide link map.

The page is static HTML. There is no account, no CMS, no connector refresh, no artifact storage, and no chat control. Placeholder and lorem text already fail the checker. The public frontend-design instruction to invent copy when the brief is thin is the opposite of that rule.

## 7. Worth building

Only static HTML, stdlib, real copy, and noindex until a human publishes. Reimplement. Do not import the React, Tailwind, Parcel, or shadcn recipe, the CDN allowlist, the design-system artifact, or the theme-factory palettes.

A project token file the painter reads before it chooses colors. Plain text or a small JSON object: named color roles, two type roles, and a spacing step. Precedence copied as a rule, not as Claude's file: the copy the human wrote outranks the token file, and the token file outranks the mold accent. The checker already measures contrast. Extend that check so a named text and background pair has to meet the existing 4.5:1 floor. Do not add a second CSS runtime.

A compose pause. Write `structure.json` for the section order the copy already produced, and do not write HTML until the human accepts that file. Claude only asks in plan mode, and it asks before publish rather than before a multi-page plan. The useful slice is the pause. No chat button, no canvas, and no second publish path. `bind --live` stays the only way off noindex.

Not worth building, because they break the static rule or invent copy: connector-backed sections, artifact storage, comment-to-model, the bundled component archive, Google Fonts as a hotlink, data-URI photos in place of local images, and the frontend-design step that writes placeholder copy.

## 8. Sources

Opened 2026-10-08 unless noted. October notes in `library/research/HOW_PRO_BUILDERS.md` and `library/research/app/HOW_CLAUDE_TOOLS.md` are dated 2026-10-01 and were not used where a live page differs.

https://code.claude.com/docs/en/artifacts — Claude Code artifact create, plan-mode ask, CSP, CDN hosts, single page, design-skill precedence, `/design` and `/slides`.
https://code.claude.com/docs/en/skills — `SKILL.md` locations, frontmatter, Agent Skills upload fields, bundled skills.
https://code.claude.com/docs/en/how-claude-code-works — agent loop, plan mode, Auto as the interactive default on v2.1.283 or later.
https://support.claude.com/en/articles/14604416-get-started-with-claude-design — canvas flow, `/design-sync`, export list, mobile limit, no version history.
https://support.claude.com/en/articles/14604397-set-up-your-design-system-in-claude-design — design system as an artifact, React `/design-sync`, extracted palette and components.
https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them — chat artifacts, templates, Claude calls, 20 MB text storage, legacy date.
https://support.claude.com/en/articles/9547008-publish-and-share-artifacts — share levels; disagrees with the Claude Code page on sign-in for a public link.
https://github.com/anthropics/skills — public skill repo and marketplace names. README says the git copy can differ from Claude.
https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md — public design instruction file, including invented copy.
https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md — React, Tailwind, shadcn recipe and `bundle.html`.
https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/scripts/init-artifact.sh — package names and the component inventory. CSS in that script was not copied.
https://github.com/anthropics/skills/blob/main/skills/theme-factory/SKILL.md — ten theme files and the wait-for-a-choice step.
https://github.com/anthropics/skills/blob/main/skills/theme-factory/themes/arctic-frost.md — theme file shape only. One file opened. Colors were not copied.
https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md — single-file Anthropic brand skill. Colors were not copied.
https://github.com/anthropics/skills/blob/main/skills/canvas-design/SKILL.md — `.md` plus `.pdf` or `.png`, not a site.
https://github.com/anthropics/knowledge-work-plugins/blob/main/design/README.md — design plugin commands and skill names.
https://github.com/anthropics/knowledge-work-plugins/blob/main/design/skills/design-system/SKILL.md — prose token categories, no schema file.
