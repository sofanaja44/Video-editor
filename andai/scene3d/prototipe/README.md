# Prototipe 3D dari kode (ANDAI)

Uji kelayakan: satu adegan ANDAI (Si Kamu melambai di jalan depan rumah) dibangun sepenuhnya dari kode
dengan three.js, dirender frame per frame di Chromium headless, lalu disalurkan ke ffmpeg.

```bash
cd andai/scene3d/prototipe
npm install                       # three.js; Playwright + Chromium sudah ada di environment Claude
node render.js uji.mp4 3 30                     # 3 dtk, 30 fps, 1080×1920
node render.js uji_preview.mp4 3 15 540 960     # mode preview
node render.js uji_hq.mp4 1 30 1080 1920 1      # dengan ambient occlusion
```

Hasil ukur di container sesi Claude (4 core CPU, tanpa GPU):

| Mode | Waktu per frame |
|---|---|
| 540×960, tanpa AO | 0,41 dtk |
| 1080×1920, tanpa AO | 0,93 dtk |
| 1080×1920, dengan AO (GTAO) | 2,9 dtk |
| Pembanding: Blender Cycles CPU, 16 sampel | 31 dtk |

Hasil visual: `skills/andai/references/img/uji-3d-perbandingan.jpg`.

Ini prototipe, bukan engine. Struktur engine yang sebenarnya ada di
`skills/andai/references/04-arsitektur-pipeline.md` bagian 3.
