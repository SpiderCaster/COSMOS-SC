Lovable

Opened 2026-10-08. Public docs and the 2026-06-01 Lovable engineering post. The 2026-10-01 notes still match the quick start and the second Publish click. Where they disagree, this file follows the live page: new apps are TanStack Start, favicon and per-page titles are generated, Build can generate images, and a first UI prompt can stop on three visual directions before the full build.

## Product

Lovable builds a full-stack web app from a plain-language description, then hosts a snapshot. The docs FAQ lists SaaS apps, internal tools, dashboards, CRMs, booking apps, company sites, landing pages, portfolios, and in-app AI. It also lists decks, images, short videos, and downloadable files. It does not generate React Native. A native store binary is outside Lovable (a PWA, or a Capacitor wrapper the person builds elsewhere).

The first input, with Build selected, is the dashboard box "Ask Lovable to create…". The quick-start prompt names a business, a hero with a headline and a photo, an interactive menu, hours, a location section, the line "Use realistic sample content throughout", a visual tone, "Works well on mobile", and "No login or database yet." Other starts: attach a mockup, remix a template, open a URL that already carries the prompt, or approve a "Create a new project?" card from Chats. You cannot start from an existing Git repository. Git sync creates a new repo from the Lovable project.

A human does not have to approve a plan before the page exists. Build is the default, and it writes the project immediately. Two optional stops sit in front of that write:

- Design guidance, on a first UI message whose look is not already specified, shows three lightweight HTML and Tailwind directions, or a short set of type, color, and layout questions. The person submits one direction, then the full build starts. Those previews use generic copy and image placeholders. A named design system, a design template, a concrete visual brief, or a non-visual task (auth, schema, edge functions) skips this step. Dashboards and internal tools skip it.
- Plan mode investigates and writes a plan the person edits and approves. Approving switches to Build and implements that plan. Skip leaves the plan unbuilt. Chat mode neither plans nor edits code. The current plan is `.lovable/plan.md`. An approved plan moves to a dated file under `.lovable/plan/`.

Before the Publish click, the quick start tells the person to click every button and link and to cycle the preview to Mobile view. No automated critic is required before the first version exists. The SEO review is a later, separate scan.

Publish is two clicks: Publish, then Publish again, after an optional edit of the suggested `lovable.app` address. The live site is a snapshot. Preview updates immediately. Visitors see the change only after Publish, then Publish changes. Asking the chat to publish still asks for approval unless the publish tool is set to auto-approve. That chat path spends build credits. The dialog path does not. Free and Pro publishes are public. Business and Enterprise can limit the live site to the workspace or a custom audience. Unpublished projects, private sites, and branded workspace URLs (`{app}.{workspace}.lovable.app`) are not indexable.

The official quick start asks for realistic sample content. A ban on invented reviews is not public. Prompting best practices separately say to avoid "lorem ipsum" and to type real headlines. Those two pages disagree. The quick start is the default first prompt.

## Code libraries

Closed product. The generated app is ordinary project files the person can read. Lovable does not publish one canonical `package.json` for a blank project. Claims below are only what the opened pages name.

Framework, no choice. Docs FAQ: apps created from 2026-05-13 use TanStack Start and render on the server. Enterprise workspaces switched on 2026-06-22. Older apps are React + Vite and render in the browser. Next.js is not offered. The database, when there is one, is PostgreSQL through built-in Cloud or a Supabase project the person owns. A TanStack project lists `@tanstack/react-start` in `package.json`. The build config package named on the external-hosting page is `@lovable.dev/vite-tanstack-config`, which prepares server output through Nitro. The 2026-06-01 engineering post adds TanStack Router, per-route SSR, SSG, or CSR, and `createServerFn` for server-only logic. It also names `*.server.ts` and `@tanstack/react-start/server-only`. That post says the old runtime was static files on Cloudflare Pages and the new runtime is Cloudflare Workers. The hosting doc says global delivery and does not name the vendor. Pixel-level bundle contents of a new scaffold are not public.

The marketing FAQ at `lovable.dev/faq` still says React, TypeScript, Vite, Tailwind CSS, shadcn/ui, and Radix. That page disagrees with `docs.lovable.dev` on the framework. The docs page wins. Whether every new TanStack app still installs Tailwind, shadcn/ui, or Radix is not public.

