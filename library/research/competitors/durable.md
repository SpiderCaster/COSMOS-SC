Durable

Notes from 2026-10-01 said the public procedure was the product page: three questions, then a generated site, with the editor model, publish click, and SEO files not public. Live help opened 2026-10-08 documents those. Where two live pages disagree, both are stated. This report did not measure a customer site's HTML.

## 1. Product

Durable builds a hosted small-business site, plus a dashboard for leads, bookings, invoices, and agents. It is not a repo the person clones. A code sandbox, terminal, and project file tree are not public.

The product page is the generation claim. The person answers three questions. The FAQ names industry, business name, and goals. Durable then generates a site with content, images, and design. The page says this takes around 30 seconds, and that there is no template browse and no blank page to fill. No screen is documented where a human approves a page or section plan before that site exists.

A different help article, for adding another business inside an account, asks for business type, city and country, and business name, then says Durable generates a blank website. Regenerating a site, from Website settings, deletes the current site and builds a new design and new content from the business info already on the dashboard. That article does not list the three questions and does not show a plan review. The old site cannot be recovered.

After a site exists, the person edits in the website editor. Pages are destinations with their own URLs. Sections are blocks stacked on one page and do not have URLs. The documented rule is: if it needs its own URL, make a page; otherwise add a section. Pages split into main navigation and other pages. Other pages stay out of the nav unless linked, and the article says that split is not an index switch.

Named controls include Add Section, Edit, Design, Customize, Move Up, Move Down, and Delete. A new page can also be described in words; the launch-era claim that a described page matches the existing site is still the product story, and the help article for regenerate confirms new content is generated from the business profile. Build-your-own (Custom) takes a prompt and an optional JPEG, PNG, or GIF, then Create custom, then AI Edit.

Themes and tokens are not chosen before the first page. They are applied after, on content that already exists. Themes (grid icon) preview the current content, Confirm theme or Undo theme, and Generate more. Customize sets palette, fonts, and corners. Shuffle remixes those three and leaves layout and section types alone.

Who reviews: the person. Preview hides edit controls. The publish checklist in the May 21, 2026 preview article is preview, desktop and mobile, navigation links, and important pages. An SEO status panel lists LLM readability, website indexability, mobile responsiveness, H1 tags, image alt text, and page titles. Nothing on the pages opened says that panel blocks Publish. No automated visual critic is named.

Going live is a human click, separate from editing. Publish, or Publish changes, updates the live site. Site settings also have Published and Unpublished, and a site-wide search-engine visibility control. The free plan is a private preview on a `*.durable.site` subdomain. The product FAQ says a custom domain that can be found on Google starts on a paid plan. That is packaging, not a measured robots rule.

The help articles disagree about whether an edit is stored before Publish. Getting Oriented (September 3, 2026) says edits save automatically in the editor and stay invisible until Publish. Blog settings (May 15, 2026) also say those settings save automatically. Pages and Sections, Working With Sections, Navigation and Footer, and Previewing (May 21, 2026) say changes do not save until Publish Changes and are lost if you leave. Designing Your Site (September 1, 2026) says design changes are not saved if you leave without publishing. Which behavior the product uses today is not measured.

What must not be invented is not public. The FAQ section article says Durable adds example questions and answers. The contact section article says the form starts with example content. AI Partner's help lists a prompt that adds a testimonial with a made-up name. No page opened says testimonials or reviews must be real.

## 2. Code libraries

The customer editor and the published customer renderer are closed. No public package, registry, CSS framework, theme filename, or section schema was found. Named font files are not public. The company marketing site is not that renderer: pages on durable.com use a `/_next/image` route and Open Graph images on a Vercel blob host. Customer sites are documented as hosted on Cloudflare (SSL, firewall, DDoS, CDN). The dashboard host linked from help is `app.durable.co`.

How a section is stored, from the editor docs, not from a file: one page holds an ordered vertical list of typed sections. A section does not exist apart from its page and does not change other pages. Page fields documented: title, navigation label, URL slug, homepage flag, SEO title, meta description, Open Graph image, and an index control. Section fields documented: text, images, buttons and links, a layout preset, and an optional section palette. Custom interactive sections add an element ID, a label, a type (slider, number, select, or toggle), range controls (minimum, maximum, step, default), options, and a formula field. Documented formula helpers are min, max, round, if, tier, and lookup. The on-disk or database shape of that model is not public.

