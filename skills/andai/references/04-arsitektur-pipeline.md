# Arsitektur Pipeline ANDAI

> Rancangan teknis engine yang akan dipakai skill. Status: **rancangan + prototipe 3D**. Prototipe yang
> membuktikan render 3D dari kode ada di `andai/scene3d/prototipe/`. Urutan pembangunan ada di
> `../ROADMAP.md`.

## 1. Gambaran besar

```
 brief.yaml
     │
     ▼
 [1] RISET ──────────► fakta.yaml          (Claude + pengguna)          ◆ Gerbang 1
     │
     ▼
 [2] NASKAH ─────────► naskah.md           (Claude)                     ◆ Gerbang 2
     │
     ▼
 [3] STORYBOARD ─────► storyboard.json     (Claude)                     ◆ Gerbang 3
     │
     ▼
 [4] VOICE-OVER ─────► audio/vo.wav        (TTS atau rekaman)
     │
     ▼
 [5] ALIGNMENT ──────► audio/words.json    (faster-whisper + pencocokan ke naskah)
     │
     ▼
 [6] TIMELINE ───────► timeline.json       (storyboard × words → frame)
     │
     ├──► [7] RENDER 3D ──────► build/shots/Sxx.mp4   (three.js di Chromium headless, per shot, di-cache)
     │              │
     │              ▼
     │    [8] KOMPOSIT ───────► grade dunia/waktu, transisi (Kedip, dissolve, whip),
     │                          caption, gelembung, Kartu Sumber            (Python)
     │
     └──► [9] MIX AUDIO ──────► audio/mix.wav (VO + SFX + musik, −14 LUFS)
                    │
                    ▼
 [10] ENCODE ────────► output/<slug>.mp4 + .srt + cover.jpg
     │
     ▼
 [11] QA ────────────► build/qa/ (contact sheet, laporan)               ◆ Gerbang 4 (preview), 5 (final)
```

Prinsip:

1. **Setiap tahap menghasilkan file yang bisa dibaca manusia.** Pengguna bisa berhenti, mengedit file,
   lalu melanjutkan dari tahap mana pun.
2. **Shot dijangkarkan ke kata, bukan ke detik.** Ganti suara atau ubah kalimat → timeline dihitung
   ulang otomatis, storyboard tidak perlu disentuh.
3. **Dunia 3D dan overlay dipisah.** Render 3D (mahal) di-cache per shot. Overlay dan grade (murah)
   dikerjakan di tahap komposit, jadi memperbaiki caption atau grade tidak perlu render 3D ulang.
4. **Deterministik.** Input dan seed yang sama menghasilkan video yang sama. Waktu animasi 3D dikendalikan
   per frame oleh runner, bukan oleh jam browser.
5. **Preview dulu, render penuh belakangan.** Mode preview 540×960, 15 fps.

## 2. Keputusan teknis

### 2.1 Sumber visual: 3D dari kode ✅ (diputuskan)

> **Pembaruan: mesin render final = Blender (`bpy`) di server RTX 5090.** Semua tetap ditulis sebagai
> kode Python (karakter, set, animasi, kamera, render). Server disiapkan dengan
> `andai/gpu/setup_server.sh`; panduan sambungannya di `../SETUP-SERVER-GPU.md`. Modul three.js di bawah
> tetap berguna untuk preview cepat di mesin tanpa GPU. Uji di bawah ini dilakukan sebelum ada GPU.

Video referensi adalah render 3D sungguhan. Pengguna memilih **3D yang dibangun sepenuhnya lewat kode**.
Tiga cara sudah diuji di container sesi Claude (4 core CPU, tanpa GPU), memakai adegan uji yang sama
(Si Kamu di jalan depan rumah):

