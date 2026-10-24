# Video-editor — Motion Graphic "Musim Hujan"

Editor motion graphic berbasis Python yang mengubah vlog TikTok (`input/source.mp4`)
menjadi video penuh kata-kata animasi dan efek. Hasil render ada di
`output/musim_hujan_motion.mp4` (1080×1920, 30 fps, ±16,7 detik).

## Isi edit

| Waktu | Teks / grafis | Efek |
|---|---|---|
| 0,0–1,2 s | Judul **MUSIM HUJAN** + "EDISI: KEPLESET OMONGAN SENDIRI" | Slide-in, efek ketik, glitch, zoom-out, flash |
| 1,2–3,0 s | NAMANYA JUGA LAGI **MUSIM HUJAN** · DER! | Kata muncul per kata sesuai suara, **petir** di kata "HUJAN", hujan makin deras |
| 3,3–4,5 s | JADI **JANGAN HERAN** 🤷 | Teks stamp + getar, zoom punch |
| 4,5–5,8 s | KALAU BANYAK YANG **KEPLESET** 🍌 | Teks "kepleset" (slip + goyang), garis polisi **AWAS LICIN**, rambu peringatan, kamera ikut miring |
| 5,8–7,0 s | KARENA **OMONGAN SENDIRI** 🗣 | Stamp, flash, camera shake |
| 7,0–8,3 s | **WKWKWK** 😂 | Huruf bergelombang, emoji tertawa melayang |
| 8,3–9,6 s | **ENJOY IN AJA** 😎🤙 | Starburst berputar, sparkle, light leak, pulse ikut beat musik |
| 9,3–10,9 s | **KABUURR!!** 💨 | Whip-pan blur, speed lines, trail |
| 10,9–12,2 s | **ADUDU LARI-LARI** 🏃 | Teks goyang + bayangan gerak, emoji lari melintas |
| 12,5–14,4 s | ADUH ADA YANG **NELEN LUDAH SENDIRI** 🤭 · GLEK! | Stamp per kata, comic burst, bloom lampu jalan, glitch |
| 14,7–16,7 s | End card: HATI-HATI **KEPLESET OMONGAN SENDIRI** | Freeze frame blur, echo audio, fade out |

Efek global: subtitle bawaan TikTok dihapus (inpainting), color grading teal-orange,
hujan animasi, vignette, film grain, HUD kamera (REC + timecode + sudut viewfinder),
badge "MUSIM HUJAN", progress bar, chromatic aberration ikut beat (±129 BPM), serta
sound effect sintetis (whoosh, petir, pop, impact, slide whistle, glitch, "glek").

## Cara render ulang

```bash
pip install -r requirements.txt     # butuh juga ffmpeg & font Noto Color Emoji
python render.py                    # render penuh -> output/musim_hujan_motion.mp4
python render.py --preview 2.4 5.5  # cek frame tertentu -> output/preview/
```

Struktur:

- `render.py` — timeline: teks per kata, posisi, animasi, kamera, jadwal efek & SFX.
- `motion/text.py` — sprite teks/emoji/bentuk (stroke, glow, gradien) + compositor alpha.
- `motion/fx.py` — easing, color grade, hujan, bloom, glitch, speed lines, petir, light leak.
- `motion/sfx.py` — sound effect sintetis dan mixing audio.
- `assets/fonts/` — Anton, Bangers, Montserrat, JetBrains Mono (SIL Open Font License).

## Skill ANDAI (rancangan)

Folder [`skills/andai/`](skills/andai/README.md) berisi rancangan skill Claude untuk video kartun narasi
berformat "Andai besok pagi kamu bangun, dan [masalah] hilang.": Buku Panduan, bedah video referensi,
bible karakter/set, arsitektur engine, skema data, checklist QA, templat, dan contoh episode pilot.
Engine render-nya belum dibangun; urutan pembangunan ada di `skills/andai/ROADMAP.md`.
