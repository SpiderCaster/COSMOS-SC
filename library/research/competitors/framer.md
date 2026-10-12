Framer Agents

## Product

Framer Agents build an editable Framer project: canvas pages, layers, components, interactions, code files, and CMS collections. They do not emit a static HTML repository. The published site is a later hosting step. Two surfaces exist. The in-product agent runs inside the editor. An external agent runs on the person's machine and talks to the project through `@framer/agent` and the Server API.

In-product first input: create a project, open the Agent tab, and type in Ask Framer. The from-scratch article says to name the subject, the sections, and the style, not a bare "build me a landing page." Tone, color, and type go in that same prompt. There is no separate design-system step before copy. The how-to-use article recommends a different rhythm: generate one section, select it so the context tool scopes the next prompt, and attach reference images or real assets. Neither article shows a plan the human must approve before the first layer exists. The agent reads the canvas and places the result on the page. After that, the person can keep prompting, select a layer, or edit text, layout, color, images, and spacing by hand.

Review is before publish, not before generation. The from-scratch article says to check content, images, layout, links, and responsive behavior. No automated critic, score, or publish block is named. Publish is a second action in Framer. Branching on this path is optional: branch menu, Create branch, review Changes, Apply to main, then publish. Work on a branch does not change main. The 2026-10-01 note described that optional path. It still matches this article.

The in-product agent does not get a Node sandbox on the pages opened. Named function calls for that canvas agent are still not public. A help article lists model roles for page design, CMS edits, and code components, and says to compare models on the same brief. Quality, speed, and credit cost per prompt are not measured here. Exact credit counts were not opened, so they are not public here. An Enterprise admin can turn AI off from workspace settings. The finer click path inside that article was not opened.

CMS input is the same Ask Framer field inside the CMS, after an optional Add to Agent on selected rows or cells. The person describes the collection and field types. The agent creates the collection, fields, and items. If the prompt does not supply the facts, the CMS article says the agent writes plausible placeholder text, and that titles, copy, dates, and names should be replaced before publish. The external-agent article's own example asks for a Team collection of five fake users. The from-scratch sample prompt asks for testimonials and does not say they must be real. The 2026-10-01 note said a "must not invent" rule was not public. The live CMS page changes that: invention of placeholders is documented, and a ban on fake testimonials is still not public.

External first input: `npx @framer/agent@latest setup`, then a project URL in a harness that can load Skills and call local tools. Named harnesses: Claude Code, Codex in ChatGPT, Cursor, Gemini CLI, and Windsurf. The first use opens a browser allow prompt and asks for an API key. No Framer MCP server is required. Setup installs skills into `~/.agents/skills` and `~/.claude/skills`. The help-article body now points at a copyable install prompt. The FAQ and the npm readme still name the `npx` command. Package engines say Node `>=22`. The readme prompt tells the agent to require Node 24 or newer. Which version the CLI actually refuses was not measured.

The external help page's recommended order is inspect, propose, review, apply, summarize, then review in Framer before publishing. The shipped `framer` skill says to explain unrequested edits and to ask before destructive actions the user did not request. That is an instruction to the outside agent, not a Framer screen that blocks the first page. The npm readme, which the 2026-10-01 note did not have, says every external-agent change lands on a branch, and that the live site changes only when a person publishes or tells the agent to publish. The help page still says the person controls what is published, and that project names, domains, and code-override assignment are not available. A hard block on `publish` was not measured.

## Code libraries

The project file is closed. A section is not a catalog row and not an HTML partial. On the canvas it is a layer the person can select. The public node model is the Plugin API, which the Server API shares. A page is a `WebPageNode`. The usual container is a `FrameNode`: it can hold children, be a breakpoint (`isBreakpoint`), and use stack or grid layout (`stackDirection`, `stackDistribution`, `stackAlignment`, `gap`, `padding`). Position values named on `FrameNode` are `relative`, `absolute`, `fixed`, and `sticky`. Other public node names: `TextNode`, `SVGNode`, `ComponentNode`, `ComponentInstanceNode`. A CMS collection in the agent skill is a `CollectionNode` whose fields are `variables`. An item is a `CollectionItemNode` whose cells are `$control__` attributes. There is no public closed section catalog.

