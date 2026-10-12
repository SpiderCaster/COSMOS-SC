"""Strict frame/mold copy schema + gap-gate compiler (step 1).

Stdlib only. Zero tokens. No deploys. No key values.

Contract (round2 3.4 / 3.5 / 3.9-step-1):
- Required miss is a hard FAIL: ``FAIL gap <section>.<field>`` on stderr,
  exit code 1, and no HTML is emitted with a substitute sentence.
- Optional miss is a clean omit: the section is left out of the IR.
- Silent about-fallback for a missing *required* field is forbidden.
  Cited leftover prose may still render as about-style text.

Step-1 scope (engine default until a frame states otherwise):
- Required sections: ["hero"]. A v2 frame may add more via explicit
  required flags; v1 frames (schema spidercaster-frame/1) carry no flags,
  so stats/testimonials/etc. stay optional and are omitted when the copy
  has nothing real for them.
- Required fields: hero.headline (non-empty span). Other required page
  fields (hero.lead, primary_action.*) are documented here but enforced
  only when a frame marks their slot required, so existing offline
  fixtures without contact blocks keep building.
- Section integrity: a block that *asks* for faq/pricing/menu/contact but
  carries none of that section's required data is a gap FAIL, not an
  about section. E.g. a "Pricing" heading with zero price rows is
  ``FAIL gap pricing.items``, not generic prose.
"""

from __future__ import annotations

import json
from pathlib import Path


class GapError(SystemExit):
    """Missing required copy. str() is the FAIL gap line.

    Subclasses SystemExit so the existing ``except SystemExit`` handlers
    in spidercaster.py / lib/hands / lib/compose convert it to a FAIL
    without writing HTML.
    """

    def __init__(self, section: str, field: str, detail: str = ""):
        self.section = str(section or "hero")
        self.field = str(field or "headline")
        line = f"FAIL gap {self.section}.{self.field}"
        if detail:
            line += f" ({detail})"
        super().__init__(line)


def gap_line(section: str, field: str) -> str:
    return f"FAIL gap {section}.{field}"


# ---------------------------------------------------------------------------
# Frame slot table
#
# v1 frame JSON: {"schema": "spidercaster-frame/1", "sections": [...]}.
# No required flags exist in v1 (base silent), so the engine default is the
# contract: hero required, every other listed slot optional.
#
# v2 (forward-compatible, honored when present):
#   {"required": ["hero", "contact"], "optional": ["faq", ...]}
#   or {"mandatory_sections": [...], "optional_sections": [...]}
#   or {"slots": [{"section": "hero", "required": true}, ...]}
# ---------------------------------------------------------------------------

def _as_section_list(value) -> list[str] | None:
    if not isinstance(value, list):
        return None
    out = [s for s in value if isinstance(s, str) and s.strip()]
    return out or None


def slots_for_frame(frame: dict | None) -> dict:
    """Return {"required": [...], "optional": [...]} for a frame dict.

    frame may be None (copy order, no frame bound) or a v1/v2 frame dict.
    Unknown section names are ignored. hero is always required.
    """
    if not isinstance(frame, dict):
        return {"required": ["hero"], "optional": []}
    sections = _as_section_list(frame.get("sections")) or []
    required: list[str] = []
    optional: list[str] = []

    slots = frame.get("slots")
    if isinstance(slots, list) and slots:
        for entry in slots:
            if not isinstance(entry, dict):
                continue
            name = entry.get("section")
            if not isinstance(name, str) or not name.strip():
                continue
            name = name.strip()
            if entry.get("required") is True:
                if name not in required:
                    required.append(name)
            else:
                if name not in optional and name not in required:
                    optional.append(name)
    else:
        for key in ("required", "mandatory_sections"):
            found = _as_section_list(frame.get(key))
            if found:
                required.extend(s for s in found if s not in required)
        for key in ("optional", "optional_sections"):
            found = _as_section_list(frame.get(key))
            if found:
                optional.extend(s for s in found if s not in optional and s not in required)
        if not required and not optional and sections:
            optional = [s for s in sections if s != "hero"]
    if "hero" not in required:
        required.insert(0, "hero")
    optional = [s for s in optional if s != "hero"]
    return {"required": required, "optional": optional}


