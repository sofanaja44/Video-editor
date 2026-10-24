# Bedah Video Referensi

> Analisis video referensi yang diberikan pengguna (kartun 3D narasi, TikTok, ±2 menit 40 detik).
> Dokumen ini menjelaskan **kenapa** aturan di `01-buku-panduan.md` seperti itu. Videonya sendiri tidak
> disimpan di repo (lihat Buku Panduan 8.3).

## 1. Data teknis

Diukur dengan ffprobe, ffmpeg (`ebur128`, `silencedetect`), dan transkripsi faster-whisper dengan
timestamp per kata.

| Ukuran | Nilai |
|---|---|
| Durasi file | 160,3 dtk (155 dtk narasi + ±4 dtk outro bawaan platform) |
| Medium | **3D sungguhan** (bukan 2.5D): perspektif berubah saat kamera bergerak, tokoh bisa menoleh/berputar, ada bayangan jatuh, sorot lampu, dan fokus kamera (latar kabur). Kemungkinan dibuat di software 3D; tokoh konsisten dan tulisan di adegan selalu tajam. Software persisnya tidak bisa dipastikan dari video. |
| Resolusi / fps | 576×1024 (9:16), 30 fps, H.264 |
| Audio | AAC 44,1 kHz stereo 128 kbps |
| Loudness | −14,1 LUFS terintegrasi, LRA 3,2 LU (sangat rata, VO dikompres) |
| Jumlah kalimat | 43 |
| Jumlah kata | 364 |
| Tempo narasi | **2,35 kata/detik** |
| Durasi kalimat (median) | 3,3 dtk |
| Durasi kata (median) | 0,36 dtk |
| Jeda antar-kalimat | median 0,2 dtk, maksimum 0,38 dtk |
| Musik latar | Hampir tidak ada; di sebagian jeda level turun ke −45 sampai −47 dB |
| SFX | Ada di beberapa jeda (−20 sampai −30 dB): ambience dan efek kejadian |
| Panjang shot | ±2–3 dtk; banyak transisi larut dan whip pan, jarang potong keras |

## 2. Konsep dalam satu paragraf

Narator mengajak "kamu" membayangkan bangun di dunia tanpa korupsi. Sepanjang satu hari (pagi sampai
malam), setiap kenyamanan di dunia itu (jalan mulus, layanan KTP cepat, bansos utuh, berita tanpa kasus
besar) dipasangkan dengan fakta dunia nyata beserta angkanya. Skalanya naik dari jalan desa sampai
kerugian ratusan triliun. Malamnya, si "kamu" ditilang dan refleks menyodorkan uang damai, padahal di
dunia baru tidak ada yang mengenal uang damai. Ternyata yang belum berubah adalah dirinya. Video ditutup
dengan skor korupsi nasional, ajakan menyimpan dompet, lalu kembali ke kamar tidur (loop).

## 3. Peta beat

