Webflow

## 1. Product

Webflow's AI site builder makes a new multi-page marketing site. It does not retrofit a site that was not built with it. First input is Dashboard, New site, AI Site Builder, a description (colors, fonts, purpose, what you do, the goal, and optional pages and audience), then Generate. That first Generate is a structure of pages and sections, not finished pages. Named colors, hex codes, fonts, or a brand to feel inspired by are mapped onto Webflow's theme system rather than copied exactly. Edit prompt regenerates the structure and drops page and section edits.

The human approves the plan before the pages exist. On the structure they can add a page by describing it (up to five at this stage; the homepage cannot be deleted), and per page they can drag sections, delete, duplicate, Change section, or add a type. Navigation and footer sections cannot be reordered. Generate site then builds the page designs and "contextually relevant content." On the canvas preview the human can add, replace, move, swap styles, or delete a section, and pick or fine-tune a theme. A theme change updates the generated site: colors, animations, typography, sections, images, buttons, forms, cards, spacing, and roundness. Fine-tuning colors, typography, or animations also applies across generated pages. Continue building is clicked twice to open the Designer. The builder page says to preview before you publish. The publish click path is not on that article.

Without a paid Workspace or Site plan the site is limited to two static pages, and the same article excludes the automatic Style guide from that count. With a paid plan the builder starts at up to five pages, and more can be generated later from the Pages panel with Generate page with AI. The builder does not consume Webflow AI credits. Generating and editing copy with Webflow AI does require a paid Workspace or Site plan. A ban on invented reviews is not public on the builder page. How an image pack is produced is not public. Changing the theme image pack does not replace images already on the site. It applies only to newly generated pages and sections. A hero step and a favicon step are not public on the builder page.

AI-generated sites open in the Marketer role: move sections, edit copy, swap images, tweak the theme. Full Designer permissions are a role switch, not the default. There is no named visual critic. Workspace settings, General, can turn Webflow AI off. The builder cannot be run on a non-AI site. Sites created with it before 8 October 2025 cannot be transferred between Workspaces. Sites created on or after that date can. Libraries cannot be shared from an AI-built site. Re-theming after generation does not restyle sections already converted to components.

The same product family, separate from the site builder, is the Designer AI Assistant, AI code components, and the remote MCP server. Those are covered below. They are not the first-run site plan.

The 2026-10-01 note of this flow still matches the live builder article. The live article adds the credit exception, the two-page and five-page caps, the Style guide exclusion, the transfer date, the library ban, and the re-theme skip. The copy article linked from the live builder is not the URL in that note. The lorem-ipsum wording from the note was not on the builder page opened today.

## 2. Code libraries

Flowkit is Webflow's CSS framework for sites its AI tools generate. It is not a public npm package and not a public stylesheet repo. The class list lives in the generated Webflow project and is described in the developer docs. Current docs are Flowkit v2 (header says v2 default). The docs index blurb still calls the intro "legacy." The page body is the v2 naming system. v1 (15 May 2025) and v2 (25 July 2025) both exist. v1 class names are not the current ones.

A generated site includes a Style guide static page (Pages panel, Static pages, Style guide) of colors, typography, cards, sliders, spacing, gradients, and effects. Token edits are the Variables panel or the canvas, not a separate token file you download.

v2 class types are Component, Utility, Combo, and Responsive modifiers. Hyphens join words and modifier prefixes. Underscores join a component to a part, or a utility property to a value, or a utility to a breakpoint postfix. Combo prefixes are `is-`, `on-`, `gap-`, `ix-`, and the responsive prefixes `tablet-`, `mobile-l-`, `mobile-`. A utility postfix `_mobile` applies only at that breakpoint. A combo prefix `mobile-` overrides a base class at that breakpoint. Size words are xxsmall, xsmall, small, medium, large, xlarge, xxlarge.

