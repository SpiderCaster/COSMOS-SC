Preview Room expert

## 1. Role

This screen shows one built folder on this PC, inside a phone-width frame, and says whether that folder is a staged site or a live domain. The one job is looking. It serves 127.0.0.1 only, labels the site noindex, and never opens a public URL.

## 2. Evidence

Read on 2026-10-08: `library/research/ui/BRIEF.md`, `lib/serve.py`, `library/research/competitors/squarespace.md`, plus the serve, visit, check, render, compose, seo pack, library bind, and crew paths those files point at. No server was started. Nothing was published. `library bind --live` was not run.

`lib/serve.py` `serve` binds `ThreadingTCPServer` to `127.0.0.1` only. The port starts at 4173 and steps through at most 20 ports (4173 through 4192). The handler is `SimpleHTTPRequestHandler` rooted at the site folder. It adds MIME types. It does not add a noindex header, a phone frame, or a studio page. `spidercaster.py` `serve` refuses a folder with no `index.html` (`no index.html in {site}; run a build first`). It then prints `preview: http://localhost:{port}` and waits until Ctrl+C. The help line says "preview a built site on localhost." The socket is 127.0.0.1. The printed name is localhost. Whether that name opens the socket on this Windows PC is not measured. The command does not open a browser. It has no host argument and no public address.

`visit` reads `index.html` from disk. Static mode checks a header, `id="main"`, hash links, a viewport meta, and fixed widths. When Playwright launches a browser, mode becomes rendered and the same file is opened with `Path.as_uri()` at 390x800 and 1280x800. `is_mobile` and `has_touch` are false. Any `http://` or `https://` request is aborted. A missing browser leaves mode static and is not a failure. Visit does not click the menu and does not look for the phone bar. A rendered phone-bar proof is not public.

`check` phone widths are 360x740, 390x844, and 412x915. The desktop width is 1280x800. The file names those three phone widths small Android, iPhone 14, and 412 Android. Those are labels in `lib/check.py`, not a device lab. `type_floor` and contrast also run at 1280. `tap_target` and the mobile rows run at the three phone widths. Body text floor is 18px, other text 16px, tap box 44px, contrast 4.5:1, large text 3:1. `sideways_scroll` fails a box that ends past the viewport. `mobile_nav_drawer` requires a 44px menu button and a drawer that opens and closes when there are more than four primary nav links. `phone_bar` is a row only when `index.html` has an anchor with class `phone-bar`. Pass means the `tel:` digits match the link text and there are at least seven digits. No anchor means no row. The noindex row looks for `name="robots" content="noindex` in the HTML. It does not read `robots.txt`.

The page stylesheet in `lib/render.py` hides `.phone-bar` until `@media(max-width:860px)`, then shows it fixed, full width inside 16px gutters, at least 48px tall. `body.nav-open` hides it. The wide sheet starts at `@media(min-width:861px)`. All three checker phone widths sit inside the 860px sheet. 1280 does not. `.nav-toggle` is hidden until that same 860px sheet, then it is 44 by 44. `_phone_bar` writes the anchor only from a contact section phone already in the page data, and only when that string has at least seven digits. The label is that string. No country code is added.

`sites/bench-harbor-tearoom/index.html` has the noindex meta, the comment `SpiderCaster: noindex until approved`, and `<a class="phone-bar" href="tel:5550142288">(555) 014-2288</a>`. The number is the line in `projects/bench-harbor-tearoom/copy/contact.md`. `sites/demo-local-compose/index.html` has the same meta and comment and the phone-bar CSS, and no phone-bar anchor. Its `robots.txt` is `User-agent: *` and `Disallow: /`. No `sitemap.xml` is under `sites/`. `report.json` has `"noindex": true` in `sites/demo-local`, `sites/demo-local-ai`, `sites/demo-local-compose`, `sites/bench-harbor-tearoom`, and `sites/assembled`. Harbor and the other three besides `demo-local-compose` have no `robots.txt` in that tree. The meta can be noindex while the crawl file is absent. `compose` calls `write_pack` with `indexable=False`. A normal `build` does that too. `build --indexable` drops the meta and the comment. A sitemap is written only when that flag is on, the HTML is not noindex, and `--host` is an origin with no path. The canonical this renderer writes is the page filename, including `index.html`, not an absolute domain.

`library/ledger.json` has one live row: site `movelixir.com`, mold `warmth-authority`, `live` true. `demo-hero.example`, `demo-stage.example`, and `harbor-test.example` are `live` false. `library bind` without `--live` prints draft. With `--live` it refuses a mold or vendor frame already live on another site. Crew sets `live` false and writes `crew-ticket.json` with `Keith click. This run does not deploy.` The preview does not join a folder to `movelixir.com` unless a file in that folder already says that name.

