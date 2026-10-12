Wix Harmony and Aria

Notes dated 2026-10-01 said mobile, header, and favicon were not public on the Harmony pages opened then, and that custom code and CMS were unavailable. Live pages opened 2026-10-08 disagree on those three points. The live page wins. Each disagreement is marked in the section it belongs to.

## Product

Wix Harmony is the editor launched in January 2026 for self-creators. It sits beside the classic Wix Editor. Wix Studio stays the editor for custom CSS, layout tools, and Velo. A Harmony site cannot be moved to the classic Editor or to Studio. Existing Editor sites are not migrated. An AI-generated Harmony site cannot be switched onto another template. Harmony and Aria are documented as English-only, on a gradual rollout. The partner overview says a new Harmony site is created from a specific intro link and then shows up in the workspace. The creation article says the path is the site dashboard, then Design Site. One creation door for every account is not public.

Aria is the agent inside the Harmony editor, and also in the dashboard (where it replaces Astro). It is not in the Studio editor. No model name, skill id, or tool schema is public.

First input, two doors in the dashboard, plus a third in ChatGPT:

- Description. Aria drafts a description from the site record. The human may edit it and add business, colors, and style, then clicks Generate Site. Aria then builds pages, layouts, colors, and starter content and images in one pass, with live progress in the editor. A separate plan the human approves before that pass is not public.
- Template. The human picks a recommended template (green Wix Harmony label) and clicks Edit, or View then Edit this site. Pre-designed sections can be added later. Categories named on the sections article include Welcome, About, and Products. A closed catalog of every section type is not public.
- ChatGPT. The human connects the Wix app, tags @wix, and reviews the chat's description of the planned site. Create Site builds it. Another message refines the description first. That is the only documented path where a human approves a plan before the page exists.

After generation, the editor opens a preview and tools to finish the site. The human can keep editing by drag and drop or by asking Aria. The stated gate is review before finalizing. Preview and Publish sit on the top bar. Saving stays in the editor. Publishing is what visitors get. The exact Publish click sequence beyond that top-bar control is not public on the creation article.

Aria's documented jobs: pages, sections, and layouts; brand colors, fonts, and elements; text, images, and media; apps and some settings in chat; questions about features, settings, and SEO. Ask Aria on the action bar is narrower. For text it offers shorter, longer, rewrite, or a tone change. For a section it offers a new layout or a spacing fix. The click is sent to Aria, which applies it. Tagging a selected element means the message does not have to name it. Voice input and file upload are documented. Anything Aria can do, the human can also edit by hand. Aria is desktop-only. It does not edit the mobile view. A dashboard change is not done inside the editor chat. Aria points at the dashboard. A business question may open My Business (Blog create or manage; Bookings services, sessions, client flow, share links).

Aria may be wrong. The creation and Aria articles both say to review suggestions before finalizing. Some AI-generated content might need a label, and labeling may be a legal requirement (the article names the EU AI Act as an example). The rights check is also documented: confirm you may use the generated content. A ban on invented reviews is not public. The image model and a stock-library step on the generation pass are not public. No extra AI credits. Same Premium plans as the other editors.

The 2026-10-01 note that mobile, header, and favicon were not public is outdated. Site Overview documents domain, favicon upload, name, business type, and description. The header article documents background, borders, and scroll behavior. The mobile article is in section 3.

## Code libraries

The Harmony site document is not public. There is no public theme folder, section JSON schema, or Git remote for a Harmony site. Velo's Git layout (wix.config.json, src/pages, src/public, src/backend) is for Editor and Studio sites that have site code. Harmony does not support site code, so that layout is not the Harmony page.

What the help pages do document, as an editor model rather than a file:

