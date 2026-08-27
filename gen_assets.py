#!/usr/bin/env python3
"""Generate on-brand placeholder SVG imagery for grosir.in.
Consistent visual identity: warm editorial palette (rust/sage/ochre on
cream/sand), Fraunces-style serif label, hand-crafted organic linework —
matching the site's CSS design system.
"""
import os, sys, math, random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "img")
os.makedirs(OUT, exist_ok=True)

CHARCOAL = "#1a1a1a"
CREAM = "#fffef9"
SAND = "#f7f6f3"
RUST = "#b85c4e"
SAGE = "#7c9885"
OCHRE = "#d4a574"
BORDER = "#e8e7e3"

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(round(c)))) for c in rgb)

def tint(hex_color, amount, towards=(255, 255, 255)):
    r, g, b = hex_to_rgb(hex_color)
    tr, tg, tb = towards
    return rgb_to_hex((r + (tr - r) * amount, g + (tg - g) * amount, b + (tb - b) * amount))

def shade(hex_color, amount):
    return tint(hex_color, amount, towards=(0, 0, 0))

random.seed(42)

def grain(n=90, w=800, h=800, opacity=0.05, color=CHARCOAL):
    dots = []
    for _ in range(n):
        x = random.uniform(0, w)
        y = random.uniform(0, h)
        r = random.uniform(0.5, 1.3)
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{color}" opacity="{opacity}"/>')
    return "".join(dots)

def pattern_defs(kind, pid, base, accent):
    """Return (<pattern> defs, fill-url) for a material texture, clipped to bag."""
    if kind == "weave":
        p = f'''<pattern id="{pid}" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(0)">
          <rect width="16" height="16" fill="{base}"/>
          <path d="M0 8H16" stroke="{shade(base,0.12)}" stroke-width="1"/>
          <path d="M8 0V16" stroke="{shade(base,0.08)}" stroke-width="1"/>
        </pattern>'''
    elif kind == "dots":
        p = f'''<pattern id="{pid}" width="18" height="18" patternUnits="userSpaceOnUse">
          <rect width="18" height="18" fill="{base}"/>
          <circle cx="4" cy="4" r="1.4" fill="{shade(base,0.18)}"/>
          <circle cx="13" cy="13" r="1.4" fill="{shade(base,0.18)}"/>
        </pattern>'''
    elif kind == "diagonal":
        p = f'''<pattern id="{pid}" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="14" height="14" fill="{base}"/>
          <rect x="0" y="0" width="7" height="14" fill="{shade(base,0.10)}"/>
        </pattern>'''
    elif kind == "crosshatch":
        p = f'''<pattern id="{pid}" width="20" height="20" patternUnits="userSpaceOnUse">
          <rect width="20" height="20" fill="{base}"/>
          <path d="M0 0L20 20M20 0L0 20" stroke="{shade(base,0.10)}" stroke-width="1"/>
        </pattern>'''
    elif kind == "scribble":
        p = f'''<pattern id="{pid}" width="22" height="22" patternUnits="userSpaceOnUse">
          <rect width="22" height="22" fill="{base}"/>
          <path d="M0 6 Q6 0 11 6 T22 6" stroke="{shade(base,0.20)}" stroke-width="1.3" fill="none"/>
          <path d="M0 16 Q6 10 11 16 T22 16" stroke="{shade(base,0.14)}" stroke-width="1.1" fill="none"/>
        </pattern>'''
    elif kind == "wave":
        p = f'''<pattern id="{pid}" width="26" height="14" patternUnits="userSpaceOnUse">
          <rect width="26" height="14" fill="{base}"/>
          <path d="M0 7 Q6.5 1 13 7 T26 7" stroke="{shade(base,0.14)}" stroke-width="1.2" fill="none"/>
        </pattern>'''
    elif kind == "print-block":
        p = f'''<pattern id="{pid}" width="40" height="40" patternUnits="userSpaceOnUse">
          <rect width="40" height="40" fill="{base}"/>
          <rect x="4" y="4" width="14" height="14" fill="{accent}" opacity="0.55"/>
          <circle cx="30" cy="12" r="7" fill="{tint(accent,0.35)}" opacity="0.6"/>
          <rect x="18" y="24" width="18" height="10" fill="{shade(base,0.15)}" opacity="0.7"/>
        </pattern>'''
    else:
        p = f'<pattern id="{pid}" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="{base}"/></pattern>'
    return p, f"url(#{pid})"