Documented component identifiers include `section`, `container`, `nav`, `nav_logo`, `nav_links`, `footer`, `footer_link`, `card`, `card_body`, `button`, `banner`, plus the component pages Buttons, Tag, Dropdown, Accordion, Images, Cards, Rich Text, Divider, Forms, Tabs, and Slider. The page-structure tree writes those layout classes in lowercase. The same page later capitalizes Nav and Footer. Treat the tree and the naming table as the identifiers.

A typical page is Body, then `nav`, then one or more `section` elements, each with a `container` div and a layout (grid, flex, or card), then `footer`. Sections are the core blocks and must use the Section tag. Section combos are `is-secondary`, `is-accent-primary`, `is-accent-secondary`, `is-accent-tertiary`, and `is-inverse`. Container combos are `is-full-width`, `is-large`, and `is-small`. The numeric max-widths are not public on that page. Grid classes are `grid_1-col` through `grid_6-col`, `grid_9-col`, and `grid_12-col`, with `gap-*` and `is-x-*` / `is-y-*`. Flex classes are `flex_horizontal` and `flex_vertical`. Interaction hooks use an `ix_` prefix (`ix_section-scroll-in`, `ix_nav-slide-out`, and others). They are class names for the Interactions panel, not CSS animations.

The public GitHub skill `webflow/webflow-skills` `plugins/webflow-skills/skills/flowkit-naming/SKILL.md` (mcp-version 2.0.1) tells an agent to prefix classes `fk-` (`fk-section`, `fk-hero`, `fk-grid-3`). Those names are not in the v2 docs. The skill is agent text, not the framework source. Do not treat `fk-` as Flowkit.

Variables are Webflow's design tokens, stored in collections in the project, not in a file the docs publish. Five types: color, size, percentage, number, font family. Groups are a `group/name` prefix. Aliases reference another variable of the same type. Modes are extra value columns. One mode per collection can be bound to a breakpoint (tablet, mobile landscape, or mobile portrait) so a linked style picks that value without a per-breakpoint override. A mode with no breakpoint is a manual theme applied to a selector. Functions in values are documented. The Variables help page names `calc()` and `clamp()`. The Designer variables reference also lists `min()`, `max()`, and `color-mix()`. Non-base collection CSS names are flagged as about to change. Custom code that hardcodes them is called out as something you may have to update. That mapping is not public here.

Flowkit's own variable categories are Colors, Sizes, and Typography. Core color names include Accent Primary, Secondary, and Tertiary, each with a Hover, plus Neutral Primary, Neutral Secondary, and Neutral Inverse. Tints run A10 through A90 on the accent and neutral groups. Semantic names alias those: backgrounds such as BG Primary and BG Inverse, text such as Text Primary and Text On Accent Primary, borders such as Border Primary. The docs give examples, not a closed list. Spacing variables are rem multiples of a 1rem base, named `0.25x` through `8x`, and the docs say a project may remap them. Gap names are `gap-xsmall` through `gap-xxlarge`. Radius names are Small, Medium, Large, and X Large. Typography variables include Base Font, Base Font Size (1rem), Base Font Weight, Base Letter Spacing, Base Line Height, Base Margin Bottom, Heading Font, Body Font, and Button Font, plus per-heading margin variables. Heading tags and `heading_h1` through `heading_h6` share those variables. Paragraph sizes are the default plus `text is-small`, `is-large`, `is-xlarge`, and `is-xxlarge`. Primary unit is rem, with the root documented as 16px unless custom code changes it. Other units named: em, percent, fr, vh, vw, dvh, px, and cqw.

How a section is stored depends on the stage. The AI builder structure is a closed editor. Its file format is not public. After Generate site, the page is a Webflow element tree in the site, not a repo. A section is a Section-tagged element with the Flowkit classes above. It can be turned into a component. A component definition is the blueprint. An instance is a copy whose props, variants, and slots can differ. The Designer API types an instance as `ComponentInstance` with an id of component plus element. Slots accept component instances only, not loose elements. Unlink turns an instance back into elements, except library and code components. Page branches are an Enterprise isolation copy of a page, not the section format.