Global design, also not a public token file: a theme (layout patterns, light or dark, navigation, buttons, backgrounds; theme names not listed), a palette with a Base color plus three swatches and shade ranges, a font choice, and a corner preset. Palette and custom colors can override one section. The color article says choosing a palette does not paint every element that exact shade; Durable picks readable variants. Manual custom colors skip those checks. Primary, Secondary, and Outline buttons can be set apart from the palette.

Two section lists are both dated May 21, 2026. Working With Sections (current editor language: control bar, Publish Changes) names Banner, Feature, Metrics, Gallery, Team, Contact, Call to Action, FAQs, Pricing, Text, and Embed. Later articles add Video and Custom. Learn About Different Sections uses Add section + and Save, and names Banner, Calendly, Call to Action, Contact Form, Embed, FAQ, Google Reviews, Image, Image Carousel, Image Grid, Instagram, List, Location, Logo Showcase, Pricing Table, Quote/Testimonial, Services, Team Members, Text, Text + Image, Video, Recent Blog Post, and Business Hours. Treat the second list as the other documented vocabulary, likely the legacy editor, which still has its own help collection. This report did not open that collection's articles.

Page templates named in help: Blank, Services, About, Contact, Single Service, Team, FAQ, Terms of Service, and Privacy Policy. Screenshots in that article use 2023 staging filenames, so the pictures may be the older builder. The names are what the May 21, 2026 article still lists. Help says Durable will not advise whether Terms or Privacy text is legally valid.

Header and footer are site-wide, not page sections. Navigation links can target a page, an external URL, email, phone, a section, or the booking widget. Dropdowns group pages. Up to four social links. Sticky header is a toggle. Navigation design presets include full-width and alignment. The language switcher sits in the nav or next to the buttons.

Blog posts are a separate record from page sections: title, author, published date, and status Draft or Published. The blog index slug defaults to `/blog` and can be changed. Post chrome presets are named Classic, Hero, Minimal, and Magazine for the header, and Complete, Related Posts, Navigation, and Minimal for the footer. Colors come from the site theme. Content width is Narrow, Medium, or Wide.

## 3. Mobile

The product page says every site is automatically responsive for mobile, tablet, and desktop, and calls templates mobile-perfect. Those are claims, not a measured spec.

Getting Oriented (September 3, 2026) says Preview toggles Desktop, Tablet, and Mobile. The May 21, 2026 preview article names desktop and mobile only. Banner design can fill the viewport and set vertical alignment. Sticky header can stay or scroll away. The SEO status panel includes mobile responsiveness. What that check measures is not public.

The performance article says image compression, lazy-loading, CSS and JavaScript minification, and CDN delivery are automatic. It names First Contentful Paint, Largest Contentful Paint, and Cumulative Layout Shift. It says mobile scores can be lower because test tools throttle network and CPU, and that Durable works on mobile Largest Contentful Paint. It says sites often score 90 or above on Lighthouse SEO, Accessibility, and Best Practices. That score was not measured here. Interaction to Next Paint is not named.

Breakpoints in pixels, a hamburger or drawer, tap-target size, and a type scale are not public. A custom-section prompt in the help text suggests a sideways-scrolling card row. That is a prompt idea, not a small-screen rule.

## 4. SEO

Documented features below are not ranking guarantees. "Get found on Google and ChatGPT", Visibility Score, and "often 90+" are product claims. This report did not measure rankings, Core Web Vitals, or a customer response.

Sitemap. Foundational SEO (May 21, 2026) says every site serves `sitemap.xml` listing public pages and last-updated timestamps, plus `robots.txt`. View your website sitemap (May 25, 2026) says the file is at `/sitemap` on the customer domain. The Search Console article says to submit the string `sitemap.xml`. Which URL responds on a customer domain is not measured. The company site durable.com, which is not the customer renderer, serves `/sitemap.xml` as an index of child sitemaps under `/sitemaps/`.

