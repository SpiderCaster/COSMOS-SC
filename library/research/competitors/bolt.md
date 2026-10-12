Bolt.new

## 1. Product

Bolt.new is a StackBlitz product. The help center describes it as a browser builder for websites, web apps, and mobile apps. The first input is a chat prompt. On the homepage, type the idea and press Enter, or click Build now. A blank prompt is enough. Other starts: attach files, import one Figma frame, import a Google Stitch design, use a marketplace template (Use template), start from a team template on a Teams plan, or import a GitHub repository or a Lovable project. The quickstart walkthrough pastes one prompt that asks for dropdowns, email sign-up, login, and saved favorites, then clicks Build now. That walkthrough says the result varies and that sign-up causes Bolt to create databases.

Before the first prompt, these steps are optional. Choose an agent. Enhance prompt opens "Help us enhance your prompt," asks questions, and returns a prompt you can edit. Plan mode is a chat toggle. On a Teams plan, select a design system before the first prompt if one exists. Anyone can also pick a pre-loaded design system from the homepage palette. The 2026-10-01 note treated design systems as Teams-only. The live introduction page still requires a paid Team plan to add your own system, and it now also offers pre-loaded systems to anyone.

A human does not have to approve a plan before a page exists. Build mode is the default, and a homepage prompt creates a project and starts building. Plan mode is optional. Inside an open project, Plan mode answers from the codebase and recent messages and does not change code. Implement this plan switches to Build mode and applies the change. Plan mode on the homepage is different: it first creates the base structure of the app, then shows a plan you can revise. Plan mode may search the web and list sources. Discussion mode belonged to the v1 agent. The release-notes index says that as of 2026-08-03 the v1 agent and Discussion mode are retired and Plan mode replaces Discussion mode. That date is from the release-notes excerpt, not re-measured here.

There is no public section catalog you reorder before generation. Prompts are expected to name features one at a time. The project is a file tree, a chat, and a preview. The preview is not the published site. Publish is a second explicit action: Publish in the top right, then Publish again in the menu. Later edits stay off the live URL until Update. Unpublish is a separate confirm. Prompting the chat to publish spends tokens. The button does not. Default visibility is public. On the free plan every published site is public. Private publish is paid-only. A custom domain cannot be private. Team admins can force private-only or public-only. Only the owner or a co-owner can publish or change visibility. The Bolt Cloud overview also names a Share button for restricted access and a Publish button for a fully public site. Both that overview and the publish article were open on 2026-10-08. They do not say which control is current if the buttons differ.

What the model must not invent is not public. The quickstart tells you to sign up with dummy data. Images default to stock photos. A ban on invented reviews is not public.

## 2. Code libraries

The live product source is not public. The help center says Bolt has no public API, CLI, or SDK. `https://github.com/stackblitz/bolt.new` is a public MIT snapshot of an older builder. Its latest commit on main is 2024-12-17 (`eda10b121221b30825a4c16eec5da1fd3eb1eb99`). That tree is the builder app, not a generated site, and it disagrees with the 2026 product (GitHub sync, PostgreSQL, Expo). Do not treat its prompt as the current procedure.

That snapshot's own packages, from `package.json`, include `@remix-run/react`, `@remix-run/cloudflare`, `vite`, `unocss`, `react` 18, `@webcontainer/api`, the `ai` package, `@ai-sdk/anthropic`, CodeMirror language packages, `@xterm/xterm`, `nanostores`, and two Radix packages (`@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`). CSS for that builder is UnoCSS plus SCSS under `app/styles/`. File roles, not source: `app/lib/webcontainer/index.ts` boots `WebContainer` with a workdir name. `app/lib/.server/llm/prompts.ts` is the system prompt. `app/lib/.server/llm/model.ts` names `claude-3-5-sonnet-20240620`. `app/types/actions.ts` allows two action types, `file` and `shell`. `app/lib/runtime/message-parser.ts` parses those actions. The prompt in that file prefers Vite, npm, and writing dependencies into `package.json`. It says Git is not available, native binaries cannot run, and Python is limited to the standard library. The current GitHub article says Bolt commits to GitHub. The current database article says PostgreSQL. The snapshot lost.

