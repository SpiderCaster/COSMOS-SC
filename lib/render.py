"""Deterministic renderer: site IR -> static HTML. Zero tokens, every time.

Single-file pages (inline CSS + JS), system font stacks, inline SVG icons,
gradient visuals. No external requests, no hotlinking, no build deps.
"""
from __future__ import annotations

import colorsys
import re
from datetime import date
from string import Template

# ---------------------------------------------------------------- utils

def esc(v) -> str:
    return (str(v if v is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def hash_str(v: str) -> int:
    h = 2166136261
    for ch in str(v):
        h ^= ord(ch[0]) if ch else 0
        h = (h * 16777619) & 0xFFFFFFFF
    return h


# ---------------------------------------------------------------- icons

ICONS = {
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/>',
    "star": '<path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.9L12 17.8l-6.2 3.3L7 14.2 2 9.3l6.9-1L12 2z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "code": '<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
    "cloud": '<path d="M18 10h-1.3A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "pulse": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "sparkles": '<path d="M12 3l2 5 5 2-5 2-2 5-2-5-5-2 5-2 2-5z"/><path d="M19 15l.9 1.8 1.8.9-1.8.9L19 21l-.9-2.1-1.8-.9 1.8-.9L19 15z"/>',
    "layers": '<path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3"/>',
    "camera": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "map": '<path d="M9 3 3 5v16l6-2 6 2 6-2V3l-6 2-6-2z"/><path d="M9 3v16M15 5v16"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "trending": '<path d="m23 6-9.5 9.5-5-5L1 18"/><path d="M17 6h6v6"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.8a2 2 0 0 1-.4 2.1L8 10a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "quote": '<path d="M7 7h4v6H7c0 3-1 4-3 4v-2c1 0 2-1 2-3V7zM17 7h4v6h-4c0 3-1 4-3 4v-2c1 0 2-1 2-3V7z" fill="currentColor" stroke="none"/>',
}


def icon(name: str) -> str:
    body = ICONS.get(name, ICONS["sparkles"])
    return (f'<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


# ---------------------------------------------------------------- color

def hex_to_rgb(h: str) -> tuple[int, int, int]:
    n = int(h.lstrip("#"), 16)
    return (n >> 16) & 255, (n >> 8) & 255, n & 255


def rgb_to_hex(r, g, b) -> str:
    return "#{:02x}{:02x}{:02x}".format(max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))


def mix_hex(a: str, b: str, t: float) -> str:
    A, B = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex(*(A[i] + (B[i] - A[i]) * t for i in range(3)))


def luminance(h: str) -> float:
    vals = []
    for v in hex_to_rgb(h):
        v /= 255.0
        vals.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    r, g, b = vals
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_on(h: str) -> str:
    return "#10131a" if luminance(h) > 0.5 else "#ffffff"


def rgba(h: str, a: float) -> str:
    r, g, b = hex_to_rgb(h)
    return f"rgba({r}, {g}, {b}, {a})"


def hue_of(h: str) -> float:
    r, g, b = (v / 255.0 for v in hex_to_rgb(h))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    return hh * 360


DARK_PAIRS = [("#5eead4", "#818cf8"), ("#f0abfc", "#f472b6"), ("#fcd34d", "#fb7185"),
              ("#86efac", "#22d3ee"), ("#93c5fd", "#c4b5fd"), ("#fda4af", "#fbbf24")]
LIGHT_PAIRS = [("#0ea5e9", "#6366f1"), ("#059669", "#0d9488"), ("#d97706", "#e11d48"),
               ("#7c3aed", "#c026d3"), ("#2563eb", "#0891b2"), ("#16a34a", "#ca8a04")]


def build_palette(theme: dict, seed: str) -> dict:
    dark = theme.get("dark", True) is not False
    pairs = DARK_PAIRS if dark else LIGHT_PAIRS
    pair = pairs[hash_str(seed or "spidercaster") % len(pairs)]
    accent = theme.get("accent") or pair[0]
    accent2 = theme.get("accent2") or pair[1]
    if dark:
        base = {"bg": "#0a0e14", "surface": "#111722", "surface2": "#161e2c",
                "text": "#e9eef6", "muted": "#9aa7b8"}
    else:
        base = {"bg": "#f7f8fa", "surface": "#ffffff", "surface2": "#f1f3f7",
                "text": "#171a21", "muted": "#5c6572"}
    pal = dict(base)
    pal.update({
        "dark": dark,
        "accent": accent,
        "accent2": accent2,
        "on_accent": contrast_on(accent),
        "accent_soft": rgba(accent, 0.14),
        "accent_shadow": rgba(accent, 0.30),
        "line": rgba("#ffffff" if dark else "#0f141e", 0.10 if dark else 0.12),
        "header_bg": rgba(hex_to_rgb(base["bg"]) and rgb_to_hex(*hex_to_rgb(base["bg"])), 0.82),
        "shadow": "rgba(0,0,0,.35)" if dark else "rgba(15,20,30,.12)",
        "radius": "16px" if theme.get("template") != "bold" else "22px",
        "font_head": ("Georgia, 'Times New Roman', serif"
                      if theme.get("template") == "editorial"
                      else "ui-sans-serif, system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"),
        "font_body": "ui-sans-serif, system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    })
    return pal


# ---------------------------------------------------------------- css

CSS_TEMPLATE = Template("""*{box-sizing:border-box}
html{scroll-behavior:smooth;font-size:18px}
body{margin:0;font-family:$font_body;background:$bg;color:$text;line-height:1.6;-webkit-font-smoothing:antialiased}
:root{--bg:$bg;--surface:$surface;--surface2:$surface2;--text:$text;--muted:$muted;--line:$line;--accent:$accent;--accent2:$accent2;--on-accent:$on_accent;--accent-soft:$accent_soft;--radius:$radius;--maxw:1120px;--font-head:$font_head;--font-body:$font_body}
img{max-width:100%;display:block}
a{color:var(--accent)}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px}
section{padding:72px 0}
h1,h2,h3{font-family:var(--font-head);line-height:1.15;margin:0 0 12px;letter-spacing:-.015em}
h1{font-size:clamp(2.3rem,5.5vw,3.9rem)}
h2{font-size:clamp(1.6rem,3vw,2.3rem)}
h3{font-size:1.12rem}
p{margin:0 0 14px}
.lede{color:var(--muted);font-size:1.08rem;max-width:62ch}
.eyebrow{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border:1px solid var(--line);border-radius:999px;font-size:1rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);background:var(--surface);margin-bottom:16px}
.icon{width:1.15em;height:1.15em;flex:none;vertical-align:-.2em}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 18px;border-radius:10px;font-weight:600;text-decoration:none;font-size:1rem;border:1px solid transparent;transition:transform .15s ease,box-shadow .15s ease}
.btn.primary{background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);box-shadow:0 6px 18px $accent_shadow}
.btn.primary:hover{transform:translateY(-1px)}
.btn.ghost{border-color:var(--line);color:var(--text);background:var(--surface)}
.site-header{position:sticky;top:0;z-index:50;backdrop-filter:blur(10px);background:$header_bg;border-bottom:1px solid var(--line)}
.nav{display:flex;align-items:center;gap:20px;min-height:64px}
.brand{font-weight:700;font-size:1.05rem;text-decoration:none;color:var(--text);font-family:var(--font-head)}
.nav-links{display:flex;gap:20px;margin-left:auto;align-items:center}
.nav-links a{color:var(--muted);text-decoration:none;font-size:.95rem}
.nav-links a:hover,.nav-links a[aria-current="page"]{color:var(--text)}
.nav-toggle{display:none;margin-left:auto;background:none;border:1px solid var(--line);border-radius:10px;color:var(--text);padding:8px 10px;cursor:pointer}
.hero{padding:96px 0 72px}
.hero .lede{margin-bottom:24px}
.hero-cta{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 20px}
.bullets{list-style:none;margin:0;padding:0;display:flex;gap:18px;flex-wrap:wrap}
.bullets li{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:1rem}
.bullets .icon{color:var(--accent)}
.hero--modern{text-align:center}
.hero--modern .lede{margin-left:auto;margin-right:auto}
.hero--modern .bullets,.hero--modern .hero-cta{justify-content:center}
.hero--editorial{padding:88px 0 64px;text-align:left}
.hero--editorial h1{max-width:20ch}
.hero--editorial .eyebrow{border-radius:0;border:none;border-bottom:2px solid var(--accent);background:none;padding:0 0 6px}
.hero--bold{padding:110px 0 84px;position:relative;overflow:hidden}
.hero--bold::before{content:"";position:absolute;top:-35%;right:-15%;width:52vw;height:52vw;background:radial-gradient(closest-side,var(--accent-soft),transparent 72%);z-index:0}
.hero--bold .wrap{position:relative;z-index:1}
.hero--bold h1{font-size:clamp(2.6rem,7vw,4.6rem);font-weight:800;letter-spacing:-.03em}
.sec-head{max-width:70ch;margin-bottom:28px}
.sec-head .lede{margin-bottom:0}
.tpl-modern .sec-head{text-align:center;margin-left:auto;margin-right:auto}
.tpl-modern .sec-head .lede{margin-left:auto;margin-right:auto}
.grid{display:grid;gap:16px}
.c2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.c3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;transition:transform .18s ease,box-shadow .18s ease}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 28px $shadow}
.chip{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:12px;background:var(--accent-soft);color:var(--accent);margin-bottom:12px}
.chip .icon{width:20px;height:20px}
.card p{color:var(--muted);margin:0}
.stats{display:flex;gap:32px;flex-wrap:wrap;justify-content:center;text-align:center}
.stat-v{font-family:var(--font-head);font-size:clamp(1.8rem,4vw,2.6rem);font-weight:700;color:var(--accent)}
.stat-l{color:var(--muted);font-size:1rem}
.steps{list-style:none;margin:0;padding:0;display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));counter-reset:step}
.steps li{counter-increment:step;position:relative}
.step-n{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);font-weight:700;margin-bottom:10px}
.step-n::before{content:counter(step)}
.gallery{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.tile{position:relative;border-radius:var(--radius);overflow:hidden;aspect-ratio:4/3;border:1px solid var(--line)}
.tile img{width:100%;height:100%;object-fit:cover}
.tile .cap{position:absolute;left:0;right:0;bottom:0;padding:10px 14px;font-size:1rem;color:#fff;background:linear-gradient(transparent,rgba(0,0,0,.65))}
.tile.grad{display:flex;align-items:flex-end}
.tile.grad .fill{position:absolute;inset:0}
.pricing{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));align-items:stretch}
.price-card{display:flex;flex-direction:column}
.price-card .price{font-family:var(--font-head);font-size:2rem;font-weight:700;margin:4px 0}
.price-card .period{color:var(--muted);font-size:1rem}
.price-card ul{list-style:none;margin:12px 0 16px;padding:0;display:grid;gap:8px}
.price-card ul li{display:flex;gap:8px;align-items:flex-start;color:var(--muted);font-size:1rem}
.price-card ul .icon{color:var(--accent);margin-top:.2em}
.price-card .btn{margin-top:auto;justify-content:center}
.price-card.featured{border-color:var(--accent);box-shadow:0 14px 34px $accent_shadow}
.badge{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);font-size:1rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:4px 12px;border-radius:999px;white-space:nowrap}
.price-card{position:relative}
.quotes{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.quote-card .q-ico{color:var(--accent);margin-bottom:8px}
.quote-card blockquote{margin:0 0 14px;color:var(--text);font-size:1rem}
.quote-card .who{display:flex;align-items:center;gap:10px}
.avatar{width:38px;height:38px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;color:var(--on-accent);background:linear-gradient(135deg,var(--accent),var(--accent2));flex:none}
.who .nm{font-weight:600;font-size:1rem}
.who .rl{color:var(--muted);font-size:1rem}
.faq-list{display:grid;gap:10px;max-width:820px}
.tpl-modern .faq-list{margin:0 auto}
details{border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);padding:0}
summary{cursor:pointer;padding:16px 18px;font-weight:600;list-style:none;display:flex;justify-content:space-between;gap:12px;align-items:center}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";color:var(--accent);font-size:1.3rem;line-height:1}
details[open] summary::after{content:"\\2212"}
details .a{padding:0 18px 16px;color:var(--muted)}
.cta-panel{background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);border-radius:calc(var(--radius) + 6px);padding:48px 32px;text-align:center}
.cta-panel h2{color:inherit}
.cta-panel .lede{color:inherit;opacity:.9;margin:0 auto 20px}
.cta-panel .btn.ghost{border-color:currentColor;color:inherit;background:transparent}
.cta-panel .btn.primary{background:$bg;color:$text;box-shadow:none}
.contact-grid{display:grid;gap:28px;grid-template-columns:1.1fr .9fr;align-items:start}
@media(max-width:860px){.contact-grid{grid-template-columns:1fr}}
.contact-info{display:grid;gap:12px}
.contact-info .row{display:flex;gap:10px;align-items:flex-start;color:var(--muted)}
.contact-info .row .icon{color:var(--accent);margin-top:.2em}
.form{display:grid;gap:12px}
.form label{font-size:1rem;color:var(--muted);display:grid;gap:6px}
.form input,.form textarea{width:100%;padding:12px 14px;border-radius:10px;border:1px solid var(--line);background:var(--surface2);color:var(--text);font:inherit}
.form input:focus,.form textarea:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
.about-grid{display:grid;gap:28px;grid-template-columns:1.2fr .8fr;align-items:start}
@media(max-width:860px){.about-grid{grid-template-columns:1fr}}
.about-body p{color:var(--muted)}
.about-panel{border-radius:var(--radius);min-height:260px;background:linear-gradient(135deg,var(--accent-soft),transparent 60%),radial-gradient(closest-side,var(--accent-soft),transparent);border:1px solid var(--line)}
.points{display:grid;gap:12px;margin-top:16px}
.points .pt{display:flex;gap:10px}
.points .pt .icon{color:var(--accent);margin-top:.25em}
.points .pt b{display:block}
.points .pt span{color:var(--muted);font-size:1rem}
.team-grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.team-card .avatar{width:56px;height:56px;font-size:1.05rem;margin-bottom:12px}
.team-card .role{color:var(--accent);font-size:1rem;font-weight:600}
.team-card .bio{color:var(--muted);font-size:1rem;margin:8px 0 0}
.menu-group{margin-bottom:28px}
.menu-group h3{margin-bottom:14px}
.menu-item{display:flex;align-items:baseline;gap:10px;padding:7px 0}
.menu-item .mi-name{font-weight:600}
.menu-item .mi-desc{color:var(--muted);font-size:1rem;width:100%}
.menu-item .dots{flex:1;border-bottom:2px dotted var(--line);transform:translateY(-4px);min-width:24px}
.menu-item .mi-price{font-weight:700;color:var(--accent);white-space:nowrap}
.menu-item .mi-col{display:flex;flex-direction:column;max-width:60%}
.logos{display:flex;gap:14px 28px;flex-wrap:wrap;justify-content:center;align-items:center}
.logos span{color:var(--muted);font-weight:600;font-family:var(--font-head);font-size:1.05rem;letter-spacing:.02em}
.site-footer{border-top:1px solid var(--line);padding:32px 0;color:var(--muted);font-size:.92rem;margin-top:24px}
.foot-row{display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between}
.foot-links{display:flex;gap:16px;flex-wrap:wrap}
.foot-links a{color:var(--muted);text-decoration:none}
.foot-links a:hover{color:var(--text)}
.credit{margin-top:10px;font-size:.92rem;opacity:.85}
.reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}
@media(max-width:860px){.nav-links{display:none;position:absolute;top:64px;left:0;right:0;background:var(--bg);border-bottom:1px solid var(--line);flex-direction:column;align-items:flex-start;padding:16px 24px;gap:14px}
.nav-links.open{display:flex}.nav-toggle{display:inline-flex}}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none}html{scroll-behavior:auto}}
.tpl-bold .btn{border-radius:999px;padding:13px 22px}
.tpl-editorial h2,.tpl-editorial h3{font-family:var(--font-head)}
""")

JS = """(function(){
var t=document.querySelector('.nav-toggle'),m=document.getElementById('site-nav');
if(t&&m){t.addEventListener('click',function(){var o=m.classList.toggle('open');t.setAttribute('aria-expanded',o?'true':'false');});}
var f=document.querySelector('form[data-mailto]');
if(f){f.addEventListener('submit',function(e){e.preventDefault();var d=new FormData(f);
var s=encodeURIComponent('['+(document.title||'Site')+'] message from '+(d.get('name')||''));
var b=encodeURIComponent((d.get('message')||'')+'\\n\\nReply to: '+(d.get('email')||''));
window.location.href='mailto:'+f.getAttribute('data-mailto')+'?subject='+s+'&body='+b;});}
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}});},{threshold:.12});
document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});}
else{document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in');});}
})();"""


# ---------------------------------------------------------------- helpers

def resolve_href(href: str, site: dict, current_slug: str) -> str:
    href = str(href or "#")
    if href.startswith(("#", "http://", "https://", "mailto:", "tel:")) or href.startswith("/"):
        return href
    slug = re.sub(r"\.html?$", "", href)
    for page in site.get("pages", []):
        if page["slug"] == slug:
            return "index.html" if page["slug"] == "index" else f"{page['slug']}.html"
    return href


def btn(a: dict | None, site: dict, current_slug: str, primary: bool = True) -> str:
    if not a or not a.get("label"):
        return ""
    cls = "btn primary" if primary else "btn ghost"
    return f'<a class="{cls}" href="{esc(resolve_href(a.get("href"), site, current_slug))}">{esc(a["label"])}</a>'


def sec_head(d: dict) -> str:
    if not d.get("title"):
        return ""
    sub = f'<p class="lede">{esc(d["subhead"])}</p>' if d.get("subhead") else ""
    return f'<div class="sec-head"><h2>{esc(d["title"])}</h2>{sub}</div>'


def initials(name: str) -> str:
    parts = [w[0] for w in re.findall(r"[A-Za-z0-9]+", str(name or "?"))[:2]]
    return ("".join(parts) or "?").upper()


# ---------------------------------------------------------------- sections

def render_section(sec: dict, site: dict, pal: dict, current_slug: str) -> str:
    kind, d = sec["type"], sec["data"]
    sid = esc(sec["id"])

    if kind == "hero":
        tpl = site["theme"]["template"]
        bullets = "".join(f'<li>{icon("check")}<span>{esc(b)}</span></li>' for b in d.get("bullets", []))
        return (
            f'<section id="{sid}" class="hero hero--{esc(tpl)}"><div class="wrap">'
            + (f'<span class="eyebrow">{esc(d["eyebrow"])}</span>' if d.get("eyebrow") else "")
            + f'<h1>{esc(d["headline"])}</h1>'
            + (f'<p class="lede">{esc(d["subhead"])}</p>' if d.get("subhead") else "")
            + f'<div class="hero-cta">{btn(d.get("primary"), site, current_slug, True)}{btn(d.get("secondary"), site, current_slug, False)}</div>'
            + (f'<ul class="bullets">{bullets}</ul>' if bullets else "")
            + "</div></section>")

    if kind == "features":
        cards = "".join(
            f'<div class="card reveal"><span class="chip">{icon(it["icon"])}</span>'
            f'<h3>{esc(it["title"])}</h3><p>{esc(it["body"])}</p></div>'
            for it in d.get("items", []))
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="grid c3">{cards}</div></div></section>')

    if kind == "stats":
        items = "".join(f'<div class="stat"><div class="stat-v">{esc(it["value"])}</div>'
                        f'<div class="stat-l">{esc(it["label"])}</div></div>' for it in d.get("items", []))
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="stats">{items}</div></div></section>')

    if kind == "steps":
        items = "".join(
            f'<li class="card reveal"><span class="step-n" aria-hidden="true"></span>'
            f'<h3>{esc(it["title"])}</h3><p>{esc(it["body"])}</p></li>'
            for it in d.get("items", []))
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<ol class="steps">{items}</ol></div></section>')

    if kind == "gallery":
        base_hue = hue_of(pal["accent"])
        tiles = []
        for i, it in enumerate(d.get("items", [])):
            hue = it.get("hue")
            hue = int(hue) % 360 if hue is not None else int((base_hue + i * 37) % 360)
            cap = esc(it.get("caption") or it.get("label") or "")
            if it.get("src"):
                inner = (f'<img src="{esc(it["src"])}" alt="{esc(it.get("alt") or it.get("label") or "")}" loading="lazy">'
                         + (f'<div class="cap">{cap}</div>' if cap else ""))
            else:
                inner = (f'<div class="fill" style="background:linear-gradient(135deg,hsl({hue} 62% 52%),hsl({(hue + 42) % 360} 62% 40%))"></div>'
                         + (f'<div class="cap">{cap}</div>' if cap else ""))
            tiles.append(f'<figure class="tile grad reveal" style="margin:0">{inner}</figure>')
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="gallery">{"".join(tiles)}</div></div></section>')

    if kind == "pricing":
        cards = []
        for it in d.get("items", []):
            feats = "".join(f'<li>{icon("check")}<span>{esc(f)}</span></li>' for f in it.get("features", []))
            period = f'<span class="period">{esc(it["period"])}</span>' if it.get("period") else ""
            badge = f'<span class="badge">{esc(it["badge"] or "Featured")}</span>' if it.get("featured") else ""
            cards.append(
                f'<div class="card price-card{" featured" if it.get("featured") else ""} reveal">{badge}'
                f'<h3>{esc(it["name"])}</h3>'
                + (f'<div class="price">{esc(it["price"])}{period}</div>' if it.get("price") else "")
                + (f'<p>{esc(it["blurb"])}</p>' if it.get("blurb") else "")
                + (f"<ul>{feats}</ul>" if feats else "")
                + btn(it.get("cta"), site, current_slug, True)
                + "</div>")
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="pricing">{"".join(cards)}</div></div></section>')

    if kind == "testimonials":
        cards = "".join(
            f'<div class="card quote-card reveal"><div class="q-ico">{icon("quote")}</div>'
            f'<blockquote>{esc(it["quote"])}</blockquote><div class="who">'
            f'<span class="avatar" aria-hidden="true">{esc(initials(it.get("name")))}</span>'
            f'<div><div class="nm">{esc(it.get("name") or "Anonymous")}</div>'
            + (f'<div class="rl">{esc(it["role"])}</div>' if it.get("role") else "")
            + "</div></div></div>"
            for it in d.get("items", []))
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="quotes">{cards}</div></div></section>')

    if kind == "faq":
        items = "".join(
            f'<details><summary>{esc(it["q"])}</summary><div class="a">{esc(it["a"])}</div></details>'
            for it in d.get("items", []))
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="faq-list">{items}</div></div></section>')

    if kind == "cta":
        return (f'<section id="{sid}" class="sec"><div class="wrap"><div class="cta-panel">'
                f'<h2>{esc(d["title"])}</h2>'
                + (f'<p class="lede">{esc(d["body"])}</p>' if d.get("body") else "")
                + f'<div class="hero-cta" style="justify-content:center">{btn(d.get("primary"), site, current_slug, True)}{btn(d.get("secondary"), site, current_slug, False)}</div>'
                + "</div></div></section>")

    if kind == "contact":
        rows = []
        if d.get("email"):
            rows.append(f'<div class="row">{icon("mail")}<span>{esc(d["email"])}</span></div>')
        if d.get("phone"):
            rows.append(f'<div class="row">{icon("phone")}<span>{esc(d["phone"])}</span></div>')
        if d.get("address"):
            rows.append(f'<div class="row">{icon("pin")}<span>{esc(d["address"])}</span></div>')
        if d.get("hours"):
            rows.append(f'<div class="row">{icon("clock")}<span>{esc(d["hours"])}</span></div>')
        form = ""
        if d.get("email"):
            form = (f'<form class="form" data-mailto="{esc(d["email"])}">'
                    f'<label>Name<input name="name" required></label>'
                    f'<label>Email<input name="email" type="email" required></label>'
                    f'<label>Message<textarea name="message" rows="5" required></textarea></label>'
                    f'<button class="btn primary" type="submit">Send message</button>'
                    f'<p class="lede" style="font-size:.8rem">Opens your email app; nothing is sent from this page.</p></form>')
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                + (f'<p class="lede">{esc(d["body"])}</p>' if d.get("body") else "")
                + f'<div class="contact-grid"><div class="contact-info">{"".join(rows)}</div>{form}</div>'
                + "</div></section>")

    if kind == "about":
        paras = "".join(f"<p>{esc(p)}</p>" for p in d.get("body", []))
        points = "".join(
            f'<div class="pt">{icon("check")}<div><b>{esc(p["title"])}</b>'
            + (f"<span>{esc(p['body'])}</span>" if p.get("body") else "")
            + "</div></div>"
            for p in d.get("points", []))
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="about-grid"><div class="about-body">{paras}'
                + (f'<div class="points">{points}</div>' if points else "")
                + f'</div><div class="about-panel" aria-hidden="true"></div></div></div></section>')

    if kind == "team":
        cards = "".join(
            f'<div class="card team-card reveal"><span class="avatar" aria-hidden="true">{esc(initials(it["name"]))}</span>'
            f'<h3>{esc(it["name"])}</h3>'
            + (f'<div class="role">{esc(it["role"])}</div>' if it.get("role") else "")
            + (f'<p class="bio">{esc(it["bio"])}</p>' if it.get("bio") else "")
            + "</div>"
            for it in d.get("items", []))
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="team-grid">{cards}</div></div></section>')

    if kind == "menu":
        groups = []
        for g in d.get("groups", []):
            rows = []
            for it in g.get("items", []):
                left = f'<div class="mi-col"><span class="mi-name">{esc(it["name"])}</span>'
                if it.get("desc"):
                    left += f'<span class="mi-desc">{esc(it["desc"])}</span>'
                left += "</div>"
                rows.append(f'<div class="menu-item">{left}<span class="dots" aria-hidden="true"></span>'
                            f'<span class="mi-price">{esc(it.get("price") or "")}</span></div>')
            head = f"<h3>{esc(g['name'])}</h3>" if g.get("name") else ""
            groups.append(f'<div class="menu-group">{head}{"".join(rows)}</div>')
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}{"".join(groups)}</div></section>')

    if kind == "logocloud":
        items = "".join(f"<span>{esc(i)}</span>" for i in d.get("items", []))
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'<div class="logos">{items}</div></div></section>')

    return ""