Shared chrome is a layout template, not a copied header on every page. Anything outside the content slot is shared. Pages that use a template must be a vertical stack. Creating a template from Home applies it to compatible pages. Each page can pick its own template. Per-page template variables exist. Their schema was not opened, so it is not public here.

Design tokens on the canvas are assets, not a CSS file the agent writes first. `ColorStyle` and `TextStyle` live in the Assets panel. A text style has font, size, color, and up to four width breakpoints, and it is assigned a semantic tag (`h1`–`h6`, `p`, or `span`) that the Accessibility panel can override per instance. Link styles are a separate asset. An external prompt may compare styles with a local file such as `tokens/colors.json`. That path is an example, not a published Framer token schema.

Code components are React 18 components in a Framer code file: Assets, Code, Create Code File, one default export. They render on the canvas, in preview, and on the published site. Property controls come from `addPropertyControls` and `ControlType` in the `framer` package. Control names in the published code-component skill: Boolean, Number, String, Enum, Color, ResponsiveImage, File, Array, Slot, EventHandler, Font, Transition, BoxShadow, Link, Date, Object, Border, Cursor, Padding, BorderRadius, Gap, TrackingId. Image, ComponentInstance, SegmentedEnum, and FusedNumber are marked deprecated there. Layout annotations are `@framerSupportedLayoutWidth` and `@framerSupportedLayoutHeight` (`fixed`, `auto`, `any-prefer-fixed`). `useIsStaticRenderer` and `RenderTarget` (`canvas`, `export`, `thumbnail`, `preview`) are public. The skill says a code file may import only `react`, `react-dom`, `framer`, and `framer-motion`, and that `motion` comes from `framer-motion`, not `framer`. The components introduction says React 18 and does not itself list that import allow-list. Canvas animations on the hosted site are described as WAAPI, powered by Motion. Code overrides are higher-order components. The external agent still cannot assign an override to a node.

Plugin and Server API packages: `framer-plugin` is the in-editor API. `framer-api` is the server package (`connect` from `framer-api`). Server-only methods named on the reference: `disconnect`, `getChangedPaths`, `getChangeContributors`, `publish`, `deploy`. The rest points at the Plugin API. Public groups there include branches, canvas nodes, CMS (`Collection` and plugin-managed `ManagedCollection`), code files (`createCodeFile`, `getCodeFile`, `typecheckCode`), localization, redirects, and publishing (`getPublishInfo`, `getDeployment`, `listDeployments`). An API key is created under Site Settings, General, and is bound to one project. Plugins may call only what that user may call (`isAllowedTo`). The public examples repo `framer/server-api-examples` is linked from the quick start and lists `csv-importer`, `json-api`, `notion-automations-sync`, and `publish`. Those examples still declare `framer-api` 0.1.x. `@framer/agent` 0.0.46 depends on `framer-api` `^5.0.0`. Treat the examples as older than the agent package. The agent CLI source repository is not linked from `package.json`. The public code is the npm tarball.

`@framer/agent` 0.0.46 (registry modified 2026-09-27) is the external CLI. Bin file `dist/cli.js`. Dependencies named in that version: `framer-api`, `commander`, `zod`, `@trpc/client`, `@trpc/server`, `is-wsl`. Shipped skills: `skills/framer/SKILL.md` and `skills/framer-code-components/SKILL.md`, plus `skills/framer/projects/__template__/`. `session new` writes a generated project folder (`index.md`, `project-inventory.md`, `prompt/`, `recipes.md`, `metadata.json`) from `framer.agent.getContext()`. Subcommands named in the skill and readme: `setup`, `project list`, `project new`, `project remix`, `session new`, `session list`, `docs`, `exec`, `apply-changes`, `override-min-release-age`. The skill prefers `framer.agent.applyChanges` for layout, styles, tokens, components, and CMS-on-canvas edits, and tells the agent not to use low-level `createNode` or `setAttributes` for that work. Read methods it names: `getNode`, `getNodes`, `getNodesOfTypes`, `getDescendantsOfTypes`, `serialize`, `serializeNodes`, `paginate`, `readComponentControls`, `readLayoutTemplateControls`. Publish goes through `framer.agent.publish`. Image search in the recipe file is `framer.agent.queryImages` with `source: "unsplash"`. The recipe file also says a page path cannot be changed. `dist/start-relay-server.js` is in the tarball. Its contract was not read, so it is not public here. Whether the in-product canvas agent calls these same methods is not public.

