"""Deterministic renderer: site IR -> static HTML. Zero tokens, every time.

Single-file pages (inline CSS + JS), system font stacks, inline SVG icons,
gradient visuals. No external requests, no hotlinking, no build deps.
"""
from __future__ import annotations

import colorsys
import json
import re
import struct
from pathlib import Path
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
    r, g, b = (max(0, min(255, int(v))) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


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


def contrast_ratio(a: str, b: str) -> float:
    hi, lo = luminance(a), luminance(b)
    if hi < lo:
        hi, lo = lo, hi
    return (hi + 0.05) / (lo + 0.05)


def contrast_on(h: str) -> str:
    dark, light = "#10131a", "#ffffff"
    if contrast_ratio(h, dark) >= contrast_ratio(h, light):
        return dark
    return light


def readable(fg: str, bg: str, floor: float = 4.5) -> str:
    """Move fg toward white or black until it clears floor against bg."""
    if contrast_ratio(fg, bg) >= floor:
        return fg
    toward = "#ffffff" if luminance(bg) < 0.4 else "#10131a"
    a, b = hex_to_rgb(fg), hex_to_rgb(toward)
    best = toward
    lo, hi = 0.0, 1.0
    for _ in range(14):
        t = (lo + hi) / 2
        mix = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
        col = rgb_to_hex(*mix)
        if contrast_ratio(col, bg) >= floor:
            best = col
            hi = t
        else:
            lo = t
    return best


def readable_on_all(fg: str, bgs, floor: float = 4.6) -> str:
    """Nudge fg until it clears floor on every bg in bgs (worst case wins)."""
    for _ in range(4):
        for bg in bgs:
            fg = readable(fg, bg, floor)
        if all(contrast_ratio(fg, bg) >= 4.5 for bg in bgs):
            break
    return fg


def rgba(h: str, a: float) -> str:
    r, g, b = hex_to_rgb(h)
    return f"rgba({r}, {g}, {b}, {a})"


def hue_of(h: str) -> float:
    r, g, b = (v / 255.0 for v in hex_to_rgb(h))
    hh, _, _ = colorsys.rgb_to_hsv(r, g, b)
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
                "text": "#e9eef6", "muted": "#b7c2d0"}
    else:
        base = {"bg": "#f7f8fa", "surface": "#ffffff", "surface2": "#f1f3f7",
                "text": "#171a21", "muted": "#3e4652"}
    pal = dict(base)
    pal["muted"] = readable(base["muted"], base["bg"])
    on_accent = contrast_on(accent)
    if contrast_ratio(accent2, on_accent) < 4.5:
        accent2 = accent
    pal.update({
        "dark": dark,
        "accent": accent,
        "accent2": accent2,
        "on_accent": on_accent,
        # accent as TEXT/ICON colour must clear 4.5:1 on bg, surface and surface2 (links,
        # roles, stat numbers, prices, icons). The raw accent stays for fills and borders.
        "accent_text": readable_on_all(accent, (base["bg"], base["surface"], base["surface2"])),
        "price": readable_on_all(accent, (base["bg"], base["surface"], base["surface2"])),
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
html{scroll-behavior:smooth;font-size:18px;scroll-padding-top:calc(72px + env(safe-area-inset-top));scroll-padding-bottom:calc(84px + env(safe-area-inset-bottom))}
body{margin:0;font-family:$font_body;background:$bg;color:$text;line-height:1.6;-webkit-font-smoothing:antialiased}
:root{--bg:$bg;--surface:$surface;--surface2:$surface2;--text:$text;--muted:$muted;--line:$line;--accent:$accent;--accent-text:$accent_text;--accent2:$accent2;--on-accent:$on_accent;--price:$price;--accent-soft:$accent_soft;--radius:$radius;--maxw:1120px;--font-head:$font_head;--font-body:$font_body}
.skip{position:absolute;left:12px;top:-80px;background:$surface;color:$text;padding:10px 14px;min-height:44px;z-index:5;border-radius:10px;text-decoration:none}
.phone-bar{display:none}
.skip:focus{top:12px}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid var(--text);outline-offset:2px}
img{max-width:100%;height:auto;display:block}
a{color:var(--accent-text)}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px}
section{padding:72px 0;scroll-margin-top:calc(72px + env(safe-area-inset-top))}
/* D5 phone order: sections carrying data-sc-order reorder below 1280px only
   (the mobile block, 360-first); 1280px and up keeps DOM order. */
