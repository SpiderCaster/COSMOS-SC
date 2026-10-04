STATUS: STARTED 2026-10-01

Read lib/render.py for the menu row CSS and the Python that emits a menu row. Explain the 360px collision. Propose a phone-only layout inside max-width:860px. Do not edit Python, stage, or lib. Do not publish. Do not change prices, names, or copy. Do not add a photo.

STATUS: DONE 2026-10-01

Wrote library/research/app/HOW_PHONE_MENU.md. The current row is a flex line: .mi-col (name, and description when present), .dots, .mi-price. On a 360px screen .mi-desc{width:100%} shares that line with the dotted leader, so the description collides with the price or wraps beside a broken leader. Proposal is CSS only, inside the existing max-width:860px query. Wider screens stay as they are. No Python, stage, or lib edit. No publish.

Proposed selectors:

@media(max-width:860px){
.menu-item{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:4px 12px;padding:12px 0;min-height:48px}
.menu-item .mi-col{display:contents}
.menu-item .mi-name{grid-column:1;grid-row:1;min-width:0;overflow-wrap:anywhere}
.menu-item .mi-price{grid-column:2;grid-row:1;justify-self:end;white-space:nowrap}
.menu-item .mi-desc{grid-column:1 / -1;grid-row:2;width:auto;min-width:0}
.menu-item .dots{display:none}
}
