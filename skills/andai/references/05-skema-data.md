# Skema Data Episode ANDAI

> Format semua file di folder episode. Claude menulis `brief.yaml` (bersama pengguna), `fakta.yaml`,
> `naskah.md`, dan `storyboard.json`. Engine menulis sisanya. Templat kosong ada di `../templates/`.

## 1. `brief.yaml`: input episode

```yaml
slug: andai-macet                 # huruf kecil-strip, juga nama file output
judul_kerja: "Andai Besok Nggak Ada Macet"
topik: kemacetan kota             # masalah sehari-hari yang "hilang" di Dunia Andai
kebiasaan_twist: parkir di bahu jalan   # kebiasaan kecil si Kamu untuk beat TWIST
aksi_penutup: naik transportasi umum     # "kalau semua orang mulai dari …"
preset: standar                   # pendek | standar | panjang (Buku Panduan 3.6)
platform: [tiktok, reels]
suara:
  engine: edge                    # edge | premium | rekaman
  id: id-ID-ArdiNeural            # nama suara (untuk edge/premium)
  kecepatan: "+0%"
musik:
  pakai: false
  file: null
  lisensi: null                   # wajib diisi jika pakai: true
handle: "@akunkamu"               # untuk metadata/deskripsi, bukan untuk end card
catatan: >
  Hindari menyebut nama kota tertentu; pakai "kotamu".
```

## 2. `fakta.yaml`: fakta dan sumber

```yaml
- id: F1
  klaim: "Rata-rata pengendara kehilangan sekian jam per tahun karena macet."
  angka: "[[PERLU SUMBER]]"        # bentuk digit, untuk prop. Wajib terisi sebelum Gerbang 1 lolos.
  ucapan: null                     # bentuk kata, untuk naskah ("enam puluh jam")
  satuan: jam/tahun
  sumber:
    lembaga: null                  # mis. nama lembaga/penerbit
    judul: null
    tahun: null
    url: null
    diakses: null                  # YYYY-MM-DD
  kartu_sumber: null               # teks pendek di layar, mis. "Sumber: <lembaga>, <tahun>"
  konversi:                        # opsional; rumus wajib ditulis
    teks: null                     # "itu sama dengan dua setengah hari penuh"
    rumus: null                    # "60 jam ÷ 24 = 2,5 hari"
  status: draf                     # draf | terverifikasi
```

Aturan validasi (`andai check`):
- Semua fakta yang dirujuk naskah **wajib** `status: terverifikasi`, `angka`, `sumber.lembaga`,
  `sumber.tahun`, dan `kartu_sumber` terisi.
- Teks `[[PERLU SUMBER]]` di mana pun → gagal.

## 3. `naskah.md`: naskah berbeat

Markdown sederhana yang bisa dibaca manusia dan di-parse engine.

```markdown
---
slug: andai-macet
preset: standar
---

## HOOK | dunia=andai | waktu=pagi
K01: Andai besok pagi kamu bangun, dan *macet* di kotamu hilang.

## ANDAI-1 | dunia=andai | waktu=pagi
K02: Jalan ke kantor cuma lima belas menit.
K03: Klakson diam, asap knalpot tinggal tipis.
K04: Pedagang asongan di lampu merah sampai *bengong*, soalnya lampunya keburu hijau.

## PIVOT | dunia=andai
K05: Tapi ini bukan dongeng. [jeda:0.5]

## NYATA-1 | dunia=nyata | waktu=pagi
K06: Padahal, di dunia nyata, pengendara di kota besar kehilangan {F1} di jalan setiap tahun.
```

Aturan format:
- Header beat: `## <KODE> | dunia=<andai|nyata|netral> | waktu=<pagi|siang|sore|malam>`. `waktu` boleh
  dihilangkan jika sama dengan beat sebelumnya.
- Satu kalimat per baris, diawali ID `Knn:` yang unik dan berurutan.
- `*kata*` = kata sorotan di caption (Buku Panduan 6.2). Angka dalam kata otomatis disorot.
- `{F1}` = sisipan ucapan dari `fakta.yaml` (`ucapan` milik F1). Kalimat itu otomatis terhubung ke fakta
  F1 (untuk Kartu Sumber). `{F1.konversi}` menyisipkan `konversi.teks` milik F1.
- `[jeda:0.5]` di akhir kalimat = jeda setelah kalimat (detik). Default 0,2.
- `> dialog: "Besok jadi."` di bawah kalimat = gelembung bicara yang tampil selama kalimat itu.
- Teks naskah = teks ucapan. **Tidak boleh ada digit** di luar `{Fn}` (validasi akan menolak).

## 4. `storyboard.json`: daftar shot