def zipper_motif(cx, y, width, color=CHARCOAL):
    """A simple zipper: dashed teeth line + a pull tab, used to visually
    distinguish 'sleting' (zippered) items from plain ('polos') ones."""
    x0, x1 = cx - width / 2, cx + width / 2
    return (
        f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{color}" stroke-width="2" stroke-dasharray="1.5 3.5" stroke-linecap="round" opacity="0.85"/>'
        f'<rect x="{cx-9}" y="{y-7}" width="18" height="14" rx="3" fill="{color}" opacity="0.9"/>'
        f'<circle cx="{cx}" cy="{y}" r="2.4" fill="{CREAM}"/>'
    )

def brand_watermark():
    return f'''<g transform="translate(700 742)" opacity="0.55">
  <path d="M-16 -4 C -16 -12 16 -12 16 -4" fill="none" stroke="{CHARCOAL}" stroke-width="3" stroke-linecap="round"/>
  <rect x="-20" y="-4" width="40" height="30" rx="4" fill="none" stroke="{CHARCOAL}" stroke-width="3"/>
  <text x="34" y="18" font-family="Georgia, serif" font-size="16" fill="{CHARCOAL}">grosir.in</text>
</g>'''

def label_ribbon(cx, cy, label, accent):
    return f'''<g transform="translate({cx} {cy})">
    <rect x="-118" y="-22" width="236" height="44" rx="22" fill="{CREAM}" stroke="{accent}" stroke-width="1.5" opacity="0.95"/>
    <text x="0" y="6" font-family="Georgia, 'Times New Roman', serif" font-size="15" font-weight="600" letter-spacing="1.5" fill="{shade(accent,0.25)}" text-anchor="middle">{label}</text>
  </g>'''

def tote_svg(material_key, label, base, accent, pattern_kind, bg=SAND, rotate=-2, has_zipper=False):
    """Build one square (800x800) totebag illustration SVG."""
    pid = f"pat-{material_key}"
    pdef, pfill = pattern_defs(pattern_kind, pid, base, accent)
    blob_id = f"blob-{material_key}"
    cx, cy = 400, 430
    zip_svg = zipper_motif(cx, cy - 143, 300) if has_zipper else ""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800" role="img" aria-label="Ilustrasi {label}">
<defs>
  {pdef}
  <radialGradient id="{blob_id}" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{accent}" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
  <filter id="grainblur-{material_key}"><feGaussianBlur stdDeviation="1.1"/></filter>
</defs>
<rect width="800" height="800" fill="{bg}"/>
{grain(120, 800, 800, 0.05)}
<circle cx="{cx}" cy="{cy-40}" r="290" fill="url(#{blob_id})"/>

<g transform="rotate({rotate} {cx} {cy})">
  <!-- handles -->
  <path d="M{cx-95} {cy-150} C {cx-95} {cy-260} {cx+95} {cy-260} {cx+95} {cy-150}"
        fill="none" stroke="{CHARCOAL}" stroke-width="13" stroke-linecap="round" opacity="0.88"/>
  <path d="M{cx-95} {cy-150} C {cx-95} {cy-260} {cx+95} {cy-260} {cx+95} {cy-150}"
        fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round" opacity="0.9"/>

  <!-- top hem -->
  <rect x="{cx-165}" y="{cy-160}" width="330" height="34" rx="8" fill="{shade(base,0.10)}" stroke="{CHARCOAL}" stroke-width="2.5"/>
  {zip_svg}

  <!-- bag body -->
  <rect x="{cx-180}" y="{cy-130}" width="360" height="330" rx="14" fill="{pfill}" stroke="{CHARCOAL}" stroke-width="3"/>

  <!-- side gussets -->
  <path d="M{cx-140} {cy-130} V {cy+200}" stroke="{shade(base,0.16)}" stroke-width="2" opacity="0.6"/>
  <path d="M{cx+140} {cy-130} V {cy+200}" stroke="{shade(base,0.16)}" stroke-width="2" opacity="0.6"/>

  <!-- bottom stitch -->
  <line x1="{cx-165}" y1="{cy+178}" x2="{cx+165}" y2="{cy+178}" stroke="{CHARCOAL}" stroke-width="2" stroke-dasharray="6 6" opacity="0.5"/>

  <!-- label ribbon -->
  {label_ribbon(cx, cy+35, label, accent)}
