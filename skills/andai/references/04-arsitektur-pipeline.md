# Arsitektur Pipeline ANDAI

> Rancangan teknis engine yang akan dipakai skill. Status: **rancangan**, belum diimplementasikan.
> Urutan pembangunan ada di `../ROADMAP.md`.

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
     ├──► [7] RENDER VISUAL ──► frame (set + tokoh + prop + kamera + grade + transisi)
     ├──► [8] OVERLAY ────────► caption, gelembung, Kartu Sumber
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
3. **Deterministik.** Input dan seed yang sama menghasilkan video yang sama (figuran, kedip, grain).
4. **Preview dulu, render penuh belakangan.** Mode preview 540×960, 15 fps untuk cek cepat.

## 2. Keputusan teknis

### 2.1 Sumber visual (keputusan terbuka #1)

| Jalur | Cara | Kelebihan | Kekurangan |
|---|---|---|---|
| **A. Engine 2.5D prosedural** (rekomendasi MVP) | Set, tokoh, dan prop digambar kode Python dari parameter `03-karakter-dan-set.md` | Sepenuhnya otomatis di dalam sesi Claude; tokoh 100% konsisten; render cepat; tanpa biaya API; "versi kita" yang jelas beda dari 3D referensi | Latar lebih sederhana; pustaka set/prop perlu dibangun bertahap |
| **B. Plate AI + engine** | Latar dibuat model gambar (pengguna mengunggah atau via API), tokoh/prop/teks tetap dari engine | Latar lebih kaya dan detail | Butuh alat luar; gaya latar bisa tidak konsisten; ada biaya |
| **C. 3D (Blender)** | Tokoh primitif 3D dirender Blender | Paling dekat dengan referensi | Render sangat berat di container tanpa GPU (jam per episode); kompleksitas tinggi |

**Rekomendasi:** bangun jalur A sebagai inti. Desain modul `set` agar satu set bisa berupa gambar plate
(jalur B) tanpa mengubah bagian lain, sehingga B bisa ditambahkan kapan saja. Jalur C tidak dikejar.

### 2.2 Suara (keputusan terbuka #2)

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

### 2.4 Render

- Python + NumPy + OpenCV + Pillow, memakai ulang modul yang sudah ada di repo:
  - `motion/text.py`: `text_sprite`, `blit` (komposit alfa dengan skala/rotasi), `supersample`
  - `motion/fx.py`: easing (`ease_out_cubic`, `back_out`, `spring`, …), `grade`, `vignette`, `grain_bank`,
    `bloom`, `motion_blur`, `flash`, `glitch`
  - `motion/sfx.py`: `whoosh`, `pop`, `impact`, `riser`, `sparkle`, `mix`
- Tokoh dan prop digambar sebagai sprite vektor dengan supersampling 2–3× lalu di-cache per
  (tokoh, pose, ekspresi). Animasi kecil (kedip, alis) memakai sprite fitur wajah terpisah.
- Frame dirender paralel (`multiprocessing`, seperti `render.py` sekarang) lalu disalurkan ke `ffmpeg`
  lewat pipe.

## 3. Struktur repo (rencana)

