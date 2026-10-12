"""Fill part slots from copy, and list grounded section strings.

Stdlib only. Does not invent copy, publish, or use the network.
"""
from __future__ import annotations

import copy
import html
from html.parser import HTMLParser

# Chrome the fill block must not repeat, even when the copy contains them.
_EXACT_SKIP = frozenset({"Read on", "Built with SpiderCaster", "About"})

_VOID = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

_RAW = frozenset({"script", "style", "textarea", "title"})


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _parse_tag(fragment: str, i: int):
    """Parse one tag starting at ``fragment[i] == '<'``.

    Returns ``(kind, start, end, tag, slot, self_closing)`` or None.
    ``end`` is the index just after ``>``. ``slot`` is the data-sc-slot
    value, or None when that attribute is absent.
    """
    n = len(fragment)
    if i >= n or fragment[i] != "<":
        return None
    j = i + 1
    if j >= n:
        return None
    is_end = False
    if fragment[j] == "/":
        is_end = True
        j += 1
    if j >= n or not (fragment[j].isalpha() or fragment[j] == "_"):
        return None
    k = j + 1
    while k < n and (fragment[k].isalnum() or fragment[k] in "-:_"):
        k += 1
    tag = fragment[j:k].lower()
    if is_end:
        p = k
        while p < n and fragment[p] != ">":
            if fragment[p] == "<":
                return None
            p += 1
        if p >= n:
            return None
        return ("end", i, p + 1, tag, None, False)

    p = k
    slot = None
    seen_slot = False
    while p < n:
        while p < n and fragment[p].isspace():
            p += 1
        if p >= n:
            return None
        if fragment[p] == ">":
            return ("start", i, p + 1, tag, slot if seen_slot else None, False)
        if fragment[p] == "/":
            q = p + 1
            while q < n and fragment[q].isspace():
                q += 1
            if q < n and fragment[q] == ">":
                return ("start", i, q + 1, tag, slot if seen_slot else None, True)
            return None
        name_start = p
        while p < n and not fragment[p].isspace() and fragment[p] not in "=/>":
            p += 1
        name = fragment[name_start:p].lower()
        if not name:
            return None
        while p < n and fragment[p].isspace():
            p += 1
        value = ""
        if p < n and fragment[p] == "=":
            p += 1
            while p < n and fragment[p].isspace():
                p += 1
            if p >= n:
                return None
            if fragment[p] in "\"'":
                quote = fragment[p]
                p += 1
                vstart = p
                while p < n and fragment[p] != quote:
                    p += 1
                if p >= n:
                    return None
                value = fragment[vstart:p]
                p += 1
            else:
                vstart = p
                while p < n and not fragment[p].isspace() and fragment[p] not in ">/":
                    p += 1
                value = fragment[vstart:p]
        if name == "data-sc-slot":
            seen_slot = True
            slot = html.unescape(value)
    return None


def _raw_close(fragment: str, tag: str, start: int) -> int:
    lower = fragment.lower()
    needle = "</" + tag
    pos = start
    while True:
        found = lower.find(needle, pos)
        if found < 0:
            return -1
        after = found + len(needle)
        if after >= len(lower) or lower[after] in "> \t\r\n/":
            return found
        pos = found + 1


def _slot_ranges(fragment: str) -> list[tuple[int, int, str]]:
    """Inner-text spans of elements that carry data-sc-slot."""
    ranges: list[tuple[int, int, str]] = []
    stack: list[dict] = []
    i = 0
    n = len(fragment)
    while i < n:
        lt = fragment.find("<", i)
        if lt < 0:
            break
        if fragment.startswith("<!--", lt):
            end = fragment.find("-->", lt + 4)
            if end < 0:
                break
            i = end + 3
            continue
        if fragment.startswith("<!", lt) or fragment.startswith("<?", lt):
            end = fragment.find(">", lt + 2)
            if end < 0:
                break
            i = end + 1
            continue
        parsed = _parse_tag(fragment, lt)
        if parsed is None:
            i = lt + 1
            continue
        kind, start, end, tag, slot, self_closing = parsed
        if kind == "end":
            match = None
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx]["tag"] == tag:
                    match = idx
                    break
            if match is not None:
                while len(stack) > match:
                    el = stack.pop()
                    if el["slot"] is not None and start >= el["inner"]:
                        ranges.append((el["inner"], start, el["slot"]))
            i = end
            continue
        if self_closing or tag in _VOID:
            i = end
            continue
        stack.append({"tag": tag, "slot": slot, "inner": end})
        if tag in _RAW:
            close_at = _raw_close(fragment, tag, end)
            if close_at < 0:
                stack.pop()
                i = end
                continue
            i = close_at
            continue
        i = end
    return ranges


