# Pattern sources

Date: 2026-10-01. Method: public docs, category guides, and two small-business articles were opened in the browser. No theme zip, PHP, or theme source was saved. Section lists below are only what those pages described. GitHub HTML for the two catalog index files returned a 9-line shell and no order text, so those two orders were read from the raw public JSON of the same files (type names and order only). The first Squarespace help open was a sign-in shell; the article body was then read from the same public URL. A search excerpt of a longer catalog homepage (rich text, collage, video, multi-column) did not match the index file that opened, so it was dropped. Third-party auto-generated theme references and template-gallery hits that were not opened are not used as section lists.

## Sources

| Product | URL | What was actually read | One-line pattern |
| --- | --- | --- | --- |
| Wix Editor | https://support.wix.com/en/article/wix-editor-adding-and-setting-up-sections | Full-width sections, chosen from a category, reorderable. Panel can follow business type (stores, blogs). A section can be a menu item, called out for a one-page site. | Stack of named sections; one-page nav jumps to them. |
| Wix Harmony | https://support.wix.com/en/article/wix-harmony-editor-adding-and-customizing-sections | Designed sections are browsed by category. The only examples named on the page are Welcome, About, and Products. Blank and AI starts also exist. | Welcome, then about, then products is the only category sample given. |
| Wix templates | https://dev.wix.com/docs/api-reference/account-level/sites/projects/site-template-ids | Four public type groups: eCommerce, service provider (bookings, no in-template payments), business (contact form), portfolio. Styles are labels only. No homepage section order. | Store, booked service, contact-led business, or portfolio. |
| Shopify help | https://help.shopify.com/en/manual/online-store/themes/theme-structure/sections-and-blocks | Home page is the default template. Named examples: Slideshow (Slide, Heading, Image, Button), Image banner, Email signup (Email form, Heading, Subheading). Merchants reorder sections. No default homepage order on this page. | Banner or slideshow, then merchant-ordered sections, with a button block. |
| Shopify index | https://shopify.dev/docs/storefronts/themes/architecture/templates/index-template | Index template is the store homepage. Merchants add, remove, and reorder sections. Points at a reference theme index and does not list that file’s sections. | Homepage is an ordered section list, not a fixed page. |
| Shopify groups | https://shopify.dev/docs/storefronts/themes/architecture/section-groups | Header and footer are the usual shared groups. An extra group may be a navigation sidebar. The footer example is newsletter then quick links. | Top bar plus footer; sidebar only if a theme adds that group. |
| Catalog index A | https://raw.githubusercontent.com/Shopify/dawn/main/templates/index.json | Opened raw JSON. Order is image banner (heading, shop-all button), then featured collection. HTML blob of the same path did not render. | Hero with a shop action, then a featured goods grid. |
| Catalog index B | https://raw.githubusercontent.com/Shopify/horizon/main/templates/index.json | Opened raw JSON. Order is hero (heading text, shop-all button), then a product list titled as a featured collection. HTML blob did not render. | Same family: hero, then featured goods. |
| Squarespace sections | https://support.squarespace.com/hc/en-us/articles/360027987711-Page-sections | First open was a sign-in shell. Article body then loaded: vertical stack; blank, saved, or category of prebuilt sections; Fluid Engine, auto layout, collection, gallery, classic. Gallery is images with little text. Suggests at most about 20 sections. Category names are not listed. | Pages are a vertical stack; galleries are their own section type. |
| Squarespace restaurant | https://support.squarespace.com/hc/en-us/articles/208922158-Building-a-restaurant-site | Start in the Restaurants template-store category. Hours and location via a contact layout, a contact section, or the footer. Menu section or menu page. Several menus can be a nav dropdown. Gallery or auto layout for food and room. Optional About, press, private events. | Menu, hours, place, and pictures; story is extra. |
| Squarespace portfolio | https://support.squarespace.com/hc/en-us/articles/210295778-Building-a-portfolio-site | Start in the Portfolios category. Landing of projects (grid or hover), gallery sections, image blocks, a bio or CV, and a contact page or form. | Work first, short bio, then a way to inquire. |
| Webflow structure | https://developers.webflow.com/flowkit/structure/page-structure | Typical page: body, nav, section, container, layout, footer. Sections are the core blocks. No marketing section order. | Nav, stacked sections, footer. |
| Webflow University | https://university.webflow.com/course-lesson/design-and-build-pages-with-seo-in-mind | One H1, H2 per major section, H3 for subsections or FAQs. Header, nav, main, section, footer. Lead with the important information. No homepage recipe. | One title, then scannable sections, FAQ as a subsection. |
| Webflow page building | https://help.webflow.com/hc/en-us/articles/33961210206483-Page-building | Marketers assemble landing, feature, solution, and event pages from approved components in page slots. No section order. | Campaign pages are a slot of reusable blocks, not a fixed stack. |
| Framer layouts | https://www.framer.com/help/articles/using-layout-templates/ | Shared layout holds navigation, footer, announcement banner, and optional sidebar. Page content sits in a slot. Desktop nav can become a compact menu on small screens. | Chrome is shared; the page is the slot inside it. |
| Framer guide | https://www.framer.com/guides/improve-hierarchy-and-clarity/ | Put the key summary first. One H1, H2 for major sections, H3 for FAQs. Vertical stack. Do not hide the summary or FAQ. | Open with the point, then sections, FAQ visible. |
| Local service article | https://front.adiq.com/learn/homepage-that-converts.html | Stated top-to-bottom order: hero, services, social-proof bar, about and team, service-area map, testimonials, FAQ, contact and footer. | Local service: offer, numbers, people, proof, questions, contact. |
| Restaurant article | https://www.tryperdiem.com/blog/the-restaurant-website-blueprint-what-to-include-and-where | Suggested flow: nav, main message with menu and order actions, featured food, reviews, what is different, catering or another service, locations, extras, common questions, footer. Menu stays its own page. | Food and the next action before the story. |