WebContainers, documented at webcontainers.io and linked from the glossary, are StackBlitz's in-browser Node runtime. The public API page shows boot, mount a file tree, spawn `npm`, and run a dev script. Native `npm`, `pnpm`, and `yarn` are named. The live glossary says WebContainers run Bolt's development environment in the browser, with no local install. Chromium browsers run that environment. Safari Code view is read-only, and Safari previews are hosted. A hosted preview is not the live site. As of April 2026, projects on the new code-storage format no longer offer Open in StackBlitz. Code view remains.

For a generated project, the live docs do not publish one default `package.json`, CSS system, or token file. The glossary says Bolt focuses on JavaScript frameworks such as React and Vue, Bolt chooses a framework, and a prompt can name another. Backends are Node.js only. PHP and Python backends are not supported. The quickstart's title edit is in `App.tsx`. That is one walkthrough, not a stated default. The intro-databases page names `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` for Bolt and Supabase databases. The `VITE_` prefix is a Vite convention. It is not a promise that every new site is Vite. A default theme file is not public.

Pre-loaded design systems named on the introduction page: Chakra, Material UI, and Shadcn. They can start a project. You cannot edit those pre-loaded systems. A team's own system is compiled from sources into a Storybook inside Bolt. Source types: files (up to 10, or a zip), a public docs URL, a public GitHub repo, a published Storybook URL, and npm packages (a name, an npmjs.com URL, or a `.tgz`). The add page's examples are `@shadcn/ui` and `@radix-ui/react-dialog`. Private registries can be saved for the org. Documentation websites alone are described as producing a theme rather than reusable components. Agent instructions can say which theme or framework to keep. The generated Storybook is not the app. Its left pane has Collections (components, icons, illustrations, tokens) and Pages (typography, color, spacing, theming). You browse it. You do not edit it. Sync pulls changed sources and keeps revisions. Switching a revision affects every project that uses that system. Attaching a system to an existing project does not rewrite code until a prompt asks. A prompt can `@` a component by name. A Figma import while a design system is active should use the Screenshot option. The Code option is described as unaware of the design system. Figma import uses Anima. Google Stitch can export screenshots plus page HTML into the Bolt prompt, and a downloaded `DESIGN.md` can be saved at the project root and pointed at from project knowledge. `DESIGN.md` is named as an open format. Its schema is not copied here.

A section is not a stored object. The page is whatever files the chosen framework uses. The public way to point at a piece of UI is Select on a preview element, Target file, Lock file, Lock all, highlight-and-Ask Bolt, or `@` a path or design-system component. Project skills live in the project's code and stay on. A skill file needs frontmatter fields `name` and `description`, then instructions. Bolt-curated skill names: SEO/GEO, Skill Creator, Web Design Guidelines, Writing Guidelines. Their instruction text is not public. `agents.md` in the project is found automatically. The file name is required. It may point at other files, but the main instructions have to be in `agents.md`. Project knowledge is a separate text field for goals, features, and design principles. It survives `/clear`. After `/clear`, the codebase remains and the recent chat does not. Knowledge also exists at account and team scope. The 2026-10-01 note documented `.bolt/ignore` with `*` wildcards. On 2026-10-08, `https://support.bolt.new/faqs/troubleshooting/guide` redirects to `https://support.bolt.new/troubleshooting/issues`, and that page does not describe `.bolt/ignore`. Whether the file still works is not public. Lock file and Lock all are the current documented write limits. An allow, ask, or deny command grammar is not public.

Two current pages disagree on file size. Manage context says to list files over about 700 lines and not change them yet. The issues page's large-project tips say to refactor a file around 500 lines or more. Neither is a measured limit.

## 3. Mobile

The product runs in a phone browser: start a project, chat, and publish. Code view, project settings, version history, visual edits, and the database are not on the mobile client. Publish from mobile is always public. Visibility cannot be changed there. A second Publish is still required to push changes.

For the generated site, there is no public pixel floor, type size, tap size, or breakpoint list. Preview controls include Responsive mode, which shows different devices and screen sizes. The Figma article says to open Responsive mode, pick a device, or drag the preview width. It points at Anima's Figma guide for responsive frames, or a prompt that asks Bolt to make a design responsive. Contrast, heading size, and a mobile drawer are not public requirements. The issues page tells you to set up navigation so people can move between pages. It does not specify a phone menu.

