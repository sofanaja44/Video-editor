# Karakter, Set, dan Prop ANDAI

> "Bible" visual versi kita. Engine 3D (kini **Blender**, lihat `04-arsitektur-pipeline.md` 2.1) membangun semuanya
> dari kode memakai parameter di bawah, sehingga tokoh selalu konsisten di setiap episode. Kode tidak boleh
> menyimpang dari dokumen ini tanpa memperbaruinya dulu. Contoh hasil uji: `img/uji-3d-perbandingan.jpg`.

## 1. Prinsip desain

1. **Siluet terbaca di HP.** Tokoh dikenali dari siluet dan warna baju, meski kecil.
2. **Kepala besar, wajah ekspresif.** Emosi dibawa alis dan mata.
3. **Dibangun dari bentuk 3D dasar.** Bola, kapsul, silinder, bentuk putar (lathe). Mudah dibuat lewat kode
   dan mudah dianimasikan lewat sendi.
4. **Indonesia sehari-hari.** Sandal jepit, motor bebek, warung, kerudung, kopiah, rumah berpagar.
5. **Beda dari referensi.** Kepala referensi bola sempurna dengan tangan-kaki lidi. Kepala kita "kacang"
   (lebih lebar di pipi), lengan dan kaki berbentuk kapsul tebal, tangan bulat tanpa jari (mitten).
6. **Tampilan "mainan doff".** Material agak kasar (roughness 0,45–0,8), bukan plastik mengilap. Semua
   sudut dibulatkan; tidak ada tepi tajam pada tokoh dan prop kecil.

## 2. Rig tokoh

### 2.1 Proporsi (satuan `u` = 1 meter di adegan 3D, sumbu Y ke atas, tinggi total ±4,3u)

Gambar di bawah adalah sketsa proporsi. Ukuran persis mengikuti prototipe `andai/scene3d/prototipe/scene.html`.

```
        ___
      /     \        Kepala "kacang": lebar ±2,2u, tinggi 2,5u
     | ◉   ◉ |       (bagian pipi 12% lebih lebar dari dahi)
     |   ‿   |
      \_____/
        | |          Leher: tidak ada (kepala menempel ke badan)
      /‾‾‾‾‾\
     |  KAOS |       Badan kapsul: lebar 1,24u, tinggi 1,94u
      \_____/
       |   |         Kaki kapsul: tebal 0,34u, panjang ±1,1u
       ◖   ◗         Sandal: setengah bola pipih, panjang 0,75u
```

| Bagian | Geometri three.js | Sendi (Object3D) |
|---|---|---|
| Kepala | `LatheGeometry` profil "kacang" (setengah lingkaran + tonjolan pipi 12% di y = −0,35), tinggi 2,5u | Pangkal kepala: miring ±15°, menoleh ±35° |
| Rambut | Lathe yang sama ×1,04, hanya bagian atas (y > 0,32), + 3 kerucut jambul | Ikut kepala |
| Badan | `CapsuleGeometry` r 0,62, panjang 0,7, dipipihkan 0,8 di Z | Pinggul: condong ±10° |
| Lengan | Kapsul r 0,15, 2 ruas | Bahu, siku |
| Tangan | Bola r 0,2 (mitten) | Pergelangan (titik pegang prop) |
| Kaki | Kapsul r 0,17, 2 ruas | Pinggul, lutut |
| Alas kaki | Setengah bola dipipihkan (sandal) | — |

Gaya render: `MeshStandardMaterial` doff, bayangan lembut dari satu cahaya utama, cahaya lingkungan
tipis. Tanpa garis tepi (outline). Semua mesh `castShadow` dan `receiveShadow`.

### 2.2 Wajah

Semua fitur wajah adalah mesh 3D kecil yang menempel di permukaan kepala, sehingga ikut berputar saat
kepala menoleh.