What the docs do say about CSS and components:

- Design-direction previews are HTML plus Tailwind. They are not the shipped app.
- A design system discovers tokens from top-level CSS custom properties (`src/index.css`, `src/styles/tokens.css`), a `tailwind.config`, or a theme or tokens file. Components come from a barrel `src/index.ts` or `src/index.tsx`, otherwise from `src/components/`.
- Connecting a Vite design system can pull Tailwind 3 into a project that already has Tailwind 4. The docs call that a known clash, not a guaranteed default.
- Email branding reads CSS variables from `src/index.css`. The file role is public. Its rules are not copied here.
- Custom fonts are a prompt: a web-safe name, a Google Font name, or a Google Fonts specimen URL. Lovable loads it. There is no font-file upload. A font file can be added through Git sync. How the Google Font request is written is not public.
- npm installs on request. Bun writes `bun.lock` or `bun.lockb`. The person does not run a terminal. Private packages need the Enterprise managed registry.

A section is not a catalog row. It is source the agent writes into the React tree. The quick start inserts one by asking for a section between two others. Docs mention pages under `src/pages/` or `src/routes/` and components under `src/components/`. A public section-type list, and the exact route-file naming convention, are not public. 21st.dev is a third-party prompt the person pastes. Lovable then adds that component's code and the person says where it goes (hero, nav, testimonial, call to action, feature section, form). It is not a Lovable registry.

Design systems are their own Lovable projects, paid plans, React only. Release writes `.lovable/design-system.json` (tokens, component catalog, constraints), `rules/components.md`, `rules/design-tokens.md`, `rules/library-guidelines.md`, and a hand-kept `system.md`. Attach copies components to `src/design-system/<slug>/` and those knowledge files to `.lovable/rules/libraries/<slug>/`. `lovable.toml` records the link under `[[libraries]]`. One design system per project. Showcase pages, stories, tests, and scaffold entrypoints are not copied. `.dsignore` adjusts that. A workspace default is pre-selected in the + menu. The person can clear it. Design templates, which copy a whole codebase, are Business and Enterprise and are a different object.

Knowledge is plain text, always in context, 10,000 characters for the workspace and 10,000 for the project. Owners and admins edit the workspace field. Anyone who can edit the project edits its field. On a conflict, project knowledge is supposed to win. Root `AGENTS.md` is always read, including in a long session. `CLAUDE.md` and connector knowledge files are also read. The sample knowledge text recommends Tailwind, shadcn/ui, React Query, and Zustand. That sample is an example the docs show, not a measured scaffold. Skills are `SKILL.md` playbooks, loaded when the description matches, up to 100,000 characters, shared across the workspace. Built-in skills include an SEO review. Their bodies are not public.

The code editor is the Code tab. Paid plans can edit there and download the tree as a zip. Search, `@` file pills, and line references such as `Button.tsx:42` are documented. A full agent tool schema is not public. Subagents are temporary and read-only. The main agent is the only writer.