Squarespace Blueprint, read from `library/research/competitors/squarespace.md`, shows a generated multi-page site that already has copy, imagery, and styling, then edit, then publish. Publish connects a domain. The product says you preview, edit, and publish only when it feels right. That is approval of a site that already exists, not of a plan before HTML. Trial sites are private and are not indexed. Only a paid site can be set Public. The FAQ says generated sites are responsive and that the mobile layout can be adjusted on its own. That is a product claim. Breakpoints, a body size, a tap size, and a contrast ratio are not public. Fluid Engine keeps a second arrangement for mobile. Blueprint AI Builder and Blueprint AI Templates do not run on mobile devices. That is an authoring limit. No visual-critic role is named. Squarespace does not hand over a static folder and does not document a measured phone frame. This room does not copy the prompt, the second layout, the Public switch, or a hosted preview.

## 3. Screen

The person acts in this order. The studio chrome is outside the page. The page inside the frame is not edited.

1. Folder. A path field and a Choose button. The only folders offered by name are built folders that already have `index.html` and the noindex meta. Known staged builds are `sites/demo-local`, `sites/demo-local-compose`, and `sites/bench-harbor-tearoom`. `compose --plan` writes `structure.json` and no HTML. That folder is refused. A fleet domain is refused. There is no copy pack here for those domains, and this screen does not invent pages.

2. Status. A text line, not a link. It reads the chosen `index.html`, `report.json`, `robots.txt`, `sitemap.xml`, and `crew-ticket.json` if that ticket is in the folder. It also reads the ledger as text. The staged line is `NOINDEX` and `Staged`. The live line, kept separate, is `Live on the ledger: movelixir.com, mold warmth-authority`. That name is not an anchor. The room does not fetch it.

3. Serve. One button. It starts `python spidercaster.py serve` on that folder. The address shown is `http://127.0.0.1:` plus the port the process actually bound. The word localhost is not the address shown. Serve is refused when the meta robots content is missing or is not noindex, when `sitemap.xml` is present, when `robots.txt` exists and does not disallow `/`, or when the folder's own ticket or report names a ledger site whose `live` value is true. A missing `robots.txt` does not refuse Serve. The status line says the crawl file is absent and does not call that a pass. `sites/bench-harbor-tearoom` is that case: meta noindex, no `robots.txt`.

4. Phone frame. Four buttons: 360, 390, 412, and 1280. Default is 390. The built page sits in an iframe of that width. Heights next to those widths are the checker heights 740, 844, and 915, and 800 for 1280. The iframe source is `http://127.0.0.1:{port}/` plus the page filename. It is never `https://`, never a ledger host, and never a sitemap `loc`. A label on the frame reads `NOINDEX` and `Staged`. There is no fake browser bar and no painted public domain. 360, 390, and 412 are inside the page's 860px sheet, so the menu button can show, and the phone bar can show when the anchor exists. 1280 is the wide sheet: the stylesheet hides the phone bar and the menu button. Whether the iframe's CSS width equals the layout viewport is not measured until Check or Visit says so.

5. Look. The person uses the page's own Menu button inside the frame. The studio has no second Menu. The phone bar, when the page has one, is the page's own `tel:` link. The studio does not dial it and does not rewrite the number.

6. Check. One button. It runs `python spidercaster.py check {folder} --expect-noindex`. If the folder was built from `projects/demo-local` or `projects/bench-harbor-tearoom`, it also passes `--project` for that directory. The stdout is shown as the command printed it. A fail stays a fail.

7. Visit. One button. It runs `python spidercaster.py visit {folder}`. The mode line is shown. `static` means the 390 and 1280 windows were not measured. `rendered` means those two windows were. Visit's 390 height is 800, not the frame's 844. The screen does not call those the same test. It does not install Playwright.

8. Stop. One button. It ends the serve process. It does not bind, upload, or change the folder.

Refused, and not shown as enabled controls: Publish, Open domain, Bind live, Indexable, Host, Edit copy, Add page, and any address that is not `http://127.0.0.1`. Also refused: `library bind --live`, `build --indexable`, a second mold bind for `warmth-authority`, and opening `movelixir.com`.

## 4. Already here

`python spidercaster.py serve {folder}` is the preview. It is loopback-only in `lib/serve.py`, and the CLI text still says localhost. `python spidercaster.py check {folder} --expect-noindex` is the phone-width judgment, including drawer, tap, type, contrast, sideways overflow, and the phone-bar row when the anchor exists. `python spidercaster.py visit {folder}` is the rendered look at 390 and 1280, and it refuses network URLs. Noindex is the meta tag and the HTML comment from `render.assemble` (default `noindex=True`), `report.json` `"noindex": true`, and, when `write_pack` ran, `robots.txt` with `Disallow: /` and no sitemap. The phone bar is `_phone_bar` in `lib/render.py` and the `.phone-bar` rules in the page CSS. The live mark is `library bind --live` and the ledger. Crew does not publish. There is no studio page, no phone frame, and no control that rewrites the printed localhost line to 127.0.0.1.

## 5. Proposal

The smallest surface is one local HTML page served by the standard library on 127.0.0.1, beside the existing serve process, not inside it. Do not edit `lib/serve.py` or the renderer. Do not install a package. Do not add React, Tailwind, or a chat control.