@media(max-width:1279px){main:has(>section[data-sc-order]){display:flex;flex-direction:column}}
h1,h2,h3{font-family:var(--font-head);line-height:1.15;margin:0 0 12px;letter-spacing:-.015em}
h1,h2{scroll-margin-top:calc(72px + env(safe-area-inset-top))}
h1{font-size:clamp(1.7rem,5.5vw,3.9rem);overflow-wrap:anywhere}
h2{font-size:clamp(1.6rem,3vw,2.3rem)}
h3{font-size:1.12rem}
p{margin:0 0 14px}
.lede{color:var(--muted);font-size:1.08rem;max-width:62ch}
.eyebrow{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border:1px solid var(--line);border-radius:999px;font-size:1rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);background:var(--surface);margin-bottom:16px}
.icon{width:1.15em;height:1.15em;flex:none;vertical-align:-.2em}
.btn{display:inline-flex;align-items:center;gap:8px;min-height:44px;min-width:44px;padding:11px 18px;border-radius:10px;font-weight:600;text-decoration:none;font-size:1rem;border:1px solid transparent;transition:transform .15s ease,box-shadow .15s ease}
.btn.primary{background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);box-shadow:0 6px 18px $accent_shadow}
.btn.primary:hover{transform:translateY(-1px)}
.btn.ghost{border-color:var(--line);color:var(--text);background:var(--surface)}
.site-header{position:sticky;top:0;z-index:50;background:$header_bg;border-bottom:1px solid var(--line);padding-top:env(safe-area-inset-top);transition:background .2s ease,box-shadow .2s ease}
.site-header.is-stuck{background:var(--bg);box-shadow:0 10px 28px $shadow}
/* blur lives on a pseudo-element layer: backdrop-filter on .site-header itself would make the header the
   containing block for the position:fixed mobile drawer and trap it in the 65px bar (DEFECT_4) */
