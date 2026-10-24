# Karakter, Set, dan Prop ANDAI

> "Bible" visual versi kita. Engine menggambar semuanya secara prosedural dari parameter di bawah,
> sehingga tokoh selalu konsisten di setiap episode. Kode tidak boleh menyimpang dari dokumen ini tanpa
> memperbaruinya dulu.

## 1. Prinsip desain

1. **Siluet terbaca di HP.** Tokoh dikenali dari siluet dan warna baju, meski kecil.
2. **Kepala besar, wajah ekspresif.** Emosi dibawa alis dan mata.
3. **Dibangun dari bentuk dasar.** Elips, kapsul, kurva. Mudah digambar engine dan mudah dianimasikan.
4. **Indonesia sehari-hari.** Sandal jepit, motor bebek, warung, kerudung, kopiah, rumah berpagar.
5. **Beda dari referensi.** Kepala referensi bola sempurna dengan tangan-kaki lidi. Kepala kita "kacang"
   (lebih lebar di pipi), lengan dan kaki berbentuk kapsul tebal, tangan bulat tanpa jari (mitten).

## 2. Rig tokoh

### 2.1 Proporsi (satuan `u`, tinggi total 6u)

```
        ___
      /     \        Kepala "kacang": lebar 2.1u, tinggi 2.4u
     | ◉   ◉ |       (bagian pipi 8% lebih lebar dari dahi)
     |   ‿   |
      \_____/
        | |          Leher: tidak ada (kepala menempel ke badan)
      /‾‾‾‾‾\
     |  KAOS |       Badan kapsul: lebar 1.3u, tinggi 1.8u
      \_____/
       |   |         Kaki kapsul: 0.32u tebal, 1.8u panjang
       ◖   ◗         Sandal/sepatu: setengah elips 0.6u
```

| Bagian | Bentuk | Titik engsel |
|---|---|---|
| Kepala | Elips kacang dengan gradien radial (terang kiri atas) | Pangkal kepala (bisa miring ±15°, menoleh lewat geser fitur wajah ±12% lebar) |
| Badan | Kapsul | Pinggul (condong ±10°) |
| Lengan | Kapsul 0,28u, 2 ruas | Bahu, siku |
| Tangan | Lingkaran 0,34u (mitten) | Pergelangan (bisa pegang prop) |
| Kaki | Kapsul 0,32u, 2 ruas | Pinggul, lutut |
| Alas kaki | Setengah elips | — |

Gaya render: isi gradien, garis tepi 3 px warna 35% lebih gelap dari isi, rim light 2 px di sisi yang
terkena cahaya, bayangan kontak elips 40% hitam blur 10 px di bawah kaki.

### 2.2 Wajah

| Fitur | Parameter |
|---|---|
| Mata | Elips putih (lebar 0,42u), pupil hitam (0,16u), titik kilau putih. Param: `skala` 0,6–1,4, `pupil` (x, y) −1..1, `kelopak` 0 (terbuka) .. 1 (tertutup) |
| Alis | Kurva tebal 0,09u. Param: `sudut` −30°..+30°, `naik` −0,1..+0,2u. Pembawa emosi utama. |
| Mulut | Param: `bentuk` (garis, senyum, tawa_terbuka, o, gelombang, cemberut, seringai), `lebar` |
| Aksesori | `keringat` (tetes biru di pelipis), `blush` (elips merah muda 40%), `bintang` (mata jadi bintang), `zzz`, `kaget_garis` (garis kejut di atas kepala) |

Kedip otomatis setiap 2,5–4 detik (acak per tokoh, durasi 4 frame), kecuali ekspresi `tidur`.

### 2.3 Daftar ekspresi