CMS field types on the plugin CMS guide: `boolean`, `color`, `number`, `string`, `formattedText`, `image`, `file`, `link`, `date`, `enum`, `collectionReference`, `multiCollectionReference`, `array` (a gallery of one image field), and an `unsupported` type when Framer has a field the plugin API does not expose. The canvas agent is told to pick those kinds of fields from the prompt (date, option, image, rich text). Connecting items to collection lists and detail pages is supported. The CMS article says filtering, pagination, references, and conditional sections on a custom layout may still need a manual canvas edit.

## Mobile

Breakpoints are separate canvas widths, not one fluid stylesheet. Help names Desktop, Tablet, and Phone or Mobile. Default pixel widths for those breakpoints are not public on the pages opened. Each breakpoint can have its own grid (columns or rows, gap, margins, width) and its own layout. A layout template gets Tablet and Mobile breakpoints added by hand. The documented mobile-nav pattern is to replace the desktop navigation with a compact menu on the small breakpoint. A phone breakpoint that does not fill the screen is blamed on fixed widths or a max width larger than the viewport. The fix named is `100%` or `1fr`, then republish. Horizontal scroll is blamed on fixed widths, large min-width, absolute position, animated offsets, and fit width. Hiding overflow is discouraged because it can break sticky elements. A minimum body size, a minimum tap size, and a required drawer component are not public.

Preview is a look, not a score. Play, or Command-P on macOS, or Ctrl-P on Windows. Resize the viewport, or preview the breakpoint that is selected, such as Tablet. Custom code from Settings is absent in preview and appears only on the published site. The from-scratch article puts responsive behavior on the human pre-publish list. No pass/fail number is published. Published sites support iOS Safari 15.6 and later. Text styles can carry up to four width breakpoints, but those breakpoints do not apply inside a component, because a component cannot read the page breakpoint. The code-component skill's sample paragraph is 15px and its sample button is 14px. Those are skill defaults, not a documented site-wide floor, and they were not measured against a live Framer site.

## SEO

Documented features, separate from ranking claims. The SEO guide says sites are optimized out of the box. That is the product's wording. No ranking result was measured.

Sitemap: every published site gets `/sitemap.xml` with no manual setup. The access article says the file lists pages, last update, change frequency, and structure. A live sitemap was not fetched, so those fields were not verified on a production file.

Robots: `robots.txt` is generated at publish. The AI-readable article says crawlers are allowed by default, including Googlebot, Bingbot, GPTBot, and PerplexityBot, and that a page can be marked `noindex` or an agent can be restricted in site settings. The exact per-agent control labels were not opened. Turning Search engines off on a page writes `<meta name="robots" content="noindex">`. That does not add a `Disallow` line. The indexing article says the default is to show the page in search engines. Password-protected pages return 401 and are an expected indexing exclusion. Staging preview links on `.framer.app` are separate from the production domain.

Canonical: with a domain connected in Framer, canonical tags are generated for that domain. A site-wide Canonical URL field sits at the bottom of Settings, Domains, for a proxy or a site mounted under a path. Per-page canonical overrides are not public on that article. The tags described are absolute URLs.

Title and description: Site Settings hold a site title and a site description. Page Settings can override Title and Page Description. CMS pages can insert fields with `{{Title}}` and `{{Description}}`. Google may still replace the description. That limit is stated, not measured.