def load_frame_slots(frame_id: str | None) -> dict:
    """Read library/frames/<id>.json slots. Unknown id -> engine default."""
    fid = str(frame_id or "").strip()
    if not fid:
        return {"required": ["hero"], "optional": [], "frame_id": ""}
    path = Path(__file__).resolve().parent.parent / "library" / "frames" / f"{fid}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"required": ["hero"], "optional": [], "frame_id": fid}
    slots = slots_for_frame(data)
    slots["frame_id"] = data.get("id") if isinstance(data, dict) else fid
    return slots


# ---------------------------------------------------------------------------
# Field-level required map (step 1: hero.headline enforced; the rest are
# recorded here so frames can promote them to required without code changes).
# ---------------------------------------------------------------------------

SECTION_REQUIRED_FIELDS: dict[str, list[str]] = {
    "hero": ["headline"],
    "contact": [],
    "cta": [],
    "faq": [],
    "pricing": [],
    "menu": [],
}

OPTIONAL_SECTIONS = (
    "features", "stats", "steps", "gallery", "pricing", "testimonials",
    "faq", "about", "team", "menu", "logocloud", "cta",
)

ITEMS_SECTIONS = frozenset({
    "faq", "pricing", "menu", "features", "stats", "steps",
    "gallery", "team", "testimonials", "logocloud",
})

CONTACT_FACT_FIELDS = ("body", "email", "phone", "address", "hours")


def _text_present(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_text_present(v) for v in value)
    if isinstance(value, dict):
        return any(_text_present(v) for v in value.values())
    return bool(value)


def _hero_headline(site: dict) -> str:
    try:
        pages = site.get("pages") or []
        sections = pages[0].get("sections") or []
    except (AttributeError, IndexError, KeyError, TypeError):
        return ""
    for sec in sections:
        if isinstance(sec, dict) and sec.get("type") == "hero":
            data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
            return str(data.get("headline") or "").strip()
    return ""


def validate_site(site: dict, frame: dict | None = None,
                  frame_id: str | None = None) -> list[str]:
    """List missing ``section.field`` entries. Empty list means no gap.

    Step-1 enforcement:
    - hero.headline must be a non-empty span.
    - Any frame-required section (v2) must be present with content.
    - Integrity: faq/pricing/menu/contact sections present but empty of
      their required data are reported as <section>.items / contact.body.
    """
    missing: list[str] = []
    if not isinstance(site, dict):
        return ["hero.headline"]
    if not _text_present(_hero_headline(site)):
        missing.append("hero.headline")

    slots = slots_for_frame(frame) if isinstance(frame, dict) else load_frame_slots(frame_id)
    required = [s for s in slots.get("required", []) if s != "hero"]
    try:
        pages = site.get("pages") or []
        sections = pages[0].get("sections") or [] if pages else []
    except (AttributeError, IndexError, TypeError):
        sections = []
    by_type: dict[str, list[dict]] = {}
    for sec in sections:
        if isinstance(sec, dict) and isinstance(sec.get("type"), str):
            by_type.setdefault(sec["type"], []).append(sec)
    for name in required:
        present = [s for s in by_type.get(name, [])
                   if _section_has_content(name, s.get("data"))]
        if not present:
            suffix = "items" if name in ITEMS_SECTIONS else "body"
            missing.append(f"{name}.{suffix}")
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        kind = sec.get("type")
        data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
        if kind == "faq" and not (data.get("items") or []):
            missing.append("faq.items")
        elif kind == "pricing" and not (data.get("items") or []):
            missing.append("pricing.items")
        elif kind == "menu" and not (data.get("groups") or []):
            missing.append("menu.items")
        elif kind == "contact" and not any(
                str(data.get(k) or "").strip()
                for k in CONTACT_FACT_FIELDS):
            missing.append("contact.body")
    seen: set[str] = set()
    ordered = [m for m in missing if not (m in seen or seen.add(m))]
    return ordered


def _section_has_content(kind: str, data) -> bool:
    if not isinstance(data, dict):
        return False
    if kind == "hero":
        return bool(str(data.get("headline") or "").strip())
    if kind in ("features", "stats", "steps", "testimonials", "team"):
        return bool(data.get("items"))
    if kind == "faq":
        return bool(data.get("items"))
    if kind == "pricing":
        return bool(data.get("items"))
    if kind == "menu":
        return bool(data.get("groups"))
    if kind == "gallery":
        return bool(data.get("items"))
    if kind == "logocloud":
        return bool(data.get("items"))
    if kind == "contact":
        return any(str(data.get(k) or "").strip()
                   for k in CONTACT_FACT_FIELDS)
    if kind == "cta":
        return bool(str(data.get("title") or "").strip() or data.get("primary"))
    if kind == "about":
        return bool(data.get("body") or data.get("points"))
    return bool(data)