| Cara | Hasil uji | Waktu per frame 1080×1920 | Episode 90 dtk (2.700 frame) | Status |
|---|---|---|---|---|
| **three.js di Chromium headless** (WebGL lewat SwiftShader) | Berhasil. Bayangan lembut, cahaya lingkungan, tone mapping | 0,93 dtk (tanpa AO) · 2,9 dtk (dengan ambient occlusion GTAO) | ±42 menit · ±2 jam 10 menit | **Dipilih** |
| Blender `bpy`, mesin Cycles (CPU, 16 sampel + denoise) | Berhasil, cahaya paling lembut | 31 dtk | ±23 jam | Terlalu lambat di sini |
| Blender `bpy`, mesin EEVEE | Gagal: butuh GPU/EGL | — | — | Tidak bisa di container |

Perbandingan visual: `img/uji-3d-perbandingan.jpg`.

**Hasil ukur di server RTX 5090** (24 Okt 2026; Ubuntu 24.04, driver 580.126.09 open, Blender 5.2.3 LTS,
AMD EPYC 9354, 1 GPU terlihat oleh container; adegan uji yang sama, 1080×1920, diukur dengan
`andai/gpu/bench_frames.py`, frame ke-2 dst.):

| Cara | Waktu per frame | Episode 90 dtk (2.700 frame) | Catatan |
|---|---|---|---|
| **Cycles GPU (CUDA), 64 sampel, denoise GPU** | **0,50 dtk** | **±22 menit** | **Dipakai.** Kualitas tertinggi |
| Cycles GPU (CUDA), 64 sampel, denoise CPU (bawaan Blender headless) | 9,3 dtk | ±7 jam | Jangan dipakai. Lihat jebakan di bawah |
| Cycles GPU, 64 sampel, tanpa denoise | 0,45 dtk | ±20 menit | Berbintik; hanya untuk pembanding |
| EEVEE | Tidak jalan | — | Container hanya membawa lapisan compute driver NVIDIA (CUDA/NVML/encode), tanpa `libEGL_nvidia`/`libGLX_nvidia`/Vulkan ICD, jadi EEVEE jatuh ke Mesa software dan menggantung |

**Jebakan:** Blender headless mendenoise di CPU secara default (`scene.cycles.denoising_use_gpu = False`),
sehingga satu frame makan ±9 dtk berapa pun jumlah sampelnya. Semua skrip render **wajib** menyetel
`denoising_use_gpu = True` saat device GPU (sudah ada di `blender_scene.py`; ikuti di `shot.py`). OptiX tidak
tersedia (tanpa `libnvoptix`), Cycles memakai CUDA, dan itu sudah cukup cepat.

**Biaya efek** (RTX 5090, 1080×1920, 64 sampel, Si Kamu berjalan + 5 figuran, diukur satu per satu):

| Efek | Tambahan waktu | Catatan |
|---|---|---|
| Cahaya 3 titik + langit gradasi | +0,2 dtk | dasar 1,35 → 1,55 dtk |
| Depth of field, motion blur | ≈ 0 | gratis di Cycles GPU |
| Debu melayang (45–90 bola) | +0,05 dtk | |
| Bloom (compositor Glare) | +0,2 dtk | node group di Blender 5 |
| Kabut (kotak volume terbatas) | +0,8 dtk | **jangan** volume dunia tak hingga: langit hilang dan gambar gelap |
| Semua efek | 2,8 dtk (64 sampel), 4,1 dtk (128) | adegan ramai 28 figuran: 4,3 / 5,8 dtk; 60 figuran: 5,1 dtk |

Membangun adegan ramai (28 figuran, ±2.900 objek) memakan ±14 dtk, sekali per shot. Perkiraan episode 90 detik
(2.700 frame): 1,3 jam tanpa kabut dan figuran, 2–3 jam dengan efek penuh, 3,2 jam bila semua shot ramai.

Karena Cycles GPU sudah ±0,5 dtk/frame, EEVEE tidak diperlukan. Bila suatu hari dibutuhkan, library grafis
NVIDIA harus dipasang dengan versi yang persis sama dengan driver (580.126.09); paket apt `libnvidia-gl-580`
menarik `libnvidia-compute-580` dan berisiko menimpa library CUDA yang disuntikkan container, jadi ekstrak
`.deb`-nya ke folder terpisah dan arahkan lewat `LD_LIBRARY_PATH`, `VK_ICD_FILENAMES`, dan
`__EGL_VENDOR_LIBRARY_FILENAMES` (belum dicoba).