Open Graph and Twitter cards: the AI-readable article says published HTML includes them, along with `title`, meta description, and canonical. Social preview images are set in page settings. A CMS cover uses an image field chosen as the social preview. The stated social image ratio is 1200 by 630. Site name in Google can be suggested with a WebSite JSON-LD block or an `og:site_name` meta tag added by hand. Neither is described as automatic.

JSON-LD: not generated from a fixed type list. The person adds it in Custom Code, in the head, as `application/ld+json`. CMS detail pages can fill it with `{{Field | json}}`. The documented example type is `BlogPosting`. A whole JSON-LD blob can be stored in a CMS text field and printed with `unsafeRaw`. A ban on `aggregateRating` is not public. WebSite is a recommended manual type for the site name, not a default script.

Headings: text styles receive semantic tags, and the person can override the tag without the article saying the visual size must change. The recommendation is one `h1`, then `h2` and `h3`. It is not described as a checker that fails a skipped level. Alt text is entered on the canvas image fill, on a CMS image, or on an image inside formatted text. The article says to use a concise sentence and not to stuff keywords. It does not say empty alt fails publish.

Internal links: an automatic internal-link builder is not public. Redirects are a settings feature, and external agents are documented as a way to add them. Page paths cannot be changed by the external skill's own limitation list.

Page speed features that are documented, not scored here: server-rendered React at publish, including responsive versions; image Auto variants so the browser picks a size; fixed image steps of 512, 1024, and 2048 when Auto is not used; lazy-loaded images and video-with-poster; gzip and Brotli; HTTP/2 and HTTP/3. A Lighthouse guide exists. Its scores were not opened, so they are not public here. Video files are not re-encoded. A poster of at least 60 by 30 is the video SEO requirement named. Favicon is a manual upload in Site Settings, General, light and dark, with 64 by 64 PNG recommended. The agent articles do not say the agent creates one.

Index default is on. `noindex` is opt-out per page. CMS items can be left as drafts. The external article names that. Markdown of each published page is also served on the same URL for AI crawlers. `llms.txt` is a file the person adds, not an automatic agent output. None of that is a ranking promise.

## Dynamic behavior

The published runtime is React, pre-rendered to HTML on Framer's servers so a client that does not run JavaScript still receives the text. Canvas motion is WAAPI via Motion. Code components and overrides are client React after that. Settings custom code is a script or style snippet and is not in preview.

CMS is the structured store: collections, fields, items, collection lists, and detail pages that are templates. Unlinked layers on a detail page repeat on every item. On-page editing lets a person with project access change text, images, component props, and CMS fields, including fields that are not visible, and can add a CMS page. That is an editor session, not a public visitor account.

Forms: a native Form layer. The field-type article names Text, Checkbox, Radio, Select, and Submit. A second article says native forms have over ten input types. The rest of that list was not on the page opened. Submissions go to email, Google Sheets, or an HTTPS webhook. The webhook is an HTTP POST of JSON, with `Framer-Signature` and `Framer-Webhook-Submission-Id`, retried up to five times, and it must return 2xx directly. Spam protection and rate limiting are named. The signature algorithm details beyond SHA-256 of the body and submission id were not copied here.

Fetch is a no-code client binding to a JSON endpoint for data that should stay dynamic (the Fetch introduction uses location, login state, and live stock as examples). It says static copy and CMS are the better path for SEO. Returned JSON must be an object. Arrays can be indexed in the Fetch UI and cannot be looped there. A built-in visitor account system is not public on the pages opened. Password protection is public and surfaces as HTTP 401. Localization (locales, groups, sources) is public and is a stated external-agent job. Redirects are public. Analytics access conflicts: the external-agent help page still says agents cannot read analytics, and the 0.0.46 skill lists traffic, visitors, page views, conversions, and events. Which statement holds was not measured.

## Already in SpiderCaster

SpiderCaster already refuses the part Framer leaves open. `compose` builds from real `copy/` files, writes `structure.json`, and stays `noindex` until a human runs `library bind --live`. The crew does not publish. Framer's in-product agent writes the page before review, and its CMS agent will invent placeholder text. The external npm FAQ allows a person to tell the agent to publish. SpiderCaster has no such action.