.site-header::before{content:"";position:absolute;inset:0;z-index:-1;-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);pointer-events:none}
.nav{display:flex;align-items:center;gap:12px;min-height:64px;flex-wrap:wrap}
.brand{display:inline-flex;align-items:center;gap:10px;min-width:0;min-height:44px;font-weight:700;font-size:1.05rem;text-decoration:none;color:var(--text);font-family:var(--font-head)}
.brand-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.brand-mark{width:28px;height:28px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;background:var(--accent);color:var(--on-accent);font-family:Georgia,'Times New Roman',serif;font-weight:700;flex:none}
.nav-here{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--muted);font-size:1rem}
.nav-links{display:flex;flex-wrap:wrap;gap:8px 18px;margin-left:auto;align-items:center;min-width:0}
.nav-links a{color:var(--muted);text-decoration:none;font-size:1rem;min-height:44px;min-width:44px;display:inline-flex;align-items:center;white-space:normal;overflow-wrap:anywhere;max-width:100%}
.nav-links a:hover,.nav-links a[aria-current="page"]{color:var(--text)}
.nav-toggle{display:none;margin-left:auto;flex:none;background:none;border:1px solid var(--line);border-radius:12px;color:var(--text);width:44px;height:44px;align-items:center;justify-content:center;cursor:pointer}
.hero{padding:28px 0 56px}
.hero-stage{display:block}
.hero-visual{position:relative;overflow:hidden;border-radius:18px;border:1px solid var(--line);aspect-ratio:16/9;height:auto;margin:0 0 18px;background:
radial-gradient(120% 90% at 100% 0%,var(--accent-soft),transparent 55%),
linear-gradient(160deg,var(--surface),var(--bg))}
.hero-visual img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center}
.hero-mark{display:flex;align-items:center;justify-content:center;padding:18px}
.hero-mark span{font-family:Georgia,'Times New Roman',serif;font-size:clamp(3rem,12vw,4.6rem);line-height:1;color:var(--accent-text)}
.hero .lede{margin-bottom:18px}
.hero-cta{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 18px}
.hero-cta .btn{min-height:44px}
.hero-more{display:inline-flex;align-items:center;min-height:44px;min-width:44px;color:var(--muted);text-underline-offset:3px}
.hero-more:hover{color:var(--text)}
.cta-panel .cta-more{display:inline-flex;align-items:center;min-height:44px;min-width:44px;color:inherit;text-underline-offset:3px}
.bullets{list-style:none;margin:0;padding:0;display:flex;gap:14px 18px;flex-wrap:wrap}
.bullets li{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:1rem}
.bullets .icon{color:var(--accent-text)}
.hero--modern{text-align:left}
.hero--editorial h1{max-width:16ch}
.hero--editorial .eyebrow{border-radius:0;border:none;border-bottom:2px solid var(--accent);background:none;padding:0 0 6px}
.hero--bold{position:relative}
.hero--bold h1{font-size:clamp(1.7rem,8vw,4.2rem);font-weight:800;letter-spacing:-.03em}
@media(min-width:861px){
.hero{padding:72px 0 80px}
.hero-stage{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(240px,.85fr);gap:40px;align-items:center}
.hero-copy{grid-column:1;grid-row:1}
.hero-visual{grid-column:2;grid-row:1;aspect-ratio:auto;height:320px;margin:0}
.hero--modern{text-align:center}
.hero--modern .hero-stage{grid-template-columns:1fr;justify-items:center}
.hero--modern .hero-copy{grid-column:1;grid-row:2;max-width:70ch}
.hero--modern .hero-visual{grid-column:1;grid-row:1;width:min(100%,760px);margin-bottom:8px}
.hero--modern .lede{margin-left:auto;margin-right:auto}
.hero--modern .bullets,.hero--modern .hero-cta{justify-content:center}
.hero--bold .hero-visual{height:380px}
.hero-visual.hero-mark,.hero--bold .hero-visual.hero-mark{height:auto;max-height:140px;aspect-ratio:2/1}
}
@media(min-width:1280px){
section{padding:88px 0}
.hero{padding:88px 0 96px}
.hero-stage{gap:48px}
.grid,.quotes,.pricing,.steps,.gallery,.team-grid{gap:20px}
.wrap{padding:0 32px}
}
.sec-head{max-width:70ch;margin-bottom:28px}
.sec-head .lede{margin-bottom:0}
.tpl-modern .sec-head{text-align:center;margin-left:auto;margin-right:auto}
.tpl-modern .sec-head .lede{margin-left:auto;margin-right:auto}
.grid{display:grid;gap:16px}
.c2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.c3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;transition:transform .18s ease,box-shadow .18s ease}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 28px $shadow}
.chip{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:12px;background:var(--accent-soft);color:var(--accent-text);margin-bottom:12px}
.chip .icon{width:20px;height:20px}
.card p{color:var(--muted);margin:0}
.stats{display:flex;gap:32px;flex-wrap:wrap;justify-content:center;text-align:center}
.stat-v{font-family:var(--font-head);font-size:clamp(1.8rem,4vw,2.6rem);font-weight:700;color:var(--accent-text)}
.stat-l{color:var(--muted);font-size:1rem}
.steps{list-style:none;margin:0;padding:0;display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));counter-reset:step}
.steps li{counter-increment:step;position:relative}
.step-n{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);font-weight:700;margin-bottom:10px}
.step-n::before{content:counter(step)}
.gallery{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.tile{position:relative;border-radius:var(--radius);overflow:hidden;aspect-ratio:4/3;border:1px solid var(--line)}
.tile img{width:100%;height:100%;object-fit:cover}
.tile .cap{position:absolute;left:0;right:0;bottom:0;padding:10px 14px;font-size:1rem;color:#fff;background:rgba(0,0,0,.72)}
.tile.grad{display:flex;align-items:flex-end}
.tile.grad .fill{position:absolute;inset:0}
.pricing{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));align-items:stretch}
.price-card{display:flex;flex-direction:column}
.price-card .price{font-family:var(--font-head);font-size:2rem;font-weight:700;margin:4px 0}
.price-card .period{color:var(--muted);font-size:1rem}
.price-card ul{list-style:none;margin:12px 0 16px;padding:0;display:grid;gap:8px}
.price-card ul li{display:flex;gap:8px;align-items:flex-start;color:var(--muted);font-size:1rem}
.price-card ul .icon{color:var(--accent-text);margin-top:.2em}
.price-card .btn{margin-top:auto;justify-content:center}
.price-card.featured{border-color:var(--accent);box-shadow:0 14px 34px $accent_shadow}
.badge{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);font-size:1rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:4px 12px;border-radius:999px;white-space:nowrap}
.price-card{position:relative}
.quotes{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.quote-card .q-ico{color:var(--accent-text);margin-bottom:8px}
.quote-card blockquote{margin:0 0 14px;color:var(--text);font-size:1rem}
.quote-card .who{display:flex;align-items:center;gap:10px}
.avatar{width:44px;height:44px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:1rem;color:var(--on-accent);background:linear-gradient(135deg,var(--accent),var(--accent2));flex:none}
.who .nm{font-weight:600;font-size:1rem}
.who .rl{color:var(--muted);font-size:1rem}
.faq-list{display:grid;gap:10px;max-width:820px}
.tpl-modern .faq-list{margin:0 auto}
details{border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);padding:0}
summary{cursor:pointer;padding:16px 18px;min-height:44px;font-weight:600;list-style:none;display:flex;justify-content:space-between;gap:12px;align-items:center}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";color:var(--accent-text);font-size:1.3rem;line-height:1}
details[open] summary::after{content:"\\2212"}
details .a{padding:0 18px 16px;color:var(--muted)}
.cta-panel{background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--on-accent);border-radius:calc(var(--radius) + 6px);padding:48px 32px;text-align:center}
.cta-panel h2{color:inherit}
.cta-panel .lede{color:inherit;margin:0 auto 20px}
.cta-panel .btn.ghost{border-color:currentColor;color:inherit;background:transparent}
.cta-panel .btn.primary{background:$bg;color:$text;box-shadow:none}
.contact-grid{display:grid;gap:28px;grid-template-columns:1fr;align-items:start}
@media(min-width:861px){.contact-grid{grid-template-columns:1.1fr .9fr}}
.contact-info{display:grid;gap:12px}
.contact-info .row{display:flex;gap:10px;align-items:center;color:var(--muted);min-height:44px}
.contact-info .row a{color:inherit;text-decoration:none;min-height:44px;min-width:44px;display:inline-flex;align-items:center}
.contact-info .row .icon{color:var(--accent-text)}
.form{display:grid;gap:12px}
.form label{font-size:1rem;color:var(--muted);display:grid;gap:6px}
.form input,.form textarea{width:100%;padding:12px 14px;border-radius:10px;border:1px solid var(--line);background:var(--surface2);color:var(--text);font:inherit;font-size:max(16px,1rem)}
.form ::placeholder{color:var(--muted);opacity:1}
.form input:focus,.form textarea:focus{outline:2px solid var(--accent-text);outline-offset:1px;border-color:transparent}
.about-body p{color:var(--muted)}
.points{display:grid;gap:12px;margin-top:16px}
.points .pt{display:flex;gap:10px}
.points .pt .icon{color:var(--accent-text);margin-top:.25em}
.points .pt b{display:block}
.points .pt span{color:var(--muted);font-size:1rem}
.team-grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.team-card .avatar{width:56px;height:56px;font-size:1.05rem;margin-bottom:12px}
.team-card .role{color:var(--accent-text);font-size:1rem;font-weight:600}
.team-card .bio{color:var(--muted);font-size:1rem;margin:8px 0 0}
.menu-group{margin-bottom:28px}
.menu-group h3{margin-bottom:14px}
.menu-item{display:flex;align-items:center;gap:10px;padding:7px 0;min-height:48px}
.menu-item .mi-name{font-weight:600}
.menu-item .mi-desc{color:var(--muted);font-size:1rem;width:100%}
.menu-item .dots{flex:0 1 1.5rem;border-bottom:2px dotted var(--line);min-width:12px}
.menu-item .mi-price{font-weight:700;color:var(--price);white-space:nowrap;flex:none}
.menu-item .mi-col{display:flex;flex-direction:column;flex:1;min-width:0}
.logos{display:flex;gap:14px 28px;flex-wrap:wrap;justify-content:center;align-items:center}
.logos span{color:var(--muted);font-weight:600;font-family:var(--font-head);font-size:1.05rem;letter-spacing:.02em}
.site-footer{border-top:1px solid var(--line);padding:32px 0 calc(32px + env(safe-area-inset-bottom));color:var(--muted);font-size:1rem;margin-top:24px}
.foot-row{display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between}
.foot-links{display:flex;gap:16px;flex-wrap:wrap}
.foot-links a{color:var(--muted);text-decoration:none;min-height:44px;min-width:44px;display:inline-flex;align-items:center}
.foot-links a:hover{color:var(--text)}
.credit{margin-top:10px;font-size:1rem}
.reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}
@media(max-width:860px){
.nav{flex-wrap:nowrap}
.brand{flex:1 1 auto;min-width:0}
.reveal{opacity:1;transform:none}
.nav-links{display:none;position:fixed;z-index:40;left:0;right:0;bottom:0;top:calc(64px + env(safe-area-inset-top));background:var(--bg);flex-direction:column;flex-wrap:nowrap;align-items:stretch;padding:8px 18px calc(18px + env(safe-area-inset-bottom));gap:0;overflow-y:auto;overscroll-behavior:contain}
.nav-links.open{display:flex}
.nav-links a{flex:none;width:100%;min-height:48px;padding:12px 0;border-bottom:1px solid var(--line);font-size:1.05rem}
.hero-cta{flex-direction:column;align-items:stretch}
.hero-cta .btn{width:100%;justify-content:center}
.nav-toggle{display:inline-flex}
.nav-here{display:block;flex:0 1 auto;max-width:4.5rem;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.nav-here:empty{display:none}
.wrap{padding:0 16px}
section{padding:20px 0}
section.sec{border-top:1px solid var(--line)}
.sec-head{margin-bottom:12px}
.tpl-modern .sec-head,.tpl-modern .sec-head .lede{text-align:left;margin-left:0;margin-right:0}
.card{padding:14px}
.card:hover{transform:none;box-shadow:none}
h1,h2{text-wrap:balance;overflow-wrap:break-word}
.mi-price{font-variant-numeric:tabular-nums}
.chip{width:32px;height:32px;margin-bottom:8px}
.points{margin-top:8px}
.hero{padding:16px 0 28px}
.hero .lede{margin-bottom:8px}
.about-body p:last-child{margin-bottom:0}
.menu-group{margin-bottom:0}
.grid{gap:8px}
.card h3{margin-bottom:4px;text-wrap:balance;overflow-wrap:break-word}
.card p{text-wrap:pretty}
.card:has(.chip){display:grid;grid-template-columns:32px minmax(0,1fr);column-gap:12px;align-items:start}
.card:has(.chip) .chip{grid-row:1 / span 2;margin-bottom:0}
.card:has(.chip) h3,.card:has(.chip) p{grid-column:2}
.grid.c3{gap:0;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.grid.c3 .card{background:transparent;border:0;border-radius:0;box-shadow:none}
.grid.c3 .card + .card{border-top:1px solid var(--line)}
.hero-visual.hero-mark{aspect-ratio:2/1;height:auto;max-height:120px}
.hero-mark span{font-size:clamp(2.8rem,16vw,4rem)}
.c2,.c3,.quotes,.pricing,.steps,.gallery,.team-grid{grid-template-columns:1fr}
.about-body:not(:has(.points)){border-left:3px solid var(--accent);padding-left:12px}
.about-body:has(.points) > p{border-left:3px solid var(--accent);padding-left:12px}
.points{gap:0;margin-top:12px;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.points .pt{padding:12px 14px;align-items:flex-start}
.points .pt + .pt{border-top:1px solid var(--line)}
.menu-item{display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:12px;row-gap:4px;align-items:baseline;padding:10px 0;border-bottom:1px solid var(--line)}
.menu-item:last-child{border-bottom:0}
.menu-item .mi-col{display:contents}
.menu-item .mi-name{grid-column:1;grid-row:1}
.menu-item .mi-price{grid-column:2;grid-row:1}
.menu-item .mi-desc{grid-column:1 / -1;grid-row:2;width:auto}
.menu-item .dots{display:none}
body.nav-open{overflow:hidden}
.phone-bar{display:flex;position:fixed;z-index:45;left:16px;right:16px;bottom:calc(12px + env(safe-area-inset-bottom));min-height:48px;align-items:center;justify-content:center;padding:0 16px;border-radius:999px;background:var(--accent);color:var(--on-accent);text-decoration:none;font-weight:700;box-shadow:0 8px 24px rgba(0,0,0,.28)}
body:has(.phone-bar){padding-bottom:calc(72px + env(safe-area-inset-bottom))}
body.nav-open .phone-bar{display:none}
}
@media(max-width:860px) and (scripting:none){
.nav{flex-wrap:wrap}
.nav-toggle{display:none}
.nav-links{display:flex;flex-wrap:wrap;position:static;flex:1 1 100%;top:auto;right:auto;bottom:auto;left:auto;background:transparent;padding:0}
}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none}html{scroll-behavior:auto}.site-header,.btn{transition:none}.btn:hover{transform:none}}
.tpl-bold .btn{border-radius:999px;padding:13px 22px}
.tpl-editorial h2,.tpl-editorial h3{font-family:var(--font-head)}
""")

JS = """(function(){
var t=document.querySelector('.nav-toggle'),m=document.getElementById('site-nav');
if(t&&m){t.addEventListener('click',function(){var o=m.classList.toggle('open');t.setAttribute('aria-expanded',o?'true':'false');document.body.classList.toggle('nav-open',o);});
m.addEventListener('click',function(e){if(e.target&&e.target.tagName==='A'){m.classList.remove('open');t.setAttribute('aria-expanded','false');document.body.classList.remove('nav-open');}});}
var head=document.querySelector('.site-header');
function stuck(){if(head) head.classList.toggle('is-stuck',window.scrollY>8);}
stuck();
window.addEventListener('scroll',stuck,{passive:true});
var here=document.querySelector('.nav-here');
if(here&&'IntersectionObserver' in window){var secs=document.querySelectorAll('main section');
var io2=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;var h=en.target.querySelector('h1,h2');var label=h?h.textContent:'';var brand=document.querySelector('.brand-name');if(brand&&label===brand.textContent)label='';here.textContent=label;});},{rootMargin:'-30% 0px -55% 0px',threshold:0});
secs.forEach(function(el){io2.observe(el);});}
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
    if href.startswith(("#", "http://", "https://", "mailto:", "tel:", "/")):
        return href
    slug = re.sub(r"\.html?$", "", href)
    for page in site.get("pages", []):
        if page["slug"] == slug:
            return "index.html" if page["slug"] == "index" else f"{page['slug']}.html"
    return href


