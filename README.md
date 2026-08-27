# grosir.in — Website Totebag Custom Grosir

Website statis (HTML/CSS/JS polos, tanpa framework) untuk toko totebag custom
grosir. Dibangun agar cepat, mobile-friendly, dan ramah SEO (setiap halaman
adalah file HTML nyata dengan meta tag & data terstruktur sendiri — bukan
single-page app).

## Struktur folder

```
index.html          Beranda
katalog.html         Katalog semua produk (bisa difilter per bahan)
tentang.html          Tentang kami
kontak.html            Form kontak + FAQ
produk/*.html          8 halaman detail produk (1 per bahan)
assets/css/style.css   Semua styling (satu file, dipakai semua halaman)
assets/js/main.js       Semua interaksi (cursor, menu mobile, kalkulator
                       harga, filter katalog, form -> WhatsApp)
assets/js/products.json Data semua produk (nama, harga, MOQ, spesifikasi)
assets/img/              Semua ilustrasi placeholder (SVG) + favicon + og-image
sitemap.xml, robots.txt  Untuk SEO / Google Search Console
build.py                Script generator — MENGHASILKAN semua file .html di atas
gen_assets.py            Script generator ilustrasi produk (SVG)
gen_brand.py             Script generator favicon/logo/hero/og-image
admin.html               Product Manager — kelola produk TANPA Python/JSON manual (lihat di bawah)
```

## Cara termudah kelola produk: admin.html (tidak perlu Python)

Buka file **`admin.html`** dengan cara diklik dua kali (akan terbuka di browser
Anda) — pakai **Google Chrome atau Microsoft Edge** untuk pengalaman penuh.
Klik "Buka Folder Website", pilih folder situs ini, lalu Anda bisa menambah,
mengubah, atau menghapus produk lewat form biasa — termasuk mengunggah foto.
Begitu klik Simpan, semua file yang perlu berubah (halaman produk, katalog,
beranda, sitemap) langsung ditulis ulang otomatis ke folder Anda. Tidak ada
JSON untuk diedit manual, tidak ada perintah `python3 build.py` untuk
dijalankan lagi — cukup unggah ulang folder ke hosting Anda setelah selesai.

**Penting:** `admin.html` adalah alat internal untuk Anda, bukan bagian dari
website publik — simpan di komputer Anda saja dan jangan ikut diunggah ke
hosting bersama file situs lainnya.

Kalau browser Anda bukan Chrome/Edge (mis. Safari/Firefox belum mendukung
fitur ini), `admin.html` otomatis menawarkan mode alternatif: Anda tetap
mengisi form yang sama, tapi hasilnya berupa file `products.json` (dan foto,
jika ada) yang terunduh untuk Anda pindahkan manual ke folder situs, lalu
jalankan `python3 build.py` satu kali seperti biasa.

Bagian di bawah ini (`build.py` + `products.json`) tetap didokumentasikan
untuk siapa pun yang lebih suka mengedit langsung / butuh kontrol penuh.

## Hal pertama yang WAJIB diganti sebelum live

1. **Nomor WhatsApp** — buka `build.py`, ganti nilai `WA_NUMBER` di baris atas
   (format `62xxxxxxxxxx`, tanpa tanda `+`).
2. **Domain asli** — ganti `SITE_URL` di `build.py` dari `https://grosir.in`
   ke domain Anda yang sebenarnya (dipakai untuk canonical URL, sitemap, dan
   data Open Graph).
3. Setelah mengubah salah satu di atas, jalankan ulang:
   ```
   python3 build.py
   ```
   Semua halaman HTML akan otomatis dibuat ulang dengan data baru — tidak
   perlu edit HTML satu per satu.

## Mengubah produk / harga / MOQ

Edit `assets/js/products.json` (nama, deskripsi, MOQ, harga bertingkat,
spesifikasi, opsi kustomisasi), lalu jalankan `python3 build.py`. Halaman
katalog dan halaman detail produk akan mengikuti otomatis.

### Menambah produk baru

Tambahkan satu object baru di `products.json` mengikuti format yang sudah
ada, siapkan gambarnya di `assets/img/` (atau jalankan `gen_assets.py` untuk
membuat ilustrasi placeholder baru — tambahkan entri ke daftar `PRODUCTS` di
file itu dulu), lalu jalankan `python3 build.py`. Halaman detail produk baru
otomatis dibuat di `produk/`, dan otomatis muncul di katalog + sitemap.

### Menghapus produk

Hapus object produk tersebut dari `products.json`, lalu jalankan
`python3 build.py`. Script otomatis menghapus juga file halaman lamanya di
`produk/` (jadi URL produk yang sudah dihapus tidak nyangkut lagi) — Anda
tidak perlu menghapus file HTML manapun secara manual.

## Mengganti gambar placeholder dengan foto asli

Semua gambar produk saat ini adalah ilustrasi SVG buatan (bukan foto asli)
agar identitas visual situs tetap konsisten sebelum Anda punya foto produk.
Untuk mengganti dengan foto asli: cukup timpa file di `assets/img/` dengan
nama file yang sama persis (lihat field `image` dan `gallery` di
`products.json`), format JPG/PNG/WebP juga didukung — tidak perlu ubah HTML.

## Konten yang masih placeholder — ganti sebelum publish

- **Testimoni** di beranda (`index.html`, bagian "Testimoni") — ganti kutipan
  & nama placeholder dengan testimoni asli dari klien Anda.
- **Statistik** (500+ perusahaan, 50rb+ totebag/bulan, dll.) di beranda dan
  halaman Tentang — sesuaikan dengan angka riil bisnis Anda.
- **Alamat, email, Instagram** di footer & halaman Kontak.

## Menjalankan / preview secara lokal

```
python3 -m http.server 8000
```
lalu buka `http://localhost:8000` di browser.

## Deploy

Ini website statis murni — tinggal unggah seluruh isi folder ini (kecuali
file `.py`) ke hosting statis mana pun: Netlify, Vercel, GitHub Pages,
cPanel, dsb. Tidak perlu server backend atau database.

## SEO checklist setelah live

- Submit `sitemap.xml` ke Google Search Console.
- Pastikan `SITE_URL` di `build.py` sudah domain asli sebelum build terakhir.
- Isi testimoni & statistik asli (lihat bagian di atas) — mesin pencari dan
  calon klien sama-sama lebih percaya data yang nyata.