# ---------------------------------------------------------------- page

def render_page(page: dict, site: dict, noindex: bool) -> str:
    pal = build_palette(site["theme"], site["meta"]["title"])
    css = CSS_TEMPLATE.substitute(pal)
    tpl = site["theme"]["template"]
    current_slug = page["slug"]

    brand = site["meta"]["title"]
    nav_links = []
    for n in site.get("nav", []):
        href = resolve_href(n["href"], site, current_slug)
        aria = ' aria-current="page"' if href.endswith(f"{current_slug}.html") and not href.startswith("#") else ""
        nav_links.append(f'<a href="{esc(href)}"{aria}>{esc(n["label"])}</a>')
    nav_html = "".join(nav_links)

    foot_links = "".join(f'<a href="{esc(resolve_href(l["href"], site, current_slug))}">{esc(l["label"])}</a>'
                         for l in site.get("footer", {}).get("links", []))
    credit = ('<div class="wrap credit">Built with SpiderCaster (openwork_space)</div>'
              if site.get("footer", {}).get("credit") else "")

    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else ""
    robots_note = "<!-- SpiderCaster: noindex until approved -->" if noindex else ""

    sections_html = "\n".join(render_section(sec, site, pal, current_slug) for sec in page["sections"])
    title = page["title"] if page["title"] == brand else f"{page['title']} - {brand}"

    return f"""<!doctype html>
<html lang="{esc(site['meta'].get('lang') or 'en')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(site['meta']['description'])}">
{robots}
<meta property="og:title" content="{esc(page['title'])}">
<meta property="og:description" content="{esc(site['meta']['description'])}">
<meta property="og:type" content="website">
<meta name="theme-color" content="{esc(pal['accent'])}">
{robots_note}
<style>
{css}
</style>
</head>
<body class="tpl-{esc(tpl)}">
<header class="site-header">
<div class="wrap nav">
<a class="brand" href="index.html">{esc(brand)}</a>
<button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">{icon('menu')}</button>
<nav id="site-nav" class="nav-links">{nav_html}</nav>
</div>
</header>
<main>
{sections_html}
</main>
<footer class="site-footer">
<div class="wrap foot-row">
<div>{esc(site['footer']['text'])}</div>
<div class="foot-links">{foot_links}</div>
</div>
{credit}
</footer>
<script>
{JS}
</script>
</body>
</html>
"""


def assemble(site: dict, noindex: bool = True) -> list[dict]:
    """IR -> list of {file, html}. Deterministic; zero tokens."""
    out = []
    for page in site.get("pages", []):
        fname = "index.html" if page["slug"] == "index" else f"{page['slug']}.html"
        out.append({"file": fname, "html": render_page(page, site, noindex)})
    return out