def btn(a: dict | None, site: dict, current_slug: str, primary: bool = True, marker: bool = False) -> str:
    if not a or not a.get("label"):
        return ""
    cls = "btn primary" if primary else "btn ghost"
    tag = ' data-cta="primary"' if primary and marker else ""
    return f'<a class="{cls}"{tag} href="{esc(resolve_href(a.get("href"), site, current_slug))}">{esc(a["label"])}</a>'


def _alive_link(a) -> bool:
    """A cited action with a real label and href. Guards hand-edited IR."""
    return (
        isinstance(a, dict)
        and bool(str(a.get("label") or "").strip())
        and bool(str(a.get("href") or "").strip())
    )


def _pick_actions(data: dict, site: dict, current_slug: str, link_cls: str, marker: bool = False) -> tuple[str, str]:
    """One primary button plus, at most, a subordinate text link.

    A lone secondary is promoted to the primary button. A secondary that
    repeats the primary href or label is dropped: the same button twice is
    a second competing treatment in one viewport.
    """
    primary = data.get("primary")
    secondary = data.get("secondary")
    if not _alive_link(primary):
        primary = secondary if _alive_link(secondary) else None
        secondary = None
    p_html = btn(primary, site, current_slug, True, marker) if _alive_link(primary) else ""
    s_html = ""
    if _alive_link(secondary) and _alive_link(primary):
        same_label = str(secondary.get("label")).strip().lower() == str(primary.get("label")).strip().lower()
        same_href = resolve_href(secondary.get("href"), site, current_slug) == resolve_href(
            primary.get("href"), site, current_slug
        )
        if not (same_label or same_href):
            s_html = (
                f'<a class="{link_cls}" href="{esc(resolve_href(secondary.get("href"), site, current_slug))}">'
                f"{esc(str(secondary['label']).strip())}</a>"
            )
    return p_html, s_html


