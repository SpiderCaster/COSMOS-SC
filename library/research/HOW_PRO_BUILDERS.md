# How pro AI website builders do it

Read 2026-10-01 from public docs and help pages only. A procedure claim is quoted or paraphrased next to its URL. If the page does not say the step, this file says **not public**. Marketing blogs, reviews, and X posts are not used as procedure.

SpiderCaster, for the adoption section only: seven seats in order (architect, content, frontend, graphics, visual, seo, deployer). Hands today: `brief_read`, `frame_pick`, `mold_pick`, `library_bind` (draft only), `copy_read`, `copy_gap`, `plan_offline`, `render`, `asset_list`, `vault_photos`, `check_site`, `uniqueness`, `meta_basics`, `ticket_write`. Package molds: warmth-authority, discover-grid, clarify-mix. Frames are `spidercaster-frame/1` lists of section types. Render already emits a sticky header, a mobile sheet, a hero visual, and `favicon.svg`. `spidercaster.py image` writes a local file plus a receipt and is not a crew hand.

Fields under each product: first input; design system before copy; section or block model; who reviews; what must not be invented; images; mobile, header, hero, favicon; publish gate.

## Claude Code, Cowork, and Claude Design

These are three surfaces, not one website builder. Claude Code artifacts are one HTML page. Claude Design is a canvas. Cowork artifacts are saved interactive pages. None of the opened docs describe a multi-page marketing site with a section catalog.

**First input.** Claude Code: name the feature or describe the visual output in plain language. Example: "Make an artifact that walks through this PR with the diff annotated inline." Claude may also publish an artifact on its own. https://code.claude.com/docs/en/artifacts

Cowork, from a session: ask in plain language, and name connected apps or local files. From the Artifacts view: open Cowork, select Artifacts, click New artifact; Claude asks a few questions. https://support.claude.com/en/articles/14729249-use-artifacts-in-claude-cowork

Claude Design typical flow: start a design, attach or import the design system, add screenshots or a codebase, then describe the build. A landing-page example in that guide is "Build a landing page for our new API product with a hero section, code examples, and pricing." https://support.claude.com/en/articles/14604416-get-started-with-claude-design

**Design system before copy.** Claude Code artifacts: a built-in design skill "looks for an existing design system in your project before choosing its own." Tokens recorded in `CLAUDE.md` or a theme file outrank that skill. "Claude treats your design system as higher precedence than its own choices, and your prompt as higher precedence than both." https://code.claude.com/docs/en/artifacts

Claude Design: "When you create a project, it automatically inherits your organization’s design system." The guide’s step 2 is attach or import the design system before step 4, describe what to build. Claude "checks its own output against your design system, and makes corrections before you see them." https://support.claude.com/en/articles/14604416-get-started-with-claude-design

**Section or block model.** An artifact "is a single HTML page" and "can’t serve multiple routes." "For multi-section content, Claude uses in-page anchors rather than separate files." https://code.claude.com/docs/en/artifacts

Claude Design is artboards on a canvas, not a named section library. You refine by chat, inline comments, or direct canvas edits. https://support.claude.com/en/articles/14604416-get-started-with-claude-design

Cowork section model: **not public**.

**Who reviews.** Outside plan mode, a new artifact published from a prompt you type "goes through without a permission prompt or classifier review," unless the publish declares runtime capabilities. In plan mode, Claude Code asks before the first publish of each artifact. After a public share, it asks once per conversation before changing the page, or the classifier reviews the change in auto mode. Organization viewers can comment; you can ask Claude to read comments. A public viewer who is signed out sees `Content is user-generated and unverified.` https://code.claude.com/docs/en/artifacts

Claude Design: you review the canvas, then export or share. You can ask Claude to review accessibility, contrast, hierarchy, and usability. That review is optional, not a gate. https://support.claude.com/en/articles/14604416-get-started-with-claude-design

Cowork: the help page says the result saves automatically. A required human Create click is **not public** on that page. https://support.claude.com/en/articles/14729249-use-artifacts-in-claude-cowork

**What must not be invented.** A ban on fake reviews, stock photos, or fake claims is **not public**. The artifact CSP "blocks every external image." Images on the page are data URIs. https://code.claude.com/docs/en/artifacts

**Images.** Attach screenshots or assets in Claude Design. https://support.claude.com/en/articles/14604416-get-started-with-claude-design

How a marketing photo is generated: **not public**. Artifact pages cannot load a remote image URL. https://code.claude.com/docs/en/artifacts

**Mobile, header, hero, favicon.** Claude Design tip: "Mention whether your design needs to work on mobile, tablet, and desktop, or just one of those." Hero appears only as an example prompt, not as a required block. https://support.claude.com/en/articles/14604416-get-started-with-claude-design

