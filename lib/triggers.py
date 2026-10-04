"""Mobile trigger table. Does not fetch a URL. Does not write a file."""
from __future__ import annotations

_WS = " \t\r\n"


def _block_end(text: str, open_at: int) -> int | None:
    depth = 0
    for index in range(open_at, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _phone_shows_reveal(html: str) -> bool:
    """True when a max-width:860px media rule sets .reveal{opacity:1."""
    start = 0
    while True:
        at = html.find("@media", start)
        if at < 0:
            return False
        open_at = html.find("{", at)
        if open_at < 0:
            return False
        if "max-width:860px" in html[at:open_at]:
            end = _block_end(html, open_at)
            body = html[open_at + 1 :] if end is None else html[open_at + 1 : end]
            if ".reveal{opacity:1" in body:
                return True
        start = open_at + 1


def _name_char(char: str) -> bool:
    return char.isalnum() or char in "-_:"


def _attr(attrs: str, name: str) -> str | None:
    index = 0
    while True:
        found = attrs.find(name, index)
        if found < 0:
            return None
        if found > 0 and _name_char(attrs[found - 1]):
            index = found + len(name)
            continue
        cursor = found + len(name)
        while cursor < len(attrs) and attrs[cursor] in _WS:
            cursor += 1
        if cursor >= len(attrs) or attrs[cursor] != "=":
            index = found + len(name)
            continue
        cursor += 1
        while cursor < len(attrs) and attrs[cursor] in _WS:
            cursor += 1
        if cursor >= len(attrs):
            return None
        quote = attrs[cursor]
        if quote in "\"'":
            stop = attrs.find(quote, cursor + 1)
            if stop < 0:
                return attrs[cursor + 1 :]
            return attrs[cursor + 1 : stop]
        stop = cursor
        while stop < len(attrs) and attrs[stop] not in _WS and attrs[stop] != ">":
            stop += 1
        return attrs[cursor:stop]


def _remote_src(src: str) -> bool:
    text = src.strip()
    return (
        text.startswith("http://")
        or text.startswith("https://")
        or text.startswith("//")
    )


def _remote_img(html: str) -> bool:
    start = 0
    token = "<img"
    while True:
        at = html.find(token, start)
        if at < 0:
            return False
        after = at + len(token)
        if after < len(html) and _name_char(html[after]):
            start = after
            continue
        end = html.find(">", after)
        if end < 0:
            return False
        src = _attr(html[after:end], "src")
        if src is not None and _remote_src(src):
            return True
        start = end + 1


def review(html: str) -> dict:
    """Return ok and hits. ok is false when any hit has fix none."""
    hits: list[dict] = []
    if "height:168px" in html:
        hits.append({"code": "phone_hero_short", "fix": "none"})
    if ".reveal{opacity:0" in html and not _phone_shows_reveal(html):
        hits.append({"code": "phone_hidden", "fix": "none"})
    if "about-panel" in html:
        hits.append({"code": "empty_panel", "fix": "none"})
    if 'href="#main"' not in html:
        hits.append({"code": "missing_skip", "fix": "none"})
    if _remote_img(html):
        hits.append({"code": "remote_img", "fix": "none"})
    ok = not any(hit["fix"] == "none" for hit in hits)
    return {"ok": ok, "hits": hits}


def main() -> int:
    short = (
        '<a class="skip" href="#main">Skip to content</a>'
        "<style>.hero-visual{height:168px}</style>"
        '<img src="assets/hero.png" alt="">'
    )
    short_row = review(short)
    assert short_row["ok"] is False
    assert {"code": "phone_hero_short", "fix": "none"} in short_row["hits"]

    good = (
        '<a class="skip" href="#main">Skip to content</a>'
        "<style>.hero-visual{aspect-ratio:16/9}</style>"
        '<img src="assets/hero.png" alt="">'
    )
    assert "about-panel" not in good
    assert review(good) == {"ok": True, "hits": []}

    hidden = (
        '<a href="#main">Skip</a><style>.reveal{opacity:0}'
        "@media(max-width:860px){.nav{display:block}}"
        "@media(prefers-reduced-motion:reduce){.reveal{opacity:1}}</style>"
    )
    hidden_row = review(hidden)
    assert hidden_row["ok"] is False
    assert {"code": "phone_hidden", "fix": "none"} in hidden_row["hits"]

    shown = (
        '<a href="#main">Skip</a><style>.reveal{opacity:0}'
        "@media(max-width:860px){.reveal{opacity:1}}</style>"
    )
    assert review(shown) == {"ok": True, "hits": []}

    panel = '<a href="#main">Skip</a><div class="about-panel"></div>'
    assert {"code": "empty_panel", "fix": "none"} in review(panel)["hits"]
    assert review(panel)["ok"] is False

    remote = '<a href="#main">Skip</a><img src="https://cdn.example/a.png" alt="">'
    assert {"code": "remote_img", "fix": "none"} in review(remote)["hits"]
    proto = '<a href="#main">Skip</a><img src="//cdn.example/a.png" alt="">'
    assert {"code": "remote_img", "fix": "none"} in review(proto)["hits"]
    plain = '<a href="#main">Skip</a><img src="http://cdn.example/a.png" alt="">'
    assert {"code": "remote_img", "fix": "none"} in review(plain)["hits"]
    local = '<a href="#main">Skip</a><img src="/assets/hero.png" alt="">'
    assert review(local) == {"ok": True, "hits": []}

    print("triggers selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