def _grounded_slot(slots: dict, key: str, copy_text: str) -> str | None:
    if not isinstance(slots, dict) or key not in slots:
        return None
    value = slots[key]
    if not isinstance(value, str) or value == "":
        return None
    if not isinstance(copy_text, str) or value not in copy_text:
        return None
    return value


def fill_fragment(fragment: str, slots: dict[str, str], copy_text: str) -> str:
    """Replace data-sc-slot text when the slot value is grounded copy.

    A value is grounded when it is a non-empty exact substring of
    ``copy_text``. Anything else leaves that element as it was. No new
    elements are added. Inserted text is HTML-escaped.
    """
    if not isinstance(fragment, str) or not fragment:
        return fragment if isinstance(fragment, str) else ""
    if not isinstance(slots, dict) or not slots:
        return fragment
    ranges = _slot_ranges(fragment)
    chosen: list[tuple[int, int, str]] = []
    seen: set[tuple[int, int]] = set()
    for start, end, key in ranges:
        if (start, end) in seen or end < start:
            continue
        seen.add((start, end))
        value = _grounded_slot(slots, key, copy_text)
        if value is None:
            continue
        chosen.append((start, end, value))
    if not chosen:
        return fragment
    kept = []
    for item in chosen:
        start, end, _value = item
        nested = False
        for other_start, other_end, _other in chosen:
            if other_start <= start and end <= other_end and (other_start, other_end) != (start, end):
                nested = True
                break
        if not nested:
            kept.append(item)
    out = fragment
    for start, end, value in sorted(kept, key=lambda item: item[0], reverse=True):
        out = out[:start] + _esc(value) + out[end:]
    return out


def _walk_strings(node, found: list[str]) -> None:
    if isinstance(node, str):
        found.append(node)
        return
    if isinstance(node, dict):
        for value in node.values():
            _walk_strings(value, found)
        return
    if isinstance(node, (list, tuple)):
        for value in node:
            _walk_strings(value, found)


def copy_block(section: dict, copy_text: str) -> str:
    """Return a sc-fill div of grounded data strings, or "" if none.

    Walks ``section["data"]`` and keeps string values that are exact
    substrings of ``copy_text``. Skips empty strings. Skips a value whose
    text is exactly ``Read on``, ``Built with SpiderCaster``, or ``About``.
    """
    if not isinstance(section, dict):
        return ""
    data = section.get("data")
    if not isinstance(data, dict):
        return ""
    if not isinstance(copy_text, str):
        copy_text = ""
    found: list[str] = []
    _walk_strings(data, found)
    kept: list[str] = []
    for value in found:
        if not isinstance(value, str) or not value.strip():
            continue
        if value not in copy_text:
            continue
        if value.strip() in _EXACT_SKIP:
            continue
        kept.append(_esc(value))
    if not kept:
        return ""
    return '<div class="sc-fill">' + "\n".join(kept) + "</div>"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _copy_has(text: str, copy_text: str) -> bool:
    """True when collapsed text is a collapsed substring of the copy."""
    folded = _norm(text)
    if not folded or not isinstance(copy_text, str):
        return False
    return folded in _norm(copy_text)


