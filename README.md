# Video-editor — ANDAI

Skill Claude untuk membuat video kartun 3D narasi vertikal berformat **"Andai besok pagi kamu bangun,
dan [masalah] hilang."**: cerita yang bolak-balik antara dunia seandainya dan dunia nyata berbasis data,
dengan voice-over, caption per kata, dan akhir yang berputar (loop).

| Folder | Isi |
|---|---|
| [`skills/andai/`](skills/andai/README.md) | Skill: Buku Panduan, bedah video referensi, bible karakter/set, arsitektur, skema data, QA, templat, contoh episode pilot, roadmap |
| `andai/gpu/` | `gpu.sh` (kendali server GPU yang boleh mati: kunci, siapkan, kirim, jalankan, ambil, cadangan, pulihkan) dan `setup_server.sh` (Blender 5.2.3 + uji kecepatan). Rencana pindah server: [`skills/andai/PINDAH-SERVER.md`](skills/andai/PINDAH-SERVER.md) |
| `andai/blender/` | Engine 3D Blender: rig karakter, 10 tokoh pemeran + kerumunan, kostum, pose, ekspresi, kedip, cahaya per waktu, efek (DOF, motion blur, kabut, debu, bloom), uji (Fase 3 sedang dibangun) |
| `andai/scene3d/prototipe/` | Prototipe adegan 3D dari kode: versi Blender (`blender_scene.py`, mesin render utama) dan three.js (preview tanpa GPU) |
| `motion/` | Modul Python untuk tahap komposit: easing, color grade, efek, teks/sprite, SFX sintetis |
| `assets/fonts/` | Font berlisensi SIL OFL |

Status: rancangan + prototipe. Engine lengkapnya belum dibangun; urutan pembangunan ada di
[`skills/andai/ROADMAP.md`](skills/andai/ROADMAP.md). Untuk render dengan GPU, lihat
[`skills/andai/SETUP-SERVER-GPU.md`](skills/andai/SETUP-SERVER-GPU.md).