| Fitur | Geometri | Parameter |
|---|---|---|
| Mata | Bola putih dipipihkan (r 0,25, Z ×0,5) + pupil bola hitam (r 0,11) mengilap | `skala` 0,6–1,4, `pupil` (x, y) −1..1, `kelopak` 0 (terbuka) .. 1 (tertutup; skala Y mata → 0,1) |
| Alis | Kapsul r 0,05 panjang 0,28 | `sudut` −30°..+30°, `naik` −0,1..+0,2u. Pembawa emosi utama. |
| Mulut | Set mesh siap tukar: `TorusGeometry` busur (senyum/cemberut), cincin (o), `TubeGeometry` di kurva (gelombang, seringai), busur + bidang gelap (tawa_terbuka) | `bentuk` (garis, senyum, tawa_terbuka, o, gelombang, cemberut, seringai), `lebar` |
| Aksesori | Tetes (`keringat`), cakram merah muda transparan (`blush`), bintang ekstrusi (`bintang`, menggantikan mata), sprite `zzz`, garis kejut | Muncul/hilang dengan skala pop 120 ms |

Kedip otomatis setiap 2,5–4 detik (acak per tokoh dari seed, durasi 4 frame), kecuali ekspresi `tidur`.

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

Setiap set adalah adegan 3D (satu file `src/sets/<id>.js`) berisi lantai/jalan, bangunan, benda latar,
langit, dan **titik bernama** (`Object3D` kosong) untuk menaruh tokoh, prop, dan target kamera. Objek
yang berulang (pagar, pohon, kendaraan) memakai `InstancedMesh` supaya render tetap cepat.

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

## 7. Resep membangun di three.js

Pelajaran dari prototipe (`andai/scene3d/prototipe/`):

- **Kepala satu mesh.** Kepala dari dua bola yang ditumpuk menimbulkan garis sambungan yang terlihat.
  Pakai satu `LatheGeometry` dengan profil kacang, lalu rambut sebagai lathe kedua yang sedikit lebih
  besar.
- **Tulisan di prop.** Gambar teks ke `<canvas>` dengan font Fredoka (tunggu `document.fonts.ready`), lalu
  pakai sebagai `CanvasTexture` di bidang/kotak prop. LED: teks terang + `emissive` pada material.
- **Angka raksasa.** `TextGeometry` (font Fredoka dikonversi ke JSON typeface) dengan `bevelEnabled`
  supaya sudutnya bulat.
- **Figuran banyak.** Bagian tubuh yang sama dibuat `InstancedMesh`; warna per instance dari palet figuran.
- **Bayangan.** Satu cahaya utama dengan `shadow.radius` 4–6 dan `shadow.bias` ±−0,0005; atur kotak
  kamera bayangan seketat mungkin di sekitar area aksi agar tajam.
- **Kedalaman.** `THREE.Fog` tipis di Dunia Andai, tebal dan keabu-abuan di Dunia Nyata.

## 8. Catatan implementasi Blender (`andai/blender/`)

Penyimpangan kecil dari rancangan three.js di atas, ditemukan saat membangun rig di Blender:

- **Sumbu:** Blender Z-atas. Tokoh menghadap **-Y** (ke kamera). `_L` = kiri tokoh (+X, tampil di kanan layar),
  `_R` = kanan tokoh (-X). Tabel pose di `poses.py`: sudut anggota badan *positif = ke depan*.
- **Garis rambut:** rambut bukan potongan lathe dengan tepi rata (y > 0,32), tetapi tudung dengan garis rambut
  yang tinggi di depan (+0,92) dan turun ke belakang, supaya alis tidak tenggelam di rambut hitam. Tebalnya
  0,05u (modifier Solidify). Enam gaya: `cepak`, `jambul`, `kuncir`, `keriting`, `bob`, `botak`.