```
Video-editor/
├── motion/                      # sudah ada; dipakai ulang
├── andai/                       # engine baru (paket Python)
│   ├── cli.py                   # perintah `python -m andai …`
│   ├── project.py               # baca/tulis file episode, validasi skema
│   ├── vo/
│   │   ├── tts.py               # edge-tts / premium / rekaman
│   │   └── align.py             # faster-whisper + pencocokan naskah
│   ├── plan/
│   │   ├── naskah.py            # parser naskah.md → kalimat, kata, sorotan, tag fakta
│   │   └── timeline.py          # storyboard + words → timeline
│   ├── scene/
│   │   ├── rig.py               # tokoh: proporsi, pose, ekspresi, kedip
│   │   ├── cast.py              # definisi pemeran (dari 03-karakter-dan-set.md)
│   │   ├── sets.py              # pustaka set berlapis (+ dukungan plate)
│   │   ├── props.py             # prop data dan benda
│   │   └── camera.py            # push_in, pull_out, truck, cu, whip, shake, parallax
│   ├── look/
│   │   ├── grade.py             # preset dunia (andai/nyata/netral) × waktu
│   │   └── transitions.py       # cut, dissolve, whip, kedip
│   ├── overlay/
│   │   ├── caption.py           # caption per kata
│   │   ├── bubble.py            # gelembung bicara
│   │   └── source.py            # Kartu Sumber
│   ├── audio/
│   │   └── mix.py               # VO + SFX + musik, ducking, loudnorm
│   ├── render.py                # loop frame, paralel, pipe ke ffmpeg
│   └── qa.py                    # contact sheet, cek aturan, laporan
├── assets/
│   ├── fonts/                   # + Nunito, Fredoka (OFL)
│   ├── sfx/                     # SFX rekaman bebas lisensi (opsional)
│   └── plates/                  # plate latar jalur B (opsional)
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
│   ├── preview/          # frame preview
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
| `python -m andai animatic <slug>` | 6 | Video kasar: kartu teks per shot + caption + VO (sebelum engine visual ada) |
| `python -m andai preview <slug> [--at 12.5 40.2]` | 7–8 | Frame/video 540×960 15 fps |
| `python -m andai render <slug>` | 7–10 | MP4 final + SRT + cover |
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

### 6.2 Caption

```
untuk setiap kata w di words.json:
    tampil dari onset(w) − 1 frame
    sampai onset(kata berikutnya), atau selesai(w) + 0,6 dtk jika itu kata terakhir sebelum jeda panjang
    gaya = sorot jika w.sorot atau w berupa angka, selain itu biasa
```

### 6.3 Grade dan Kedip

- Grade = `grade_waktu[waktu]` lalu `grade_dunia[dunia]`, diterapkan per frame setelah semua lapisan
  dunia dikomposit, **sebelum** overlay (caption, Kartu Sumber tidak ikut di-grade).
- Saat transisi `kedip`, kelopak menutup penuh di frame ke-4 sampai ke-6; grade berganti tepat di frame
  gelap, sehingga perubahan warna tidak terlihat sebagai lompatan.

### 6.4 Kamera dan parallax

- Kamera = (zoom, pan_x, pan_y, rotasi) sebagai fungsi waktu dalam shot, default `push_in` 1,00→1,06
  dengan `ease_in_out`.
- Setiap lapisan set punya faktor kedalaman (langit 0,1; belakang 0,35; tengah 0,7; depan 1,15). Geseran
  kamera dikalikan faktor tersebut sehingga parallax muncul otomatis.

### 6.5 Mix audio

1. VO gabungan (jeda antar-kalimat sesuai naskah; default 0,2 dtk, `[jeda:0.6]` untuk jeda dramatis).
2. SFX dari `timeline.json` (diturunkan dari kolom `sfx` dan transisi storyboard).
3. Musik opsional dengan ducking sidechain terhadap VO.
4. `ffmpeg loudnorm` dua tahap ke −14 LUFS, TP −1 dBTP.

## 7. Target performa

| Mode | Resolusi | fps | Target waktu (episode 90 dtk, 4 core) |
|---|---|---|---|
| Animatic | 540×960 | 15 | < 30 dtk |
| Preview | 540×960 | 15 | < 2 menit |
| Final | 1080×1920 | 30 | < 10 menit |

## 8. Dependensi

```
numpy, opencv-python-headless, pillow, scipy      # sudah ada di requirements.txt
pyyaml, jsonschema                                # baca/validasi file episode
faster-whisper                                    # alignment
edge-tts                                          # TTS gratis (opsional)
ffmpeg (sistem)                                   # encode, loudnorm
```

Font tambahan: Nunito, Fredoka (keduanya SIL OFL) ke `assets/fonts/`.

## 9. Risiko dan mitigasi

| Risiko | Mitigasi |
|---|---|
| Latar prosedural terlihat terlalu sederhana | Investasi di lighting (sinar jendela, bloom, kabut) dan parallax; buka jalur B untuk set yang sulit |
| Whisper salah dengar kata | Kata naskah tetap dipakai; whisper hanya memberi waktu. Kata tak cocok diinterpolasi dan ditandai di QA |
| TTS salah baca singkatan/angka | Naskah wajib angka dalam kata; singkatan dieja ("ka te pe") di naskah ucapan |
| Fakta salah | Gerbang 1 wajib; Kartu Sumber; `check` menolak `[[PERLU SUMBER]]` |
| Render lambat | Cache sprite, preview 540p, render paralel |
| Pustaka set kurang untuk topik baru | Storyboard boleh memakai set terdekat + catatan; set baru ditambahkan per episode |
