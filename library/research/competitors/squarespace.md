Squarespace Blueprint AI

## Product

Squarespace Blueprint AI builds a version 7.1 site: pages, starter copy, images, colors, and fonts, then leaves the result in the Squarespace editor. It does not hand the customer a static file. The marketed first input changed after the 2026-10-01 notes.

On 2026-10-08 the product page starts with a free-text description: what the site is for, who it serves, what visitors should do, and how it should feel. Step 2 is a generated multi-page site that already has content, imagery, and styling. Step 3 is editing, including an Add pages checklist in the step-3 image. Step 4 is publish: connect a domain, add selling or scheduling tools, and work on search and AI-search visibility. The FAQ says the builder produces pages, copy, imagery, colors, and fonts, that a trial can explore the site, and that a paid website plan is required to publish. It also says you preview, edit, and publish only when it feels right. That is approval of a site that already exists, not approval of a plan before any page exists.

The help article Choosing the right template, still live the same day, describes a different builder. Blueprint AI Builder asks you to select or enter a site title, a brand personality, a homepage, the sections and pages you need, a color palette and a font pairing, and AI-generated images from a curated library. Blueprint AI Templates is a second path: on the templates page, pick a topic and review three AI templates at the top of the results. Using Squarespace AI adds a third path: in Squarespace GPT, enter business name, business type, brand personality, and the goal. That text is passed to Blueprint, which shows an example. The same article says that any of these methods generates text and images and chooses style settings from the prompts. Neither help page says the human must accept a written section plan before HTML exists. The 2026-10-01 reading that Blueprint is a plan you edit before the full page exists does not match the live product page. The structured field list is still what the template article documents.

Both AI start tools are only available on computers. Creating a site this way means you agree to the Product Specific Terms and you are responsible for what you publish. The help article tells you to review generated text, not to publish text you would not have written, and warns that similar prompts can produce the same text on another site. No visual-critic role is named. Trial sites are private by default and search engines do not index them. Only a paid site can be set Public.

Later editing is not the Blueprint gate. Design Intelligence writes or rewrites text in supported fields, with prompt starters Paragraph, Sales Pitch, and Blurb, after an optional Brand Identity (a business description plus a personality). Clarkson AI chat, rolled out in waves, can change text and images, products, discounts, email, contacts, analytics summaries, and site styles. The product page also says you can describe a missing section, such as a comparison, gallery, pricing display, testimonial, or call to action, and preview it before publishing. Using Squarespace AI does not document that generator. How that generated section is stored is not public.

## Code libraries

Version 7.1, which Blueprint produces, does not ship a public template package. The Developer Platform FAQ says developer mode can create or modify a 7.0 template and can read that template's markup, style sheets, scripts, and design assets. It cannot create or modify a 7.1 site, cannot read CMS content, and cannot change blocks or the editor. The 7.1 section record, palette file, and font token file are not public.

The only public template source is the 7.0 developer model. developers.squarespace.com/template-overview describes folders `assets`, `blocks`, `collections`, `pages`, `scripts`, `styles`, plus root `site.region` and `template.conf`. File roles: `.block` and `.block.conf` for partials, `.list`, `.item`, and `.conf` for collections, `.page` and `.page.conf` for static pages, `site.js` for scripts, `.css` and `.less` for styles. The languages named there are JSON-T and LESS. GitHub `Squarespace/base-template` is a minimal developer-mode starter with the same roles and no tweaks, web fonts, or modules. GitHub `Squarespace/template-engine` is described as a TypeScript implementation of the template language, and `Squarespace/template-compiler` as a Java compiler for it. The local tool named on the developer docs is the npm package `@squarespace/server`. None of that is the Blueprint or 7.1 store. Do not import it.

On 7.1 a page is a vertical stack of sections in the hosted CMS. Documented section kinds:

- Block section. New blank and prebuilt block sections use Fluid Engine. Older block areas can still be the classic editor until upgraded. Upgrade is one way. A classic section taller than the 1000-row grid is split.
- Auto layout. Preset lists, carousels, or slideshows. The auto-layout article names the categories Team, Testimonials, and Calendar, and the layouts Simple list, Banner slideshow, and Carousel. Items are typed in by hand. Collection items use a summary block instead.
- Gallery section. Images with little text. Add paths named in the gallery article are Images and Portfolio. Layout names given there: grid simple, strips, masonry, and slideshow simple, full, reel.
- Collection section. Belongs to a collection page such as blog, events, store, portfolio, or videos. It cannot be deleted. It cannot be saved.

Add Section offers a category of prebuilt layouts, a blank block section, or Saved. The page-sections article does not list every category name. A full public registry of section type ids is not public. Saved sections are a snapshot, up to 250 per site, not linked back to the original. Collection sections cannot be saved. Form and newsletter storage connections are not kept in the snapshot.

Fluid Engine is the 7.1 block editor, not a public CSS library. Blocks sit on a grid, may overlap, and may be pinned. Documented section style fields are Row Count, Gap, Fill Screen, Height, Content Width, and Content Alignment, plus a Background tab (image, video, or art, full-bleed or inset) and a Colors tab. Each section has a 1000-row limit. There is no hard cap on sections or blocks. The docs recommend no more than about 20 sections and no more than 60 blocks on a page, and a page size of 5 MB or less, because of load time. Desktop column count and mobile column count are not public on those articles.

A block is the content unit inside a block section. The blocks article describes drag-and-drop pieces that land with placeholder content. Names in the public extracts include text, image, button, form, newsletter, gallery, summary, menu, map, markdown, embed, code, donation, OpenTable, Flickr, and tag cloud. Spacer is classic-editor only. That extract is not a complete menu. Block type ids are not public. In 7.1 you cannot add blocks to the site-wide header.

Color is site styles, not a published token file. A palette has five colors. Most include black and white for text. You can type hex, RGB, or HSL. A new palette can be Presets, From image, or From color. The 2026-08-20 colors article says From image uses the image's three most prominent colors. The palette generates ten color themes. A theme edit applies to every section that uses that theme. Switching a section's theme resets text colors set in the text toolbar. Theme labels in the colors-guide extract are Lightest 1, Light 1, Dark 1, Darkest 1, Lightest 2, Light 2, Dark 2, Darkest 2, Bright 1, and Bright 2. The 2026-08-20 extract confirms the five-color palette and the ten themes and does not repeat those labels, so the labels are documented and not re-measured on a full August body. Site-style theme packs, examples Professional, Playful, and Innovative, set fonts, colors, and buttons together. The product-page image shows personality words Professional, Sophisticated, Friendly, Playful, Bold, Quirky, and Innovative. A complete personality enum is not public.

Fonts are font packs of Google Fonts, grouped Sans-serif, Serif, and Mixed. A base size scales other text. Style groups named in the fonts and styling articles are Headings, Paragraphs, Buttons, and Miscellaneous. Assign Styles can point site navigation at a custom face. Custom font upload is documented. Adobe Fonts are called out for version 7.0. The CSS editor is limited, in the docs, to fonts, colors, and backgrounds, and the same article says custom CSS can break mobile layout. No 7.1 CSS variable list is public.

## Mobile

The product FAQ says generated sites are responsive for desktop, tablet, and mobile, and that the mobile layout can be adjusted on its own. That is a product claim, not a measured viewport test. Breakpoints, a required body size, a tap size, and a contrast ratio are not public.

Fluid Engine keeps the same blocks on mobile and gives them a separate arrangement. Resizing or moving a block on the computer layout does not change the mobile layout. Pinning is also per layout. Row Count is the only section style the docs say can differ between computer and mobile. The mobile app cannot add or edit blocks inside Fluid Engine sections. It can move a section, add a section, or style a classic-editor section. Site styles for fonts and colors are available in the app on 7.1.

Classic-editor columns stack on small screens. The docs say the second and later columns move under the first, and that an image with text beside it keeps that text under the image. Spacer blocks are hidden on mobile on all 7.1 sites. Summary blocks in Fluid Engine keep the computer arrangement. In the classic editor, wall and grid summaries stack, and a carousel summary shows two items.