</g>

{brand_watermark()}
</svg>'''
    return svg

def pouch_svg(key, label, base, accent, pattern_kind, bg=SAND, rotate=-2):
    """Small zippered pouch — no handles, wrist loop instead."""
    pid = f"pat-{key}"
    pdef, pfill = pattern_defs(pattern_kind, pid, base, accent)
    blob_id = f"blob-{key}"
    cx, cy = 400, 420
    w, h = 320, 220
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800" role="img" aria-label="Ilustrasi {label}">
<defs>
  {pdef}
  <radialGradient id="{blob_id}" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{accent}" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="800" height="800" fill="{bg}"/>
{grain(120, 800, 800, 0.05)}
<circle cx="{cx}" cy="{cy}" r="260" fill="url(#{blob_id})"/>

<g transform="rotate({rotate} {cx} {cy})">
  <!-- wrist loop -->
  <path d="M{cx+w/2-34} {cy-h/2+8} q 30 -8 30 24" fill="none" stroke="{CHARCOAL}" stroke-width="7" stroke-linecap="round" opacity="0.85"/>
  <!-- body -->
  <rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="26" fill="{pfill}" stroke="{CHARCOAL}" stroke-width="3"/>
  {zipper_motif(cx, cy-h/2+24, w-56)}
</g>

{label_ribbon(cx, cy+h/2+58, label, accent)}
{brand_watermark()}
</svg>'''
    return svg

def pencil_case_svg(key, label, base, accent, pattern_kind, bg=SAND, rotate=-1):
    """Long narrow zippered pencil case."""
    pid = f"pat-{key}"
    pdef, pfill = pattern_defs(pattern_kind, pid, base, accent)
    blob_id = f"blob-{key}"
    cx, cy = 400, 420
    w, h = 420, 140
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800" role="img" aria-label="Ilustrasi {label}">
<defs>
  {pdef}
  <radialGradient id="{blob_id}" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{accent}" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="800" height="800" fill="{bg}"/>
{grain(120, 800, 800, 0.05)}
<circle cx="{cx}" cy="{cy}" r="260" fill="url(#{blob_id})"/>

<g transform="rotate({rotate} {cx} {cy})">
  <rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="20" fill="{pfill}" stroke="{CHARCOAL}" stroke-width="3"/>
  {zipper_motif(cx, cy-h/2+22, w-70)}
  <!-- small tab pull at the end -->
  <path d="M{cx+w/2-16} {cy-h/2+22} q 22 0 22 18" fill="none" stroke="{CHARCOAL}" stroke-width="5" stroke-linecap="round" opacity="0.75"/>
</g>

{label_ribbon(cx, cy+h/2+70, label, accent)}
{brand_watermark()}
</svg>'''
    return svg

def sling_bag_svg(key, label, base, accent, pattern_kind, bg=SAND, rotate=-2):
    """Sling/crossbody bag — single diagonal strap instead of two handles."""
    pid = f"pat-{key}"
    pdef, pfill = pattern_defs(pattern_kind, pid, base, accent)
    blob_id = f"blob-{key}"
    cx, cy = 400, 440
    w, h = 260, 260
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800" role="img" aria-label="Ilustrasi {label}">
<defs>
  {pdef}
  <radialGradient id="{blob_id}" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{accent}" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="800" height="800" fill="{bg}"/>
{grain(120, 800, 800, 0.05)}
<circle cx="{cx}" cy="{cy-40}" r="280" fill="url(#{blob_id})"/>

<g transform="rotate({rotate} {cx} {cy})">
  <!-- single diagonal strap -->
  <path d="M{cx-w/2+10} {cy-h/2+20} C {cx-260} {cy-360} {cx+260} {cy-360} {cx+w/2-20} {cy-h/2+10}"
        fill="none" stroke="{CHARCOAL}" stroke-width="14" stroke-linecap="round" opacity="0.88"/>
  <path d="M{cx-w/2+10} {cy-h/2+20} C {cx-260} {cy-360} {cx+260} {cy-360} {cx+w/2-20} {cy-h/2+10}"
        fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round" opacity="0.9"/>

  <!-- top flap -->
  <path d="M{cx-w/2} {cy-h/2+10} Q {cx} {cy-h/2-40} {cx+w/2} {cy-h/2+10} L{cx+w/2} {cy-h/2+50} Q {cx} {cy-h/2+70} {cx-w/2} {cy-h/2+50} Z"
        fill="{shade(base,0.08)}" stroke="{CHARCOAL}" stroke-width="2.5"/>

  <!-- body -->
  <rect x="{cx-w/2}" y="{cy-h/2+40}" width="{w}" height="{h}" rx="18" fill="{pfill}" stroke="{CHARCOAL}" stroke-width="3"/>

  <!-- front pocket -->
  <rect x="{cx-w/2+30}" y="{cy}" width="{w-60}" height="{h/2-20}" rx="10" fill="{shade(base,0.1)}" stroke="{CHARCOAL}" stroke-width="2" opacity="0.85"/>
</g>

{label_ribbon(cx, cy+h/2+70, label, accent)}
{brand_watermark()}
</svg>'''
    return svg

