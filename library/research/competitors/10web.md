10Web Agentic Website Builder

Research date: 2026-10-08. The 2026-10-01 notes in library/research/HOW_PRO_BUILDERS.md are the head start. Where a live page disagrees, the live page is what this report uses.

## 1. Product

It builds a WordPress website. The first input, on 10web.io or in the dashboard prompt box, is a description, or one of: Clone site from URL, Redesign site from URL, Take a screenshot, Attach a media file, or Import Figma. A system theme can be chosen before submit. The dashboard path also asks for a data center.

A human can approve a plan before the page exists. The help article still shows a structure preview of pages and the sections on each page. From 10web.io the next click is Generate my website, then sign-up or login, then generation. From the dashboard the choices are Start building, Customize structure, or start over. Customize structure opens a structure editor: add a page, add a section, edit the section name, edit the section prompt, Enhance with AI on that prompt, or remove a section, then Save and start building. The final design, content, and layout are created only after that generation starts. Reorder inside that structure editor is not public. The older ecommerce article still says you can rearrange, delete, or modify sections on a schematic outline, then set global fonts, colors, and styles, then Generate.

Changed since the 2026-10-01 notes: a 2026-09-11 release names a Planner Agent. It writes a plan for the onboarding prompt and for later editor requests. The human can rewrite it, approve it, or, in onboarding only, skip it. The release says nothing is built until approve, unless onboarding skips the plan. Whether that plan is the same screen as the structure editor is not public. The plan file format is not public.

After generation the site opens in 10Web AI Editor. The human can preview, chat (typed or voice), edit visually, read a code diff, restore a history point, Save manual edits, then Publish and Publish changes. Publish is global across saved unpublished changes, not one page. Regenerate wipes the WordPress site, chat history, and AI edits and rebuilds from scratch. What the generator must not invent is not public. The ecommerce path says it generates sample products.

## 2. Code libraries

Two stacks are both still documented. They are not the same editor.

Agentic editor. The features page says the generated site is a React front end on a WordPress backend. The React package list, bundler, theme file names, and how a section is stored on disk are not public. Code mode browses website files. Selecting an element and choosing the code icon opens that element at a file and line. The path and language of that file are not public. In the visual editor a section or container has layout, spacing, background, size, border radius, stroke, and shadow. A selected text node can be labeled p, h2, or span, and an image img. The color picker offers theme colors, a Tailwind palette, and custom colors. Whether the shipped CSS is Tailwind utility classes is not public. Do not import Tailwind.

Global theme tokens in the AI Editor theme panel are Colors, Fonts, Radius, and Shadow. Radius steps there are None, Small, Medium, and Large. Shadow steps are None, Small, Medium, Large, Solid, and Custom. A theme change applies to the whole site. A 2026-05-07 release says generation can start from one of 10 predefined system themes and names Bold Heritage, Brutalist, Calm Rose, Fresh Lime, and Modern Slate. The other names are not public on that page. Per-element radius and shadow use a longer scale (Default, None, Extra Small through Extra Large). The pre-generation section record the help article describes is a name plus a prompt. Its stored schema is not public.

Classic 10Web Website Builder, still the ecommerce section-generation path. Help says the editor is drag-and-drop flexbox containers, and that a generated page is container-based sections made of child containers plus Elementor and Builder widgets. The AI Builder article says the tool is based on Elementor Basic. A separate article says 10Web Builder is its own plugin with its own architecture, able to sit beside Elementor Pro. The 10Web Builder plugin source and the 10Web theme source are not public. Elementor Core is public. Its docs store a page as JSON in a private WordPress post-meta field. The public Elementor source uses the meta key `_elementor_data`. An exported template is a JSON object with title, type, version, page_settings, and content. A container element has elType container and nests children in elements. A container setting can set the HTML tag, including section. Document types in those docs include page, post, header, footer, error-404, and popup. That is Elementor's model. 10Web does not publish a second schema.

Public 10Web packages on the WordPress.org plugin directory, GPLv2 or later where the plugin page says so: tenweb-speed-optimizer (10Web Booster), form-maker, photo-gallery, slider-wd. These are not the agentic app. A white-label press page says a license plugin installs the AI Builder, Elementor, and a 10Web theme. That license plugin is not a public registry package.

## 3. Mobile

The AI Editor preview switches between desktop and mobile, plus a full-screen preview. The pixel width of that mobile preview is not public. A 2026-10-02 release rebuilds the editor on a phone: AI chat and the preview share one swipe rail, with a new publish sheet. That is editor chrome, not a generated-site breakpoint.

The features page says generated sites are responsive across devices. An agency-plan article says generated sites are mobile optimized. Breakpoint pixels, a required hamburger, tap size, type size, and contrast for the agentic generator are not public.

The classic builder does publish breakpoints. Global Layout defaults are tablet portrait 1025px and mobile portrait 768px. Layouts use the tablet view between those two, and the mobile view below 768px. The Nav Menu widget can show a hamburger, optionally full width, at a breakpoint of Mobile, Tablet, or None. Those numbers are the classic builder, not a measured agentic page.

