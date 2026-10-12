#!/usr/bin/env python3
r"""SpiderCaster mobile bench (stdlib, plus Playwright when installed).

Cold start (reuses bench\coldstart_bench.py helpers): copy the tree to a temp dir,
strip provider-key variables, then build, build#2 (PYTHONHASHSEED 1 vs 2, same
SOURCE_DATE_EPOCH), SHA-256 repro, check --expect-noindex, serve (200/404),
doctor, crew selftest and shipcheck.

Then serve the build with `spidercaster.py serve` (binds 127.0.0.1 only) and render
every built page (capped by --pages) at each viewport with Playwright + Chrome.
Default viewports: 360x800, 390x844, 412x800 (mobile) and 1280x800 (desktop baseline).
Gates judged per page per viewport (pass / fail / not-run, with evidence):

  overflow_x           scrollWidth <= innerWidth AND <= clientWidth (1px tolerance). Mobile Chrome widens
                       innerWidth to fit overflowing content, so innerWidth alone cannot catch it
  tap_target_rendered  every visible control >= engine TAP_MIN_PX (44) on both axes at mobile
                       viewports; drawer links are measured again after the menu is opened.
                       Desktop (>480px wide) uses --desktop-tap-floor (default 24 = WCAG 2.5.8 AA)
                       and lists controls under 44px as info
  type_floor_rendered  body element >= engine TYPE_FLOOR_PX; body copy >= BODY_FLOOR_PX;
                       every other visible text >= TYPE_FLOOR_PX (floors read from lib/check.py)
  viewport_meta        <meta name="viewport"> containing width=device-width
  nav_toggle           if a nav exists and its links are hidden, a toggle must open it,
                       aria-expanded must flip false -> true, and every menu link must then be
                       usable: visible box >= 44px (or inside a scroller >= 44px) and not covered
                       at its centre (elementFromPoint); inline nav passes; no nav passes
  sticky_25            no fixed/sticky element in view taller than 25% of the viewport height
  img_srcset           raster <img> carry srcset (and sizes when w descriptors are used);
                       SVG images and inline <svg> are exempt; counts reported
  grey_tile_rendered   FIRST rendered grey_tile check: photo-ish slots (figure, or class/id
                       hero|photo|thumb|image|img|cover|media|picture|placeholder|banner|poster|
                       avatar|gallery) that render a flat grey background or an empty box with no
                       loaded image, plus visible imgs that are broken (404 / naturalWidth 0),
                       never loaded after a full scroll, or point at a placeholder service
  mobile_desktop_diff  informational only: visible element counts, content visible on desktop
                       but hidden on mobile (nav/header excluded)

The capture runs twice (fresh browser each time, identical steps) and every gate verdict
and number must match (capture repro; pixels are not compared). Visibility uses
getBoundingClientRect + computed style + checkVisibility() + closed-<details> rule.
If Playwright or Chrome is missing every mobile gate is not-run with the reason, never pass.

Usage (from V:\A\Ai\spidercaster\working):
  python bench\mobile_bench.py
  python bench\mobile_bench.py --pages 5 --viewports 360x800,1280x800 --keep
  python bench\mobile_bench.py --no-capture            # cold start only (mobile gates not-run)

Writes bench\results\mobile-latest.json/.md and, in --out-dir (default
V:\streams\webdev\OUT\bench-qa): MOBILE_RUN_<ts>.md, READY_MOBILE_<project>_<ts>.md/.json
and MOBILE_CAPTURE_<project>_<ts>\ (patterns.json, dom.html, aria.yml, shot.png, drawer.png).
Exit code: 0 READY, 1 any fail, 2 no fail but something not-run.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import coldstart_bench as cs  # noqa: E402  (stdlib-only; main() is guarded)

DEFAULT_VIEWPORTS = "360x800,390x844,412x800,1280x800"
DEFAULT_OUT = r"V:\streams\webdev\OUT\bench-qa"
GATES = ["overflow_x", "tap_target_rendered", "type_floor_rendered", "viewport_meta", "nav_toggle",
         "sticky_25", "img_srcset", "grey_tile_rendered", "mobile_desktop_diff"]
INFO_GATES = {"mobile_desktop_diff"}
MOBILE_MAX_W = 480
STICKY_MAX = 0.25

# ----------------------------------------------------------------------------- JS probes
HELPERS = r"""
  const W = window.innerWidth, H = window.innerHeight, sx = window.scrollX, sy = window.scrollY;
  const VW = Math.min(W, document.documentElement.clientWidth || W);  // visible layout width (mobile Chrome widens innerWidth to fit overflow)
  const CS = e => getComputedStyle(e);
  const rnd = v => Math.round(v * 10) / 10;
  const cls = e => (typeof e.className === 'string' ? e.className : (e.getAttribute('class') || '')).trim();
  const desc = e => { let s = e.tagName.toLowerCase(); if (e.id) s += '#' + e.id; const c = cls(e); if (c) s += '.' + c.split(/\s+/).slice(0, 3).join('.'); return s; };
  const path = e => { const parts = []; for (let n = e; n && n.nodeType === 1 && n !== document.body; n = n.parentElement) { let i = 1; for (let s = n.previousElementSibling; s; s = s.previousElementSibling) if (s.tagName === n.tagName) i++; parts.unshift(n.tagName.toLowerCase() + ':' + i); } return parts.join('>'); };
  const inClosedDetails = e => { for (let d = e.closest('details'); d; d = d.parentElement && d.parentElement.closest('details')) { if (!d.open) { const sm = d.querySelector(':scope > summary'); if (!(sm && (sm === e || sm.contains(e)))) return true; } } return false; };
  const boxVis = e => { const r = e.getBoundingClientRect(), s = CS(e); if (!(r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none')) return false;
    if (typeof e.checkVisibility === 'function' && !e.checkVisibility({visibilityProperty: true, contentVisibilityAuto: false})) return false;
    return !inClosedDetails(e); };
  const clipped = e => { const r = e.getBoundingClientRect(); for (let c = e, a = e.parentElement; a && a !== document.documentElement; c = a, a = a.parentElement) { if (CS(c).position === 'fixed') break; const s = CS(a); if (s.overflowX !== 'visible' || s.overflowY !== 'visible') { const ar = a.getBoundingClientRect(); if (ar.width < 1 || ar.height < 1) return true; if (r.right <= ar.left || r.left >= ar.right || r.bottom <= ar.top || r.top >= ar.bottom) return true; } } return false; };
  const visBox = e => { const r = e.getBoundingClientRect(); let L = Math.max(r.left, 0), T = Math.max(r.top, 0), Rr = Math.min(r.right, VW), B = Math.min(r.bottom, H), sc = null;
    for (let c = e, a = e.parentElement; a && a !== document.documentElement; c = a, a = a.parentElement) { if (CS(c).position === 'fixed') break; const s = CS(a);
      if (s.overflowX !== 'visible' || s.overflowY !== 'visible') { const ar = a.getBoundingClientRect(); L = Math.max(L, ar.left); T = Math.max(T, ar.top); Rr = Math.min(Rr, ar.right); B = Math.min(B, ar.bottom);
        if (!sc && /(auto|scroll)/.test(s.overflowX + ' ' + s.overflowY)) sc = a; } }
    return {w: Math.max(0, Rr - L), h: Math.max(0, B - T), cx: (L + Rr) / 2, cy: (T + B) / 2, sc}; };
  const offPage = e => { const r = e.getBoundingClientRect(); return (r.bottom + sy) <= 0 || (r.right + sx) <= 0 || (r.left + sx) >= VW; };
  const shown = e => boxVis(e) && !clipped(e) && !offPage(e);
  const isSvgSrc = s => /^data:image\/svg/i.test(s || '') || /\.svg(?:[?#]|$)/i.test(s || '');
"""

PROBE = "(cfg) => {" + HELPERS + r"""
  const failed = new Set((cfg && cfg.failed) || []);
  const de = document.documentElement, body = document.body;
  const all = [...body.querySelectorAll('*')].filter(e => !(e.closest('svg') && e.tagName.toLowerCase() !== 'svg'));
  const shownList = all.filter(shown);
  const shownSet = new Set(shownList);

  // overflow
  const scrollWidth = Math.max(de.scrollWidth, body.scrollWidth);
  const offAll = all.filter(boxVis).filter(e => CS(e).position !== 'fixed' && e.getBoundingClientRect().right + sx > VW + 1).slice(0, 400);
  const offInner = offAll.filter(e => !offAll.some(o => o !== e && e.contains(o))).slice(0, 8)
    .map(e => { const r = e.getBoundingClientRect(); return {sel: desc(e), right: Math.round(r.right + sx), w: Math.round(r.width)}; });
  const ovh = [de, body].some(e => { const s = CS(e); return s.overflowX === 'hidden' || s.overflowX === 'clip'; });

  // tap targets
  const TAP = 'a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=link],[role=tab],[role=menuitem]';
  const inlineInSentence = e => { if (e.tagName !== 'A' || CS(e).display !== 'inline') return false; const blk = e.closest('p,li,dd,td,blockquote,figcaption'); if (!blk) return false; return ((blk.textContent || '').trim().length - (e.textContent || '').trim().length) >= 20; };
  const ex = {hidden: 0, srOnly: 0, offscreen: 0, inline: 0};
  const taps = [];
  for (const e of body.querySelectorAll(TAP)) {
    if (!boxVis(e) || clipped(e)) { ex.hidden++; continue; }
    const r = e.getBoundingClientRect();
    if (r.width <= 1.5 || r.height <= 1.5) { ex.srOnly++; continue; }
    if (offPage(e)) { ex.offscreen++; continue; }
    if (inlineInSentence(e)) { ex.inline++; continue; }
    taps.push({sel: desc(e), w: rnd(r.width), h: rnd(r.height)});
  }

  // type
  const SKIP_TXT = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'TITLE', 'OPTION']);
  const CHROME = 'nav,header,footer,figcaption,caption,label,button,small,sup,sub,code,kbd,pre,samp,[role=navigation]';
  const texts = [];
  for (const e of shownList) {
    if (SKIP_TXT.has(e.tagName)) continue;
    let t = ''; for (const n of e.childNodes) if (n.nodeType === 3) t += n.textContent;
    t = t.trim(); if (!t) continue;
    const inChrome = !!e.closest(CHROME);
    const copy = !inChrome && (!!e.closest('p,li,dd,blockquote,td') || (['DIV', 'SPAN', 'ARTICLE', 'SECTION', 'MAIN'].includes(e.tagName) && !e.closest('a,button')));
    texts.push({sel: desc(e), px: rnd(parseFloat(CS(e).fontSize)), role: copy ? 'body' : 'chrome', text: t.slice(0, 40)});
  }

  // viewport meta
  const vm = document.querySelector('meta[name="viewport" i]');

  // sticky / fixed
  const sticky = shownList.filter(e => { const p = CS(e).position; return p === 'fixed' || p === 'sticky'; }).map(e => {
    const r = e.getBoundingClientRect();
    return {sel: desc(e), pos: CS(e).position, top: Math.round(r.top), h: rnd(r.height), w: rnd(r.width),
            inView: !(r.right <= 0 || r.left >= VW || r.bottom <= 0 || r.top >= H)}; }).slice(0, 20);

  // images
  const imgs = [...document.images].map(i => {
    const src = i.currentSrc || i.src || i.getAttribute('src') || '';
    const pic = i.closest('picture'); const ss = i.getAttribute('srcset') || '';
    const picSS = pic ? pic.querySelectorAll('source[srcset]').length : 0;
    return {sel: desc(i), src: src.slice(0, 160), svg: isSvgSrc(src) || isSvgSrc(i.getAttribute('src')), srcset: !!ss || picSS > 0,
            wdesc: /\d+w(\s|,|$)/.test(ss), sizes: i.hasAttribute('sizes') || (pic ? !!pic.querySelector('source[sizes]') : false),
            shown: shownSet.has(i), complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight,
            failed: failed.has(i.currentSrc) || failed.has(i.src), lazy: i.loading === 'lazy'}; });
  const inlineSvg = body.querySelectorAll('svg').length;

  // grey tiles (first rendered grey_tile check)
  const parseRGBA = s => { const m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return null; const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(parseFloat); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const PH = /(hero|photo|thumb|image|img|cover|media|picture|placeholder|banner|poster|avatar|gallery)/i;
  const SLOT = /(photo|thumb|image|img|cover|picture|placeholder|poster|avatar)/i;
  const PH_TXT = /(no image|image coming|placeholder|image unavailable|photo coming)/i;
  const imgLoaded = i => !failed.has(i.currentSrc) && !failed.has(i.src) && i.complete && (i.naturalWidth > 0 || isSvgSrc(i.currentSrc || i.src));
  const hasVisual = e => {
    for (const i of e.querySelectorAll('img')) if (imgLoaded(i)) return true;
    if (e.querySelector('svg,video,canvas,iframe,object,embed')) return true;
    return [e, ...e.querySelectorAll('*')].slice(0, 300).some(k => { const bi = CS(k).backgroundImage; return bi && bi !== 'none'; });
  };
  const greyFlags = []; let greyChecked = 0;
  for (const e of shownList) {
    const tag = e.tagName.toLowerCase(); if (tag === 'img' || tag === 'svg') continue;
    const name = cls(e) + ' ' + e.id; const isFig = tag === 'figure';
    if (!isFig && !PH.test(name)) continue;
    const r = e.getBoundingClientRect(); if (r.width < 40 || r.height < 40) continue;
    greyChecked++;
    if (hasVisual(e)) continue;
    const txt = (e.innerText || '').trim(); const s = CS(e); const c = parseRGBA(s.backgroundColor);
    const avg = c ? (c.r + c.g + c.b) / 3 : 0;
    const grey = !!c && c.a >= 0.5 && (Math.max(c.r, c.g, c.b) - Math.min(c.r, c.g, c.b)) <= 12 && avg >= 40 && avg <= 245;
    const base = {sel: desc(e), bg: s.backgroundColor, w: Math.round(r.width), h: Math.round(r.height), text: txt.slice(0, 40)};
    if (grey && (txt.length <= 40 || PH_TXT.test(txt))) greyFlags.push(Object.assign({kind: 'flat-grey-no-image'}, base));
    else if ((isFig || SLOT.test(name)) && txt.length === 0 && r.width >= 80 && r.height >= 80) greyFlags.push(Object.assign({kind: 'empty-photo-slot'}, base));
    else if (PH_TXT.test(txt) && txt.length <= 80) greyFlags.push(Object.assign({kind: 'placeholder-text'}, base));
  }
  const PH_SVC = /(placehold|placeholder\.|dummyimage|fakeimg|lorempixel|picsum\.photos)/i;
  const imgFlags = imgs.filter(i => i.shown).filter(i => i.failed || (i.complete && i.nw === 0 && !i.svg) || !i.complete || PH_SVC.test(i.src))
    .map(i => ({kind: i.failed ? 'img-http-error' : (!i.complete ? 'img-not-loaded-after-scroll' : (PH_SVC.test(i.src) ? 'img-placeholder-service' : 'img-naturalWidth-0')), sel: i.sel, src: i.src}));

  // nav + toggle
  const navEl = document.querySelector('nav,[role=navigation]');
  const toggleRe = /menu|nav|hamburger|toggle|drawer|offcanvas/i;
  const tcands = [...body.querySelectorAll('button,[role=button],[aria-expanded],[aria-controls]')].filter(shown).filter(e => {
    const lab = (e.getAttribute('aria-label') || '') + ' ' + cls(e) + ' ' + e.id + ' ' + (e.textContent || '').slice(0, 30);
    const ctl = e.getAttribute('aria-controls'); const tgt = ctl && document.getElementById(ctl);
    return toggleRe.test(lab) || (!!tgt && !!navEl && (tgt === navEl || tgt.contains(navEl) || navEl.contains(tgt))); });
  document.querySelectorAll('[data-mbench-toggle]').forEach(e => e.removeAttribute('data-mbench-toggle'));
  const tog = tcands[0] || null; if (tog) tog.setAttribute('data-mbench-toggle', '1');
  const navRoot = (tog && tog.getAttribute('aria-controls') && document.getElementById(tog.getAttribute('aria-controls'))) || navEl;
  const navLinks = navRoot ? [...navRoot.querySelectorAll('a[href]')] : [];
  const nav = {exists: !!navEl, navSel: navEl ? desc(navEl) : null, rootSel: navRoot ? desc(navRoot) : null,
               links: navLinks.length, linksShown: navLinks.filter(shown).length, toggleCandidates: tcands.length,
               toggle: tog ? {sel: desc(tog), label: tog.getAttribute('aria-label'), expanded: tog.getAttribute('aria-expanded'), controls: tog.getAttribute('aria-controls')} : null};

  // mobile vs desktop diff keys
  const CONTENT = 'p,h1,h2,h3,h4,h5,h6,img,figure,table,blockquote,li,dl,video,picture,form,input,textarea,select,iframe';
  const contentKeys = shownList.filter(e => e.matches(CONTENT) && !e.closest('nav,header,[role=navigation],[aria-hidden=true],dialog')).slice(0, 4000).map(path);

  // SOP-compatible fields (SAMPLE_DATA/_tools/mobile_capture.py)
  const ctas = [...document.querySelectorAll('a[href^="tel:"],a[href^="sms:"],a[href*="maps"]')].filter(boxVis).map(desc).slice(0, 10);
  return {innerWidth: W, innerHeight: H, clientWidth: de.clientWidth, visibleWidth: VW, scrollWidth, overflowX: scrollWidth > VW + 1,
          overflowOffenders: offInner, overflowXHiddenRoot: ovh,
          taps, tapExcluded: ex, texts, bodyFontPx: rnd(parseFloat(CS(body).fontSize)),
          viewportMeta: vm ? vm.getAttribute('content') : null, sticky, imgs, inlineSvg,
          pictureEls: document.querySelectorAll('picture').length, srcsetImgs: document.querySelectorAll('img[srcset]').length,
          mediaSources: [...document.querySelectorAll('picture source[media]')].map(s => s.media).slice(0, 10),
          telSmsMapLinks: ctas, grey: {checked: greyChecked, flags: greyFlags, imgFlags}, nav, contentKeys,
          visibleCount: all.filter(boxVis).length, shownCount: shownList.length};
}"""

DRAWER_PROBE = "() => {" + HELPERS + r"""
  const t = document.querySelector('[data-mbench-toggle]');
  const exp = t ? t.getAttribute('aria-expanded') : null;
  const ctl = t && t.getAttribute('aria-controls');
  const root = (ctl && document.getElementById(ctl)) || document.querySelector('nav,[role=navigation]');
  const links = root ? [...root.querySelectorAll('a[href]')] : [];
  const sh = links.filter(shown);
  const items = links.map(e => { const r = e.getBoundingClientRect(); const vb = visBox(e); let covered = null;
    if (boxVis(e) && vb.w > 0 && vb.h > 0) { const hit = document.elementFromPoint(vb.cx, vb.cy); if (!(hit && (hit === e || e.contains(hit)))) covered = hit ? desc(hit) : 'nothing'; }
    const sr = vb.sc ? vb.sc.getBoundingClientRect() : null;
    return {sel: desc(e), text: (e.textContent || '').trim().slice(0, 30), displayed: boxVis(e), w: rnd(r.width), h: rnd(r.height),
            visW: rnd(vb.w), visH: rnd(vb.h), covered, scroller: vb.sc ? desc(vb.sc) : null,
            scrollerW: sr ? rnd(Math.min(sr.width, VW)) : null, scrollerH: sr ? rnd(Math.min(sr.height, H)) : null}; });
  const rr = root ? root.getBoundingClientRect() : null;
  return {expanded: exp, rootSel: root ? desc(root) : null, rootBox: rr ? {top: rnd(rr.top), w: rnd(rr.width), h: rnd(rr.height), pos: CS(root).position, overflow: CS(root).overflowX + '/' + CS(root).overflowY} : null,
          links: links.length, linksShown: sh.length, items,
          taps: sh.map(e => { const r = e.getBoundingClientRect(); return {sel: desc(e), w: rnd(r.width), h: rnd(r.height)}; })};
}"""

SCROLL_JS = r"""async () => {
  const H = window.innerHeight; let y = 0;
  for (let i = 0; i < 60; i++) { y += Math.max(200, Math.round(H * 0.8)); window.scrollTo(0, y);
    await new Promise(r => setTimeout(r, 80)); if (y >= document.documentElement.scrollHeight) break; }
  window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 250));
  return document.documentElement.scrollHeight;
}"""


# ----------------------------------------------------------------------------- helpers
def parse_viewports(text: str) -> list[tuple[int, int]]:
    out = []
    for part in text.split(","):
        m = re.fullmatch(r"\s*(\d+)\s*[xX]\s*(\d+)\s*", part)
        if not m:
            raise SystemExit(f"bad viewport {part!r}; use WIDTHxHEIGHT")
        out.append((int(m.group(1)), int(m.group(2))))
    return out


def vp_name(vp) -> str:
    return f"{vp[0]}x{vp[1]}"


def is_mobile(vp) -> bool:
    return vp[0] <= MOBILE_MAX_W


def engine_floors(root: Path) -> dict:
    """Read TYPE_FLOOR_PX, BODY_FLOOR_PX, TAP_MIN_PX from lib/check.py (text only, no import)."""
    out = {"source": str(root / "lib" / "check.py")}
    try:
        txt = (root / "lib" / "check.py").read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        out["error"] = repr(exc)
        return out
    for name in ("TYPE_FLOOR_PX", "BODY_FLOOR_PX", "TAP_MIN_PX"):
        m = re.search(rf"^{name}\s*=\s*([0-9.]+)", txt, re.M)
        out[name] = float(m.group(1)) if m else None
    return out


def G(status, evidence, **nums):
    return {"status": status, "evidence": evidence, "nums": nums}


def not_run_gates(reason: str) -> dict:
    return {g: G("not-run", reason) for g in GATES}


def fmt_list(items, n=4):
    return ", ".join(items[:n]) + (f" (+{len(items) - n} more)" if len(items) > n else "")


# ----------------------------------------------------------------------------- gates
def gate_overflow(i, vp=None):
    sw, iw, cw = i["scrollWidth"], i["innerWidth"], i["clientWidth"]
    # 1px tolerance: Chrome rounds a scaled 980px layout viewport to 981px at some widths
    fail = sw > iw + 1 or sw > cw + 1
    ev = f"scrollWidth {sw}px vs innerWidth {iw}px and clientWidth {cw}px (1px rounding tolerance)"
    if vp and iw > vp[0] + 1:
        ev += (f"; innerWidth is wider than the {vp[0]}px viewport: "
               + ("no viewport meta, so the page lays out at a desktop width"
                  if i.get("viewportMeta") is None else "Chrome widened the layout viewport to fit overflowing content"))
    if i["overflowOffenders"]:
        ev += "; past the right edge: " + fmt_list([f"{o['sel']} (right {o['right']}px, w {o['w']}px)" for o in i["overflowOffenders"]])
    if i["overflowXHiddenRoot"]:
        ev += "; note: html/body has overflow-x hidden/clip, so overflow can be masked"
    return G("fail" if fail else "pass", ev, scrollWidth=sw, innerWidth=iw, clientWidth=cw,
             offenders=len(i["overflowOffenders"]))


DESKTOP_TAP_FLOOR = 24.0  # WCAG 2.5.8 (AA) pointer target; 44px is the touch rule (engine TAP_MIN_PX)


def gate_tap(i, floors, static_row, vp=None):
    touch = floors.get("TAP_MIN_PX") or 44.0
    desktop = vp is not None and not is_mobile(vp)
    floor = DESKTOP_TAP_FLOOR if desktop else touch
    eps = floor - 0.05
    taps = i["taps"]
    nt = i.get("nav_test") or {}
    dt = nt.get("drawer_taps") or []
    small = [t for t in taps if t["w"] < eps or t["h"] < eps]
    dsmall = [t for t in dt if t["w"] < eps or t["h"] < eps]
    both = taps + dt
    sm = min(both, key=lambda t: min(t["w"], t["h"])) if both else None
    ev = f"{len(taps)} visible controls measured, {len(small)} under {floor:g}px"
    if sm:
        ev += f"; smallest {sm['w']}x{sm['h']}px ({sm['sel']})"
    ev += (f"; menu opened: {len(dt)} drawer links measured, {len(dsmall)} under {floor:g}px" if nt.get("clicked")
           else "; no drawer opened")
    ex = i["tapExcluded"]
    ev += (f"; excluded: {ex['hidden']} hidden, {ex['srOnly']} sr-only, {ex['offscreen']} off-screen, "
           f"{ex['inline']} inline-in-sentence links (WCAG 2.5.8)")
    if small or dsmall:
        ev += "; under floor: " + fmt_list([f"{t['sel']} {t['w']}x{t['h']}px" for t in small + dsmall], 5)
    if desktop:
        u44 = [t for t in both if t["w"] < touch - 0.05 or t["h"] < touch - 0.05]
        ev = (f"desktop pointer floor {floor:g}px (WCAG 2.5.8 AA; --desktop-tap-floor to change); info: {len(u44)} under the "
              f"{touch:g}px touch floor" + (f" ({fmt_list([t['sel'] + ' ' + str(t['w']) + 'x' + str(t['h']) + 'px' for t in u44], 3)})" if u44 else "")
              + "; " + ev)
    if static_row:
        ev += f"; static engine row: [{static_row['status']}] {static_row['detail'][:80]}"
    return G("fail" if (small or dsmall) else "pass", ev, measured=len(taps), under=len(small),
             drawer_measured=len(dt), drawer_under=len(dsmall),
             smallest=round(min(sm["w"], sm["h"]), 1) if sm else None)


def gate_type(i, floors):
    tf, bf = floors.get("TYPE_FLOOR_PX"), floors.get("BODY_FLOOR_PX")
    if tf is None or bf is None:
        return G("not-run", f"engine floors not readable from {floors.get('source')}: {floors.get('error', 'constants missing')}")
    texts = i["texts"]
    bad = [t for t in texts if t["px"] < (bf if t["role"] == "body" else tf) - 0.005]
    body_px = i["bodyFontPx"]
    body_bad = body_px < tf - 0.005
    smallest = min((t["px"] for t in texts), default=None)
    body_min = min((t["px"] for t in texts if t["role"] == "body"), default=None)
    ev = (f"body element {body_px:g}px (floor {tf:g}px); {len(texts)} visible text elements, smallest "
          f"{smallest if smallest is not None else 'n/a'}px; body copy smallest {body_min if body_min is not None else 'n/a'}px "
          f"(floor {bf:g}px); {len(bad)} under floor (engine lib/check.py TYPE_FLOOR_PX={tf:g}, BODY_FLOOR_PX={bf:g})")
    if bad:
        ev += "; e.g. " + fmt_list([f"{t['sel']} {t['px']}px {t['role']} '{t['text'][:24]}'" for t in bad], 3)
    return G("fail" if (bad or body_bad) else "pass", ev, body_px=body_px, smallest=smallest, body_min=body_min,
             under=len(bad), texts=len(texts))


def gate_viewport(i):
    c = i["viewportMeta"]
    if c is None:
        return G("fail", "no <meta name=\"viewport\"> in the rendered DOM", present=False)
    ok = bool(re.search(r"width\s*=\s*device-width", c, re.I))
    ev = f"content=\"{c}\""
    if re.search(r"user-scalable\s*=\s*(no|0)", c, re.I) or re.search(r"maximum-scale\s*=\s*1(\.0*)?\b", c, re.I):
        ev += "; note: zoom is blocked (WCAG 1.4.4 risk)"
    return G("pass" if ok else "fail", ev + ("" if ok else "; width=device-width missing"), present=True, device_width=ok)


def link_usable(it, floor):
    """Return (state, why). state: usable | scroll | unusable."""
    if not it["displayed"]:
        return "unusable", "not displayed"
    if it["scroller"] and (it["scrollerH"] or 0) >= floor - 0.05 and (it["scrollerW"] or 0) >= floor - 0.05:
        if it["visW"] > 0 and it["visH"] > 0 and it["visW"] >= min(floor, it["w"]) - 0.5 and it["visH"] >= min(floor, it["h"]) - 0.5 and it["covered"]:
            return "unusable", f"covered by {it['covered']}"
        return ("usable" if it["visH"] >= min(floor, it["h"]) - 0.5 and it["visW"] >= min(floor, it["w"]) - 0.5 else "scroll"), ""
    if it["visW"] < min(floor, it["w"]) - 0.5 or it["visH"] < min(floor, it["h"]) - 0.5:
        sc = f" by scroller {it['scroller']} {it['scrollerW']}x{it['scrollerH']}px" if it["scroller"] else ""
        return "unusable", f"visible box {it['visW']}x{it['visH']}px of {it['w']}x{it['h']}px{sc}"
    if it["covered"]:
        return "unusable", f"covered by {it['covered']}"
    return "usable", ""


def gate_nav(i, floors=None):
    nav = i["nav"]
    nt = i.get("nav_test") or {}
    tog = nav.get("toggle")
    if not nav["exists"] and not tog:
        return G("pass", "no <nav>/[role=navigation] and no menu toggle on the page: nothing to open", nav=False)
    total, shown_before = nav["links"], nav["linksShown"]
    if not tog:
        if total and shown_before == total:
            return G("pass", f"inline nav {nav['navSel']}: {shown_before}/{total} links visible without a toggle", nav=True,
                     links=total, shown=shown_before, toggle=False)
        return G("fail", f"nav {nav['navSel']} shows {shown_before}/{total} links and no visible menu toggle was found",
                 nav=True, links=total, shown=shown_before, toggle=False)
    if not nt.get("clicked"):
        return G("fail", f"toggle {tog['sel']} found but clicking it failed: {nt.get('error', 'unknown')}", nav=True,
                 toggle=True, clicked=False)
    before, after, closed = nt.get("expanded_before"), nt.get("expanded_after"), nt.get("expanded_after_close")
    sa = nt.get("links_shown_after")
    floor = (floors or {}).get("TAP_MIN_PX") or 44.0
    flipped = before == "false" and after == "true"
    opened = (sa or 0) > shown_before or (total > 0 and shown_before == total)
    states = [(it, *link_usable(it, floor)) for it in nt.get("items") or []]
    bad = [(it, why) for it, st, why in states if st == "unusable"]
    n_use = sum(1 for _, st, _ in states if st == "usable")
    n_scr = sum(1 for _, st, _ in states if st == "scroll")
    rb = nt.get("root_box") or {}
    ev = (f"toggle {tog['sel']} (aria-controls={tog.get('controls')}): aria-expanded {before} -> {after} after tap"
          f" -> {closed} after second tap; nav links visible {shown_before}/{total} before, {sa}/{nt.get('links')} after; "
          f"opened menu {nt.get('root')} is {rb.get('pos')} {rb.get('w')}x{rb.get('h')}px overflow {rb.get('overflow')}; "
          f"links usable {n_use}, reachable by scrolling a >= {floor:g}px scroller {n_scr}, unusable {len(bad)}")
    reasons = []
    if not flipped:
        reasons.append("aria-expanded did not flip false -> true")
    if not opened:
        reasons.append("no nav links became visible")
    if bad:
        reasons.append(f"{len(bad)} of {len(states)} menu links unusable after opening: "
                       + fmt_list([f"'{it['text']}' {why}" for it, why in bad], 3))
    if reasons:
        ev += "; FAIL: " + "; ".join(reasons)
    return G("fail" if reasons else "pass", ev, nav=nav["exists"], toggle=True, before=before, after=after,
             closed=closed, shown_before=shown_before, shown_after=sa, usable=n_use, scroll=n_scr, unusable=len(bad))


def gate_sticky(i):
    H = i["innerHeight"]
    items = [s for s in i["sticky"] if s["inView"]]
    big = [s for s in items if s["h"] > STICKY_MAX * H + 0.05]
    tallest = max(items, key=lambda s: s["h"]) if items else None
    ev = f"{len(items)} fixed/sticky element(s) in view"
    if tallest:
        ev += f"; tallest {tallest['sel']} {tallest['pos']} {tallest['h']}px = {100 * tallest['h'] / H:.1f}% of {H}px (limit 25%)"
    if big:
        ev += "; over limit: " + fmt_list([f"{s['sel']} {s['h']}px" for s in big])
    return G("fail" if big else "pass", ev, count=len(items), over=len(big),
             tallest_pct=round(100 * tallest["h"] / H, 1) if tallest else 0)


def gate_img(i):
    imgs = i["imgs"]
    svg = [m for m in imgs if m["svg"]]
    raster = [m for m in imgs if not m["svg"]]
    with_ss = [m for m in raster if m["srcset"]]
    missing = [m for m in raster if not m["srcset"]]
    no_sizes = [m for m in raster if m["srcset"] and m["wdesc"] and not m["sizes"]]
    ev = (f"{len(imgs)} img ({len(raster)} raster, {len(svg)} svg); raster with srcset {len(with_ss)}, without {len(missing)}; "
          f"w-descriptor srcset without sizes {len(no_sizes)}; picture elements {i['pictureEls']}; inline svg {i['inlineSvg']} "
          "(CSS background images not counted)")
    if missing or no_sizes:
        ev += "; offenders: " + fmt_list([f"{m['sel']} {m['src'][-40:]}" for m in missing + no_sizes])
    return G("fail" if (missing or no_sizes) else "pass", ev, imgs=len(imgs), raster=len(raster), svg=len(svg),
             srcset=len(with_ss), missing=len(missing), no_sizes=len(no_sizes), inline_svg=i["inlineSvg"])


def gate_grey(i):
    g = i["grey"]
    flags, imf = g["flags"], g["imgFlags"]
    shown_imgs = sum(1 for m in i["imgs"] if m["shown"])
    ev = (f"first rendered grey_tile check: {g['checked']} photo-ish slot(s) checked, {len(flags)} flagged; "
          f"{shown_imgs} visible img checked, {len(imf)} broken/unloaded/placeholder")
    if flags:
        ev += "; slots: " + fmt_list([f"{f['kind']} {f['sel']} {f['w']}x{f['h']} bg {f['bg']}" for f in flags], 3)
    if imf:
        ev += "; imgs: " + fmt_list([f"{f['kind']} {f['sel']} {f['src'][-40:]}" for f in imf], 3)
    return G("fail" if (flags or imf) else "pass", ev, checked=g["checked"], flagged=len(flags), imgs=shown_imgs,
             img_flagged=len(imf))


def judge(info, floors, static_tap, vp=None):
    if not info or "error" in info:
        return not_run_gates("capture error: " + (info or {}).get("error", "no data"))
    out = {}
    for name, fn in (("overflow_x", lambda: gate_overflow(info, vp)), ("tap_target_rendered", lambda: gate_tap(info, floors, static_tap, vp)),
                     ("type_floor_rendered", lambda: gate_type(info, floors)), ("viewport_meta", lambda: gate_viewport(info)),
                     ("nav_toggle", lambda: gate_nav(info, floors)), ("sticky_25", lambda: gate_sticky(info)),
                     ("img_srcset", lambda: gate_img(info)), ("grey_tile_rendered", lambda: gate_grey(info))):
        try:
            out[name] = fn()
        except Exception as exc:  # a gate bug must never read as pass
            out[name] = G("not-run", f"gate error {exc.__class__.__name__}: {exc}")
    out["mobile_desktop_diff"] = G("not-run", "computed after all viewports")
    return out


def add_diff(results: dict, vps: list) -> None:
    desk = max((v for v in vps if not is_mobile(v)), default=None, key=lambda v: v[0])
    for page, per in results.items():
        dinfo = per.get(vp_name(desk), {}).get("info") if desk else None
        for vp in vps:
            r = per.get(vp_name(vp))
            if not r:
                continue
            info = r.get("info") or {}
            if "error" in info or "contentKeys" not in info:
                r["gates"]["mobile_desktop_diff"] = G("not-run", "no capture for this viewport")
                continue
            if desk is None or not dinfo or "contentKeys" not in dinfo:
                r["gates"]["mobile_desktop_diff"] = G("not-run", "no desktop viewport captured to compare against")
                continue
            if vp == desk:
                r["gates"]["mobile_desktop_diff"] = G("info", f"desktop baseline: {info['shownCount']} visible elements, "
                                                              f"{len(info['contentKeys'])} content elements", visible=info["shownCount"])
                continue
            mk, dk = set(info["contentKeys"]), set(dinfo["contentKeys"])
            hidden, extra = sorted(dk - mk), sorted(mk - dk)
            ev = (f"visible elements {info['shownCount']} here vs {dinfo['shownCount']} at {vp_name(desk)}; content visible on desktop "
                  f"but hidden here: {len(hidden)}" + (f" ({fmt_list(hidden, 3)})" if hidden else "") +
                  f"; content only visible here: {len(extra)} (nav/header excluded; informational)")
            r["gates"]["mobile_desktop_diff"] = G("info", ev, visible=info["shownCount"], desktop_visible=dinfo["shownCount"],
                                                  hidden_on_mobile=len(hidden), mobile_only=len(extra))


# ----------------------------------------------------------------------------- capture
def profile_opts(p, vp):
    w, h = vp
    if is_mobile(vp):
        dev = "iPhone 14" if w == 390 else "Pixel 7"
        o = dict(p.devices[dev])
        o.pop("default_browser_type", None)
        o["viewport"] = {"width": w, "height": h}
        o["screen"] = {"width": w, "height": h}
        return dev, o
    return "desktop", {"viewport": {"width": w, "height": h}, "device_scale_factor": 1}


def launch_browser(p):
    errs = []
    for kw, label in (({"channel": "chrome"}, "Chrome (channel=chrome)"), ({}, "Playwright bundled chromium")):
        try:
            return p.chromium.launch(headless=True, **kw), label, errs
        except Exception as exc:
            errs.append(f"{label}: {exc.__class__.__name__}: {(str(exc).splitlines() or [''])[0][:200]}")
    return None, None, errs


def capture_one(browser, p, url, vp, nav_ms, save_dir: Path | None):
    dev, opts = profile_opts(p, vp)
    ctx = browser.new_context(**opts)
    page = ctx.new_page()
    failed: list[str] = []

    def on_resp(r):
        try:
            if r.request.resource_type == "image" and r.status >= 400:
                failed.append(r.url)
        except Exception:
            pass

    page.on("response", on_resp)
    page.on("requestfailed", lambda rq: failed.append(rq.url) if rq.resource_type == "image" else None)
    info: dict
    try:
        page.goto(url, wait_until="load", timeout=nav_ms)
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        page.evaluate(SCROLL_JS)
        try:
            page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(300)
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
            (save_dir / "dom.html").write_text(page.content(), encoding="utf-8")
            try:
                (save_dir / "aria.yml").write_text(page.locator("body").aria_snapshot(), encoding="utf-8")
            except Exception as exc:
                (save_dir / "aria.yml").write_text(f"# aria_snapshot failed: {exc!r}\n", encoding="utf-8")
            page.screenshot(path=str(save_dir / "shot.png"))
        info = page.evaluate(PROBE, {"failed": failed})
        info["device"] = dev
        tog = (info.get("nav") or {}).get("toggle")
        if tog:
            nt = {"clicked": False, "expanded_before": tog.get("expanded")}
            loc = page.locator("[data-mbench-toggle]").first
            try:
                loc.click(timeout=3000)
                page.wait_for_timeout(700)
                after = page.evaluate(DRAWER_PROBE)
                nt.update(clicked=True, expanded_after=after["expanded"], links=after["links"],
                          links_shown_after=after["linksShown"], drawer_taps=after["taps"], root=after["rootSel"],
                          root_box=after["rootBox"], items=after["items"])
                if save_dir:
                    page.screenshot(path=str(save_dir / "drawer.png"))
                    try:
                        (save_dir / "aria_drawer.yml").write_text(page.locator("body").aria_snapshot(), encoding="utf-8")
                    except Exception:
                        pass
                try:
                    loc.click(timeout=3000)
                    page.wait_for_timeout(500)
                    nt["expanded_after_close"] = page.evaluate(DRAWER_PROBE)["expanded"]
                except Exception as exc:
                    nt["expanded_after_close"] = f"second tap failed: {exc.__class__.__name__}"
            except Exception as exc:
                nt["error"] = f"{exc.__class__.__name__}: {(str(exc).splitlines() or [''])[0][:200]}"
            info["nav_test"] = nt
        info["failedImageUrls"] = sorted(set(failed))
    except Exception as exc:
        info = {"error": f"{exc.__class__.__name__}: {(str(exc).splitlines() or [''])[0][:300]}"}
    finally:
        try:
            ctx.close()
        except Exception:
            pass
    return info


def capture_all(pages, vps, floors, nav_ms, save_root: Path | None, static_tap=None):
    """pages: list of (name, url). Returns (results, meta). Never raises; missing tools => not-run."""
    meta = {"browser": None, "error": None, "seconds": 0.0}
    results = {name: {} for name, _ in pages}
    t0 = time.perf_counter()
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        meta["error"] = f"playwright not importable ({exc.__class__.__name__}: {exc})"
    if meta["error"] is None:
        try:
            with sync_playwright() as p:
                browser, label, errs = launch_browser(p)
                if browser is None:
                    meta["error"] = "no browser launched: " + " | ".join(errs)
                else:
                    meta["browser"] = f"{label} {browser.version}"
                    for name, url in pages:
                        for vp in vps:
                            sd = (save_root / name / vp_name(vp)) if save_root else None
                            info = capture_one(browser, p, url, vp, nav_ms, sd)
                            gates = judge(info, floors, static_tap, vp)
                            results[name][vp_name(vp)] = {"url": url, "info": info, "gates": gates}
                            if sd:
                                sd.mkdir(parents=True, exist_ok=True)
                                (sd / "patterns.json").write_text(json.dumps({"url": url, "viewport": vp_name(vp), "info": info,
                                                                              "gates": gates}, indent=1), encoding="utf-8")
                    browser.close()
        except Exception as exc:
            meta["error"] = f"playwright run failed ({exc.__class__.__name__}: {(str(exc).splitlines() or [''])[0][:300]})"
    if meta["error"]:
        for name, url in pages:
            for vp in vps:
                results[name].setdefault(vp_name(vp), {"url": url, "info": {"error": meta["error"]},
                                                       "gates": not_run_gates(meta["error"])})
    add_diff(results, vps)
    if save_root:
        for name, per in results.items():
            d = save_root / name
            d.mkdir(parents=True, exist_ok=True)
            (d / "patterns.json").write_text(json.dumps({"url": next(iter(per.values()))["url"] if per else None,
                                                         "profiles": {k: {"gates": v["gates"]} for k, v in per.items()}},
                                                        indent=1), encoding="utf-8")
    meta["seconds"] = round(time.perf_counter() - t0, 3)
    return results, meta


def signature(results) -> dict:
    return {f"{page}|{vp}|{g}": [r["gates"][g]["status"], r["gates"][g].get("nums", {})]
            for page, per in results.items() for vp, r in per.items() for g in GATES}


def compare_signatures(a, b) -> dict:
    diffs = [k for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
    nr = [k for k, v in a.items() if v[0] == "not-run"]
    if not a:
        return {"status": "not-run", "note": "no capture results"}
    if len(nr) == len(a):
        return {"status": "not-run", "note": "every gate was not-run in run 1; nothing to compare"}
    if diffs:
        return {"status": "fail", "note": f"{len(diffs)} of {len(a)} gate results differ between capture runs",
                "diffs": [{"key": k, "run1": a.get(k), "run2": b.get(k)} for k in diffs[:20]]}
    return {"status": "pass", "note": f"{len(a)} gate results (verdict + numbers) identical across two capture runs"
                                      " (fresh browser each run; screenshots not compared)"}


# ----------------------------------------------------------------------------- engine check rows
ROW_RE = re.compile(r"^\s*\[(pass|fail|warn|skip)\]\s+(\S+)(?:\s+-\s+(.*))?\s*$")


def parse_check_rows(stdout: str) -> list[dict]:
    rows = []
    for line in (stdout or "").splitlines():
        m = ROW_RE.match(line)
        if m:
            rows.append({"row": m.group(2), "status": m.group(1), "detail": (m.group(3) or "").strip()})
    return rows


# ----------------------------------------------------------------------------- readiness
LABEL = {"pass": "VERIFIED pass", "fail": "VERIFIED fail", "not-run": "not-run", "info": "info (not a gate)",
         "warn": "warn (not verified)", "covered": "VERIFIED pass (rendered)"}


def readiness_items(steps, rows, results, crepro, capture_on):
    items = []
    for s in steps:
        st = {"PASS": "pass", "FAIL": "fail"}.get(s["status"], "not-run")
        items.append({"section": "cold start", "gate": s["step"], "viewport": "-", "status": st,
                      "evidence": (s.get("note") or s.get("command") or "")[:300]})
    rendered_grey = [r["gates"]["grey_tile_rendered"]["status"] for per in results.values() for r in per.values()]
    grey_ok = bool(rendered_grey) and all(x == "pass" for x in rendered_grey)
    if not rows:
        items.append({"section": "engine check", "gate": "check rows", "viewport": "-", "status": "not-run",
                      "evidence": "no engine check rows parsed (check step did not run or printed none)"})
    for r in rows:
        st = {"pass": "pass", "fail": "fail", "warn": "warn", "skip": "not-run"}[r["status"]]
        ev = r["detail"][:300]
        if r["row"] == "grey_tile" and st == "not-run":
            if grey_ok:
                st = "covered"
                ev = "static row not-run by design; covered by grey_tile_rendered = pass on every page at every viewport below. Static: " + ev
            else:
                ev = "static row not-run; rendered grey_tile_rendered did not pass everywhere (see below). Static: " + ev
        items.append({"section": "engine check", "gate": r["row"], "viewport": "static", "status": st, "evidence": ev})
    for page, per in results.items():
        for vp, r in per.items():
            for g in GATES:
                x = r["gates"][g]
                items.append({"section": f"mobile {page}", "gate": g, "viewport": vp, "status": x["status"], "evidence": x["evidence"]})
    if not results:
        items.append({"section": "mobile", "gate": "all mobile gates", "viewport": "-", "status": "not-run",
                      "evidence": "capture disabled (--no-capture)" if not capture_on else "no pages captured"})
    if crepro:
        items.append({"section": "repro", "gate": "capture repro", "viewport": "all", "status": crepro["status"], "evidence": crepro["note"]})
    return items


def verdict(items):
    gate_items = [i for i in items if i["status"] != "info"]
    fails = [i for i in gate_items if i["status"] == "fail"]
    nr = [i for i in gate_items if i["status"] not in ("pass", "covered", "fail")]
    ready = not fails and not nr and bool(gate_items)
    return ("READY" if ready else "NOT READY"), fails, nr


def write_ready(od: Path, project: str, stamp: str, items, meta_lines, engine_desc) -> tuple[Path, Path, str]:
    v, fails, nr = verdict(items)
    pname = Path(project).name
    md = [f"# READY_MOBILE {pname} {stamp}", "",
          f"Build under test: `python spidercaster.py build {project} --offline --out <temp>` ({engine_desc}).",
          "READY means: every gate below ran and passed (info rows are not gates). It never means deployed or published.", ""]
    md += meta_lines + ["", f"## Verdict: **{v}**", ""]
    if fails:
        md.append(f"- {len(fails)} gate(s) VERIFIED fail: " + fmt_list([f"{i['gate']}@{i['viewport']}" for i in fails], 10))
    if nr:
        md.append(f"- {len(nr)} gate(s) not-run or not verified: " + fmt_list([f"{i['gate']}@{i['viewport']} ({i['status']})" for i in nr], 10))
    if not fails and not nr:
        md.append("- every gate ran and passed")
    sections = []
    for i in items:
        if i["section"] not in sections:
            sections.append(i["section"])
    for sec in sections:
        md += ["", f"## {sec}", "", "| Gate | Viewport | Result | Evidence |", "|---|---|---|---|"]
        for i in items:
            if i["section"] == sec:
                ev = i["evidence"].replace("|", "\\|").replace("\n", " ")
                md.append(f"| {i['gate']} | {i['viewport']} | {LABEL.get(i['status'], i['status'])} | {ev} |")
    mdp = od / f"READY_MOBILE_{pname}_{stamp}.md"
    mdp.write_text("\n".join(md) + "\n", encoding="utf-8")
    jp = od / f"READY_MOBILE_{pname}_{stamp}.json"
    jp.write_text(json.dumps({"project": project, "stamp": stamp, "verdict": v, "engine": engine_desc,
                              "fails": len(fails), "not_run": len(nr), "items": items}, indent=1), encoding="utf-8")
    return mdp, jp, v


# ----------------------------------------------------------------------------- main
def list_pages(site: Path, cap: int) -> list[str]:
    pages = sorted(p.relative_to(site).as_posix() for p in site.rglob("*.html"))
    pages.sort(key=lambda r: (r != "index.html", r))
    return pages[:cap] if cap and cap > 0 else pages


def start_server(co: Path, site: str, env: dict):
    port = cs.free_port()
    proc = subprocess.Popen([sys.executable, "spidercaster.py", "serve", site, "--port", str(port)], cwd=co, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    deadline = time.time() + 20
    while time.time() < deadline:
        if proc.poll() is not None:
            return proc, port, f"serve exited early with code {proc.returncode}"
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3) as r:
                if r.status == 200:
                    return proc, port, ""
        except Exception:
            time.sleep(0.25)
    return proc, port, "serve did not answer GET / within 20s"


def stop_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default="projects/demo-local")
    ap.add_argument("--viewports", default=DEFAULT_VIEWPORTS)
    ap.add_argument("--pages", type=int, default=20, help="cap on built pages captured (0 = all)")
    ap.add_argument("--keep", action="store_true", help="keep the temp checkout and captures")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--timeout", type=int, default=180, help="per-step timeout seconds (page navigation uses min(timeout,45))")
    ap.add_argument("--no-capture", action="store_true", help="cold start only; mobile gates report not-run")
    ap.add_argument("--source", choices=["worktree", "head"], default="worktree")
    ap.add_argument("--skip-shipcheck", action="store_true")
    ap.add_argument("--results", default=str(HERE / "results"))
    ap.add_argument("--desktop-tap-floor", type=float, default=24.0,
                    help="tap floor for viewports wider than 480px (default 24 = WCAG 2.5.8 AA; 44 = touch rule)")
    args = ap.parse_args()
    globals()["DESKTOP_TAP_FLOOR"] = args.desktop_tap_floor

    vps = parse_viewports(args.viewports)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    pname = Path(args.project).name
    od = Path(args.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    results_dir = Path(args.results)
    results_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="sc-mobile-"))
    co = tmp / "checkout"
    site = "sites/bench-out"
    steps: list[dict] = []
    timings: dict = {}
    results: dict = {}
    crepro = None
    cmeta1 = cmeta2 = None
    pages: list[str] = []
    rows: list[dict] = []
    floors: dict = {}
    t_all = time.perf_counter()
    sde = os.environ.get("SOURCE_DATE_EPOCH")
    try:
        t0 = time.perf_counter()
        (cs.snapshot_head if args.source == "head" else cs.snapshot_worktree)(co)
        nfiles = sum(1 for p in co.rglob("*") if p.is_file())
        steps.append({"step": "checkout", "status": "PASS", "seconds": round(time.perf_counter() - t0, 3),
                      "command": f"snapshot {args.source}", "exit_code": 0, "note": f"{nfiles} files into temp checkout",
                      "stdout": "", "stderr": ""})
        floors = engine_floors(co)
        build_argv = ["spidercaster.py", "build", args.project, "--offline", "--out", site]
        s1 = cs.run("build", build_argv, co, cs.make_env("1"), args.timeout)
        steps.append(s1)
        snap1 = tmp / "build1"
        if (co / site).exists():
            shutil.copytree(co / site, snap1)
            shutil.rmtree(co / site)
        time.sleep(1.2)
        s2 = cs.run("build#2", build_argv, co, cs.make_env("2"), args.timeout)
        steps.append(s2)
        snap2 = tmp / "build2"
        if (co / site).exists():
            shutil.copytree(co / site, snap2)
        t0 = time.perf_counter()
        if not snap1.exists() or not snap2.exists():
            rep = {"status": "FAIL", "note": "a build produced no output dir, cannot compare", "diff": ""}
        else:
            h1, h2 = cs.tree_hashes(snap1), cs.tree_hashes(snap2)
            changed = sorted(r for r in set(h1) & set(h2) if h1[r] != h2[r])
            only = sorted(set(h1) ^ set(h2))
            if changed or only:
                rep = {"status": "FAIL", "note": f"differing={changed}; only-in-one={only}",
                       "diff": "\n\n".join(cs.diff_summary(snap1, snap2, changed))}
            else:
                rep = {"status": "PASS", "note": f"{len(h1)} files identical (SHA-256), PYTHONHASHSEED 1 vs 2, "
                                                 f"SOURCE_DATE_EPOCH {'=' + sde if sde else 'unset'} in both", "diff": ""}
        steps.append({"step": "repro", "status": rep["status"], "seconds": round(time.perf_counter() - t0, 3),
                      "command": "sha256 of every file in build #1 vs build #2", "exit_code": None, "note": rep["note"],
                      "stdout": rep["diff"], "stderr": ""})
        if (co / site).exists():
            chk = cs.run("check", ["spidercaster.py", "check", site, "--expect-noindex"], co, cs.make_env(), args.timeout)
            steps.append(chk)
            rows = parse_check_rows(chk["stdout"])
            res_line = next((l.strip() for l in chk["stdout"].splitlines() if l.strip().startswith("result:")), "")
            chk["note"] = chk["note"] or res_line
            steps.append(cs.step_serve(co, cs.make_env(), site, args.timeout))
        else:
            for n in ("check", "serve"):
                steps.append({"step": n, "status": "SKIP", "seconds": 0, "command": "", "exit_code": None,
                              "note": "no built site (build failed)", "stdout": "", "stderr": ""})
        steps.append(cs.run("doctor", ["spidercaster.py", "doctor"], co, cs.make_env(), args.timeout))
        steps.append(cs.run("crew selftest", ["spidercaster.py", "crew", "selftest"], co, cs.make_env(), args.timeout,
                            expect_in_stdout="crew selftest ok"))
        if not args.skip_shipcheck:
            steps.append(cs.run("shipcheck", ["spidercaster.py", "shipcheck"], co, cs.make_env(), max(args.timeout, 600)))
        timings["cold_start"] = round(time.perf_counter() - t_all, 3)

        static_tap = next((r for r in rows if r["row"] == "tap_target"), None)
        if args.no_capture:
            pass
        elif not (co / site).exists():
            pass
        else:
            pages = list_pages(co / site, args.pages)
            proc, port, err = start_server(co, site, cs.make_env())
            try:
                if err:
                    reason = f"local serve for capture failed: {err}"
                    results = {pg: {vp_name(v): {"url": None, "info": {"error": reason}, "gates": not_run_gates(reason)} for v in vps} for pg in pages}
                else:
                    urls = [(pg.replace("/", "__"), f"http://127.0.0.1:{port}/" + urllib.parse.quote(pg)) for pg in pages]
                    nav_ms = min(args.timeout, 45) * 1000
                    results, cmeta1 = capture_all(urls, vps, floors, nav_ms, tmp / "capture1", static_tap)
                    timings["capture_run1"] = cmeta1["seconds"]
                    results2, cmeta2 = capture_all(urls, vps, floors, nav_ms, tmp / "capture2", static_tap)
                    timings["capture_run2"] = cmeta2["seconds"]
                    crepro = compare_signatures(signature(results), signature(results2))
            finally:
                stop_server(proc)
        if (tmp / "capture1").exists():
            dest = od / f"MOBILE_CAPTURE_{pname}_{stamp}"
            shutil.copytree(tmp / "capture1", dest)
    finally:
        timings["total"] = round(time.perf_counter() - t_all, 3)
        if not args.keep:
            shutil.rmtree(tmp, ignore_errors=True)

    git_head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--short"], capture_output=True, text=True).stdout.splitlines()
    engine_desc = f"engine git {git_head}, {len(dirty)} uncommitted paths, source={args.source}"
    if args.no_capture:
        crepro = {"status": "not-run", "note": "--no-capture given"}
    items = readiness_items(steps, rows, results, crepro, not args.no_capture)
    browser = (cmeta1 or {}).get("browser") or (cmeta1 or {}).get("error") or ("capture disabled" if args.no_capture else "not started")
    meta_lines = [f"- When: {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}",
                  f"- Python {sys.version.split()[0]}; browser: {browser}",
                  f"- Viewports: {', '.join(vp_name(v) for v in vps)} (mobile <= {MOBILE_MAX_W}px wide use Pixel 7 / iPhone 14 emulation; wider = desktop)",
                  f"- Pages captured: {len(pages)} ({', '.join(pages[:10]) or 'none'})",
                  f"- Engine floors (lib/check.py): TYPE_FLOOR_PX={floors.get('TYPE_FLOOR_PX')}, BODY_FLOOR_PX={floors.get('BODY_FLOOR_PX')}, TAP_MIN_PX={floors.get('TAP_MIN_PX')}",
                  f"- Timings (s): " + ", ".join(f"{k} {v}" for k, v in timings.items())]
    rmd, rjs, v = write_ready(od, args.project, stamp, items, meta_lines, engine_desc)

    # MOBILE_RUN report
    run = [f"# MOBILE_RUN {stamp} - {pname}", "", *meta_lines, f"- {engine_desc}",
           "- Stripped env (names only): " + ", ".join(cs.STRIP_ENV), f"- Readiness: **{v}** -> `{rmd.name}`", "",
           "## Cold start", "", "| Step | Command | Exit | Seconds | Result | Note |", "|---|---|---|---|---|---|"]
    for s in steps:
        note = (s.get("note") or "").replace("|", "\\|").replace("\n", " ")[:220]
        run.append(f"| {s['step']} | `{s['command']}` | {s['exit_code']} | {s['seconds']} | {s['status']} | {note} |")
    run += ["", "## Engine check rows (static)", "", "| Row | Result | Detail |", "|---|---|---|"]
    for r in rows:
        run.append(f"| {r['row']} | {r['status']} | {r['detail'].replace('|', '/')[:200]} |")
    for vp in vps:
        run += ["", f"## Viewport {vp_name(vp)} ({'mobile' if is_mobile(vp) else 'desktop baseline'})", "",
                "| Page | Gate | Result | Evidence |", "|---|---|---|---|"]
        for page, per in results.items():
            r = per.get(vp_name(vp))
            if not r:
                continue
            for g in GATES:
                x = r["gates"][g]
                run.append(f"| {page} | {g} | {LABEL.get(x['status'], x['status'])} | {x['evidence'].replace('|', '/')} |")
        if not results:
            run.append(f"| - | all | not-run | {'--no-capture given' if args.no_capture else 'no capture'} |")
    run += ["", "## Reproducibility", "",
            f"- Build repro: {next((s['status'] for s in steps if s['step'] == 'repro'), 'not-run')} - {next((s['note'] for s in steps if s['step'] == 'repro'), '')}",
            f"- Capture repro: {(crepro or {}).get('status', 'not-run')} - {(crepro or {}).get('note', '')}"]
    for d in (crepro or {}).get("diffs", [])[:20]:
        run.append(f"  - {d['key']}: run1={d['run1']} run2={d['run2']}")
    if (od / f"MOBILE_CAPTURE_{pname}_{stamp}").exists():
        run += ["", f"Capture artifacts (run 1): `{od / f'MOBILE_CAPTURE_{pname}_{stamp}'}` (patterns.json, dom.html, aria.yml, shot.png, drawer.png per page/viewport)"]
    fails = [s for s in steps if s["status"] == "FAIL"]
    for s in fails:
        run += ["", f"### {s['step']} FAIL", "", f"Reproduce: `{s['command']}`", "", "```", (s.get("stderr") or s.get("stdout") or "")[-3000:], "```"]
    runp = od / f"MOBILE_RUN_{stamp}.md"
    runp.write_text("\n".join(run) + "\n", encoding="utf-8")

    data = {"stamp": stamp, "project": args.project, "verdict": v, "timings": timings, "engine": engine_desc, "floors": floors,
            "steps": steps, "check_rows": rows, "capture_meta": [cmeta1, cmeta2], "capture_repro": crepro,
            "results": {pg: {vp: {"gates": r["gates"]} for vp, r in per.items()} for pg, per in results.items()}}
    (results_dir / "mobile-latest.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    shutil.copyfile(runp, results_dir / "mobile-latest.md")

    for s in steps:
        print(f"{s['status']:5} {s['step']:14} {s['seconds']:>8}s  {(s['note'] or '')[:100]}")
    for vp in vps:
        for page, per in results.items():
            r = per.get(vp_name(vp))
            if r:
                print(f"{vp_name(vp):9} {page:16} " + " ".join(f"{g}={r['gates'][g]['status']}" for g in GATES))
    print(f"capture repro: {(crepro or {}).get('status', 'not-run')} - {(crepro or {}).get('note', '')}")
    print(f"timings: {timings}")
    print(f"READY verdict: {v} -> {rmd}")
    print(f"run report: {runp}")
    _, f_items, nr_items = verdict(items)
    return 0 if v == "READY" else (1 if f_items else 2)


if __name__ == "__main__":
    raise SystemExit(main())
