# Studio discussion

Date: 2026-10-08. The twelve screen reports are in `library/research/ui/`. Subagents do not talk to each other. This note is the chair's reconciliation. A conflict is decided here. The studio code follows this note.

## What everyone agreed

One stdlib page on `127.0.0.1`. No React, Tailwind, shadcn, chat, or new package. No `library bind --live`. `warmth-authority` is not a paint choice and is not bound again. Projects are only `projects/demo-local` and `projects/bench-harbor-tearoom`. Fleet names are a blocked list. A fail stays a fail. `grey_tile` stays skip. The studio is not the customer site. Built pages are judged by `check --project --expect-noindex` and `visit`.

## Conflicts and the decision

1. Plan Room says Accept writes `structure.json` and nothing paints from that file. Mold Room's Paint runs `compose` again, which plans from copy and replaces the file. Decision: `compose --structure PATH` paints only when that file is a drop or reorder of the fresh plan (same schema, frame, mold, pages, and section objects). An added section, a changed id, or a cross-page move refuses and writes no HTML. The studio Plan button writes `sites/<project>-studio-plan` only. Paint writes `sites/<project>-studio`.

2. Domains said Compose local writes `sites/<project>-compose`. That folder already holds a checked demo-local compose. Decision: the studio does not write `sites/demo-local`, `sites/demo-local-compose`, `sites/demo-local-ai`, or `sites/bench-harbor-tearoom`. Those stay readable. New HTML goes to `sites/<project>-studio`.

3. Parts Shelf would Apply onto those existing indexes. Decision: Apply and Replace write only `sites/<project>-studio/index.html`, and only for the six kinds header, hero, card, faq, cta, and footer. The result line says appended or swapped. Check runs after a zero exit. There is no undo.

4. SEO Desk's Write sitemap runs `build --indexable --host`, which drops composed parts, and Domains refuses a fleet host. Decision: the desk shows noindex, `robots.txt`, sitemap absent or present, the description source, and heading order. The studio does not clear noindex and does not write a sitemap. The CLI line stays on the page as text.

5. Crew Board's Run crew calls `library_bind`, which writes a draft ledger row even when live is false. Decision: the board lists the seven seats as `not run`. Run crew is refused. The studio does not write `library/ledger.json`.

6. Shell wants four doors and an empty frame on the desk. The other ten reports each want a screen. Decision: the desk opens Plan, Parts, Preview, and Check, and the same page lists Copy, Mold, Mobile, SEO, Crew, Domains, and Score. Opening the desk runs no command. Frame and mold are chosen in Plan, not on the desk.

7. Scorecard says SKIP blocks a group word of PASS. Check Board says SKIP does not stop Next. Both stand. A group word is FAIL, then WARN, then SKIP, then PASS. Next is about fails only. `grey_tile` stays skip. The card is not a new scale and not a rank.

8. Preview and Mobile both serve the built folder. Decision: one preview process, bound to `127.0.0.1`, started at port 4300 so it does not take the studio port. The address shown is `http://127.0.0.1:` plus the port actually bound. Serve is refused when the page is not noindex, when `sitemap.xml` is present, or when `robots.txt` exists and does not disallow `/`. A missing `robots.txt` is shown and does not refuse. The 1280 frame sits in a slot that scrolls. The studio page does not grow to 1280.

9. Copy Desk is read-only. A missing frame type is the word missing and "not in copy". The brief is context. It is not written into a section.

## Build order the studio will run

Plan `demo-local` with `welcome-scroll` and `discover-grid`. Accept that file with no drops. Paint `sites/demo-local-studio`. Plan `bench-harbor-tearoom` with `hours-stack` and `discover-grid`. Accept. Paint `sites/bench-harbor-tearoom-studio`. Check and visit both. Rate them from the checker rows. Fix the engine only when a row fails.