Shared chrome matches in role only. Framer uses a layout template and a content slot. `compose` inserts one header and one footer around sections the copy already produced, and a package frame may only reorder those sections. Both keep the page body distinct from the chrome. SpiderCaster does not import Framer templates.

Checks already cover the from-scratch review list where it can be static: one `h1`, non-empty `alt`, relative canonical, WebSite JSON-LD with no `aggregateRating`, FAQ text visible when FAQPage is present, skip link, sticky header, mobile drawer, no sideways overflow at 360, 390, and 412, contrast 4.5:1, tap 44px, body text 18px, chrome 16px, no SAMPLE, lorem, or placeholder, no hotlinked images, and `internal_links` against pages the build emitted. `visit` measures at 390 and 1280 when Playwright is installed. Framer's preview is manual and unscored. `og:image` is emitted only when the hero already has a local image. Favicon is `favicon.svg`, not a generated 64 by 64 PNG.

The floors are stricter than the code-component skill's 15px paragraph and 14px button samples. Those samples are not a target. There is no React, `framer-motion`, CMS, webhook form, or Server API in the engine. SEO seat hands remain `uniqueness` and `meta_basics`.

## Worth building

One checker, still static HTML and the standard library. Fail a heading level that skips, so an `h1` is followed by `h2` and an `h3` does not appear before an `h2` on that page. Framer's text-style article recommends that order and lets the tag differ from the visual size. `check.py` already requires one `h1`. A skipped-level fail was not found there. Do not copy Framer's type sizes or its text-style objects.

Do not build the rest. No placeholder testimonials, no Unsplash search, no `framer.agent.publish`, no React code components, no Motion runtime, no CMS, no webhook form, no per-breakpoint copy of the page, and no analytics client. Framer's publishing actions stay outside the engine.

## Sources

Opened 2026-10-08. One line each. Help articles below show an on-page Updated date of 2026-09-15 unless noted.

https://www.framer.com/help/articles/how-to-build-a-website-from-scratch-with-framer-agents/ — first prompt, canvas edits, optional branch, pre-publish review.

https://www.framer.com/help/articles/how-to-use-agents/ — context tool, one section at a time, attached assets, interactions.

https://www.framer.com/help/articles/use-external-agents-with-framer/ — setup, no MCP, CMS read and write, stated limits.

https://www.framer.com/help/articles/what-you-can-do-with-local-agents/ — external scope, workflow, analytics listed as unavailable.

https://www.framer.com/help/articles/how-to-add-content-to-your-cms-with-framer-agents/ — collections, placeholder copy, CSV import, manual layout review.

https://www.framer.com/help/ai/ — agent article index, including Enterprise AI disable.

https://www.framer.com/help/articles/choosing-a-model-in-the-framer-agent/ — model roles. Page date 2026-10-05. Quality not measured.

https://registry.npmjs.org/@framer/agent/latest — package 0.0.46, readme, engines, dependencies. Registry modified 2026-09-27.

https://cdn.jsdelivr.net/npm/@framer/agent@0.0.46/package.json — bin `dist/cli.js` and dependency list.

https://cdn.jsdelivr.net/npm/@framer/agent@0.0.46/skills/framer/SKILL.md — CLI subcommands and `framer.agent` method names.

https://cdn.jsdelivr.net/npm/@framer/agent@0.0.46/skills/framer/projects/__template__/recipes.md — CMS node shape, Unsplash query, path and override limits.

https://cdn.jsdelivr.net/npm/@framer/agent@0.0.46/skills/framer-code-components/SKILL.md — import limit, property-control names, layout annotations.

https://data.jsdelivr.com/v1/packages/npm/@framer/agent@0.0.46 — tarball file roles, including `dist/start-relay-server.js`.

https://www.framer.com/developers/ — plugins, Fetch, code components, overrides, Server API, external agents.

https://www.framer.com/developers/components-introduction — React 18 code components.

https://www.framer.com/developers/server-api-introduction — Server API purpose, including a note that someone could build their own MCP.