| Kode | Alis | Mata | Mulut | Aksesori | Dipakai untuk |
|---|---|---|---|---|---|
| `netral` | datar | 1,0 | garis | — | Default |
| `senyum` | naik sedikit | 0,9, kelopak 0,2 | senyum | — | Dunia Andai |
| `tawa` | naik | kelopak 0,8 (melengkung) | tawa_terbuka | — | Detail lucu |
| `kaget` | naik tinggi | 1,3 | o | kaget_garis | Angka besar muncul |
| `bengong` | datar | 1,1, pupil ke atas | o kecil | — | Tukang yang "dirugikan" dunia ideal |
| `bingung` | satu naik satu turun | 1,0 | gelombang | — | Tokoh Dunia Andai saat twist |
| `malu_keringat` | turun di tengah | 0,9, pupil ke samping | gelombang | keringat, blush | Si Kamu saat twist |
| `sedih` | turun di luar | 1,0, kilau besar | cemberut | — | Dunia Nyata |
| `licik` | turun di dalam | kelopak 0,5 | seringai | — | Arketipe pejabat korup |
| `mata_bintang` | naik | bintang | tawa_terbuka | — | Senang berlebihan |
| `lelah` | datar | kelopak 0,6 | garis turun | — | Antrean dunia nyata |
| `tidur` | datar | kelopak 1,0 | o kecil | zzz | Adegan tidur / loop |

### 2.4 Daftar pose

`berdiri`, `jalan` (siklus 8 frame), `duduk`, `naik_motor`, `menunjuk`, `angkat_bahu`, `pegang` (prop di
tangan kanan), `rogoh_saku`, `sodor` (menyodorkan benda), `menulis`, `antre` (berdiri, bahu turun),
`tidur` (berbaring), `bangun` (duduk di kasur, tangan meregang).

## 3. Pemeran (versi kita)

Semua tokoh fiktif. Kulit beragam sesuai Indonesia: `kulit_terang #F2C9A0`, `kulit_sawo #C98E5A`,
`kulit_gelap #8D5A3B`.

| ID | Tokoh | Ciri | Palet baju |
|---|---|---|---|
| `kamu` | **Si Kamu** (protagonis, mewakili penonton) | Jambul hitam mencuat, kulit sawo, kaos oblong, celana jeans, sandal jepit | Kaos `#E8743B` oranye bata, celana `#2F4A6D`, sandal `#3FA34D` |
| `tetangga` | Bu Tetangga | Kerudung segi empat, daster bermotif titik | Kerudung `#4FA88B`, daster `#F2B84B` |
| `petugas` | Petugas layanan | Seragam krem berkantong dua, tanpa lambang | `#D9C7A1`, celana `#5B4A3A` |
| `polisi` | Polisi | Seragam cokelat tua + topi pet, tanpa lambang/pangkat asli | `#6B4F33` |
| `pejabat` | Arketipe pejabat korup | Jas hitam, dasi merah, kacamata hitam bundar, ekspresi default `licik` | Jas `#22252B`, dasi `#C8333B` |
| `peneliti` | Peneliti/ekonom | Helm proyek kuning, kacamata bulat, rompi | Helm `#F5C542`, rompi `#E57A2E` |
| `nenek` | Nenek | Rambut putih disanggul, kacamata, kebaya | `#9C6FB0` |
| `bayi` | Bayi tetangga | Kepala 70% badan, popok | `#FFFFFF` |
| `tukang_ban` | Tukang tambal ban | Kaos singlet, handuk di leher, topi terbalik | Singlet `#EDEDED`, topi `#C8333B` |
| `ibu` | Ibu si Kamu | Rambut disanggul atau kerudung, kemeja longgar | Kerudung `#B5546A`, baju `#F4E3C3` |
| `warga_1`, `warga_2`, … | Figuran bernomor | Satu figuran tetap yang bisa muncul lagi di shot lain (penampilan dari seed + nomor). Boleh diberi `peran` (mis. `sopir_angkot`). | Palet figuran di bawah |
| `warga_n` | Kelompok figuran | Banyak figuran sekaligus. Parameter `jumlah` dan `sebar`: `deret`, `lajur_penuh`, `antre_lajur`, `serobot_lajur`, `acak`. | Palet figuran di bawah |

Figuran = kombinasi 6 gaya rambut × 8 warna baju × 3 warna kulit, ditentukan dari `seed` storyboard,
sehingga `warga_2` selalu terlihat sama sepanjang episode.

Palet figuran: `#5B8DEF #E85D75 #F2B84B #4FA88B #9C6FB0 #E8743B #6C7A89 #3FA34D`.

## 4. Palet ANDAI

