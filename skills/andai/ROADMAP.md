# Roadmap ANDAI

## Keputusan

| # | Keputusan | Status |
|---|---|---|
| 1 | Sumber visual | ✅ **Blender lewat kode (`bpy`), dirender di server RTX 5090.** Karakter, set, animasi, dan kamera ditulis sebagai skrip Python; render EEVEE (episode biasa) atau Cycles (kualitas tertinggi). three.js tetap ada sebagai preview tanpa GPU. Latar belakang uji: `references/04-arsitektur-pipeline.md` 2.1 |
| 2 | Suara narator | Terbuka: rekaman sendiri · TTS gratis (edge-tts) · TTS premium/kloning. Rekomendasi: TTS gratis untuk prototipe; rekaman sendiri atau kloning untuk rilis |
| 3 | Nama seri dan akun | Terbuka: "ANDAI" masih nama kerja. Tetapkan sebelum Fase 4 karena dipakai di logo pojok |
| 4 | Topik pilot | Terbuka: `andai-macet` (contoh sudah ada) atau topik lain yang datanya mudah dicari dan tidak menyebut orang |
| 5 | Durasi default | Terbuka: rekomendasi `standar` (±90 dtk) |

## Fase

### Fase 0: Rancangan ✅
- Buku Panduan, bedah referensi, bible karakter/set, arsitektur, skema data, QA, templat, contoh pilot.
- Prototipe kelayakan 3D: `andai/scene3d/prototipe/` (satu adegan jalan + Si Kamu, render ke MP4).

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
  `plan/timeline.py`, `composite/caption.py`, `audio/mix.py`.
- `python -m andai animatic`: latar warna polos per dunia/waktu, kartu teks berisi deskripsi shot,
  caption per kata, Kartu Sumber, transisi Kedip, VO, dan SFX.
- **Selesai jika:** animatic pilot bisa ditonton, tempo dan caption sesuai Buku Panduan, loudness −14 LUFS.

### Fase 3: Engine 3D MVP (Blender, di server RTX 5090)
- Siapkan server: `bash andai/gpu/setup_server.sh` (cek driver, pasang Blender 5.2.3 LTS, jalankan uji
  render). Catat hasil `andai/gpu/hasil/hasil_uji.txt` ke `04-arsitektur-pipeline.md` bagian 2.1.
- `andai/blender/rig.py` + `cast.py`: Si Kamu + 2 figuran dari skrip, 6 pose, 8 ekspresi, kedip otomatis.
  Simpan sebagai aset `assets/blender/karakter.blend` agar dipakai ulang.
- `andai/blender/sets/`: 5 set (`kamar`, `jalan_raya`, `halte`, `jalan_malam`, `dapur`).
- `andai/blender/props/`: 8 prop (`led`, `kalender`, `label_harga`, `angka_raksasa`, `jam_dinding`,
  `motor`, `mobil`, `lampu_lalu_lintas`), tulisan memakai objek teks Blender dengan font Fredoka.
- `andai/blender/lights.py` (4 waktu), `camera.py`, `shot.py` (render satu shot dari storyboard ke
  `build/shots/Sxx.mp4`, dengan cache), lalu `composite/grade.py` dan `composite/transitions.py`.
- **Selesai jika:** setiap set terlihat konsisten dengan `03-karakter-dan-set.md`, dunia bisa ditebak dari
  warna saja, dan waktu render per shot terukur di RTX 5090.

### Fase 4: Episode pilot end-to-end
- Lengkapi set/prop yang dipakai `templates/contoh-andai-macet/storyboard.json`.
- `python -m andai render` + `qa`. Uji tonton di HP; perbaiki Buku Panduan berdasarkan temuan.
- **Selesai jika:** pilot lolos semua gerbang dan siap unggah.

### Fase 5: Perluasan
- Tambah set/prop untuk 3–5 topik berikutnya.
- Mode `final-hq` (ambient occlusion) sebagai standar jika waktunya bisa diterima.
- Opsional: ekspor adegan ke Blender untuk render berkualitas tinggi di komputer pengguna yang punya GPU.
- Preset `panjang` (±150 dtk), musik opsional dengan ducking.
- Evaluasi skill (pemicu dan kualitas naskah) dengan skill-creator.