## 4. SEO

Documented controls, separate from ranking claims:

- Index. WordPress Settings, Reading, Search engine visibility. Staging sites have discourage-search-engines turned on by default. The indexing article says sites on a temporary `.10web.site` subdomain are not intended to be indexed. Any extra robots rule behind that subdomain statement is not public. A custom domain is required before they tell you to expect Google to index the site.
- Title and description. The 2026-09-11 structure panel, on cloud sites, edits a page SEO title and description, plus slug and parent, without opening WP admin. The same panel covers posts, products, and categories. The general SEO article also tells you to set a title and meta description in whatever SEO plugin you install.
- Sitemap. The help articles tell you to submit a sitemap, usually at sitemap.xml, and say Yoast SEO typically writes that file. A 10Web-native sitemap writer is not public. A community thread says Photo Gallery can add a gallery sitemap when Yoast is active.
- robots.txt as a file 10Web generates: not public. The documented switch is the WordPress Reading checkbox above.
- Canonical: not public.
- Open Graph: not public.
- JSON-LD types generated by 10Web: not public. The features page lists schema markup as an SEO-agent deliverable and does not name a type. That is a claim, not a type list.
- Heading order. The SEO help article says use one H1 for the page title, H2 for sections, and H3 under those. It says WordPress sets the H1. It is advice, not a checker.
- Internal links. The same article says to add them. A generator that inserts them is not public.
- Page speed. 10Web Booster levels are Standard (combine and compress CSS and JS, delay some JS, WebP, lazy-load images, video, and iframes), Balanced (adds critical CSS), Strong (delays all JS until interaction), and Extreme (more critical CSS and JS delay). Hosted sites can add a Pro level that turns on Cloudflare CDN. Full-page cache is off until enabled. The features page and the Booster plugin page claim a 90+ PageSpeed score and better rankings. Not measured here. Those sentences are ranking promises, not a procedure.

They recommend installing Yoast SEO, All in One SEO, or Rank Math. Preinstallation of any of those on an agentic site is not public.

## 5. Dynamic behavior

The runtime is WordPress. The classic-builder article says pages are produced by PHP, a MySQL database, and theme files when a visitor requests them, not as a folder of fixed HTML files. The agentic features page adds a React front end. How that front end is mounted on WordPress is not public.

The AI Editor can switch between Pages and Posts. A Posts section is styled in the visual editor and edited in WP admin. Menus open the WordPress menus screen, and the structure panel can add pages, custom links, and nested items and can set the home page. A form's Manage action opens WordPress Form Data: submissions, notification emails, test emails, export, and hooks. Which form plugin an agentic site installs is not public. form-maker is a separate public plugin, not identified on that screen.

Custom post type sections open a Dynamic Data tab. The ecommerce generation path preinstalls WooCommerce and builds category, shop, and single-product templates plus sample products. A 2026-08-10 release says AI chat can update WooCommerce products, categories, and tags. A 2026-07-28 release says a WordPress shortcode can be inserted from chat or an Add Shortcode control and renders as its own block. A 2026-09-11 release says chat can recommend a plugin and the human can install and activate it or decline it.

Accounts are the 10Web dashboard plus WP admin. Generated-site roles beyond WordPress are not public. Editor-only client behavior includes AI chat, voice input, screenshots, Figma page URLs, and code diffs. None of that is documented as a widget on the published page. GA4 setup is a features-page claim. The agentic setup steps are not public.

## 6. Already in SpiderCaster

Compose already plans from real copy files, applies one frame by reordering sections that copy already produced, paints one mold, and inserts one catalog part per section plus a header and a footer. It writes the HTML, structure.json, site.json, and report.json in the same offline run. It does not stop for a human to approve that plan, and it has no section prompt that asks a model to write new sentences.

The build stays noindex until a human runs library bind --live. Assemble writes a meta description and a robots noindex meta. The checker requires a relative canonical, one h1, a non-empty description, WebSite JSON-LD with no aggregateRating, FAQ text visible when FAQPage is present, alt text, skip link, scroll-margin, sticky header, and a mobile drawer. The SEO seat's hands are uniqueness and meta_basics. Open Graph, a sitemap file, and named JSON-LD types beyond WebSite and the FAQ rule are not checker floors.

Mobile floors already measured in check, without a WordPress breakpoint table: body text 18px, chrome 16px, contrast 4.5:1 (large text 3:1), tap 44px, no sideways overflow at 360, 390, and 412. visit measures at 390 and 1280 when Playwright is installed. Molds already carry a palette, a type lead, a nav, and a template name. They do not carry a radius or shadow token. There is no React, Tailwind, Elementor, or WordPress runtime. Forms, accounts, and WooCommerce are out of the static engine.

## 7. Worth building