Robots. A `robots.txt` is documented for customer sites. Its directives are not public. Per-page, Foundational SEO names a noIndex setting that also removes the page from the sitemap and from `llms.txt`. The Search Console article names a toggle, Remove from sitemap. Whether those are one control is not public. Site-wide, General settings cover Published or Unpublished and search-engine visibility. The free plan is described as a private preview. The meta robots string on that preview is not public.

Canonical. Not public for customer sites. The company site prints an absolute canonical. That is not the customer procedure.

Title and description. Every published page gets a title and meta description generated from the business profile and page content. The person can edit SEO Title and Description per page, or use AI generate SEO / Use AI. The page-settings article recommends a description of 110 to 160 characters. That is their writing advice, not a measured ranking rule. A title length limit is not public in the articles opened. Initial values are generated at publish; they are not rewritten automatically when the page changes. Grow marketing copy says the site and SEO metadata can be translated. The language article says titles and meta descriptions are translated and kept in sync, up to five extra languages, and that business names and service names stay in the original language. hreflang is not public.

Open Graph. Customer pages get Open Graph tags, including an image, title, and description. The person can replace the Open Graph image or Regenerate it. Twitter card tags on customer sites are not public. The company site uses `summary_large_image`.

JSON-LD. Foundational SEO says every published page includes JSON-LD generated from the business profile and page content, and that it is not editable in the dashboard. Schema types are not named. The article's examples of rich results (star ratings, author bylines, FAQ boxes) are illustrations, not a type list. The FAQ section article does not mention FAQPage. The pricing page of durable.com itself, the company site, emits FAQPage. That was not checked on a customer site.

Heading order. Help says content uses H1, H2, and H3. The pricing table lists auto-tagged H1, H2, and H3 under Advanced SEO. A single-H1 rule is not public. The editor status panel includes H1 tags. What fails that check is not public.

Internal links. Documented sources are navigation, footer, section links, dropdowns, and buttons. Other pages can be linked without sitting in the nav. Blog settings can show related posts. A keyword tool can create a new page or blog post from a topic. That is an agent feature, not a link graph this report measured.

Page speed. See Mobile. Documented mechanisms are compression, lazy-loading, minification, and CDN. No customer timing was measured.

Index controls. Publish versus Unpublished, site-wide search visibility, per-page noIndex and Remove from sitemap, and optional manual submission of `sitemap.xml` in Google Search Console (HTML tag pasted into custom code in the head) plus a Bing import of that Search Console property. Indexing is not instant; the article says days to weeks. Submitting a URL again does not raise its queue priority. `llms.txt` is named as a file that loses a page when noIndex is on, and as a pricing-table row. Its path and body are not public.

Pricing table rows for Advanced SEO (optimized metadata, auto-tagged headings, JSON-LD, sitemap and robots.txt, fast mobile pages) lost their checkmarks in the text extract, so which plan includes each row is not public from that extract. The foundational article says those SEO features are on for every published site. Launch marketing copy is what says "Advanced SEO & GEO".

Slug changes can add a 301 from the old slug to the new one via a checkbox, Redirect /old-slug to /new-slug. A separate article covers 301s for missing pages. Those redirects are a hosted feature.

## 5. Dynamic behavior

Customer pages are served by Durable's host, not exported as a documented static bundle. An export format is not public. The page runtime's framework name is not public.

Contact. A Contact section includes a form. Documented settings are the destination email, phone, address, a directions link, and a success title, message, and button. Submissions are a lead. The Website Lead Agent can draft replies; the person reviews them. The form's request URL and backend name are not public.

Bookings. A booking widget can be shown from the header calendar control or a Booking link. Launch marketing copy includes calendar sync and paid bookings. The booking runtime was not opened article by article.

Custom code. Site-wide snippets go in Website settings, Integrations, Custom Code, placed at the end of the head or the end of the body. An Embed section is the per-section path for HTML, CSS, JavaScript, maps, or other widgets. Entries can be disabled or deleted. Help says the snippet must come from a trusted source. This is customer JavaScript on a Durable page, not a public Durable component library. Launch marketing copy lists custom code. Whether the free plan can save a snippet is not stated in the articles opened.

Custom sections can run in-page tools (calculators, toggles, sliders) using the formula fields in section 2. That execution engine is not named.

Blog. Posts are drafted in the editor from a description, with title suggestions, Generate, and Regenerate, or written without generation. Save, then Publish Post. Unpublish Post removes it from the live site. The first post adds the blog to navigation. The Blog Agent researches and drafts. Its tool schema is not public.

