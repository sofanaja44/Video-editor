# QA dan Gerbang Persetujuan ANDAI

> Claude berhenti di setiap gerbang dan meminta persetujuan pengguna sebelum lanjut. Checklist dipakai
> Claude untuk memeriksa diri sendiri sebelum menyerahkan hasil, dan oleh `andai check` / `andai qa`
> untuk butir yang bisa dicek otomatis (ditandai ⚙).

## 1. Gerbang

| Gerbang | Setelah tahap | Yang diserahkan ke pengguna | Pertanyaan ke pengguna |
|---|---|---|---|
| **G1 Konsep & Fakta** | Riset | Ringkasan konsep (topik, kebiasaan twist, aksi penutup) + tabel fakta dengan sumber | "Fakta dan sudut ceritanya sudah oke?" |
| **G2 Naskah** | Naskah | `naskah.md` + estimasi durasi | "Naskahnya sudah pas? Ada kalimat yang mau diganti?" |
| **G3 Storyboard** | Storyboard | Tabel shot ringkas (waktu perkiraan, set, aksi, data, transisi) | "Visualnya sesuai bayangan?" |
| **G4 Preview** | Preview/animatic | Video 540p atau contact sheet + laporan QA | "Tempo, caption, dan audionya sudah enak?" |
| **G5 Final** | Render | MP4 final + SRT + cover + teks deskripsi berisi sumber | "Siap diunggah?" |

Pengguna boleh meminta melompati gerbang ("langsung render saja"). Claude mencatatnya, tapi G1 (fakta)
tidak boleh dilompati jika ada angka yang belum bersumber.

## 2. Checklist

### 2.1 Fakta (G1)
- [ ] ⚙ Setiap `{Fn}` di naskah ada di `fakta.yaml` dengan `status: terverifikasi`.
- [ ] ⚙ Tidak ada `[[PERLU SUMBER]]`.
- [ ] Skor dan peringkat berasal dari edisi/tahun yang sama.
- [ ] Rumus konversi benar (hitung ulang).
- [ ] Tokoh nyata disebut lewat peran; kasusnya sudah diputus pengadilan.

### 2.2 Naskah (G2)
- [ ] ⚙ Kalimat pertama adalah hook (beat `HOOK`), tanpa salam/intro.
- [ ] ⚙ Semua beat wajib ada: HOOK, ≥2 siklus ANDAI/NYATA, TWIST, REFLEKSI, LOOP.
- [ ] ⚙ Estimasi durasi (jumlah kata ÷ 2,35, ditambah jeda dramatis `[jeda:…]` di atas 0,2 dtk) masuk rentang preset.
- [ ] ⚙ Tidak ada kalimat > 18 kata (peringatan di > 14).
- [ ] ⚙ Tidak ada digit di luar `{Fn}`.
- [ ] Waktu hari berjalan maju (pagi → malam).
- [ ] Skala naik tiap siklus; twist turun ke diri sendiri.
- [ ] Setiap adegan Andai punya satu detail lucu.
- [ ] Twist tidak menceramahi; tokoh Dunia Andai bingung, bukan marah.
- [ ] Kalimat penutup menggantung dan bisa disambung ke hook.
- [ ] Tidak memakai kalimat ikonik video referensi apa adanya.

### 2.3 Storyboard (G3)
- [ ] ⚙ Shot pertama berjangkar di K01 kata 0; jangkar berurutan maju.
- [ ] ⚙ Pergantian dunia selalu memakai `kedip`.
- [ ] ⚙ Setiap fakta punya shot dengan `data.fakta`.
- [ ] ⚙ Shot terakhir = set dan pose shot pertama.
- [ ] ⚙ Perkiraan durasi tiap shot 1,5–3,5 dtk (peringatan di luar rentang, gagal di luar 1,0–4,5).
- [ ] Satu angka utama per shot.
- [ ] Setiap shot punya gerak kamera dan minimal satu perubahan kecil (ekspresi/aksi/prop).
- [ ] Pun visual dipakai minimal sekali per siklus.
- [ ] Tidak ada logo, lambang, atau uang kertas asli.

