# grosir.in — output repo

Repo ini berisi **hasil generate** situs https://grosir.in dan tidak lain.
GitHub Pages melayani isinya apa adanya, dengan domain kustom lewat `CNAME`.

> **Jangan mengedit file apa pun di sini secara manual.**
> Semua `.html`, `sitemap.xml`, dan `robots.txt` dibuat ulang dari nol oleh
> generator di repo sumber. Perubahan yang diketik langsung di sini akan hilang
> pada promosi berikutnya, tanpa peringatan.

## Cara mengubah isi situs

Sumber dan seluruh tooling-nya ada di **repo privat terpisah**. Alurnya:

1. Ubah sumbernya di repo privat (data produk, artikel, atau template).
2. Jalankan generator di sana untuk membuat ulang semua halaman.
3. Catat perubahannya di `CHANGELOG.md` repo privat.
4. Buka PR ke repo ini berisi **hanya file hasil generate**.

PR itulah satu-satunya gerbang persetujuan sebelum sesuatu tayang.
Jangan pernah push langsung ke `main`.

## Yang ada di sini

```
index.html  katalog.html  tentang.html  kontak.html
artikel.html  artikel/*.html
produk/*.html
assets/css/  assets/js/  assets/img/
sitemap.xml  robots.txt
CNAME  LICENSE
```

## Yang sengaja TIDAK ada di sini

Generator (`build.py`, `gen_*.py`), product manager internal (`admin.html`),
sumber data (`products.json`, `articles.json`), ledger sitemap
(`lastmod.json`), dan tool invoicing lokal — semuanya tinggal di repo privat.

Dua di antaranya penting alasannya:

- **`admin.html`** adalah alat harga internal. Kalau ikut terunggah, ia bisa
  diakses siapa pun di domain publik.
- **Tool invoicing** memuat data klien nyata (nama, telepon, alamat kirim).
  Isinya tidak pernah boleh menyentuh repo publik, dalam bentuk apa pun.

## Domain

`grosir.in` sudah aktif: GitHub Pages + `CNAME`, DNS di Namecheap.
**Jangan mengubah atau menghapus file `CNAME`** — situs akan lepas dari
domainnya. Begitu juga pengaturan custom domain di Settings → Pages.