| Token | Hex | Pakai |
|---|---|---|
| `brand.oranye` | `#FF8A3D` | Aksen merek, highlight hangat |
| `brand.tinta` | `#2B2D42` | Teks gelap, garis tepi netral |
| `caption.putih` | `#FFFFFF` | Caption |
| `caption.sorot` | `#FFD23F` | Kata kunci dan angka di caption |
| `andai.langit` | `#8FD3FF` | Langit Dunia Andai |
| `andai.cahaya` | `#FFD9A0` | Cahaya matahari/lampu hangat |
| `andai.daun` | `#5CC27A` | Vegetasi |
| `nyata.abu` | `#8A9099` | Dominan Dunia Nyata |
| `nyata.dingin` | `#5E6E80` | Bayangan Dunia Nyata |
| `nyata.kabut` | `#C9CED6` | Kabut latar |
| `nyata.bahaya` | `#E5484D` | Angka kerugian, LED merah |
| `malam.langit` | `#1D2547` | Langit malam |
| `malam.lampu` | `#FFC56B` | Lampu jalan/teras |

Saat dirender, palet di atas adalah warna **sebelum** grade. Grade dunia (Buku Panduan 4.2) diterapkan
di akhir.

## 5. Pustaka set (MVP: 12 set)

Setiap set terdiri dari lapisan `langit`, `belakang`, `tengah`, `depan` (untuk parallax) dan titik
penempatan tokoh/prop bernama.

| ID | Set | Lapisan dan elemen | Titik bernama | Waktu yang didukung |
|---|---|---|---|---|
| `kamar` | Kamar Si Kamu | Jendela bertirai + sinar, kasur, meja kecil + jam weker, karpet | `kasur`, `meja`, `pintu` | pagi, malam |
| `jalan_kampung` | Jalan depan rumah | Rumah berpagar, tiang listrik + kabel, warung fotokopi, pohon pisang | `jalan_kiri`, `jalan_tengah`, `teras` | semua |
| `kios_ban` | Kios tambal ban | Tumpukan ban, kompresor, papan tulisan tangan | `bangku`, `papan` | pagi, siang |
| `kantor_layanan` | Kantor layanan publik | Loket, layar antrean, kursi tunggu, AC, meja petugas | `loket`, `kursi_1..4`, `layar` | siang |
| `dapur` | Dapur tetangga | Meja taplak kotak-kotak, kompor, lampu gantung, jendela | `meja`, `kompor` | siang |
| `ruang_tamu` | Ruang tamu + TV | Sofa, meja, TV di bufet, jendela kota | `sofa`, `tv` | sore, malam |
| `gudang` | Gudang barang | Rak tinggi, kardus bertumpuk, ban berjalan | `rak`, `konveyor` | siang (nyata) |
| `lahan_rusak` | Alam rusak | Bukit gundul, kolam bekas tambang, tunggul pohon | `tengah`, `jauh` | siang (nyata) |
| `brankas` | Ruang kas negara | Pintu brankas bundar, meja, papan LED | `meja`, `led` | (nyata) |
| `sel_vip` | Sel penjara mewah | Jeruji, sofa empuk, neon, kalender dinding | `sofa`, `kalender` | (nyata) |
| `jalan_malam` | Jalan malam | Lampu jalan, pagar rumah, pos jaga kecil | `jalan`, `pos` | malam |
| `kelas` | Ruang kelas | Papan tulis, meja murid, papan rapor besar | `meja_murid`, `papan` | siang (netral) |

Tambahan untuk episode pilot `andai-macet`:

| ID | Set | Lapisan dan elemen | Titik bernama | Waktu yang didukung |
|---|---|---|---|---|
| `jalan_raya` | Jalan raya kota | Jalan 4 lajur, simpang + lampu lalu lintas, trotoar, gedung latar, pulau jalan | `lajur_kiri`, `lajur_kanan`, `simpang`, `trotoar`, `pulau_jalan`, `tiang` | semua |
| `halte` | Halte bus | Atap halte, bangku, tiang jadwal, jalur bus | `bangku`, `tiang_halte`, `jalur_bus` | pagi, siang, sore |
| `taman_kota` | Taman dan trotoar lebar | Pohon peneduh, bangku taman, trotoar lebar, anak bermain | `trotoar`, `bangku`, `rumput` | siang, sore |

Set baru untuk topik lain (halte, sungai, sekolah, puskesmas, pasar) ditambahkan dengan pola yang sama
dan dicatat di tabel ini.

## 6. Pustaka prop

### 6.1 Prop data (menampilkan angka/teks)

