"""Prove the studio refuses a fleet name, and that an accepted drop changes HTML.

Run from the engine root: python lib/studio_selftest.py
"""
from __future__ import annotations

import sys
import tempfile
import threading
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.compose import compose_project
from lib.structure import load_structure, save_structure
from lib.studio import RENDER, Desk, act, serve_studio

PROJECT = ROOT / "projects" / "demo-local"


def _fail(msg: str) -> int:
    print("studio selftest FAIL: " + msg)
    return 1


def _get(port: int, path: str) -> str:
    with urlopen(f"http://127.0.0.1:{port}{path}", timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def _pages(port: int) -> int:
    home = _get(port, "/")
    if home.count("<h1>") != 1:
        return _fail("desk does not have one h1")
    if 'href="#main"' not in home or "noindex" not in home:
        return _fail("desk is missing the skip link or noindex")
    if "demo-local" not in home or "bench-harbor-tearoom" not in home:
        return _fail("desk does not list both copy projects")
    if "<textarea" in home.lower():
        return _fail("desk has a text area")
    domains = _get(port, "/domains")
    if "iseark.com" not in domains or "May stage" not in domains and "May stage" not in domains:
        return _fail("staging list is missing")
    if "iseark.com" not in domains or "WordPress" not in domains:
        return _fail("iseark is not blocked")
    seo = _get(port, "/seo")
    if "does not clear noindex" not in seo:
        return _fail("seo desk can clear noindex")
    crew = _get(port, "/crew")
    if "not run" not in crew or "does not write library/ledger.json" not in crew:
        return _fail("crew board offers a run")
    if "<button" in crew and "Run crew" in crew:
        return _fail("crew board has a run button")
    for path in ("/plan", "/parts", "/preview", "/check", "/copy", "/mold", "/mobile", "/score"):
        page = _get(port, path)
        if page.count("<h1>") != 1:
            return _fail(f"{path} does not have one h1")
        if "noindex" not in page:
            return _fail(f"{path} is missing noindex")
    return 0


def _drop_paint() -> int:
    with tempfile.TemporaryDirectory(prefix="sc-studio-") as tmp:
        root = Path(tmp)
        plan = root / "plan"
        site = root / "site"
        refused = root / "refused"
        result = compose_project(
            PROJECT, plan, frame_id="welcome-scroll", mold_id="discover-grid", plan_only=True,
        )
        if not result.get("ok"):
            return _fail("plan failed: " + str(result.get("error")))
        if (plan / "index.html").is_file():
            return _fail("plan wrote HTML")
        data = load_structure(plan / "structure.json")
        sections = data["pages"][0]["sections"]
        if len(sections) < 2:
            return _fail("plan has fewer than two sections")
        dropped = sections.pop()
        save_structure(plan / "structure.json", data)
        painted = compose_project(
            PROJECT,
            site,
            frame_id="welcome-scroll",
            mold_id="discover-grid",
            accepted=plan / "structure.json",
        )
        if not painted.get("ok"):
            return _fail("paint failed: " + str(painted.get("error")))
        html = (site / "index.html").read_text(encoding="utf-8")
        needle = f'id="{dropped["id"]}"'
        if needle in html:
            return _fail("dropped section is still on the page")
        sections.append({"id": "pop", "type": "pricing", "part_id": "nope"})
        save_structure(plan / "structure.json", data)
        blocked = compose_project(
            PROJECT,
            refused,
            frame_id="welcome-scroll",
            mold_id="discover-grid",
            accepted=plan / "structure.json",
        )
        if blocked.get("ok"):
            return _fail("an added section was painted")
        if (refused / "index.html").is_file():
            return _fail("a refused paint wrote HTML")
    return 0


def _refuse_fleet() -> int:
    desk = Desk(ROOT)
    act(desk, {"action": "select", "project": "iseark"})
    if desk.project:
        return _fail("a fleet name was selected")
    if "not a copy pack" not in desk.error:
        return _fail("fleet refusal text is missing")
    act(desk, {"action": "plan", "project": "demo-local", "mold": "warmth-authority"})
    if "already live" not in desk.error:
        return _fail("warmth-authority was not refused")
    return 0


def _selected() -> int:
    for project in ("demo-local", "bench-harbor-tearoom"):
        desk = Desk(ROOT)
        act(desk, {"action": "select", "project": project})
        if desk.project != project:
            return _fail(f"{project} was not selected")
        for path, render in RENDER.items():
            try:
                html = render(desk)
            except Exception as exc:
                return _fail(f"{path} raised after selecting {project}: {exc}")
            if html.count("<h1>") != 1:
                return _fail(f"{path} does not have one h1 after selecting {project}")
            if "noindex" not in html:
                return _fail(f"{path} is missing noindex after selecting {project}")
    return 0


def main() -> int:
    httpd, port = serve_studio(port=0, root=ROOT)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        failed = _pages(port)
        if failed:
            return failed
    finally:
        httpd.shutdown()
        httpd.server_close()
    failed = _refuse_fleet()
    if failed:
        return failed
    failed = _selected()
    if failed:
        return failed
    failed = _drop_paint()
    if failed:
        return failed
    print("studio selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