- A page is full-width sections, plus a header and a footer. A section can be hidden per page (Hide header / Hide footer). There is no published section-count cap. The layers FAQ says you can add as many as you need.
- A section is added as Generate with AI, a Designed Section, or a Blank Section. It can also be inserted from the edge of an existing section. Reorder is the arrows on the section, or a drag in Layers.
- Each section has a grid. It starts as one cell. The human picks a layout, splits or merges cells, drags grid lines, and sets gaps. Documented minimum row height is 40px. Cells can swap. A cell can have its own background, border, corners, and shadow.
- Elements live in a section, box, or grid cell. Layers can reorder an element inside its section. Moving it to another section is a canvas drag or cut and paste, not a Layers drag.
- A layer name is editor-only. It is not shown to visitors.
- A section has a name and a section link. Renaming the section updates the link. The link is only the ending after the site address, up to 60 characters.
- Optimize DOM order is on by default, so the section's element order matches visual placement. It can be turned off per section.
- Background is a color, image, or video. An image can take alt text, or be marked decorative. Dividers are suggested shapes, Wix media shapes, or an uploaded SVG (the dividers FAQ says SVG only, and no larger than 250KB). Scroll animations on the section background depend on that background type. The animation names are not public on the sections article.

Add Elements categories named on the elements article: Text (branded titles and paragraphs, designed titles, running text, collapsible text), Image, Button (text, icon, or both; social bar; share buttons), Graphics (shapes, vector art, icons, stickers, lines), Box (empty boxes, pre-designed boxes, slideshows), Video (Wix clips and players for TikTok, YouTube, Instagram, and others), Form and Contact (forms, plus Google Maps), Menu (site menu or a custom menu), Gallery, Social, Embed (a link or pasted HTML), and Apps (Wix business apps and third-party apps). List and Repeaters are named on the repeaters article, not in that category table. Still listed as not yet in Harmony, on the editor overview: Accordion, audio player, glass effect, multi-state box, tabs, text mask. The introducing article also lists hover-state customization as not yet in. A public npm package for these built-in elements is not public.

Brand is the theme. It is set once in the Site Brand panel and applied across pages. One element can still be restyled. The public token surface for apps is the Harmony CSS variable set, prefix `--wst-`, documented for published pages only. In the editor, a custom element is sandboxed and may not see the live values. Groups, not a pasted stylesheet:

- Palette, nine colors the owner picks: Base 1 and 2, Shade 1 to 3, Accent 1 to 4. Switching brand kit changes all nine.
- Semantic colors that follow the palette until edited: primary background, secondary background, links and actions, graphics 1 and 2, disabled.
- Fixed system colors: success, error, alert, default dark, default light. The doc publishes the hex values. They are not a measured contrast result.
- Text: Heading 1 through Heading 6, and Paragraph 1 through Paragraph 3. Each has a font variable and a color variable. Fonts come from the font set.
- Buttons: primary, secondary, tertiary. A set swap changes borders, radii, and spacing. Colors keep following palette variables.
- Boxes: Box 1 and Box 2. Lines: Line 1 and Line 2.

Editor and Studio sites expose a smaller, different `--wst-` set (for example `--wst-color-title`). Those names are not the Harmony set. Preferring the Harmony names is an instruction to app authors, not a file SpiderCaster can read.

App code that is public, and is not the site:

- Editor React Components, alpha, Harmony only. A React component plus a declarative manifest. The editor stores data changes as props and style changes as CSS on the manifest's selectors. Types come from the package `@wix/editor-react-types`. The CLI command `wix generate manifest` refreshes the generated manifest. Self-hosting this extension type is not supported. This is how an app widget is described, not how a built-in section is stored.
- Wix CLI site widgets and site plugins, and self-managed extensions, can be installed on Harmony. Dashboard and backend extensions can too. Wix Blocks widgets and plugins cannot. Legacy custom elements cannot. Legacy iframe widgets are partial. There is no migration from an Editor or Studio site to Harmony, and no automatic migration from Blocks to the CLI.
- `wix-style-react`, `wix-ui-tpa`, and `wix-base-ui` are public Wix UI kits (Stylable is named in the design-systems examples repo). They are not the Harmony page document. Do not treat them as a section library.