def raise_first_gap(site: dict, frame: dict | None = None,
                    frame_id: str | None = None) -> None:
    missing = validate_site(site, frame=frame, frame_id=frame_id)
    if missing:
        section, _, field = missing[0].partition(".")
        raise GapError(section, field or "body")


# ---------------------------------------------------------------------------
# --from re-read: citations stored by the strict planner are re-sliced
# against copy/ files. Legacy site.json without citations passes through
# so old rebuilds keep working.
# ---------------------------------------------------------------------------

def verify_citations(site: dict, project_dir) -> list[str]:
    """Return missing gap names when cited spans no longer resolve.

    citations shape: {section_id: {"file": "overview.md", "texts": [str]}}.
    Each text must occur verbatim in copy/<file>. A missing copy dir, a
    missing file, or a text that no longer occurs is
    ``<section>.citation`` (reported against the section id's type when
    known, else the id).
    """
    if not isinstance(site, dict):
        return []
    citations = site.get("citations")
    if not citations:
        return []
    if not isinstance(citations, dict):
        return []
    try:
        copy_dir = Path(project_dir) / "copy"
    except TypeError:
        return []
    if not copy_dir.is_dir():
        return [f"{sec}.citation" for sec in citations]
    try:
        pages = site.get("pages") or []
        sections = pages[0].get("sections") or [] if pages else []
    except (AttributeError, IndexError, TypeError):
        sections = []
    type_by_id = {s.get("id"): s.get("type") for s in sections if isinstance(s, dict)}
    missing: list[str] = []
    for sec_id, cite in citations.items():
        if not isinstance(cite, dict):
            continue
        fname = str(cite.get("file") or "")
        texts = cite.get("texts") or []
        if not fname or ".." in fname.replace("\\", "/").split("/") or fname.startswith("/"):
            missing.append(f"{sec_id}.citation")
            continue
        path = copy_dir / fname
        if not path.is_file():
            missing.append(f"{sec_id}.citation")
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            missing.append(f"{sec_id}.citation")
            continue
        kind = type_by_id.get(sec_id, sec_id)
        for text in texts if isinstance(texts, list) else []:
            if isinstance(text, str) and text.strip() and text not in content:
                missing.append(f"{kind}.citation")
                break
    seen: set[str] = set()
    return [m for m in missing if not (m in seen or seen.add(m))]


def _selftest() -> int:
    # slots: v1 default is hero-required, rest optional
    assert slots_for_frame(None) == {"required": ["hero"], "optional": []}
    assert slots_for_frame({"sections": ["hero", "stats", "faq"]}) == {
        "required": ["hero"], "optional": ["stats", "faq"]}
    v2 = {"sections": ["hero", "contact", "faq"],
          "required": ["hero", "contact"], "optional": ["faq"]}
    assert slots_for_frame(v2)["required"] == ["hero", "contact"]
    assert slots_for_frame({"slots": [
        {"section": "hero", "required": True},
        {"section": "faq", "required": False},
    ]}) == {
        "required": ["hero"], "optional": ["faq"]}

    site_ok = {"pages": [{"sections": [
        {"id": "hero", "type": "hero", "data": {"headline": "Harbor Tea"}}]}]}
    assert validate_site(site_ok) == []
    site_blank = {"pages": [{"sections": [
        {"id": "hero", "type": "hero", "data": {"headline": "  "}}]}]}
    assert validate_site(site_blank) == ["hero.headline"]
    try:
        raise_first_gap(site_blank)
    except GapError as exc:
        assert str(exc) == "FAIL gap hero.headline", str(exc)
    else:
        raise SystemExit("blank hero did not raise")

    # optional miss is omit, not fail: no stats section, no gap
    assert validate_site(site_ok) == []
    # empty optional sections present-but-empty are integrity gaps
    site_empty_faq = {"pages": [{"sections": [
        {"id": "hero", "type": "hero", "data": {"headline": "T"}},
        {"id": "faq", "type": "faq", "data": {"title": "Q", "items": []}}]}]}
    assert "faq.items" in validate_site(site_empty_faq)

    # citations: legacy without citations passes
    assert verify_citations(site_ok, ".") == []
    print("copy_schema selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