Favicon-like control, artifacts only: "Claude can also pick a browser-tab icon that matches what the page is, such as a chart or a calendar. Ask Claude for a specific title, emoji, or tab icon if you want one." https://code.claude.com/docs/en/artifacts

Header handling and a required hero: **not public**. Cowork mobile, header, hero, and favicon: **not public**.

**Publish gate.** A new artifact "stays private to you until you share it." Share is the **Share** control in the page header. Team and Enterprise public sharing is off until an Owner enables External sharing. https://code.claude.com/docs/en/artifacts

Claude Design starts private. Click Share and choose who can open it. Export includes a zip, PDF, standalone HTML, or a handoff to Claude Code, Netlify, Vercel, Wix, v0, or Lovable. https://support.claude.com/en/articles/14604416-get-started-with-claude-design

Cowork sharing rules for older live artifacts are a different article. The current share dialog is documented at https://support.claude.com/en/articles/9547008-publish-and-share-artifacts

## Perplexity Computer

**First input.** Computer is "an independent digital worker." You ask it to do work; the help page does not show a website-only form. https://www.perplexity.ai/help-center/en/articles/13837784-what-is-computer

The API docs say Computer can "Build and deploy websites to a live public URL in minutes." They do not show the prompt fields. https://docs.perplexity.ai/docs/getting-started/integrations/computer-mcp-server

**Design system before copy.** **Not public.**

**Section or block model.** **Not public.**

**Who reviews.** The site starts as a preview "visible only to you." No visual critic or checklist is named. https://www.perplexity.ai/help-center/en/articles/20260711-publishing-your-website-to-the-web

**What must not be invented.** **Not public.**

**Images.** Computer’s overview lists "Rich media generation for creating visual content." It does not say how a site image is attached. https://www.perplexity.ai/help-center/en/articles/13837784-what-is-computer

**Mobile, header, hero, favicon.** **Not public** in the help pages opened. A 2026-09-09 post from @AskPerplexity said desktop and mobile previews exist. That post is not a help page, so it is not treated as the procedure.

**Publish gate.** "To publish, open the website preview and select Publish in the publish view." Two paths: **Publish (Perplexity)** to a `pplx.app` URL, or **Publish with Vercel** through the Vercel connector. "Publishing and visibility are separate — publishing a site does not make it public unless you choose that visibility level." Organization sites default to organization-only. Consumer sites default to public. Visibility can be private, organization, specific people, or public. Admins can disable public publishing under Organization Settings > Computer; Vercel publish is then removed. Unpublish is a separate confirm. https://www.perplexity.ai/help-center/en/articles/20260711-publishing-your-website-to-the-web

## Wix: ADI is retired; Harmony is current

**ADI.** "As of November 10th 2024, Wix no longer supports sites created using the ADI (Artificial Design Intelligence) builder. The ADI builder is no longer supported and cannot be accessed to create websites." ADI was replaced by the Wix AI Website Builder. Published ADI sites open in the Wix Editor. Unpublished changes that were never published "have not been transferred." https://support.wix.com/en/article/adi-sites-no-longer-supported

Harmony is the January 2026 editor. Aria is the agent inside it. https://support.wix.com/en/article/about-the-new-wix-harmony-editor

**First input.** Log in, open the site dashboard, click **Design Site**. Either edit Aria’s suggested description (business, colors, style) and click **Generate Site**, or pick a recommended template and click **Edit**. https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai

ChatGPT path: write a prompt that includes `@wix`, review the planned site, then click **Create Site** or send another message first. https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-from-chatgpt

**Design system before copy.** On the description path, Aria "will generate your site's pages, layouts, colors, and fill your site with starter content and images" in one pass. The human can put colors and style in the prompt before that pass. A separate token step before copy is **not public**. An AI-generated site cannot be switched onto a different template. https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai

**Section or block model.** Aria can generate new sections, adjust site colors, and change tone of voice. https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai

In the editor, "Ask Aria to move sections, generate a new design, fix layout issues, or improve section text." https://support.wix.com/en/article/wix-harmony-editor-a-guided-tour

Custom elements: **+ Add**, **Generate with AI**, describe, **Generate Element**, review, **Save** into AI Elements. https://support.wix.com/en/article/wix-harmony-editor-generating-an-element-with-ai

One theme versus many: the AI site cannot change template after generation. Named section types and a reorder UI are **not public** beyond "move sections."

**Who reviews.** "Aria is powered by AI and as such may produce unexpected or inaccurate results. Always review Aria’s suggestions or changes before finalizing your site." https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai

No separate visual-critic role is named.

**What must not be invented.** A ban on fake reviews is **not public**. "Should AI-generated content be labeled? Yes, some AI-generated content might need to be labeled as AI." Labeling "may also be a legal requirement." https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai

