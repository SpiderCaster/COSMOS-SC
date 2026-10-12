"""Prove project_copy_text. Run from the engine root: python lib/copy_pack_selftest.py"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.copy_pack import project_copy_text

DEMO = Path(r"V:\A\Ai\spidercaster\working\projects\demo-local")
DEMO_SENTENCE = "SpiderCaster is a copy-driven static website engine."
BRIEF_ONLY = "Audience: Keith and the free-model seats."


def _fail(msg: str) -> int:
    print("copy_pack selftest FAIL: " + msg)
    return 1


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _temp_project(root: Path) -> Path:
    project = root / "proj"
    _write(project / "brief.md", "BRIEF_ONLY_MARKER " + BRIEF_ONLY + "\n")
    _write(project / "notes.txt", "ROOT_TXT_MARKER\n")
    _write(project / "copy" / "b.txt", "beta body\n")
    _write(project / "copy" / "a.md", "alpha body\n")
    _write(project / "copy" / "c.markdown", "gamma body\n")
    _write(project / "copy" / "extra.TXT", "upper suffix body\n")
    _write(project / "copy" / "skip.json", "JSON_ONLY_MARKER\n")
    _write(project / "copy" / "skip.html", "HTML_ONLY_MARKER\n")
    _write(project / "copy" / "nested" / "deep.md", "NESTED_ONLY_MARKER\n")
    return project


def main() -> int:
    if project_copy_text(ROOT / "no-such-project") != "":
        return _fail("missing project did not return empty")
    if project_copy_text(ROOT) != "":
        return _fail("engine root has no copy/ and should return empty")

    with tempfile.TemporaryDirectory(prefix="sc-copy-pack-") as tmp:
        root = Path(tmp)
        bare = root / "bare"
        bare.mkdir()
        if project_copy_text(bare) != "":
            return _fail("missing copy directory did not return empty")
        empty = root / "empty-copy"
        (empty / "copy").mkdir(parents=True)
        if project_copy_text(empty) != "":
            return _fail("empty copy directory did not return empty")
        (root / "not-a-dir").write_text("x", encoding="utf-8")
        copy_file = root / "file-project"
        copy_file.mkdir()
        (copy_file / "copy").write_text("not a directory", encoding="utf-8")
        if project_copy_text(copy_file) != "":
            return _fail("copy path that is a file did not return empty")

        project = _temp_project(root)
        text = project_copy_text(project)
        expected = "\n".join((
            "alpha body\n",
            "beta body\n",
            "gamma body\n",
            "upper suffix body\n",
        ))
        if text != expected:
            return _fail("temp join mismatch: " + repr(text))
        for banned in (
            "BRIEF_ONLY_MARKER",
            "ROOT_TXT_MARKER",
            "JSON_ONLY_MARKER",
            "HTML_ONLY_MARKER",
            "NESTED_ONLY_MARKER",
        ):
            if banned in text:
                return _fail("included excluded text: " + banned)

    demo = project_copy_text(DEMO)
    if not demo.strip():
        return _fail("demo-local copy is empty")
    if DEMO_SENTENCE not in demo:
        return _fail("demo-local copy is missing the overview sentence")
    commands = demo.find("# Commands")
    faq = demo.find("# Questions about the engine")
    overview = demo.find("# SpiderCaster: websites from real copy, on free tokens")
    if commands < 0 or faq < 0 or overview < 0 or not (commands < faq < overview):
        return _fail("demo-local files are not all present in name order")
    if BRIEF_ONLY in demo:
        return _fail("demo-local brief leaked into copy text")

    print("copy_pack selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