https://www.framer.com/developers/server-api-quick-start — `framer-api` `connect`, API key, `publish`, `deploy`, examples repo link.

https://www.framer.com/developers/server-api-reference — server-only methods.

https://www.framer.com/developers/reference — plugin method groups.

https://www.framer.com/developers/cms — CMS field types.

https://www.framer.com/developers/fetch-introduction — Fetch for dynamic JSON, not for copy that can be static.

https://github.com/framer/server-api-examples — public examples. Listing shows `framer-api` 0.1.x, older than the agent package.

https://www.framer.com/help/articles/using-layout-templates/ — shared slot, vertical stack, Tablet and Mobile breakpoints.

https://www.framer.com/help/articles/text-styles-and-semantic-tags/ — semantic tags and the h1, h2, h3 recommendation.

https://www.framer.com/help/articles/why-aren-t-my-text-style-breakpoints-working-in-components/ — component text styles ignore page breakpoints.

https://www.framer.com/help/articles/why-is-my-site-not-filling-the-screen-on-the-phone-breakpoint/ — relative widths on the phone breakpoint.

https://www.framer.com/help/articles/how-to-fix-horizontal-scrolling-issue-on-mobile/ — overflow causes. Hiding overflow can break sticky.

https://www.framer.com/help/articles/how-to-preview-your-site/ — preview versus publish. Settings custom code is absent in preview.

https://www.framer.com/help/articles/layout-grids/ — per-breakpoint grid settings.

https://www.framer.com/help/articles/guide-to-seo-features-and-tools/ — sitemap, robots, titles, semantic tags, JSON-LD, redirects. Ranking claim not measured.

https://www.framer.com/help/articles/how-can-i-access-the-sitemap-xml-file/ — `/sitemap.xml` on publish.

https://www.framer.com/help/articles/how-do-i-prevent-specific-pages-from-getting-indexed-by-search-engines/ — page `noindex` meta, not `robots.txt` Disallow.

https://www.framer.com/help/articles/setting-up-a-custom-canonical-url-in-framer/ — automatic and custom site canonical.

https://www.framer.com/help/articles/how-to-update-page-titles-descriptions-and-social-images/ — site, page, and CMS meta. Social image 1200 by 630.

https://www.framer.com/help/articles/structured-data-through-json-ld/ — hand-written JSON-LD, `BlogPosting` example.

https://www.framer.com/help/articles/how-to-change-the-site-name-in-framer/ — manual WebSite schema or `og:site_name`.

https://www.framer.com/help/articles/make-site-readable-by-ai-agents/ — pre-rendered HTML, Open Graph, Twitter, canonical, generated robots and sitemap.

https://www.framer.com/help/articles/how-to-add-alt-tags-to-images/ — alt on canvas and CMS images.

https://www.framer.com/help/articles/how-to-add-icons-and-set-up-a-favicon/ — manual favicon, 64 by 64 PNG.

https://www.framer.com/help/articles/troubleshooting-google-indexing/ — default index, `noindex`, password 401. Page date 2026-10-03.

https://www.framer.com/help/articles/guide-to-framer-hosting-infrastructure/ — SSR, image and compression behavior, staging links. Speed numbers not measured. Page date 2026-09-30.

https://www.framer.com/help/articles/image-resolution-options/ — Auto image sizes and fixed 512, 1024, 2048 steps.

https://www.framer.com/help/articles/add-different-field-types-to-native-form/ — Text, Checkbox, Radio, Select, Submit.

https://www.framer.com/help/articles/framer-form-webhook-setup/ — webhook POST, signature header, retry.

https://www.framer.com/help/articles/how-to-add-typeform-to-your-website/ — native forms also send to email or Google Sheets. Full field list beyond the field-type article is not public here.

https://www.framer.com/help/articles/on-page-editing/ — editor session for page and CMS fields, not a visitor account.

https://www.framer.com/developers/reference/plugins-frame-node — `FrameNode` as the common container, including breakpoint and stack.

https://www.framer.com/developers/reference/plugins-text-style — `TextStyle` and a maximum of four breakpoints.
