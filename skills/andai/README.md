# Skill ANDAI: video kartun narasi "dunia seandainya"

Skill Claude untuk membuat video kartun narasi vertikal berformat **"Andai besok pagi kamu bangun, dan
[masalah] hilang."** Konsepnya diambil dari video referensi (kartun 3D satire tentang korupsi), lalu
dibuat ulang sebagai versi kita sendiri: 3D yang dibangun sepenuhnya dari kode (three.js), tokoh, transisi
Kedip, Kartu Sumber, dan bank frasa milik sendiri.

**Status: Fase 0 (rancangan).** Dokumen lengkap dan prototipe render 3D sudah terbukti jalan
(`andai/scene3d/prototipe/`). Engine lengkapnya belum dibangun. Lihat `ROADMAP.md`.

## Isi folder

| File | Isi |
|---|---|
| `SKILL.md` | Entri skill: kapan dipakai dan alur kerja Claude (draf) |
| `references/01-buku-panduan.md` | **Buku Panduan**: DNA format, formula naskah, bahasa visual, tempo, caption, audio, etika |
| `references/02-bedah-referensi.md` | Bedah video referensi: data teknis, peta beat, teknik, pelajaran |
| `references/03-karakter-dan-set.md` | Bible visual: rig tokoh 3D, ekspresi, pemeran, palet, set, prop, SFX |
| `references/04-arsitektur-pipeline.md` | Rancangan teknis engine: tahap, hasil uji 3D (three.js vs Blender), struktur kode, algoritma |
| `references/img/uji-3d-perbandingan.jpg` | Hasil uji render 3D dari kode: three.js vs Blender Cycles |
| `references/05-skema-data.md` | Format file episode: brief, fakta, naskah, storyboard, words, timeline |
| `references/06-qa-checklist.md` | Gerbang persetujuan, checklist QA, kasus uji skill |
| `templates/` | Templat kosong `brief.yaml`, `fakta.yaml`, `naskah.md` |
| `templates/contoh-andai-macet/` | Contoh episode pilot lengkap (brief, fakta kosong, naskah, storyboard 39 shot) |
| `ROADMAP.md` | Keputusan terbuka dan fase pembangunan |
| `SETUP-SERVER-GPU.md` | Cara menjalankan Claude Code di server GPU dan menyambungkannya lewat Remote Control |

## Urutan baca

1. `references/02-bedah-referensi.md`: memahami apa yang membuat video referensi bekerja.
2. `references/01-buku-panduan.md`: aturan versi kita.
3. `templates/contoh-andai-macet/naskah.md` dan `storyboard.json`: aturan itu diterapkan.
4. `ROADMAP.md`: jawab keputusan terbuka, lalu mulai Fase 1.

## Cara memasang skill

- **Claude Code** (repo ini): salin atau symlink folder ini ke `.claude/skills/andai/`. Claude akan
  memuatnya otomatis saat permintaan cocok dengan deskripsi di `SKILL.md`.
- **claude.ai**: kompres folder `andai/` menjadi ZIP (dengan `SKILL.md` di dalam folder itu), lalu unggah
  lewat pengaturan Skills.

Sebelum engine selesai, skill sudah berguna untuk Tahap 0–3: riset fakta, naskah, dan storyboard.