**Alasan memilih three.js (keputusan awal, sebelum ada GPU):**
- Satu-satunya yang realistis dijalankan otomatis di dalam sesi Claude.
- Playwright + Chromium sudah terpasang di environment; three.js cukup `npm install`.
- Tulisan di prop (LED, kalender, label harga) bisa digambar persis memakai `CanvasTexture` dengan font
  Fredoka, sehingga angka selalu cocok dengan `fakta.yaml`.
- Rig tokoh dari primitif (bola, kapsul, lathe) cocok dengan gaya kartun yang dituju.

**Blender tetap jadi opsi masa depan** untuk kualitas lebih tinggi bila render dijalankan di komputer
pengguna yang punya GPU (EEVEE bisa < 1 dtk/frame di GPU). Untuk itu, deskripsi adegan disimpan sebagai
data (storyboard + pustaka set/prop), bukan terkunci ke API three.js.

Catatan: angka di atas diukur pada adegan uji yang sederhana. Adegan nyata dengan lebih banyak objek
dan figuran akan lebih lambat; ukur ulang di Fase 3.

### 2.2 Suara

| Opsi | Alat | Catatan |
|---|---|---|
| Rekaman sendiri | Pengguna merekam per kalimat (`K01.wav`, `K02.wav`, …) | Paling khas. Alignment tetap otomatis. |
| TTS gratis | `edge-tts` (suara neural `id-ID`) | Butuh internet. Cocok untuk prototipe dan animatic. |
| TTS premium | Layanan TTS/kloning berbayar via API key di environment | Kualitas terbaik; kunci API tidak boleh di-commit. |

Engine memperlakukan ketiganya sama: hasilnya satu file WAV per kalimat, lalu digabung dengan jeda sesuai
naskah.

### 2.3 Alignment kata

Sudah diuji pada video referensi: `faster-whisper` model `small`, `language="id"`, `word_timestamps=True`
menghasilkan timestamp per kata yang rapi untuk narasi Bahasa Indonesia.