| Waktu | Beat | Narasi (ringkas) | Visual kunci | Dunia |
|---|---|---|---|---|
| 0:00–0:12 | HOOK + ANDAI-1 (pagi) | Bangun, lubang di depan rumah hilang, jalan mulus, motor meluncur, tukang tambal ban bengong | Kamar pagi + jam weker → jalan mulus → motor sudut rendah → kios ban bertuliskan "SEPI, BOS" | Andai |
| 0:12–0:13 | PIVOT | "Ini bukan sulap." | Topi pesulap (pun visual) | Andai |
| 0:13–0:27 | NYATA-1 | Ekonom mengebor ratusan jalan desa, mengukur pasir/batu, mencocokkan laporan belanja; >¼ uang tidak jadi jalan | Peneliti berhelm + alat ukur, kertas "LAPORAN BELANJA", papan "PROYEK SELESAI" di jalan rusak | Nyata (abu, berkabut) |
| 0:27–0:31 | JEMBATAN-1 | Uang itu ada di bawah ban motormu | Penampang lapisan jalan ASPAL/BATU/PASIR dengan motor di atasnya | Andai |
| 0:31–0:44 | ANDAI-2 | Urus KTP: antre pendek, AC dingin, tanpa amplop/uang rokok/orang dalam, "besok jadi" | Layar antrean "002", laci kosong, toples "UANG ROKOK" bersarang laba-laba, gelembung bicara, kalender sobek | Andai |
| 0:44–0:55 | NYATA-2 | 3 dari 10 orang pernah menyuap untuk layanan publik; proyek e-KTP bocor Rp2,3 T | Antrean panjang malam, kartu raksasa retak dan tumpah, LED "KERUGIAN NEGARA" | Nyata |
| 0:55–1:03 | ANDAI-3 (siang) | Tetangga menerima sembako lengkap, menghitung dua kali | Dapur, kardus sembako, mata bintang | Andai |
| 1:03–1:13 | NYATA-3 | Menteri memotong Rp10 ribu per paket; dikali jutaan paket | Tokoh berjas di gudang, label harga di kardus berjalan, tumpukan "JUTAAN PAKET" | Nyata (gelap) |
| 1:13–1:19 | JEMBATAN-3 | Rp10 ribu kembali jadi telur dan mi instan | Kardus terbuka, telur bersinar | Andai |
| 1:19–1:23 | ANDAI-4 (sore) | Buka berita, tidak ada kasus timah | TV "BERITA SORE: CUACA CERAH • JALAN LANCAR" | Andai |
| 1:23–1:52 | NYATA-4 (eskalasi) | Kasus timah Rp300 T, kerusakan alam; dibagi rata >Rp1 juta per orang; dari Rp100 yang dikorupsi kembali <Rp5; vonis rata-rata 3 tahun 3 bulan | Angka "300" raksasa di lahan tambang rusak, deret warga, kalender tahun, brankas "KAS NEGARA", celengan, neon "SEL VIP" | Nyata |
| 1:52–2:12 | TWIST (malam) | Ditilang karena lampu mati, refleks sodorkan Rp50 ribu, polisi bingung, menulis surat tilang pelan-pelan; yang belum berubah adalah kamu | Motor malam, close-up wajah polisi bingung, surat tilang, Si Kamu berkeringat | Netral malam |
| 2:12–2:26 | REFLEKSI | Skor korupsi 34/100, peringkat dari 180 negara; bukan cuma triliunan di TV, tapi lembaran kecil yang kita selipkan | Si Kamu sebagai murid dengan rapor "SKOR KORUPSI", meteran jarum, deret bendera, TV "KORUPSI TRILIUNAN", uang Rp50 ribu di tangan | Netral |
| 2:26–2:35 | LOOP | Simpan dompet, terima tilang, pulang, tidur; "kalau semua orang mulai menyimpan dompetnya, mungkin…" | Deret warga memegang dompet → kamar tidur + jam weker (= frame pertama) | Andai |
| 2:35–2:40 | (outro platform) | — | Logo platform + nama akun (bukan bagian edit) | — |

## 4. Teknik yang dipakai

1. **Narasi di detik 0.** Tidak ada intro atau judul. Kalimat pertama mulai di 0,00 dtk.
2. **Satu hari sebagai tulang punggung.** "Besok pagi…", "Siangnya…", "Sorenya…", "Malamnya…".
3. **Pasangan dunia dengan grade.** Adegan dunia nyata konsisten pucat, abu-abu, berkabut, atau gelap;
   dunia ideal hangat dan jenuh.
4. **Data diegetik.** Semua angka ada di dalam dunia: kertas laporan, LED, kalender, label harga, TV,
   rapor, angka raksasa. Tidak ada overlay grafik.
5. **Caption satu kata.** Putih, tebal, bulat, bayangan lembut, di ±70% tinggi frame, berganti di onset
   kata. Angka ditulis sebagai kata ("tiga", "puluh", "empat", "dari", "seratus,"), sementara digit hanya
   ada di prop.
