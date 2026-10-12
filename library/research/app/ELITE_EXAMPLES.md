# Elite public examples for a fast brochure

Read 2026-10-01 by opening the live URLs below. Search snippets were not used as evidence. No HTML or CSS from those sites was saved. Nothing here is a theme, a class name, or a markup recipe. Stripe and Vercel were not opened; Linear loaded, so that marketing slot is filled.

Harbor notes are only what is in `stage/harbor/out/index.html` on this date. Menu prices on that file are not repeated here. No reviews were on that file, and none are invented.

## Linear marketing

URL: https://linear.app/

Opened. Skip link reads "Skip to content". The visible title is "The product development system for teams and agents". The line under it is "Purpose-built for planning and building products. Designed for the AI era." A small "New" chip links to Loops. There is no single hero button at the top. Further down, section links read "Learn more". The closing row reads "Built for the future. Available today." and the controls are "Get started", "Contact sales", "Open app", and "Download".

Image treatment: large product screenshots (an issue, boards, a timeline), served already scaled from their image host, plus small avatars. The pictures show the product in use. They are not a short cropped photo behind the title.

Behavior: the first screen names the job in one sentence and shows the thing already working, with one primary next step. The brand name is not the heading.

## Astro marketing

URL: https://astro.build/

Opened. Skip link reads "Skip to content". A thin banner says "Astro 7.3" and "Available now!". The heading is "The web framework for content-driven websites". The support line says Astro powers fast marketing sites, blogs, and shops. The button is "Get Started" and goes to the docs. Beside it is the command `npm create astro@latest`.

Image treatment: the hero background is a webp. Later, the images section labels one asset "800px • WEBP" and another "3600px • PNG". A demo product card shows a cap photo, the name "Snapback Cap", a price printed on that card, and the button "Add to cart". That price is theirs, not Harbor's. Theme cards are small previews with "View Theme".

Behavior: one action ("Get Started"), and pictures are already a modern format at a stated pixel size instead of one unscaled file.

## Astro image docs

URL: https://docs.astro.build/en/guides/images/

Opened. This is the docs page, not a brochure. Skip link reads "Skip to content". The heading is "Images". There is no hero and no call-to-action button. A small related-recipe picture is a webp.

What the page states, as behavior only: keep local pictures where the build can resize them; files left in a public folder are copied unchanged; every content picture needs a description, and a decorative picture gets an empty description; the rendered picture carries width and height so the layout does not jump; a responsive picture offers more than one width; the default on their generated pictures is lazy and async decode, which is the wrong default for the first picture on a brochure.

Behavior: describe the hero picture, or mark it decorative, and reserve a box that matches the size actually painted. Do not lazy-load that first picture.

## Eleventy image docs

URL: https://www.11ty.dev/docs/plugins/image/

Opened. Skip links read "Skip to navigation" and "Skip to main content". The heading is "Image". Stable version on the page is 3.1.6. There is no hero photograph and no brochure button. A video link reads "Optimize your Images with Eleventy Image". The left column is a docs nav. Community links use small square screenshots.

What the page states, as behavior only: at build time, write width and height so the aspect ratio holds; emit more than one size and more than one format; do not enlarge a raster picture past its real pixels; cache repeats; while serving locally, optimize a picture when the browser asks for it instead of processing every picture before the page can be viewed. The options text names webp and jpeg as the usual pair, and "auto" width as "keep the original width".

Behavior: generate the smaller sizes ahead of time, keep the real aspect ratio, and never upscale the tea-room photo.

## web.dev case studies index

URL: https://web.dev/case-studies

Opened, but thin. Skip link reads "Skip to main content". A header image (`case-studies-header.png`) sits above the heading "Case studies" and the sentence "Learn why and how other developers have used the web to create amazing web experiences for their users." No study cards, no button label, and no case-study body rendered in that fetch. Not used for a behavior.

## web.dev case study

URL: https://web.dev/case-studies/nuvemshop

Opened. Skip link reads "Skip to main content". The heading is "How Nuvemshop's image prioritization strategy led to a 68% improvement in LCP and 8.9% more conversions". There is no hero button. Author portraits are small photos. Published date on the page is June 24, 2026.

Figures the article itself prints: LCP health from 57% to 96% in one year; Core Web Vitals pass rate from 48% to 72%; on one mobile organic cohort, conversion up 8.9% and cart engagement up 8.4%. Those figures are Nuvemshop's, not a Harbor result.

Image treatment, stated in the article and not copied: the first section must paint immediately, with no transition that delays when the browser counts it as visible; the first image in that section is not lazy-loaded; high priority is set on that one image only, because marking every image high priority cancels the signal. Their example description is "Featured product", and the file they name is a webp. They also say they would not cache a price or a stock count if a stale copy could mislead a buyer.

Behavior: the first picture paints at once, is not lazy, and is the only picture marked high priority. Later pictures can wait.

## USWDS landing template

URL: https://designsystem.digital.gov/templates/landing-page/

Opened. This is an agency first-impression template, not a restaurant theme and not a tea-room theme. Skip link reads "Skip to main content". An official-site banner sits above the page title "Landing page" and the line "Provide someone’s first impression of your agency or program." The about heading is "About the landing page template". A preview image of the layout is linked as "Demo Landing page".

