STATUS: STARTED 2026-10-01

Read the @media(max-width:860px) block in lib/render.py. Confirm it contains .card:has(.chip) and .grid.c3{gap:0. If either is missing, do not edit the skills. Say so in the inbox. If both are present, add one bullet to each ## Mobile section that does not already say card:has(.chip): library/seats/frontend/SKILL.md, library/seats/frontend/WRAPPER.md, library/seats/visual/SKILL.md, and library/seats/visual/WRAPPER.md. Bullet: On a phone, a card icon sits beside its heading, and a group of cards shares one bordered list. Hands stay unchanged. Frontend: plan_offline, render. Visual: check_site. Do not publish. Do not edit Python, stage/, or lib/. Never delete. No secrets. Do not add a hand.

STATUS: DONE 2026-10-01

Both are present inside @media(max-width:860px) in lib/render.py: .card:has(.chip){display:grid;grid-template-columns:32px minmax(0,1fr);column-gap:12px;align-items:start} and .grid.c3{gap:0;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}. None of the four ## Mobile sections already said card:has(.chip). The bullet is now on:

- library/seats/frontend/SKILL.md
- library/seats/frontend/WRAPPER.md
- library/seats/visual/SKILL.md
- library/seats/visual/WRAPPER.md

Hands are unchanged. Frontend hands stay plan_offline and render. The visual hand stays check_site. Python, stage/, and lib/ were not edited.