AI code components are a second model. The Assistant writes one React file on the component canvas. It reads the site's styles and variables. The file is not a public package. DevLink code components are the external form: a React component plus a `ComponentName.webflow.tsx` definition that default-exports `declareComponent` from `@webflow/react`, with `props` from `@webflow/data-types`. `webflow.json` names the library and a glob of those definition files. The CLI shares that library to the Workspace. Prop types documented: Text, Rich Text, Text Node, Link, Image, Number, Boolean, Variant, Visibility, Slot, and ID. Options include `applyTagSelectors` and SSR. Each code component mounts in its own Shadow DOM and its own React root. Site classes do not cross that boundary. Site variables can, via `var(--name)`. `font-family: inherit` crosses it. Tag selectors apply only if that option is on.

Registry versions opened 2026-10-08: `@webflow/react` 2.6.0 (MIT, peer `react` and `react-dom` `>=18 <20`, depends on `@webflow/data-types` and `@webflow/functions` `^2.6.0`), `@webflow/data-types` 2.6.0, `@webflow/webflow-cli` 2.11.0 (Node `>=22.13.0`). The CLI description says it manages sites, CMS, forms, assets, and code components. Docs also name `@webflow/emotion-utils` and `@webflow/styled-components-utils` for Shadow DOM CSS-in-JS. Their versions were not opened. Tailwind is a documented code-component CSS option and a dependency the Assistant may add. It is not Flowkit.

AI code component limits, from the help article: React only. One file. No manual class management inside the component. No CMS connection yet. No DevLink export, and the Assistant will not edit an imported DevLink component. Cannot be created from an existing component. Sites that contain code components cannot be cloned. Copy between sites drops them. Code export strips them. A prompt that makes the Assistant request exceed 256 KB returns 413. The Assistant will not add a database, secret store, or authentication. Secrets in a prompt are unsupported. Create and modify spend AI credits. Visual edits do not. Create requires Site Manager or Designer. Marketer, Content editor, and Reviewer can view. Publish of a site that contains them needs a CMS Site plan or above and a paid Workspace. Code dependencies are npm package names only. Names that start with `@webflow/` are required and updated by Webflow. Removing a package a component still uses puts it back on the next rebuild.

MCP is the agent surface, not a CSS library. Remote server `https://mcp.webflow.com/mcp`. OAuth is one Workspace. A docs-only server is `https://developers.webflow.com/_mcp/server`. Data tools run headless. Designer-session tools need the Designer open and the MCP Bridge App connected. Granting a tool grants every action. Page-building data tools also require `siteId` and `pageId`. Designer actions require `siteId`. The agent cannot change site or Workspace access. Its role is the person's role. Changes land in the site activity log. Agent Instructions (skills and rules, markdown, `SKILL.md` for a skill) live on the site and are handed to connected agents. They can reference variables, styles, components, pages, CMS, locales, and other instructions. Shared Libraries can carry them. The 2026-10-01 note that skills and rules stay off until toggled was not restated on the how-it-works page opened today. That default is not public here.

Data tools named on the tools page include `data_element_tool`, `data_element_builder`, `data_element_settings_tool`, `data_whtml_builder`, `data_style_tool`, `data_variable_tool`, `data_component_tool`, `data_component_props_tool`, `data_component_variants_tool`, `data_component_builder`, `data_interactions_tool`, `data_pages_tool`, `data_sitemap_tool`, `data_cms_tool`, `data_forms_tool`, `data_assets_tool`, `data_fonts_tool`, `data_scripts_tool`, `data_localization_tool`, `data_sites_tool` (including `publish_site`), `data_agent_instructions_tool`, `data_enterprise_tool` (redirects, robots.txt, well-known files, activity log, Enterprise), `data_analyze_tool`, `data_apps_tool` (Webflow Cloud from GitHub, secrets not accepted or returned), `data_comments_tool`, `data_campaigns_tool` (Early Access), and `data_webhook_tool`. Designer tools are still `asset_tool` (`upload_image_by_url` only), `designer_tool`, and `element_snapshot_tool`. Other asset work moved to `data_assets_tool`. The 2026-10-01 note that the asset action list was unpublished is out of date.

