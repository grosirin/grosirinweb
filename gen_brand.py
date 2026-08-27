#!/usr/bin/env python3
"""Generate brand-identity assets: favicon, nav/footer logomark, hero
illustration (bulk stock of totebags), and the social share (OG) image.
Shares the exact palette/linework language as the product illustrations.
"""
import os, sys
import cairosvg

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

# ---------------------------------------------------------------
# 1) Favicon / logomark — simple tote bag glyph
# ---------------------------------------------------------------
favicon_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <rect width="32" height="32" rx="7" fill="{CREAM}"/>
  <path d="M11 12C11 8.5 13 6.5 16 6.5C19 6.5 21 8.5 21 12" fill="none" stroke="{RUST}" stroke-width="2" stroke-linecap="round"/>
  <rect x="7.5" y="12" width="17" height="14" rx="2.5" fill="{RUST}" opacity="0.92"/>
  <rect x="7.5" y="12" width="17" height="4.5" rx="2" fill="{OCHRE}" opacity="0.9"/>
</svg>'''
with open(f"{OUT}/favicon.svg", "w", encoding="utf-8") as f:
    f.write(favicon_svg)
cairosvg.svg2png(bytestring=favicon_svg.encode(), write_to=f"{OUT}/favicon.png", output_width=64, output_height=64)

# nav logomark (slightly more detailed, used inline in <header>)
logomark_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none">
  <path d="M8 9C8 5.7 9.8 3.5 12 3.5C14.2 3.5 16 5.7 16 9" stroke="{RUST}" stroke-width="1.6" stroke-linecap="round"/>
  <rect x="5" y="9" width="14" height="11.5" rx="2" fill="none" stroke="{RUST}" stroke-width="1.6"/>
  <path d="M5 12.5H19" stroke="{RUST}" stroke-width="1.2" opacity="0.5"/>
</svg>'''
with open(f"{OUT}/logomark.svg", "w", encoding="utf-8") as f:
    f.write(logomark_svg)

# ---------------------------------------------------------------
# 2) Hero illustration — a small "bulk stock" of totebags
# ---------------------------------------------------------------
def bag(x, y, scale, fill, accent, rot):
    return f'''<g transform="translate({x} {y}) rotate({rot}) scale({scale})">
      <path d="M-70 -95C-70 -145 70 -145 70 -95" fill="none" stroke="{CHARCOAL}" stroke-width="9" stroke-linecap="round" opacity="0.85"/>
      <rect x="-110" y="-100" width="220" height="30" rx="7" fill="{accent}" opacity="0.9"/>
      <rect x="-125" y="-78" width="250" height="230" rx="12" fill="{fill}" stroke="{CHARCOAL}" stroke-width="2.4"/>
      <line x1="-95" y1="-78" x2="-95" y2="140" stroke="{CHARCOAL}" stroke-width="1.4" opacity="0.18"/>
      <line x1="95" y1="-78" x2="95" y2="140" stroke="{CHARCOAL}" stroke-width="1.4" opacity="0.18"/>
    </g>'''

hero_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 720" width="900" height="720" role="img" aria-label="Ilustrasi stok totebag grosir.in">
<defs>
  <radialGradient id="heroblob1" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{RUST}" stop-opacity="0.14"/><stop offset="100%" stop-color="{RUST}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="heroblob2" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{SAGE}" stop-opacity="0.14"/><stop offset="100%" stop-color="{SAGE}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="900" height="720" fill="{CREAM}"/>
<circle cx="640" cy="200" r="260" fill="url(#heroblob1)"/>
<circle cx="220" cy="560" r="240" fill="url(#heroblob2)"/>

{bag(330, 470, 0.72, '#efe3cd', OCHRE, -10)}
{bag(560, 480, 0.78, '#f0d9d2', RUST, 7)}
{bag(450, 380, 0.95, '#e4ece5', SAGE, -2)}

<g transform="translate(450 660)" opacity="0.6">
  <path d="M-16 -4 C -16 -12 16 -12 16 -4" fill="none" stroke="{CHARCOAL}" stroke-width="3" stroke-linecap="round"/>
  <rect x="-20" y="-4" width="40" height="30" rx="4" fill="none" stroke="{CHARCOAL}" stroke-width="3"/>
  <text x="34" y="18" font-family="Georgia, serif" font-size="18" fill="{CHARCOAL}">grosir.in</text>
</g>
</svg>'''
with open(f"{OUT}/hero-illustration.svg", "w", encoding="utf-8") as f:
    f.write(hero_svg)

# ---------------------------------------------------------------
# 3) OG / social share image (1200x630)
# ---------------------------------------------------------------
og_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
<defs>
  <radialGradient id="ogblob1" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{RUST}" stop-opacity="0.16"/><stop offset="100%" stop-color="{RUST}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="ogblob2" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{SAGE}" stop-opacity="0.14"/><stop offset="100%" stop-color="{SAGE}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="1200" height="630" fill="{CREAM}"/>
<circle cx="1000" cy="80" r="260" fill="url(#ogblob1)"/>
<circle cx="120" cy="560" r="240" fill="url(#ogblob2)"/>

<g transform="translate(120 150)">
  <path d="M-14 -4 C -14 -11 14 -11 14 -4" fill="none" stroke="{RUST}" stroke-width="3.4" stroke-linecap="round"/>
  <rect x="-18" y="-4" width="36" height="27" rx="4" fill="none" stroke="{RUST}" stroke-width="3.4"/>
  <text x="30" y="16" font-family="Georgia, serif" font-size="26" fill="{CHARCOAL}">grosir.in</text>
</g>

<text x="120" y="300" font-family="Georgia, serif" font-size="64" fill="{CHARCOAL}" font-weight="400">Totebag Custom Grosir</text>
<text x="120" y="365" font-family="Georgia, serif" font-size="64" font-style="italic" fill="{RUST}">untuk Acara &amp; Korporat</text>
<text x="120" y="430" font-family="Arial, sans-serif" font-size="22" fill="#4a5568">Mulai dari 50 pcs · Kanvas, Spunbond, Furing, Drill &amp; lainnya</text>

{bag(1010, 420, 0.62, '#f0d9d2', RUST, -8) if False else ''}
<g transform="translate(1000 430) rotate(-6) scale(0.62)">
  <path d="M-70 -95C-70 -145 70 -145 70 -95" fill="none" stroke="{CHARCOAL}" stroke-width="9" stroke-linecap="round" opacity="0.85"/>
  <rect x="-110" y="-100" width="220" height="30" rx="7" fill="{OCHRE}" opacity="0.9"/>
  <rect x="-125" y="-78" width="250" height="230" rx="12" fill="#f0d9d2" stroke="{CHARCOAL}" stroke-width="2.4"/>
</g>
</svg>'''
with open(f"{OUT}/og-image.svg", "w", encoding="utf-8") as f:
    f.write(og_svg)
cairosvg.svg2png(bytestring=og_svg.encode(), write_to=f"{OUT}/og-image.png", output_width=1200, output_height=630)

print("Brand assets generated.")
