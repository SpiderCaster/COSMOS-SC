# Phone menu row

Read 2026-10-01 from `lib/render.py` only. This note does not render a page, does not edit Python, stage, or lib, and does not publish. Prices, names, and descriptions stay as the item already has them. No photo is added.

## What the renderer emits

The menu branch (`kind == "menu"`) writes one `div.menu-item` per item. Inside it, `div.mi-col` holds `span.mi-name` and, only when that item has a description, `span.mi-desc`. After the column it always writes `span.dots` (`aria-hidden="true"`) and `span.mi-price`. The price text is the item price, or an empty string when there is no price. The text is escaped. Nothing in that branch rewrites the words or the price.

Those six rules are the whole menu-row stylesheet. The existing `@media(max-width:860px)` block does not restyle them, so a 360px screen uses the same six:

```css
.menu-item{display:flex;align-items:center;gap:10px;padding:7px 0;min-height:48px}
.menu-item .mi-name{font-weight:600}
.menu-item .mi-desc{color:var(--muted);font-size:1rem;width:100%}
.menu-item .dots{flex:0 1 1.5rem;border-bottom:2px dotted var(--line);min-width:12px}
.menu-item .mi-price{font-weight:700;color:var(--price);white-space:nowrap;flex:none}
.menu-item .mi-col{display:flex;flex-direction:column;flex:1;min-width:0}
```

## What that does at 360px

The page root font size is 18px, so `1rem` is 18px and the leader’s `1.5rem` basis is 27px. Under 860px the wrap’s side padding is 16px, so the row has 328px to use. The row is a horizontal flex line (`flex-wrap` is not set, so it does not wrap). The three flex items are the column, the leader, and the price, with 10px between them. They are centered as a group. Padding is 7px on the top and bottom, and `min-height:48px` keeps a short row from going under 48px.

The column grows and shrinks (`flex:1`) and its `min-width:0` lets it become narrower than the text inside it. The name is only bold. It has no width of its own. The description, when present, is muted 18px text with `width:100%`. That percentage is of the column, not of the 328px row. The description is also a flex item of that column, and it does not set `min-width:0`, so its minimum is the longest unbreakable run of its own text. If that run is wider than the leftover column, the description paints out of the column, across the leader and the price. The price cannot get out of the way: `white-space:nowrap` and `flex:none` keep it one chunk at its full width. That is the collision.

If the description does wrap, it wraps only in the leftover column, beside the leader and the price, not across the row. The leader is an empty span, at least 12px and at most about 27px, with a 2px dotted bottom border. Because the row centers its items, that short dotted segment sits at the vertical middle of the name-plus-description stack. It is not a line from the name to the price. That is the broken leader.

A row with no description is one line: name, short dotted segment, price, at least 48px tall. The defect is the description rule, not the name-and-price line by itself.

## Phone-only proposal

A later edit can add the rules below inside the existing `max-width:860px` query. Wider screens keep the six rules above, including the dotted leader. This is CSS only. The same spans stay in the same order. No name, price, or description changes. No photo.

`display:contents` on `.mi-col` drops the column box so the name and the description become cells of the row. The name and the price share the first grid row. The price sits in an `auto` column, stays `white-space:nowrap`, and aligns to the end, so it does not wrap and does not drop to the next line. A long name wraps inside the first column (`minmax(0,1fr)` and `overflow-wrap:anywhere`) instead of pushing the price. The description spans both columns on the next row. `width:auto` and `min-width:0` replace the `width:100%` that overflowed the flex line, and the grid area is the full row, so the description is full width under the name and the price. `.dots` is `display:none`, so there is no dotted leader under 860px. The dots span is already `aria-hidden`. Vertical padding is 12px and `min-height:48px` stays, so a row that has a name and a price is at least 48px tall. A description adds a second line and the row grows. An item with no description leaves that second row empty.

```css
@media(max-width:860px){
.menu-item{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:4px 12px;padding:12px 0;min-height:48px}
.menu-item .mi-col{display:contents}
.menu-item .mi-name{grid-column:1;grid-row:1;min-width:0;overflow-wrap:anywhere}
.menu-item .mi-price{grid-column:2;grid-row:1;justify-self:end;white-space:nowrap}
.menu-item .mi-desc{grid-column:1 / -1;grid-row:2;width:auto;min-width:0}
.menu-item .dots{display:none}
}
```
