"""Supplied proof versus tagged sample praise. Stdlib only. Writes nothing."""
from __future__ import annotations

import re

SAMPLE_TAG = "[sample]"
_SPECIFIC = re.compile(r"\d|[$%]|https?://")


def is_generic_praise(text: str) -> bool:
    """True when praise has no digits, money, or URLs."""
    body = str(text or "").replace(SAMPLE_TAG, "").strip()
    return bool(body) and _SPECIFIC.search(body) is None


def is_sample_quote(item: dict) -> bool:
    """A quote is a sample only when the copy says so."""
    if not isinstance(item, dict):
        return False
    if item.get("sample") is True:
        return True
    return str(item.get("quote") or "").rstrip().endswith(SAMPLE_TAG)


def shown_quote(item: dict) -> str:
    """Quote text. A flagged generic quote ends with the literal [sample] tag."""
    quote = str((item or {}).get("quote") or "").strip()
    if is_sample_quote(item) and not quote.endswith(SAMPLE_TAG) and is_generic_praise(quote):
        return quote + " " + SAMPLE_TAG
    return quote


def quote_faults(html: str, copy_text: str = "") -> list[str]:
    """Faults for testimonial cards. Empty when every card is supplied or a clean sample."""
    norm = " ".join(str(copy_text or "").split())
    faults: list[str] = []
    parts = str(html or "").split("quote-card")
    for chunk in parts[1:]:
        match = re.search(r"<blockquote>(.*?)</blockquote>", chunk, re.S)
        if not match:
            continue
        quote = " ".join(re.sub(r"<[^>]+>", "", match.group(1)).split())
        tagged = quote.endswith(SAMPLE_TAG)
        avatar = 'class="avatar"' in chunk
        stars = "sc-stars" in chunk
        if tagged:
            body = quote[: -len(SAMPLE_TAG)].strip()
            if not is_generic_praise(body):
                faults.append("sample quote has an invented specific")
            elif norm and body not in norm:
                faults.append("sample praise is not in the copy")
            continue
        if avatar or stars:
            faults.append("initials avatar or stars on an untagged quote")
        elif norm and quote and quote not in norm:
            faults.append("quote is not supplied truth")
    return faults


def main() -> int:
    supplied = {"quote": "The desk kept the note.", "name": "Ada"}
    assert is_sample_quote(supplied) is False
    assert shown_quote(supplied) == "The desk kept the note."
    sample = {"quote": "Clear and careful work.", "sample": True}
    assert shown_quote(sample).endswith(SAMPLE_TAG)
    assert is_generic_praise("Clear and careful work.")
    assert is_generic_praise("Saved $20") is False
    clean = (
        '<div class="quote-card"><blockquote>Clear and careful work. [sample]</blockquote>'
        '<span class="avatar">CA</span><div class="sc-stars"></div></div>'
    )
    assert quote_faults(clean, "Clear and careful work.") == []
    invented = '<div class="quote-card"><blockquote>Saved $20 [sample]</blockquote></div>'
    assert quote_faults(invented, "Saved $20")
    bare = '<div class="quote-card"><blockquote>The desk kept the note.</blockquote><span class="avatar">A</span></div>'
    assert quote_faults(bare, "The desk kept the note.")
    print("proof selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
