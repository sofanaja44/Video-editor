# Server GPU boleh mati: rencana kelangsungan proyek

Server GPU itu sewaan, bisa mati atau diganti kapan saja. Karena itu proyek dibagi dua peran:

| Peran | Mesin | Isi |
|---|---|---|
| **Rumah** | server utama | Semua yang berharga: kode, episode (brief/fakta/naskah/storyboard/audio), hasil render, cache shot, cadangan Blender, kunci SSH |
| **Pekerja** | server GPU sewaan | Hanya merender. Tidak menyimpan apa pun yang tak tergantikan. Hilang = pasang yang baru dalam beberapa menit |

Semua kendali lewat satu skrip yang dijalankan dari Rumah: `bash andai/gpu/gpu.sh <perintah>`.

## Di mana apa disimpan

| Apa | Lokasi (Rumah) | Cara aman |
|---|---|---|
| Kode + dokumen + font | `/root/Video-editor` (git) | `gpu.sh snapshot`; dorong ke GitHub sebagai cadangan di luar server |
| Input episode (`brief.yaml`, `fakta.yaml`, `naskah.md`, `storyboard.json`, `audio/`) | `/root/Video-editor/episodes/<slug>/` | ikut snapshot; `gpu.sh kirim` mengirimnya ke pekerja |
| Hasil render dan cache shot (`build/`, `output/`, `hasil*/`) | `/root/andai-aset/render/` | `gpu.sh cadangan` (tambah saja, tidak pernah menghapus) |
| Blender 5.2.3 persis (367 MB) | `/root/andai-aset/blender/` + `.sha256` | `gpu.sh cache-blender` |
| Snapshot proyek bertanggal | `/root/andai-aset/snapshot/` | `gpu.sh snapshot` |
| Kunci SSH ke pekerja | `~/.ssh/andai_gpu` | kunci khusus proyek; **tidak ada password di file mana pun** |

Aturan: **jangan** menaruh sesuatu yang berharga hanya di server GPU. Sebelum server GPU dimatikan atau
diganti: `bash andai/gpu/gpu.sh cadangan`.

## Pasang server GPU baru (±3 menit, sudah diuji)

Syarat server baru: GPU NVIDIA (RTX 30/40/50, A-series, dst., VRAM ≥ 8 GB; seri RTX 50 butuh driver 570+ varian
`open`), Ubuntu 22.04/24.04, disk ≥ 50 GB, akses SSH dengan sudo tanpa password atau root.

```bash
# 1. Alamat server baru: edit andai/gpu/gpu.env (GPU_HOST, GPU_PORT, GPU_USER). Contoh: gpu.env.example
# 2. Kunci SSH (minta password server baru SEKALI, setelah itu tanpa password)
bash andai/gpu/gpu.sh kunci
# 3. Kirim kode, pasang Blender, uji kecepatan. Blender diunduh dari blender.org; bila tak terjangkau, otomatis
#    memakai cadangan di server utama. Paksa cadangan: BLENDER_DARI_CADANGAN=1
bash andai/gpu/gpu.sh siapkan
# 4. Bila ada cache render lama: kembalikan agar shot yang sudah jadi tidak dirender ulang
bash andai/gpu/gpu.sh pulihkan
# 5. Cek ujung ke ujung (lembar karakter + uji keyframe)
bash andai/gpu/gpu.sh uji
```

`gpu.sh status` menampilkan GPU dan versi Blender kapan saja. Angka yang harus muncul di langkah 3: Cycles GPU
sekitar 0,5 dtk/frame pada RTX 5090 (GPU lain berbanding terbalik dengan kecepatannya). Jika ratusan detik per
frame, denoiser jatuh ke CPU atau GPU tidak terpakai: lihat `references/04-arsitektur-pipeline.md` 2.1.

Setelah server lama mati: `ssh-keygen -R "[alamat-lama]:port"` (opsional), dan ganti password server lama bila
sempat. Kunci `andai_gpu` hanya berlaku di server yang pernah dipasangi.

## Kalau server mati di tengah render

- **Yang hilang:** hanya shot yang sedang dirender dan apa pun yang belum dicadangkan.
- **Rancangan (belum dibangun):** `shot.py` akan menulis tiap shot ke `build/shots/Sxx-<hash>.mp4` dan melewati
  shot yang sudah ada. Setelah itu episode bisa dilanjutkan di server baru tanpa mengulang shot yang sudah jadi.
  Sampai `shot.py` ada, render dilakukan per perintah dan hasilnya langsung `gpu.sh ambil`/`cadangan`.
- **Selama render panjang**, jalankan cadangan berkala dari Rumah, mis. tiap 30 menit:
  `*/30 * * * * cd /root/Video-editor && bash andai/gpu/gpu.sh cadangan >> /root/andai-aset/cadangan.log 2>&1`
  (belum dipasang otomatis; pasang dengan `crontab -e` bila mau). Bila server sudah mati, cron itu gagal diam-diam
  dan tidak merusak apa pun.
- **Pemulihan:** pasang server baru (langkah di atas), `gpu.sh pulihkan`, lalu render ulang (setelah `shot.py` ada:
  hanya shot yang belum ada yang dikerjakan).

## Kalau tidak ada server GPU sama sekali

Diukur di server GPU saat ini, memakai CPU saja (Cycles, 1080×1920, adegan Si Kamu + 6 figuran):

| Mode | Waktu per frame | Cukup untuk |
|---|---|---|
| CPU, 8 core efektif, 32 sampel | ±48 dtk | 1–2 gambar uji, bukan video |
| CPU, 540×960, 24 sampel | ±15 dtk | pratinjau satu shot |
| GPU RTX 5090, 64 sampel + semua efek | 2,8–4,3 dtk | produksi |

(64 thread di container ini malah lebih lambat daripada 8, karena kuota CPU.) Video 90 detik (2.700 frame)
memerlukan ±35 jam di CPU, jadi untuk produksi tetap perlu GPU; sewa GPU per jam sudah cukup karena satu episode
diperkirakan ±1,5–3 jam GPU RTX 5090 (2.700 frame × 2–4 dtk). Pratinjau ringan tanpa GPU tetap bisa memakai prototipe three.js
(`andai/scene3d/prototipe/`).

## Keamanan

- Password server tidak pernah disimpan di repo, di toko aset, atau di `gpu.env`; hanya kunci SSH.
- `andai/gpu/gpu.env` tidak di-commit (ada di `.gitignore`); `gpu.env.example` yang di-commit.
- Kunci SSH proyek: `~/.ssh/andai_gpu` (di Rumah). Jangan salin ke tempat lain; buat baru dengan `gpu.sh kunci`.
