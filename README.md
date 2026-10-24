# Video-editor — ANDAI

Skill Claude untuk membuat video kartun 3D narasi vertikal berformat **"Andai besok pagi kamu bangun,
dan [masalah] hilang."**: cerita yang bolak-balik antara dunia seandainya dan dunia nyata berbasis data,
dengan voice-over, caption per kata, dan akhir yang berputar (loop).

| Folder | Isi |
|---|---|
| [`skills/andai/`](skills/andai/README.md) | Skill: Buku Panduan, bedah video referensi, bible karakter/set, arsitektur, skema data, QA, templat, contoh episode pilot, roadmap |
| `andai/scene3d/prototipe/` | Prototipe render 3D dari kode (three.js di Chromium headless) + versi Blender untuk pembanding |
| `motion/` | Modul Python untuk tahap komposit: easing, color grade, efek, teks/sprite, SFX sintetis |
| `assets/fonts/` | Font berlisensi SIL OFL |

Status: rancangan + prototipe. Engine lengkapnya belum dibangun; urutan pembangunan ada di
[`skills/andai/ROADMAP.md`](skills/andai/ROADMAP.md). Untuk render dengan GPU, lihat
[`skills/andai/SETUP-SERVER-GPU.md`](skills/andai/SETUP-SERVER-GPU.md).