Variable tool actions create color, font family, number, percentage, and size variables, plus collections and modes. Style actions create classes and combo classes and can set a variable mode per breakpoint or pseudo. Element actions read the tree, set text, heading level 1 through 6, image asset, link, attributes, and styles. `data_whtml_builder` inserts an HTML and CSS fragment. That is a closed Webflow import, not a format to copy.

## 3. Mobile

The builder article says the result is a responsive website. It does not state a type size, a tap size, a drawer, or a breakpoint width. Hero and favicon behavior on small screens is not public there.

Webflow's breakpoints, help article updated 2 September 2026, start at the desktop base. Styles cascade down to smaller breakpoints and up to larger ones. Ranges: 1920px and above, 1440px and above, 1280px and above, desktop base unless overridden, tablet 991px and below, mobile landscape 767px and below, mobile portrait 479px and below. The three large breakpoints are optional and cannot be removed once added. Older public text said 478px for portrait. The page opened today says 479. Only Style panel changes cascade. Element order, element settings, and content replacements apply at every width. Hiding is `display: none`, and the hidden element stays in the published HTML. Flex or grid children can be reordered per breakpoint. Expand canvas shows the breakpoint frames together. There is no documented requirement to design mobile-first. The help text says to start on desktop and then go down.

Flowkit v2 grids collapse without an extra class. `grid_2-col` is 2, then 2, then 1, then 1 across desktop, tablet, mobile landscape, and mobile. `grid_3-col` is 3, 3, 2, 1. `grid_4-col` is 4, 2, 1, 1. `grid_5-col` and `grid_6-col` are 5 or 6, then 3, then 2, then 1. `grid_9-col` and `grid_12-col` are 9 or 12, then 3, then 2, then 1. A combo such as `tablet-1-col` overrides that. The v2 flex page does not say a horizontal flex becomes a column on tablet. The v1 flex page did, at 991px and below. That automatic stack is not public for v2. v2 flex responsive classes that are public are alignment combos (`tablet-x-center`, `mobile-l-x-center`, `mobile-x-center`, and the y equivalents). The utilities reference says some margin and padding utilities use a smaller spacing variable on smaller screens. Its example is `margin-top_xlarge` at 6x on desktop and 3x on mobile. Variable modes can supply a different token value at tablet, mobile landscape, or mobile portrait, one mode per breakpoint per collection.

`ix_nav-slide-out` is the documented class hook for a mobile nav animation. A required hamburger, focus trap, or 44px target is not public. Interactions with GSAP can be limited by breakpoint and cascade down like styles. GSAP interactions do not support the old navbar, tabs, dropdown, or slider element triggers.

AI code components can be styled per breakpoint on the component canvas. That does not publish a phone layout rule.

## 4. SEO

Documented controls, not ranking results. No page opened here measures a ranking change. The University lesson says search systems reward readable structure. That is a course claim, not a measurement. Mark it not public as a result.

Sitemap. Site settings, SEO, Sitemap, Auto-generate sitemap writes `sitemap.xml` and updates it on publish. Localize sites add hreflang for static and dynamic pages. Turning auto-generate off allows a pasted custom sitemap. Webflow adds the sitemap URL to `robots.txt` unless Remove sitemap.xml from robots.txt is on. A second manual Sitemap line would leave two. MCP `data_sitemap_tool` reads and sets `includeInSitemap` on static pages and CMS items. Folder, collection-template, and utility pages are outside the page actions. Item changes are staged until publish.