The 7.1 header collapses to an expandable menu. Layout, height, and width of the header can differ on mobile. The menu overlay has its own color theme. A second logo image can be set for the mobile header. A logo replaces the site title until the logo is removed. Favicon setup is not part of Blueprint. Sites start with the Squarespace cube. A replacement works best at 100 to 300 px square, must be under 100 KB, is shown at 16 px, and is not a multi-resolution icon file. The favicon article says it usually does not show in mobile browsers.

Blueprint AI Builder and Blueprint AI Templates do not run on mobile devices. That is an authoring limit, not a layout rule.

## SEO

Documented features and ranking language are separate. The built-in SEO article says Squarespace cannot guarantee ranking changes or how a listing looks. Checklist character counts are writing advice, not a measured ranking effect.

Sitemap. A public site serves `/sitemap.xml`. It is generated and updated by the platform. You cannot edit it. It lists page URLs and image metadata. It omits disabled pages, password-protected pages, pages hidden from search in page settings, member-site URLs, code-block content, embed-block content, and uploaded-file URLs. The site-map article dated 2025-12-08 says the homepage priority is 1, other pages 0.75, and blog posts 0.5, and that priority can help engines rank pages inside the site against each other. The site-map article updated 2026-07-07 says those priority levels do not directly influence search-result rankings. The newer article wins on the ranking claim. The numeric priorities were not repeated in that July extract.

Robots and index controls. Settings, Crawlers, Block search engine crawlers is the site-wide control. The hiding article shows the robots rule `Disallow: /` and also says "if turned off," so which toggle state writes that line is not cleanly public. The built-in `/search` URL is disallowed by robots.txt. A separate Crawlers checkbox, Block known artificial intelligence crawlers, updates robots.txt to ask named bots to skip the site. The public list includes AI2Bot, Amazonbot, anthropic-ai, Applebot-Extended, Bytespider, CCBot, ClaudeBot, cohere-ai, FacebookBot, Google-Extended, and GoogleOther. The article says the request does not guarantee they will skip the site. Trial sites are not indexed. Only a paid Public site is open to search engines. Password and Private availability also hide the site from indexing. Per page, Hide page from search results adds a noindex tag and drops the URL from the sitemap. The same noindex typed into code injection leaves the URL on the sitemap. Disabled pages and page passwords are off the sitemap and off the index. Not linked only removes the nav link. Member-site pages lose their SEO fields and leave the sitemap.

Canonical. Secondary custom domains 301 to the primary domain. The built-in `sitename.squarespace.com` host does not redirect to that primary. A canonical metadata tag is documented for blog tag and category static URLs, so the static URL is the one to index. A `rel=canonical` on every layout page is not public.

Title and description. Three titles exist: SEO title, page title, and navigation title. The SEO title is what the docs say appears in the browser tab, search results, and social shares. If it is empty, the page title is used. Homepages have no SEO title field. They use the site title and the SEO site description. The SEO title field has a 100-character limit. The checklist recommends a site title under 60 characters. The keyword article recommends titles of 70 characters or fewer. Those are different recommendations, not one measured rule. Title format variables are `%s` for the site title, `%p` for the page SEO title or page title, and `%i` for an item. The default page format is page title, then site name. The checklist recommends an SEO description of 50 to 300 characters for the site and for each page, and the same for blog posts, products, and events. Descriptions may be rewritten by the search engine. That is stated as a limit on what Squarespace controls, not as a ranking result.

Open Graph. The English social articles do not name `og:` or `twitter:` properties. They document a site-wide social sharing logo and a per-page Alternate Social Sharing Image, plus which title and description fields Facebook, X, LinkedIn, and Pinterest display. Facebook images must be at least 200 by 200 px. Twitter Cards are a separate switch for extra product text. Property names in the page source are not public.

JSON-LD. The platform generates structured data and you cannot edit or remove it. The documented schema names are Blog post, Event, Local business, Organization, Product, and Website. The schema.org `@type` strings are not public. Product rich results may show name, image, description, price range, availability, and URL. FAQPage is not documented. No article says the site emits aggregateRating.