"Before using any AI-generated content, we recommend double-checking that you have the right to use it." https://support.wix.com/en/article/wix-harmony-editor-working-with-aria

**Images.** The generator fills the site with starter images. Afterward "you can add your own content (e.g. text and images)." https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai

Aria can "generate and enhance images, and manage your site’s media." https://support.wix.com/en/article/wix-harmony-editor-working-with-aria

The image model and a stock-library step are **not public** on those pages. From Wixel, Aria can shape the website prompt from a project or a brand, and you click **Review website prompt** before generation. https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-from-wixel

**Mobile, header, hero, favicon.** **Not public** on the Harmony pages opened.

**Publish gate.** The generator opens a preview "along with tools to finalize your site for launch." Domain connection is a later Aria task. The exact Publish click sequence is **not public** on the creation article. The stated gate is human review "before finalizing your site." https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai

## Framer Agents

**First input.** New project, open the **Agent** tab, type in **Ask Framer…**. The help page says to name the subject, the sections, and the style, not "build me a landing page." Example: `Build a landing page for a coffee roastery called "Ember Roast". Include a hero, a "What We Roast" section with three coffee blends, testimonials, and a contact section. Use a warm, earthy style.` https://www.framer.com/help/articles/how-to-build-a-website-from-scratch-with-framer-agents/

**Design system before copy.** **Not public** as a separate step. Tone, colors, and typography go in the same first prompt. "You can always add detail later, so start with the structure and refine from there." Same URL.

**Section or block model.** Sections are whatever you name in the prompt. After the draft you can say "add a pricing section with three tiers," or select a layer on the canvas and ask the agent to change that part. Same URL.

A closed section catalog and a one-theme rule are **not public** on that page.

**Who reviews.** "Before going live, review the content, images, layout, links, and responsive behavior, just as you would with any site you build in Framer." No automated critic is named. Same URL.

**What must not be invented.** **Not public.** The sample prompt asks for testimonials. The page does not say those must be real.

**Images.** "You can change text, layout, colors, and images directly on the canvas." How the agent produces the image file is **not public**. Same URL.

**Mobile, header, hero, favicon.** Responsive behavior is on the pre-publish review list. Hero is in the sample prompt and in the follow-up "make the hero full-screen." Header and favicon handling: **not public**. Same URL.

**Publish gate.** You publish from Framer when you are happy with the direction. Optional safety path: branch menu, **Create branch**, review **Changes**, **Apply to main**, then publish. Work on a branch does not change **main**. Same URL.

## Durable

The public procedure found is the product page, not a help-center article. https://help.durable.com/en/ lists a Website Editor and does not, in the index that was opened, link a generation procedure. Exact click labels beyond the product page are **not public**.

**First input.** "Answer 3 questions about your business." The FAQ says "your industry, business name, and goals." https://durable.com/ai-website-builder

**Design system before copy.** **Not public.** The same FAQ says the AI then "generates a complete website with relevant content, images, and design." Design is not described as a prior choice.

**Section or block model.** "Drag and drop editor" to "control layouts, swap images, adjust headings, and customize fonts." Named sections, reorder, and one theme: **not public**. Same URL.

**Who reviews.** **Not public.**

**What must not be invented.** **Not public.**

**Images.** The FAQ says the generated site includes images. How they are produced or swapped, beyond "swap images" in the editor, is **not public**. Same URL.

**Mobile, header, hero, favicon.** "builds a mobile-perfect site" is the product claim. Header, hero, and favicon steps: **not public**. Same URL.

**Publish gate.** **Not public** on the page opened. Pricing says a free plan includes a `*.durable.site` subdomain and paid plans include a custom domain. That is packaging, not the click sequence. https://durable.com/pricing

## 10Web Agentic Website Builder

**First input.** On 10web.io, describe the site in the prompt field, or use the plus menu: **Clone site from URL**, **Redesign site from URL**, **Take a screenshot**, **Attach a media file**. Or click **Import Figma**. "If needed, choose a website style from the available system themes." Then submit. https://help.10web.io/hc/en-us/articles/36515422635922-How-to-Generate-a-Website-with-10Web-s-Agentic-Website-Builder

**Design system before copy.** A system theme can be chosen before submit. The structure preview comes next, and "The final website design, content, and layout are created after you start the generation process." So a style pick and a section plan both sit before generated copy. Same URL.

**Section or block model.** The structure shows pages and the sections on each page. In the structure editor you can add a page, add a section, edit the section name, edit the section prompt, use **Enhance with AI** on that prompt, or remove a section. Then **Save and start building**. Same URL.