6. **Pun visual.** "sulap" → topi pesulap; "uang rokok" → toples bersarang laba-laba; "bocor" → kartu retak.
7. **Detail lucu di dunia ideal.** Tukang tambal ban yang sepi, tetangga menghitung dua kali.
8. **Konversi angka.** Rp300 T → >Rp1 juta per orang, "termasuk nenekmu dan bayi tetangga sebelah".
9. **Eskalasi lalu jatuh ke diri sendiri.** Triliunan → selembar Rp50 ribu.
10. **Tokoh tidak berbicara.** Tidak perlu lip-sync; emosi lewat ekspresi. Dialog tampil sebagai gelembung.
11. **Kamera selalu bergerak.** Push-in pelan, sudut rendah, close-up reaksi, whip pan antar-lokasi.
12. **Loop.** Adegan terakhir = kamar tidur yang sama dengan adegan pertama.

## 5. Klaim fakta di referensi (wajib cek ulang sebelum dipakai)

Daftar ini **bukan** bahan siap pakai. Fungsinya menunjukkan jenis fakta yang cocok untuk format ini dan
mengingatkan bahwa angka di video viral pun perlu diverifikasi.

| Waktu | Klaim | Jenis sumber yang perlu dicari | Catatan |
|---|---|---|---|
| 0:13 | Ekonom mengebor ratusan jalan desa; >¼ dana tidak jadi jalan | Studi lapangan akademik (penelitian Olken tentang jalan desa di Indonesia) | Cek persentase persisnya di makalah aslinya. |
| 0:44 | 3 dari 10 orang mengaku pernah menyuap untuk layanan publik | Survei barometer korupsi internasional | Cek tahun survei. |
| 0:50 | Proyek e-KTP merugikan negara Rp2,3 T | Putusan pengadilan / rilis KPK | Kasus sudah diputus. |
| 1:03 | Potongan Rp10 ribu per paket bansos | Putusan pengadilan | Narasi menyebut peran, bukan nama. |
| 1:23 | Kasus timah Rp300 T, sebagian besar kerusakan alam | Putusan/rilis Kejaksaan dan perhitungan ahli | Cek porsi kerusakan lingkungan. |
| 1:31 | Dibagi rata >Rp1 juta per orang | Hitungan sendiri | 300 T ÷ ±280 juta jiwa ≈ Rp1,07 juta. Konsisten. |
| 1:40 | Dari Rp100 yang dikorupsi pada 2024, kembali <Rp5 | Laporan tren vonis lembaga pemantau korupsi | Cek definisi "kembali" (uang pengganti vs kerugian). |
| 1:47 | Vonis koruptor rata-rata 3 tahun 3 bulan | Laporan tren vonis | Cek tahun laporan. |
| 2:12 | Skor 34/100, peringkat 109 dari 180 negara | Indeks Persepsi Korupsi | Skor dan peringkat berubah tiap tahun. Pastikan keduanya dari edisi yang sama. |

## 6. Pelajaran untuk ANDAI

| Temuan | Jadi aturan |
|---|---|
| Tempo 2,35 kata/dtk, kalimat ±3,3 dtk | Buku Panduan 3.3 dan 3.6 |
| Dunia dibedakan grade | Buku Panduan 4.2, ditambah transisi Kedip sebagai penanda versi kita |
| Angka hanya di prop, caption tetap kata | Buku Panduan 4.4 dan 6.2 |
| Tidak ada sumber di layar | Kita tambah Kartu Sumber (6.4) |
| Tokoh tidak lip-sync | Engine tidak perlu lip-sync; cukup ekspresi (lebih murah dibangun) |
| Medium 3D | Engine kita juga 3D, dibangun sepenuhnya dari kode (three.js), dengan desain tokoh sendiri |
| Hampir tanpa musik | Musik opsional; prioritas VO dan SFX |
| Shot 2–3 dtk, dijangkarkan ke kata | Storyboard menjangkarkan shot ke kata, bukan detik (`05-skema-data.md`) |
| Loop kamar tidur | Buku Panduan 5.3 |
