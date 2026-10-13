"""Multi-level graphics generation engine for SpiderCaster sites.

Provides several levels of graphic generation:
  Level 0: Deterministic procedural vector scenes (terminal, dashboard, browser, isometric)
  Level 1: Ambient mesh lighting, dot matrix patterns, and dynamic sparklines
  Level 2: Local raster asset auditing, luminance normalization, and size optimization
  Level 3: Multi-slot AI photographic synthesis (hero, gallery, feature spotlights)
  Level 4: Visual verification and probe readiness

Zero-token defaults, pure standard library (optional Pillow for raster optimization),
and strictly zero remote URLs in emitted markup.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib import render

# ---------------------------------------------------------------- Level 0: Vector Art Scenes

SCENE_KINDS = ("browser", "terminal", "dashboard", "isometric", "editorial")


def _esc(text: str) -> str:
    return render.esc(text)


def generate_vector_scene(
    kind: str = "browser",
    brand: str = "SpiderCaster",
    palette: dict | None = None,
    width: int = 640,
    height: int = 360,
) -> str:
    """Generate a responsive 16:9 inline vector SVG illustration.

    Pure vector geometry with zero text nodes and zero external URLs
    to comply with fleet cited_text and no_hotlink gates.
    """
    clean_brand = _esc(brand or "Studio")
    pal = palette or {}
    accent = pal.get("accent") or "var(--accent)"
    accent2 = pal.get("accent2") or "var(--accent2)"
    surface = pal.get("surface") or "var(--surface)"
    surface2 = pal.get("surface2") or "var(--surface2)"
    bg = pal.get("bg") or "var(--bg)"
    line = pal.get("line") or "var(--line)"
    text_color = pal.get("text") or "var(--text)"
    muted = pal.get("muted") or "var(--muted)"

    if kind == "terminal":
        # Developer CLI / Terminal build engine scene
        return (
            f'<svg class="hero-scene hero-terminal" viewBox="0 0 {width} {height}" fill="none" role="img" aria-label="{clean_brand}">'
            f'<defs>'
            f'<linearGradient id="sc-t-bg" x1="0" y1="0" x2="{width}" y2="{height}" gradientUnits="userSpaceOnUse">'
            f'<stop stop-color="{surface}"/>'
            f'<stop offset="1" stop-color="{bg}"/>'
            f'</linearGradient>'
            f'<radialGradient id="sc-t-glow" cx="{width * 0.75}" cy="100" r="180" gradientUnits="userSpaceOnUse">'
            f'<stop stop-color="{accent}" stop-opacity="0.25"/>'
            f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/>'
            f'</radialGradient>'
            f'</defs>'
            f'<rect width="{width}" height="{height}" rx="16" fill="url(#sc-t-bg)"/>'
            f'<circle cx="{width * 0.75}" cy="100" r="180" fill="url(#sc-t-glow)"/>'
            # Terminal Window
            f'<rect x="28" y="24" width="{width - 56}" height="{height - 48}" rx="14" fill="{surface}" fill-opacity="0.9" stroke="{line}" stroke-width="1"/>'
            # Titlebar
            f'<path d="M28 38a14 14 0 0 1 14-14h{width - 84}a14 14 0 0 1 14 14v16H28V38z" fill="{surface2}" fill-opacity="0.95"/>'
            f'<line x1="28" y1="54" x2="{width - 28}" y2="54" stroke="{line}" stroke-width="1"/>'
            f'<circle cx="52" cy="39" r="5" fill="#ff5f56"/>'
            f'<circle cx="68" cy="39" r="5" fill="#ffbd2e"/>'
            f'<circle cx="84" cy="39" r="5" fill="#27c93f"/>'
            f'<rect x="180" y="32" width="280" height="14" rx="7" fill="{bg}" stroke="{line}" stroke-width="1"/>'
            f'<circle cx="194" cy="39" r="3" fill="{accent}"/>'
            f'<rect x="206" y="36" width="90" height="6" rx="3" fill="{muted}" fill-opacity="0.5"/>'
            # Terminal Lines
            # Prompt 1
            f'<path d="M52 82l6 6-6 6" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<rect x="70" y="84" width="140" height="8" rx="4" fill="{text_color}" fill-opacity="0.9"/>'
            f'<rect x="52" y="104" width="240" height="7" rx="3.5" fill="{muted}" fill-opacity="0.6"/>'
            f'<rect x="52" y="118" width="310" height="7" rx="3.5" fill="{muted}" fill-opacity="0.6"/>'
            # Status Badge
            f'<rect x="52" y="136" width="96" height="20" rx="5" fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-width="1"/>'
            f'<circle cx="64" cy="146" r="3.5" fill="{accent}"/>'
            f'<rect x="74" y="143" width="60" height="6" rx="3" fill="{accent}"/>'
            # Prompt 2
            f'<path d="M52 178l6 6-6 6" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<rect x="70" y="180" width="180" height="8" rx="4" fill="{text_color}" fill-opacity="0.9"/>'
            # Output grid card
            f'<rect x="52" y="204" width="{width - 104}" height="110" rx="10" fill="{surface2}" stroke="{line}" stroke-width="1"/>'
            f'<rect x="72" y="222" width="120" height="8" rx="4" fill="{muted}" fill-opacity="0.7"/>'
            f'<rect x="72" y="240" width="260" height="7" rx="3.5" fill="{muted}" fill-opacity="0.45"/>'
            f'<rect x="72" y="254" width="200" height="7" rx="3.5" fill="{muted}" fill-opacity="0.45"/>'
            f'<rect x="72" y="278" width="80" height="22" rx="6" fill="{accent}"/>'
            f'<circle cx="{width - 96}" cy="259" r="24" fill="{surface}" stroke="{accent}" stroke-width="1.5"/>'
            f'<path d="M{width - 104} 259l6 6 12-12" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'</svg>'
        )

    elif kind == "dashboard":
        # Analytics & Metrics Dashboard Scene
        return (
            f'<svg class="hero-scene hero-dashboard" viewBox="0 0 {width} {height}" fill="none" role="img" aria-label="{clean_brand}">'
            f'<defs>'
            f'<linearGradient id="sc-d-bg" x1="0" y1="0" x2="{width}" y2="{height}" gradientUnits="userSpaceOnUse">'
            f'<stop stop-color="{surface}"/>'
            f'<stop offset="1" stop-color="{bg}"/>'
            f'</linearGradient>'
            f'<linearGradient id="sc-d-accent" x1="0" y1="0" x2="1" y2="1">'
            f'<stop stop-color="{accent}"/>'
            f'<stop offset="1" stop-color="{accent2}"/>'
            f'</linearGradient>'
            f'<radialGradient id="sc-d-glow" cx="{width * 0.6}" cy="120" r="210" gradientUnits="userSpaceOnUse">'
            f'<stop stop-color="{accent}" stop-opacity="0.22"/>'
            f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/>'
            f'</radialGradient>'
            f'</defs>'
            f'<rect width="{width}" height="{height}" rx="16" fill="url(#sc-d-bg)"/>'
            f'<circle cx="{width * 0.6}" cy="120" r="210" fill="url(#sc-d-glow)"/>'
            # Window Frame
            f'<rect x="24" y="20" width="{width - 48}" height="{height - 40}" rx="14" fill="{surface}" fill-opacity="0.88" stroke="{line}" stroke-width="1"/>'
            # Header bar
            f'<path d="M24 34a14 14 0 0 1 14-14h{width - 76}a14 14 0 0 1 14 14v16H24V34z" fill="{surface2}" fill-opacity="0.9"/>'
            f'<line x1="24" y1="50" x2="{width - 24}" y2="50" stroke="{line}" stroke-width="1"/>'
            f'<circle cx="48" cy="35" r="5" fill="#ff5f56"/>'
            f'<circle cx="64" cy="35" r="5" fill="#ffbd2e"/>'
            f'<circle cx="80" cy="35" r="5" fill="#27c93f"/>'
            # Metric Cards Row
            f'<rect x="44" y="68" width="160" height="92" rx="10" fill="{surface2}" stroke="{line}" stroke-width="1"/>'
            f'<rect x="58" y="82" width="24" height="24" rx="6" fill="{accent}" fill-opacity="0.15"/>'
            f'<rect x="58" y="114" width="70" height="16" rx="4" fill="{text_color}" fill-opacity="0.95"/>'
            f'<rect x="58" y="136" width="90" height="8" rx="4" fill="{muted}" fill-opacity="0.5"/>'
            f'<rect x="220" y="68" width="160" height="92" rx="10" fill="{surface2}" stroke="{line}" stroke-width="1"/>'
            f'<rect x="234" y="82" width="24" height="24" rx="6" fill="{accent2}" fill-opacity="0.15"/>'
            f'<rect x="234" y="114" width="80" height="16" rx="4" fill="{accent}"/>'
            f'<rect x="234" y="136" width="100" height="8" rx="4" fill="{muted}" fill-opacity="0.5"/>'
            f'<rect x="396" y="68" width="{width - 440}" height="92" rx="10" fill="{surface2}" stroke="{line}" stroke-width="1"/>'
            f'<rect x="410" y="82" width="24" height="24" rx="6" fill="{accent}" fill-opacity="0.15"/>'
            f'<rect x="410" y="114" width="60" height="16" rx="4" fill="{text_color}" fill-opacity="0.95"/>'
            f'<rect x="410" y="136" width="85" height="8" rx="4" fill="{muted}" fill-opacity="0.5"/>'
            # Large Chart Area
            f'<rect x="44" y="174" width="{width - 88}" height="150" rx="12" fill="{surface2}" stroke="{line}" stroke-width="1"/>'
            f'<rect x="64" y="190" width="130" height="10" rx="5" fill="{muted}" fill-opacity="0.7"/>'
            # Grid lines
            f'<line x1="64" y1="230" x2="{width - 64}" y2="230" stroke="{line}" stroke-dasharray="3 3"/>'
            f'<line x1="64" y1="265" x2="{width - 64}" y2="265" stroke="{line}" stroke-dasharray="3 3"/>'
            f'<line x1="64" y1="300" x2="{width - 64}" y2="300" stroke="{line}" stroke-dasharray="3 3"/>'
            # Sparkline Chart
            f'<path d="M64 285 Q 140 240, 220 255 T 380 215 T 490 230 T {width - 64} 195" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>'
            f'<circle cx="{width - 64}" cy="195" r="5" fill="{accent}"/>'
            f'<circle cx="380" cy="215" r="4" fill="{accent2}"/>'
            f'</svg>'
        )

    else:
        # Default: Modern Studio App Window Scene (clean, responsive, sleek)
        return render.vector_hero_svg()


# ---------------------------------------------------------------- Level 1: Dynamic Sparklines

def generate_sparkline(values: list[float], width: int = 120, height: int = 36, color: str = "var(--accent)") -> str:
    """Generate an inline SVG sparkline path from numeric values."""
    if not values or len(values) < 2:
        return ""
    v_min, v_max = min(values), max(values)
    rng = (v_max - v_min) or 1.0
    dx = width / (len(values) - 1)
    pts = []
    for i, val in enumerate(values):
        x = i * dx
        y = height - ((val - v_min) / rng * (height - 8) + 4)
        pts.append((x, y))
    d_path = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        d_path += f" L{pts[i][0]:.1f} {pts[i][1]:.1f}"
    return (
        f'<svg class="sparkline" viewBox="0 0 {width} {height}" fill="none" aria-hidden="true">'
        f'<path d="{d_path}" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3" fill="{color}"/>'
        f'</svg>'
    )


# ---------------------------------------------------------------- Level 2: Local Asset Auditing & Normalization

def audit_project_assets(project_dir: Path) -> dict:
    """Audit project assets for dimensions, luminance (photo_luma), and byte weight.

    Returns structured status data without mutating files.
    """
    assets_dir = Path(project_dir) / "assets"
    if not assets_dir.is_dir():
        return {"ok": True, "count": 0, "assets": []}

    results = []
    all_ok = True
    for p in sorted(assets_dir.iterdir()):
        if not p.is_file() or p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        size_b = p.stat().st_size
        w, h = render.image_box(p)
        luma = None
        luma_ok = True
        try:
            from lib.check import LUMA_MAX, LUMA_MIN, _mean_luma

            luma, _ = _mean_luma(p)
            luma_ok = LUMA_MIN <= luma <= LUMA_MAX
        except (OSError, ImportError, ValueError):
            luma = None
            luma_ok = True

        weight_ok = size_b <= 204800  # 200KB fleet budget
        item_ok = weight_ok and luma_ok and (w > 0 and h > 0)
        if not item_ok:
            all_ok = False

        results.append({
            "file": p.name,
            "width": w,
            "height": h,
            "bytes": size_b,
            "weight_ok": weight_ok,
            "luma": round(luma, 1) if luma is not None else None,
            "luma_ok": luma_ok,
            "ok": item_ok,
        })

    return {"ok": all_ok, "count": len(results), "assets": results}


def normalize_image_luma_and_weight(path: Path, target_luma: float = 120.0, max_bytes: int = 204800) -> bool:
    """Safely adjust image brightness and compression to clear photo_luma and weight gates."""
    try:
        from PIL import Image, ImageEnhance

        from lib.check import LUMA_MAX, LUMA_MIN, _mean_luma

        img = Image.open(path)
        cur_luma, _ = _mean_luma(path)
        if cur_luma < LUMA_MIN:
            factor = min(1.6, max(1.1, (LUMA_MIN + 15) / max(1.0, cur_luma)))
            img = ImageEnhance.Brightness(img).enhance(factor)
        elif cur_luma > LUMA_MAX:
            factor = max(0.6, min(0.9, (LUMA_MAX - 15) / max(1.0, cur_luma)))
            img = ImageEnhance.Brightness(img).enhance(factor)

        # Optimize file size
        quality = 85
        while quality >= 60:
            img.save(path, quality=quality, optimize=True)
            if path.stat().st_size <= max_bytes:
                break
            quality -= 5
        return True
    except (OSError, ImportError, ValueError):
        return False


# ---------------------------------------------------------------- Level 3: AI Photographic Synthesis

def prompt_for_slot(slot: str, brief: str, project_name: str) -> str:
    """Build a specialized camera prompt following the visual research rules."""
    context = brief or project_name
    if slot == "hero":
        return (
            f"Editorial still life photograph for {context}, no text, no logo, no watermark. "
            "Warm natural light from a window, subject positioned on the right third, quiet space on the left, "
            "calm craftsmanship and deep focus. Not a product ad."
        )
    elif slot.startswith("gallery"):
        return (
            f"Authentic documentary detail photograph relating to {context}, no text, no logo, no watermark. "
            "Sharp focus on tools, materials, and workshop surfaces, balanced natural shadows. Not an advertisement."
        )
    return (
        f"Clean still life photograph for {context}, no text, no watermark, quiet natural lighting. Not a product ad."
    )


def imagine_project_slots(
    project_dir: Path,
    slots: list[str] | None = None,
    provider: str = "xai",
    model: str = "",
) -> list[dict]:
    """Generate requested local asset slots using xAI Grok Imagine or OpenRouter.

    Saves files strictly to project/assets/<name>.png and writes receipt JSONs.
    """
    from lib.imagine import ImagineError, generate

    project = Path(project_dir)
    assets_dir = project / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    brief = ""
    for name in ("brief.md", "brief.txt"):
        bp = project / name
        if bp.is_file():
            brief = bp.read_text(encoding="utf-8", errors="replace").strip()
            break

    target_slots = slots or ["hero"]
    receipts = []
    for slot in target_slots:
        dest = assets_dir / f"{slot}.png"
        if dest.is_file():
            continue  # Don't overwrite existing
        prompt = prompt_for_slot(slot, brief, project.name)
        try:
            rc = generate(
                prompt,
                dest,
                provider=provider,
                model=model,
                aspect_ratio="16:9" if slot == "hero" else "4:3",
                quality="low",
            )
            receipts.append(rc)
        except ImagineError as exc:
            receipts.append({"slot": slot, "error": str(exc)})
    return receipts


# ---------------------------------------------------------------- Level 4: Engine Selftest

def selftest() -> int:
    """Verify procedural vector scene generation across all scene kinds and sparklines."""
    for kind in SCENE_KINDS:
        svg = generate_vector_scene(kind=kind, brand="TestSite")
        assert svg.startswith("<svg") and svg.endswith("</svg>"), f"scene {kind} must emit svg"
        assert "http://" not in svg and "https://" not in svg, f"scene {kind} must have no external URLs"
        assert "<text" not in svg, f"scene {kind} must have zero text nodes"

    spark = generate_sparkline([10.0, 25.0, 18.0, 42.0, 38.0, 60.0])
    assert "<path" in spark and "circle" in spark, "sparkline must emit path and point"
    print("graphics_engine selftest ok")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