- **Mata tertutup:** `kelopak` ≥ 0,95 menggepengkan mata sampai garis tipis dan memunculkan **garis lengkung gelap**
  (∪) di depannya; `tawa` memakai garis lengkung ^ ^ sebagai pengganti mata. Tanpa ini mata tertutup terlihat
  seperti irisan putih.
- **Kilau mata:** setiap pupil punya bola kilau putih kecil (skala `kilau`, 1,9 untuk `sedih`).
- **Lengan:** `lengan: pendek` (Si Kamu, kaos oblong) = lengan atas warna baju, lengan bawah warna kulit.
- **Pop aksesori:** bagian yang muncul/hilang (keringat, blush, zzz, bintang, garis kejut, mulut yang tidak
  dipakai) ditukar lewat skala 1 ↔ 0,0001, sehingga bisa di-keyframe dan di-ease seperti objek lain.
- **Tinggi pinggul otomatis:** `poses.resolve` menghitung tinggi pinggul dari sudut paha dan lutut supaya kaki
  yang terendah selalu menapak lantai (jalan, duduk).
- **Figuran:** selain warna dan gaya rambut, `tinggi` (0,92–1,06) dan `lebar` badan (0,9–1,18) diundi dari seed,
  supaya barisan figuran tidak terlihat seragam.

### 8.1 Peningkatan model (kedua)

- **Telinga, hidung, jempol:** telinga elips pipih dengan bagian dalam lebih gelap (kepala tidak lagi botak dari
  samping), hidung bulat kecil (`hidung` = skala, 0 untuk tanpa hidung), jempol mitten kecil di tiap telapak.
- **Alas kaki:** `sandal` = kaki telanjang di atas sol tipis + tali Y (jepit), `sepatu` = kubah bulat + sol terang,
  `bot` = sepatu + selongsong, `tanpa` = kaki telanjang.
- **Material:** kulit memakai subsurface (cahaya merembes hangat); kain memakai sheen + butiran halus; rambut sheen
  + butiran. Motif kain prosedural di ruang objek: `('titik'|'garis'|'kotak'|'ombak', warna2, skala)`.
- **Warna dan cahaya:** transformasi warna **Khronos PBR Neutral** (bukan AgX) supaya warna palet tetap setia;
  AgX membuat semuanya pucat. Langit gradasi tiga warna ikut menerangi adegan; lampu isi dan pinggir memakai
  *spot* (lampu area memotong lantai dengan tepi keras).
- **Bayi:** `baju=None` dan `celana=None` berarti kulit telanjang; `kepala_skala` 1,4 + `tinggi` 0,5 memberi
  kepala ±70% badan; `mata_besar`.

### 8.2 Pemeran yang sudah dibangun

| ID | Pembeda utama (kode: `cast.py`) |
|---|---|
| `kamu` | Jambul, kaos oranye bata, jeans, sandal jepit hijau |
| `tetangga` | Kerudung hijau (potongan wajah oval), daster kuning bermotif titik, bulu mata |
| `petugas` | Seragam krem, dua saku dada, sabuk, tali ID + kartu kosong |
| `polisi` | Seragam cokelat tua, topi pet, bot hitam, sabuk, dua saku; tanpa lambang |
| `pejabat` | Jas hitam, kemeja putih + dasi merah, kacamata hitam bundar, kumis, perut bulat, ekspresi `licik` |
| `peneliti` | Helm proyek kuning, kacamata bulat, rompi oranye dengan pita pantul |
| `nenek` | Rambut putih disanggul, kacamata, kebaya ungu, kain batik, membungkuk |
| `bayi` | Kepala besar, popok putih, satu jambul keriting, tanpa baju |
| `tukang_ban` | Singlet, handuk di leher, topi merah terbalik, noda oli, kulit gelap |
| `ibu` | Kerudung merah muda, tunik krem longgar, bulu mata |

`warga(n, seed, peran)` = figuran bernomor; `kerumunan(jumlah, sebar, ...)` = banyak figuran sekaligus.