`mobile app` in the first prompt is an Expo target, not a responsive website rule. Web projects do not switch to mobile cleanly. Expo builds one JavaScript app for iOS, Android, and web. Device Preview shows a QR code for Expo Go. Store builds use EAS outside the browser (`app.json` fields `name` and `slug`, then `eas` commands). Those commands are the Expo publish path, not the website publish path. A generated website's small-screen CSS is not public.

## 4. SEO

Documented index control is publish visibility, not a meta-tag checklist. A public site can be viewed by anyone, and the publish article says search engines can find and list it. A private site cannot, and search engines cannot list it. Private is paid-only, and a custom domain forces public. Unpublish takes a Bolt-hosted site offline. HTTPS is automatic for connected domains. The Bolt Cloud overview says a new project "is ready for search engines from the start" and "loads quickly." Those are claims. Measured ranking or lab speed is not public.

`https://support.bolt.new/cloud/hosting/seo` returned 307 to `/cloud/hosting.md` on 2026-10-08. The current `llms.txt` index has no SEO article. A search-index excerpt of that old URL described a paid SEO Boost prerender, title and description, Open Graph, Twitter cards, a canonical URL, structured data, and anchor links. Because the live URL redirects, that procedure is not public now. The prompt library has a category named SEO. The article does not print the prompt text. The curated skill SEO/GEO is a name only. Its body is not public.

Sitemap generation, `robots.txt`, a canonical link, a title and description writer, Open Graph, JSON-LD types, heading order, an internal-link rule, and page-speed scores are not public on the pages opened. Hosting plans do publish quotas: free is up to 10 GB and 333,333 requests a month, with a hard stop. Pro is up to 30 GB and 1 million requests, then a spending cap. Those are transfer caps, not Core Web Vitals. Analytics on a paid Bolt-hosted site shows visitors, pageviews, top pages, bandwidth, sources, locations, and 404s, for up to 30 days, including crawler traffic. There is no documented filter that removes bots. Third-party analytics means pasting that vendor's script or prompting Bolt to paste it.

## 5. Dynamic behavior

A published Bolt site is the project's own JavaScript build on Bolt hosting, or on Netlify if that integration is used. One named client runtime for every site is not public. The preview runtime is WebContainers in Chromium, or a hosted preview in Safari. Bolt Cloud is described as powered by platforms like Netlify and Supabase.

There is no public CMS and no section model. Changing content that users edit means a database. Bolt Database is PostgreSQL. Bolt creates one when the project needs it, or when the prompt asks. A prompt can refuse it and ask for local storage instead. The quickstart's sign-up app gets a favorites table and a user table. Version history does not restore the database. An unpublished database can pause after six days of low use. A published project's database does not pause that way. Tables, rows, and columns are the data model. Real-time updates are documented for Postgres. Row-level security is a database security check. The file-storage article says you can see buckets, labeled Public or Private, and cannot yet manage individual files. The Cloud overview says you can view all files in one place. The storage article is the more specific one.

Accounts: email sign-up and login, optional email confirm, password rules, and Google sign-in. Leaked-password checks use Have I Been Pwned and start on for a Bolt-created database. Email templates use Supabase-style fields such as `{{ .ConfirmationURL }}` and `{{ .Token }}`. Auth email defaults to Supabase's sender until custom SMTP is set. The send-email article says Bolt often picks Resend if you do not name a provider, and also names Mailgun, Postmark, and SendGrid. The secret name it specifies is `RESEND_API_KEY`. Server functions (also called edge functions) run off the browser for payments, webhooks, mail, and other server work. How the agent calls the database, beyond creating it when needed, is not public.

Forms that only display are not given a product object. The token article's example of a contact or help page does not name an endpoint. A form that stores data uses the database. A form that sends mail uses a server function. Stripe needs a Bolt or Supabase database, authentication, and edge functions. Checkout stays server-side. Test-card numbers are in the Stripe article. They are not repeated here.

Client edits before save: Select, then a visual-edit batch (text, colors, font size, alignment, links, alt text, object fit). The preview updates immediately. Code updates only when you click Save changes. Direct Code view edits save with Save or Ctrl+S, then Bolt builds. Terminal commands in Code view, including `npm run build`, `npx knip --production --fix --allow-remove-files`, `npx depcheck`, and `npm dedupe`, do not spend tokens. A named agent shell schema is not public.