Reorder is **not public** on that agentic article. A separate ecommerce article says you can "Rearrange, delete, or modify the sections" on a schematic outline, then set global fonts, colors, and styles, then generate. https://help.10web.io/hc/en-us/articles/23531608839570-Section-Based-Ecommerce-Site-Generation

**Who reviews.** The human, on the structure screen: **Start building**, **Customize structure**, or start over. After generation, the AI Editor can preview, chat, edit visually, review code differences, and restore previous changes. No named visual critic. https://help.10web.io/hc/en-us/articles/36515422635922-How-to-Generate-a-Website-with-10Web-s-Agentic-Website-Builder

**What must not be invented.** **Not public.**

**Images.** Inputs can be a screenshot, a media file, or a Figma file. Whether generation still uses a named image model is **not public** on the agentic article. Same URL.

**Mobile, header, hero, favicon.** **Not public** on the agentic article.

**Publish gate.** "publish the website when it is ready" inside 10Web AI Editor. The button name is **not public** on the generation article. Same URL.

## Hostinger AI Builder

**First input.** Dashboard, **Add website**, choose **AI Builder**. Then choose **Manual** or **Agentic**. Then, on "Let AI create your online presence," type a description, click a suggested prompt ("Create a business website" or "Launch an appointments website"), pick a template, speak with the microphone, or attach an image or PDF. "The description should not exceed 700 characters (including spaces)." https://www.hostinger.com/support/7266945-how-to-use-hostinger-ai-builder/

**Design system before copy.** **Not public.** Mode (manual or agentic) is chosen before the description. Colors and tokens are not a separate step on this page.

**Section or block model.** Manual mode: "Drag and edit text, images, and sections by hand." Agentic mode: "Describe changes in a chat with AI, which edits the whole site for you." Named section types and reorder: **not public**. Same URL.

**Who reviews.** "Shortly, you’ll be presented with the result and be able to proceed with any desired changes." No critic or checklist is named. Same URL.

**What must not be invented.** **Not public.**

**Images.** You may attach an image or PDF "such as a design reference or a document with your business details." How generated images are made: **not public**. Same URL.

**Mobile, header, hero, favicon.** **Not public** on this article.

**Publish gate.** **Not public** on this article. The agentic overview says: "Choose a domain name for your website, or select Use temporary domain to set one up later." A temporary domain looks like `calendar-app-802980.hostingersite.com`. https://www.hostinger.com/support/hostinger-ai-builder-agentic-mode-product-overview/

## Squarespace Blueprint AI

**First input.** Two tools, "only available on computers." Blueprint AI Builder: you "select or enter" a site title, a brand personality, a homepage, the sections and pages you need, a color palette and font pairing, and AI-generated images from a curated library. Blueprint AI Templates: on the templates page, pick a topic in the search dropdown and review three AI templates at the top of the results. https://support.squarespace.com/hc/en-us/articles/206545337-Choosing-the-right-template

The product page numbers it: (1) answer questions about the business and brand, (2) the builder generates image, copy, and design suggestions, (3) preview and refine design selections, (4) the builder turns the final choices into the site. https://www.squarespace.com/websites/ai-website-builder

A third path, from the AI help page: in Squarespace GPT, enter business name, business type, brand personality, and the goal. That is passed to Blueprint. https://support.squarespace.com/hc/en-us/articles/16282290976013-Using-Squarespace-AI

**Design system before copy.** Palette and font pairing are inputs you select in the builder, listed beside sections and pages. The help page does not say copy is locked until those tokens are chosen. "When you create a site using any of these methods, Squarespace AI will generate text and images for it and choose style settings based on your prompts." https://support.squarespace.com/hc/en-us/articles/16282290976013-Using-Squarespace-AI

**Section or block model.** Blueprint asks for "Sections and pages you need." https://support.squarespace.com/hc/en-us/articles/206545337-Choosing-the-right-template

After that, version 7.1 pages are page sections. "All sites share the same template, with the same features and style options." You add sections and can override site-wide styles per section. Reorder inside Blueprint itself: **not public**. The general editor is where sections are added. Same URL, plus https://support.squarespace.com/hc/en-us/articles/360027987711-Page-sections

**Who reviews.** "By creating a site using Blueprint AI Builder or Blueprint AI Templates you agree to our Product Specific Terms and understand you're responsible for any content you publish on your site." https://support.squarespace.com/hc/en-us/articles/206545337-Choosing-the-right-template

No visual-critic role is named. Clarkson AI chat can change text and images later; that is editor help, not the Blueprint gate. https://support.squarespace.com/hc/en-us/articles/16282290976013-Using-Squarespace-AI

**What must not be invented.** A ban on fake reviews is **not public**. Responsibility for what you publish is the public rule. Same template article.

