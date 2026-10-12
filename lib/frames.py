"""Package section frames. A frame is an original section order, not a mold and not a vendor theme."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.ir import SECTION_TYPES, TEMPLATES

SCHEMA = "spidercaster-frame/1"
NAVS = ("segmented", "top-bar", "sidebar", "one-page", "footer-only")
_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_KEYS = {"schema", "id", "intent", "sections", "nav", "template", "package", "note",
         # Step-1 gap-gate slot flags (v2 frames). v1 files carry none of
         # these; the engine default (hero required, rest optional) applies.
         "required", "optional", "mandatory_sections", "optional_sections", "slots"}
_PACKAGE_IDS = (
    "service-counter", "shop-shelf", "kitchen-board", "proof-letter",
    "local-desk", "catalog-front", "house-menu", "project-index",
    "visit-book", "welcome-scroll", "hours-stack", "practice-intro",
    "trust-lane", "maker-shelf",
)

#: FINAL D4 conversion slot order (offer -> proof -> ask). Proof sections
#: make the case; ask sections (contact/cta) close it and always come last.
PROOF_TYPES = ("features", "stats", "testimonials", "faq")
ASK_TYPES = ("contact", "cta")


def check_ask_after_proof(sections: list) -> str:
    """Empty when no ask section precedes a proof section, else a FAIL line.

    Pure, stdlib, zero tokens. Vacuous PASS when the page has no ask slot
    or no proof slot: the order rule only binds pages that make and close
    a case.
    """
    if not isinstance(sections, list):
        return ""
    kinds = [
        str(sec.get("type") or "") if isinstance(sec, dict) else ""
        for sec in sections
    ]
    proof_at = [i for i, kind in enumerate(kinds) if kind in PROOF_TYPES]
    if not proof_at:
        return ""
    last_proof = max(proof_at)
    for i, kind in enumerate(kinds):
        if kind in ASK_TYPES and i < last_proof:
            sec_id = ""
            if isinstance(sections[i], dict):
                sec_id = str(sections[i].get("id") or kind)
            late = kinds[last_proof]
            return f"ask {sec_id or kind} before proof {late} (offer->proof->ask)"
    return ""


class FrameError(Exception):
    pass


def frames_dir() -> Path:
    env = os.environ.get("SPIDERCASTER_HOME")
    if env:
        candidate = Path(env) / "library" / "frames"
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parent.parent / "library" / "frames"


def _validate(data, source_id: str | None = None) -> dict:
    if not isinstance(data, dict):
        raise FrameError("frame is not an object")
    extra = set(data) - _KEYS
    if extra or "palette" in data or "parents" in data:
        raise FrameError("a frame has no palette, parents, or private fields")
    if data.get("schema") != SCHEMA:
        raise FrameError("bad schema")
    if data.get("package") is not True:
        raise FrameError("not a package frame")
    fid = data.get("id")
    if not isinstance(fid, str) or not _ID.fullmatch(fid):
        raise FrameError("bad id")
    if source_id is not None and fid != source_id:
        raise FrameError("id does not match file")
    intent = data.get("intent")
    if not isinstance(intent, str) or not intent.strip():
        raise FrameError("intent is required")
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        raise FrameError("sections are required")
    if any(not isinstance(kind, str) for kind in sections):
        raise FrameError("sections must be type names")
    if sections[0] != "hero":
        raise FrameError("sections must start with hero")
    if len(sections) != len(set(sections)):
        raise FrameError("sections must be unique")
    if any(kind not in SECTION_TYPES for kind in sections):
        raise FrameError("unknown section")
    if data.get("nav") not in NAVS:
        raise FrameError("bad nav")
    if data.get("template") not in TEMPLATES:
        raise FrameError("bad template")
    note = data.get("note")
    if note is not None and not isinstance(note, str):
        raise FrameError("bad note")
    if isinstance(note, str) and (":" in note or "\\" in note or "/" in note):
        raise FrameError("note is not public")
    public = {
        "schema": SCHEMA,
        "id": fid,
        "intent": intent.strip(),
        "sections": list(sections),
        "nav": data["nav"],
        "template": data["template"],
        "package": True,
    }
    if isinstance(note, str) and note.strip():
        public["note"] = note.strip()
    # Forward v2 slot flags when a frame states them; validated lightly so
    # v1 files (no flags) pass through unchanged. copy_schema.slots_for_frame
    # is the single interpreter of these flags.
    for key in ("required", "optional", "mandatory_sections", "optional_sections"):
        val = data.get(key)
        if isinstance(val, list) and val and all(isinstance(x, str) and x in SECTION_TYPES for x in val):
            public[key] = list(val)
    slots = data.get("slots")
    if isinstance(slots, list) and slots:
        clean = []
        for entry in slots:
            if not isinstance(entry, dict):
                continue
            name = entry.get("section")
            if name not in SECTION_TYPES:
                continue
            clean.append({"section": name, "required": entry.get("required") is True})
        if clean:
            public["slots"] = clean
    return public


def slots_for_frame(frame: dict | None) -> dict:
    """Slot contract for a frame dict. Thin wrapper over copy_schema."""
    from lib.copy_schema import slots_for_frame as _slots
    return _slots(frame)


def list_frames() -> list[dict]:
    root = frames_dir()
    if not root.is_dir():
        return []
    out = []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            out.append(_validate(data, path.stem))
        except (OSError, ValueError, FrameError):
            continue
    return out


def load_frame(frame_id: str) -> dict:
    fid = str(frame_id or "").strip()
    if not _ID.fullmatch(fid):
        raise FrameError(f"unknown frame {fid or frame_id}")
    path = frames_dir() / f"{fid}.json"
    if not path.is_file():
        raise FrameError(f"unknown frame {fid}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise FrameError(f"unknown frame {fid}") from exc
    try:
        return _validate(data, fid)
    except FrameError as exc:
        raise FrameError(f"frame {fid} is not a package frame") from exc


def apply_frame(planned_sections: list[dict], frame: dict) -> list[dict]:
    """Keep planned sections the frame names, in frame order. Never invent one."""
    if not isinstance(planned_sections, list):
        return planned_sections
    wanted = frame.get("sections") if isinstance(frame, dict) else None
    if not isinstance(wanted, list) or "hero" not in wanted:
        return planned_sections
    has_hero = any(isinstance(sec, dict) and sec.get("type") == "hero" for sec in planned_sections)
    if not has_hero:
        return planned_sections
    buckets: dict[str, list[dict]] = {}
    for sec in planned_sections:
        if not isinstance(sec, dict):
            continue
        kind = sec.get("type")
        if isinstance(kind, str) and kind:
            buckets.setdefault(kind, []).append(sec)
    ordered: list[dict] = []
    for kind in wanted:
        found = buckets.get(kind)
        if found:
            ordered.append(found.pop(0))
    _keep_dropped_hours(planned_sections, ordered)
    return ordered


def _hours_lines(section: dict) -> list[str]:
    """Sentences from a block titled Hours. Other dropped blocks stay dropped."""
    data = section.get("data") if isinstance(section, dict) else None
    if not isinstance(data, dict):
        return []
    title = str(data.get("title") or "").strip()
    if title.casefold() != "hours" and section.get("id") != "hours":
        return []
    body = data.get("body")
    if isinstance(body, str):
        return [body.strip()] if body.strip() else []
    if not isinstance(body, list):
        return []
    return [item.strip() for item in body if isinstance(item, str) and item.strip()]


def _keep_dropped_hours(planned: list[dict], kept: list[dict]) -> None:
    """A frame that omits Hours still shows those sentences on Contact.

    hours-stack says hours stay with the place line. The planner stores a
    separate Hours block. That block is not a new section here. Its sentences
    are copied onto the contact row the frame already kept, and only when
    that row has no hours line of its own.
    """
    contact = next((sec for sec in kept if isinstance(sec, dict) and sec.get("type") == "contact"), None)
    if not isinstance(contact, dict):
        return
    data = contact.get("data")
    if not isinstance(data, dict):
        return
    if str(data.get("hours") or "").strip():
        return
    kept_ids = {id(sec) for sec in kept}
    lines: list[str] = []
    for sec in planned:
        if not isinstance(sec, dict) or id(sec) in kept_ids:
            continue
        lines.extend(_hours_lines(sec))
    if lines:
        data["hours"] = " ".join(lines)


def _selftest() -> int:
    frames = list_frames()
    ids = {frame["id"] for frame in frames}
    if ids != set(_PACKAGE_IDS):
        raise SystemExit("frame list is not the package frames: " + ", ".join(sorted(ids)))
    frame = load_frame("service-counter")
    planned = [
        {"type": "hero", "id": "hero", "data": {"headline": "Counter"}},
        {"type": "menu", "id": "menu", "data": {"title": "Menu"}},
        {"type": "faq", "id": "faq", "data": {"title": "Questions"}},
    ]
    got = apply_frame(planned, frame)
    kinds = [sec["type"] for sec in got]
    if "menu" in kinds or "hero" not in kinds:
        raise SystemExit("service-counter did not drop menu and keep hero")
    if kinds != ["hero", "faq"]:
        raise SystemExit("frame order was not applied")
    bare = [
        {"type": "hero", "id": "hero", "data": {"headline": "Counter"}},
        {"type": "features", "id": "features", "data": {"title": "Work"}},
    ]
    if any(sec.get("type") == "pricing" for sec in apply_frame(bare, frame)):
        raise SystemExit("pricing was invented")
    no_hero = [{"type": "menu", "id": "menu"}]
    if apply_frame(no_hero, frame) is not no_hero:
        raise SystemExit("planned list changed when hero was missing")
    try:
        load_frame("nope-missing")
    except FrameError:
        pass
    else:
        raise SystemExit("unknown id did not raise")
    hours_frame = load_frame("hours-stack")
    planned_hours = [
        {"type": "hero", "id": "hero", "data": {"headline": "Harbor"}},
        {"type": "menu", "id": "menu", "data": {"title": "Menu"}},
        {
            "type": "about",
            "id": "hours",
            "data": {
                "title": "Hours",
                "body": ["Open Tuesday to Sunday, 8am to 6pm.", "Closed Mondays."],
            },
        },
        {"type": "contact", "id": "contact", "data": {"title": "Contact", "hours": ""}},
    ]
    got_hours = apply_frame(planned_hours, hours_frame)
    if any(sec.get("id") == "hours" for sec in got_hours):
        raise SystemExit("hours-stack kept a section the frame does not name")
    contact = next(sec for sec in got_hours if sec.get("type") == "contact")
    expected = "Open Tuesday to Sunday, 8am to 6pm. Closed Mondays."
    if contact["data"].get("hours") != expected:
        raise SystemExit("dropped hours copy was not kept on contact")
    planned_hours[3]["data"]["hours"] = "Open Tuesday to Sunday."
    again = apply_frame(planned_hours, hours_frame)
    kept_contact = next(sec for sec in again if sec.get("type") == "contact")
    if kept_contact["data"].get("hours") != "Open Tuesday to Sunday.":
        raise SystemExit("an existing contact hours line was replaced")
    print("frames selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