Custom site code is unavailable: page code, backend code, the custom CSS file, HTTP functions, routers, data hooks, backend events, web modules, scheduled jobs, and Dev Mode. The substitute inside the editor is the AI element generator. The human describes an element, generates it, reviews it, and saves it into that site's AI Elements library (per site, not per account). The generated source is not public. Some design controls exist only in that chat. The generator article says the elements are designed to be accessible and to follow SEO practices. That is a vendor claim, not a measurement.

The 2026-10-01 note that custom code was unavailable is half right. Site code is still unavailable. Dashboard custom code is documented for Harmony. See Dynamic behavior.

## Mobile

Harmony is documented as automatically responsive. The human designs on desktop. Those changes flow to mobile and to other screens. The human can open a mobile view (top-right icon) and change size, color, or placement there without changing desktop. Pixel breakpoints are not public. Studio's 1001 / 751 / 320 breakpoints are a different editor. A measured check at 360, 390, or 412 is not public.

Documented mobile rules:

- Elements added while the mobile view is open are mobile-only. Layers marks them.
- Hide on mobile removes an element or section from the phone view and leaves it on desktop. Show on mobile reverses that.
- Moving an element into a different section, box, or grid cell is disabled on mobile. Reorder inside the current container is allowed and does not change desktop order.
- A horizontal or vertical menu in the header becomes a hamburger on mobile. Header items other than the cart icon and the logo move into that menu. The human can move an item back to the header.
- Text and some elements are resized for mobile automatically. Font size, color, and width can be edited on mobile without changing desktop. The automatic sizes are not public.
- Aria is absent in the mobile view and does not edit it.

The header can scroll as Move with page, Stay fixed, Disappear, or Fade out. Overlap with the next section is a separate toggle. One menu in the header is the documented limit. Another menu can sit in another section or in the footer. A minimum tap size is not public. The 40px section-row minimum is a grid rule, not a tap rule.

## SEO

Documented on the Harmony SEO article, as controls, not as a ranking promise. The article's visibility language is a claim. No ranking number and no page-speed number are public. Core Web Vitals are not public on that page.

The checklist, opened from the site name, then SEO, then Go to SEO Tasks:

- Business setup: site name, where the business serves people (a place, a service area, or online), and a short description of what it sells and who it is for.
- SEO topics: a main topic, then generated site topics the human can edit. Changing the main topic requires Regenerate Site Topics. These topics guide Wix's keyword research. They are not a documented change to the HTML.
- Per page, under SEO and accessibility, then SEO. The human can run Optimize With AI and uncheck suggestions before Approve, or do the tasks by hand. Manual tasks named on the page: focus keyword, title tag, meta description, the toggle Let search engines index this page, page URL, and heading structure (pick a heading tag from the page-headings dropdown).
- Search Console and Bing Webmaster Tools, from the dashboard. The Search Console path adds a verification meta tag. Automatic sitemap submission to Google is described on the general Wix sitemap article as part of the SEO setup checklist, and that article says a Premium plan and a connected domain are required. The Harmony article links that submit step. It does not restate the Premium rule.
- Social share, in the dashboard: image, title, and description, with a preview for how the page looks when shared. Platforms named on the Harmony page: Facebook, Instagram, and X. A Twitter-card property name is not on that page.

Heading tags, on the general heading article the Harmony checklist links: H1 through H6, H1 described as the page title, and an example of H2 for section titles and H3 for subsections. Empty line breaks set to the H1 text theme can emit blank H1 tags. The article does not require a single H1 in a machine check. It says headings help visitors, search, and assistive tech. It also says they can help AI tools quote a section. That last sentence is a claim, not a measured result.

Index control is per page, defaulting to indexable unless the human turns the toggle off. The general default-settings article says the hide state is a robots meta content of noindex, and the show state is index. That article does not say Harmony. The Harmony page itself only names the toggle.