Robots and index. Site settings, SEO, Indexing, can turn staging indexing off so the `webflow.io` host is not indexed. The same area holds `robots.txt` rules (User-agent, Allow, Disallow) and a Content-Signal line. The help page says Content-Signal is a proposed extension to RFC 9309 and is not an accepted standard. `robots.txt` is public. A Disallow does not remove a URL from the auto-generated sitemap. The Sitemap indexing toggle on a page, and the same control on a CMS item, adds a robots noindex meta. That is the documented index control. Enterprise MCP can read and replace `robots.txt`.

Canonical. Site settings, SEO, Global canonical tag URL is a base URL, expected to match the default domain, combined with each slug. A static page can override it with a full absolute Page canonical URL. The tags are written into the head. They apply after publish.

Title and description. Per page, Pages panel, Page settings, SEO settings. Title tag and meta description. The help page says they cannot be set globally, and it calls a title under 60 characters best practice. It says search engines truncate long descriptions and does not give a description length. Webflow AI can Generate each field from the page. Collection templates can bind fields. Localize can override title, description, slug, and Open Graph per locale, and can machine-translate those fields except the slug.

Open Graph. Per page only, not global. Three fields: title, description, image. Title and description can be copied from the SEO fields with checkboxes. The image is an asset or a public image URL. If unset, the help page says a share can show random content or none. Collection pages have the same fields. Localize can override them.

JSON-LD. Page settings, Schema markup, including Collection templates. Generate schema markup uses Webflow AI, or the field is pasted. It is live only after publish. The help page says structured data can enable rich snippets such as reviews, events, or menus, and tells you to check a validator. It does not list the types the generator emits. Those types are not public. MCP `data_pages_tool` can read and write page schema markup in bulk. SpiderCaster's refusal of aggregateRating is the opposite of treating review snippets as a feature to copy.

Headings. Flowkit says one `h1` per page, semantic order `h1` then `h2` then `h3` then `p`, and `heading_h1` when the look of an h1 is needed again. The University lesson, opened today, says one h1, h2 for major sections, h3 through h6 for subsections, and do not skip levels. It does not name FAQ as an h3. The 2026-10-01 note that said H3 for FAQs is narrower than the live lesson. MCP can set a heading level from 1 to 6. Nothing opened requires the FAQ text to be visible when FAQ schema is present.

Internal links. A link can target a URL, a page, an element, an email, or a phone. There is no documented internal-link report in the product settings. The MCP overview describes an agent workflow that scans broken links, missing alt text, and weak metadata. The data-tools page has no separate audit tool. A prompt library page exists for a link auditor. That is a prompt, not a checker with published thresholds.

Page speed. Advanced publishing can minify HTML, CSS, and JS separately. The help page says minifying can help the live site load faster. It does not publish a lab score. Asynchronously load JavaScript is off by default and needs a paid Site or Workspace plan. When it is off, scripts load in order before the page. Optimized publishing is a publish-pipeline beta. The "up to 70 percent" figure is Webflow's claim about publish time, not a page-speed measurement. The hosting article opened today does not name the CDN vendor for ordinary Webflow hosting. `cdn.webflow.com` appears as an origin name in a proxy article. Fastly or CloudFront there are examples of an Enterprise customer's own proxy. The default CDN vendor is not public on the pages opened. Image compression to WebP or AVIF is an MCP asset action, rate-limited, not a Lighthouse promise. Code components can SSR for first paint. The docs say that can help perceived performance and SEO. No figure is published.

Index controls recap: staging indexing off, per-page or per-item Sitemap indexing noindex, robots.txt, draft pages, and a Collection template publish toggle that can keep item pages unpublished. Publish is what makes sitemap, canonical, and schema live.

## 5. Dynamic behavior

