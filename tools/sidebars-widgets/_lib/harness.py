"""Shared test harness for the SpiderCaster sidebars-widgets slice.

Stdlib only. Each item folder holds a thin test.py that calls run_item(__file__).
Checks, in order: manifest, files and slug, template tokens, rendered HTML lint,
CSS lint, JS lint, secret scan, size budget, then headless Chrome at 360 and 1280 px
in an OceanWP-like context (root 62.5%) and a GeneratePress-like context.
Exit code 0 = every check passed. Exit 1 = a check failed. Exit 2 = static pass,
browser checks skipped because no Chrome or Edge was found.
"""
import gzip, html, json, os, re, shutil, subprocess, sys, tempfile, time
from html.parser import HTMLParser
from pathlib import Path

LIB = Path(__file__).resolve().parent
ROOT = LIB.parent
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
WIDTHS = (360, 1280)
CTXS = ("oceanwp", "generatepress")
REQUIRED_MANIFEST = ("name", "slug", "kind", "purpose", "inputs", "files", "test_command", "status", "version", "themes", "budget_bytes")
BAD_WORDS = re.compile(r"\b(lorem|ipsum|sample|placeholder|original schematic|amazing|awesome|best[- ]in[- ]class|cutting[- ]edge|world[- ]class|seamless|stunning|revolutionary|powerful|click here)\b", re.I)
SECRET_RES = [re.compile(p, re.I) for p in (
    r"cfat_[A-Za-z0-9_-]{8,}", r"\bsk-[A-Za-z0-9]{16,}", r"\bAKIA[0-9A-Z]{12,}",
    r"(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*[\"'][^\"']{8,}[\"']", r"\b[0-9a-f]{32,}\b",
    r"BEGIN [A-Z ]*PRIVATE KEY")]


# ---------- rendering ----------
EACH = re.compile(r"<!--each (\w+)-->(.*?)<!--/each-->", re.S)
IF = re.compile(r"<!--if (\w+)-->(.*?)<!--/if-->", re.S)
UNLESS = re.compile(r"<!--unless (\w+)-->(.*?)<!--/unless-->", re.S)
RAW = re.compile(r"\{\{\{([\w@]+)\}\}\}")
ESC = re.compile(r"\{\{([\w@]+)\}\}")


def _scalar(t, d):
    t = IF.sub(lambda m: m.group(2) if d.get(m.group(1)) else "", t)
    t = UNLESS.sub(lambda m: "" if d.get(m.group(1)) else m.group(2), t)
    t = RAW.sub(lambda m: str(d.get(m.group(1), "")), t)
    return ESC.sub(lambda m: html.escape(str(d.get(m.group(1), "")), quote=True), t)


def render(tpl, data):
    def each(m):
        out = []
        for i, item in enumerate(data.get(m.group(1), []) or []):
            scope = dict(data)
            scope.update(item if isinstance(item, dict) else {"value": item})
            scope["@index"] = i + 1
            out.append(_scalar(m.group(2), scope))
        return "".join(out)
    return _scalar(EACH.sub(each, tpl), data)


def tokens_of(tpl):
    """Return (top-level tokens, {loop: tokens}) used by a template."""
    loops = {}
    for m in EACH.finditer(tpl):
        loops[m.group(1)] = set(re.findall(r"\{\{\{?([\w@]+)\}\}\}?", m.group(2))) | set(re.findall(r"<!--(?:if|unless) (\w+)-->", m.group(2)))
    top = EACH.sub("", tpl)
    names = set(re.findall(r"\{\{\{?([\w@]+)\}\}\}?", top)) | set(re.findall(r"<!--(?:if|unless) (\w+)-->", top))
    return names, loops


