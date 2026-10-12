"""a11y_scan.py - px/contrast scan of SpiderCaster built output (and the render.py source).

Standalone stdlib tool. NOT part of lib/check.py (SC Checker owns that file).
  python tools/a11y_scan.py SITE_DIR [SITE_DIR ...]     scan built html (inline <style> + style="")
  python tools/a11y_scan.py --tokens                    sweep every palette token pair (6 pairs x dark/light x 3 templates)
Rules: any text < 16px FAIL; body-class text < 18px FAIL (this engine sets html 18px, so
every font-size must resolve >= 1rem); contrast < 4.5:1 FAIL (3:1 for large text, >= 24px or >= 18.66px bold).
Exit 1 on any FAIL.
"""
import re, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import render as R

ROOT_PX = 18.0
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
DECL = re.compile(r"([a-z-]+)\s*:\s*([^;]+)")

def css_of(html):
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))

def parse_rules(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for sel, body in RULE.findall(css):
        sel = sel.strip()
        if sel.startswith("@"):
            continue
        yield sel, dict((k, v.strip()) for k, v in DECL.findall(body)), body.strip()

def root_vars(css):
    m = re.search(r":root\{([^}]*)\}", css)
    return dict(re.findall(r"--([\w-]+):([^;]+)", m.group(1))) if m else {}

def px_of(val, parent=ROOT_PX):
    """Smallest px a font-size value can resolve to (clamp -> min, max(a,b) -> max)."""
    v = val.strip().lower()
    m = re.fullmatch(r"max\((.+),(.+)\)", v)
    if m:
        a, b = px_of(m.group(1), parent), px_of(m.group(2), parent)
        return max(x for x in (a, b) if x is not None) if (a is not None or b is not None) else None
    m = re.fullmatch(r"clamp\(([^,]+),.*", v)
    if m:
        return px_of(m.group(1), parent)
    m = re.fullmatch(r"([\d.]+)(px|rem|em)", v)
    if m:
        n = float(m.group(1)); u = m.group(2)
        return n if u == "px" else n * ROOT_PX if u == "rem" else n * parent
    return None

def hexes(val, vars_):
    v = val.strip()
    m = re.fullmatch(r"var\(--([\w-]+)\)", v)
    if m:
        return hexes(vars_.get(m.group(1), ""), vars_)
    if re.fullmatch(r"#[0-9a-fA-F]{6}", v):
        return v.lower(), 1.0
    if re.fullmatch(r"#[0-9a-fA-F]{3}", v):
        return "#" + "".join(c * 2 for c in v[1:]).lower(), 1.0
    m = re.fullmatch(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)(?:[ ,/]+([\d.]+))?\s*\)", v)
    if m:
        return R.rgb_to_hex(*(int(m.group(i)) for i in (1, 2, 3))), float(m.group(4) or 1)
    return None

def blend(fg, a, bg):
    return R.mix_hex(bg, fg, a)

def is_large(px, bold):
    return px >= 24 or (bold and px >= 18.66)