Langkah:
1. Transkripsi VO → daftar kata whisper dengan (mulai, selesai).
2. Normalisasi kedua sisi: huruf kecil, buang tanda baca, angka whisper diubah ke kata ("34" → "tiga
   puluh empat", "2,3" → "dua koma tiga").
3. Cocokkan urutan kata naskah ke urutan kata whisper (`difflib.SequenceMatcher` per kalimat).
4. Kata naskah yang tidak cocok diberi waktu interpolasi dari tetangganya, ditandai `"interp": true`.
5. Hasil: `words.json` berisi kata **dari naskah** (ejaan dan tanda baca benar) dengan waktu **dari audio**.

Catatan teknis dari uji: versi `av` terbaru tidak cocok dengan `faster_whisper.decode_audio`; muat WAV
sendiri dengan `wave` + `numpy` lalu kirim array float32 16 kHz ke `transcribe()`.

### 2.4 Render 3D (three.js)

Cara kerja yang sudah terbukti di prototipe:

1. Runner Node (`runner.js`) membuka Chromium headless lewat Playwright dengan flag
   `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist`.
2. Halaman adegan memuat three.js dari `node_modules` (dilayani lewat `page.route`, tanpa server).
3. Halaman menyediakan `window.renderFrame(t)`: mengatur pose, ekspresi, kamera, dan prop untuk waktu `t`,
   lalu me-render satu frame.
4. Runner memanggil `renderFrame` untuk setiap frame, mengambil screenshot JPEG, dan menyalurkannya ke
   `ffmpeg` (`image2pipe`) → `build/shots/Sxx.mp4`.
5. Setiap shot dirender dengan **handle** (frame tambahan di awal dan akhir) untuk transisi dissolve/Kedip.
6. Cache: nama file shot = hash dari (spesifikasi shot, durasi, versi pustaka). Shot yang tidak berubah
   tidak dirender ulang.

Pengaturan render bawaan:
- `MeshStandardMaterial` (roughness 0,45–0,8) agar terlihat seperti mainan/plastik doff.
- `HemisphereLight` + satu `DirectionalLight` (matahari/bulan) dengan `PCFSoftShadowMap`, peta bayangan
  2048 px.
- Cahaya lingkungan `RoomEnvironment` (PMREM), intensitas 0,4–0,5.
- Tone mapping ACES Filmic, color space sRGB.
- Kabut (`THREE.Fog`) untuk kedalaman, terutama di Dunia Nyata.
- Ambient occlusion (`GTAOPass`) hanya di mode `final-hq`.

Mode render:

| Mode | Resolusi | fps | AO | Terukur di prototipe | Perkiraan episode 90 dtk |
|---|---|---|---|---|---|
| `preview` | 540×960 | 15 | tidak | 0,41 dtk/frame | ±9 menit |
| `final` | 1080×1920 | 30 | tidak | 0,93 dtk/frame | ±42 menit |
| `final-hq` | 1080×1920 | 30 | GTAO | 2,9 dtk/frame | ±2 jam 10 menit |

Menjalankan beberapa browser paralel hampir tidak menambah kecepatan (SwiftShader sudah memakai semua
core). Penghematan terbesar datang dari cache per shot dan preview.

### 2.5 Komposit (Python)

Memakai ulang modul yang sudah ada di repo:
- `motion/fx.py`: easing (`ease_out_cubic`, `back_out`, `spring`, …), `grade`, `vignette`, `grain_bank`,
  `bloom`, `motion_blur`, `flash`.
- `motion/text.py`: `text_sprite`, `blit` (komposit alfa dengan skala/rotasi) untuk caption, gelembung,
  dan Kartu Sumber.
- `motion/sfx.py`: `whoosh`, `pop`, `impact`, `riser`, `sparkle`, `mix`.

Urutan per frame: ambil frame shot (+ shot berikutnya saat transisi) → grade waktu → grade dunia →
transisi → grain/vignette → overlay (caption, gelembung, Kartu Sumber; tidak ikut di-grade) → ffmpeg.

## 3. Struktur repo (rencana)

```
Video-editor/
├── motion/                      # sudah ada; dipakai ulang untuk komposit
├── andai/                       # engine baru
│   ├── cli.py                   # perintah `python -m andai …`
│   ├── project.py               # baca/tulis file episode, validasi skema
│   ├── vo/
│   │   ├── tts.py               # edge-tts / premium / rekaman
│   │   └── align.py             # faster-whisper + pencocokan naskah
│   ├── plan/
│   │   ├── naskah.py            # parser naskah.md → kalimat, kata, sorotan, tag fakta
│   │   └── timeline.py          # storyboard + words → timeline
│   ├── scene3d/                 # dunia 3D (JavaScript + three.js)
│   │   ├── package.json
│   │   ├── prototipe/           # ✅ sudah ada: uji kelayakan satu adegan
│   │   ├── runner.js            # Playwright: render satu shot → mp4, dengan cache
│   │   ├── shot.html            # halaman render: baca spesifikasi shot, sediakan renderFrame(t)
│   │   └── src/
│   │       ├── rig.js           # tokoh: kepala lathe, kapsul, sendi, ekspresi, kedip
│   │       ├── cast.js          # definisi pemeran (dari 03-karakter-dan-set.md)
│   │       ├── sets/            # satu file per set (kamar.js, jalan_raya.js, …)
│   │       ├── props/           # prop benda + prop data (CanvasTexture untuk tulisan)
│   │       ├── lights.js        # preset cahaya per waktu (pagi/siang/sore/malam)
│   │       ├── camera.js        # push_in, pull_out, truck, tilt, orbit, cu, rendah, shake
│   │       └── materials.js     # palet + material standar
│   ├── composite/
│   │   ├── grade.py             # preset dunia (andai/nyata/netral) × waktu
│   │   ├── transitions.py       # cut, dissolve, whip, kedip
│   │   ├── caption.py           # caption per kata
│   │   ├── bubble.py            # gelembung bicara
│   │   └── source.py            # Kartu Sumber
│   ├── audio/
│   │   └── mix.py               # VO + SFX + musik, ducking, loudnorm
│   ├── render.py                # orkestrasi: render3d per shot → komposit → encode
│   └── qa.py                    # contact sheet, cek aturan, laporan
├── assets/
│   ├── fonts/                   # + Nunito, Fredoka (OFL), juga dipakai CanvasTexture
│   └── sfx/                     # SFX rekaman bebas lisensi (opsional)
├── episodes/
│   └── <slug>/                  # satu folder per episode (lihat 4)
└── skills/andai/                # skill ini
```

## 4. Struktur folder episode

```
episodes/andai-macet/
├── brief.yaml            # input pengguna
├── fakta.yaml            # fakta + sumber + konversi
├── naskah.md             # naskah berbeat
├── storyboard.json       # daftar shot berjangkar kata
├── audio/
│   ├── kalimat/K01.wav … # VO per kalimat
│   ├── vo.wav            # VO gabungan
│   ├── words.json        # timestamp per kata
│   └── mix.wav           # hasil mix akhir
├── timeline.json         # hasil hitung (jangan diedit tangan)
├── build/
│   ├── shots/            # cache render 3D per shot (S01-<hash>.mp4)
│   ├── preview/          # frame/video preview
│   └── qa/               # contact sheet, laporan QA
└── output/
    ├── andai-macet.mp4
    ├── andai-macet.srt
    └── cover.jpg
```

`audio/`, `build/`, dan `output/` masuk `.gitignore`; file teks (brief, fakta, naskah, storyboard)
di-commit.

## 5. Perintah CLI (rencana)

| Perintah | Tahap | Hasil |
|---|---|---|
| `python -m andai new <slug>` | 0 | Folder episode + templat dari `skills/andai/templates/` |
| `python -m andai check <slug>` | 1–3 | Validasi skema + aturan Buku Panduan (durasi, panjang kalimat, sumber, angka di naskah) |
| `python -m andai vo <slug> [--engine edge\|premium\|rekaman]` | 4 | `audio/kalimat/*.wav`, `audio/vo.wav` |
| `python -m andai align <slug>` | 5 | `audio/words.json` |
| `python -m andai plan <slug>` | 6 | `timeline.json` |
| `python -m andai animatic <slug>` | 6 | Video kasar: kartu teks per shot + caption + VO (sebelum engine 3D ada) |
| `python -m andai shot <slug> S07 [--mode preview]` | 7 | Render satu shot saja untuk dicek |
| `python -m andai preview <slug> [--at 12.5 40.2]` | 7–8 | Frame/video 540×960 15 fps |
| `python -m andai render <slug> [--hq]` | 7–10 | MP4 final + SRT + cover |
| `python -m andai qa <slug>` | 11 | Laporan QA + contact sheet |

## 6. Algoritma kunci

### 6.1 Storyboard → timeline

```
untuk setiap shot i (urut):
    mulai_i   = onset(kata jangkar shot i) − lead            # lead = 1 frame
    selesai_i = mulai_{i+1}                                   # shot terakhir: akhir VO + ekor loop
    jika transisi masuk shot i ≠ cut:
        overlap = durasi transisi; shot i−1 diperpanjang setengahnya, shot i dimajukan setengahnya
validasi: 1,0 ≤ durasi shot ≤ 4,5 dtk (peringatan di luar 1,5–3,5)
```

Kata jangkar ditulis sebagai `{"kalimat": "K07", "kata": 3}` (indeks kata ke-3 di kalimat K07, mulai 0).
`aksi[].di_kata` dan `muncul_di_kata` diubah ke waktu relatif shot, lalu dikirim ke halaman render 3D.

### 6.2 Caption

```
untuk setiap kata w di words.json:
    tampil dari onset(w) − 1 frame
    sampai onset(kata berikutnya), atau selesai(w) + 0,6 dtk jika itu kata terakhir sebelum jeda panjang
    gaya = sorot jika w.sorot atau w berupa angka, selain itu biasa
```

### 6.3 Grade dan Kedip

- Cahaya 3D mengikuti `waktu` (arah, warna, dan intensitas matahari; warna langit; lampu menyala di
  malam hari). Grade dunia (`andai`/`nyata`/`netral`) diterapkan di tahap komposit, sehingga set 3D yang
  sama bisa tampil sebagai dua dunia hanya dengan grade dan kabut yang berbeda.
- Kabut Dunia Nyata dikerjakan di 3D (`THREE.Fog` lebih tebal) karena butuh informasi kedalaman.
- Saat transisi `kedip`, kelopak menutup penuh di frame ke-4 sampai ke-6; grade berganti tepat di frame
  gelap, sehingga perubahan warna tidak terlihat sebagai lompatan.

### 6.4 Kamera 3D

- Kamera = posisi + target + lensa (mm) sebagai fungsi waktu dalam shot. Default `push_in`: kamera maju
  ±15% jarak ke target dengan `ease_in_out`.
- Karena dunia benar-benar 3D, parallax dan perubahan perspektif muncul sendiri.
- `orbit` (memutar 5–15° mengelilingi target) adalah gerak khas 3D yang tidak mungkin di 2.5D. Pakai
  untuk adegan yang perlu terasa "hidup" dan memperlihatkan bentuk benda.
- Close-up (`cu`) memakai lensa lebih panjang (50–85 mm) agar wajah tidak terdistorsi.

### 6.5 Mix audio

1. VO gabungan (jeda antar-kalimat sesuai naskah; default 0,2 dtk, `[jeda:0.6]` untuk jeda dramatis).
2. SFX dari `timeline.json` (diturunkan dari kolom `sfx` dan transisi storyboard).
3. Musik opsional dengan ducking sidechain terhadap VO.
4. `ffmpeg loudnorm` dua tahap ke −14 LUFS, TP −1 dBTP.

## 7. Dependensi

```
# Python
numpy, opencv-python-headless, pillow, scipy      # sudah ada di requirements.txt
pyyaml, jsonschema                                # baca/validasi file episode
faster-whisper                                    # alignment
edge-tts                                          # TTS gratis (opsional)

# Node (andai/scene3d)
three@0.170.0                                     # mesin 3D
playwright                                        # sudah terpasang di environment Claude; di mesin lain: npm i playwright

# Sistem
ffmpeg, Chromium (bawaan Playwright)
```

Font tambahan: Nunito, Fredoka (keduanya SIL OFL) ke `assets/fonts/`.

## 8. Risiko dan mitigasi

| Risiko | Mitigasi |
|---|---|
| Render lambat untuk adegan ramai (banyak figuran) | Cache per shot; preview 540p; instancing (`InstancedMesh`) untuk figuran dan benda berulang; AO hanya di `final-hq` |
| Tampilan "primitif" terlalu polos | Investasi di cahaya (matahari rendah, lampu malam, cahaya lingkungan), kabut, material doff, detail kecil prop; bandingkan rutin dengan `02-bedah-referensi.md` |
| Animasi 3D tidak deterministik | Waktu dikendalikan runner per frame; random pakai seed; tidak memakai `requestAnimationFrame` |
| Font belum termuat saat tulisan prop digambar | Tunggu `document.fonts.ready` sebelum frame pertama |
| Whisper salah dengar kata | Kata naskah tetap dipakai; whisper hanya memberi waktu. Kata tak cocok diinterpolasi dan ditandai di QA |
| TTS salah baca singkatan/angka | Naskah wajib angka dalam kata; singkatan dieja ("ka te pe") di naskah ucapan |
| Fakta salah | Gerbang 1 wajib; Kartu Sumber; `check` menolak `[[PERLU SUMBER]]` |
| Pustaka set kurang untuk topik baru | Storyboard boleh memakai set terdekat + catatan; set baru ditambahkan per episode |
