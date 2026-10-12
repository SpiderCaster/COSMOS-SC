"""Prove part wrap, replace, and hash binding. Stdlib only.

Run from the repo root: ``python lib/part_swap_selftest.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.part_swap import PartSwapError, bind_hashes, replace_part, wrap_part


def _fail(msg: str) -> int:
    print("part_swap selftest FAIL: " + msg)
    return 1


def _must_raise(html: str, catalog_id: str) -> str | None:
    try:
        replace_part(html, catalog_id, "z{a:b}", "<i>no</i>")
    except PartSwapError as exc:
        if str(exc) != "part not on page":
            return "wrong message: " + str(exc)
        return None
    return "missing part did not raise"


def main() -> int:
    links = (
        '<a href="#brand">Brand</a>'
        '<a href="#main">Stay</a>'
        '<a href="#kept">Kept</a>'
    )
    old_frag = "<p>One</p>" + links
    new_frag = "<p>Two</p>" + links
    poison = "p{color:red}</style>TAIL</STYLE>END"
    first = wrap_part("hero-a", poison, old_frag)
    if not first.startswith('<style data-sc-tool="hero-a">'):
        return _fail("wrap missing style marker")
    if f'<div data-sc-part="hero-a">{old_frag}</div>' not in first:
        return _fail("wrap did not put the fragment in the part div")
    if first.find("data-sc-tool") > first.find("data-sc-part"):
        return _fail("wrap put the div before the style")
    open_end = first.find(">")
    close_at = first.lower().find("</style>")
    inner = first[open_end + 1 : close_at]
    if "</style" in inner.lower():
        return _fail("css closed the style tag")
    if "p{color:red}" not in inner or "TAIL" not in inner or "END" not in inner:
        return _fail("wrap dropped css")
    if "<\\/style" not in inner:
        return _fail("literal </style was not neutralized")

    second = wrap_part("card-b", "h2{color:blue}", '<h2 id="kept">Keep</h2>')
    page = (
        '<main id="main">'
        + first
        + "<!--mid-->"
        + second
        + '<a href="#brand">Out</a>'
        + "</main>"
    )
    replaced = replace_part(page, "hero-a", "p{color:green}", new_frag)
    if "p{color:green}" not in replaced:
        return _fail("replace did not change the css")
    if "p{color:red}" in replaced or "TAIL" in replaced:
        return _fail("replace left the old css")
    if "<p>Two</p>" not in replaced or "<p>One</p>" in replaced:
        return _fail("replace did not change the fragment")
    if second not in replaced or "<!--mid-->" not in replaced:
        return _fail("replace did not keep the second part")
    if replaced.count('data-sc-part="card-b"') != 1:
        return _fail("second part marker changed")

    missing = _must_raise(page, "no-such")
    if missing:
        return _fail(missing)
    only_style = _must_raise('<style data-sc-tool="only">a{}</style>', "only")
    if only_style:
        return _fail(only_style)
    only_div = _must_raise('<div data-sc-part="only">a</div>', "only")
    if only_div:
        return _fail(only_div)

    bound = bind_hashes(replaced)
    if 'href="#brand"' in bound:
        return _fail("dangling #brand was not rewritten")
    if '<a href="#main">Stay</a>' not in bound:
        return _fail("#main itself did not stay")
    if '<a href="#main">Brand</a>' not in bound or '<a href="#main">Out</a>' not in bound:
        return _fail("#brand did not become #main")
    if '<a href="#kept">Kept</a>' not in bound:
        return _fail("hash that matches an id was rewritten")
    if "h2{color:blue}" not in bound or '<h2 id="kept">Keep</h2>' not in bound:
        return _fail("bind_hashes changed the second part")
    loose = '<p><a href="#brand">B</a><a href="#main">M</a></p>'
    if bind_hashes(loose) != loose:
        return _fail("bind_hashes changed html that has no id=main")

    nested_frag = '<div class="in"><script>var x="</div>";</script><p>Hi</p></div>'
    nested = wrap_part("nest", "a{b:c}", nested_frag)
    nested_page = nested + "\n" + second
    nested_out = replace_part(nested_page, "nest", "a{b:z}", "<p>Yo</p>")
    if "a{b:z}" not in nested_out or "<p>Yo</p>" not in nested_out:
        return _fail("nested replace did not apply")
    if 'var x="</div>"' in nested_out or "a{b:c}" in nested_out:
        return _fail("nested replace closed the div inside script")
    if second not in nested_out:
        return _fail("nested replace dropped the second part")

    again = replace_part(replaced, "hero-a", "p{color:blue}", new_frag)
    if "p{color:blue}" not in again or "p{color:green}" in again:
        return _fail("second replace did not find the wrapped part")
    if second not in again:
        return _fail("second replace dropped the second part")

    for catalog_id, expect in (
        ('a"b', 'data-sc-tool="a&quot;b"'),
        ("a&b", 'data-sc-tool="a&amp;b"'),
        ("a+b.c", 'data-sc-tool="a+b.c"'),
    ):
        wrapped = wrap_part(catalog_id, "m{}", "<b>q</b>")
        if expect not in wrapped:
            return _fail("wrap escaped " + catalog_id + " wrong")
        swapped = replace_part(wrapped, catalog_id, "n{}", "<b>r</b>")
        if "n{}" not in swapped or "m{}" in swapped or "<b>r</b>" not in swapped:
            return _fail("replace missed id " + catalog_id)

    print("part_swap selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
