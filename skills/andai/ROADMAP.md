# Roadmap ANDAI

## Keputusan terbuka (perlu jawaban pengguna)

| # | Keputusan | Pilihan | Rekomendasi |
|---|---|---|---|
| 1 | Sumber visual | A. Engine 2.5D prosedural · B. Plate AI + engine · C. 3D Blender | **A** sebagai inti, dengan dukungan plate B per set (`04-arsitektur-pipeline.md` 2.1) |
| 2 | Suara narator | Rekaman sendiri · TTS gratis (edge-tts) · TTS premium/kloning | TTS gratis untuk prototipe; rekaman sendiri atau kloning untuk rilis |
| 3 | Nama seri dan akun | "ANDAI" (nama kerja) atau lainnya | Tetapkan sebelum Fase 4, karena dipakai di logo pojok |
| 4 | Topik pilot | `andai-macet` (contoh sudah ada) atau topik lain | Topik yang datanya mudah dicari dan tidak menyebut orang |
| 5 | Durasi default | `pendek` / `standar` / `panjang` | `standar` (±90 dtk) |

## Fase

### Fase 0: Rancangan ✅
- Buku Panduan, bedah referensi, bible karakter/set, arsitektur, skema data, QA, templat, contoh pilot.
- **Selesai jika:** dokumen di `skills/andai/` disetujui pengguna.

### Fase 1: Skill tanpa engine (naskah dan storyboard)
- Pasang skill (lihat `README.md`), uji dengan kasus di `06-qa-checklist.md` bagian 4.
- Tulis `andai/project.py` + `python -m andai new|check`: membuat folder episode dan memvalidasi
  brief, fakta, naskah, storyboard sesuai `05-skema-data.md` (termasuk aturan jangkar, kedip, loop,
  digit di naskah, `[[PERLU SUMBER]]`).
- Isi fakta pilot dengan sumber nyata.
- **Selesai jika:** Claude bisa menghasilkan brief → fakta → naskah → storyboard yang lolos `andai check`
  untuk dua topik berbeda.

### Fase 2: Audio dan animatic
- `vo/tts.py` (edge-tts + rekaman), `vo/align.py` (faster-whisper + pencocokan naskah),
  `plan/timeline.py`, `overlay/caption.py`, `audio/mix.py`.
- `python -m andai animatic`: latar warna polos per dunia/waktu, kartu teks berisi deskripsi shot,
  caption per kata, Kartu Sumber, transisi Kedip, VO, dan SFX.
- **Selesai jika:** animatic pilot bisa ditonton, tempo dan caption sesuai Buku Panduan, loudness −14 LUFS.

### Fase 3: Engine visual MVP
- `scene/rig.py` + `scene/cast.py`: Si Kamu + 2 figuran, 6 pose, 8 ekspresi, kedip otomatis.
- `scene/sets.py`: 5 set (`kamar`, `jalan_raya`, `halte`, `jalan_malam`, `dapur`) dengan parallax.
- `scene/props.py`: 8 prop (`led`, `kalender`, `label_harga`, `angka_raksasa`, `jam_dinding`, `motor`,
  `mobil`, `lampu_lalu_lintas`).
- `scene/camera.py`, `look/grade.py`, `look/transitions.py`.
- **Selesai jika:** frame preview setiap set terlihat konsisten dengan `03-karakter-dan-set.md`, dan
  dunia bisa ditebak dari warna saja.

### Fase 4: Episode pilot end-to-end
- Lengkapi set/prop yang dipakai `templates/contoh-andai-macet/storyboard.json`.
- `python -m andai render` + `qa`. Uji tonton di HP; perbaiki Buku Panduan berdasarkan temuan.
- **Selesai jika:** pilot lolos semua gerbang dan siap unggah.

### Fase 5: Perluasan
- Tambah set/prop untuk 3–5 topik berikutnya.
- Jalur B (plate AI) untuk set yang sulit digambar prosedural.
- Preset `panjang` (±150 dtk), musik opsional dengan ducking.
- Evaluasi skill (pemicu dan kualitas naskah) dengan skill-creator.