The studio page starts `python spidercaster.py serve` and reads the port from that process. It shows `http://127.0.0.1` and that port. The phone frame is an iframe at 360, 390, 412, or 1280, sourced from that same address. Check and Visit are the two existing commands, run when those buttons are used, with their text left intact. Stop closes the serve process. The studio page carries `<meta name="robots" content="noindex, nofollow">` and does not write a sitemap. Its only heading is `Staged preview`. Its buttons are Choose, Serve, 360, 390, 412, 1280, Check, Visit, and Stop. It does not call `compose`, `build`, `refine`, `bind`, or the image command.

The iframe loads only the built folder's own pages. Relative links stay on 127.0.0.1. The five built indexes under `sites/` have no `http://` or `https://` in `href` or `src`. `schema.org` inside the existing JSON-LD is a type context, not a page this room opens. If a later page contains an absolute web URL, the room still does not offer it as a control. Following it would leave the job. That case is refused by not putting such a URL in the studio chrome. A click inside an already-built page is the page's own link. None of the indexes read here have one.

## 6. 4Cs+ test

The studio and the built page are judged apart. Unmeasured studio paint is not public.

Copy. The studio writes no sentence onto the site. Frame labels are the status words and the width numbers above. Visible claims on the page must already be in that project's `copy/`. Check with `--project` is the copy test, and only for `projects/demo-local` and `projects/bench-harbor-tearoom`. The harbor phone bar is the contact line already in copy. A folder with no phone anchor gets no phone-bar pass and no invented number.

Contrast. The built page is the checker's contrast row at 360, 390, 412, and 1280. The studio's own contrast is not measured. Not public.

Chrome. The built page is judged by the checker floors already in the brief: body 18px, chrome 16px, tap 44px, sticky header, skip link, hero visual, favicon. The phone bar's own rule is taller than 44px (`min-height:48px`) and is hidden while the drawer is open. The studio buttons are specified at 44px or taller, with body text 18px and chrome 16px. That studio size is not measured. Not public. Studio chrome sits outside the iframe so it does not cover the page skip link, the sticky header, or the phone bar. The studio is not a second sticky header on the site.

Crawl. The built page must keep one h1, the relative canonical, WebSite JSON-LD, no aggregateRating, and a description, as Check already scores them. The studio page is a tool shell: one heading, `Staged preview`, no second WebSite object, no public canonical, no sitemap. Its noindex meta is the label. Being on 127.0.0.1 is what keeps a public crawler off it. The meta is what still labels the files if they are copied later. Both are required. A missing `robots.txt` is shown and is not a crawl-file pass. Check's noindex row can still pass on the meta alone. The room must not hide that split.

Plus. On a studio window at 360, 390, and 412, the studio document itself must not scroll sideways. The 1280 frame sits in a scroll box so the studio body does not grow to 1280. That studio overflow is not measured. Not public. The built page's sideways test is `sideways_scroll` at 360, 390, and 412, plus Visit when mode is rendered: `scrollWidth` greater than `clientWidth` plus 1 fails, at 390x800 and 1280x800. The drawer test is `mobile_nav_drawer`, not a studio script clicking Menu. The person may open Menu inside the frame. That look is not a measured pass. Visit's header check is a visible header at those two windows, with no phone user-agent. A static Visit does not prove the phone frame.

## 7. Risks

Showing the CLI string `http://localhost:{port}` could leave the 127.0.0.1 socket. That outcome is not measured. The room shows the numeric address and does not open a browser.

Stamping `NOINDEX` on a folder that was built with `--indexable` would hide an indexable page. Serve is refused for that folder. Serving a folder that contains `sitemap.xml` would put absolute origins on disk next to the preview. Serve is refused. Writing a fake domain into a device bezel would make a staged folder look like a live site. The frame does not do that.

Putting `movelixir.com` in an anchor, or treating a local folder as that domain because the mold feels similar, would publish by click. The ledger line stays plain text. `warmth-authority` is not bound from this room.

A missing `robots.txt` next to a noindex meta is a real gap on harbor and on three other built folders. Calling Check's noindex pass a full crawl pass would hide it. The status line keeps them apart.

Visit in static mode must not be labeled as a measured phone layout. A rendered pass at 390x800 must not be labeled as the checker's 390x844 frame. The phone bar has no rendered measurement in Visit. Not public.

`contenteditable`, a refine box, or a prompt would invent copy or spend a token path. They are not on this screen. `compose` from this screen would write HTML the person had not asked to look at. It is not a button.

Binding `0.0.0.0`, scanning past the existing twenty ports, or following a sitemap `loc` would leave the machine. The room does not add those. The site process still has no password. Loopback is the fence. Whether another session on this PC can open the port is not measured. Not public.

Running `library bind --live` from a preview button would mark a domain live and can refuse, or steal, a mold that is already live. This screen has no such button. This note did not run it.
