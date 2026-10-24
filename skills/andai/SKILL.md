---
name: andai
description: Membuat video kartun narasi vertikal (TikTok/Reels/Shorts) berformat "Andai besok…". Cerita orang kedua yang bolak-balik antara Dunia Andai (ideal, hangat) dan Dunia Nyata (fakta + data bersumber), berjalan dari pagi ke malam, ditutup twist yang berbalik ke penonton dan akhir yang berputar (loop). Mencakup riset fakta, naskah, storyboard, voice-over, caption per kata, render, dan QA. Gunakan saat pengguna minta video/konten edukasi atau satire sosial bergaya "bayangkan kalau…", "andai…", "dunia tanpa…", explainer kartun dengan narasi, atau menyebut ANDAI. Use for Indonesian narrated cartoon explainer videos in a what-if / counterfactual format. Jangan dipakai untuk edit vlog atau footage biasa.
---

# ANDAI: video kartun narasi "dunia seandainya"

> **Status: DRAF.** Dokumen panduan dan skema sudah lengkap; engine (`python -m andai …`) belum
> dibangun. Visualnya 3D yang dibangun dari kode (three.js); prototipenya ada di
> `andai/scene3d/prototipe/`. Sampai engine ada, jalankan Tahap 0–3 (sampai storyboard), lalu beri tahu pengguna bahwa
> tahap audio dan render belum tersedia. Lihat `ROADMAP.md`.

## Konsep singkat

"Andai besok pagi kamu bangun, dan [masalah sehari-hari] hilang." Narator mengajak "kamu" menjalani satu
hari di dunia itu. Setiap kenyamanan di Dunia Andai dipasangkan dengan fakta Dunia Nyata. Fakta tampil
sebagai benda di dunia cerita, dengan skala yang naik terus. Malamnya, si Kamu sendiri tergoda melakukan
kebiasaan lama, dan dunia baru tidak mengenalnya. Video ditutup kalimat menggantung yang tersambung
kembali ke awal.

## Aturan emas (selalu berlaku)

1. Kalimat pertama di detik 0. Tanpa intro, salam, atau judul.
2. Enam pilar wajib ada: orang kedua, dua dunia, satu hari, fakta jadi benda, twist cermin, akhir loop.
3. **Jangan mengarang angka.** Setiap angka butuh sumber + tahun di `fakta.yaml`. Belum ada sumber →
   tulis `[[PERLU SUMBER]]` dan berhenti di Gerbang 1.
4. Sebut peran, bukan nama orang. Tanpa logo/lambang lembaga asli. Tanpa desain uang rupiah asli.
5. Tiru format dan teknik referensi, bukan aset atau kalimat khasnya.
6. Caption satu kata, angka ditulis kata. Digit hanya muncul di prop.
7. Shot dijangkarkan ke kata di naskah, bukan ke detik.

## Alur kerja

Kerjakan berurutan. Di setiap ◆ gerbang, serahkan hasil dan tunggu persetujuan pengguna (kecuali
pengguna meminta melompati gerbang; Gerbang 1 tetap wajib jika ada angka tanpa sumber).

### Tahap 0: Brief
- Tanyakan atau simpulkan: topik (masalah yang "hilang"), kebiasaan untuk twist, aksi penutup, preset
  durasi (`pendek` ±60 dtk / `standar` ±90 dtk / `panjang` ±150 dtk), platform, sumber suara.
- Tulis `episodes/<slug>/brief.yaml` dari `templates/brief.yaml`.

### Tahap 1: Riset fakta → ◆ Gerbang 1
- Baca `references/01-buku-panduan.md` bab 1, 3.2, dan 8.
- Cari 3–6 fakta yang membentuk eskalasi skala (pribadi → lokal → layanan → nasional → sistemik), plus
  satu data untuk refleksi. Utamakan sumber primer: laporan lembaga, putusan, studi.
- Tulis `fakta.yaml` dari `templates/fakta.yaml`, termasuk `ucapan` (angka dalam kata), `kartu_sumber`,
  dan `konversi` + rumusnya.
- Serahkan: ringkasan sudut cerita + tabel fakta (klaim, angka, sumber, tahun).

### Tahap 2: Naskah → ◆ Gerbang 2
- Baca `references/01-buku-panduan.md` bab 3 (struktur beat, aturan kalimat, bank frasa, durasi).
- Tulis `naskah.md` dari `templates/naskah.md`. Format: `references/05-skema-data.md` bab 3.
- Cek sendiri dengan `references/06-qa-checklist.md` bagian 2.2. Hitung estimasi durasi
  (kata ÷ 2,35).
- Serahkan naskah utuh + estimasi durasi.

### Tahap 3: Storyboard → ◆ Gerbang 3
- Baca `references/01-buku-panduan.md` bab 4–5 dan `references/03-karakter-dan-set.md`.
- Tulis `storyboard.json`. Format: `references/05-skema-data.md` bab 4. Contoh lengkap:
  `templates/contoh-andai-macet/`.
- Pakai hanya set/prop/ekspresi yang ada di `03-karakter-dan-set.md`. Kalau butuh yang baru, tambahkan
  ke dokumen itu dan sebutkan ke pengguna.
- Cek sendiri dengan `06-qa-checklist.md` bagian 2.3.
- Serahkan tabel ringkas: ID shot, perkiraan waktu, dunia/waktu, set, aksi, data, transisi.

### Tahap 4–6: Suara, alignment, timeline *(butuh engine)*
- `python -m andai vo <slug>` → `python -m andai align <slug>` → `python -m andai plan <slug>`.
- Detail: `references/04-arsitektur-pipeline.md` bagian 2.2, 2.3, 6.1.
- Rekaman sendiri: minta file per kalimat bernama sesuai ID (`K01.wav`, …).

### Tahap 7–10: Render → ◆ Gerbang 4 (preview), ◆ Gerbang 5 (final) *(butuh engine)*
- `python -m andai preview <slug>` dulu, lalu `python -m andai render <slug>`.
- `python -m andai qa <slug>`, lalu periksa `build/qa/laporan.md` dan contact sheet.
- Serahkan MP4, SRT, cover, dan teks deskripsi berisi daftar sumber dari `fakta.yaml`.

## Kapan membaca referensi apa

| File | Baca saat |
|---|---|
| `references/01-buku-panduan.md` | Selalu, sebelum Tahap 1–3. Sumber kebenaran gaya. |
| `references/02-bedah-referensi.md` | Butuh contoh bagaimana referensi menerapkan suatu teknik. |
| `references/03-karakter-dan-set.md` | Menulis storyboard; menambah tokoh, set, prop, atau SFX. |
| `references/04-arsitektur-pipeline.md` | Menjalankan atau membangun engine. |
| `references/05-skema-data.md` | Menulis atau memvalidasi file episode. |
| `references/06-qa-checklist.md` | Sebelum menyerahkan hasil di setiap gerbang. |

## Saat pengguna meminta hal yang melanggar aturan

- Menyebut nama pejabat atau orang nyata → tolak dengan sopan, jelaskan aturan peran (Buku Panduan 8.2),
  tawarkan versi berbasis peran.
- Memakai angka tanpa sumber → tandai `[[PERLU SUMBER]]`, bantu mencari sumber, jangan dikarang.
- Menyalin karakter, kalimat khas, atau potongan video referensi → tawarkan padanan versi ANDAI.