Only static HTML, stdlib, and text that already exists in copy/. Noindex until a human publishes. Reimplement. Do not import React, Tailwind, Elementor, or a WordPress plugin.

- A plan gate before HTML. Write the page and section ids compose would already use, from the copy files and the chosen frame, and do not assemble until a human file approves that list. Allow drop and reorder of those existing sections only. Do not add a section prompt, Enhance with AI, or a skip that generates anyway. 10Web's skip and its sample products invent content. SpiderCaster must not.
- Per-page title and description taken from that page's own copy, still the description and single h1 the checker already requires. The 10Web structure panel edits those two fields per page. Do not add a second SEO plugin or a schema type the copy does not already support.
- Two optional mold fields, corner radius and shadow, painted as plain CSS custom properties with the current mold as the default. Not a Tailwind scale, and not a live theme switcher.

Do not build a chat control, a plugin installer, a PageSpeed service, a sitemap promise, or Open Graph, until a later brief asks for a static tag written from real copy.

## 8. Sources

Opened 2026-10-08.

https://help.10web.io/hc/en-us/articles/36515422635922-How-to-Generate-a-Website-with-10Web-s-Agentic-Website-Builder — generation steps, structure editor, Generate my website, Start building, Save and start building.
https://help.10web.io/hc/en-us/articles/23531608839570-Section-Based-Ecommerce-Site-Generation — rearrange-before-generate, flexbox sections, Elementor and Builder widgets, WooCommerce, sample products.
https://help.10web.io/hc/en-us/articles/36411956830738-10Web-AI-Editor — preview, code, visual edit, theme tokens, desktop and mobile preview, Save versus Publish.
https://help.10web.io/hc/en-us/articles/36446295345042-10Web-AI-Editor-How-to-Use-the-Visual-Editor — sections, containers, HTML labels, Tailwind palette in the color picker, Form Data, posts, menus, dynamic data.
https://10web.io/product-release/planner-agent/ — Planner Agent, approve or skip, updated 2026-09-11.
https://10web.io/product-release/website-structure-panel/ — pages, menus, posts, products, per-page SEO title and description, updated 2026-09-11.
https://10web.io/product-release/ — mobile editor swipe rail and publish sheet, 2026-10-02. Index only. Child posts below were opened the same day.
https://10web.io/product-release/section-drag-drop/ — drag a section after generation, including onto another page, 2026-07-28.
https://10web.io/product-release/global-themes/ — ten system themes, five names, 2026-05-07.
https://10web.io/product-release/svg-logos/ — generated SVG logo, 2026-05-07. Favicon steps for the agentic builder remain not public.
https://10web.io/features/ — React front end, WordPress backend, agent list, 90+ PageSpeed claim, schema-markup claim. Claims, not a procedure.
https://help.10web.io/hc/en-us/articles/27132650573586-How-to-Optimize-Your-WordPress-Site-for-SEO — Yoast, Rank Math, All in One SEO, permalinks, H1 H2 H3 advice, alt text, sitemap submit.
https://help.10web.io/hc/en-us/articles/26837210538130-Why-Isn-t-My-Website-Showing-Up-On-Google — Reading checkbox, `.10web.site` not for indexing, sitemap path, custom domain.
https://help.10web.io/hc/en-us/articles/12203981996946-Preventing-Staging-Sites-from-Being-Indexed-by-Google — staging noindex via Search engine visibility, on by default.
https://help.10web.io/hc/en-us/articles/6216454280338-10Web-Booster-Optimization-Levels — Standard, Balanced, Strong, Extreme, Pro CDN.
https://help.10web.io/hc/en-us/articles/18569074513682-Global-Layout — classic breakpoints 1025px and 768px.
https://help.10web.io/hc/en-us/articles/360031136211-Nav-Menu-Widget — classic hamburger breakpoint.
https://help.10web.io/hc/en-us/articles/25664682627474-Can-I-Have-HTML-And-CSS-Code-Of-My-Website — classic stack is WordPress, PHP, MySQL, Elementor-based builder. Predates the agentic code editor.
https://help.10web.io/hc/en-us/articles/22578168072210-AI-Editor-Basics — classic AI Builder based on Elementor Basic.
https://help.10web.io/hc/en-us/articles/13751735928082-Can-I-Use-10Web-Builder-With-Elementor-Pro — 10Web Builder is a separate plugin based on Elementor.
https://developers.elementor.com/docs/data-structure/ — Elementor JSON in post meta. Opened with the container and general-structure pages.
https://github.com/elementor/elementor/blob/main/includes/db.php — public meta key `_elementor_data`.
https://wordpress.org/plugins/tenweb-speed-optimizer/ — public Booster plugin, 10Web, GPLv2 or later.
https://wordpress.org/plugins/form-maker/ — public Form Maker plugin. Not tied to agentic Form Data by the visual-editor article.
https://10web.io/press-kit/press-release-ai-website-builder-wordpress-hosts/ — white-label license plugin installs AI Builder, Elementor, and a 10Web theme. Source of that theme is not public.