```json
{
  "slug": "andai-macet",
  "fps": 30,
  "ukuran": [1080, 1920],
  "seed": 62,
  "shots": [
    {
      "id": "S01",
      "beat": "HOOK",
      "anchor": {"kalimat": "K01", "kata": 0},
      "dunia": "andai",
      "waktu": "pagi",
      "set": "kamar",
      "cast": [
        {"id": "kamu", "pose": "bangun", "ekspresi": "tidur", "titik": "kasur",
         "aksi": [{"di_kata": 2, "ekspresi": "senyum"}]}
      ],
      "props": [{"id": "jam_weker", "titik": "meja"}],
      "efek": ["sinar_jendela", "debu_melayang"],
      "kamera": {"gerak": "push_in", "zoom": [1.0, 1.06]},
      "transisi_masuk": "kedip",
      "sfx": [{"id": "burung_pagi", "mulai": "awal", "level": -35}],
      "catatan": "Frame pertama = frame terakhir (loop)."
    }
  ]
}
```

| Kolom | Wajib | Isi |
|---|---|---|
| `id` | ya | `S01`, `S02`, … berurutan |
| `beat` | ya | Kode beat dari naskah |
| `anchor` | ya | Kata tempat shot dimulai: `kalimat` (ID) + `kata` (indeks mulai 0) + `teks` (opsional, kata itu tanpa tanda baca, untuk validasi). Shot pertama wajib `K01` kata 0. |
| `dunia`, `waktu` | ya | Menentukan grade |
| `set` | ya | ID dari pustaka set (`03-karakter-dan-set.md` bagian 5) |
| `cast[]` | tidak | `id`, `pose`, `ekspresi`, `titik` (titik bernama di set) atau `pos` [x, z] dalam meter di lantai set, `skala`, `hadap` (kiri/kanan), `pegang` (ID prop), `peran` (untuk figuran), `jumlah` + `sebar` (untuk `warga_n`), `aksi[]` (perubahan pada kata tertentu: `di_kata` + `ekspresi`/`pose`/`anim`) |
| `props[]` | tidak | `id` prop + parameternya (`teks`, `nilai`, …), `titik`/`pos`, `muncul_di_kata` |
| `data` | tidak | `{"fakta": "F1", "bagian": "angka", "prop": "led", "muncul_di_kata": 4}`: prop yang menampilkan angka fakta + Kartu Sumber. `bagian`: `angka` (default) atau `konversi`. |
| `efek[]` | tidak | Efek lingkungan |
| `kamera` | ya | `gerak` (Buku Panduan 4.8) + parameter (`zoom`, `geser`, `target`, `sudut`, `orbit` derajat, `lensa` mm). `zoom` dan `geser` adalah ukuran relatif yang diterjemahkan engine ke gerak kamera 3D. |
| `transisi_masuk` | ya | `cut` / `dissolve` / `whip` / `kedip`. Wajib `kedip` jika `dunia` berbeda dari shot sebelumnya. |
| `sfx[]` | tidak | `id`, `mulai` (`awal` atau `{"kata": n}`), `level` (dB relatif) |
| `catatan` | tidak | Bebas. Awali `pun:` untuk pun visual. |

Cara menghitung indeks `kata`: pecah teks kalimat mentah di `naskah.md` berdasarkan spasi setelah
membuang `*` dan `[jeda:…]`. Sisipan `{F1}` atau `{F1.konversi}` dihitung **satu** token, apa pun panjang
ucapannya; engine memetakan token itu ke kata pertama hasil sisipan. Dengan begitu storyboard tidak
berubah saat angka di `fakta.yaml` diperbarui.

Aturan validasi:
- Jangkar berurutan maju dan tidak ada dua shot di kata yang sama.
- Jika `anchor.teks` diisi, harus sama dengan token di posisi itu (tanpa tanda baca).
- Setiap kalimat yang memuat `{Fn}` punya shot dengan `data.fakta = Fn`.
- S01 wajib `transisi_masuk: kedip`. Engine memecahnya di batas loop: separuh tutup di akhir video,
  separuh buka di awal video.
- Shot terakhir: set, pose tokoh utama, dan waktu sama dengan S01 (loop).

## 5. `audio/words.json`: hasil alignment (ditulis engine)

```json
[
  {"i": 0, "kalimat": "K01", "k": 0, "teks": "Andai", "mulai": 0.00, "selesai": 0.34, "sorot": false, "interp": false},
  {"i": 1, "kalimat": "K01", "k": 1, "teks": "besok", "mulai": 0.36, "selesai": 0.62, "sorot": false, "interp": false}
]
```

`teks` berasal dari naskah (ejaan dan tanda baca persis), `mulai`/`selesai` dari audio.

## 6. `timeline.json`: hasil hitung (ditulis engine, jangan diedit)

```json
{
  "fps": 30,
  "total_frame": 2730,
  "shots": [
    {"id": "S01", "f0": 0, "f1": 96, "masuk": {"jenis": "kedip", "f0": 0, "f1": 10}}
  ],
  "caption": [
    {"f0": 0, "f1": 11, "teks": "Andai", "sorot": false}
  ],
  "kartu_sumber": [
    {"f0": 410, "f1": 485, "teks": "Sumber: …"}
  ],
  "gelembung": [],
  "sfx": [
    {"f": 0, "id": "tik", "level": -18}
  ]
}
```
