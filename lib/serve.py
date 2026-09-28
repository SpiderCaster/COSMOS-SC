"""Tiny static preview server (stdlib only). Port auto-increments if busy."""
from __future__ import annotations

import http.server
import socketserver
from pathlib import Path

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".txt": "text/plain; charset=utf-8",
}


def serve(site_dir: Path, port: int = 4173, attempts: int = 20) -> tuple[socketserver.TCPServer, int]:
    site_dir = Path(site_dir).resolve()

    class Handler(http.server.SimpleHTTPRequestHandler):
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, **MIME}

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(site_dir), **kwargs)

    last_exc: Exception | None = None
    for p in range(port, port + attempts):
        try:
            httpd = socketserver.ThreadingTCPServer(("127.0.0.1", p), Handler)
            httpd.daemon_threads = True
            return httpd, p
        except OSError as exc:
            last_exc = exc
    raise RuntimeError(f"no free port in {port}..{port + attempts - 1} ({last_exc})")