The published site is Webflow hosting plus whatever client script the project turned on. There is no single public runtime name for a normal AI-built page. CMS, forms, accounts, and commerce are Webflow services, not files in the site repo. Code export drops CMS, and forms on an export need a third-party action URL. Code components are stripped from that export.

CMS. A Collection is a schema plus items. Name and slug are required. Field types listed on the help page: plain text, rich text, image, multi-image, video link, link, email, phone, number, date/time, switch, color, option, file, reference, and multi-reference. Each item can generate a Collection page, and lists can place items on any page. The builder page says a paid plan can generate Collection items with the Assistant. Item publish is separate from a full site publish: Publish now, queue for the next site publish, schedule, unpublish, or archive. Scheduled publish is not on Starter or Basic, and not for an item that was already published. MCP creates items as drafts. Publishing them is a separate action. Localized CMS items cannot be created through MCP. Existing items and static secondary-locale content can be read or updated. `data_localization_tool` writes secondary locales only.

Forms. The native form element posts to Webflow when the site is hosted by Webflow. Submissions are in Site settings, Forms. A custom domain needs a Site plan. The form-submissions article says the staging host can receive submissions without a Site plan. Exported sites do not. Custom action is a method and a URL the customer pastes. Webhooks include a form-submission trigger. MCP can list forms and submissions and can update user-hidden fields only. Flowkit styles those form parts. It does not replace the backend.

Accounts. The APIs intro names a Users API for User Accounts. The AI site builder article does not say it creates logins. Whether a generated site includes accounts is not public.

Commerce. The same APIs intro names an Ecommerce API. The builder prompt examples include product sales as a goal. A generated store is not public on that article.

Client JavaScript. Interactions with GSAP are the default on sites that do not already have Classic interactions. Triggers documented: click, hover, mouse move, page load, scroll, and custom event. Targets can be an element id, a class, an attribute, or the element that started the interaction. Classic interactions are invisible to MCP. The GSAP library itself is a separate toggle under Settings, GSAP integration, and can also be loaded from Webflow's CDN into custom code. Custom code sits in site or page head and footer, or in an embed. MCP registers hosted or inline scripts and applies them separately. Inline registration is limited to 2000 characters. The Browser API index names `wf.ready()` and consent get, allow, and deny. Those method pages were not opened.

Code components are the other runtime. SSR is on unless the definition sets `ssr` to false. The server HTML is hydrated in the browser. React Server Components are not supported. Each component is its own React root, so they do not share context. The architecture page's cross-component options are URL parameters, `localStorage` or `sessionStorage` for non-sensitive data, Nano Stores, and custom events. Data fetch is client-side, public APIs only, no `.env`. Webflow Cloud is a separate full-stack host from a GitHub repo. MCP can deploy that GitHub source and will not accept secret values. App Gen under Site settings is the in-product prompt for those apps. Its tool schema is not public.

`publish_site` on the MCP data tools publishes to the site's domains. The AI builder's Preview button does not. Campaigns can generate a landing page from markdown and cannot, through MCP, launch ads. That is Early Access.

## 6. Already in SpiderCaster

SpiderCaster does not generate a site from a prompt, and it does not write the page copy. `compose` reads real `copy/` files, may reorder only section types those files already produced, paints one mold, and inserts one catalog part per section plus a header and a footer. The human's approval is the copy and the later `library bind --live`, not a generated sitemap. `structure.json` records frame, mold, and the picked parts. Header, mobile sheet, and `favicon.svg` are renderer-owned, which is the same lock Webflow puts on navigation and footer, without a section catalog the model can restyle.

Tokens are the mold palette and type lead. `paint_css` swaps one hex and a local font stack, and it refuses a palette that fails contrast for white and for `#1a1a1a`. There is no variable collection, no modes, no tint scale, and no post-generation theme swap. Body text floor is 18px, above Flowkit's 1rem base. Chrome floor is 16px. Contrast floor is 4.5:1, large text 3:1. Tap floor is 44px. The checker rejects SAMPLE, lorem, and placeholder text, hotlinked images, a non-relative canonical, a missing or extra h1, aggregateRating, FAQPage questions that are not visible, a missing skip link, missing scroll-margin, a missing sticky header, a missing mobile drawer, and sideways overflow at 360, 390, and 412. `visit` measures at 390 and 1280 when Playwright is installed. Those widths are not Webflow's 479, 767, and 991.

