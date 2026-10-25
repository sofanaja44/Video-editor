# Roadmap ANDAI

## Keputusan

| # | Keputusan | Status |
|---|---|---|
| 1 | Sumber visual | ✅ **Blender lewat kode (`bpy`), dirender di server RTX 5090.** Karakter, set, animasi, dan kamera ditulis sebagai skrip Python; render EEVEE (episode biasa) atau Cycles (kualitas tertinggi). three.js tetap ada sebagai preview tanpa GPU. Latar belakang uji: `references/04-arsitektur-pipeline.md` 2.1 |
| 2 | Suara narator | ✅ **ElevenLabs lewat API**, suara "Sopeng" (`TnhigSuEbLfRMVdZNHmu`, model `eleven_v4`) lewat `/root/anime-karakter/tools/tts.py`, yang juga memberi timestamp per kata (mengganti Whisper). Kuota ±36 ribu karakter per bulan dibagi dengan proyek lain |
| 3 | Nama seri dan akun | Terbuka: "ANDAI" masih nama kerja. Tetapkan sebelum Fase 4 karena dipakai di logo pojok |
| 4 | Topik pilot | ✅ `andai-macet`; fakta bersumber ada di `episodes/andai-macet/fakta.yaml` (menunggu Gerbang 1) |
| 5 | Durasi default | ✅ `standar` (±90 dtk) |

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
  ✅ Selesai 24 Okt 2026: Cycles GPU (CUDA) ±0,5 dtk/frame di 1080×1920 (wajib `denoising_use_gpu = True`);
  EEVEE tidak jalan di container ini dan tidak diperlukan.
- `andai/blender/rig.py` + `cast.py`: Si Kamu + 2 figuran dari skrip, 6 pose, 8 ekspresi, kedip otomatis.
  Simpan sebagai aset `assets/blender/karakter.blend` agar dipakai ulang.
  ✅ Selesai 24 Okt 2026, lebih dari target: Si Kamu + figuran bernomor tanpa batas (`warga(n, seed)`), **12**
  ekspresi, 6 pose (berdiri, jalan, duduk, menunjuk, angkat_bahu, pegang), 6 gaya rambut, kedip otomatis,
  keyframe (pose, ekspresi, tempat, siklus jalan). Karakter dibangun dari kode per shot (<1 dtk), jadi
  `karakter.blend` tidak dibuat. Uji: `andai/blender/uji_karakter.sh` dan `uji_keyframe.py`. Lihat
  `andai/blender/README.md`. Belum ada: pose `naik_motor`, `rogoh_saku`, `sodor`, `menulis`, `antre`, `tidur`,
  `bangun`; tokoh selain Si Kamu dan figuran (Bu Tetangga, polisi, pejabat, dst.).
  ✅ **Pemeran lengkap** (24 Okt 2026): 10 tokoh bernama (`cast.tokoh(nama)`: kamu, tetangga, petugas, polisi,
  pejabat, peneliti, nenek, bayi, tukang_ban, ibu) + figuran bernomor dengan peran (`sopir_angkot`, `anak`) +
  `kerumunan(jumlah, sebar)` (deret, lajur_penuh, antre_lajur, serobot_lajur, acak). Sistem kostum `kostum.py`
  (rok, kerudung, topi, helm, kacamata, jas+dasi, rompi, saku, sabuk, handuk, popok, dst.). Peningkatan model:
  telinga, hidung, jempol, sandal jepit bertali, kulit SSS, kain bertekstur dan bermotif.
  ✅ **Cahaya dan efek** (`lights.py`, `fx.py`): 4 waktu (pagi/siang/sore/malam), DOF, motion blur, kabut,
  debu melayang, bloom. Terukur: adegan ramai 28 figuran + semua efek 4,3 dtk/frame (1080×1920, 64 sampel).
  ✅ **Ketahanan server:** `andai/gpu/gpu.sh` + `PINDAH-SERVER.md` (server GPU boleh mati; aset di server utama).
  Belum ada: set, prop, `camera.py`, `shot.py`, `composite/grade.py`, `transitions.py`, efek `sinar_jendela`,
  `hujan`, `uap_kopi`, `bintang_kilau`, `retak`, `asap_knalpot`.
  ✅ **Mulai set/prop/kamera** (24 Okt 2026): `sets/jalan_raya.py` (jalan 4 lajur, persimpangan, zebra, trotoar, gedung
  berjendela yang menyala acak di malam hari, pohon, tiang lampu, titik bernama, palet dua dunia),
  `props/kendaraan.py` (motor, mobil, angkot, bus) dan `props/lampu.py` (lampu lalu lintas), pose `naik_motor`,
  `camera.py` (push_in, pull_out, truck, cu, tilt, orbit, getar; kamera tidak pernah di bawah tanah; set menyembunyikan
  gedung yang menghalangi). Uji: `uji_jalan.py`. Sisa kebutuhan episode `andai-macet`: lihat "Rencana pilot" di bawah.
