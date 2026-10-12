# Mobile resources

Resource finder for a phone-layout pass. Read `library/resources/INDEX.md` and the seven `library/seats/*/SKILL.md` Mobile sections. Waited for `library/resources/MOBILE.md` and `library/rules/mobile.json`. Did not edit Python. Did not publish. Did not build a site. Did not run crew. Did not open key files.

Second check: 2026-10-01 16:13:40 -05:00. `library/resources/MOBILE.md` was absent. `library/rules/` was absent, so `library/rules/mobile.json` was absent. `INDEX.md` (4544 bytes, last written 2026-10-01 15:03:10) names hands plus the package mold and frame paths. It does not name a mobile card or a mobile rule file.

## Molds

Three package molds under `library/molds/`. None lists an `hours` or `menu` section. None has a mobile field. A phone pass can rely on palette, type-lead, nav, and template from these files. It cannot rely on a mold to keep hours or menu.

| id | origin | parents | palette | type_lead | nav | template | sections |
| --- | --- | --- | --- | --- | --- | --- | --- |
| warmth-authority | scratch | none | #c8923e | serif | segmented | editorial | hero, about, features, faq, contact |
| discover-grid | mutate | warmth-authority | #2a6f8f | sans | top-bar | modern | hero, features, steps, faq, contact |
| clarify-mix | mix | warmth-authority, discover-grid | #6b4c3b | slab | one-page | bold | hero, faq, about, contact |

All three set `package` true.

## Frames that include hours and menu

Fourteen frames use `spidercaster-frame/1`. No frame has a section id `hours`.

The only frame that names both hours and menu is `hours-stack`:

- sections: hero, menu, features, faq, contact
- intent: hours, place, and links stay in the footer
- nav: footer-only
- template: editorial
- package: true

Menu is a section. Hours are footer intent, not a section.

Frames with a `menu` section and no hours wording:

- `house-menu`: hero, menu, gallery, testimonials, about, faq, contact. nav segmented. template editorial.
- `kitchen-board`: hero, about, menu, gallery, faq, contact. nav sidebar. template editorial. Intent is a food or drink menu from copy only.

`welcome-scroll` uses the word menu for in-page jumps. Its sections are hero, about, features, gallery, faq, contact. It has neither an hours section nor a menu section.

## Harbor hero

Both files exist. Same byte size. The files were not opened.

| path | bytes | last write |
| --- | --- | --- |
| stage/harbor/src/assets/hero.png | 261195 | 2026-10-01 15:37:57 |
| stage/harbor/out/assets/hero.png | 261195 | 2026-10-01 15:54:06 |

## Rules still only prose

No machine rule file was on disk. Every Mobile line below is still only the prose in that seat's `SKILL.md`. `INDEX.md` does not encode these lines.

| seat | Mobile prose |
| --- | --- |
| architect | Do not pick a frame that drops hours or menu when the copy has those sections. |
| content | Do not invent copy to fill a thin mobile page. |
| frontend | Phone layout is under 860px. The hero is 16/9. Content is visible without waiting for JavaScript. |
| graphics | Local hero only, real pixel size, no hotlink. |
| visual | Fail height 168px, hidden reveal, empty about-panel, and a missing skip link. |
| seo | Staged pages stay noindex. One h1. The description is a full sentence. |
| deployer | This seat does not publish. |

Frontend says the hero is 16/9. Visual says fail height 168px. Those sentences are not the same rule, and neither is in `mobile.json`.

A phone pass can rely on the three molds, on `hours-stack`, `house-menu`, and `kitchen-board` for a menu section, and on the two harbor hero files at 261195 bytes. It cannot rely on an hours section id, a seat card, or an encoded rule file.