# ---------- html lint ----------
class Lint(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems, self.ids, self.fors = [], [], [], set()
        self.text, self.attrtext, self.inputs, self.labels_open = [], [], [], 0
        self.in_label = []

    def p(self, msg):
        self.problems.append(msg)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if tag == "label":
            self.in_label.append(True)
        if tag == "script":
            self.p("script tag inside fragment")
        for k, v in attrs:
            if k.startswith("on"):
                self.p("inline handler " + k)
            if k == "style":
                self.p("inline style on <%s>" % tag)
            if k == "id":
                self.ids.append(v)
            if k in ("aria-label", "alt", "title", "placeholder") and v:
                self.attrtext.append(v)
        if tag == "img":
            if not a.get("alt"):
                self.p("img without alt")
            if not (a.get("width") and a.get("height")):
                self.p("img without width and height")
        if tag == "a" and a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
            self.p("target=_blank without rel=noopener")
        if tag == "a" and not a.get("href") and not a.get("role"):
            self.p("a without href")
        if tag == "button" and a.get("type") not in ("button", "submit", "reset"):
            self.p("button without type")
        if tag == "label" and a.get("for"):
            self.fors.add(a["for"])
        if tag in ("input", "select", "textarea"):
            t = a.get("type", "text")
            if t not in ("hidden", "submit", "button", "reset"):
                self.inputs.append((tag, a, bool(self.in_label)))
        for k in ("href", "src", "action"):
            v = a.get(k) or ""
            if re.match(r"https?://", v) and tag in ("img", "script", "link", "source"):
                self.p("hotlinked %s on <%s>" % (k, tag))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "label" and self.in_label:
            self.in_label.pop()
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.p("unbalanced </%s> (open: %s)" % (tag, self.stack[-1] if self.stack else "none"))
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
            return
        self.stack.pop()

    def handle_data(self, data):
        if data.strip():
            self.text.append(data.strip())

    def finish(self):
        if self.stack:
            self.p("unclosed tags: " + ",".join(self.stack))
        if len(set(self.ids)) != len(self.ids):
            self.p("duplicate ids")
        for tag, a, in_label in self.inputs:
            ok = in_label or a.get("aria-label") or a.get("aria-labelledby") or (a.get("id") in self.fors)
            if not ok:
                self.p("%s name=%s has no label" % (tag, a.get("name")))
        joined = " ".join(self.text + self.attrtext)
        if "!" in joined:
            self.p("exclamation point in copy")
        m = BAD_WORDS.search(joined)
        if m:
            self.p("banned word in copy: " + m.group(0))
        return self.problems


# ---------- css / js lint ----------
def css_problems(css):
    p = []
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    if re.search(r"\d(rem)\b", body):
        p.append("rem unit used (OceanWP root is 62.5%, use px)")
    for m in re.finditer(r"font-size\s*:\s*([\d.]+)(px|em|%|pt)", body):
        if m.group(2) != "px":
            p.append("font-size in %s" % m.group(2))
        elif float(m.group(1)) < 16:
            p.append("font-size %spx below 16" % m.group(1))
    if len(re.findall(r"!important", body)) > 3:
        p.append("more than 3 !important")
    if re.search(r"@import|expression\(", body) or re.search(r"url\(\s*[\"']?https?:", body):
        p.append("@import, expression or remote url")
    for m in re.finditer(r"(?:^|\})\s*([^{}@]+)\{", body):
        for sel in m.group(1).split(","):
            sel = sel.strip()
            if sel and not re.search(r"\.sc-|\[data-sc", sel) and not re.fullmatch(r"(from|to|\d+%)", sel):
                p.append("unscoped selector: " + sel[:50])
    return p


JS_BAD = re.compile(r"innerHTML|outerHTML|insertAdjacentHTML|\beval\s*\(|new Function|document\.write|XMLHttpRequest|\bfetch\s*\(|sendBeacon")


def js_problems(js, ok_hosts):
    p = []
    if JS_BAD.search(js):
        p.append("forbidden API: " + JS_BAD.search(js).group(0))
    for h in re.findall(r"https?://([\w.-]+)", js):
        if h not in ok_hosts:
            p.append("host not in manifest external_hosts: " + h)
    if '"use strict"' not in js and "'use strict'" not in js:
        p.append("missing use strict")
    return p


def node_check(path):
    node = shutil.which("node")
    if not node:
        return None
    r = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
    return r.stderr.strip() if r.returncode else ""


# ---------- chrome ----------
def find_chrome():
    cands = [os.environ.get("SC_CHROME", "")]
    for n in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        cands.append(shutil.which(n) or "")
    for d in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        b = os.environ.get(d)
        if b:
            cands += [os.path.join(b, "Google", "Chrome", "Application", "chrome.exe"),
                      os.path.join(b, "Microsoft", "Edge", "Application", "msedge.exe")]
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def wrap_frame(page_html, width):
    return ('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#888}iframe{display:block;border:0;background:#fff}</style></head>'
            '<body><iframe width="%d" height="900" srcdoc="%s"></iframe></body></html>' % (width, html.escape(page_html, quote=True)))


def run_chrome(chrome, page, width, tmp):
    prof = tempfile.mkdtemp(prefix="scprof_", dir=tmp)
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--no-first-run",
           "--disable-extensions", "--user-data-dir=" + prof, "--window-size=%d,1000" % max(width + 40, 540),
           "--virtual-time-budget=4000", "--dump-dom", Path(page).as_uri()]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return None, "chrome timeout"
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    m = re.search(r'<pre id="sc-result">(.*?)</pre>', r.stdout, re.S)
    if not m:
        return None, "no result block (rc=%s) %s" % (r.returncode, r.stderr[-200:].strip())
    try:
        return json.loads(html.unescape(m.group(1))), None
    except ValueError as e:
        return None, "bad result json: %s" % e