def _hero_actions(data: dict, site: dict, current_slug: str) -> str:
    """One cited primary CTA per hero; secondary is a text link, never a button."""
    p_html, s_html = _pick_actions(data, site, current_slug, "hero-more", True)
    if not (p_html or s_html):
        return ""
    return f'<div class="hero-cta">{p_html}{s_html}</div>'


def _cta_actions(data: dict, site: dict, current_slug: str) -> str:
    """CTA panel mirrors the hero contract: one button, subordinate link."""
    p_html, s_html = _pick_actions(data, site, current_slug, "cta-more", False)
    if not (p_html or s_html):
        return ""
    return f'<div class="hero-cta" style="justify-content:center">{p_html}{s_html}</div>'


def sec_head(d: dict) -> str:
    title = str(d.get("title") or "").strip()
    if not title:
        return ""
    sub = f'<p class="lede">{esc(d["subhead"])}</p>' if d.get("subhead") else ""
    return f'<div class="sec-head"><h2>{esc(title)}</h2>{sub}</div>'


def initials(name: str) -> str:
    parts = [w[0] for w in re.findall(r"[A-Za-z0-9]+", str(name or "?"))[:2]]
    return ("".join(parts) or "?").upper()


def brand_letter(name: str) -> str:
    found = re.findall(r"[A-Za-z0-9]", str(name or ""))
    return (found[0] if found else "S").upper()


