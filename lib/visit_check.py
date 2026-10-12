"""Visit checks for one SpiderCaster page.

Static checks always run. When Playwright can launch a browser, visit_site
also measures the local index at 360x800 and 1280x800. A missing browser is
not a failure.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

_VIEWPORTS = ((360, 800), (1280, 800))
_WIDTH = re.compile(r"(?<![\w-])width\s*:\s*([0-9]*\.?[0-9]+)\s*px\b", re.IGNORECASE)
_MIN_WIDTH = re.compile(r"(?<![\w-])min-width\s*:\s*([0-9]*\.?[0-9]+)\s*px\b", re.IGNORECASE)
_ROOT = re.compile(r"^(?:body|html)(?![\w-])", re.IGNORECASE)
_IS = re.compile(r"^:(?:is|where|matches)\((.*)\)\s*$", re.IGNORECASE | re.DOTALL)
_KEYFRAMES = re.compile(r"^@(?:-webkit-)?keyframes\b", re.IGNORECASE)
_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_STRING = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'")
_PX_ATTR = re.compile(r"([0-9]*\.?[0-9]+)(?:px)?\Z", re.IGNORECASE)

_PROBE = """() => {
  const de = document.documentElement;
  const body = document.body;
  const scrollWidth = Math.max(de ? de.scrollWidth : 0, body ? body.scrollWidth : 0);
  const clientWidth = de ? de.clientWidth : 0;
  const shown = (el) => {
    for (let node = el; node && node.nodeType === 1; node = node.parentElement) {
      const st = window.getComputedStyle(node);
      if (!st || st.display === "none" || st.visibility === "hidden" || st.visibility === "collapse") {
        return false;
      }
      if (parseFloat(st.opacity || "1") === 0) return false;
    }
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };
  let header = false;
  for (const el of document.querySelectorAll("header, .site-header")) {
    if (shown(el)) { header = true; break; }
  }
  return {scrollWidth, clientWidth, header};
}"""


def _px(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{float(value):.4f}".rstrip("0").rstrip(".")


def _as_text(html: str) -> str:
    if isinstance(html, str):
        return html
    if isinstance(html, bytes):
        return html.decode("utf-8", "replace")
    return ""


def _result(mode: str, failures: list[dict[str, str]]) -> dict:
    return {"ok": not failures, "mode": mode, "failures": failures}


def _add(out: list[str], detail: str) -> None:
    if detail not in out:
        out.append(detail)


def _bare(text: str) -> str:
    return _STRING.sub("''", text)


def _split_commas(selector: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    quote = ""
    i = 0
    while i < len(selector):
        ch = selector[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and i + 1 < len(selector):
                buf.append(selector[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    parts.append("".join(buf))
    return parts


def _compounds(selector: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    quote = ""
    i = 0
    text = selector.strip()
    while i < len(text):
        ch = text[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and i + 1 < len(text):
                buf.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if ch == "(":
            depth += 1
            buf.append(ch)
            i += 1
            continue
        if ch == ")" and depth:
            depth -= 1
            buf.append(ch)
            i += 1
            continue
        if depth == 0 and (ch in ">+~" or ch.isspace()):
            piece = "".join(buf).strip()
            if piece:
                parts.append(piece)
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    piece = "".join(buf).strip()
    if piece:
        parts.append(piece)
    return parts


def _selector_hits_root(selector: str) -> bool:
    for piece in _split_commas(selector):
        compounds = _compounds(piece)
        if compounds and _compound_is_root(compounds[-1]):
            return True
    return False


def _compound_is_root(compound: str) -> bool:
    text = compound.strip()
    if not text:
        return False
    # * and :root match html/body. A class, id, or attribute on them does not always.
    if text == "*" or (text.startswith("*") and text[1] == ":"):
        return True
    if text == ":root" or text.startswith(":root:"):
        return True
    if _ROOT.match(text):
        return True
    match = _IS.match(text)
    if match:
        return _selector_hits_root(match.group(1))
    return False


def _check_decls(body: str, out: list[str], where: str, on_root: bool) -> None:
    text = _bare(body)
    for match in _WIDTH.finditer(text):
        value = float(match.group(1))
        if value > 1280:
            _add(out, f"fixed width {_px(value)}px > 1280px{where}")
    if on_root:
        for match in _MIN_WIDTH.finditer(text):
            value = float(match.group(1))
            if value > 400:
                _add(out, f"min-width {_px(value)}px > 400px on body or html{where}")


def _scan_css(css: str, out: list[str]) -> None:
    css = _COMMENT.sub("", css).replace("<!--", "").replace("-->", "")
    n = len(css)
    i = 0

    def skip_string(pos: int, quote: str) -> int:
        pos += 1
        while pos < n:
            if css[pos] == "\\" and pos + 1 < n:
                pos += 2
                continue
            if css[pos] == quote:
                return pos + 1
            pos += 1
        return pos

    while i < n:
        while i < n and css[i].isspace():
            i += 1
        if i >= n:
            return
        start = i
        while i < n and css[i] not in "{};":
            if css[i] in "\"'":
                i = skip_string(i, css[i])
                continue
            i += 1
        prelude = css[start:i].strip()
        if i >= n:
            return
        if css[i] != "{":
            i += 1
            continue
        i += 1
        body_start = i
        depth = 1
        while i < n and depth:
            ch = css[i]
            if ch in "\"'":
                i = skip_string(i, ch)
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
        body = css[body_start:i - 1] if depth == 0 else css[body_start:i]
        if not prelude or _KEYFRAMES.match(prelude):
            continue
        if prelude[0] == "@" and "{" in _bare(body):
            _scan_css(body, out)
        else:
            on_root = prelude[0] != "@" and _selector_hits_root(prelude)
            _check_decls(body, out, "", on_root)


def _width_attr(tag: str, raw: str, out: list[str]) -> None:
    match = _PX_ATTR.fullmatch(raw.strip())
    if not match:
        return
    value = float(match.group(1))
    if value > 1280:
        _add(out, f"fixed width {_px(value)}px > 1280px on <{tag}>")


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hashes: list[str] = []
        self.header = False
        self.main = False
        self.viewport = False
        self.sideways: list[str] = []
        self._style: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes: list[str] = []
        values: dict[str, str] = {}
        for key, value in attrs:
            text = value or ""
            if key == "class":
                classes.extend(text.split())
                continue
            values.setdefault(key, text)
        if tag == "style":
            self._style = []
        if tag == "header" or "site-header" in classes:
            self.header = True
        element_id = values.get("id", "")
        if element_id:
            self.ids.add(element_id)
            if element_id == "main":
                self.main = True
        if tag == "meta" and values.get("name", "").lower() == "viewport":
            self.viewport = True
        href = values.get("href", "")
        if href.startswith("#") and len(href) > 1:
            frag = unquote(href[1:])
            if frag:
                self.hashes.append(frag)
        if "width" in values:
            _width_attr(tag, values["width"], self.sideways)
        if "style" in values:
            where = "" if tag in {"body", "html"} else f" on <{tag}>"
            _check_decls(values["style"], self.sideways, where, tag in {"body", "html"})

    def handle_endtag(self, tag: str) -> None:
        if tag == "style" and self._style is not None:
            _scan_css("".join(self._style), self.sideways)
            self._style = None

    def handle_data(self, data: str) -> None:
        if self._style is not None:
            self._style.append(data)

    def close(self) -> None:
        super().close()
        if self._style is not None:
            _scan_css("".join(self._style), self.sideways)
            self._style = None

    def broken(self) -> list[str]:
        missing: list[str] = []
        seen: set[str] = set()
        for frag in self.hashes:
            if frag in seen:
                continue
            seen.add(frag)
            if frag not in self.ids:
                missing.append(frag)
        return missing


def visit_html(html: str) -> dict:
    """Static visit result. mode is always static."""
    page = _Page()
    page.feed(_as_text(html))
    page.close()
    failures: list[dict[str, str]] = []
    if not page.header:
        failures.append({
            "code": "missing_header",
            "detail": "no site-header class and no header element",
        })
    if not page.main:
        failures.append({"code": "missing_main", "detail": 'no id="main"'})
    for frag in page.broken():
        failures.append({
            "code": "broken_hash",
            "detail": f'href="#{frag}" has no matching id',
        })
    if not page.viewport:
        failures.append({"code": "missing_viewport", "detail": "no viewport meta"})
    for detail in page.sideways:
        failures.append({"code": "sideways", "detail": detail})
    return _result("static", failures)


def _local_only(route) -> None:
    url = route.request.url
    if url.startswith(("http://", "https://")):
        route.abort()
        return
    route.continue_()


def _launch(playwright):
    attempts = (
        {"channel": "chrome", "headless": True, "timeout": 20000, "args": ["--allow-file-access-from-files"]},
        {"headless": True, "timeout": 20000, "args": ["--allow-file-access-from-files"]},
    )
    for kwargs in attempts:
        try:
            return playwright.chromium.launch(**kwargs)
        except Exception:
            continue
    return None


def _measure(browser, url: str) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for width, height in _VIEWPORTS:
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
        )
        try:
            page = context.new_page()
            page.route("**/*", _local_only)
            page.set_viewport_size({"width": width, "height": height})
            page.goto(url, wait_until="domcontentloaded", timeout=8000)
            data = page.evaluate(_PROBE)
        finally:
            context.close()
        if not isinstance(data, dict):
            raise RuntimeError("layout was not measured")
        client = float(data.get("clientWidth") or 0)
        scroll = float(data.get("scrollWidth") or 0)
        if client <= 0:
            raise RuntimeError("layout was not measured")
        if scroll > client + 1:
            failures.append({
                "code": "sideways",
                "detail": (
                    f"scrollWidth {_px(scroll)} > clientWidth {_px(client)} + 1"
                    f" at {width}x{height}"
                ),
            })
        if not data.get("header"):
            failures.append({
                "code": "missing_header",
                "detail": f"no visible header at {width}x{height}",
            })
    return failures


def _rendered_failures(index: Path) -> list[dict[str, str]] | None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return None
    try:
        with sync_playwright() as playwright:
            browser = _launch(playwright)
            if browser is None:
                return None
            try:
                return _measure(browser, index.resolve().as_uri())
            finally:
                try:
                    browser.close()
                except Exception:
                    pass
    except Exception:
        return None


def visit_site(site_dir: Path) -> dict:
    """Read site_dir/index.html. Rendered mode only after a browser launches."""
    index = Path(site_dir) / "index.html"
    if not index.is_file():
        return visit_html("")
    try:
        html = index.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return visit_html("")
    result = visit_html(html)
    extra = _rendered_failures(index)
    if extra is None:
        return result
    result["mode"] = "rendered"
    result["failures"].extend(extra)
    result["ok"] = not result["failures"]
    return result