**Images.** "AI-generated images from our curated library." https://support.squarespace.com/hc/en-us/articles/206545337-Choosing-the-right-template

"The AI-created images and text on your site are generated with the aid of third-party AI software." Later, a section background can be an AI image, pattern, gradient, or video from **Browse Backgrounds**. https://support.squarespace.com/hc/en-us/articles/16282290976013-Using-Squarespace-AI

**Mobile, header, hero, favicon.** The AI tools "aren’t supported on mobile devices." That is where you are allowed to run Blueprint, not how the page responds. https://support.squarespace.com/hc/en-us/articles/206545337-Choosing-the-right-template

Header, hero, and favicon steps inside Blueprint: **not public**.

**Publish gate.** **Not public** as a Blueprint-specific click sequence. The public gate on the template article is that you are responsible for content you publish.

## Shopify Magic and the Horizon section model

**First input.** Two different tools.

Theme generation, mobile only: Shopify app or a mobile browser, Online Store, **Manage themes**, describe the business under **Design your store in seconds**, tap **Generate themes** (up to 3), tap **Try theme**. "You can no longer generate one from the desktop Shopify admin." "Certain topics that violate Shopify's policies can't be used for theme generation." The theme lands under **Draft themes**. https://help.shopify.com/en/manual/online-store/themes/adding-themes

Inside an existing theme, text: **Edit theme**, select a text element, **Generate text**, enter a prompt such as headline or title, then optional edit, then **Save**. https://help.shopify.com/en/manual/online-store/themes/customizing-themes/theme-editor/shopify-magic/generate-content

Inside an existing theme, a block: open the section, **Add block**, **Generate**, describe the block. Prompts should be at least five words. The help example ends with "Stack on mobile." https://help.shopify.com/en/manual/online-store/themes/customizing-themes/theme-editor/shopify-magic/generate-blocks

**Design system before copy.** Generating a theme is the design. The public steps do not say tokens are chosen before the theme’s copy. In the editor, you already have one theme, including its colors and fonts, before you generate a heading or a block. Global colors and fonts are theme settings, and they do not carry over when you switch themes. https://help.shopify.com/en/manual/online-store/themes/adding-themes

**Section or block model.** "Themes that support theme blocks, including the Horizon family of themes, are the latest theme architecture version." https://help.shopify.com/en/manual/online-store/themes/managing-themes/versions

Sections group into **Header** (header, announcement bar, apps, custom Liquid), **Template** (the page body), and **Footer**. You drag sections and blocks between areas that accept them. https://help.shopify.com/en/manual/online-store/themes/customizing-themes/theme-editor/customizing-sections

"Each template can have up to 25 sections." Blocks sit inside sections. A generated block is added to the block picker and can be placed on compatible sections. https://help.shopify.com/en/manual/online-store/themes/theme-structure/sections-and-blocks and https://help.shopify.com/en/manual/online-store/themes/customizing-themes/theme-editor/shopify-magic/generate-blocks

"Only one theme can be published at any time." https://help.shopify.com/en/manual/online-store/themes/adding-themes

**Who reviews.** "Carefully review the output to ensure it's accurate and meets your standards. It's your responsibility to review all generated text before publishing." https://help.shopify.com/en/manual/shopify-admin/productivity-tools/shopify-magic/tips

"AI-generated code may not always be perfect... You're responsible for reviewing, testing, and ensuring the generated block meets your standards." https://help.shopify.com/en/manual/online-store/themes/customizing-themes/theme-editor/shopify-magic/generate-blocks

"Review suggested changes before you apply them." https://help.shopify.com/en/manual/ai-powered-tools/best-practices

No automated visual critic is named.

**What must not be invented.** Theme generation refuses topics that violate Shopify’s policies. The text-generation page warns that models hallucinate and that you must review before publishing. A specific ban on fake reviews is **not public**. "Shopify prioritizes originality and respects creators' rights, and doesn't support or endorse uploading images from the web or copyright infringement." https://help.shopify.com/en/manual/online-store/themes/adding-themes

**Images.** Media generation edits a file you already have: solid background, or **Generate** from a natural-language prompt, in the file editor. https://help.shopify.com/en/manual/ai-powered-tools/shopify-magic/media-generation

How theme generation attaches a hero photo: **not public**.

**Mobile, header, hero, favicon.** Theme generation runs in the app or a mobile browser, not desktop admin. A block prompt may say "Stack on mobile." The Header area is a real section group. Hero and favicon steps: **not public**.

**Publish gate.** **Try theme** adds the AI theme to **Draft themes**. It is not the live theme. "You can preview any of these themes, but only one theme can be published at any time." Publishing a theme is a separate help page linked from that article. Editor text changes end at **Save**. https://help.shopify.com/en/manual/online-store/themes/adding-themes and https://help.shopify.com/en/manual/online-store/themes/customizing-themes/theme-editor/shopify-magic/generate-content