- `andai/blender/sets/`: 5 set (`kamar`, `jalan_raya`, `halte`, `jalan_malam`, `dapur`).
- `andai/blender/props/`: 8 prop (`led`, `kalender`, `label_harga`, `angka_raksasa`, `jam_dinding`,
  `motor`, `mobil`, `lampu_lalu_lintas`), tulisan memakai objek teks Blender dengan font Fredoka.
- `andai/blender/lights.py` (4 waktu), `camera.py`, `shot.py` (render satu shot dari storyboard ke
  `build/shots/Sxx.mp4`, dengan cache), lalu `composite/grade.py` dan `composite/transitions.py`.
- **Selesai jika:** setiap set terlihat konsisten dengan `03-karakter-dan-set.md`, dunia bisa ditebak dari
  warna saja, dan waktu render per shot terukur di RTX 5090.

### Fase 4: Episode pilot end-to-end

**Rencana pilot `andai-macet`** (inventaris dari `storyboard.json`: 39 shot):

| # | Langkah | Status |
|---|---|---|
| M0 | Brief + fakta bersumber (4 fakta; sumber primer, ada catatan keterbatasan) | ✅ draf → ◆ **Gerbang 1** menunggu persetujuan |
| M1 | Naskah final dengan ucapan fakta, hitung durasi → ◆ Gerbang 2 | menunggu Gerbang 1 |
| M2 | Suara: ElevenLabs per kalimat (`tts.py`, voice Sopeng) → `words.json` → timeline dari jangkar kata. ±1.500 karakter per take penuh | setelah Gerbang 2 |
| M3 | Isi dunia 3D: set `kamar`, `dapur`, `halte`, `jalan_kampung`, `taman_kota`, `jalan_malam` (+ `jalan_raya` ✅); prop `jam_weker`, `jam_dinding`, `piring`, `papan_nama`, `layangan`, `gerobak_martabak` + prop data `led` (+ motor, mobil, angkot, bus, lampu ✅); pose `bangun`, `tidur`; efek `sinar_jendela`, `asap_knalpot`, `uap_kopi`, `bintang_kilau` (+ `debu_melayang`, `kabut` ✅); peran figuran | berjalan |
| M4 | Mesin shot: `shot.py` (storyboard → Blender, jangkar → waktu, cache per shot, bisa dilanjutkan), `composite/` (grade dunia, transisi kedip/dissolve/whip/cut, caption per kata, Kartu Sumber, loop), mix audio −14 LUFS | berikutnya |
| M5 | Pratinjau 540p → ◆ Gerbang 4; final 1080×1920 → ◆ Gerbang 5; QA; caption posting tanpa kata "satire"/"sindiran"; unggah manual | — |

Kebutuhan episode (39 shot): set `jalan_raya` 17, `jalan_malam` 7, `jalan_kampung` 5, `halte` 4, `kamar` 3, `dapur` 2, `taman_kota` 1;
pose `naik_motor` 10, `berdiri` 9, `duduk` 5; transisi `cut` 17, `kedip` 9, `dissolve` 9, `whip` 4; kamera `push_in` 13,
`truck` 10, `cu` 9, `pull_out` 6, `tilt` 1.

- Lengkapi set/prop yang dipakai `templates/contoh-andai-macet/storyboard.json`.
- `python -m andai render` + `qa`. Uji tonton di HP; perbaiki Buku Panduan berdasarkan temuan.
- **Selesai jika:** pilot lolos semua gerbang dan siap unggah.

### Fase 5: Perluasan
- Tambah set/prop untuk 3–5 topik berikutnya.
- Mode `final-hq` (ambient occlusion) sebagai standar jika waktunya bisa diterima.
- Opsional: ekspor adegan ke Blender untuk render berkualitas tinggi di komputer pengguna yang punya GPU.
- Preset `panjang` (±150 dtk), musik opsional dengan ducking.
- Evaluasi skill (pemicu dan kualitas naskah) dengan skill-creator.