# ---------------------------------------------------------------
# Product illustrations (primary + 2 alt angles reusing same identity)
# ---------------------------------------------------------------
PRODUCTS = [
    ("baby-kanvas",    "BABY KANVAS",    tint(OCHRE, 0.65),    RUST,     "weave"),
    ("kanvas-natural", "KANVAS NATURAL", tint(OCHRE, 0.42),    RUST,     "weave"),
    ("blacu",          "BLACU",          tint(OCHRE, 0.78),    CHARCOAL, "crosshatch"),
    ("taslan",         "TASLAN",         tint(SAGE, 0.7),      CHARCOAL, "wave"),
    ("kanvas-denim",   "KANVAS DENIM",   tint(CHARCOAL, 0.55), OCHRE,    "diagonal"),
]

for key, label, base, accent, pat in PRODUCTS:
    svg = tote_svg(key, label, base, accent, pat, rotate=-2)
    with open(f"{OUT}/produk-{key}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    # alt angle 2: mirrored / different rotation for gallery thumbs
    svg2 = tote_svg(key, label, base, accent, pat, rotate=3)
    with open(f"{OUT}/produk-{key}-2.svg", "w", encoding="utf-8") as f:
        f.write(svg2)
    svg3 = tote_svg(key, label, base, accent, pat, rotate=-6)
    with open(f"{OUT}/produk-{key}-3.svg", "w", encoding="utf-8") as f:
        f.write(svg3)

# ---------------------------------------------------------------
# New product-type illustrations (vendor sheet expansion): a zippered
# totebag, plus three genuinely different silhouettes so a pouch doesn't
# get drawn as a miniature tote — accuracy matters since these are what a
# customer expects to receive.
# ---------------------------------------------------------------
OTHER_PRODUCTS = [
    # (key, label, base, accent, pattern, builder)
    ("totebag-sleting", "TOTEBAG SLETING", tint(OCHRE, 0.58), RUST,     "weave",      "tote_zip"),
    ("pouch",           "POUCH",           tint(SAGE, 0.55),  RUST,     "dots",       "pouch"),
    ("tempat-pinsil",   "TEMPAT PINSIL",   tint(RUST, 0.72),  CHARCOAL, "scribble",   "pencil_case"),
    ("gendong",         "GENDONG",         tint(SAGE, 0.4),   OCHRE,    "print-block","sling_bag"),
]

BUILDERS = {
    "tote_zip": lambda key, label, base, accent, pat, rotate: tote_svg(key, label, base, accent, pat, rotate=rotate, has_zipper=True),
    "pouch": pouch_svg,
    "pencil_case": pencil_case_svg,
    "sling_bag": sling_bag_svg,
}

for key, label, base, accent, pat, kind in OTHER_PRODUCTS:
    builder = BUILDERS[kind]
    for suffix, rotate in [("", -2), ("-2", 3), ("-3", -6)]:
        svg = builder(key, label, base, accent, pat, rotate=rotate)
        with open(f"{OUT}/produk-{key}{suffix}.svg", "w", encoding="utf-8") as f:
            f.write(svg)

print("Product illustrations generated:", (len(PRODUCTS) + len(OTHER_PRODUCTS)) * 3)