def favicon_svg(brand: str, accent: str) -> str:
    letter = brand_letter(brand)
    color = accent if re.fullmatch(r"#[0-9A-Fa-f]{6}", str(accent or "")) else "#c8923e"
    ink = contrast_on(color)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        f'<rect width="32" height="32" rx="8" fill="{color}"/>'
        f'<text x="16" y="22" text-anchor="middle" font-family="Georgia,serif" '
        f'font-size="18" fill="{ink}">{esc(letter)}</text></svg>\n'
    )


def _local_image_src(raw) -> str:
    """Relative hero src already on the IR. Remote and protocol-relative stay empty."""
    if isinstance(raw, dict):
        raw = raw.get("src")
    src = str(raw or "")
    if src and not src.startswith(("http://", "https://", "//")):
        return src
    return ""


def image_box(path: Path) -> tuple[int, int]:
    """PNG or JPEG pixel size. Returns (0, 0) when the header is not one of those."""
    try:
        raw = Path(path).read_bytes()
    except OSError:
        return 0, 0
    if raw.startswith(b"\x89PNG\r\n\x1a\n") and len(raw) >= 24 and raw[12:16] == b"IHDR":
        w, h = struct.unpack(">II", raw[16:24])
        return int(w), int(h)
    if raw.startswith(b"\xff\xd8"):
        i = 2
        while i + 9 < len(raw):
            if raw[i] != 0xFF:
                break
            mark = raw[i + 1]
            if mark in {0xC0, 0xC1, 0xC2}:
                h, w = struct.unpack(">HH", raw[i + 5:i + 9])
                return int(w), int(h)
            if mark == 0xD8 or mark == 0xD9:
                i += 2
                continue
            if i + 4 > len(raw):
                break
            size = struct.unpack(">H", raw[i + 2:i + 4])[0]
            if size < 2:
                break
            i += 2 + size
    return 0, 0


def _lede_html(text) -> str:
    """One paragraph per sentence already in the text. No words are added."""
    raw = str(text or "").strip()
    if not raw:
        return ""
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", raw) if part.strip()]
    return "".join(f'<p class="lede">{esc(part)}</p>' for part in parts)


def _tel_href(phone: str) -> str:
    """tel: from digits already in the copy. No country code is added."""
    text = str(phone or "").strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) < 7:
        return ""
    return "tel:" + ("+" if text.startswith("+") else "") + digits


def _mail_href(email: str) -> str:
    """mailto: only for a single address already in the copy."""
    text = str(email or "").strip()
    if "@" not in text or any(ch in text for ch in " \t\r\n<>\"'"):
        return ""
    return "mailto:" + text


_ASK_LINE_RE = re.compile(r"\b(call|phone|ring|dial|text|sms|reach)\b", re.IGNORECASE)
_PHONE_RUN_RE = re.compile(r"\+?\(?\d[\d\s().\-]{5,}\d")