# ---------- page assembly ----------
def read(p):
    return Path(p).read_text(encoding="utf-8")


def item_parts(d, m):
    slug = m["slug"]
    f = {k: (d / (slug + ext)) for k, ext in (("html", ".html"), ("css", ".css"), ("js", ".js"))}
    return {k: (read(v) if v.exists() else "") for k, v in f.items()}


def fixture_of(d):
    return json.loads(read(d / "fixture.json"))


def widget_html(kind_dir, slug, over=None):
    d = ROOT / "widgets" / slug
    m = json.loads(read(d / "manifest.json"))
    parts = item_parts(d, m)
    data = dict(fixture_of(d)["data"])
    data.update(over or {})
    return render(parts["html"], data), parts["css"], parts["js"]


def fragment_for(d, m, fx, data=None, lint=False):
    """Return (html, css, js) for an item. Sidebar layouts get slots filled with fixture widgets."""
    parts = item_parts(d, m)
    data = dict(fx["data"] if data is None else data)
    css, js = parts["css"], parts["js"]
    if m["kind"] == "sidebar":
        page = "<p>Fixture text.</p>" if lint else '<div data-sc-test-skip>' + read(LIB / "page_content.html") + '</div>'
        data.setdefault("main", page)
        for slot, names in (fx.get("slots") or {}).items():
            buf = []
            for n in names:
                over = None
                if isinstance(n, dict):
                    n, over = n["widget"], n.get("data")
                h, c, j = widget_html("widgets", n, over)
                buf.append(h); css += "\n" + c; js += "\n" + j
            data[slot] = "\n".join(buf)
    return render(parts["html"], data), css, js