Accounts. The owner has a dashboard per business (site, contacts, invoices). Grow marketing copy includes unlimited teammates. A visitor login for the public site is not public.

Other client behavior documented: language switcher, Google Analytics via Integrations, Studio image generate and edit, AI-written alt text on uploaded images (the article says uploaded; alt text on generated images is not separately stated), and AI Partner. AI Partner is a chat that can change site text and images, show an Updated website draft, and wait for the person to Publish. Undo sits on that draft message. It can also be asked for research, bookings, and social posts. No tool schema, allow list, or plan mode that refuses writes is public.

Agents named on the pricing page as credit uses, not as function signatures: website edit with AI, blog post, social post, Studio image, lead reply, Google review reply, business recap, AI chat reply, deep research, keyword research. Free includes 300 credits total. Launch includes 1000 a month. Grow includes 5000 a month. Those counts are packaging.

## 6. Already in SpiderCaster

SpiderCaster already keeps a site noindex until a human runs `library bind --live`. Compose builds from real `copy/` files, reorders only sections that copy already produced, paints one mold, and inserts one catalog part per section plus a header and a footer. It writes `structure.json`, `site.json`, and `report.json`. That is a page-and-section split with a human publish gate, without Durable's generate-first step.

The renderer already emits a viewport meta tag, a per-page title, a meta description, `og:title`, `og:description`, `og:type`, `og:image` only when the hero already has a local relative image, a relative canonical, `favicon.svg`, WebSite JSON-LD, and FAQPage JSON-LD only from questions on the page. The checker refuses aggregateRating, requires FAQ text to be visible when FAQPage is present, requires one h1, skip link, scroll-margin, sticky header, a mobile drawer, 44px taps, 18px body text, 16px chrome, contrast 4.5:1, and no sideways overflow at 360, 390, and 412. `visit` measures at 390 and 1280 when Playwright is installed. The SEO seat's hands are only `uniqueness` and `meta_basics`.

The meta description and `og:description` are the site description on every page, not a per-page field. There is no `sitemap.xml`, no `robots.txt` file (only a robots meta tag), no per-page noindex separate from the site flag, no blog record, no contact-form handler, and no token file the person edits as Base-plus-three swatches. Contrast is enforced, including on custom colors. Durable's manual colors skip that check. SpiderCaster does not.

## 7. Worth building

Only static HTML, the standard library, and real copy. The site stays noindex until a human publishes. Reimplement. Do not import Durable's editor, agents, or snippets.

A `sitemap.xml` of real pages, with lastmod taken from file times, and a `robots.txt` that points at it, written only on the indexable build. While the site is noindex, do not write a crawlable sitemap. This is the documented file pair SpiderCaster does not emit. It is not a ranking promise.

A per-page flag, stored with that page, that adds noindex on that file and leaves the page out of the sitemap. The site-wide noindex flag still wins until the human publishes. Do not invent a second index file whose body is not public. `llms.txt` format is not public, so do not add one.

Per-page meta description and `og:description` read from that page's copy. Keep `og:image` limited to a local image the page already has. Do not add an AI rewrite of the description, and do not enforce 110 to 160 characters as if it were a rank rule.

A static blog: one HTML file per post that already exists in `copy/`, plus an index that links those files. Show title, date, and author on the page. Related links only when copy names them. No draft generator.

Do not build Durable's image or blog agents, example FAQ or contact filler, testimonial or review blocks, star-rating JSON-LD, quote calculators, embed or custom-code injection, chat or booking widgets, machine translation, keyword-invented pages, or hosted 301s. A static file cannot perform their slug redirect. Do not loosen the one-h1 rule, the contrast check, or the ban on sideways overflow to match undocumented mobile behavior.

## 8. Sources

Opened 2026-10-08 unless noted. Help articles are the procedure. The product and pricing pages are packaging and claims. The company sitemap is the marketing site, not a customer site.