`render` writes a relative canonical, a meta description from site meta, robots noindex until the live bind, Open Graph title, description, and type `website`, and `og:image` only when the hero already has a local relative image. It writes WebSite JSON-LD and FAQPage only from visible FAQ copy. It writes `favicon.svg`. It does not write `sitemap.xml` or `robots.txt`. The SEO seat's hands are `uniqueness` and `meta_basics`. There is no CMS, no accounts, no form post, no GSAP, no React root, and no remote image upload. Parts are static HTML fragments filled only with substrings of `copy/`.

## 7. Worth building

Only static HTML, the standard library, copy that already exists, and noindex until a human publishes. Reimplement. Do not import Flowkit, `@webflow/react`, Tailwind, or GSAP. Do not add a theme swap after paint, an image pack, generated sentences, a review schema, a form backend, a CMS, or a chat control that publishes.

A sitemap and a robots file, written only when `library bind --live` turns noindex off, listing the real HTML pages and pointing `robots.txt` at that sitemap. Until then, write neither. Webflow's own split is the useful part: a noindex page is not an invitation to crawl, and a Disallow is the wrong tool for a page you still list. Do not add Content-Signal.

Per-page title and description only when that page's copy already contains them. Open Graph already mirrors the title, the description, and a local hero image. Do not add Webflow's public image URL for `og:image`.

One inverse surface in the painter: a second background derived from the mold palette, applied to a section the copy already has, refused when contrast fails. Not a mode collection, not A10–A90 tints, not a second theme the human picks after the page exists.

Not worth a new breakpoint system. The overflow checks at 360, 390, and 412 already cover the phone. Flowkit's seven widths and its `display: none` hiding would keep hidden nodes in the HTML. Do not copy that. Do not lower the 18px body floor to Flowkit's 16px root.

Not worth a style-guide page. It would be a page the copy did not ask for. Not worth component instances, slots, or a single-file React island. The section stays HTML in the page.

## 8. Sources

Opened 2026-10-08. One line each. Marketing posts were not used as procedure.