Connectors are MCP. Built-in names include Notion, Linear, and GitHub, plus a custom server URL with HTTP or SSE and API key, OAuth, or no auth. Tool names a connector exposes are chosen per server and are not one public Bolt list. Auto-enable for all projects is a separate switch. GitHub the integration syncs the repo. GitHub the connector is for issues and other non-commit work. New repos start private on `main`. Bolt commits when a change does not break the project and polls GitHub about every 30 seconds. Merging branches is not done inside Bolt.

Agents on the live agents page: Standard on every plan, Max on paid plans, and Forge when the account has it. Bolt picks the model for Standard and Max. The project remembers the agent. Forge is a third picker entry for open-source models. The Forge article excerpt lists GLM 5.3, GLM 5.3 Flash, Kimi K3, and DeepSeek v4 Pro, and says the research preview runs 2026-09-14 through 2026-10-14. The glossary still says only Standard and Max. The agents page is the one that includes Forge.

Images: stock by default. Uploads may be `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, or `.svg`. Paid plans can edit an image with AI or generate one. Generated images are converted to WebP. That is a product statement, not a measured speed result. The 2026-10-01 note said image generation was not public. The images article now documents it. Chat attachments are also `.pdf`, text, many source extensions, and config files. Bolt still only builds JavaScript apps. Other languages are reference. Free attach limit: 5 files, 10 MB each. Paid: 20 files, 100 MB each. Code view can drop an image into the `Public` folder and copy a relative path without spending tokens. A video poster's path may be a project path or an external URL. Hotlink rules for ordinary images are not public.

## 6. Already in SpiderCaster

SpiderCaster already separates a local preview from a human publish. `compose` writes an offline site that stays noindex until a human runs `library bind --live`. Bolt's preview is also not the live site, but a public Publish is indexable by the help center's own words. SpiderCaster's gate is the stricter one.

The first input on both sides can be a short brief. SpiderCaster then builds only from real `copy/` files. Bolt builds from the prompt and may use stock images and starter behavior. `compose` reorders sections the copy already produced, paints one mold, and inserts one catalog part per section plus a header and a footer. It writes `structure.json`, `site.json`, and `report.json`. Bolt has no public section catalog. A mold picked before paint is the analog of choosing a design system before the first prompt, without Storybook, npm, or Shadcn.

`lock.txt` already makes `tools apply` refuse a path. That is the analog of Lock file, not of a browser IDE. Checker floors already cover body text 18px, chrome 16px, contrast 4.5:1, tap 44px, no SAMPLE, lorem, or placeholder, no hotlinked images, a relative canonical, one h1, WebSite JSON-LD with no aggregateRating, visible FAQ text when FAQPage is present, a skip link, scroll-margin, a sticky header, a mobile drawer, and no sideways overflow at 360, 390, and 412. `visit` measures at 390 and 1280 when Playwright is installed. `check.py` also requires a non-empty meta description and `favicon.svg`. The SEO seat's hands are `uniqueness` and `meta_basics`. None of that is Expo, a device dropdown, or a JS prerender.

Seat skills and `seat_gate` already bound which hand may run. That is a local permission list, not Bolt Plan mode and not an `agents.md` chat file.

## 7. Worth building

One item fits the static, stdlib, real-copy, noindex-until-a-human-publishes rule.

In-project Plan mode does not change files until the human chooses Implement this plan. SpiderCaster can mirror that without a chat model: a local plan that lists section ids already present in copy, and a compose step that does not write HTML until a human accept flag exists in the project. Do not copy homepage Plan mode, which creates the base structure before the plan is approved.

Do not build the rest. No WebContainer, npm, Vite, React, Tailwind, shadcn, Storybook, Chakra, or Material UI runtime. No Expo app. No database, accounts, server functions, Stripe, or email provider. No MCP connector. No stock photos, no generated images, no external poster URL. No Knip or other `npx` cleanup. No chat control that publishes. No security audit that rewrites the project. No public-by-default host and no "Made in Bolt" badge. No SEO Boost-style prerender. The old SEO URL now redirects, so there is no live tag procedure to reimplement. Open Graph, a sitemap, and `robots.txt` stay not public on Bolt's current help center. If they are added later, they have to be static files from real copy, still noindex until `library bind --live`.

## 8. Sources

Opened 2026-10-08 unless noted.

https://support.bolt.new/llms.txt
https://support.bolt.new/get-started/intro-bolt.md
https://support.bolt.new/get-started/quickstart.md
https://support.bolt.new/get-started/project-lifecycle.md
https://support.bolt.new/building/start-project.md
https://support.bolt.new/best-practices/plan-mode.md
https://support.bolt.new/best-practices/prompting-effectively.md
https://support.bolt.new/best-practices/manage-context.md
https://support.bolt.new/best-practices/maximizing-token-efficiency.md
https://support.bolt.new/concepts/supported-technologies.md
https://support.bolt.new/concepts/glossary.md
https://support.bolt.new/concepts/intro-databases.md
https://support.bolt.new/concepts/faq.md excerpt in search results, full page not fetched
https://support.bolt.new/building/using-bolt/agents.md
https://support.bolt.new/building/using-bolt/code-view.md
https://support.bolt.new/building/chat-tools.md
https://support.bolt.new/building/using-bolt/connect-mcp.md
https://support.bolt.new/building/skills.md
https://support.bolt.new/building/images.md
https://support.bolt.new/building/upload-files.md
https://support.bolt.new/building/visual-edits.md
https://support.bolt.new/building/preview-controls.md
https://support.bolt.new/building/prompt-library.md
https://support.bolt.new/building/security.md
https://support.bolt.new/building/design-system/introduction.md
https://support.bolt.new/building/design-system/add-design-system.md
https://support.bolt.new/building/design-system/use-design-system.md
https://support.bolt.new/building/design-system/view-design-system.md
https://support.bolt.new/building/design-system/sync-design-system.md
https://support.bolt.new/settings/project-settings.md
https://support.bolt.new/cloud/hosting/publish.md
https://support.bolt.new/cloud/hosting.md
https://support.bolt.new/cloud/hosting/plans.md
https://support.bolt.new/cloud/hosting/analytics.md
https://support.bolt.new/cloud/hosting/seo probed, 307 to /cloud/hosting.md, procedure not on the live page
https://support.bolt.new/cloud/bolt-cloud.md
https://support.bolt.new/cloud/database.md
https://support.bolt.new/cloud/database/authentication.md
https://support.bolt.new/cloud/database/server-functions.md
https://support.bolt.new/cloud/database/security.md
https://support.bolt.new/cloud/database/file-storage.md
https://support.bolt.new/cloud/database/send-emails.md
https://support.bolt.new/integrations/expo.md
https://support.bolt.new/integrations/figma.md
https://support.bolt.new/integrations/git.md
https://support.bolt.new/integrations/stripe.md
https://support.bolt.new/integrations/supabase.md
https://support.bolt.new/integrations/google-stitch.md
https://support.bolt.new/troubleshooting/issues.md
https://support.bolt.new/faqs/troubleshooting/guide probed, 308 to /troubleshooting/issues
https://support.bolt.new/account-and-subscription/bolt-forge.md excerpt, model names and preview dates
https://support.bolt.new/release-notes excerpt, v1 and Discussion mode retirement date
https://github.com/stackblitz/bolt.new snapshot, last commit 2024-12-17
https://raw.githubusercontent.com/stackblitz/bolt.new/main/package.json
https://raw.githubusercontent.com/stackblitz/bolt.new/main/app/lib/.server/llm/prompts.ts file role and constraints only, source not copied
https://raw.githubusercontent.com/stackblitz/bolt.new/main/app/types/actions.ts
https://raw.githubusercontent.com/stackblitz/bolt.new/main/app/lib/webcontainer/index.ts
https://raw.githubusercontent.com/stackblitz/bolt.new/main/app/lib/.server/llm/model.ts
https://webcontainers.io/
https://developer.stackblitz.com/platform/api/webcontainer-api page shell only
https://support.bolt.new/building/switch-v1-projects excerpt in search results
Oct 1 notes compared, not treated as current: library/research/HOW_PRO_BUILDERS.md and library/research/app/HOW_CODE_BUILDERS_TOOLS.md
