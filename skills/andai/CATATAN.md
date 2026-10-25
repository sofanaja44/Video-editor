# Catatan serah-terima ANDAI (baca ini dulu di sesi baru)

Terakhir diperbarui: 2026-10-25. Buku catatan bersama untuk proyek ANDAI: status, keputusan, yang menunggu
persetujuan, dan cara melanjutkan. Perbarui bagian "Status terakhir" dan "Langkah berikutnya" setiap selesai bekerja.

## Status terakhir

- **Episode pilot:** `andai-macet` ("Andai besok pagi kamu bangun, dan macet hilang"), `episodes/andai-macet/`.
  Brief dan 4 fakta bersumber sudah ditulis (`fakta.yaml`, status `draf`). Naskah dan storyboard masih contoh dari templat.
- **◆ Gerbang 1 (fakta) menunggu persetujuan Sopeng.** Jangan menulis naskah final sebelum disetujui.
  Setelah disetujui: ubah `status: draf` menjadi `terverifikasi` di `fakta.yaml`.
- **Engine Blender** (`andai/blender/`): rig + 10 tokoh pemeran + kerumunan + kostum, cahaya, efek, set `jalan_raya`,
  kendaraan, lampu lalu lintas, pose `naik_motor`, `camera.py`. Uji regresi lulus. Belum ada: 6 set lain, prop sisa,
  pose `bangun`/`tidur`, efek sisa, `shot.py`, `composite/`, mix audio. Tabel M0–M5: `ROADMAP.md` (Fase 4).
- **Server GPU sewaan sudah hilang** (dicek 2026-10-25; port SSH menolak, port 22 di IP yang sama milik mesin lain). Tidak
  ada data hilang: semuanya ada di server utama. Belum ada GPU pengganti.
- **Render sementara:** CPU server utama. Blender 5.2.3 sudah terpasang di server utama (`/root/blender`).

## Keputusan yang sudah diambil

| Hal | Keputusan |
|---|---|
| Topik pilot | `andai-macet`; durasi `standar` (±90 dtk); platform TikTok + Reels |
| Suara | ElevenLabs lewat API (suara "Sopeng", model `eleven_v4`), per kalimat; timestamp per kata menggantikan Whisper. Alatnya ada di server utama (catatan memori Claude: `anime-karakter-sora`). **Sistem bisa memblokir skrip itu karena ia membaca kunci API: minta konfirmasi eksplisit Sopeng ("lanjut, pakai API"); jangan pernah mencetak atau membaca kuncinya.** Kuota ±18.500 karakter sampai 18 Nov 2026, dipakai bersama proyek lain; satu take penuh ±1.500 karakter |
| Aset 3D | Dibuat dari kode (gaya mainan seragam). Model gratis dari internet boleh dipakai bila perlu (utamakan lisensi CC0), tetapi belum ada yang dibutuhkan |
| Kota | Suara dan caption tidak menyebut nama kota ("kota besar kita"). Kartu Sumber menulis lembaga dan cakupan data apa adanya (usulan, menunggu setuju) |
| Caption posting | Tanpa kata "satire" atau "sindiran" (preferensi Sopeng) |
| Unggah | Manual oleh Sopeng; tidak ada otomatisasi |
| Warna render | Khronos PBR Neutral (AgX membuat warna pucat) |

## Fakta episode (ringkas; lengkap di `fakta.yaml`)

| # | Isi | Sumber | Catatan |
|---|---|---|---|
| F1 | 117 jam/tahun hilang di jam sibuk (≈ hampir 5 hari) | TomTom Traffic Index 2023, via CNN Indonesia | halaman TomTom tak bisa dibuka; definisi: 10 km pergi-pulang, 230 hari kerja |
| F2 | ±10% perjalanan harian pakai angkutan umum | BPTJ, data 2022 (10,29% tanpa ojek online; 18,45% dengan) | kutipan lewat Investortrust |
| F3 | Rp65 triliun/tahun kerugian macet (≈ Rp178 miliar/hari) | Bappenas via Setkab, 2019 | cakupan Jabodetabek; konversi "per warga" dibuang (penduduk resmi tak terverifikasi) |
| F4 | 39,03% kapasitas jalan hilang karena parkir di badan jalan | Masrul & Utami, 2021 | satu ruas jalan: narasi wajib "satu studi di ruas jalan dekat pasar" |