https://help.webflow.com/hc/en-us/articles/38840145286035-Build-a-site-with-Webflow-s-AI-site-builder — AI site builder flow, page caps, Flowkit, Marketer role, theme, image pack, preview.
https://help.webflow.com/hc/en-us/articles/51168990228499-Build-AI-code-components — React code components, roles, npm dependencies, limits, credits.
https://developers.webflow.com/mcp/reference/overview — MCP capabilities and limits.
https://developers.webflow.com/mcp/reference/how-it-works — `https://mcp.webflow.com/mcp`, Bridge App, Agent Instructions.
https://developers.webflow.com/mcp/tools/data-tools — data tool and action names.
https://developers.webflow.com/mcp/tools/designer-tools — Designer session tools.
https://developers.webflow.com/llms.txt — product index.
https://developers.webflow.com/flowkit/llms.txt — Flowkit v1 and v2 indexes.
https://developers.webflow.com/flowkit/getting-started/intro — v2 class types and naming.
https://developers.webflow.com/flowkit/getting-started/units — rem and other units.
https://developers.webflow.com/flowkit/variables/overview — Flowkit variable categories.
https://developers.webflow.com/flowkit/variables/color — color roles and tints.
https://developers.webflow.com/flowkit/variables/typography — type variables and one h1.
https://developers.webflow.com/flowkit/variables/border — border and radius variable names.
https://developers.webflow.com/flowkit/foundation/spacing — spacing scale and gap names.
https://developers.webflow.com/flowkit/structure/page-structure — body, nav, section, container, footer.
https://developers.webflow.com/flowkit/structure/grid — column counts by breakpoint.
https://developers.webflow.com/flowkit/structure/flex — v2 flex classes. No automatic stack on this page.
https://developers.webflow.com/flowkit/components — component page list.
https://developers.webflow.com/flowkit/reference/utilities — smaller spacing utilities on small screens.
https://developers.webflow.com/flowkit/changelog — v1 on 15 May 2025, v2 on 25 July 2025.
https://developers.webflow.com/code-components/llms.txt — code component doc index.
https://developers.webflow.com/code-components/component-architecture — Shadow DOM, SSR, no shared React context.
https://developers.webflow.com/code-components/styling-components — site variables versus site classes.
https://developers.webflow.com/code-components/define-code-component — `declareComponent` and `.webflow.tsx`, seen in search extract of that URL.
https://help.webflow.com/hc/en-us/articles/33961268146323-Variables — five variable types, modes, aliases, groups.
https://help.webflow.com/hc/en-us/articles/33961300305811-Breakpoints-overview — widths, including portrait 479px.
https://university.webflow.com/course-lesson/design-and-build-pages-with-seo-in-mind — one h1, h2, then h3–h6, no skipped levels.
https://help.webflow.com/hc/en-us/articles/33961237278611-Add-SEO-title-and-meta-description — per-page title and description.
https://help.webflow.com/hc/en-us/articles/33961370297107-Control-the-look-of-social-shares-with-Open-Graph — three Open Graph fields.
https://help.webflow.com/hc/en-us/articles/33961263684115-Set-canonical-tags-to-improve-SEO — global and page canonicals.
https://help.webflow.com/hc/en-us/articles/33961355371667-Create-a-sitemap-in-Webflow — auto sitemap and robots line.
https://help.webflow.com/hc/en-us/articles/33961368603539-Disable-search-engine-indexing — staging, noindex toggle, robots.txt does not drop sitemap URLs.
https://help.webflow.com/hc/en-us/articles/41954080897683-Set-robots-txt-rules — robots rules and Content-Signal called a proposal.
https://help.webflow.com/hc/en-us/articles/45766917223955-Add-schema-markup-in-Webflow-to-improve-SEO-and-AEO — schema field and AI generate. Types not listed.
https://help.webflow.com/hc/en-us/articles/33961287288339-Advanced-publishing-options — minify and async scripts.
https://help.webflow.com/hc/en-us/articles/33961244391059-Manage-CMS-Collections — collection fields.
https://help.webflow.com/hc/en-us/articles/33961289539347-Collection-items-overview — items and item publish.
https://help.webflow.com/hc/en-us/articles/33961344521235 — form submissions on Webflow hosting versus export.
https://help.webflow.com/hc/en-us/articles/33961356296723-Intro-to-Webflow-s-APIs — Users API and Ecommerce API named.
https://help.webflow.com/hc/en-us/articles/42832301823635-Intro-to-Interactions-with-GSAP — GSAP interactions as the default without Classic.
https://help.webflow.com/hc/en-us/articles/40538857574419-Use-GSAP-in-Webflow — GSAP library toggle.
https://help.webflow.com/hc/en-us/articles/46223183211155-Webflow-custom-hosting-overview — hosting comparison. Default CDN vendor not named.
https://registry.npmjs.org/@webflow/react/latest — 2.6.0.
https://registry.npmjs.org/@webflow/data-types/latest — 2.6.0.
https://registry.npmjs.org/@webflow/webflow-cli/latest — 2.11.0.
https://github.com/webflow/webflow-skills/blob/main/plugins/webflow-skills/skills/flowkit-naming/SKILL.md — `fk-` skill, disagrees with the v2 docs.

Not used as procedure: Webflow marketing blogs, third-party SEO guides, and the unrelated npm package `flow-kit`.