## Webflow AI site builder

**First input.** Dashboard, **New site**, **AI Site Builder**, describe colors, fonts, purpose, what you do, and the goal, then **Generate**. https://help.webflow.com/hc/en-us/articles/38840145286035-Build-a-site-with-Webflow-s-AI-site-builder

**Design system before copy.** The first Generate builds a structure of pages and sections, not the finished pages. "If you name specific colors, hex codes, or fonts in your description... the AI site builder maps those details to Webflow's theme system rather than copying them exactly." After **Generate site**, you pick or fine-tune a theme (colors, typography, animations, and also "sections, images, buttons, forms, cards, spacing, roundness"). A style guide page is generated with the site. Sites use the Flowkit CSS framework of utility classes and design tokens. Same URL.

So structure is reviewed before full page copy. The theme can be named in the prompt and is applied with the page generation, then adjusted. It is not a locked token step that finishes before any section exists.

**Section or block model.** On the structure: reorder by drag, except "The navigation and footer sections can't be reordered." Delete, duplicate, **Change section** to another type, or add a type. On the canvas preview: add, replace, move up or down, swap styles, or delete a section. One theme updates the whole generated site. Same URL.

**Who reviews.** The human, on the structure and then on the theme preview. AI-generated sites open in the Marketer role by default: "moving sections around, editing copy, swapping images, and tweaking your theme." **Preview** shows the visitor view. No named visual critic. Same URL.

**What must not be invented.** A ban on fake reviews is **not public**. Copy generation is described as a way to avoid lorem ipsum, on a paid plan. https://help.webflow.com/hc/en-us/articles/38323375464723-Generate-and-refine-copy-with-Webflow-AI

**Images.** Choosing a theme updates images. "If you change your theme's image pack, existing images won't be affected. The new image pack is only applied to newly generated pages and sections." The Marketer role can swap images. How an image pack is produced: **not public**. https://help.webflow.com/hc/en-us/articles/38840145286035-Build-a-site-with-Webflow-s-AI-site-builder

**Mobile, header, hero, favicon.** The builder "generates a complete, responsive website." Navigation is a section and cannot be reordered. Hero and favicon: **not public**. Same URL.

**Publish gate.** The AI article says to preview "before you publish" and does not list the publish clicks. **Preview** is the documented pre-publish control. Same URL.

Workspace admins can turn all of Webflow AI off under Workspace settings > General. https://help.webflow.com/hc/en-us/articles/49786374523923-Enable-or-disable-Webflow-AI

## v0

**First input.** Sign in at v0.app, start a chat or a project, describe the idea. Docs examples include "A landing page for a SaaS product with hero section and pricing." v0 may offer to enhance a short prompt into a longer spec. You can also upload a screenshot, a mockup, or a Figma design. https://v0.app/docs/quickstart and https://v0.dev/docs/text-prompting

**Design system before copy.** Default component system is shadcn/ui. A registry can pass components, blocks, and tokens into generation. That is optional context, not a required step before copy. Built-in **Plan Mode** writes a plan and waits for approval before code. https://v0.dev/docs/design-systems and https://v0.dev/docs/instructions

**Section or block model.** **Not public** as named marketing sections you reorder inside one theme. Design mode selects an element and either prompts ("make this a three-column grid") or uses a design panel. https://v0.dev/docs/design-mode

**Who reviews.** Plan Mode waits for your approval. The preview is the other review. You can also edit code. No visual-critic role is named. https://v0.dev/docs/instructions

**What must not be invented.** **Not public.**

**Images.** Upload screenshots or mockups, or import Figma. https://v0.app/docs/quickstart

Generating a photograph: **not public** on the pages opened.

**Mobile, header, hero, favicon.** A custom instruction example is "Always design for mobile screens first, then adapt the layout for larger screens." Hero is only in sample prompts. Header and favicon procedures: **not public**. https://v0.dev/docs/instructions

**Publish gate.** **Publish** in the chat header. First publish: confirm the Vercel project name, choose visibility, confirm the `vercel.app` domain or a custom domain, review commerce mode if it appears, then **Publish**. Later updates: **Publish**, review, **Publish Changes**. Preview deployments do not change the production URL. GitHub-backed publish opens or reuses a pull request, merges it, and still obeys branch protection. https://v0.app/docs/deployments

## Bolt

**First input.** On the Bolt homepage, type in the chatbox and press Enter, or click **Build now**. Optional, before the first prompt on a Teams plan: select a design system. Optional for anyone: **Enhance prompt**, which asks questions in "Help us enhance your prompt." Optional: Plan mode, "Review the plan first." You can also attach files or import Figma or Google Stitch. https://support.bolt.new/building/start-project and https://support.bolt.new/best-practices/prompting-effectively