def _ask_line_digits(data: dict) -> str:
    """Digits from the first explicit ask line (G47 S5 precedence, level 1).

    An ask line names the act (call/phone/ring/...) and carries the number,
    e.g. ``Call (555) 999-0100 today``. Returns the matched digit run
    verbatim, or ``""`` when no ask line carries one.
    """
    lines: list[str] = []
    for key in ("title", "body"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            lines.extend(value.splitlines())
        elif isinstance(value, list):
            lines.extend(str(item) for item in value if isinstance(item, str))
    for line in lines:
        if not _ASK_LINE_RE.search(line):
            continue
        match = _PHONE_RUN_RE.search(line)
        if not match:
            continue
        run = match.group(0).strip()
        if run.startswith("(") and ")" not in run:
            run = run[1:].strip()
        if len("".join(ch for ch in run if ch.isdigit())) >= 7:
            return run
    return ""


def tel_autowire(*blocks: dict | None) -> tuple[str, str]:
    """(href, label) per FINAL D4 / G47 S5 precedence.

    First explicit ask line, else first phone, else first email across the
    contact/cta blocks in order. Digits are verbatim from the copy: no
    country code is added, a leading ``+`` is preserved. Absent contact
    data returns ``("", "")``: the bar is omitted, never invented.
    """
    for data in blocks:
        if not isinstance(data, dict):
            continue
        ask = _ask_line_digits(data)
        if ask:
            return _tel_href(ask), ask
    for data in blocks:
        if not isinstance(data, dict):
            continue
        phone = str(data.get("phone") or "").strip()
        href = _tel_href(phone)
        if href:
            return href, phone
    for data in blocks:
        if not isinstance(data, dict):
            continue
        href = _mail_href(str(data.get("email") or ""))
        if href:
            return href, str(data.get("email") or "").strip()
    return "", ""


def _phone_bar(page: dict) -> str:
    """Fixed tap target, auto-wired at build time from verbatim copy digits.

    Contact block first, cta block as fallback (G47 S5: the contact/cta
    block). Absent digits and absent email render no bar: check FAILs the
    ask slot instead of shipping an invented number.
    """
    contact: dict = {}
    cta: dict = {}
    for sec in page.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
        if sec.get("type") == "contact" and not contact:
            contact = data
        elif sec.get("type") == "cta" and not cta:
            cta = data
    href, label = tel_autowire(contact, cta)
    if not href:
        return ""
    return f'<a class="phone-bar" href="{esc(href)}">{esc(label)}</a>'


def _mobile_section_attrs(sec: dict) -> str:
    """Extra ``<section>`` attributes from the D5 ``mobile`` block.

    ``order`` reorders below 1280px only (paired with the ``main:has()``
    rule in CSS; 1280px+ keeps DOM order). ``stack`` is a declarative
    marker: single-column below 1280px is already the CSS contract, so the
    block records the 360-first design intent without new taxonomy.
    """
    data = sec.get("data") if isinstance(sec, dict) else None
    mob = data.get("mobile") if isinstance(data, dict) else None
    if not isinstance(mob, dict):
        return ""
    out = ""
    order = mob.get("order")
    if isinstance(order, bool):
        order = None
    if isinstance(order, int) and order >= 0:
        out += f' data-sc-order="{order}" style="order:{order}"'
    elif isinstance(order, float) and order.is_integer() and order >= 0:
        out += f' data-sc-order="{int(order)}" style="order:{int(order)}"'
    if mob.get("stack") is True and "data-sc-order" not in out:
        out += ' data-sc-mobile="stack"'
    return out


def _apply_mobile_blocks(sections_html: str, sections: list) -> str:
    """Splice D5 ``mobile`` attributes into rendered ``<section id=...>`` tags."""
    for sec in sections or []:
        if not isinstance(sec, dict) or not sec.get("id"):
            continue
        attrs = _mobile_section_attrs(sec)
        if not attrs:
            continue
        needle = f'<section id="{esc(sec["id"])}"'
        if needle in sections_html:
            sections_html = sections_html.replace(
                needle, needle + attrs, 1
            )
    return sections_html


def _contact_row(kind: str, text: str, href: str) -> str:
    shown = f'<a href="{esc(href)}">{esc(text)}</a>' if href else f"<span>{esc(text)}</span>"
    return f'<div class="row">{icon(kind)}{shown}</div>'


def hero_visual(d: dict, brand: str) -> str:
    src = _local_image_src(d.get("image"))
    if src:
        alt = str(d.get("image_alt") or "").strip() or str(brand or "").strip() or "hero"
        try:
            w, h = int(d.get("image_w") or 0), int(d.get("image_h") or 0)
        except (TypeError, ValueError):
            w, h = 0, 0
        box = f' width="{w}" height="{h}"' if w > 0 and h > 0 else ""
        return (
            f'<div class="hero-visual"><img src="{esc(src)}" alt="{esc(alt)}"{box} '
            f'sizes="100vw" fetchpriority="high" decoding="async"></div>'
        )
    return f'<div class="hero-visual hero-mark" aria-hidden="true"><span>{esc(brand_letter(brand))}</span></div>'


def page_filename(page: dict) -> str:
    slug = str(page.get("slug") or "index")
    return "index.html" if slug == "index" else f"{slug}.html"


def hero_og_image(page: dict) -> str:
    """og:image only when the page hero already has a local relative image."""
    for sec in page.get("sections") or []:
        if not isinstance(sec, dict) or sec.get("type") != "hero":
            continue
        data = sec.get("data") if isinstance(sec.get("data"), dict) else {}
        src = _local_image_src(data.get("image"))
        if not src:
            return ""
        return f'<meta property="og:image" content="{esc(src)}">'
    return ""


def website_jsonld(site: dict) -> str:
    """WebSite node from site meta only. No rating, review, address, or phone."""
    meta = site.get("meta") if isinstance(site.get("meta"), dict) else {}
    payload = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": str(meta.get("title") or ""),
        "description": str(meta.get("description") or ""),
    }
    blob = json.dumps(payload, ensure_ascii=True).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{blob}</script>'