def _keep_text(text: str, allowed: set[str], copy_text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped in _EXACT_SKIP:
        return False
    folded = _norm(stripped)
    if stripped in allowed or folded in allowed:
        return True
    return len(folded) >= 20 and _copy_has(folded, copy_text)


def _clean(value, copy_text: str) -> str:
    """A field string that is real copy. Short tokens stay when they are the field."""
    if not isinstance(value, str):
        return ""
    text = _norm(value)
    if not text or text in _EXACT_SKIP:
        return ""
    if not _copy_has(text, copy_text):
        return ""
    return text


def _tel_href(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 7:
        return ""
    return "tel:" + ("+" if phone.startswith("+") else "") + digits


def _mail_href(email: str) -> str:
    text = email.strip()
    if "@" not in text or any(ch in text for ch in " \t\r\n<>\"'"):
        return ""
    return "mailto:" + text


def _action(link, copy_text: str) -> dict | None:
    if not isinstance(link, dict):
        return None
    label = _clean(link.get("label"), copy_text)
    href = link.get("href")
    if not label or not isinstance(href, str) or not href.strip():
        return None
    href = href.strip()
    if not (href.startswith("#") or href.startswith(("tel:", "mailto:", "http://", "https://"))):
        return None
    return {"label": label, "href": href}


def section_fields(section: dict, copy_text: str) -> dict:
    """Grounded title, prose, actions, and rows from one section. No new words."""
    data = section.get("data") if isinstance(section, dict) else None
    if not isinstance(data, dict):
        data = {}
    if not isinstance(copy_text, str):
        copy_text = ""
    kind = str(section.get("type") or "") if isinstance(section, dict) else ""
    sec_id = str(section.get("id") or "") if isinstance(section, dict) else ""
    title = _clean(data.get("headline") if kind == "hero" else data.get("title"), copy_text)
    if kind == "hero" and not title:
        title = _clean(data.get("title"), copy_text)
    lead = ""
    extras: list[str] = []
    actions: list[dict] = []
    items: list[dict] = []

    def add_extra(value) -> None:
        line = _clean(value, copy_text)
        if line and line != title and line != lead and line not in extras:
            extras.append(line)

    if kind == "hero":
        lead = _clean(data.get("subhead"), copy_text)
        for bullet in data.get("bullets") or []:
            add_extra(bullet)
        for key in ("primary", "secondary"):
            action = _action(data.get(key), copy_text)
            if action and action["label"] not in {item["label"] for item in actions}:
                actions.append(action)
    elif kind == "faq":
        lead = _clean(data.get("subhead"), copy_text)
        for it in data.get("items") or []:
            if not isinstance(it, dict):
                continue
            question = _clean(it.get("q"), copy_text)
            answer = _clean(it.get("a"), copy_text)
            if question or answer:
                items.append({"heading": question, "body": answer})
    elif kind == "menu":
        lead = _clean(data.get("subhead"), copy_text)
        for group in data.get("groups") or []:
            if not isinstance(group, dict):
                continue
            for it in group.get("items") or []:
                if not isinstance(it, dict):
                    continue
                cells = []
                for key in ("name", "desc", "price"):
                    cell = _clean(it.get(key), copy_text)
                    if cell and cell not in cells:
                        cells.append(cell)
                if cells:
                    items.append({"cells": cells})
    elif kind == "contact":
        lead = _clean(data.get("body"), copy_text)
        add_extra(data.get("address"))
        add_extra(data.get("hours"))
        phone = _clean(data.get("phone"), copy_text)
        email = _clean(data.get("email"), copy_text)
        if phone:
            href = _tel_href(phone)
            if href:
                actions.append({"label": phone, "href": href})
            else:
                add_extra(phone)
        if email:
            href = _mail_href(email)
            if href:
                actions.append({"label": email, "href": href})
            else:
                add_extra(email)
    else:
        lead = _clean(data.get("subhead"), copy_text)
        body = data.get("body")
        if isinstance(body, str):
            add_extra(body)
        elif isinstance(body, list):
            for para in body:
                add_extra(para)
        for point in data.get("points") or []:
            if not isinstance(point, dict):
                continue
            heading = _clean(point.get("title"), copy_text)
            body_text = _clean(point.get("body"), copy_text)
            if heading or body_text:
                items.append({"heading": heading, "body": body_text, "href": f"#{sec_id}" if sec_id and heading else ""})
        for it in data.get("items") or []:
            if isinstance(it, str):
                heading = _clean(it, copy_text)
                if heading:
                    items.append({"heading": heading, "body": "", "href": f"#{sec_id}" if sec_id else ""})
                continue
            if not isinstance(it, dict):
                continue
            heading = ""
            for key in ("title", "name", "label", "q", "value"):
                heading = _clean(it.get(key), copy_text)
                if heading:
                    break
            body_text = ""
            for key in ("body", "desc", "blurb", "quote", "caption", "a"):
                body_text = _clean(it.get(key), copy_text)
                if body_text and body_text != heading:
                    break
                body_text = ""
            price = _clean(it.get("price"), copy_text)
            if price and price not in {heading, body_text}:
                cells = [part for part in (heading, body_text, price) if part]
                if cells:
                    items.append({"cells": cells})
                continue
            if heading or body_text:
                items.append({
                    "heading": heading,
                    "body": body_text,
                    "href": f"#{sec_id}" if sec_id and heading else "",
                })
    return {
        "title": title,
        "lead": lead,
        "extras": extras,
        "actions": actions,
        "items": items,
        "kind": kind,
    }


def field_strings(fields: dict) -> list[str]:
    """Every grounded string bind may print. Short ones stay only because they are fields."""
    found: list[str] = []

    def add(value) -> None:
        if isinstance(value, str) and value and value not in found:
            found.append(value)

    if not isinstance(fields, dict):
        return found
    add(fields.get("title"))
    add(fields.get("lead"))
    for line in fields.get("extras") or []:
        add(line)
    for action in fields.get("actions") or []:
        if isinstance(action, dict):
            add(action.get("label"))
    for item in fields.get("items") or []:
        if not isinstance(item, dict):
            continue
        add(item.get("heading"))
        add(item.get("body"))
        for cell in item.get("cells") or []:
            add(cell)
    return found


_HOST = frozenset({
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "td", "th", "a", "span", "li",
    "caption", "button", "label", "small", "strong", "em", "time", "dd", "dt",
    "blockquote", "figcaption", "summary",
})
_HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
_PROSE = frozenset({"p", "span", "li", "blockquote", "figcaption", "small", "caption"})
_REPEAT_PRIORITY = {"tr": 0, "details": 1, "article": 2, "li": 3, "div": 4}
_SCRUB_ATTRS = frozenset({"data-label", "alt", "aria-label", "title", "placeholder"})


def _parse_tree(fragment: str) -> dict:
    class Tree(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.root = {"tag": "root", "attrs": [], "kids": []}
            self.stack = [self.root]
            self.skip = 0

        def handle_starttag(self, tag, attrs):
            node = {
                "tag": tag,
                "attrs": list(attrs),
                "kids": [],
                "void": tag in _VOID,
                "raw": tag in _RAW,
            }
            self.stack[-1]["kids"].append(node)
            if tag not in _VOID:
                self.stack.append(node)
            if tag in _RAW:
                self.skip += 1

        def handle_startendtag(self, tag, attrs):
            node = {"tag": tag, "attrs": list(attrs), "kids": [], "void": True}
            self.stack[-1]["kids"].append(node)

        def handle_endtag(self, tag):
            if tag in _RAW and self.skip:
                self.skip -= 1
            for index in range(len(self.stack) - 1, 0, -1):
                if self.stack[index].get("tag") == tag:
                    del self.stack[index:]
                    break

        def handle_data(self, data):
            self.stack[-1]["kids"].append({"text": data, "raw_text": self.skip > 0})

        def handle_comment(self, data):
            self.stack[-1]["kids"].append({"text": f"<!--{data}-->", "raw_text": True})

    tree = Tree()
    tree.feed(fragment)
    tree.close()
    return tree.root


def _visible(node: dict) -> str:
    if "text" in node:
        return "" if node.get("raw_text") else node["text"]
    if node.get("raw"):
        return ""
    return "".join(_visible(kid) for kid in node.get("kids") or [])


def _has_host_descendant(node: dict) -> bool:
    for kid in node.get("kids") or []:
        if "tag" not in kid or kid.get("raw"):
            continue
        if kid.get("tag") in _HOST and _visible(kid).strip():
            return True
        if _has_host_descendant(kid):
            return True
    return False


def _collect_slots(node: dict, skip_ids: set[int], stack: list[dict], found: list[tuple[dict, list[dict]]]) -> None:
    if "text" in node or node.get("raw") or id(node) in skip_ids:
        return
    stack.append(node)
    tag = node.get("tag")
    if tag in _HOST and _visible(node).strip() and not _has_host_descendant(node):
        found.append((node, list(stack)))
    else:
        for kid in node.get("kids") or []:
            if "tag" in kid:
                _collect_slots(kid, skip_ids, stack, found)
    stack.pop()


def _contains_tag(node: dict, tags: set[str]) -> bool:
    if node.get("tag") in tags:
        return True
    return any(_contains_tag(kid, tags) for kid in node.get("kids") or [] if "tag" in kid)


def _rowish(node: dict) -> bool:
    tag = node.get("tag")
    if not _visible(node).strip():
        return False
    if tag in {"tr", "details", "article", "li"}:
        return True
    if tag == "div":
        return _contains_tag(node, {"details", "article", "h2", "h3"})
    return False


def _find_repeat(node: dict, depth: int = 0, best=None):
    kids = [kid for kid in node.get("kids") or [] if "tag" in kid]
    grouped: dict[str, list[dict]] = {}
    for kid in kids:
        tag = kid.get("tag")
        if tag in _REPEAT_PRIORITY and _rowish(kid):
            grouped.setdefault(tag, []).append(kid)
    for tag, group in grouped.items():
        if len(group) < 2:
            continue
        score = (depth, _REPEAT_PRIORITY[tag])
        if best is None or score < best[0]:
            best = (score, node, group)
    for kid in kids:
        best = _find_repeat(kid, depth + 1, best)
    return best


def _set_text(node: dict, value: str) -> None:
    node["kids"] = [{"text": value}]


def _clear(node: dict) -> None:
    node["kids"] = []


def _set_attr(node: dict, name: str, value: str) -> None:
    attrs = []
    found = False
    for key, current in node.get("attrs") or []:
        if key == name:
            attrs.append((key, value))
            found = True
        else:
            attrs.append((key, current))
    if not found:
        attrs.append((name, value))
    node["attrs"] = attrs


def _find_parent(node: dict, target: dict) -> dict | None:
    for kid in node.get("kids") or []:
        if kid is target:
            return node
        if "tag" in kid:
            found = _find_parent(kid, target)
            if found is not None:
                return found
    return None


def _clone_after(root: dict, node: dict) -> dict:
    parent = _find_parent(root, node)
    clone = copy.deepcopy(node)
    if parent is None:
        return clone
    kids = parent.setdefault("kids", [])
    index = next(pos for pos, kid in enumerate(kids) if kid is node)
    kids.insert(index + 1, clone)
    return clone


def _is_heading_slot(node: dict, stack: list[dict]) -> bool:
    if node.get("tag") in _HEADINGS:
        return True
    return node.get("tag") == "a" and any(item.get("tag") in _HEADINGS for item in stack)


def _is_prose_slot(node: dict, stack: list[dict]) -> bool:
    if _is_heading_slot(node, stack) or node.get("tag") == "a":
        return False
    if any(item.get("tag") == "thead" for item in stack):
        return False
    return node.get("tag") in _PROSE


def _fill_row(row: dict, item: dict) -> None:
    slots = []
    _collect_slots(row, set(), [], slots)
    if "cells" in item:
        values = [value for value in item.get("cells") or [] if value]
        for (slot, _stack), value in zip(slots, values):
            _set_text(slot, value)
        for slot, _stack in slots[len(values):]:
            _clear(slot)
        return
    heading = str(item.get("heading") or "")
    body = str(item.get("body") or "")
    href = str(item.get("href") or "")
    heading_slot = next((slot for slot, stack in slots if _is_heading_slot(slot, stack)), None)
    prose_slot = next((slot for slot, stack in slots if _is_prose_slot(slot, stack)), None)
    used: set[int] = set()
    if heading and heading_slot is not None:
        _set_text(heading_slot, heading)
        used.add(id(heading_slot))
        if heading_slot.get("tag") == "a" and href.startswith("#"):
            _set_attr(heading_slot, "href", href)
    elif heading and prose_slot is not None and not body:
        _set_text(prose_slot, heading)
        used.add(id(prose_slot))
    if body and prose_slot is not None and id(prose_slot) not in used:
        _set_text(prose_slot, body)
        used.add(id(prose_slot))
    elif body and heading_slot is not None and id(heading_slot) not in used:
        _set_text(heading_slot, body)
        used.add(id(heading_slot))
    for slot, _stack in slots:
        if id(slot) not in used:
            _clear(slot)


def _replace_group(parent: dict, group: list[dict], clones: list[dict]) -> None:
    group_ids = {id(node) for node in group}
    kids = []
    placed = False
    for kid in parent.get("kids") or []:
        if id(kid) in group_ids:
            if not placed:
                kids.extend(clones)
                placed = True
            continue
        kids.append(kid)
    parent["kids"] = kids


def _relabel(node: dict, title: str, copy_text: str) -> None:
    if "tag" not in node:
        return
    attrs = []
    for key, value in node.get("attrs") or []:
        if key == "aria-label" and title:
            shown = "" if value is None else str(value)
            if shown.strip() in _EXACT_SKIP or not _copy_has(shown, copy_text):
                attrs.append((key, title))
                continue
        attrs.append((key, value))
    node["attrs"] = attrs
    for kid in node.get("kids") or []:
        if "tag" in kid:
            _relabel(kid, title, copy_text)


def _promote_heading(node: dict) -> bool:
    if "tag" not in node:
        return False
    if node.get("tag") in _HEADINGS:
        node["tag"] = "h1"
        return True
    for kid in node.get("kids") or []:
        if "tag" in kid and _promote_heading(kid):
            return True
    return False


def _start_tag(tag: str, attrs: list, void: bool) -> str:
    parts = [f"<{tag}"]
    for key, value in attrs:
        if value is None:
            parts.append(" " + key)
            continue
        parts.append(f' {key}="{_esc(str(value))}"')
    parts.append(">" if not void else ">")
    return "".join(parts)


def _scrub_attrs(attrs: list, allowed: set[str], copy_text: str) -> list:
    kept = []
    for key, value in attrs:
        if key in _SCRUB_ATTRS:
            shown = "" if value is None else str(value)
            if shown.strip() and not _keep_text(shown, allowed, copy_text):
                continue
        kept.append((key, value))
    return kept


def _serialize(node: dict, allowed: set[str] | None = None, copy_text: str = "") -> str:
    if "text" in node:
        if node.get("raw_text"):
            return node["text"]
        return _esc(node["text"])
    if node.get("tag") == "root":
        return "".join(_serialize(kid, allowed, copy_text) for kid in node.get("kids") or [])
    attrs = node.get("attrs") or []
    if allowed is not None:
        attrs = _scrub_attrs(attrs, allowed, copy_text)
    inner = "".join(_serialize(kid, allowed, copy_text) for kid in node.get("kids") or [])
    start = _start_tag(node.get("tag") or "div", attrs, bool(node.get("void")))
    if node.get("void"):
        return start
    return start + inner + f"</{node.get('tag')}>"


def bind_fragment(fragment: str, section: dict, copy_text: str) -> str:
    """Refill a catalog snippet from grounded section fields.

    Repeating rows, details, articles, and item divs are cloned so each real
    item has a slot. Catalog sentences are cleared. A snippet that cannot be
    filled is returned unchanged so the ground step can drop it.
    """
    if not isinstance(fragment, str) or not fragment.strip():
        return fragment if isinstance(fragment, str) else ""
    if not isinstance(copy_text, str):
        copy_text = ""
    fields = section_fields(section if isinstance(section, dict) else {}, copy_text)
    if not field_strings(fields):
        return fragment
    try:
        root = _parse_tree(fragment)
    except Exception:
        return fragment
    found = _find_repeat(root)
    group_ids: set[int] = set()
    parent = None
    group: list[dict] = []
    if found is not None:
        _score, parent, group = found
        group_ids = {id(node) for node in group}
    chrome: list[tuple[dict, list[dict]]] = []
    _collect_slots(root, group_ids, [], chrome)
    prose_outside = [(slot, stack) for slot, stack in chrome if _is_prose_slot(slot, stack)]
    items = list(fields["items"])
    extras = list(fields["extras"])
    lead = fields["lead"]
    title = fields["title"]
    actions = list(fields["actions"])
    if found is not None and not prose_outside:
        moved = []
        if lead:
            moved.append(lead)
            lead = ""
        moved.extend(extras)
        extras = []
        if moved:
            items = [{"heading": "", "body": line} for line in moved] + items
    if items and found is None:
        for item in items:
            for value in item.get("cells") or [item.get("heading"), item.get("body")]:
                if value and value not in extras and value != lead and value != title:
                    extras.append(value)
        items = []
    row_ids: set[int] = set()
    if found is not None and parent is not None:
        template = copy.deepcopy(group[0]) if group else None
        clones = [copy.deepcopy(template) for _ in items] if template is not None else []
        _replace_group(parent, group, clones)
        for clone, item in zip(clones, items):
            _fill_row(clone, item)
        if items and group:
            tag = group[0].get("tag")
            row_ids = {
                id(kid)
                for kid in parent.get("kids") or []
                if kid.get("tag") == tag and _rowish(kid)
            }
    chrome = []
    _collect_slots(root, row_ids, [], chrome)
    heading_slots = [(slot, stack) for slot, stack in chrome if _is_heading_slot(slot, stack)]
    prose_slots = [slot for slot, stack in chrome if _is_prose_slot(slot, stack)]
    action_slots = [
        slot for slot, stack in chrome
        if slot.get("tag") == "a" and not _is_heading_slot(slot, stack)
    ]
    used: set[int] = set()
    prose: list[str] = []
    if title and heading_slots:
        _set_text(heading_slots[0][0], title)
        used.add(id(heading_slots[0][0]))
    elif title:
        prose.append(title)
    if lead and lead not in prose:
        prose.append(lead)
    for line in extras:
        if line not in prose:
            prose.append(line)
    targets = list(prose_slots)
    if prose and targets:
        while len(targets) < len(prose):
            targets.append(_clone_after(root, targets[-1]))
        for slot, value in zip(targets, prose):
            _set_text(slot, value)
            used.add(id(slot))
        for slot in targets[len(prose):]:
            _clear(slot)
            used.add(id(slot))
    elif not prose:
        for slot in prose_slots:
            _clear(slot)
            used.add(id(slot))
    atargets = list(action_slots)
    if actions and atargets:
        while len(atargets) < len(actions):
            atargets.append(_clone_after(root, atargets[-1]))
        for slot, action in zip(atargets, actions):
            _set_text(slot, action["label"])
            href = str(action.get("href") or "")
            if href:
                _set_attr(slot, "href", href)
            used.add(id(slot))
        for slot in atargets[len(actions):]:
            _clear(slot)
            used.add(id(slot))
    elif not actions:
        for slot in action_slots:
            _clear(slot)
            used.add(id(slot))
    for slot, _stack in chrome:
        if id(slot) not in used:
            _clear(slot)
    _relabel(root, title, copy_text)
    if fields.get("kind") == "hero":
        _promote_heading(root)
    return _serialize(root)


def ground_fragment(fragment: str, slots: dict, copy_text: str) -> str:
    """Fill grounded slots, then drop catalog demo sentences.

    A text node stays when it is a grounded slot value, or a copy sentence
    of at least 20 characters after whitespace is collapsed. Demo titles,
    sample rows, and short tokens that merely occur inside a copy line are
    removed. Ungrounded data-label, alt, aria-label, title, and placeholder
    attributes are removed. Empty elements go with them. Style and script
    text is left as written.
    """
    if not isinstance(fragment, str):
        return ""
    if not isinstance(slots, dict):
        slots = {}
    if not isinstance(copy_text, str):
        copy_text = ""
    filled = fill_fragment(fragment, slots, copy_text)
    allowed: set[str] = set()
    for value in slots.values():
        if not isinstance(value, str) or not value.strip():
            continue
        if value.strip() in _EXACT_SKIP or not _copy_has(value, copy_text):
            continue
        allowed.add(value.strip())
        allowed.add(_norm(value))
    try:
        root = _parse_tree(filled)
    except Exception:
        return filled

    def has_media(node: dict) -> bool:
        if node.get("tag") in {"img", "svg", "video", "input", "textarea", "iframe"}:
            return True
        return any(has_media(kid) for kid in node.get("kids") or [] if "tag" in kid)

    def prune(node: dict) -> None:
        kept_kids = []
        for kid in node.get("kids") or []:
            if "text" in kid:
                if kid.get("raw_text") or _keep_text(kid["text"], allowed, copy_text):
                    kept_kids.append(kid)
                continue
            prune(kid)
            if kid.get("tag") in _RAW or kid.get("void") or _visible(kid).strip() or has_media(kid):
                kept_kids.append(kid)
        node["kids"] = kept_kids

    prune(root)
    return _serialize(root, allowed, copy_text)


def has_grounded_markup(fragment: str) -> bool:
    """True when a grounded fragment still has visible text or media.

    Style and script text does not count. An empty shell does not count.
    """
    from html.parser import HTMLParser

    if not isinstance(fragment, str) or not fragment.strip():
        return False

    class Seen(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.found = False
            self.skip = 0

        def handle_starttag(self, tag, attrs):
            if tag in {"img", "svg", "video", "input", "textarea", "iframe"}:
                self.found = True
            if tag in _RAW:
                self.skip += 1

        def handle_endtag(self, tag):
            if tag in _RAW and self.skip:
                self.skip -= 1

        def handle_data(self, data):
            if not self.skip and data.strip():
                self.found = True

    parser = Seen()
    try:
        parser.feed(fragment)
        parser.close()
    except Exception:
        return True
    return parser.found