def ctx_wrap(ctx, kind, inner):
    if kind == "sidebar":
        if ctx == "oceanwp":
            return ('<div id="outer-wrap" class="site clr"><div id="wrap" class="clr"><main id="main" class="site-main clr">'
                    '<div id="content-wrap" class="container clr"><div id="sc-under-test">%s</div></div></main></div></div>' % inner)
        return ('<div class="site grid-container container hfeed" id="page"><div class="site-content" id="content" style="display:block">'
                '<div id="sc-under-test">%s</div></div></div>' % inner)
    page = '<div data-sc-test-skip>' + read(LIB / "page_content.html") + '</div>'
    if ctx == "oceanwp":
        return ('<div id="outer-wrap" class="site clr"><div id="wrap" class="clr"><main id="main" class="site-main clr">'
                '<div id="content-wrap" class="container clr"><div id="primary" class="content-area clr"><div id="content" class="site-content clr">'
                '<article class="entry-content clr">%s</article></div></div>'
                '<aside id="right-sidebar" class="sidebar-container widget-area sidebar-primary" role="complementary" aria-label="Primary Sidebar">'
                '<div id="right-sidebar-inner" class="clr"><div class="sidebar-box widget_custom_html clr"><div id="sc-under-test">%s</div></div></div></aside>'
                '</div></main></div></div>' % (page, inner))
    return ('<div class="site grid-container container hfeed" id="page"><div class="site-content" id="content">'
            '<div class="content-area" id="primary"><main class="site-main" id="main"><article class="inside-article"><div class="entry-content">%s</div></article></main></div>'
            '<div class="widget-area sidebar is-right-sidebar" id="right-sidebar"><div class="inside-right-sidebar">'
            '<aside class="widget inner-padding widget_custom_html"><div id="sc-under-test">%s</div></aside></div></div></div></div>' % (page, inner))


def build_page(ctx, m, inner, css, js, test_js=None, title_suffix=""):
    body_cls = "oceanwp-theme content-full-width" if ctx == "oceanwp" else "wp-theme-generatepress no-sidebar"
    ctxcss = read(LIB / ("ctx_%s.css" % ctx))
    extra = ""
    if test_js is not None:
        extra = ("<style>*{transition:none!important;animation:none!important;scroll-behavior:auto!important}</style>"
                 "<script>%s</script><script>%s</script>"
                 "<script>window.addEventListener('load',function(){setTimeout(function(){"
                 "var res={w:innerWidth,rootFont:getComputedStyle(document.documentElement).fontSize,behavior:[],error:null};"
                 "var t={ok:function(n,c,d){res.behavior.push({name:n,ok:!!c,detail:d||''})},sleep:function(ms){return new Promise(function(r){setTimeout(r,ms)})}};"
                 "var T=window.scTest||{};"
                 "Promise.resolve().then(function(){return T.behavior&&T.behavior(t,{width:innerWidth})})"
                 ".then(function(){return T.prepare&&T.prepare(t,{width:innerWidth})})"
                 ".then(function(){res.measure=scMeasure(document.getElementById('sc-under-test'))})"
                 ".catch(function(e){res.error=String(e&&e.stack||e)})"
                 ".then(function(){var H=(window.parent!==window?window.parent.document:document);var pre=H.createElement('pre');pre.id='sc-result';pre.textContent=JSON.stringify(res);H.body.appendChild(pre);});},50)});</script>"
                 % (read(LIB / "measure.js"), test_js))
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex"><title>%s demo, %s context</title><style>%s</style><style>%s</style></head>'
            '<body class="%s">%s<script>%s</script>%s</body></html>'
            % (html.escape(m["name"]), ctx, ctxcss, css, body_cls, ctx_wrap(ctx, m["kind"], inner), js, extra))


# ---------- main entry ----------
class Result:
    def __init__(self):
        self.checks = []

    def add(self, cid, ok, detail=""):
        self.checks.append({"id": cid, "ok": bool(ok), "detail": detail if not ok else (detail or "")})
        return ok

    @property
    def failed(self):
        return [c for c in self.checks if not c["ok"]]


