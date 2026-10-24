# Video-editor — ANDAI

Skill Claude untuk membuat video kartun 3D narasi vertikal berformat **"Andai besok pagi kamu bangun,
dan [masalah] hilang."**: cerita yang bolak-balik antara dunia seandainya dan dunia nyata berbasis data,
dengan voice-over, caption per kata, dan akhir yang berputar (loop).

| Folder | Isi |
|---|---|
| [`skills/andai/`](skills/andai/README.md) | Skill: Buku Panduan, bedah video referensi, bible karakter/set, arsitektur, skema data, QA, templat, contoh episode pilot, roadmap |
| `andai/gpu/` | `setup_server.sh`: menyiapkan server RTX 5090 (Blender 5.2.3) dan menguji kecepatan render |
| `andai/scene3d/prototipe/` | Prototipe adegan 3D dari kode: versi Blender (`blender_scene.py`, mesin render utama) dan three.js (preview tanpa GPU) |
| `motion/` | Modul Python untuk tahap komposit: easing, color grade, efek, teks/sprite, SFX sintetis |
| `assets/fonts/` | Font berlisensi SIL OFL |

Status: rancangan + prototipe. Engine lengkapnya belum dibangun; urutan pembangunan ada di
[`skills/andai/ROADMAP.md`](skills/andai/ROADMAP.md). Untuk render dengan GPU, lihat
[`skills/andai/SETUP-SERVER-GPU.md`](skills/andai/SETUP-SERVER-GPU.md).