https://durable.com/ai-website-builder — product steps, FAQ, free preview versus paid domain.
https://durable.com/pricing — plans, feature rows, Cloudflare hosting claim, FAQPage on the company page.
https://durable.com/sitemap.xml — company sitemap index only.
https://durable.com/made-with-durable — company page; customer URLs did not appear in the extract.
https://help.durable.com/en/ — help index.
https://help.durable.com/en/collections/19642592-website-editor — current editor collection.
https://help.durable.com/en/collections/19642594-working-with-sections — section-type collection.
https://help.durable.com/en/collections/16090429-seo-geo — SEO and GEO collection.
https://help.durable.com/en/collections/19639576-agents — agents collection.
https://help.durable.com/en/collections/12782840-pro-tips — custom code, redirects, video.
https://help.durable.com/en/articles/15199760-getting-oriented-in-the-website-editor — editor areas, themes, auto-save claim, preview sizes, SEO status list. September 3, 2026.
https://help.durable.com/en/articles/15199765-understanding-pages-and-sections — page versus section, publish-only save claim. May 21, 2026.
https://help.durable.com/en/articles/15199768-working-with-sections — section controls and the short type list. May 21, 2026.
https://help.durable.com/en/articles/15199833-learn-about-different-sections-you-can-add-to-your-site — longer type list and Save. May 21, 2026.
https://help.durable.com/en/articles/15199807-learn-about-different-page-templates-you-can-add-to-your-site — page template names. May 21, 2026.
https://help.durable.com/en/articles/16056435-build-your-own-section — custom section fields and formulas. September 3, 2026.
https://help.durable.com/en/articles/15199763-designing-your-site-colors-fonts-and-corners — palette, fonts, corners, contrast note. September 1, 2026.
https://help.durable.com/en/articles/15199761-editing-navigation-and-footer — header, footer, sticky header. May 21, 2026.
https://help.durable.com/en/articles/15199764-previewing-publishing-and-managing-visibility — preview and publish. May 21, 2026.
https://help.durable.com/en/articles/15199789-create-a-new-website-by-adding-a-business — type, location, name, blank site. May 21, 2026.
https://help.durable.com/en/articles/15199859-how-to-regenerate-your-entire-website — regenerate deletes the old site. May 21, 2026.
https://help.durable.com/en/articles/14808635-understanding-durable-s-foundational-seo-features — meta, Open Graph, alt text, headings, JSON-LD, sitemap, robots, noIndex, llms.txt. May 21, 2026.
https://help.durable.com/en/articles/14808637-optimizing-website-performance-for-search-engines — speed claims. May 21, 2026.
https://help.durable.com/en/articles/11202140-edit-seo-settings-for-your-site-and-individual-pages — title, description, share image. March 25, 2026.
https://help.durable.com/en/articles/15199752-manage-page-seo-settings-slugs-and-redirects — slug 301 and Open Graph. Updated the week of the fetch.
https://help.durable.com/en/articles/15199802-view-your-website-sitemap — `/sitemap` path. May 25, 2026.
https://help.durable.com/en/articles/15199855-how-to-index-your-durable-website-in-google-search-console — Search Console, Remove from sitemap. May 21, 2026.
https://help.durable.com/en/articles/12841871-introduction-to-seo-geo — Visibility Score and GEO tools. September 3, 2026.
https://help.durable.com/en/articles/16222219-add-multi-language-support-to-your-website — languages and translated SEO. August 19, 2026.
https://help.durable.com/en/articles/15199864-add-a-blog-page-to-your-site — blog create and publish. May 21, 2026.
https://help.durable.com/en/articles/15112393-customize-your-blog-s-appearance-and-url — blog width, chrome, slug. May 15, 2026.
https://help.durable.com/en/articles/15199776-add-frequently-asked-questions-faq-to-your-website — example FAQ items. May 21, 2026.
https://help.durable.com/en/articles/15199778-when-to-use-a-contact-section-on-your-website — contact form fields. May 21, 2026.
https://help.durable.com/en/articles/15199856-add-custom-code-to-your-website — head and body snippets.
https://help.durable.com/en/articles/16988169-introducing-ai-partner-your-ai-powered-business-assistant — draft, publish, undo.

Prior notes, not re-opened as live pages: `library/research/HOW_PRO_BUILDERS.md` and `library/research/app/HOW_CODE_BUILDERS_TOOLS.md`, gathered 2026-10-01. The live help pages above replace their "not public" lines for sections, publish, and foundational SEO.