def scan_html(path, findings, notes):
    html = Path(path).read_text(encoding="utf-8", errors="replace")
    css = css_of(html)
    V = root_vars(css)
    bgs = {k: hexes(V[k], V)[0] for k in ("bg", "surface", "surface2") if k in V and hexes(V[k], V)}
    acc = hexes(V.get("accent", ""), V); acc2 = hexes(V.get("accent2", ""), V)
    accent = acc[0] if acc else None; accent2 = acc2[0] if acc2 else None
    f = lambda kind, where, msg: findings.append(f"{Path(path).name}: {kind}: {where}: {msg}")
    own_bg = {  # selector fragment -> backgrounds the text sits on (first match wins)
        ".cta-panel .btn.primary": [bgs.get("bg")], ".btn.primary": [accent, accent2], ".badge": [accent, accent2], ".avatar": [accent, accent2],
        ".brand-mark": [accent], ".step-n": [accent, accent2], ".phone-bar": [accent],
        ".cta-panel": [accent, accent2], ".tile .cap": ["#474747"],  # .72 black over worst-case white photo
    }
    for sel, d, raw in parse_rules(css):
        # --- px
        if "font-size" in d:
            px = px_of(d["font-size"])
            if px is not None:
                if px < 16:
                    f("FAIL px<16", sel, f"font-size:{d['font-size']} = {px:.2f}px")
                elif px < ROOT_PX and "input" not in sel:
                    f("FAIL px<18", sel, f"font-size:{d['font-size']} = {px:.2f}px (body text floor 18px)")
        if "font" in d and re.search(r"\b(\d+(\.\d+)?)px\b", d["font"]):
            f("WARN", sel, f"font shorthand {d['font']}")
        # --- contrast
        col = d.get("color")
        if col and col not in ("inherit", "currentColor"):
            h = hexes(col, V)
            if not h:
                continue
            fg, a = h
            # opacity on same rule lowers effective contrast
            op = float(d["opacity"]) if "opacity" in d and re.fullmatch(r"[\d.]+", d["opacity"]) else 1.0
            a *= op
            targets = None
            for frag, tg in own_bg.items():
                if frag in sel:
                    targets = [t for t in tg if t]; break
            if targets is None:
                targets = list(bgs.values())
            px = px_of(d.get("font-size", "1rem")) or ROOT_PX
            bold = d.get("font-weight", "400") in ("600", "700", "800", "bold")
            floor = 3.0 if is_large(px, bold) else 4.5
            for bg in targets:
                eff = blend(fg, a, bg) if a < 1 else fg
                cr = R.contrast_ratio(eff, bg)
                if cr < floor:
                    f("FAIL contrast", sel, f"color {col}->{eff} on {bg} = {cr:.2f}:1 (< {floor})")
        elif "opacity" in d and "reveal" not in sel and re.fullmatch(r"[\d.]+", d["opacity"]) and float(d["opacity"]) < 1 and not any(k in d for k in ("position",)):
            f("FAIL contrast", sel, f"opacity:{d['opacity']} dims inherited text colour (blend not verifiable)")
    # CTA panel lede etc. inherit on_accent: check gradient ends
    on = hexes(V.get("on-accent", ""), V)
    if on and accent:
        for nm, bg in (("accent", accent), ("accent2", accent2)):
            cr = R.contrast_ratio(on[0], bg)
            if cr < 4.5:
                f("FAIL contrast", ":root --on-accent", f"{on[0]} on {nm} {bg} = {cr:.2f}:1")
    if "::placeholder" not in css and "<input" in html:
        f("FAIL contrast", "input", "no ::placeholder colour rule (browser default grey ~4.2:1 on surface2)")
    for m in re.finditer(r'style="([^"]*)"', html):
        d = dict(DECL.findall(m.group(1)))
        if "font-size" in d:
            px = px_of(d["font-size"])
            if px is not None and px < ROOT_PX:
                f("FAIL px<18", "inline style", m.group(1))
        if "color" in d or "opacity" in d:
            notes.append(f"{Path(path).name}: inline style with color/opacity: {m.group(1)[:80]}")
    for m in re.finditer(r'<(?:font|small)\b', html):
        f("FAIL px", "markup", m.group(0))

def sweep_tokens(findings):
    pairs = [(a, b) for a, b in R.DARK_PAIRS] + [(a, b) for a, b in R.LIGHT_PAIRS]
    n = 0
    for tpl in ("modern", "editorial", "bold"):
        for dark, plist in ((True, R.DARK_PAIRS), (False, R.LIGHT_PAIRS)):
            for a, b in plist:
                p = R.build_palette({"dark": dark, "template": tpl, "accent": a, "accent2": b}, "x")
                n += 1
                tag = f"{tpl}/{'dark' if dark else 'light'}/{a}"
                tx = p.get("accent_text", p["accent"])
                for nm, bg in (("bg", p["bg"]), ("surface", p["surface"]), ("surface2", p["surface2"])):
                    for tn, fg in (("text", p["text"]), ("muted", p["muted"]), ("accent-text", tx), ("price", p["price"])):
                        cr = R.contrast_ratio(fg, bg)
                        if cr < 4.5:
                            findings.append(f"tokens: FAIL contrast: {tag}: {tn} {fg} on {nm} {bg} = {cr:.2f}:1")
                for nm, bg in (("accent", p["accent"]), ("accent2", p["accent2"])):
                    cr = R.contrast_ratio(p["on_accent"], bg)
                    if cr < 4.5:
                        findings.append(f"tokens: FAIL contrast: {tag}: on_accent {p['on_accent']} on {nm} {bg} = {cr:.2f}:1")
    return n

def main(argv):
    findings, notes = [], []
    sites = [a for a in argv if not a.startswith("--")]
    if "--tokens" in argv:
        n = sweep_tokens(findings)
        print(f"token sweep: {n} palettes")
    pages = 0
    for s in sites:
        for p in sorted(Path(s).glob("*.html")):
            scan_html(p, findings, notes); pages += 1
    for line in findings: print(line)
    for line in notes: print("NOTE", line)
    print(f"a11y_scan: {pages} page(s), {len(findings)} finding(s)")
    return 1 if any("FAIL" in x for x in findings) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))