Advanced settings the Harmony FAQ says are in dashboard SEO Settings: structured data markup, and robots meta tags. The robots-meta article lists directives including noindex, nofollow, and nosnippet. It does not say Harmony.

Sitemap. The Harmony FAQ tells the human to submit an updated sitemap and links the general article. That article says every Wix site has a sitemap index, updated when the site changes, viewed by adding sitemap.xml to the domain, and that individual sitemaps are added for features such as Wix Stores. A Harmony-only sitemap difference is not public. Changing a page's default canonical can drop that URL from the sitemap, on the general sitemap article. The Harmony checklist does not name canonical.

Canonical. Not named on the Harmony SEO article. The general default-settings article lists a self-referencing canonical for site pages, and a separate article says Wix creates that default and recommends leaving it. Whether Harmony emits the same tag is not public on the Harmony page.

Open Graph property names. The Harmony page documents a social image, title, and description. The general default-settings article lists og:title, og:site_name, a type of website, the page URL, and image width and height when a social image is set. It does not say Harmony.

JSON-LD. Harmony's FAQ says structured data markup is available. It does not name the types Harmony emits by itself. The general structured-data article, which does not say Harmony, says Wix accepts JSON-LD only, up to five markups per page, each under 7,000 characters, and that markup does not guarantee rich results. Preset markup named there is for Wix Stores product pages, Wix Bookings service pages, Wix Blog posts, and Wix Events pages. A business name and location can produce Local Business markup on the homepage. Site Search can add a sitelinks search box. AI-generated markup is documented for Wix Blog posts only. FAQ markup for blog collapsible lists is optional, with a note that Google limits FAQ and How-To rich results. Custom-code docs list LocalBusiness, FAQPage, and Event as examples a human may paste. Those are not an automatic Harmony feature. Aggregate rating markup is not named as a Harmony default.

Internal links. Menus connect to site pages or to a custom set of links. Section links are in-page fragments. A link checker is not public.

Page speed. Not public as a measurement. A marketing SEO-hub page claims a multi-cloud CDN, automatic SSL, and built-in structured data. That page is not a procedure and those figures were not measured here.

URL changes can 404 old bookmarks. The Harmony article points at the URL Redirect Manager for a 301. Time for a change to appear in search is described as days to weeks. That is not a measurement of this engine.

## Dynamic behavior

Harmony pages are not a static file the human downloads. The rendering engine is named only as the Wix rendering engine. It may re-render during page transitions or viewport changes. Generated class names and element ids are unstable across republish. A public name for the runtime bundle is not public.

CMS. The editor overview FAQ still lists CMS among apps not yet in Harmony. The repeaters article, opened the same day, says Wix is releasing CMS in Harmony and that it is not yet on every account. Where it is on, a repeater connects to a new or existing collection. Text, image, and button elements inside the repeater can bind to fields. Connected elements are marked in the editor. On a static page, only elements inside a repeater can connect to a collection. The item-pages article says item pages replace the dynamic pages used in the other editors. Their URL is a shared prefix plus an item slug. Access can be everyone, a password, or site members (all members, or members with roles, plans, or badges). One SEO setup covers the collection's item pages. This is a hosted collection, not a static list in the HTML.

Forms. The Harmony forms article adds a Wix form from scratch, from an existing form, or from a template in categories such as Subscribe, Request and Registration, and Contact us. Fields can be added, and field design has Normal, Hover, and Error states. The submission URL and the storage schema are not public on that article. The runtime is Wix Forms, not a static HTML form.

Accounts. Site members are an access rule on item pages, as above. A public account schema is not public.

