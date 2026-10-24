# Buku Panduan ANDAI

> Pegangan gaya untuk setiap episode ANDAI. Isinya aturan cerita, visual, caption, audio, dan etika.
> Claude membaca buku ini sebelum menulis naskah atau storyboard. Manusia membacanya sebelum menyetujui.
>
> Turunan dari bedah video referensi (lihat `02-bedah-referensi.md`). Yang kita ambil format dan
> tekniknya; karakter, gaya gambar, suara, dan identitasnya milik kita sendiri.

---

## Daftar isi

0. [Cara pakai buku ini](#0-cara-pakai-buku-ini)
1. [DNA format](#1-dna-format)
2. [Versi kita vs referensi](#2-versi-kita-vs-referensi)
3. [Formula naskah](#3-formula-naskah)
4. [Bahasa visual](#4-bahasa-visual)
5. [Tempo dan editing](#5-tempo-dan-editing)
6. [Caption dan teks layar](#6-caption-dan-teks-layar)
7. [Audio](#7-audio)
8. [Fakta, etika, dan hak cipta](#8-fakta-etika-dan-hak-cipta)
9. [Larangan dan kesalahan umum](#9-larangan-dan-kesalahan-umum)
10. [Glosarium](#10-glosarium)

---

## 0. Cara pakai buku ini

- **MUST** = wajib, melanggar berarti episode belum boleh dirilis.
- **SHOULD** = standar; boleh dilanggar kalau ada alasan yang ditulis di `catatan` storyboard.
- **MAY** = pilihan kreatif.
- Angka teknis (detik, piksel, LUFS) adalah nilai awal. Kalau hasil uji di HP berkata lain, ubah di sini
  dulu, baru di kode, supaya buku ini tetap jadi sumber kebenaran.

---

## 1. DNA format

Satu kalimat: **"Andai besok pagi kamu bangun, dan [masalah sehari-hari] hilang."** Lalu penonton diajak
menjalani satu hari di dunia itu, sambil terus dibandingkan dengan dunia nyata lewat data, sampai
akhirnya kamera berbalik ke penonton sendiri.

Enam pilar yang **MUST** ada di setiap episode:

| # | Pilar | Artinya | Kenapa berhasil |
|---|---|---|---|
| 1 | **Orang kedua** | Narator bicara ke "kamu"; tokoh utama = penonton. | Penonton merasa ini cerita tentang dirinya. |
| 2 | **Dua dunia** | Selang-seling *Dunia Andai* (ideal, hangat) dan *Dunia Nyata* (fakta, dingin). | Kontras membuat data terasa, bukan sekadar dibaca. |
| 3 | **Satu hari** | Waktu berjalan pagi → siang → sore → malam → tidur. | Struktur alami, penonton tahu "masih ada lanjutannya". |
| 4 | **Fakta jadi benda** | Setiap angka muncul sebagai benda di dunia cerita (papan, LED, kalender, label harga). | Data lebih mudah diingat dan tidak terasa seperti slide presentasi. |
| 5 | **Twist cermin** | Menjelang akhir, ternyata yang belum berubah adalah si "kamu". | Mengubah video dari "menyalahkan mereka" jadi "mengajak kita". |
| 6 | **Akhir loop** | Kalimat terakhir menggantung ("mungkin…") dan gambar terakhir = gambar pertama. | Penonton menonton ulang tanpa sadar; durasi tonton naik. |

---

## 2. Versi kita vs referensi

Yang kita **pertahankan**: enam pilar di atas, tempo narasi, caption per kata, data diegetik, struktur loop.
Yang kita **ganti**: semua aset dan identitas.

| Aspek | Video referensi | ANDAI (versi kita) |
|---|---|---|
| Gaya gambar | Render 3D (kemungkinan dibuat di software 3D), kepala bola, kaki-tangan lidi | **3D dari kode, gaya "mainan doff"**: dibangun dari bentuk dasar lewat three.js, material doff, bayangan lembut. Semua adegan ditulis sebagai kode, tanpa software 3D manual (lihat `04-arsitektur-pipeline.md`). |
| Tokoh utama | Kaos hijau toska, rambut cokelat | **Si Kamu**: kepala "kacang", jambul hitam, kaos oranye bata, sandal jepit (lihat `03-karakter-dan-set.md`). |
| Pindah dunia | Hanya lewat perubahan warna | **Transisi Kedip**: kelopak mata hitam menutup dari atas-bawah lalu membuka dengan *grade* dunia lain, ditambah bunyi "tik" jam. Nyambung dengan tema bangun tidur. |
| Caption | Putih polos per kata | Putih per kata, **angka dan kata kunci jadi kuning** dengan pop kecil. |
| Sumber data | Tidak ditampilkan | **Kartu Sumber** kecil di setiap fakta Dunia Nyata ("Sumber: ICW, 2024"). |
| Penutup | Outro bawaan platform | Tanpa end card supaya loop mulus. Branding cukup lewat logo kecil di pojok dan profil. |
| Kalimat khas | "Ini bukan sulap", "satu-satunya yang belum berubah adalah kamu" | Bank frasa kita sendiri (bagian 3.5). Kalimat ikonik referensi **MUST NOT** dipakai apa adanya. |

---

## 3. Formula naskah

### 3.1 Struktur beat

Porsi durasi dihitung dari total. Preset durasi ada di 3.6.

| Beat | Kode | Porsi | Fungsi | Pola kalimat |
|---|---|---|---|---|
| Hook | `HOOK` | 3–5% | Kalimat pertama di detik 0. Masalah sehari-hari yang hilang. | "Andai besok pagi kamu bangun, dan [masalah] hilang." |
| Detail Andai | `ANDAI-n` | 8–10% per siklus | 2–4 detail indrawi + 1 detail lucu kecil. | "[Benda] jadi [kondisi]. [Orang] sampai [reaksi lucu]." |
| Pivot | `PIVOT` | 1–2% | Kalimat pendek yang memutar ke dunia nyata. | "Tapi ini bukan dongeng." |
| Fakta Nyata | `NYATA-n` | 10–15% per siklus | 1–2 fakta bersumber, diceritakan sebagai kejadian. | "Di dunia nyata, [pelaku/peran] [kata kerja] [angka]." |
| Konversi | `KONVERSI` | 2–4% | Angka besar dibuat terasa. | "Kalau dibagi rata, itu [angka] untuk setiap [satuan dekat]." |
| Jembatan | `JEMBATAN-n` | 2–3% | Kembali ke Dunia Andai: uang/manfaat itu berubah jadi benda. | "Di duniamu yang baru, [angka] itu jadi [benda konkret] di [tempat]." |
| Twist | `TWIST` | 10–12% | Si Kamu tergoda melakukan kebiasaan lama; dunia baru tidak mengenalnya. | "[Kebiasaan] sudah hilang dari dunia ini. Kecuali dari kamu." |
| Refleksi | `REFLEKSI` | 6–8% | Skor/peringkat nasional + "bukan cuma soal besar, tapi juga yang kecil". | "Angka itu bukan cuma milik [mereka]. Ada bagian kecil milik kita." |
| Penutup loop | `LOOP` | 3–5% | Si Kamu memilih benar, pulang, tidur. Kalimat menggantung. | "Kalau semua orang mulai dari [aksi kecil], mungkin…" |

Siklus `ANDAI → (PIVOT) → NYATA → (KONVERSI) → (JEMBATAN)` diulang 2–5 kali, satu per waktu (pagi, siang,
sore, malam). Beat dalam kurung boleh dilewati. `PIVOT` cukup sekali di siklus pertama; siklus berikutnya
pakai frasa pindah yang lebih ringan ("Padahal, di dunia nyata…"). `JEMBATAN` **SHOULD** ada minimal di
siklus pertama, supaya penonton paham pola "uang yang hilang di dunia nyata jadi benda di Dunia Andai".

### 3.2 Eskalasi skala

Setiap siklus **SHOULD** naik satu tingkat, supaya video makin "berat" menjelang twist:

```
pribadi   →  lingkungan   →  layanan publik  →  nasional/triliunan  →  sistemik (statistik)  →  DIRI SENDIRI
(rumahmu)    (jalan, gang)    (kelurahan)        (kasus besar)           (skor, vonis)           (twist)
```

Twist bekerja karena turun drastis dari skala triliunan ke selembar uang di dompet si Kamu.

### 3.3 Aturan kalimat

1. **MUST** satu gagasan per kalimat, idealnya ≤ 14 kata. Median referensi: 3,3 detik per kalimat.
2. **MUST** angka ditulis sebagai kata di naskah ("tiga puluh empat dari seratus"). Naskah adalah teks
   ucapan; TTS dan caption membacanya apa adanya. Versi digit hanya ada di `fakta.yaml` untuk prop.
3. **MUST** menyebut peran, bukan nama orang ("seorang menteri", "seorang ekonom"). Lihat bab 8.
4. **SHOULD** kata kerja konkret dan detail indrawi: *mulus, dingin, wangi, sepi, bengong*. Hindari kata
   abstrak seperti *efisiensi, tata kelola, integritas*.
5. **SHOULD** satu detail lucu per adegan Andai: orang yang dirugikan oleh dunia ideal secara lucu
   (tukang tambal ban sepi, toples "uang rokok" berdebu).
6. **SHOULD** setiap angka besar diikuti konversi ke skala manusia (per orang, per paket, per hari).
7. **SHOULD** kalimat Dunia Nyata dibuka penanda waktu atau dunia: "Di dunia nyata…", "Waktu pandemi…",
   "Sepanjang tahun 2024…".
8. **MAY** dialog tokoh maksimal 4 kata dan tampil sebagai gelembung bicara, bukan suara tokoh.
9. Gaya bahasa: santai tapi rapi. Pakai "kamu", bukan "lo/gue" atau "Anda". Hindari singkatan chat.

### 3.4 Twist yang baik

- Si Kamu melakukan kebiasaan kecil yang sehari-hari dianggap wajar (uang damai, titip absen, parkir
  liar, buang sampah sembarangan, tergantung topik).
- Tokoh lain di Dunia Andai **bingung**, bukan marah. Dunia baru tidak kenal kebiasaan itu.
- Si Kamu malu (ekspresi `malu_keringat`), lalu memilih yang benar.
- Narator tidak menceramahi. Satu kalimat pengakuan, satu kalimat data, selesai.

### 3.5 Bank frasa ANDAI

Pakai, variasikan, atau tambah. Jangan pakai kalimat ikonik referensi apa adanya.

| Fungsi | Pilihan |
|---|---|
| Hook | "Andai besok pagi kamu bangun, dan [X] hilang." · "Bayangin, besok pagi [X] sudah nggak ada." · "Suatu pagi, kamu bangun di kota yang [X]-nya hilang." |
| Pivot | "Tapi ini bukan dongeng." · "Kedengarannya mustahil? Tunggu dulu." · "Sayangnya, kita belum di sana." |
| Pindah ke nyata | "Padahal, di dunia nyata…" · "Kembali ke dunia kita…" · "Di dunia yang kamu tinggali sekarang…" |
| Jembatan | "Di duniamu yang baru, [angka] itu jadi [benda] di [tempat]." · "Di sini, uang itu nggak hilang. Dia jadi [benda]." |
| Twist | "Kotanya sudah berubah. Kebiasaanmu belum." · "Semua orang sudah lupa caranya. Kecuali kamu." · "Dunia ini nggak kenal [kebiasaan]. Kamu yang masih ingat." |
| Refleksi | "Angka itu bukan cuma soal [skala besar], tapi juga [hal kecil] yang kita lakukan sendiri." |
| Penutup loop | "Kalau semua orang mulai dari [aksi kecil], mungkin…" · "Mungkin besok pagi, kamu bangun… dan [X] benar-benar hilang." |

Penutup **SHOULD** bisa disambung secara gramatikal ke kalimat hook, supaya saat video berputar ulang,
"…mungkin…" langsung bertemu "Andai besok pagi kamu bangun…".

### 3.6 Hitungan durasi

Tempo referensi **2,35 kata/detik**, dihitung dari total durasi sehingga jeda normal antar-kalimat
(median 0,2 detik) sudah termasuk. Jumlah kata kira-kira `durasi × 2,3`; jeda dramatis ditambahkan terpisah.

| Preset | Durasi | Kata | Siklus dunia | Cocok untuk |
|---|---|---|---|---|
| `pendek` | 55–65 dtk | 125–150 | 2 | Uji topik, Reels/Shorts |
| `standar` | 85–95 dtk | 195–220 | 3 | Default TikTok |
| `panjang` | 140–160 dtk | 320–370 | 4–5 | Topik kaya data, setara referensi |

Twist dan Loop **MUST** ada di semua preset. Yang dipangkas adalah jumlah siklus.

---

## 4. Bahasa visual

### 4.1 Gaya gambar

- **3D sungguhan yang dibangun dari kode**: tokoh, set, dan prop disusun dari bentuk dasar (bola, kapsul,
  silinder, lathe) dengan sudut membulat. Contoh hasil uji: `img/uji-3d-perbandingan.jpg`.
- Material doff seperti mainan (roughness 0,45–0,8), tanpa garis tepi.
- Satu cahaya utama (matahari, bulan, atau lampu) dengan bayangan lembut, ditambah cahaya lingkungan tipis
  supaya bayangan tidak hitam pekat.
- Kabut untuk kedalaman; butiran halus (grain) di seluruh frame ditambahkan di tahap komposit.
- Kamera bebas bergerak di ruang 3D, jadi parallax dan perubahan perspektif muncul dengan sendirinya.
- Semua tulisan di dunia cerita memakai font bulat tebal yang sama (lihat 6.1) supaya terasa satu dunia.

### 4.2 Dua dunia

Dunia ditandai oleh *grade* warna. Penonton harus tahu sedang di dunia mana **tanpa membaca apa pun**.

| Parameter | Dunia Andai (`andai`) | Dunia Nyata (`nyata`) |
|---|---|---|
| Saturasi | 1,15–1,25 | 0,35–0,5 |
| Suhu warna | Hangat (+8 sampai +12) | Dingin (−6 sampai −10) |
| Kontras | Lembut, *lift* bayangan | Agak keras, bayangan lebih gelap |
| Kabut/haze | Tipis, keemasan | Tebal, abu-abu (terutama di latar jauh) |
| Bloom | Ada (sumber cahaya berpendar) | Tidak ada |
| Grain | Halus (0,015) | Lebih kasar (0,03) |
| Vignette | Ringan | Sedang |
| Aksen warna | Oranye senja, hijau daun | Merah peringatan untuk angka kerugian |
| Ekspresi tokoh | Senang, santai, bengong lucu | Tegang, licik, lelah, antre |

`netral` (dipakai untuk TWIST dan REFLEKSI) = grade normal, saturasi 1,0, malam yang jujur.

### 4.3 Waktu hari

Waktu memberi tahu penonton posisi dalam cerita. Grade dunia ditumpuk di atas grade waktu.

Di engine 3D, waktu diatur lewat preset cahaya: arah dan warna matahari/bulan, warna langit, serta lampu
yang menyala di malam hari.

| Waktu | Cahaya utama | Langit | Catatan |
|---|---|---|---|
| `pagi` | Matahari rendah, hangat, sinar masuk jendela | Biru muda → kuning pucat | Hook selalu di kamar tidur pagi. |
| `siang` | Terang, bayangan pendek | Biru cerah | Adegan rumah tangga/tetangga. |
| `sore` | Jingga keemasan dari samping | Jingga → ungu | Adegan berita/TV, pulang kerja. |
| `malam` | Lampu jalan kuning, lampu teras | Biru tua | Twist selalu malam. |

### 4.4 Fakta jadi benda (data diegetik)

Aturan inti ANDAI: **tidak ada infografik melayang**. Setiap angka muncul sebagai benda di dunia cerita.

| Perangkat | Dipakai untuk | Contoh |
|---|---|---|
| Papan nama/spanduk | Nama program, nama lokasi, ironi | Papan "PROYEK SELESAI" di jalan yang rusak |
| Layar LED/papan digital | Angka kerugian, nomor antrean | "KERUGIAN NEGARA Rp2,3 T" berwarna merah |
| Kalender sobek | Tahun, durasi, "besok" | Kalender berganti dari JAN 2025 ke APR 2028 |
| Label harga | Potongan per unit | Label "Rp10.000" tergantung di kardus |
| Layar TV + teks berjalan | Berita, kontras dunia | "BERITA SORE — CUACA CERAH • JALAN LANCAR" |
| Rapor/meteran (gauge) | Skor dan peringkat | Jarum meteran berhenti di 34/100 |
| Angka raksasa | Angka utama satu segmen | Angka "300" setinggi rumah di lahan rusak |
| Tumpukan/kardus/toples | Jumlah, akumulasi, "tidak terpakai" | Toples "UANG ROKOK" bersarang laba-laba |
| Penggaris bendera | Peringkat antarnegara | Deret bendera fiktif, satu disorot |
| Celengan/brankas | Uang negara yang kembali | Celengan kecil di samping brankas besar |

Aturan:
- **MUST** digit hanya muncul di prop; caption tetap mengikuti ucapan (kata).
- **MUST** satu angka utama per shot. Angka kedua masuk di shot berikutnya.
- **SHOULD** angka masuk frame bersama aksi (kalender disobek, LED menyala, label diayun), bukan diam
  sejak awal shot.
- **SHOULD** angka tampil ≥ 1,2 detik dan cukup besar untuk dibaca di HP (tinggi digit ≥ 6% tinggi frame).
- **MUST** setiap fakta Dunia Nyata disertai Kartu Sumber (6.4).

### 4.5 Pun visual

Kata kunci di narasi diterjemahkan jadi benda literal di frame. Ini sumber humor visual utama.

| Kata di narasi | Visual |
|---|---|
| "bukan dongeng" | Buku dongeng ditutup keras |
| "uang rokok" sudah tidak ada | Toples berlabel "UANG ROKOK" penuh debu dan sarang laba-laba |
| "bocor" | Kartu raksasa retak, isinya tumpah |
| "besok jadi" | Kalender disobek satu halaman |
| "dibagi rata" | Kue/tumpukan uang dipotong ke deretan warga |

Saat membuat storyboard, tandai setiap pun di kolom `catatan` dengan awalan `pun:`.

### 4.6 Akting karakter

- Narator yang bicara; tokoh **tidak** lip-sync. Tokoh bereaksi lewat wajah dan pose.
- Wajah > tubuh: emosi dibawa alis, mata, mulut, plus aksesori (keringat, pipi merah, mata bintang).
- Setiap shot dengan tokoh **SHOULD** punya satu perubahan ekspresi atau gerak kecil (kedip, menoleh,
  bahu naik), supaya frame tidak terasa seperti foto.
- Reaksi lucu pakai ekspresi berlebihan: `mata_bintang` (senang berlebihan), `bengong`, `malu_keringat`.
- Daftar ekspresi dan pose ada di `03-karakter-dan-set.md`.

### 4.7 Komposisi 9:16 dan zona aman

Kanvas 1080×1920. UI TikTok/Reels menutupi pinggir layar.

```
 ┌──────────────────────────┐  y=0
 │  ░░ zona UI atas ░░░░░░  │  0–10%   jangan taruh teks penting
 │                          │
 │      SUBJEK UTAMA        │  18–60%  wajah/angka utama di sini
 │      (kepala tokoh,      │
 │       angka di prop)     │
 │                       ░░ │
 │  ═══ caption 66–72% ═══ ░░│  ← pita caption (tengah, y≈69%)
 │                       ░░ │  kanan 13%: tombol like/komen/share
 │  [Sumber: …]          ░░ │  ← Kartu Sumber, kiri, di atas zona bawah
 │  ░░ zona UI bawah ░░░░░░ │  80–100% nama akun, deskripsi, musik
 └──────────────────────────┘  y=1920
```

- **MUST** wajah tokoh dan angka utama tidak tertutup pita caption.
- **SHOULD** subjek sedikit ke kiri dari tengah (karena kanan tertutup tombol).

### 4.8 Kamera

**MUST** setiap shot bergerak. Kamera diam terasa seperti slide.

| Gerak | Kode | Default | Kapan |
|---|---|---|---|
| Push-in pelan | `push_in` | zoom 1,00 → 1,06 sepanjang shot, ease in-out | Default semua shot |
| Pull-out | `pull_out` | 1,08 → 1,00 | Mengungkap skala (tumpukan, antrean panjang) |
| Geser samping | `truck` | 3–5% lebar frame | Deretan benda/orang, parallax terasa |
| Geser vertikal | `tilt` | 8–12% tinggi frame | Mengungkap langit, gedung, tumpukan tinggi |
| Sudut rendah | `rendah` | Kamera di bawah, sedikit menengadah | Momen "keren" di Dunia Andai, angka raksasa |
| Orbit | `orbit` | Memutar 5–15° mengelilingi target | Memperlihatkan bentuk 3D benda/tokoh; adegan Andai yang santai |
| Close-up reaksi | `cu` | Zoom 1,4–1,8 ke wajah (lensa 50–85 mm) | Reaksi lucu, twist |
| Whip pan | `whip` | Blur gerak 6–8 frame | Pindah lokasi/waktu dalam dunia yang sama |
| Goyang halus | `shake` | 2–4 px | Kejutan (retak, angka kerugian muncul) |

---

## 5. Tempo dan editing

### 5.1 Panjang shot

- **SHOULD** 1,5–3,5 detik per shot; kira-kira satu shot per klausa narasi.
- **MUST** pergantian shot jatuh tepat di awal kata (onset), idealnya kata kunci klausa baru, bukan di
  tengah kata atau di jeda acak. Storyboard menjangkarkan shot ke kata, bukan ke detik (lihat
  `05-skema-data.md`).
- **MAY** shot dengan angka penting dibiarkan hingga 4 detik.

### 5.2 Transisi

| Transisi | Kode | Durasi | Dipakai saat |
|---|---|---|---|
| Potong langsung | `cut` | 0 | Default dalam satu adegan |
| Larut (dissolve) | `dissolve` | 8–12 frame | Antar-shot dalam satu dunia dan waktu |
| Whip pan | `whip` | 6–8 frame | Pindah lokasi atau waktu dalam dunia yang sama |
| **Kedip** (khas ANDAI) | `kedip` | 10 frame: tutup 4, gelap 2, buka 4 | **Setiap pergantian dunia** (andai ↔ nyata) dan dari LOOP ke awal |
| Fade ke hitam | `fade` | 12 frame | Tidak dipakai. Akhir video memakai `kedip` supaya loop mulus. |

Spesifikasi **Kedip**: dua bidang hitam melengkung (seperti kelopak mata) bergerak dari atas dan bawah
hingga bertemu di tengah (ease-in), tahan 2 frame, lalu membuka (ease-out) dengan grade dunia baru sudah
aktif. Bunyi "tik" jam pelan di frame tutup. Pinggir kelopak diberi blur 12 px agar lembut.

### 5.3 Desain loop

- **MUST** frame terakhir (setelah "mungkin…") = set dan pose yang sama dengan frame pertama: kamar tidur
  pagi, Si Kamu baru bangun, jam weker di meja.
- **MUST** kalimat pertama mulai di frame 0, tanpa intro, judul, atau logo animasi.
- **SHOULD** 0,3–0,5 detik hening setelah "mungkin…", lalu `kedip` menutup di frame terakhir, sehingga
  saat video berputar ulang kelopak "membuka" ke kamar pagi.

---

## 6. Caption dan teks layar

### 6.1 Font

| Peran | Font (lisensi SIL OFL) | Catatan |
|---|---|---|
| Caption | **Nunito Black** | Bulat dan tebal, mirip nuansa referensi tanpa menyalin. |
| Tulisan di dunia (papan, LED, label) | **Fredoka SemiBold/Bold** | Satu keluarga untuk semua prop. |
| Angka LED | Fredoka + efek titik LED | Atau font dot-matrix berlisensi OFL. |
| Kartu Sumber | Nunito Bold | Kecil, abu terang. |

Font disimpan di `assets/fonts/` beserta `OFL.txt`. Jangan pakai font berlisensi tertutup.

### 6.2 Caption per kata

| Atribut | Nilai |
|---|---|
| Satuan | **Satu kata per tampilan**, berganti tepat di onset kata (boleh maju 1 frame). |
| Huruf | Persis seperti ucapan: huruf kecil, kecuali awal kalimat dan nama diri. Tanda baca dipertahankan (`mulus,` `rupiah.` `mungkin…`). |
| Angka | Ditulis kata ("tiga puluh empat"). Bilangan multi-kata tampil per kata. |
| Ukuran | 68 px pada lebar 1080 (tinggi huruf kapital ±4% tinggi frame). |
| Warna | Putih `#FFFFFF`. **Kata kunci dan angka**: kuning `#FFD23F`. |
| Bayangan | Hitam 55%, geser (0, 4) px, blur 8 px. Tanpa outline tebal. |
| Posisi | Tengah horizontal, garis dasar di y = 69% tinggi frame. |
| Animasi | Kata biasa: muncul instan. Kata sorotan: skala 0,85 → 1,08 → 1,0 dalam 120 ms. |
| Jeda | Kata terakhir kalimat tetap tampil sampai kata berikutnya muncul, maksimal 0,6 detik setelah selesai diucapkan, lalu hilang. |

Kata sorotan ditandai di naskah dengan `*kata*`. Angka otomatis disorot.

### 6.3 Gelembung bicara

Untuk dialog pendek tokoh (≤ 4 kata): gelembung putih membulat, ekor ke arah mulut tokoh, teks hitam
Fredoka Bold 56 px. Muncul dengan pop 150 ms, tampil selama kalimat itu diucapkan narator. Caption tetap
jalan seperti biasa.

### 6.4 Kartu Sumber (khas ANDAI)

- Teks kecil: `Sumber: [lembaga], [tahun]`. Nunito Bold 30 px, putih 85%, latar pil hitam 35%.
- Posisi kiri bawah, di atas zona UI bawah (y ≈ 77%).
- Muncul bersamaan dengan angka di prop, tampil 2,5 detik, fade 6 frame.
- **MUST** ada untuk setiap fakta Dunia Nyata. Detail lengkap sumber disimpan di `fakta.yaml` dan bisa
  ditempel di deskripsi video.

---

## 7. Audio

### 7.1 Voice-over

- Satu narator sepanjang episode, nada tenang seperti teman yang bercerita, bukan pembaca berita.
- Tempo target 2,3–2,4 kata/detik. Jeda antar-kalimat 0,15–0,3 detik; jeda dramatis (sebelum twist dan
  sebelum "mungkin…") 0,5–0,8 detik.
- Pilihan sumber suara (keputusan di `ROADMAP.md`):
  1. Rekaman suara sendiri: paling khas dan paling "versi kita".
  2. TTS gratis (mis. suara neural Bahasa Indonesia di edge-tts): cepat, konsisten, cocok untuk prototipe.
  3. TTS premium/kloning suara sendiri: kualitas terbaik, berbayar.
- Rekaman sendiri: WAV 48 kHz 24-bit, ruang kering, jarak mik 15–20 cm, satu kalimat per take.

### 7.2 Musik

- **MAY** pad atau ambient tipis. Referensi hampir tanpa musik: jeda antar-kalimat turun ke −45 dB.
- Jika dipakai: −30 LUFS di bawah VO, ducking 6 dB saat narator bicara, berganti warna saat pindah dunia
  (Andai: hangat/mayor; Nyata: dingin/drone).
- **MUST** musik bebas royalti dengan lisensi tercatat di `brief.yaml`.

### 7.3 SFX

Ringan dan jarang. SFX menegaskan kejadian, bukan mengisi setiap detik.

| Kejadian | SFX |
|---|---|
| Transisi `kedip` | "tik" jam pelan |
| Transisi `whip` | whoosh pendek |
| Angka/LED menyala | ding/beep elektronik |
| Uang, label harga | cring koin / mesin kasir |
| "bocor", retak | kaca retak |
| Kalender disobek | sobekan kertas |
| Reaksi lucu | pop kecil |
| Ambience per set | burung pagi, AC kantor, jangkrik malam (−35 LUFS) |

Repo ini sudah punya SFX sintetis (`motion/sfx.py`: whoosh, pop, impact, riser, sparkle) yang bisa
dipakai ulang.

### 7.4 Master

| Ukuran | Target | Referensi |
|---|---|---|
| Loudness terintegrasi | −14 LUFS | −14,1 LUFS |
| True peak | ≤ −1 dBTP | — |
| Loudness range | ≤ 5 LU | 3,2 LU |
| Format | AAC 192 kbps, 48 kHz, stereo | AAC 128 kbps, 44,1 kHz |

---

## 8. Fakta, etika, dan hak cipta

### 8.1 Fakta

- **MUST** setiap angka punya sumber kredibel dan tahun: laporan lembaga, putusan pengadilan, studi
  akademik, atau media arus utama yang mengutip sumber primer. Dicatat di `fakta.yaml`.
- **MUST** skor dan peringkat dari edisi/tahun yang sama. Indeks seperti IPK berubah setiap tahun;
  jangan campur skor tahun A dengan peringkat tahun B.
- **MUST** hitungan konversi ditulis rumusnya di `fakta.yaml` (mis. `300 T ÷ 280 juta jiwa ≈ Rp1,07 juta`).
- **SHOULD** pakai kata seperti "lebih dari" atau "hampir" hanya jika angkanya memang begitu.
- Claude **MUST NOT** mengarang angka. Jika sumber belum ditemukan, tulis `[[PERLU SUMBER]]` dan berhenti
  di Gerbang 1.

### 8.2 Etika satire

- **MUST** sebut peran, bukan nama ("seorang menteri"), dan hanya untuk kasus yang sudah diputus
  pengadilan.
- **MUST NOT** desain tokoh yang mirip wajah atau ciri khas orang nyata.
- **MUST NOT** memakai logo, lambang, atau seragam persis milik lembaga nyata. Pakai versi fiktif yang
  generik (seragam cokelat tanpa lambang, papan "KANTOR LAYANAN").
- **MUST NOT** meniru desain uang kertas rupiah. Pakai uang fiktif bergaya kartun dengan nominal saja.
- Twist mengajak, bukan mempermalukan penonton.

### 8.3 Hak cipta dan orisinalitas

- Yang kita tiru: **format dan teknik** (struktur dua dunia, caption per kata, data diegetik, loop).
  Ide dan teknik tidak dilindungi hak cipta.
- Yang **MUST NOT** ditiru: karakter, desain set, kalimat khas, nama akun, watermark, dan potongan
  video/audio referensi.
- File video referensi hanya untuk analisis internal dan **MUST NOT** di-commit ke repo atau dipakai di
  hasil render.

### 8.4 Label AI

Jika memakai suara TTS atau gambar buatan AI, **MUST** mengaktifkan label konten AI di platform sesuai
aturan platform yang berlaku.

---

## 9. Larangan dan kesalahan umum

| Jangan | Kenapa | Lakukan ini |
|---|---|---|
| Membuka dengan judul, logo, atau "Halo guys" | Penonton menggulir lewat dalam 1 detik | Kalimat hook di frame 0 |
| Infografik melayang (diagram, bar chart overlay) | Merusak dunia cerita, terasa seperti presentasi | Fakta jadi benda (4.4) |
| Caption satu kalimat penuh | Mata sibuk membaca, gambar tidak dilihat | Satu kata per tampilan |
| Kamera diam | Terasa seperti slide | `push_in` minimal |
| Dua angka dalam satu shot | Tidak ada yang teringat | Satu angka per shot |
| Dunia Nyata dengan warna cerah | Penonton bingung sedang di dunia mana | Grade `nyata` (4.2) |
| Menyebut nama pejabat | Risiko hukum, mengalihkan dari pesan | Sebut peran |
| Twist yang menceramahi | Penonton defensif | Tokoh bingung, Si Kamu malu, satu kalimat data |
| Penutup "Jangan lupa follow!" | Merusak loop | Kalimat menggantung → `kedip` → awal |
| Angka tanpa sumber | Bisa jadi hoaks, merusak kepercayaan | Kartu Sumber dan `fakta.yaml` |

---

## 10. Glosarium

| Istilah | Arti |
|---|---|
| Dunia Andai | Dunia ideal tempat masalah sudah hilang. Grade hangat. |
| Dunia Nyata | Dunia sekarang, berisi fakta dan data. Grade dingin dan pucat. |
| Siklus | Satu putaran ANDAI → NYATA → JEMBATAN. |
| Data diegetik | Angka yang muncul sebagai benda di dalam dunia cerita. |
| Grade | Pengaturan warna dan cahaya seluruh frame. |
| Onset | Saat sebuah kata mulai diucapkan. |
| Jangkar (anchor) | Kata di naskah tempat sebuah shot dimulai. |
| Kedip | Transisi khas ANDAI berbentuk kelopak mata menutup lalu membuka. |
| Kartu Sumber | Label kecil sumber data di frame. |
| Pun visual | Kata di narasi yang diterjemahkan jadi benda literal di gambar. |
