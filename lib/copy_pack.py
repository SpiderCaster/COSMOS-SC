"""Concatenated project copy. Does not read the brief or keys."""
from __future__ import annotations

from pathlib import Path

_COPY_SUFFIXES = {".md", ".markdown", ".txt"}


def project_copy_text(project: Path) -> str:
    """Join project/copy files (.md, .markdown, .txt) in name order.

    A missing copy directory returns "". Other suffixes and the project
    brief are not included. Only files directly inside copy/ are read.
    """
    copy_dir = Path(project) / "copy"
    if not copy_dir.is_dir():
        return ""
    files = sorted(
        (
            path
            for path in copy_dir.iterdir()
            if path.is_file() and path.suffix.lower() in _COPY_SUFFIXES
        ),
        key=lambda path: path.name,
    )
    parts = [path.read_text(encoding="utf-8") for path in files]
    return "\n".join(parts)