| ID | Parameter | Animasi bawaan |
|---|---|---|
| `papan_nama` | `teks`, `warna`, `gaya` (spanduk/papan kayu/neon) | Ayun kecil |
| `led` | `teks`, `warna` (merah/hijau/kuning) | Menyala per karakter, kedip |
| `kalender` | `hari`, `tanggal`, `bulan`, `tahun` | Sobek halaman (bisa beruntun, dengan angka berganti cepat) |
| `label_harga` | `teks` | Berayun di tali |
| `layar_tv` | `judul`, `isi`, `ticker` | Ticker berjalan |
| `meteran` | `nilai`, `maks`, `label` | Jarum bergerak dengan pegas |
| `rapor` | `baris` [(mapel, nilai)] | Baris muncul satu per satu |
| `angka_raksasa` | `teks`, `bahan` (emas/beton/kayu) | Jatuh dan memantul, debu |
| `layar_antrean` | `nomor` | Angka berganti dengan bunyi |
| `kertas_laporan` | `judul`, `baris` | Melayang turun |
| `penggaris_bendera` | `jumlah`, `sorot` (indeks) | Kamera geser, satu bendera menyala |

### 6.2 Prop benda

`motor` (bebek, merah; `posisi`, `jumlah`), `kardus` (`label`), `toples` (`label`, `sarang_laba`), `celengan`,
`uang_kertas` (fiktif: hanya nominal, desain kartun, **tidak** meniru rupiah asli), `dompet`, `surat_tilang`,
`amplop`, `jam_weker`, `tumpukan` (`item`, `jumlah`), `buku_dongeng`, `telur`, `mi_instan`, `ban`,
`kerucut_lalu_lintas`, `gelembung_bicara` (`teks`).

Tambahan untuk episode pilot: `mobil` (`jumlah`), `angkot` (`kosong`), `bus` (anim `datang`),
`lampu_lalu_lintas` (`status`: merah/kuning/hijau), `jam_dinding` (`jam` "HH.MM", anim `putar_cepat`),
`gerobak_martabak`, `layangan` (`jumlah`), `nampan_asongan`, `piring` (`jumlah`).

### 6.3 Efek lingkungan

`sinar_jendela`, `debu_melayang`, `kabut` (`kepadatan`), `hujan`, `uap_kopi`, `bintang_kilau`,
`retak` (pada prop), `asap_knalpot`.

### 6.4 Pustaka SFX

ID yang dipakai di kolom `sfx` storyboard. Yang bertanda * sudah ada versi sintetisnya di `motion/sfx.py`;
sisanya diambil dari pustaka SFX bebas lisensi ke `assets/sfx/<id>.wav`.

| Kelompok | ID |
|---|---|
| Transisi | `tik` (Kedip), `whoosh`* (whip) |
| Penegas | `pop`*, `ding`, `beep`, `impact`*, `riser`*, `sparkle`* |
| Benda | `cring` (koin/kasir), `sobek_kertas`, `kaca_retak`, `standar_motor`, `rem_bus` |
| Ambience | `burung_pagi`, `jangkrik`, `klakson_ramai`, `ac_kantor`, `hujan`* |

## 7. Opsi plate AI (jika memakai jalur B di `04-arsitektur-pipeline.md`)

Jika latar dibuat dengan model gambar, pakai templat prompt yang sama setiap kali agar gaya konsisten.
Tokoh tetap digambar engine di atas plate supaya konsisten antar-episode.

```
Latar ilustrasi vertikal 9:16 untuk animasi kartun 2.5D, tanpa tokoh manusia.
Lokasi: {deskripsi set}, Indonesia, {waktu: pagi/siang/sore/malam}.
Gaya: bentuk vektor sederhana, gradien lembut, garis tepi tipis berwarna gelap senada,
bayangan lembut, palet {andai: hangat jenuh | nyata: pucat dingin berkabut}.
Komposisi: lantai/jalan di 55–90% tinggi gambar untuk tempat tokoh, area atas lapang.
Tanpa teks, tanpa logo, tanpa watermark.
```

Teks di dunia (papan, LED, label) tetap ditambahkan engine sebagai prop, bukan oleh model gambar,
karena model gambar sering salah mengeja dan angkanya harus persis sesuai `fakta.yaml`.