Not opened, so not used for a section list: Wix template-gallery HTML (search hits only), a third-party auto-doc of catalog section files (search hit only), and Framer video tutorials. No search query returned an empty error. The GitHub HTML views and the first Squarespace open failed as shells, as noted above.

Shipped copies of these objects are `library/frames/<id>.json`. Package notes drop the colon the frame checker refuses. The section order is unchanged.

## frames

```json
[
  {
    "id": "local-desk",
    "intent": "A local service page that says the job and the place, then shows the offer, numbers, and how to ask.",
    "sections": ["hero", "features", "stats", "about", "testimonials", "faq", "contact"],
    "nav": "top-bar",
    "template": "modern",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: local service. Not a copy of a vendor theme."
  },
  {
    "id": "catalog-front",
    "intent": "A small shop homepage that opens on a banner with one shop action, then a featured set of goods.",
    "sections": ["hero", "features", "gallery", "cta"],
    "nav": "top-bar",
    "template": "bold",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: online catalog. Not a copy of a vendor theme."
  },
  {
    "id": "house-menu",
    "intent": "A restaurant or cafe page that puts the menu and a way to visit ahead of the story.",
    "sections": ["hero", "menu", "gallery", "testimonials", "about", "faq", "contact"],
    "nav": "segmented",
    "template": "editorial",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: restaurant menu. Not a copy of a vendor theme."
  },
  {
    "id": "project-index",
    "intent": "A portfolio that leads with the work, then a short bio and a project inquiry.",
    "sections": ["hero", "gallery", "about", "steps", "cta"],
    "nav": "sidebar",
    "template": "editorial",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: portfolio. Not a copy of a vendor theme."
  },
  {
    "id": "visit-book",
    "intent": "A booking practice that lists services, the visit steps, and a price cue before the ask.",
    "sections": ["hero", "features", "steps", "pricing", "testimonials", "faq", "cta"],
    "nav": "one-page",
    "template": "modern",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: booked service. Not a copy of a vendor theme."
  },
  {
    "id": "welcome-scroll",
    "intent": "A single scrolling page whose menu jumps from a welcome to the story, the offer, and contact.",
    "sections": ["hero", "about", "features", "gallery", "faq", "contact"],
    "nav": "one-page",
    "template": "bold",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: one-page welcome. Not a copy of a vendor theme."
  },
  {
    "id": "hours-stack",
    "intent": "A food page with a short stack and hours, place, and links kept in the footer.",
    "sections": ["hero", "menu", "features", "faq", "contact"],
    "nav": "footer-only",
    "template": "editorial",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: restaurant hours. Not a copy of a vendor theme."
  },
  {
    "id": "practice-intro",
    "intent": "A professional practice that introduces the firm and the people before the contact path.",
    "sections": ["hero", "about", "team", "features", "testimonials", "contact"],
    "nav": "sidebar",
    "template": "modern",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: professional service. Not a copy of a vendor theme."
  },
  {
    "id": "trust-lane",
    "intent": "A quote-led service page that shows numbers, the process, and a price cue, then the form.",
    "sections": ["hero", "stats", "steps", "pricing", "faq", "contact"],
    "nav": "segmented",
    "template": "bold",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: local service quote. Not a copy of a vendor theme."
  },
  {
    "id": "maker-shelf",
    "intent": "A product maker page with a gallery, a strip of marks, a short story, and one shop action.",
    "sections": ["hero", "gallery", "logocloud", "about", "cta"],
    "nav": "top-bar",
    "template": "editorial",
    "package": true,
    "note": "Original section order for SpiderCaster. Pattern family: small shop. Not a copy of a vendor theme."
  }
]
```

## Do not ship

- No vendor HTML, CSS, PHP, or theme zip. These frames are section order only.
- No stock CDN urls and no remote image addresses in a mold or a page.
- No live reuse of one frame on two sites. A mold or frame already live stays on that one site.
- Do not name a Wix, Shopify, Squarespace, Webflow, or Framer template as a SpiderCaster mold.