Headings. Text styles map to tags: Heading 1 is `h1`, Heading 2 is `h2`, Heading 3 is `h3`, Heading 4 is `h4`, and Paragraph 1, 2, and 3 are `p`. The site title has no heading tag on 7.1. Collection pages do not keep a single `h1`. On the 7.1 table, blog and event item titles are `h1` on both the collection page and the item page. Store item titles have no heading on the collection page and are `h1` on the product page. Portfolio 1 and 2 use `h3` for item titles on the collection. Portfolio 3 uses `h1`. The keyword article advises putting Heading 1 at the top and descending after that. That is advice. The template does not enforce it.

Internal links. The checklist says to link pages to each other where it is relevant. No link-graph tool is documented.

Page speed. The speed article says to keep a page at 5 MB or under, and that 1 MB is the safest size on a cellular connection. It points at large images, more than 60 blocks, custom code, and long redirect lists. The SEO article says load time may affect ranking and, in the same help center, support says it cannot guarantee ranking. No Core Web Vitals numbers are public.

Alt text. If you do not write a description, the platform uses the file name. On 7.1, the SEO report can flag missing alt text on image blocks, gallery sections, and auto layouts, and missing SEO descriptions, then suggest text from the Brand Identity. Collection-item images are outside that scan. Suggestions are editable before save. The tool does not flag a missing title in some cases where a title format variable was removed.

## Dynamic behavior

The published site is a hosted Squarespace site, not a file you serve yourself. The visitor runtime's framework name is not public. The help center says JavaScript is what runs slideshows, sliders, and lightboxes, and that an Ajax loading switch can conflict with custom code and anchor links. Code injection can add HTML and JavaScript in the site header, footer, lock page, order confirmation, order status, or a single page's head. A code block can hold HTML, CSS, and Markdown on every plan. JavaScript and iframes in a code block need a higher plan. An embed block pulls oEmbed content. Custom code is not supported by Squarespace support, and the docs say it can break mobile layout.

Forms are form blocks and newsletter blocks. Storage options documented for forms are the login email, the contacts list, Google Drive, Mailchimp, and Zapier. Newsletter blocks default to Squarespace storage and can also use Mailchimp, Zapier, and Google Drive. Submissions are not a static HTML post. The docs recommend no more than 30 fields.

Accounts are customer accounts. A login link appears in the 7.1 navigation when accounts are on. Member sites gate pages behind that account, and behind a price if you set one. Those pages are off the sitemap. Commerce, donations, and Acuity scheduling are separate hosted tools. Blueprint does not have to turn them on. The product page lists selling and scheduling as things you add after the generated site exists.

Editor AI is not the visitor runtime. Text generation is attributed to OpenAI, Anthropic, and Google. Image Studio generates or reshoots images and spends AI credits. Clarkson is an in-editor chat. None of those run as a chat button the docs say you must ship on the public page.

## Already in SpiderCaster

`compose` plans from real `copy/` files. It does not invent a site from a prompt. A package frame only reorders sections the copy already produced. One mold is painted. One catalog part is inserted per section, plus a header and a footer. It writes `structure.json`, `site.json`, and `report.json`. The page stays noindex until a human runs `library bind --live`. The crew does not publish.

`lib/render.py` already builds a palette into CSS variables (`--bg`, `--surface`, `--text`, `--accent`, `--font-head`, `--font-body`) and keeps accent text at the checker's 4.5:1 floor. Sections are a vertical stack with ids. Frames such as `welcome-scroll` name a short list. That is not a Fluid Engine grid, not a saved-section snapshot, and not an auto-layout carousel.

The header is sticky, the brand is text plus a letter mark, and a `nav-toggle` opens `site-nav`. The checker already requires a skip link, scroll-margin, a sticky header, a mobile drawer, no sideways overflow at 360, 390, and 412, a 44 px tap target, 18 px body text, and 16 px chrome. `visit` measures at 390 and 1280 when Playwright is installed. A separate mobile block grid is not generated.