# FAQPage JSON-LD is retired (Google removed the FAQ rich result 2023-2026;
# <seo-research>/schema.md section 1). The renderer emits
# no FAQPage/Question/Answer structured data. Visible FAQ sections
# (render_section kind "faq", native <details>) are unchanged.


# ---------------------------------------------------------------- sections

def render_section(sec: dict, site: dict, pal: dict, current_slug: str) -> str:
    kind, d = sec["type"], sec["data"]
    sid = esc(sec["id"])

    if kind == "hero":
        tpl = site["theme"]["template"]
        bullets = "".join(f'<li>{icon("check")}<span>{esc(b)}</span></li>' for b in d.get("bullets", []))
        brand = site["meta"]["title"]
        return (
            f'<section id="{sid}" class="hero hero--{esc(tpl)}"><div class="wrap hero-stage">'
            + hero_visual(d, brand)
            + '<div class="hero-copy">'
            + (f'<span class="eyebrow">{esc(d["eyebrow"])}</span>' if d.get("eyebrow") else "")
            + f'<h1>{esc(d["headline"])}</h1>'
            + _lede_html(d.get("subhead"))
            + _hero_actions(d, site, current_slug)
            + (f'<ul class="bullets">{bullets}</ul>' if bullets else "")
            + "</div></div></section>")

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
            src = _local_image_src(it.get("src"))
            if src and ".." not in src.replace("\\", "/").split("/"):
                alt = it.get("alt") or it.get("label") or it.get("caption") or "photo"
                inner = (f'<img src="{esc(src)}" alt="{esc(alt)}" loading="lazy">'
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
                + _cta_actions(d, site, current_slug)
                + "</div></div></section>")

    if kind == "contact":
        rows = []
        if d.get("email"):
            rows.append(_contact_row("mail", str(d["email"]), _mail_href(str(d["email"]))))
        if d.get("phone"):
            rows.append(_contact_row("phone", str(d["phone"]), _tel_href(str(d["phone"]))))
        if d.get("address"):
            rows.append(_contact_row("pin", str(d["address"]), ""))
        if d.get("hours"):
            rows.append(f'<div class="row">{icon("clock")}<span>{esc(d["hours"])}</span></div>')
        form = ""
        if d.get("email"):
            form = (f'<form class="form" data-mailto="{esc(d["email"])}">'
                    f'<label>Name<input name="name" required></label>'
                    f'<label>Email<input name="email" type="email" required></label>'
                    f'<label>Message<textarea name="message" rows="5" required></textarea></label>'
                    f'<button class="btn primary" type="submit">Send message</button>'
                    f'<p class="lede">Opens your email app; nothing is sent from this page.</p></form>')
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
        body = (f'<div class="about-body">{paras}'
                + (f'<div class="points">{points}</div>' if points else "")
                + "</div>")
        return (f'<section id="{sid}" class="sec"><div class="wrap">{sec_head(d)}'
                f'{body}</div></section>')

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
            name = str(g.get("name") or "").strip()
            if name == str(d.get("title") or "").strip():
                name = ""
            head = f"<h3>{esc(name)}</h3>" if name else ""
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

    foot_links = "".join(f'<a href="{esc(resolve_href(lnk["href"], site, current_slug))}">{esc(lnk["label"])}</a>'
                         for lnk in site.get("footer", {}).get("links", []))

    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else ""
    robots_note = "<!-- SpiderCaster: noindex until approved -->" if noindex else ""
    fname = page_filename(page)
    og_image = hero_og_image(page)
    jsonld = website_jsonld(site)

    sections_html = _apply_mobile_blocks(
        "\n".join(render_section(sec, site, pal, current_slug) for sec in page["sections"]),
        page["sections"],
    )
    phone_bar = _phone_bar(page)
    title = page["title"] if page["title"] == brand else f"{page['title']} - {brand}"
    desc = str(page.get("description") or "").strip() or str(site["meta"].get("description") or "")

    return f"""<!doctype html>
<html lang="{esc(site['meta'].get('lang') or 'en')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<meta property="og:title" content="{esc(page['title'])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
{og_image}
<meta name="theme-color" content="{esc(pal['accent'])}">
<link rel="canonical" href="{esc(fname)}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="favicon.svg">
{jsonld}
{robots_note}
<style>
{css}
</style>
</head>
<body class="tpl-{esc(tpl)}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
<div class="wrap nav">
<a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">{esc(brand_letter(brand))}</span><span class="brand-name">{esc(brand)}</span></a>
<span class="nav-here" aria-live="polite"></span>
<button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">{icon('menu')}</button>
<nav id="site-nav" class="nav-links">{nav_html}</nav>
</div>
</header>
<main id="main">
{sections_html}
</main>
<footer class="site-footer">
<div class="wrap foot-row">
<div>{esc(site['footer']['text'])}</div>
<div class="foot-links">{foot_links}</div>
</div>
</footer>
{phone_bar}
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
    theme = site.get("theme") if isinstance(site.get("theme"), dict) else {}
    brand = (site.get("meta") or {}).get("title") or "Site"
    accent = build_palette(theme, brand)["accent"]
    out.append({"file": "favicon.svg", "html": favicon_svg(brand, accent)})
    return out