**Design system before copy.** "If you’re on a Teams plan and have a design system set up, select it before sending your first prompt." It is not required on other plans. https://support.bolt.new/building/start-project

**Section or block model.** **Not public.** The docs talk about files, components, and one-feature-at-a-time prompts, not a section catalog.

**Who reviews.** You review the plan if you used Plan mode. On a paid plan you can run a security audit from the Publish menu "and Bolt automatically fixes any issues it finds." https://support.bolt.new/cloud/hosting/publish

**What must not be invented.** **Not public.**

**Images.** Attach files or import a Figma design. How a photo is generated: **not public**. https://support.bolt.new/building/start-project

**Mobile, header, hero, favicon.** Include the words `mobile app` in the first prompt to get an Expo app. That is an app target, not a responsive website rule. The Bolt mobile client cannot change site visibility, and publish from mobile is always public. Header, hero, and favicon: **not public**. https://support.bolt.new/concepts/supported-technologies

**Publish gate.** Click **Publish** in the top right, then **Publish** again in the menu. Default visibility is public. Private publish is paid-only, and a custom domain cannot be private. "Always use the Publish or Update button in the Publish menu... Prompting Bolt to publish your project decreases your token balance." https://support.bolt.new/cloud/hosting/publish

## Lovable

**First input.** With **Build** selected, type in "Ask Lovable to create…". The quick-start prompt names the business, a hero with a headline and a photo, an interactive menu, hours, a location section, "Use realistic sample content throughout," a visual tone, "Works well on mobile," and "No login or database yet." You can attach a mockup, remix a template, or start from a URL that already carries the prompt. https://docs.lovable.dev/introduction/getting-started

If the workspace has a default design system, the **+** menu "pre-selects it." Choosing one is available on paid plans. Design templates are Business and Enterprise. https://docs.lovable.dev/introduction/dashboard-overview

**Design system before copy.** Optional, and pre-selected when a default exists. The quick start does not require tokens before the sample copy. The sample prompt mixes layout, sample content, and tone in one message. https://docs.lovable.dev/introduction/getting-started

**Section or block model.** Sections are sentences in the prompt. A later prompt can insert one section between two others. There is no public catalog of section types you reorder before generation. Same URL.

**Who reviews.** Before publish, the guide tells you to click every button and link, try the interactive parts, and use the device toggle to cycle to **Mobile view**. You can also select an element in the preview toolbar, or use **Edit text inline**. No automated critic is named. Same URL.

**What must not be invented.** The opposite is in the official prompt: "Use realistic sample content throughout." A ban on fake reviews is **not public**. Same URL.

**Images.** Attach images as a visual reference. The sample prompt asks for a hero photo. How that photo file is produced: **not public**. Same URL.

**Mobile, header, hero, favicon.** Mobile is both a prompt line and a preview toggle you must check. Hero is part of the sample prompt, not a product object. Header and favicon: **not public**. Same URL.

**Publish gate.** Click **Publish**, edit the suggested `lovable.app` address, click **Publish** again. "Your live site is a snapshot." Later edits show in the preview immediately and reach the live URL only when you click **Publish → Publish changes**. Same URL.

## Relume Site Builder

**First input.** A short sitemap prompt: company description, goals, and notes. The doc says to keep it shorter than the sample. The sample asks for a coaches page, a blog, one page per service, and "Keep the pages to 4-8 sections long." You can set a language in that same panel. Then "hit the purple magic button." https://www.relume.ai/resources/docs/building-a-sitemap-with-ai

**Design system before copy.** No. Copy is part of the wireframe pass, which comes after the sitemap. The style guide is a later stage: Design View "applies your Style Guide (including color, typography, and UI elements) across your entire site" after the sitemap and wireframe exist. https://www.relume.io/whats-new/july-2025-release

The product page describes wireframes as "real components un-styled with copy," then a style guide. https://www.relume.io/webflow

**Section or block model.** "Each section of the sitemap is linked directly to a section in the wireframes." Deleting one deletes the other. Section title and description are the section prompt, and they "help inform AI what component to generate." Edit those before wireframes. Add a section from the section panel. Drag sections by the handle. A section can be marked global so copies stay in sync. https://www.relume.ai/resources/docs/building-a-sitemap-with-ai and https://www.relume.ai/resources/docs/how-to-create-and-edit-wireframes-in-the-relume-site-builder

Components come from Relume’s library. The product page says "a built-in design system and component library of 1000+ components." https://www.relume.io/webflow

**Who reviews.** You review the home page first, then click "continue generating pages," then edit names and descriptions before wireframes. You can generate a second sitemap and compare. No automated critic is named. https://www.relume.ai/resources/docs/building-a-sitemap-with-ai