SEO already written on the page: a relative canonical, a site-level meta description reused on every page, a title of page title plus brand, `og:title`, `og:description`, `og:type` of website, `og:image` when a hero image exists, WebSite JSON-LD, no aggregateRating, FAQPage only when the questions are visible, one `h1` on the index, and a non-empty alt on every image. The noindex signal is a meta robots tag, not `robots.txt`. No Python in this tree writes `sitemap.xml`. The SEO seat's hands are `uniqueness` and `meta_basics` only. Favicon is `favicon.svg`.

There is no account system, no form store, no commerce schema, no chat control, and no generated copy.

## Worth building

Only static HTML, the standard library, and strings that already exist in copy. The site stays noindex until a human publishes. Nothing below is imported from Squarespace.

A `robots.txt` that matches the build flag. While the site is noindex, disallow the whole host. After `library bind --live`, write a `sitemap.xml` that lists only the real pages. Do not copy Squarespace priority numbers, and do not claim that a priority changes rank. Do not copy their AI-crawler name list.

A page description only when that page's copy file already has one. Use that string for the page's meta description and `og:description`. If the copy file has none, keep the current site description. Do not write one.

A section surface of light or dark, named in the frame or the copy, painted from the palette `render.py` already builds, and still subject to the contrast checker. Two surfaces, not ten named themes, and not a palette generated from an image.

Do not build a prompt-to-site writer, Image Studio, Clarkson, a custom-section generator, member login, form storage, product rich results, filename-as-alt, multiple `h1`s, a Google Fonts load, a JSON-T import, a second mobile layout that rearranges blocks on its own, or a chat button.

## Sources

https://www.squarespace.com/websites/ai-website-builder — opened 2026-10-08. Marketed four-step flow and FAQ.

https://support.squarespace.com/hc/en-us/articles/206545337-Choosing-the-right-template — opened 2026-10-08. Blueprint field list, shared 7.1 template, publish responsibility.

https://support.squarespace.com/hc/en-us/articles/16282290976013-Using-Squarespace-AI — opened 2026-10-08. Design Intelligence, Image Studio, three create paths, Clarkson, SEO suggestions, stock backgrounds.

https://support.squarespace.com/hc/en-us/articles/360027987711-Page-sections — opened 2026-10-08. Vertical stack, blank, saved, prebuilt, about 20 sections as a load recommendation.

https://support.squarespace.com/hc/en-us/articles/6421525446541-Editing-your-site-with-Fluid-Engine — opened 2026-10-08. Grid editor, 1000-row limit, separate mobile layout.

https://support.squarespace.com/hc/en-us/articles/46489938125965-Style-page-sections — opened 2026-10-08. Design, background, and color fields.

https://support.squarespace.com/hc/en-us/articles/360057763852-Auto-layouts — opened 2026-10-08. Team, Testimonials, Calendar, and named layouts.

https://support.squarespace.com/hc/en-us/articles/360035636332-Gallery-sections — opened 2026-10-08. Gallery layouts.

https://support.squarespace.com/hc/en-us/articles/46489432825613-Save-and-reuse-page-sections — opened 2026-10-08. Saved-section cap and what a snapshot keeps.

https://support.squarespace.com/hc/en-us/articles/206543757-Add-content-to-your-site-with-blocks — opened 2026-10-08. Block model and partial type list.

https://support.squarespace.com/hc/en-us/articles/205815278-Change-your-site-s-colors — opened 2026-10-08. Five-color palette and ten themes.

https://support.squarespace.com/hc/en-us/articles/206545327-Choose-and-style-your-site-s-fonts — opened 2026-10-08. Font packs and base size.

https://support.squarespace.com/hc/en-us/articles/205815788-Make-style-changes-to-your-site — opened 2026-10-08. Site-style theme packs.

https://support.squarespace.com/hc/en-us/articles/206545717-Squarespace-Developer-Platform-FAQ — opened 2026-10-08. 7.1 template source is closed.

https://developers.squarespace.com/template-overview/ — opened 2026-10-08. 7.0 folder roles, JSON-T, LESS.

https://github.com/Squarespace/base-template — opened 2026-10-08. Public 7.0 starter. Not the Blueprint store.