Inside the documented hero, the heading is "Hero callout: Bring attention to a project priority", with two short sentences of support, and the button label is "Call to action". The next heading is "A tagline highlights your approach". A graphic list uses small circular images beside short headings, including "Stick to 6 or fewer words." A later section button is also "Call to action". Guidance on the same page says the verb should be active ("Get in touch", "Learn more"), a landing page should not grow a form or a side navigation just to fill the template, unused blocks should be removed, and a one-task page may drop the header so nothing competes with that task. Graphic headings stay to about six words; the body under them stays to about thirty words.

Behavior: one priority, a short support line, one active-verb button, and no extra block that the visitor did not need. Do not copy the template.

## GOV.UK contact pattern (tea-room visit facts)

URL: https://design-system.service.gov.uk/patterns/contact-a-department-or-service-team/

Opened. This is the public pattern for a phone, opening hours, and an address in one place. It is not a restaurant theme. Skip link reads "Skip to main content". The heading is "Help users to Contact a department or service team". The line under it is "Give users contact information within your service." There is no hero and no hero button. Links on the page include "Open this example in a new tab", "Find out about call charges", and, inside the longer example, "Speak to an adviser now". The footer link is "Back to top".

The short example heading is "Get help with your application". That example is a list: a phone line, then one hours line, "Monday to Friday, 9am to 5pm (except public holidays)". The phone number in the example is a pattern placeholder, not a Harbor number. The longer example uses small headings in this order: Phone, Email, Webchat, Address, Social media. The address is stacked on separate lines (street, city, postcode). Social channels are last, with a warning not to put personal details where others can see them. Hours guidance says to use a time range, and to name exceptions (a closed day, a bank holiday, or a split day) in that same place. It also says to tell people how long a reply usually takes. One or two lines of contact stay in the page body. A disclosure is only for a long contact block. An inset example, headed "Talk to an advisor", still keeps the phone and the hours together.

The page says the pattern was tested in two rounds with 12 participants, from government campaign and courts work. That is their research, not a Harbor test.

Behavior for a tea room: one visit block lists the phone and the opening hours together, stacks the address, and names the closed day there. Do not hide a two-line fact. Do not copy their markup.

## What SpiderCaster can adopt

These are behaviors, not code and not a look.

- The first heading says what the place does. The name can sit in the title and the header. Linear and the Astro homepage both do this. The USWDS hero is a priority callout plus two short sentences.
- One primary control, labeled as a verb that matches the task ("See the menu", "Plan a visit"), not the noun of a section. USWDS states the active-verb rule. Linear's closing row is four distinct tasks, which is more than a one-page tea room needs; take the labeling, not the count.
- The first picture paints immediately, is not lazy-loaded, and is the only high-priority image. That is the Nuvemshop case study. Harbor's hero image already carries high priority and is not lazy. Keep that. Do not spread high priority onto later pictures.
- Offer a smaller size and a modern format, with width and height that match the painted box, and do not upscale. That is the Astro and Eleventy docs. A short cover crop that ignores the declared 1600 by 900 box fails the "reserve the real box" rule even when the attributes are present.
- Describe the picture, or leave the description empty if it is decoration. The Astro docs require one or the other. A business name is neither.
- Phone, hours, and address are one visit block. The closed day is in that block. The GOV.UK pattern is the source. A two-line fact stays visible.
- A skip link is the first control. Every full page above had one, except that this is a behavior to add, not a visual theme.
- Do not add a form, a review row, or a side navigation to fill space. USWDS says to remove unused pieces. Harbor's contact section already has no form. Leave it that way unless a real ask needs one.
- Do not cache or invent a price. The case study flags stale prices as a trust failure. Harbor's menu prices stay the ones already in the draft.

## Harbor draft, differences that are still true

Source: `stage/harbor/out/index.html` only. Five differences.

1. The only `h1` is "Harbor Tea Room". The job line, "A quiet tea room that seats walk-ins by the water.", is a paragraph under it. Linear and the Astro homepage put the job in the heading.

2. The only hero control is a button labeled "Contact" that jumps to `#contact`. The USWDS landing guidance asks for an active verb. The contact section under that button has no form. It shows the phone as plain text, "(555) 014-2288", and one address line, "14 Harbor Lane".

3. The hero is one PNG, `assets/hero.png`, with alt text "Harbor Tea Room", width 1600 and height 900, high priority, and async decode. There is no second size and no second format. The style paints that image 168px tall, and 320px tall from 861px up, with a cover crop. The reserved ratio and the painted crop do not match. High priority on this single first image already matches the case study; that part is not a gap.

4. Hours are a later section, not in the contact block. That section says "Open Tuesday to Sunday, 8am to 6pm." and "Closed Mondays." The GOV.UK pattern keeps the number and those hours in one list. Page order after the hero is an about sentence with no heading ("Loose-leaf, brewed to order; decaf after 4pm on request."), then Contact, then Hours, then Menu. The nav order is Contact, Hours, Menu. The about block also has an empty decorative panel and no picture.

5. There is no skip link. The header starts at the brand link. Linear, both Astro pages, Eleventy, both web.dev pages, USWDS, and GOV.UK each showed a skip link.