**What must not be invented.** **Not public.** The sitemap prompt is expected to produce "bespoke copywriting for each section."

**Images.** **Not public** on the sitemap doc. Wireframes are described as unstyled on the product page. https://www.relume.io/webflow

**Mobile, header, hero, favicon.** **Not public** on the sitemap doc. Global sections are the closest public mechanism for a repeated header, and the doc’s example is an FAQ, not a header.

**Publish gate.** Relume does not document a live host publish on these pages. The handoff is export. The Webflow app "will create all of the pages, sections and copywriting" and can import a style guide once per Webflow project. A page can be added alone with "Add to page." https://www.relume.ai/resources/docs/using-the-relume-site-builder-import-webflow-app

Going live is then Webflow’s publish, which these Relume pages do not specify.

## What the public procedures agree on

The human almost always types a short brief, not finished page copy. Durable, Hostinger, Shopify theme generation, v0, Bolt, and Lovable start there. Relume, 10Web, Webflow, and Squarespace Blueprint turn that brief into a page-and-section plan the human can edit before the full page exists. Wix Harmony can skip the plan and generate pages, layouts, colors, and starter content together. Claude Code does not plan a multi-page site at all. It publishes one HTML page.

A design system is chosen first only in some products, and only when one already exists: Claude Design’s org system, Bolt Teams, Lovable’s pre-selected default, Webflow’s theme mapped from colors you named, Shopify’s already-installed theme. Relume styles after the wireframe. Durable does not show a token step.

Where a section model exists, it is one theme plus named sections the human can add, delete, or reorder. Webflow refuses to reorder navigation and footer. Shopify separates Header, Template, and Footer, and allows one published theme. Generated copy is starter or sample copy unless a human replaces it. Lovable’s own quick start tells you to ask for realistic sample content. Shopify is the clearest public warning: review generated text before publishing, because the model can be wrong. Wix adds a possible labeling duty and a rights check. Nobody’s opened help page says "never invent a review" in those words.

Images are either attached by the human (Hostinger, Lovable, v0, Bolt, 10Web, Claude Design), taken from a curated or theme image pack (Squarespace, Webflow), or dropped in as starter images (Wix, Durable). Claude Code artifacts cannot load an external image URL.

Publish is a second explicit action in v0, Bolt, Lovable, Framer (after an optional branch), Perplexity (preview, then Publish, then a separate visibility choice), and Shopify (draft theme, then publish). Claude Code’s private URL can appear without a permission prompt. The public share is the human gate.

## Adopt in SpiderCaster

Seven changes. No new seat. No image-generation hand. No vendor theme.

1. Keep the first input a short brief. `brief_read` maps it onto one existing `spidercaster-frame/1` id. If the brief names a section type the frame does not have, `frame_pick` fails. Do not add a 10Web or Relume "section prompt" that content is expected to satisfy by writing new sentences. Those products generate copy from that prompt. This content seat does not.

2. Keep `mold_pick` in the architect seat, before `copy_read`. The mold’s palette, type lead, and nav are the only tokens. Do not add Webflow’s post-generation theme swap. The package has three molds, and a mold already live on another site stays refused.

3. `frame_pick` may reorder only section types the copy already produced. An empty frame id keeps copy order. The sticky header, the mobile sheet, and `favicon.svg` stay renderer-owned. They are not rows in the frame. That matches Webflow locking navigation and footer, and Shopify putting the header in its own group, without inventing a new section type.

4. Do not adopt Lovable’s "Use realistic sample content," Wix starter content, or Durable’s generated images-and-copy pass. `copy_gap` keeps failing when a frame section has no copy file. `check_site` should also fail a testimonial, review, rating, or award string that is not in `copy/`. Shopify’s public rule is the one that fits: the human is responsible for generated text, so this crew does not generate it.

5. Graphics stays local. `asset_list` may list a vault photo or a file with a `spidercaster.py image` receipt. A remote URL still fails. Image generation stays the optional CLI, not a hand. If the hero file is absent, render keeps the letter mark it already knows how to emit.

6. Point the visual seat at what render already emits. `check_site` fails when the sticky header, the mobile sheet, the hero visual, or `favicon.svg` is missing, and it still runs noindex. That is the Framer pre-publish list (content, images, layout, links, responsive behavior) and the Lovable mobile check, encoded as a stop, not as a new reviewer.

7. Leave publish as two steps. `ticket_write` is the preview record, noindex still on. `library bind --live` is the only live click, and it still refuses a mold that is already live. That is the same shape as v0 and Lovable (preview, then a second Publish) and Perplexity (publishing is not the same act as making it public). Do not add a chat button that publishes.