Preview is a temporary cloud environment on the right of the editor. It is not the published site. It shares the Cloud database with the published app. It can pause. Live preview can be turned off so the pane shows the last finished version. The page selector has Social and Search cards (image, title, description, and the search card's favicon) from the latest code, before publish.

## Mobile

Lovable builds responsive web pages, not a phone app. The mobile client (iOS 15+, Android 9+) is a builder: chat, preview, voice, camera, drafts, and Publish. The preview toolbar, inline comments, and OAuth connector setup are absent on a small screen. There is no offline edit.

The docs require a human check, not a published pixel floor. The quick start says to cycle the device toggle to Mobile view before publish. The preview toggle is Desktop, Tablet, and Mobile. The pixel width of each view is not public. Browser testing can try mobile, tablet, and desktop, and by default uses the current preview size. It runs when asked, in a remote browser, against the preview. An example skill in the skills doc mentions 375px and no horizontal scroll. That line is sample skill text, not a product rule.

The SEO review's page-basics check flags a missing viewport or a missing `lang` on `<html>`. It no longer runs a mobile-usability or Lighthouse audit. The page tells the person to use PageSpeed Insights for that. A generated tap-target, type-size, or overflow floor is not public.

Design questions include layout wireframes (hero grid, single column, split screen, sidebar, masonry, bento, and others). Those are choices before the build, not a small-screen stylesheet the docs print.

## SEO

Documented features, not a ranking promise. The docs say a Lovable app can rank like other modern apps, and that rank still depends on content, links, competition, and algorithms outside Lovable. The 2026-06-01 post reports a vendor measurement of +2.9% organic traffic and +98.5% AI-tool traffic after pre-rendering. That number was not measured here.

Where it lives. More, then SEO & AI search. Scan project is free. Try to fix spends build credits. Sitemap, `robots.txt`, titles, and other tags are not always generated up front. The review finds gaps and can write or repair most of them.

Crawl. New apps (from 2026-05-13) return server-rendered HTML to every request. The engineering post says routes that do not depend on per-request data can be prerendered at deploy, and that Lovable applies that when a route qualifies. Older React + Vite apps stay SPAs for people. Verified crawlers (Google, Bing, social-preview bots, and the named AI engines ChatGPT, Perplexity, Claude, Gemini) get on-request pre-rendered HTML. Other scanners see the SPA shell. `llms.txt` is not required. A published-site check confirms a Markdown rendering for AI crawlers. The URL of that Markdown is not public.

Index controls. Only a publicly published app can be indexed. Private, unpublished, and branded workspace URLs are never indexable. The review treats a sitewide `noindex` meta, a homepage that will not load, `robots.txt` blocking crawlers on a live site, or an `X-Robots-Tag: noindex` header on a server-rendered deploy as high impact. `robots.txt` findings include a missing file, blocked crawlers, a missing `Sitemap:` line, or invalid rules. Sitemap findings include a missing file, invalid XML, placeholder routes, relative URLs, a host mismatch, or routes out of sync with the file. Google Search Console connection, verification, and sitemap submit are checked only on a live public site, and only if that connector is enabled for the workspace.

Metadata. Lovable generates a title, a meta description, and a favicon per page from the page content. Open Graph is per route. If the person has not set an image, a public site can use the latest screenshot. Sites that are not public do not get that automatic image. The review flags duplicate titles, placeholder text, weak descriptions, canonicals that point at the homepage, missing or generic Open Graph, and Lovable branding left on share cards. The docs suggest share images at 1200 by 630 and a few hundred KB. That is guidance, not a measured checker.

Structured data. The review flags JSON-LD that does not parse, does not match the visible page, or is incomplete for a Google Search feature the page already qualifies for. Missing generic `WebSite` or `Organization` markup is not a finding. A missing `FAQPage` is not a finding. The full list of schema types it will suggest is not public.

Headings, links, speed. Content structure flags a missing or generic H1, a skip from H1 to H3, images without alt text, and link text that does not describe the destination. Internal-link insertion as its own feature is not public. The review does not score page speed, accessibility, or mobile usability anymore. The hosting page says the site is served from locations near the visitor. A Core Web Vitals number for Lovable hosting is not public.

## Dynamic behavior

The default first prompt says no login and no database yet. Backend is optional and is real client and server JavaScript, not a static page.

Runtime. The browser runs the TypeScript React app. New apps also run server code (SSR, server functions, API routes) on the host. Older apps are a Vite client bundle plus, when used, Supabase Edge Functions. Cloud is on by default for the workspace and turns on for a project when a feature needs it, or asks first, depending on the Enable Cloud permission. Always allow is the default for that switch. Cloud is Supabase's open-source stack under Lovable's account: PostgreSQL, auth, storage, realtime, and Edge Functions. The pause-Cloud page says apps built before May 2026 depend on Edge Functions more than newer apps. Edge Function source, when present, is `supabase/functions/`. Schema changes are SQL migrations. The external-hosting page names `supabase/migrations/` and, for some projects, `drizzle/migrations/`. Which of those a new TanStack app writes is not public as a single rule.

Accounts. Email and password, phone with the person's own SMS provider, Google, Apple, Microsoft, and SAML SSO. Row-level security is part of the documented security model. A complete generated auth-file list is not public.

Forms and CMS. A form is React the agent writes. The quick start's menu filter is client state. Submissions go to Cloud or Supabase only after the person asks for storage. There is no built-in page CMS. Contentful, Storyblok, WordPress, Notion, and Airtable are connectors, not the default store. Tables the agent creates in Cloud are the documented content store.

Other client behavior. npm packages (charts, drag-and-drop, animation) install into the project. Built-in AI (chat, summary, image) can be added inside the published app and spends run credits. Payments are Paddle or Stripe on a paid plan, or the person's own Stripe account. Preview and the live site share one database, so a row written in preview is live data.

## Already in SpiderCaster

The engine already does the parts that stay static. `compose` plans from real `copy/` files, reorders only sections that copy already produced, paints one mold, and inserts one catalog part per section plus a header and a footer. It writes `structure.json`, `site.json`, and `report.json`. It does not invent the sample sentences Lovable's quick start requests.

Render already emits `lang`, a viewport tag, a title, a meta description, `noindex` until a human runs `library bind --live`, Open Graph title, description, and type, `og:image` only when the hero image is already a local file, a relative canonical, `favicon.svg`, WebSite JSON-LD with no `aggregateRating`, FAQPage only when the FAQ text is visible, a skip link, a sticky header, and a mobile drawer. `check` already fails body text under 18px, chrome under 16px, contrast under 4.5:1 (large text 3:1), tap targets under 44px, SAMPLE or lorem or placeholder, hotlinked images, a bad canonical, a missing or extra h1 on the index, a missing alt, a missing sticky header or mobile drawer, and sideways overflow at 360, 390, and 412. `visit` measures at 390 and 1280 when Playwright is installed. The SEO seat's hands are `uniqueness` and `meta_basics`. `seat_gate` refuses a hand that is not on that seat. Publish stays a second human click. There is no chat control that deploys.

SpiderCaster does not have Lovable's React tree, TanStack server, Supabase, design-system file copy, knowledge field that can order sample copy, image generation, or browser-testing agent. It should not grow those.

## Worth building

Only static HTML, the stdlib, and copy the human already wrote. No React, Tailwind, shadcn, remote component fetch, generated reviews, or a chat button that publishes.

1. Per-page description from that page's copy. Render already varies the title by page, then repeats one site description on every page. Lovable's review treats a repeated or placeholder description as a finding. If a page's copy file already has a description line, emit that line. If it does not, keep the site line or leave the description empty and fail the check. Do not write a new sentence.

2. A heading-skip row in `check`. Lovable flags an H1 that jumps to an H3. The checker already requires one h1 on the index and measures heading type size. It does not name a skipped level. A static walk of `h1` through `h6` on each built page is enough.

3. Sitemap and `robots.txt` only after the live bind, and only if that bind already has a host. Lovable will not accept a sitemap of relative URLs. SpiderCaster's canonicals stay relative, and pages stay `noindex` until the human publishes. Writing an indexable sitemap earlier would fight that. Do not invent a hostname.

Do not build the three design-direction previews. They are placeholder copy. Do not build a knowledge field that says "use realistic sample content." Do not copy `.lovable` schema files or 21st.dev prompts into the catalog. The mobile check Lovable leaves to a person with a device toggle is already a stop here: overflow, tap size, drawer, and sticky header.

## Sources

Opened 2026-10-08.

- https://docs.lovable.dev/llms.txt
- https://docs.lovable.dev/introduction/getting-started
- https://docs.lovable.dev/introduction/dashboard-overview
- https://docs.lovable.dev/introduction/faq
- https://docs.lovable.dev/features/agent-mode
- https://docs.lovable.dev/features/plan-mode
- https://docs.lovable.dev/features/knowledge
- https://docs.lovable.dev/features/skills
- https://docs.lovable.dev/features/subagents
- https://docs.lovable.dev/features/design-guidance
- https://docs.lovable.dev/features/design-systems
- https://docs.lovable.dev/features/projects/preview
- https://docs.lovable.dev/features/browser-testing
- https://docs.lovable.dev/features/publish
- https://docs.lovable.dev/features/hosting
- https://docs.lovable.dev/features/cloud
- https://docs.lovable.dev/features/seo-aeo
- https://docs.lovable.dev/integrations/lovable-mobile-app
- https://docs.lovable.dev/tips-tricks/npm-packages
- https://docs.lovable.dev/tips-tricks/custom-fonts
- https://docs.lovable.dev/tips-tricks/21stdev
- https://docs.lovable.dev/prompting/prompting-one
- https://lovable.dev/blog/building-apps-using-tanstack-start