https://support.squarespace.com/hc/en-us/articles/360000667707-Build-your-site-header — opened 2026-10-08. Header and mobile menu.

https://support.squarespace.com/hc/en-us/articles/205815288-How-blocks-stack-on-mobile-in-the-classic-editor — opened 2026-10-08. Classic column stack.

https://support.squarespace.com/hc/en-us/articles/206542527-Adding-a-favicon-or-browser-icon — opened 2026-10-08. Favicon limits.

https://support.squarespace.com/hc/en-us/articles/206744067-What-Squarespace-does-for-SEO — opened 2026-10-08. Sitemap, structured data, no ranking guarantee. Live title is "How does Squarespace optimize my site for search results?"

https://support.squarespace.com/hc/en-us/articles/360002090267-SEO-checklist — opened 2026-10-08. Title, description, alt, links, page size.

https://support.squarespace.com/hc/en-us/articles/206543547-View-your-site-map — opened 2026-10-08. Sitemap contents. July 2026 text says priority is not a ranking control.

https://support.squarespace.com/hc/en-us/articles/21829426828045-Hiding-your-site-from-search-results — opened 2026-10-08. Crawlers toggle and `Disallow: /`.

https://support.squarespace.com/hc/en-us/articles/360022347072-Request-that-AI-models-exclude-your-site — opened 2026-10-08. AI crawler request. Not a guarantee.

https://support.squarespace.com/hc/en-us/articles/360022365512-Controlling-who-can-access-your-site-s-pages — opened 2026-10-08. Index and sitemap matrix.

https://support.squarespace.com/hc/en-us/articles/206536827-Starting-a-Squarespace-trial-site — opened 2026-10-08. Trials are not indexed.

https://support.squarespace.com/hc/en-us/articles/360002088548-Publishing-or-hiding-your-site — opened 2026-10-08. Private, password, and public.

https://support.squarespace.com/hc/en-us/articles/205812368-Setting-a-primary-domain — opened 2026-10-08. Primary domain and 301.

https://support.squarespace.com/hc/en-us/articles/360025606831-How-blog-tags-and-categories-appear-in-search — opened 2026-10-08. Canonical on filtered blog URLs.

https://support.squarespace.com/hc/en-us/articles/206544147-Editing-page-titles — opened 2026-10-08. SEO title, 100-character limit.

https://support.squarespace.com/hc/en-us/articles/205814428-Changing-title-formats-for-SEO-and-browser-tabs — opened 2026-10-08. `%s`, `%p`, `%i`.

https://support.squarespace.com/hc/en-us/articles/206543657-Page-settings — opened 2026-10-08. SEO description, SEO title, social image, hide from search.

https://support.squarespace.com/hc/en-us/articles/205812778-Adding-social-sharing-images — opened 2026-10-08. Social sharing images. Open Graph property names not on this page.

https://support.squarespace.com/hc/en-us/articles/360002076628-Heading-tags-and-Squarespace — opened 2026-10-08. Heading map, including multiple `h1`s on collections.

https://support.squarespace.com/hc/en-us/articles/360022529371-Reducing-your-page-size-for-faster-loading — opened 2026-10-08. 5 MB recommendation.

https://support.squarespace.com/hc/en-us/articles/206566737-Form-blocks — opened 2026-10-08. Form block and storage.

https://support.squarespace.com/hc/en-us/articles/205814638-Managing-form-and-newsletter-storage — opened 2026-10-08. Email, contacts, Google Drive, Mailchimp, Zapier.

https://support.squarespace.com/hc/en-us/articles/360050832631-Member-Sites — opened 2026-10-08. Member pages leave the sitemap.

https://support.squarespace.com/hc/en-us/articles/115012777327-Customer-accounts — opened 2026-10-08. Account login on 7.1.

https://support.squarespace.com/hc/en-us/articles/205815908-Using-code-injection — opened 2026-10-08. Header and footer script injection.

https://support.squarespace.com/hc/en-us/articles/38299115788813-Optimize-your-site-for-AI-powered-search-engines — opened 2026-10-08. AI-search advice. Not a procedure that changes the page template.
