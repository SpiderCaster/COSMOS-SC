"""Refuse a hand unless the caller is that seat. Does not call the hand."""
from __future__ import annotations

from lib.crew import ROLES

_BY_ID = {role["id"]: role for role in ROLES}


def seat_gate(caller: str, seat: str, hand: str) -> dict:
    """Allow only when caller is seat and hand is on that seat's ROLES list."""
    role = _BY_ID.get(seat) if isinstance(seat, str) else None
    hands = role["hands"] if role is not None else ()
    same = isinstance(caller, str) and isinstance(seat, str) and caller == seat
    known = isinstance(hand, str) and hand in hands
    allowed = role is not None and same and known
    if allowed:
        error = ""
    elif role is None:
        error = "unknown seat"
    elif not same:
        error = "caller differs from seat"
    else:
        error = "unknown hand"
    return {
        "seat": seat,
        "hand": hand,
        "allowed": allowed,
        "ok": allowed,
        "error": error,
    }


def main() -> int:
    picked = seat_gate("architect", "architect", "frame_pick")
    assert picked == {
        "seat": "architect",
        "hand": "frame_pick",
        "allowed": True,
        "ok": True,
        "error": "",
    }
    rendered = seat_gate("architect", "architect", "render")
    assert rendered["allowed"] is False and rendered["ok"] is False
    crossed = seat_gate("content", "architect", "frame_pick")
    assert crossed["allowed"] is False and crossed["ok"] is False
    listed = seat_gate("architect", "architect", "frame_list")
    assert listed["allowed"] is False and listed["ok"] is False
    assert _BY_ID["architect"]["hands"] == [
        "brief_read",
        "frame_pick",
        "mold_pick",
        "library_bind",
    ]
    print("seat_gate selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