### 2.4 Visual (G4/G5)
- [ ] Dunia bisa ditebak dari warna saja (tes: tutup audio, lihat contact sheet).
- [ ] ⚙ Wajah tokoh dan angka utama tidak berada di pita caption (66–72%) atau zona UI.
- [ ] Angka di prop terbaca di layar HP (tinggi digit ≥ 6% tinggi frame).
- [ ] Tidak ada frame kosong, kedipan hitam tak sengaja, atau sprite terpotong.
- [ ] Loop mulus: putar 3 detik terakhir lalu 3 detik pertama berurutan.

### 2.5 Caption (G4/G5)
- [ ] ⚙ Setiap kata naskah muncul tepat sekali, berurutan.
- [ ] ⚙ Selisih onset caption vs onset kata ≤ 2 frame (dari `words.json`).
- [ ] ⚙ Kata `interp: true` didaftar di laporan untuk dicek manual.
- [ ] Ejaan dan tanda baca persis seperti naskah.
- [ ] Angka dan kata kunci tersorot kuning.
- [ ] Kartu Sumber muncul di setiap fakta Dunia Nyata.

### 2.6 Audio (G4/G5)
- [ ] ⚙ Loudness −14 LUFS ±1, true peak ≤ −1 dBTP.
- [ ] VO jelas di atas musik dan SFX (tes dengan speaker HP).
- [ ] Pengucapan angka, singkatan, dan nama tempat benar.
- [ ] SFX tidak menutupi kata.
- [ ] Musik (jika ada) berlisensi dan tercatat di `brief.yaml`.

### 2.7 Teknis ekspor (G5)
- [ ] ⚙ 1080×1920, 30 fps, H.264 High, yuv420p, `+faststart`.
- [ ] ⚙ AAC 48 kHz stereo 192 kbps.
- [ ] ⚙ Durasi sesuai preset.
- [ ] File `.srt` dan `cover.jpg` ada.
- [ ] Teks deskripsi berisi daftar sumber lengkap dari `fakta.yaml`.
- [ ] Label konten AI diaktifkan saat unggah jika memakai TTS/gambar AI.

## 3. Laporan QA otomatis (`andai qa`)

`build/qa/laporan.md` berisi:
- Ringkasan lulus/peringatan/gagal per bagian di atas.
- Contact sheet: satu frame per shot (di tengah shot) dengan label ID shot, dunia, waktu.
- Grafik sederhana durasi shot (teks).
- Daftar kata hasil interpolasi.
- Hasil pengukuran loudness.

## 4. Kasus uji skill

Dipakai untuk menguji apakah skill memicu dan berperilaku benar (misalnya dengan `skill-creator`).

| # | Prompt pengguna | Perilaku yang diharapkan |
|---|---|---|
| 1 | "Bikinin video kayak gini tapi soal sampah plastik" | Skill terpicu; mulai dari brief; mencari fakta bersumber; berhenti di G1. |
| 2 | "Buat naskah ANDAI 60 detik soal pungli parkir" | Naskah preset `pendek` dengan semua beat wajib; angka tanpa sumber ditandai `[[PERLU SUMBER]]`, bukan dikarang. |
| 3 | "Langsung render aja, nggak usah tanya-tanya" | Lewati G2–G4, tetap tahan di G1 jika ada fakta belum bersumber, dan bilang alasannya. |
| 4 | "Pakai nama menterinya biar jelas" | Menolak dengan sopan, menjelaskan aturan peran (Buku Panduan 8.2), menawarkan alternatif. |
| 5 | "Ganti suaranya jadi rekaman saya" | Minta file per kalimat sesuai ID, jalankan ulang `align` dan `plan`; storyboard tidak diubah. |
| 6 | "Edit video vlog saya biar ada teks animasi" | Skill **tidak** terpicu (itu pekerjaan edit vlog biasa, bukan format ANDAI). |
