# Elite public pages at phone width

Read 2026-10-01 in Chrome at a 390 by 844 CSS-pixel phone layout, touch, no zoom lock. Search snippets were not used. No HTML or CSS from these sites was saved. Nothing here is a theme, a class name, or a markup recipe.

Every page below returned the article or the marketing page. None was a login wall. A "Sign in" or "Log in" control in a header is not a wall. No password field was on screen. Page scroll width matched the layout width (390, except the responsive article below, which measured 414). Nothing stuck out sideways past the screen.

## Linear

URL: https://linear.app/

Opened. One column. The title is "The product development system for teams and agents" at 38px type, line height about 42px. The line under it is 15px: "Purpose-built for planning and building products. Designed for the AI era." There is no hero photograph. Under the type, a product picture is cut off by the bottom of the screen. That picture is not a second column of the page.

The header is fixed and was still at the top after a scroll. It is one short bar: the name, "Log in", a "Sign up" pill (about 73 by 32, 13px type), and an icon button on the right (about 64 by 64) with no text name. "Sign up" is the only button label in that bar. The page does not show a full-width button under the title.

## Stripe

URL: https://stripe.com/

Opened. One column of type. The title is "Financial infrastructure to grow your revenue." at 34px. A small line above it is 12px. The support copy lower down is 22px. The hero graphic is a full-bleed color wash behind the title, taller than the type, with no photo beside the title. A logo row sits under the buttons and is cropped at the screen edges. The page itself does not scroll sideways.

Buttons, stacked and full width of the column: "Get started" (about 358 by 44, 16px type), then "Sign up with Google" (same width and height). The header is the wordmark and a menu button labeled "Toggle navigation menu" (40 by 40). That header is not sticky. After a scroll it had left the screen.

## Vercel

URL: https://vercel.com/

Opened. One column. A thin line at the top reads "Ship 26 is coming to SF" and "Get your ticket" at 14px. Under that, one centered mark about 195px square, on a full-width graphic area. The title "Agentic Infrastructure" is 48px, line height 56px. The line under it is 16px: "For coding agents".

Buttons, stacked and full width of the column, 16px type: "Deploy now" (about 342 by 40), then "Talk to sales" (about 342 by 40). The header is sticky and stayed at the top after a scroll. It shows the mark and a button labeled "Open menu" (44 by 44). A logo row at the bottom of the first screen is cropped at the edges.

## GOV.UK header component

URL: https://design-system.service.gov.uk/components/header/

Opened. One column. A cookie notice covers the top. Its buttons are stacked and full width: "Accept analytics cookies" and "Reject analytics cookies", with "View cookies" as a text link under them. Notice type is 19px. The title under that is 21px.

The site header is not sticky. It scrolls away. On this width it stacks: the service name "Design System" at about 31px, a search field, then a "Menu" control. That Menu control is about 78 by 25, which is short. There is no hero image. The page title "GOV.UK header" is 32px, line height 35px. The sentence under it is 19px. A breadcrumb ("Home", "Components") is one line, not a second column.

## USWDS header component

URL: https://designsystem.digital.gov/components/header/

Opened. One column. No hero image. A full-width official-site bar is 12px type, about 48px tall, and includes "Here's how you know". Under it, a short bar has the name and a "MENU" button on the right (about 62 by 48). That bar is not sticky. After a scroll it had left the screen.

The title "Header" is 40px, line height 48px. The lead under it is 20px. Body copy is 16px. The lead says a header helps users identify where they are and reach the main sections. No second column, and no hero button.

## Astro image docs

URL: https://docs.astro.build/en/guides/images/

Opened. This is a docs page, not a brochure. One column. No hero image and no hero button. The title "Images" is 35px, line height 42px. Body copy is 16px and uses the column width (about 358 of 390). "On this page" is a small control on the same line as "Overview", not a side column.

The header is fixed, about 56px tall, and stayed after a scroll. It shows "Astro", "Docs", a "Search" button (about 30 by 40), and a "Menu" button (about 32 by 32).

## Eleventy docs

URL: https://www.11ty.dev/docs/

Opened. One column. No hero image. Skip links read "Skip to navigation" and "Skip to main content". The header does not collapse to one menu button. A row shows "Get Started", "Blog", and "Community" (those links are about 21px tall), plus a version chip "v3.1.6", a search field, and "GitHub". Under that, docs links stack full width, including "Introduction", "Community", "Guide", "Plugins", and "Services". The header is not sticky. It is tall and scrolls away.

The title "Get Started" is about 48px and sits well below the header. The note under it is 18px.

## web.dev tap targets

URL: https://web.dev/articles/accessible-tap-targets

Opened. One column. No hero image and no hero button. The title "Accessible tap targets" is 48px, line height 60px. Body type elsewhere on these web.dev articles is 16px. An "On this page" list stacks under the title. Author photos are small circles about 65px, with the name beside the photo. Two names can sit on one line. That is a byline, not a two-column article.

The header is fixed and stayed after a scroll. It is two rows, about 125px tall once scrolled: an "Open menu" button (about 40 by 48), the logo, an "Open search" button (about 24 by 24), and "Sign in", then the section name "Resources" at 20px. A breadcrumb is 13px. "Was this helpful?" sits above the title at 13px.

The article's own text, on this page, says a minimum touch target is around 48 device-independent pixels when the mobile viewport is set, and that targets should be spaced about 8 pixels apart. The page says it was last updated 2020-03-31.

## web.dev responsive design

URL: https://web.dev/articles/responsive-web-design-basics

Opened. Same phone context, but this page's layout width measured 414, not 390. Still one column, and scroll width matched that 414. Same header behavior as the tap-target article: fixed, "Open menu", "Open search", "Sign in", then "Articles". The title "Responsive web design basics" is 48px, line height 60px, and wraps inside the column. No hero image. "On this page" is a stacked list, including "Set the viewport" and "Size content to the viewport". Not a login wall.

## What the mobile renderer should adopt

At most these six. Do not add reviews. Do not invent menu items. The menu button opens whatever sections the page already has.

1. One column at phone width. The page does not scroll sideways. Title, support line, and actions stack in that column, with a small side inset (these pages used about 16px).

2. One primary button under the title, full width of the column, with a short label such as "Get started" or "Deploy now". A second action stacks under it. Do not put the button beside the title. Docs pages with no action do not grow a fake hero button.

3. A short header that stays on screen (fixed or sticky), with the site name and one menu button. Linear, Vercel, Astro, and web.dev kept that bar after a scroll. Do not leave the whole link list in the bar. Eleventy did, and the bar was tall and scrolled away.

4. One hero shape, or none. A centered mark above the title (Vercel), a full-bleed graphic behind the title (Stripe), or a product picture below the title (Linear). Docs pages had no hero image. Do not place a photo in a second column next to the title.

5. Title type about 32 to 48px. Body type 16px. A support line may be 15 to 22px. The title wraps inside the column. web.dev's title line height (60 on 48) is looser than Linear (about 42 on 38) or GOV.UK (35 on 32).

6. Make the menu button and the primary button about 44 to 48px on the short side, with about 8px between stacked targets. That is what the tap-target article says, and it matches the larger controls that were measured (web.dev menu 48px tall, USWDS MENU 48px tall, Vercel menu 44px, Stripe "Get started" 44px tall). Do not copy the short ones: GOV.UK "Menu" was 25px tall, web.dev search was 24px, and Eleventy's text links were about 21px tall.