## Yang menunggu jawaban Sopeng

1. Setujui empat fakta (Gerbang 1), atau minta ganti (mis. F2 pakai 18,45%).
2. Setuju aturan "tanpa nama kota di suara, sumber jujur di kartu"?
3. Konfirmasi "lanjut, pakai API" untuk membuat suara ElevenLabs (setelah naskah disetujui).

## Langkah berikutnya

1. Setelah Gerbang 1: tulis `naskah.md` final (angka dalam kata lewat `{F1}` dst.), hitung durasi → ◆ Gerbang 2.
2. Suara per kalimat → `words.json` → timeline dari jangkar kata (M2).
3. Bangun dunia yang tersisa (M3): set `kamar`, `dapur`, `halte`, `jalan_kampung`, `taman_kota`, `jalan_malam`; prop `jam_weker`,
   `jam_dinding`, `piring`, `papan_nama`, `layangan`, `gerobak_martabak`, prop data `led`; pose `bangun`, `tidur`; efek
   `sinar_jendela`, `asap_knalpot`, `uap_kopi`, `bintang_kilau`.
4. Mesin shot (M4): `shot.py` dengan **preset render** (pratinjau / hemat / penuh / hq), cache per shot yang bisa dilanjutkan,
   lalu `composite/` dan mix audio. Tambahkan mode "lokal" di `andai/gpu/gpu.sh` (render langsung di server utama).
5. Bila Sopeng mau: notebook Colab (`.ipynb`) yang memasang Blender, mengambil kode dari GitHub, merender shot yang belum
   jadi, dan menyimpan ke Google Drive.

## Cara melanjutkan render (tiga jalur)

| Jalur | Kapan | Perkiraan waktu mode hemat / video 90 dtk |
|---|---|---|
| **GPU sewaan baru** (terbaik) | bila Sopeng menyewa lagi: edit `andai/gpu/gpu.env`, lalu `gpu.sh kunci`, `siapkan`, `pulihkan` (±4 menit, sudah diuji) | RTX 5090: ±25 menit–3 jam mode penuh |
| **CPU server utama** | sekarang | mode hemat ±9 jam (15 fps); penuh tidak realistis (±5 hari) |
| **Colab gratis (T4)** | tambahan, manual lewat browser | mode hemat ±1,5–2,5 jam, penuh ±11–21 jam (perkiraan, belum diukur) |

Preset yang dirancang: **pratinjau** 540×960, 8 sampel; **hemat** 720×1280, 16 sampel, tanpa kabut, pantulan 2 (CPU);
**penuh** 1080×1920, 64 sampel, semua efek (GPU); **hq** 128 sampel untuk gambar diam. Rincian dan angka ukur:
`PINDAH-SERVER.md` dan `references/04-arsitektur-pipeline.md` 2.1. Render berat di server utama: pakai `nice -n 10` dan
paling banyak 6 dari 8 thread (server dipakai bersama proyek lain).

## Aturan penting yang sudah dipelajari

- Cycles headless: **wajib `denoising_use_gpu = True`** di GPU (kalau tidak, ±9 dtk/frame). EEVEE tidak jalan di container
  tanpa library grafis NVIDIA. Area light memotong lantai dengan tepi keras: pakai spot. Kabut: kotak volume terbatas, bukan
  volume dunia. Kamera tidak boleh di bawah tanah; set menyembunyikan gedung di antara kamera dan subjek (`Set.pandang`).
- Repo ini **publik**: sebelum push, pindai isi commit dari IP/port server, password, kunci. `andai/gpu/gpu.env` tidak di-commit.
- Aset berharga ada di server utama: `/root/andai-aset/` (Blender, cermin render, snapshot); lihat `MANIFEST.md` di sana
  dan `PINDAH-SERVER.md`.

## Riwayat singkat

- 2026-10-24: server GPU dipasang, benchmark, engine karakter/pemeran/efek, alur server sekali pakai, commit pertama.
- 2026-10-24: episode pilot `andai-macet`: fakta bersumber, set jalan raya, kendaraan, kamera, pose naik_motor.
- 2026-10-25: server GPU hilang; Blender dipasang di server utama; angka render CPU diukur; catatan serah-terima ini ditulis.
