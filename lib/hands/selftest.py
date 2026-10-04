"""Run from the SpiderCaster working tree: py -3.14 -m lib.hands.selftest"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from lib.crew import ROLES
from lib.hands import HANDS, _copy_citation
from lib.ingest import Block, Copy
from lib.library import Library, LibraryError

ORDER = [name for role in ROLES for name in role["hands"]]

# Real 1x1 RGBA PNG. Bytes only; not a download.
TINY_PNG = bytes((
    137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82,
    0, 0, 0, 1, 0, 0, 0, 1, 8, 6, 0, 0, 0, 31, 21, 196, 137,
    0, 0, 0, 13, 73, 68, 65, 84, 120, 218, 99, 96, 96, 96, 96,
    0, 0, 0, 5, 0, 1, 122, 168, 87, 80, 0, 0, 0, 0, 73, 69, 78, 68,
    174, 66, 96, 130,
))


def main() -> int:
    if list(HANDS) != ORDER:
        raise SystemExit("HANDS is not the crew order")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        project = root / "project"
        (project / "copy").mkdir(parents=True)
        (project / "brief.md").write_text(
            "# Brief\n\nA harbor tea room with a quiet counter and local pages only.\n",
            encoding="utf-8",
        )
        (project / "copy" / "overview.md").write_text(
            "# Harbor Tea Room\n\n"
            "The harbor tea room pours afternoon tea from a quiet counter on the dock.\n\n"
            "Guests sit by the window and watch the small boats while the kettle finishes.\n",
            encoding="utf-8",
        )
        pkg = root / "pkg"
        vault = root / "vault"
        out = root / "site"
        ctx = {
            "project": str(project),
            "site": "hands-demo.example",
            "out": str(out),
            "mold_id": "",
            "vault": str(vault),
            "package_library": str(pkg),
            "live": False,
            "palette": "#1f6f5b",
            "type_lead": "serif",
            "nav": "segmented",
            "template": "editorial",
            "hands": [],
            "frame_id": "service-counter",
        }
        for name in ORDER:
            result = HANDS[name](ctx)
            status = result.get("status")
            if status not in {"PASS", "FAIL", "SKIP"} or "detail" not in result or not isinstance(result.get("data"), dict):
                raise SystemExit(f"{name} returned a bad result")
            if name == "frame_pick" and "service-counter" not in result["detail"]:
                raise SystemExit("frame_pick did not name service-counter")
            if name == "copy_read" and "copy/overview.md" not in result["detail"]:
                raise SystemExit("copy_read did not cite copy/overview.md")
            if name != "ticket_write":
                ctx["hands"].append({
                    "hand": name,
                    "status": status,
                    "detail": result["detail"],
                })
            if status == "FAIL":
                raise SystemExit(f"{name} FAIL: {result['detail']}")
        ticket_path = out / "crew-ticket.json"
        if not ticket_path.is_file():
            raise SystemExit("crew-ticket.json was not written")
        ticket = json.loads(ticket_path.read_text(encoding="utf-8"))
        if not ticket.get("ok"):
            raise SystemExit("ticket not ok")
        index = out / "index.html"
        if not index.is_file():
            raise SystemExit("index.html was not written")
        html = index.read_text(encoding="utf-8")
        for needle in ("hero-visual", "site-header", "is-stuck", "favicon.svg", 'rel="icon"'):
            if needle not in html:
                raise SystemExit(f"index missing {needle}")
        if not (out / "favicon.svg").is_file():
            raise SystemExit("favicon.svg was not written")
        if "hero-visual hero-mark" not in html:
            raise SystemExit("letter mark missing when no local hero")
        mold_id = ctx["mold_id"]
        lib = Library(pkg, vault)
        lib.bind("hands-demo.example", mold_id, live=True)
        try:
            lib.bind("other.example", mold_id, live=True)
        except LibraryError:
            pass
        else:
            raise SystemExit("second live bind was allowed")
        remote = root / "remote"
        remote.mkdir()
        (remote / "assets").mkdir()
        (remote / "assets" / "hero.png").write_bytes(TINY_PNG)
        (remote / "assets.json").write_text(
            json.dumps({"images": {"hero": "https://cdn.example.com/hero.jpg"}}),
            encoding="utf-8",
        )
        remote_ctx = {
            "project": str(remote),
            "site": ctx["site"],
            "out": str(out),
            "mold_id": mold_id,
            "vault": str(vault),
            "package_library": str(pkg),
            "live": False,
        }
        got = HANDS["asset_list"](remote_ctx)
        if got["status"] != "FAIL":
            raise SystemExit("remote asset url was allowed")
        if "assets/hero.png" not in got["data"].get("local", []):
            raise SystemExit("asset_list did not report the local hero")
        missing = HANDS["frame_pick"]({"frame_id": "nope-missing"})
        if missing.get("status") != "FAIL":
            raise SystemExit("missing frame was allowed")
        outside = Copy()
        leaked = Block(r"..\secret.md", 1, "no")
        leaked.paragraphs = ["not from this project"]
        outside.blocks = [leaked]
        _files, bad = _copy_citation(project, outside)
        if not bad:
            raise SystemExit("a block file outside copy/ was accepted")
        (project / "assets").mkdir()
        (project / "assets" / "hero.png").write_bytes(TINY_PNG)
        painted = HANDS["render"](ctx)
        if painted.get("status") != "PASS":
            raise SystemExit(f"render with local hero FAIL: {painted.get('detail')}")
        html = (out / "index.html").read_text(encoding="utf-8")
        for needle in ("hero-visual", "site-header", "is-stuck", "favicon.svg", 'rel="icon"'):
            if needle not in html:
                raise SystemExit(f"index missing {needle}")
        if 'src="assets/hero.png"' not in html:
            raise SystemExit("hero img src is not assets/hero.png")
        if "hero-visual hero-mark" in html:
            raise SystemExit("letter mark used even though assets/hero.png exists")
        copied = out / "assets" / "hero.png"
        if not copied.is_file() or copied.read_bytes() != TINY_PNG:
            raise SystemExit("local hero was not copied into the output")
        if not (out / "favicon.svg").is_file():
            raise SystemExit("favicon.svg was not written")
        listed = HANDS["asset_list"](ctx)
        if listed.get("status") != "PASS" or "assets/hero.png" not in listed["data"].get("local", []):
            raise SystemExit("asset_list did not report assets/hero.png")
    print("hands selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