Embeds and custom code. An Embed element can place a link or HTML on the page. Separately, dashboard Settings, then Custom Code, injects HTML, JavaScript, or CSS into the head, the start of the body, or the end of the body, on all pages or on chosen pages, once per visit or on every page. It runs in the browser only, only on a published site with a connected domain, and it is not visible in the editor. It cannot call Wix APIs, `$w`, collections, or backend methods. Tracking pixels for Google Analytics, Google Tag Manager, and Facebook and TikTok are documented as not working through this slot. Marketing integrations are the documented path for those. Secrets in the snippet are visible in the page source. The custom-code article names JSON-LD in the head as one use. It is not the SEO panel.

Apps that the overview still lists as not yet in Harmony, besides the CMS conflict above: Wix Chat, Wix Donations, Wix Hotels, Wix Music and Video, Wix Multilingual, Wix Portfolio, Wix Restaurants Orders (New), Wix Referral Program. Most other App Market apps are said to work. That "most" is not a measured list.

Client JavaScript written as site code does not exist on Harmony. The AI element generator and dashboard custom code are the documented substitutes. Neither is a library SpiderCaster can vendor.

## Already in SpiderCaster

SpiderCaster already refuses the parts of Harmony that do not fit a static, noindex, copy-first build.

- The first input is real files in `copy/`, not a prompt that invents pages. `compose` plans from those files, reorders only sections the copy already produced, paints one mold, and inserts one catalog part per section plus a header and a footer. It writes `structure.json`, `site.json`, and `report.json`. There is no Generate Site pass and no starter text.
- A human publishes. Offline output stays noindex until `library bind --live`. The crew does not publish. Harmony's default is the other way: pages are indexable until a human turns the toggle off.
- One mold holds the theme: a single `#rrggbb` palette, `type_lead`, `nav`, and `template` in `modern`, `editorial`, or `bold`. A live mold is not restyled into a second site. That is the same "one theme" rule as Harmony's brand kit, with a smaller token set.
- The checker already covers a relative canonical, a title, a meta description, a viewport, one h1 on the index, WebSite JSON-LD and no aggregateRating, visible FAQ text when FAQPage is present, skip link, scroll-margin, a sticky header, a mobile drawer, no sideways overflow at 360, 390, and 412, body text 18px, chrome 16px, contrast 4.5:1 (large text 3:1), tap 44px, a non-empty alt on every img, no SAMPLE or lorem, and no hotlinked images. `visit` measures at 390 and 1280 when Playwright is installed.
- `render.py` already emits `og:title`, `og:description`, and `og:type` of website, and `og:image` when a local image is the source. Internal links fail when a fragment or a relative page is missing. A favicon link and `favicon.svg` are required. Those are the static versions of Harmony's social-share fields, section fragments, and Site Overview favicon, without a dashboard.
- The SEO seat's hands are only `uniqueness` and `meta_basics`. `seat_gate` refuses any other hand. There is no Aria chat, no keyword generator, and no copy writer.
- Header and footer are real parts. The mobile drawer is a checker gate, which is the static stand-in for Harmony's hamburger, without a second mobile document.
- DOM order is the section order `compose` writes. A separate optimizer is not required.
- No CMS, no member login, no hosted form, no app market, and no React runtime. `lib/ingest.py` drops `http://` and `https://` asset URLs. Media stays on local files.

## Worth building

Only what stays static HTML, Python standard library, real copy, and noindex until a human publishes. Reimplement. Do not import Wix CSS, `--wst-*` names, Editor React Components, `wix-style-react`, or a Harmony template.

- At `library bind --live` only, write `sitemap.xml` for pages that already exist and a `robots.txt` that names it. Wix keeps a sitemap on every site and indexes unless a page toggle is off. SpiderCaster must not copy that default. The offline build stays noindex and must not advertise those URLs.
- Let the human add three more mold hex fields: background, text, and link. Paint them from the mold the way the single accent is painted now. Harmony's public theme is nine palette colors plus semantic roles. SpiderCaster does not need the nine, and it must not generate a palette. One kit, human-entered, still one mold.
- Add a checker row that fails a skipped heading level, such as an h1 followed later by an h3 with no h2, on headings the copy already produced. Do not retag text and do not add headings. Harmony's control is a manual dropdown. The static version is a check. One h1 is already enforced.

