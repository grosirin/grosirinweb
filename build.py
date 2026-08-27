#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static site generator for grosir.in — produces plain, crawlable HTML
pages (good for SEO, no JS required to see content) that all share one
CSS/JS design system. Run: python3 build.py
"""
import json, os, sys, urllib.parse, hashlib

# Force UTF-8 for console output too (not just file writes below) — on
# Windows, the terminal's default codepage (e.g. cp1252) can't represent
# every character this script prints, which crashes the script with a
# UnicodeEncodeError on some machines but not others depending on locale.
# reconfigure() is available on Python 3.7+; guarded for anything older.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
WA_NUMBER = "6287714070404"  # TODO: ganti dengan nomor WhatsApp bisnis asli
SITE_URL = "https://grosir.in"  # TODO: ganti dengan domain asli saat live

with open(f"{ROOT}/assets/js/products.json", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

def _asset_version(*paths):
    """Content hash used as a cache-busting query string (?v=xxxxx) so that
    browsers/hosts don't keep serving a stale cached copy of style.css or
    main.js after a rebuild changes them — it changes automatically only
    when the file content actually changes."""
    h = hashlib.md5()
    for p in paths:
        try:
            with open(f"{ROOT}/{p}", "rb") as f:
                h.update(f.read())
        except FileNotFoundError:
            pass
    return h.hexdigest()[:8]

CSS_VERSION = _asset_version("assets/css/style.css")
JS_VERSION = _asset_version("assets/js/main.js")

def wa_href(message):
    return f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(message)}"

def fmt_idr(n):
    return "Rp " + f"{n:,.0f}".replace(",", ".")

# =================================================================
# SHARED PARTIALS
# =================================================================
NAV_ITEMS = [
    ("beranda", "Beranda", "index.html"),
    ("katalog", "Katalog", "katalog.html"),
    ("tentang", "Tentang", "tentang.html"),
    ("kontak", "Kontak", "kontak.html"),
]

def head(title, description, path, base, og_image=None, ld_list=None, noindex=False):
    canonical = f"{SITE_URL}/{path}" if path != "index.html" else f"{SITE_URL}/"
    og_image = og_image or f"{base}assets/img/og-image.png"
    og_image_abs = og_image.replace(base, f"{SITE_URL}/") if base else f"{SITE_URL}/{og_image}"
    ld_scripts = ""
    for ld in (ld_list or []):
        ld_scripts += f'\n<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    robots = '<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow">'
    return f'''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{og_image_abs}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="id_ID">
<meta property="og:site_name" content="grosir.in">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image_abs}">
<link rel="icon" type="image/svg+xml" href="{base}assets/img/favicon.svg">
<link rel="icon" type="image/png" href="{base}assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..600&family=Inter:wght@400;450;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/css/style.css?v={CSS_VERSION}">{ld_scripts}'''

def nav(active, base):
    links = ""
    for key, label, href in NAV_ITEMS:
        cls_attr = ' class="active"' if key == active else ""
        links += f'<li><a href="{base}{href}"{cls_attr} data-page="{key}">{label}</a></li>\n      '
    return f'''<nav class="nav" id="nav">
  <div class="nav-inner">
    <a class="nav-logo" href="{base}index.html">
      <img src="{base}assets/img/logomark.svg" width="24" height="24" alt="" aria-hidden="true">
      grosir.in
    </a>
    <ul class="nav-links" id="nav-links">
      {links}<li><a href="{wa_href('Halo grosir.in, saya ingin request quote totebag custom.')}" class="nav-cta" target="_blank" rel="noopener">Request Quote →</a></li>
    </ul>
    <button class="nav-toggle" id="nav-toggle" aria-label="Buka menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>'''

def footer_material_links(base):
    seen = set()
    links = []
    for p in PRODUCTS:
        if not p.get("materialCard") or p["category"] in seen:
            continue
        seen.add(p["category"])
        links.append(f'<li><a href="{base}produk/{p["slug"]}.html">{p["categoryLabel"]}</a></li>')
        if len(links) >= 6:
            break
    return "\n        ".join(links)

def footer(base):
    return f'''<footer class="footer">
  <div class="footer-grid">
    <div>
      <a href="{base}index.html" class="footer-brand">
        <img src="{base}assets/img/logomark.svg" width="22" height="22" alt="" aria-hidden="true" style="filter:invert(1) brightness(1.4)">
        grosir.in
      </a>
      <p class="footer-desc">Produsen &amp; supplier totebag custom untuk kebutuhan acara, seminar, dan merchandise korporat — grosir mulai dari 10 pcs, siap kirim ke seluruh Indonesia.</p>
    </div>
    <div>
      <h4>Navigasi</h4>
      <ul>
        <li><a href="{base}index.html">Beranda</a></li>
        <li><a href="{base}katalog.html">Katalog Produk</a></li>
        <li><a href="{base}tentang.html">Tentang Kami</a></li>
        <li><a href="{base}kontak.html">Kontak</a></li>
      </ul>
    </div>
    <div>
      <h4>Bahan Populer</h4>
      <ul>
        <!-- AUTO:FOOTERLINKS:START -->
        {footer_material_links(base)}
        <!-- AUTO:FOOTERLINKS:END -->
      </ul>
    </div>
    <div>
      <h4>Kontak</h4>
      <ul>
        <li><a href="{wa_href('Halo grosir.in, saya ingin bertanya-tanya.')}" target="_blank" rel="noopener">WhatsApp Bisnis</a></li>
        <li><a href="mailto:halo@grosir.in">halo@grosir.in</a></li>
        <li>Jakarta, Indonesia</li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">&copy; 2026 grosir.in — Totebag Custom Grosir untuk Acara &amp; Korporat.</div>
</footer>
<a class="wa-float" href="{wa_href('Halo grosir.in, saya ingin request quote totebag custom.')}" target="_blank" rel="noopener" aria-label="Chat WhatsApp">
  <svg width="28" height="28" viewBox="0 0 24 24" fill="white"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.72.45 3.4 1.3 4.88L2.05 22l5.36-1.4a9.9 9.9 0 0 0 4.63 1.18h.01c5.46 0 9.9-4.45 9.9-9.91C21.95 6.45 17.5 2 12.04 2m0 18.13h-.01a8.2 8.2 0 0 1-4.19-1.15l-.3-.18-3.12.82.84-3.04-.2-.31a8.2 8.2 0 0 1-1.27-4.36c0-4.54 3.7-8.24 8.26-8.24 2.2 0 4.27.86 5.83 2.42a8.18 8.18 0 0 1 2.41 5.83c0 4.55-3.7 8.21-8.25 8.21m4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.17.24-.64.81-.78.97-.15.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.65-1.24-1.46-1.38-1.71-.15-.24-.02-.38.11-.5.11-.11.25-.29.37-.43.12-.15.16-.25.24-.42.08-.16.04-.3-.02-.43-.06-.12-.56-1.35-.77-1.85-.2-.48-.4-.42-.56-.42-.14-.01-.31-.01-.47-.01a.9.9 0 0 0-.65.3c-.22.24-.86.84-.86 2.05s.88 2.38 1 2.54c.13.17 1.73 2.64 4.19 3.7.58.25 1.04.4 1.4.52.59.19 1.12.16 1.55.1.47-.07 1.47-.6 1.68-1.19.2-.58.2-1.08.14-1.19-.06-.1-.22-.16-.47-.28"/></svg>
</a>
<script src="{base}assets/js/main.js?v={JS_VERSION}"></script>'''

PAGE_TOP = '''<!DOCTYPE html>
<html lang="id">
<head>
{head}
</head>
<body>
<div class="scroll-progress" id="scroll-progress"></div>
{nav}
<main>
'''
PAGE_BOTTOM = '''
</main>
{footer}
</body>
</html>
'''

def page(head_html, nav_html, main_html, footer_html):
    return PAGE_TOP.format(head=head_html, nav=nav_html) + main_html + PAGE_BOTTOM.format(footer=footer_html)

def write(path, content):
    full = f"{ROOT}/{path}"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

# =================================================================
# ORGANIZATION JSON-LD (reused)
# =================================================================
ORG_LD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "grosir.in",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/assets/img/favicon.png",
    "description": "Produsen dan supplier totebag custom grosir untuk kebutuhan acara, seminar, dan merchandise korporat di Indonesia.",
    "areaServed": "ID",
    "contactPoint": [{
        "@type": "ContactPoint",
        "contactType": "sales",
        "telephone": "+" + WA_NUMBER,
        "areaServed": "ID",
        "availableLanguage": ["id"]
    }]
}

PROD_BY_SLUG = {p["slug"]: p for p in PRODUCTS}

# =================================================================
# HOME PAGE
# =================================================================
def cat_card(p, base, idx):
    return f'''<a class="cat-card reveal reveal-d{(idx % 4) + 1}" href="{base}produk/{p['slug']}.html">
  <img class="cat-icon" src="{base}assets/img/{p['image']}" width="44" height="44" alt="" aria-hidden="true">
  <h3>{p['categoryLabel']}</h3>
  <p>{p['shortDesc']}</p>
  <span class="cat-moq">MOQ {p['moq']} pcs</span>
</a>'''

def material_pills_html(products):
    seen = set()
    pills = ""
    for p in products:
        if p["category"] in seen:
            continue
        seen.add(p["category"])
        pills += f'<a class="strip-pill" href="katalog.html#{p["category"]}">{p["categoryLabel"]}</a>'
    return pills

def product_card(p, base, idx=0):
    lowest = min(p["priceTiers"], key=lambda t: t["price"])
    return f'''<a class="product-card reveal reveal-d{(idx % 4) + 1}" href="{base}produk/{p['slug']}.html" data-category="{p['category']}">
  <div class="thumb"><img src="{base}assets/img/{p['image']}" alt="{p['name']} — {p['tagline']}" loading="lazy" width="600" height="600"></div>
  <div class="body">
    <span class="tag">{p['categoryLabel']}</span>
    <h3>{p['name']}</h3>
    <p class="desc">{p['tagline']}</p>
    <div class="meta">
      <span class="price-from">Mulai dari<strong>{fmt_idr(lowest['price'])}/pcs</strong></span>
      <span class="moq-badge">MOQ {p['moq']} pcs</span>
    </div>
  </div>
</a>'''

def build_home():
    base = ""
    title = "grosir.in — Totebag Custom Grosir untuk Acara & Korporat"
    desc = "Produsen totebag custom grosir mulai 10 pcs untuk seminar, event, dan merchandise korporat. Baby Kanvas, Kanvas Natural, Blacu, Taslan, Kanvas Denim — cetak Sublim & DTF. Request quote via WhatsApp."
    ld = [ORG_LD, {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "grosir.in",
        "url": SITE_URL + "/"
    }]
    h = head(title, desc, "index.html", base, ld_list=ld)
    n = nav("beranda", base)
    f = footer(base)

    material_products = [p for p in PRODUCTS if p.get("materialCard")]
    other_products = [p for p in PRODUCTS if not p.get("materialCard")]
    cats = "\n".join(cat_card(p, base, i) for i, p in enumerate(material_products))
    featured_list = [p for p in material_products if p.get("featured")][:8]
    featured = "\n".join(product_card(p, base, i) for i, p in enumerate(featured_list))
    other = "\n".join(product_card(p, base, i) for i, p in enumerate(other_products))
    material_pills = material_pills_html(material_products)

    main = f'''<section class="hero">
  <div class="floating-shape" style="width:300px;height:300px;background:radial-gradient(circle,var(--rust),transparent 70%);top:5%;right:0%"></div>
  <div class="floating-shape" style="width:240px;height:240px;background:radial-gradient(circle,var(--sage),transparent 70%);top:55%;left:-5%;animation-delay:6s"></div>
  <div style="position:relative;z-index:1;max-width:900px">
    <div class="hero-badge"><span class="hero-badge-dot"></span>Partner Totebag Korporat &amp; Event</div>
    <h1>Totebag Custom <em>Grosir</em> untuk Acara &amp; Kebutuhan Korporat Anda</h1>
    <p class="hero-sub">
      Kami memproduksi totebag custom dalam jumlah besar — mulai dari <span class="acc acc-rust">10 pcs</span> —
      untuk goodie bag seminar, souvenir event, hingga <span class="acc acc-sage">merchandise korporat</span>.
      Bahan lengkap, harga transparan per tingkat kuantitas, dan <span class="acc acc-ochre">konsultasi desain gratis</span>.
    </p>
    <div class="hero-actions">
      <a class="btn-primary btn-wa" href="{wa_href('Halo grosir.in, saya ingin request quote totebag custom untuk kebutuhan acara/korporat.')}" target="_blank" rel="noopener">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
        <span>Request Quote via WhatsApp</span>
      </a>
      <a class="btn-secondary" href="katalog.html">
        Lihat Katalog Produk
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="9 18 15 12 9 6"/></svg>
      </a>
    </div>
    <div class="hero-trust">
      <div class="trust-item">MOQ mulai 10 pcs<span class="trust-dot" style="margin-left:8px"></span></div>
      <div class="trust-item">Custom cetak Sublim &amp; DTF<span class="trust-dot" style="margin-left:8px"></span></div>
      <div class="trust-item">Kirim ke seluruh Indonesia</div>
    </div>
  </div>
</section>

<div class="strip">
  <div class="strip-inner">
    <span class="strip-label">Bahan Tersedia</span>
    <!-- AUTO:MATERIALS:START -->
    {material_pills}
    <!-- AUTO:MATERIALS:END -->
  </div>
</div>

<section class="section" id="produk">
  <div class="section-inner">
    <span class="section-label">Pilihan Bahan</span>
    <h2 class="section-title"><span class="stw">Bahan pilihan,</span> <span class="stn">satu kualitas terjaga.</span></h2>
    <p class="section-sub">Setiap bahan kami kurasi untuk kebutuhan yang berbeda — dari souvenir massal paling ekonomis hingga merchandise korporat premium.</p>
    <!-- AUTO:CATEGORIES:START -->
    <div class="cat-grid scroll-row">
      {cats}
    </div>
    <!-- AUTO:CATEGORIES:END -->
  </div>
</section>

<section class="section section-sand">
  <div class="section-inner">
    <span class="section-label">Cara Kerja</span>
    <h2 class="section-title"><span class="stw">Proses yang</span> <span class="stn">jelas dari awal.</span></h2>
    <p class="section-sub">Empat langkah sederhana dari konsultasi kebutuhan Anda sampai totebag custom diterima di lokasi.</p>
    <div class="process-grid">
      <div class="process-step reveal reveal-d1"><div class="process-num">01</div><h3>Konsultasi &amp; Quote</h3><p>Ceritakan kebutuhan Anda (jenis acara, jumlah, budget) via WhatsApp atau form kontak, kami kirimkan estimasi harga.</p></div>
      <div class="process-step reveal reveal-d2"><div class="process-num">02</div><h3>Desain &amp; Sample</h3><p>Tim kami membuatkan mock-up desain, dan sample fisik tersedia untuk approval sebelum produksi massal.</p></div>
      <div class="process-step reveal reveal-d3"><div class="process-num">03</div><h3>Produksi Massal</h3><p>Setelah desain disetujui, produksi berjalan sesuai linimasa yang disepakati dengan quality check berkala.</p></div>
      <div class="process-step reveal reveal-d4"><div class="process-num">04</div><h3>Pengiriman</h3><p>Totebag dikemas rapi dan dikirim ke lokasi Anda di seluruh Indonesia, siap dipakai untuk acara.</p></div>
    </div>
  </div>
</section>

<section class="stats-bar">
  <div class="stats-inner">
    <div class="stat"><div class="stat-num"><span>500+</span></div><div class="stat-lbl">Perusahaan &amp; event terlayani</div></div>
    <div class="stat"><div class="stat-num"><span>50rb+</span></div><div class="stat-lbl">Totebag diproduksi / bulan</div></div>
    <div class="stat"><div class="stat-num"><span>8</span></div><div class="stat-lbl">Tahun pengalaman produksi</div></div>
    <div class="stat"><div class="stat-num"><span>20+</span></div><div class="stat-lbl">Kota pengiriman di Indonesia</div></div>
  </div>
</section>

<section class="section">
  <div class="section-inner">
    <span class="section-label">Produk Pilihan</span>
    <h2 class="section-title"><span class="stw">Paling banyak</span> <span class="stn">dipesan klien kami.</span></h2>
    <!-- AUTO:FEATURED:START -->
    <div class="product-grid scroll-row">
      {featured}
    </div>
    <!-- AUTO:FEATURED:END -->
    <div style="text-align:center;margin-top:48px">
      <a class="btn-secondary" href="katalog.html">Lihat Semua Produk<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="9 18 15 12 9 6"/></svg></a>
    </div>
  </div>
</section>

<section class="section section-sand">
  <div class="section-inner">
    <span class="section-label">Produk Lainnya</span>
    <h2 class="section-title"><span class="stw">Pelengkap</span> <span class="stn">di luar totebag utama.</span></h2>
    <p class="section-sub">Aksesori tambahan dari bahan yang sama — cocok sebagai pelengkap goodie bag atau merchandise kecil.</p>
    <!-- AUTO:OTHERPRODUCTS:START -->
    <div class="product-grid scroll-row">
      {other}
    </div>
    <!-- AUTO:OTHERPRODUCTS:END -->
  </div>
</section>

<section class="section">
  <div class="section-inner">
    <span class="section-label">Testimoni</span>
    <h2 class="section-title"><span class="stw">Kata mereka</span> <span class="stn">yang sudah pesan.</span></h2>
    <div class="testi-grid">
      <div class="testi-card"><div class="quote-mark">"</div><p>Tempatkan kutipan testimoni asli dari klien Anda di sini setelah proyek pertama selesai.</p><div class="testi-who"><div class="testi-avatar">?</div><div><div class="testi-name">Nama Klien</div><div class="testi-role">Jabatan, Nama Perusahaan</div></div></div></div>
      <div class="testi-card"><div class="quote-mark">"</div><p>Tempatkan kutipan testimoni asli dari klien Anda di sini setelah proyek pertama selesai.</p><div class="testi-who"><div class="testi-avatar">?</div><div><div class="testi-name">Nama Klien</div><div class="testi-role">Jabatan, Nama Perusahaan</div></div></div></div>
      <div class="testi-card"><div class="quote-mark">"</div><p>Tempatkan kutipan testimoni asli dari klien Anda di sini setelah proyek pertama selesai.</p><div class="testi-who"><div class="testi-avatar">?</div><div><div class="testi-name">Nama Klien</div><div class="testi-role">Jabatan, Nama Perusahaan</div></div></div></div>
    </div>
    <p class="testi-note">*Placeholder — ganti dengan testimoni nyata dari klien Anda sebelum situs ini dipublikasikan.</p>
  </div>
</section>

<section class="cta-section">
  <h2>Siap pesan totebag custom untuk <em>tim atau acara Anda</em>?</h2>
  <p class="cta-sub">Konsultasikan kebutuhan Anda sekarang — tim kami siap membantu memilih bahan, desain, dan kuantitas yang tepat.</p>
  <div class="cta-actions">
    <a class="btn-primary btn-wa" href="{wa_href('Halo grosir.in, saya ingin request quote totebag custom.')}" target="_blank" rel="noopener"><span>Chat via WhatsApp</span></a>
    <a class="btn-secondary" href="kontak.html">Isi Form Kontak</a>
  </div>
</section>
'''
    write("index.html", page(h, n, main, f))

build_home()

# =================================================================
# KATALOG PAGE
# =================================================================
def build_katalog():
    base = ""
    title = "Katalog Totebag Custom Grosir — Baby Kanvas, Kanvas Natural, Blacu, Taslan, Denim | grosir.in"
    desc = "Jelajahi katalog lengkap totebag custom grosir.in: Baby Kanvas, Kanvas Natural, Blacu, Taslan, Kanvas Denim. Cetak Sublim & DTF. Harga bertingkat per kuantitas, MOQ mulai 10 pcs."
    ld = [ORG_LD, {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Beranda", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Katalog", "item": SITE_URL + "/katalog.html"}
        ]
    }, {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{SITE_URL}/produk/{p['slug']}.html", "name": p["name"]}
            for i, p in enumerate(PRODUCTS)
        ]
    }]
    h = head(title, desc, "katalog.html", base, ld_list=ld)
    n = nav("katalog", base)
    f = footer(base)

    chips = '<button class="filter-chip active" data-filter="all">Semua</button>'
    seen = set()
    for p in PRODUCTS:
        if p["category"] in seen:
            continue
        seen.add(p["category"])
        chips += f'\n      <button class="filter-chip" data-filter="{p["category"]}">{p["categoryLabel"]}</button>'
    cards = "\n".join(product_card(p, base, i) for i, p in enumerate(PRODUCTS))

    main = f'''<div class="page-hero">
  <div class="breadcrumb"><a href="index.html">Beranda</a><span>/</span><span>Katalog</span></div>
  <span class="eyebrow">Katalog Produk</span>
  <h1>Semua bahan totebag, <em>satu tempat pemesanan.</em></h1>
  <p>Bandingkan bahan, MOQ, dan harga per tingkat kuantitas. Klik salah satu produk untuk melihat detail spesifikasi dan menghitung estimasi harga sesuai jumlah pesanan Anda.</p>
</div>
<div class="section-inner" style="padding:0 32px 100px;max-width:1200px;margin:0 auto">
  <!-- AUTO:FILTERS:START -->
  <div class="filter-bar">
    {chips}
  </div>
  <!-- AUTO:FILTERS:END -->
  <!-- AUTO:PRODUCTS:START -->
  <div class="product-grid">
    {cards}
  </div>
  <!-- AUTO:PRODUCTS:END -->
</div>
<section class="cta-section" style="padding-top:40px">
  <h2>Tidak yakin bahan mana yang <em>paling cocok</em>?</h2>
  <p class="cta-sub">Ceritakan kebutuhan acara atau brand Anda, tim kami akan membantu merekomendasikan bahan dan estimasi budget yang sesuai.</p>
  <div class="cta-actions">
    <a class="btn-primary btn-wa" href="{wa_href('Halo grosir.in, saya butuh rekomendasi bahan totebag yang cocok untuk kebutuhan saya.')}" target="_blank" rel="noopener"><span>Konsultasi via WhatsApp</span></a>
  </div>
</section>
'''
    write("katalog.html", page(h, n, main, f))

build_katalog()

# =================================================================
# PRODUCT DETAIL PAGES
# =================================================================
CHECK_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>'

def related_products(current_slug, n=4):
    cur = PROD_BY_SLUG[current_slug]
    same_cat = [p for p in PRODUCTS if p["slug"] != current_slug and p["category"] == cur["category"]]
    others = [p for p in PRODUCTS if p["slug"] != current_slug and p["category"] != cur["category"]]
    return (same_cat + others)[:n]

def overall_lowest_price(p):
    """Lowest price across every quantity tier AND (if present) every
    Warna/Ukuran variant — used for the schema.org 'starting from' price so
    it stays accurate for products with variant-specific pricing."""
    tier_lists = [o["priceTiers"] for o in p.get("variants", {}).get("options", [])] or [p["priceTiers"]]
    return min(t["price"] for tiers in tier_lists for t in tiers)

def specs_html(p):
    """Render the four spec boxes (Bahan / Ukuran / Warna / Metode Print).
    Ukuran and Warna become interactive <select> dropdowns — populated with
    real option text server-side so they work even without JS — for any
    product that has vendor-driven variants; other products keep the plain
    text value unchanged."""
    variants = p.get("variants")
    parts = []
    for k, v in p["specs"].items():
        if variants and k == "Warna":
            opts = "\n".join(
                f'<option value="{c}"{" selected" if i == 0 else ""}>{c}</option>'
                for i, c in enumerate(variants["colors"])
            )
            parts.append(f'<label class="pd-spec pd-spec-select" for="pd-warna-select"><span class="pd-spec-lbl">{k}</span><select class="pd-select" id="pd-warna-select" aria-label="Pilih warna">{opts}</select></label>')
        elif variants and k == "Ukuran":
            default_color = variants["colors"][0]
            sizes = [o["ukuran"] for o in variants["options"] if o["warna"] == default_color]
            opts = "\n".join(
                f'<option value="{s}"{" selected" if i == 0 else ""}>{s}</option>'
                for i, s in enumerate(sizes)
            )
            parts.append(f'<label class="pd-spec pd-spec-select" for="pd-ukuran-select"><span class="pd-spec-lbl">{k}</span><select class="pd-select" id="pd-ukuran-select" aria-label="Pilih ukuran">{opts}</select></label>')
        else:
            parts.append(f'<div class="pd-spec"><div class="pd-spec-lbl">{k}</div><div class="pd-spec-val">{v}</div></div>')
    return "\n".join(parts)

def build_product_page(p):
    base = "../"
    title = f"{p['name']} Custom Grosir — MOQ {p['moq']} pcs | grosir.in"
    desc = p["shortDesc"]
    lowest_price = overall_lowest_price(p)
    canonical_path = f"produk/{p['slug']}.html"
    ld = [{
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["name"],
        "description": p["longDesc"],
        "sku": p["slug"],
        "category": p["categoryLabel"],
        "image": f"{SITE_URL}/assets/img/{p['image']}",
        "brand": {"@type": "Brand", "name": "grosir.in"},
        "offers": {
            "@type": "Offer",
            "priceCurrency": "IDR",
            "price": str(lowest_price),
            "priceValidUntil": "2026-12-31",
            "availability": "https://schema.org/InStock",
            "url": f"{SITE_URL}/{canonical_path}",
            "eligibleQuantity": {"@type": "QuantitativeValue", "minValue": p["moq"], "unitCode": "C62"}
        }
    }, {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Beranda", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Katalog", "item": SITE_URL + "/katalog.html"},
            {"@type": "ListItem", "position": 3, "name": p["name"], "item": f"{SITE_URL}/{canonical_path}"}
        ]
    }]
    h = head(title, desc, canonical_path, base, og_image=f"{base}assets/img/{p['image']}", ld_list=ld)
    n = nav("katalog", base)
    f = footer(base)

    thumbs = "\n".join(
        f'<div class="pd-thumb{" active" if i == 0 else ""}"><img src="{base}assets/img/{img}" alt="{p["name"]} tampilan {i+1}" width="76" height="76"></div>'
        for i, img in enumerate(p["gallery"])
    )
    specs = specs_html(p)
    tier_rows = "\n".join(
        f'<tr><td>{t["min"]}+ pcs</td><td class="price">{fmt_idr(t["price"])}/pcs</td></tr>'
        for t in p["priceTiers"]
    )
    customize = "\n".join(f'<div class="ci">{CHECK_SVG}<span>{c}</span></div>' for c in p["customize"])
    tiers_json = json.dumps(p["priceTiers"])
    variants_attr = f" data-variants='{json.dumps(p['variants'], ensure_ascii=False)}'" if p.get("variants") else ""
    related = related_products(p["slug"])
    related_html = "\n".join(product_card(rp, base, i) for i, rp in enumerate(related))

    main = f'''<div class="page-hero" style="padding-bottom:0">
  <div class="breadcrumb"><a href="{base}index.html">Beranda</a><span>/</span><a href="{base}katalog.html">Katalog</a><span>/</span><span>{p['name']}</span></div>
</div>
<div class="pd-grid">
  <div>
    <div class="pd-gallery-main"><img src="{base}assets/img/{p['gallery'][0]}" alt="{p['name']} — {p['tagline']}" width="700" height="700"></div>
    <div class="pd-thumbs">{thumbs}</div>
  </div>
  <div data-product="{p['name']}" data-tiers='{tiers_json}' data-moq="{p['moq']}"{variants_attr}>
    <span class="pd-tag">{p['categoryLabel']}</span>
    <h1 class="pd-title">{p['name']}</h1>
    <p class="pd-desc">{p['longDesc']}</p>
    <div class="pd-specs">
      {specs}
    </div>
    <div class="pd-tiers">
      <h4>Harga Bertingkat per Kuantitas</h4>
      <table class="tier-table">
        <thead><tr><th>Jumlah Pesanan</th><th>Harga / pcs</th></tr></thead>
        <tbody>{tier_rows}</tbody>
      </table>
    </div>
    <div class="qty-box">
      <div class="qty-stepper">
        <button type="button" class="qty-minus" aria-label="Kurangi">−</button>
        <input type="number" class="qty-input" value="{p['moq']}" min="{p['moq']}" step="10" aria-label="Jumlah pcs">
        <button type="button" class="qty-plus" aria-label="Tambah">+</button>
      </div>
      <div class="qty-est">Estimasi total <strong class="qty-est-value">-</strong><br><span class="qty-est-unit"></span></div>
    </div>
    <h4 style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--text-tertiary);margin-bottom:12px">Opsi Kustomisasi</h4>
    <div class="pd-customize">
      {customize}
    </div>
    <div class="pd-actions">
      <a class="btn-primary btn-wa qty-wa-btn" href="{wa_href('Halo grosir.in')}" target="_blank" rel="noopener">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
        <span>Request Quote via WhatsApp</span>
      </a>
      <a class="btn-secondary" href="{base}katalog.html">Lihat Produk Lain</a>
    </div>
  </div>
</div>

<section class="section section-sand" style="padding-top:70px">
  <div class="section-inner">
    <span class="section-label">Mungkin Anda Suka</span>
    <h2 class="section-title"><span class="stw">Bahan lain</span> <span class="stn">yang sering dipadukan.</span></h2>
    <div class="related-grid">
      {related_html}
    </div>
  </div>
</section>
'''
    write(canonical_path, page(h, n, main, f))

def clean_stale_product_pages():
    """Remove produk/*.html files left over from products that were since
    deleted from products.json, so a removed product doesn't stay reachable
    at its old URL forever."""
    valid = {f"{p['slug']}.html" for p in PRODUCTS}
    produk_dir = f"{ROOT}/produk"
    if not os.path.isdir(produk_dir):
        return
    for fname in os.listdir(produk_dir):
        if fname.endswith(".html") and fname not in valid:
            os.remove(f"{produk_dir}/{fname}")
            print("removed stale product page:", fname)

clean_stale_product_pages()
for _p in PRODUCTS:
    build_product_page(_p)

# =================================================================
# TENTANG (ABOUT) PAGE
# =================================================================
def build_tentang():
    base = ""
    title = "Tentang grosir.in — Produsen Totebag Custom Grosir Indonesia"
    desc = "Kenali grosir.in, produsen totebag custom untuk kebutuhan acara dan korporat. Fokus pada kualitas konsisten, transparansi harga, dan layanan konsultatif."
    ld = [ORG_LD, {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Beranda", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Tentang", "item": SITE_URL + "/tentang.html"}
        ]
    }]
    h = head(title, desc, "tentang.html", base, ld_list=ld)
    n = nav("tentang", base)
    f = footer(base)

    main = f'''<div class="page-hero">
  <div class="breadcrumb"><a href="index.html">Beranda</a><span>/</span><span>Tentang</span></div>
  <span class="eyebrow">Tentang Kami</span>
  <h1>Fokus pada satu hal: <em>totebag grosir yang bisa diandalkan.</em></h1>
  <p>Kami tidak melayani pembelian satuan — seluruh proses produksi, tim, dan kapasitas kami dirancang khusus untuk memenuhi pesanan dalam jumlah besar bagi perusahaan dan penyelenggara acara.</p>
</div>

<div class="about-grid">
  <div class="about-body">
    <p class="reveal">grosir.in berawal dari kebutuhan sederhana yang sering luput diperhatikan: banyak perusahaan dan event organizer kesulitan menemukan <strong>supplier totebag yang bisa diajak bicara soal spesifikasi teknis</strong> — bahan, gramasi, metode cetak — bukan sekadar menerima katalog template.</p>
    <p class="reveal">Kami memutuskan untuk fokus melayani <strong>kebutuhan grosir saja</strong>: goodie bag seminar, souvenir konferensi, merchandise korporat, hingga totebag campaign brand. Dengan fokus ini, kami bisa menjaga MOQ tetap rendah (mulai 10 pcs) sambil tetap memberi harga bertingkat yang kompetitif untuk volume besar.</p>
    <p class="reveal">Setiap pesanan melalui proses yang sama: konsultasi kebutuhan, approval desain &amp; sample fisik, produksi terjadwal dengan quality check, lalu pengiriman ke lokasi Anda. Transparan dari awal, tanpa biaya tersembunyi.</p>
    <div class="capability-grid">
      <div class="cap-card reveal reveal-d1"><div class="cap-num">50rb+</div><div class="cap-lbl">Kapasitas produksi / bulan</div></div>
      <div class="cap-card reveal reveal-d2"><div class="cap-num">7–14</div><div class="cap-lbl">Hari rata-rata waktu produksi*</div></div>
      <div class="cap-card reveal reveal-d3"><div class="cap-num">20+</div><div class="cap-lbl">Kota pengiriman di Indonesia</div></div>
    </div>
    <p style="font-size:12px;color:var(--text-tertiary)">*Estimasi, tergantung kompleksitas desain dan jumlah pesanan — dikonfirmasi saat quote.</p>
  </div>
  <div>
    <img src="assets/img/hero-illustration.svg" alt="Ilustrasi stok totebag grosir.in" style="border-radius:12px;border:.5px solid var(--border);margin-bottom:32px">
    <div class="values-list">
      <div class="value-item"><div class="value-title">Kualitas Konsisten</div><div class="value-desc">Setiap batch produksi melalui quality check bahan dan jahitan sebelum dikirim.</div></div>
      <div class="value-item"><div class="value-title">Transparansi Harga</div><div class="value-desc">Harga bertingkat per kuantitas ditampilkan terbuka, tanpa negosiasi berlapis.</div></div>
      <div class="value-item"><div class="value-title">Layanan Konsultatif</div><div class="value-desc">Tim kami membantu memilih bahan &amp; metode cetak sesuai budget dan tujuan acara.</div></div>
      <div class="value-item"><div class="value-title">Linimasa Jelas</div><div class="value-desc">Estimasi waktu produksi disepakati di awal dan dipantau hingga pengiriman.</div></div>
    </div>
  </div>
</div>

<section class="cta-section" style="padding-top:20px">
  <h2>Mari diskusikan <em>kebutuhan totebag</em> Anda.</h2>
  <p class="cta-sub">Tim kami siap membantu dari tahap perencanaan hingga totebag siap dipakai di acara Anda.</p>
  <div class="cta-actions">
    <a class="btn-primary btn-wa" href="{wa_href('Halo grosir.in, saya ingin tahu lebih lanjut tentang layanan Anda.')}" target="_blank" rel="noopener"><span>Chat via WhatsApp</span></a>
    <a class="btn-secondary" href="katalog.html">Lihat Katalog Produk</a>
  </div>
</section>
'''
    write("tentang.html", page(h, n, main, f))

build_tentang()

# =================================================================
# KONTAK PAGE
# =================================================================
FAQS = [
    ("Berapa minimum order (MOQ) untuk totebag custom?", "MOQ untuk semua bahan kami mulai dari 10 pcs, jadi Anda bisa memesan dalam jumlah kecil maupun besar. Harga per pcs semakin turun seiring bertambahnya jumlah pesanan — detail harga bertingkat setiap bahan tersedia di halaman katalog."),
    ("Berapa lama waktu produksi?", "Rata-rata 7–14 hari kerja tergantung kompleksitas desain, metode cetak, dan jumlah pesanan. Estimasi pasti akan diinformasikan saat Anda request quote."),
    ("Apakah bisa membuat sample sebelum produksi massal?", "Bisa. Untuk pesanan dalam jumlah besar, kami menyediakan sample fisik terlebih dahulu untuk approval sebelum produksi massal dijalankan."),
    ("Metode cetak apa saja yang tersedia?", "Kami hanya melayani dua metode cetak: Sublim (sublimasi full color) dan DTF (Direct to Film). Kirimkan logo/desain Anda dalam format vector atau gambar resolusi tinggi, dan tim kami akan membantu menyesuaikannya dengan bahan yang dipilih."),
    ("Apakah melayani pengiriman ke luar kota?", "Ya, kami melayani pengiriman ke seluruh Indonesia menggunakan ekspedisi rekanan, dengan opsi pengambilan langsung di lokasi produksi untuk area Jabodetabek."),
]

def build_kontak():
    base = ""
    title = "Kontak & Request Quote Totebag Custom — grosir.in"
    desc = "Hubungi grosir.in untuk konsultasi dan request quote totebag custom grosir. Respons cepat via WhatsApp, atau isi form kebutuhan Anda."
    ld = [ORG_LD, {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Beranda", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Kontak", "item": SITE_URL + "/kontak.html"}
        ]
    }, {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQS
        ]
    }]
    h = head(title, desc, "kontak.html", base, ld_list=ld)
    n = nav("kontak", base)
    f = footer(base)

    plus_svg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>'
    material_options = "\n".join(f'<option value="{p["categoryLabel"]}">{p["categoryLabel"]}</option>' for p in PRODUCTS)
    faq_html = "\n".join(f'''<div class="faq-item">
      <div class="faq-q"><span>{q}</span>{plus_svg}</div>
      <div class="faq-a"><p>{a}</p></div>
    </div>''' for q, a in FAQS)

    main = f'''<div class="page-hero">
  <div class="breadcrumb"><a href="index.html">Beranda</a><span>/</span><span>Kontak</span></div>
  <span class="eyebrow">Kontak</span>
  <h1>Ceritakan kebutuhan Anda, <em>kami siapkan quote-nya.</em></h1>
  <p>Isi form di bawah atau langsung chat WhatsApp — tim kami biasanya merespons dalam hitungan jam pada hari kerja.</p>
</div>

<div class="contact-grid">
  <div class="contact-form-card">
    <h2>Form Request Quote</h2>
    <p>Semakin detail informasi yang Anda berikan, semakin akurat estimasi harga yang bisa kami siapkan.</p>
    <form id="quote-form">
      <div class="form-group">
        <label class="form-label" for="nama">Nama Lengkap</label>
        <input class="form-input" type="text" id="nama" name="nama" placeholder="Nama Anda" required>
      </div>
      <div class="form-group">
        <label class="form-label" for="perusahaan">Nama Perusahaan / Event</label>
        <input class="form-input" type="text" id="perusahaan" name="perusahaan" placeholder="PT / Instansi / Nama Acara">
      </div>
      <div class="form-group">
        <label class="form-label" for="kebutuhan">Bahan yang Diminati</label>
        <select class="form-select" id="kebutuhan" name="kebutuhan">
          <option value="Belum tahu / minta rekomendasi">Belum tahu / minta rekomendasi</option>
          {material_options}
        </select>
      </div>
      <div class="form-group">
        <label class="form-label" for="jumlah">Estimasi Jumlah (pcs)</label>
        <input class="form-input" type="number" id="jumlah" name="jumlah" placeholder="Contoh: 200" min="1">
      </div>
      <div class="form-group">
        <label class="form-label" for="pesan">Detail Kebutuhan</label>
        <textarea class="form-textarea" id="pesan" name="pesan" placeholder="Ceritakan jenis acara, tenggat waktu, atau desain yang diinginkan..."></textarea>
      </div>
      <button type="submit" class="btn-primary btn-wa">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
        <span>Kirim via WhatsApp</span>
      </button>
    </form>
  </div>
  <div class="contact-sidebar">
    <h3>Status</h3>
    <div class="info-card">
      <div class="info-status"><span class="info-dot"></span> Online — biasanya balas dalam 1 jam</div>
      <div class="info-text">Jam operasional: Senin–Sabtu, 09.00–18.00 WIB</div>
    </div>
    <h3>Hubungi Langsung</h3>
    <div class="social-l">
      <a class="soc-link" href="{wa_href('Halo grosir.in, saya ingin bertanya-tanya.')}" target="_blank" rel="noopener">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
        WhatsApp Bisnis
      </a>
      <a class="soc-link" href="mailto:halo@grosir.in">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>
        halo@grosir.in
      </a>
      <a class="soc-link" href="https://instagram.com/grosir.in" target="_blank" rel="noopener">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="3.5"/><circle cx="17.5" cy="6.5" r="1"/></svg>
        @grosir.in
      </a>
    </div>
    <h3>Pertanyaan Umum</h3>
    <div>
      {faq_html}
    </div>
  </div>
</div>
'''
    write("kontak.html", page(h, n, main, f))

build_kontak()

# =================================================================
# SITEMAP.XML + ROBOTS.TXT
# =================================================================
def build_sitemap_robots():
    urls = ["", "katalog.html", "tentang.html", "kontak.html"]
    urls += [f"produk/{p['slug']}.html" for p in PRODUCTS]
    items = "\n".join(
        f'  <url><loc>{SITE_URL}/{u}</loc><changefreq>weekly</changefreq><priority>{"1.0" if u == "" else "0.8"}</priority></url>'
        for u in urls
    )
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>
'''
    write("sitemap.xml", sitemap)

    robots = f'''User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
'''
    write("robots.txt", robots)

build_sitemap_robots()

print("\nBuild complete —", len(PRODUCTS), "product pages generated.")
print("Remember to update WA_NUMBER and SITE_URL at the top of build.py before going live,")
print("then re-run: python3 build.py")