def run_item(test_file, write_demo=True):
    d = Path(test_file).resolve().parent
    R = Result()
    t0 = time.time()
    mpath = d / "manifest.json"
    try:
        m = json.loads(read(mpath))
    except Exception as e:
        R.add("manifest.parse", False, str(e))
        return finish(d, {"slug": d.name}, R, t0, False)
    miss = [k for k in REQUIRED_MANIFEST if k not in m]
    R.add("manifest.keys", not miss, "missing: %s" % miss)
    slug = m.get("slug", "")
    R.add("slug.shape", SLUG_RE.match(slug) and slug == d.name, "slug %r folder %r" % (slug, d.name))
    R.add("manifest.kind", m.get("kind") in ("sidebar", "widget"), str(m.get("kind")))
    R.add("manifest.test_command", "test.py" in str(m.get("test_command")), str(m.get("test_command")))
    files = m.get("files", [])
    absent = [f for f in files if not (d / f).exists()]
    R.add("files.exist", not absent, "absent: %s" % absent)
    R.add("files.named", all(f in files for f in ("manifest.json", "test.py", "fixture.json", slug + ".html", slug + ".css")), str(files))
    parts = item_parts(d, m)
    # tokens vs inputs
    inputs = {i["name"]: i for i in m.get("inputs", [])}
    names, loops = tokens_of(parts["html"])
    undeclared = sorted(n for n in names if n not in inputs and not n.startswith("@"))
    R.add("tokens.declared", not undeclared, "undeclared tokens: %s" % undeclared)
    badloop = []
    for lp, toks in loops.items():
        fields = set((inputs.get(lp) or {}).get("fields", []))
        badloop += ["%s.%s" % (lp, t) for t in toks if t not in fields and t not in inputs and not t.startswith("@")]
    R.add("tokens.loop_fields", not badloop, "unknown loop fields: %s" % badloop)
    used = names | set(loops)
    for _t in loops.values():
        used |= _t
    unused = sorted(n for n, i in inputs.items() if n not in used and not i.get("slot_only"))
    R.add("tokens.used", not unused, "declared but unused: %s" % unused)
    nested = re.search(r"<!--if \w+-->(?:(?!<!--/if-->).)*<!--if ", parts["html"], re.S)
    R.add("template.no_nested_if", not nested, "nested if blocks")
    fx = fixture_of(d)
    # rendered html lint, full fixture and required-only
    req = {k: v for k, v in fx["data"].items() if inputs.get(k, {}).get("required", True)}
    for n, i in inputs.items():
        if not i.get("required", True) and "default" in i:
            req[n] = i["default"]
    for label, data in (("full", fx["data"]), ("required_only", req)):
        h, css, js = fragment_for(d, m, fx, data, lint=True)
        lint = Lint()
        try:
            lint.feed(h); lint.close()
            probs = lint.finish()
        except Exception as e:
            probs = ["parse error %s" % e]
        R.add("html.lint." + label, not probs, "; ".join(sorted(set(probs))))
    for vname, over in (fx.get("variants") or {}).items():
        vd = dict(fx["data"]); vd.update(over)
        h, css, js = fragment_for(d, m, fx, vd, lint=True)
        lint = Lint()
        lint.feed(h); lint.close()
        probs = lint.finish()
        R.add("html.lint.variant." + vname, not probs, "; ".join(sorted(set(probs))))
    cp = css_problems(parts["css"])
    R.add("css.lint", not cp, "; ".join(cp))
    hosts = m.get("external_hosts", [])
    if parts["js"]:
        jp = js_problems(parts["js"], hosts)
        R.add("js.lint", not jp, "; ".join(jp))
        nc = node_check(d / (slug + ".js"))
        R.add("js.syntax", nc in ("",), "node not found" if nc is None else nc)
    else:
        R.add("js.lint", True, "no js")
    secrets = []
    for f in files:
        txt = read(d / f) if (d / f).exists() else ""
        for rx in SECRET_RES:
            if rx.search(txt):
                secrets.append("%s:%s" % (f, rx.pattern[:20]))
    R.add("secrets.none", not secrets, "; ".join(secrets))
    raw = sum(len((parts[k]).encode()) for k in parts)
    gz = len(gzip.compress((parts["html"] + parts["css"] + parts["js"]).encode(), 9))
    R.add("size.budget", raw <= m.get("budget_bytes", 6144), "%d bytes > budget %s" % (raw, m.get("budget_bytes")))
    extra = {"bytes": raw, "gzip_bytes": gz}
    # browser
    chrome = None if os.environ.get("SC_NO_BROWSER") else find_chrome()
    browser_ran = False
    if not chrome:
        R.checks.append({"id": "browser.skipped", "ok": True, "detail": "no Chrome or Edge found, or SC_NO_BROWSER set"})
        return finish(d, m, R, t0, False, extra, skipped=True)
    test_js = read(d / "test.behavior.js") if (d / "test.behavior.js").exists() else "window.scTest={};"
    h, css, js = fragment_for(d, m, fx)
    tmp = tempfile.mkdtemp(prefix="scsw_")
    demo = d / "demo"
    if write_demo:
        demo.mkdir(exist_ok=True)
    try:
        for ctx in CTXS:
            if write_demo:
                (demo / (ctx + ".html")).write_text(build_page(ctx, m, h, css, js), encoding="utf-8")
            test_page = build_page(ctx, m, h, css, js, test_js)
            for w in WIDTHS:
                tag = "%s@%d" % (ctx, w)
                page = Path(tmp) / ("%s-%d.html" % (ctx, w))
                page.write_text(wrap_frame(test_page, w), encoding="utf-8")
                res, err = run_chrome(chrome, page, w, tmp)
                if err or res is None:
                    R.add("browser.run." + tag, False, err)
                    continue
                browser_ran = True
                R.add("browser.error." + tag, not res.get("error"), res.get("error"))
                R.add("browser.viewport." + tag, abs(res["w"] - w) <= 20, "innerWidth %s" % res["w"])
                if ctx == "oceanwp":
                    R.add("browser.root62." + tag, res["rootFont"] == "10px", "root font %s" % res["rootFont"])
                for b in res.get("behavior", []):
                    R.add("behavior.%s.%s" % (b["name"], tag), b["ok"], b.get("detail"))
                ms = res.get("measure") or {}
                if tag == "oceanwp@360":
                    extra["measured_360"] = {"text_nodes": (ms.get("counts") or {}).get("texts"), "tap_targets": (ms.get("counts") or {}).get("targets"), "min_contrast": ms.get("minContrast")}
                R.add("measure.no_overflow." + tag, not ms.get("overflow") and ms.get("docScrollWidth", 0) <= res["w"] + 1,
                      "%s doc=%s" % (ms.get("overflow", [])[:3], ms.get("docScrollWidth")))
                R.add("measure.text_floor." + tag, not ms.get("smallText"), "; ".join(ms.get("smallText", [])[:4]))
                R.add("measure.contrast." + tag, not ms.get("lowContrast"), "; ".join(ms.get("lowContrast", [])[:4]))
                R.add("measure.tap_44." + tag, not ms.get("smallTargets"), "; ".join(ms.get("smallTargets", [])[:5]))
                R.add("measure.has_content." + tag, (ms.get("counts") or {}).get("texts", 0) > 0, "no visible text measured")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return finish(d, m, R, t0, browser_ran, extra)


def finish(d, m, R, t0, browser_ran, extra=None, skipped=False):
    failed = R.failed
    status = "fail" if failed else ("pass" if browser_ran else "static-only")
    out = {"slug": m.get("slug", d.name), "status": status, "passed": len(R.checks) - len(failed), "failed": len(failed),
           "total": len(R.checks), "seconds": round(time.time() - t0, 1), "extra": extra or {}, "checks": R.checks}
    rd = ROOT / "results"
    rd.mkdir(exist_ok=True)
    (rd / (out["slug"] + ".json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("%s %s: %d/%d checks%s" % (status.upper(), out["slug"], out["passed"], out["total"], "" if not extra else "  %s bytes (%s gz)" % (extra["bytes"], extra["gzip_bytes"])))
    for c in failed:
        print("  FAIL %s: %s" % (c["id"], c["detail"]))
    return 1 if failed else (2 if skipped else 0)