Do not build: an Aria chat, starter copy, an AI element generator, a form that posts anywhere, a CMS or repeater bound to remote data, a per-page index toggle inside the offline build, a 40px tap or row floor (the checker floor is 44px), mobile-only elements that hide the h1 or main, extra JSON-LD types, aggregateRating, a chat button, or a share image the project does not already have.

## Sources

Opened 2026-10-08 unless noted. Marketing pages are not a procedure and are not listed.

- https://support.wix.com/en/article/about-the-new-wix-harmony-editor — January 2026 editor, Aria, auto-responsive, no site code, app and element gaps, Blocks, English-only, templates.
- https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai — Design Site, Generate Site, one-pass starter content, no template switch, review, labeling.
- https://support.wix.com/en/article/wix-harmony-editor-working-with-aria — Ask Aria, jobs, desktop-only, rights check, My Business.
- https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-from-chatgpt — @wix, review the plan, Create Site.
- https://support.wix.com/en/article/introducing-the-wix-harmony-editor — no transfer to Editor or Studio. Hover-state gap.
- https://support.wix.com/en/article/wix-harmony-editor-adding-and-customizing-sections — full-width sections, grid, 40px row, section link of 60 characters.
- https://support.wix.com/en/article/wix-harmony-editor-adding-elements — element categories.
- https://support.wix.com/en/article/wix-harmony-editor-working-with-the-layers-panel — editor-only names, DOM order, hide header or footer, hide on mobile.
- https://support.wix.com/en/article/wix-harmony-editor-adjusting-your-site-for-mobile — desktop-first, mobile-only elements, hamburger, cart and logo.
- https://support.wix.com/en/article/wix-harmony-editor-customizing-your-sites-header — scroll effects, one menu in the header.
- https://dev.wix.com/docs/build-apps/develop-your-app/extensions/site-extensions/harmony-site-theme-css-variables — `--wst-` Harmony theme variables.
- https://dev.wix.com/docs/develop-websites/articles/get-started/about-wix-harmony — no site code. Custom-code snippets are allowed. Feature list that is missing.
- https://dev.wix.com/docs/develop-websites-sdk/code-your-site/build-a-custom-frontend/custom-code/about-custom-code — head and body snippets, browser only, unstable selectors.
- https://dev.wix.com/docs/build-apps/get-started/overview/about-wix-harmony-and-apps — which extension types run on Harmony.
- https://dev.wix.com/docs/build-apps/develop-your-app/extensions/site-extensions/editor-react-components/about-editor-react-components — React plus manifest, `@wix/editor-react-types`, alpha, Harmony only.
- https://support.wix.com/en/article/wix-harmony-editor-optimizing-your-site-with-seo — SEO checklist, index toggle, title, description, headings, social share.
- https://support.wix.com/en/article/understanding-your-sites-sitemap-file — every Wix site, sitemap.xml. Does not say Harmony.
- https://support.wix.com/en/article/understanding-your-pages-default-seo-settings — default title, description, robots, canonical, og tags. Does not say Harmony.
- https://support.wix.com/en/article/adding-structured-data-markup-to-your-sites-pages-2546962 — JSON-LD rules and preset types. Does not say Harmony.
- https://support.wix.com/en/article/managing-your-pages-heading-tags — H1 through H6. Does not say Harmony.
- https://support.wix.com/en/article/wix-harmony-adding-and-setting-up-repeaters — CMS rolling out, not on every account.
- https://support.wix.com/en/article/wix-harmony-editor-whats-new-with-item-pages — item pages, prefix and slug, member access.
- https://support.wix.com/en/article/wix-harmony-editor-adding-and-setting-up-a-form-on-your-site — Wix Forms in the editor. Submission endpoint not public there.
- https://support.wix.com/en/article/wix-harmony-editor-generating-an-element-with-ai — per-site AI Elements library. Source not public.
