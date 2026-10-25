# andai/blender: engine 3D Blender

Karakter, set, dan kamera ditulis sebagai kode Python (`bpy`) dan dirender dengan Cycles di GPU. Dijalankan
**di dalam Blender**, bukan dengan `python` biasa:

```bash
blender -b --python andai/blender/uji_karakter.py -- OUT_DIR 48     # atau: bash andai/blender/uji_karakter.sh
blender -b --python andai/blender/uji_keyframe.py                    # uji numerik jalur keyframe, cetak "ALL OK"
```

Server GPU: `bash andai/gpu/gpu.sh siapkan` (kirim kode, pasang Blender 5.2.3, ukur kecepatan); server boleh mati dan
diganti, lihat `skills/andai/PINDAH-SERVER.md`. Angka dan jebakan GPU: `skills/andai/references/04-arsitektur-pipeline.md` 2.1.

| File | Isi |
|---|---|
| `materials.py` | Palet, `mat(hex, rough, emit, alpha, sss, sheen, bump, pola)` (material bersama; kulit SSS, kain, motif titik/garis/kotak/ombak), `darker`, sRGB → linear |
| `geo.py` | Primitif dari kode: `empty` (sendi), `lathe`, `sphere`, `capsule`, `tube`, `flat_poly`, `star`, `surface` (permukaan parametrik), `rbox` (kotak bulat) |
| `poses.py` | Tabel pose dan ekspresi (data murni, tanpa `bpy`), `resolve` (tinggi pinggul otomatis), `jalan(fase)` |
| `rig.py` | `Character`: tubuh, kepala "kacang", telinga, hidung, rambut (6 gaya), wajah, alas kaki; `pose`, `expression`, `place`, `blink`, `walk` |
| `kostum.py` | Kostum dan aksesori: `rok`, `kerudung`, `topi_pet`, `helm_proyek`, `kacamata`, `kumis`, `dasi_jas`, `rompi`, `saku_dada`, `sabuk`, `tali_id`, `handuk`, `popok`, `sanggul`, `noda`, `jambul_bayi` |
| `cast.py` | 10 tokoh bernama (`tokoh('polisi')`), `kamu()`, `warga(n, seed, peran)`, `kerumunan(jumlah, sebar, ...)` |
| `lights.py` | `setup(sc, waktu)`: langit gradasi + matahari + lampu isi + lampu pinggir untuk pagi/siang/sore/malam |
| `fx.py` | `dof`, `motion_blur`, `kabut` (kotak volume terbatas), `debu`, `bloom` (compositor) |
| `camera.py` | `pasang(spec, fokus, f0, f1)`: gerak kamera dari storyboard (push_in, pull_out, truck, cu, tilt, orbit, getar), tinggi lensa dijaga di atas tanah |
| `sets/` | `bangun(nama, dunia, waktu, seed)` mengembalikan `Set` dengan titik bernama; `jalan_raya` sudah ada; `pandang()` menyembunyikan penghalang di antara kamera dan subjek |
| `props/` | `buat('motor' / 'mobil' / 'angkot' / 'bus' / 'lampu_lalu_lintas', ...)` mengembalikan `Prop` dengan soket (`dudukan`, `setang_L/R`, `knalpot`, ...) |
| `stage.py` | `fresh_scene` (Cycles GPU + denoise GPU, Khronos PBR Neutral), `sky`, `sun`, `floor`, `camera`, `render` |
| `uji_karakter.py/.sh` | Lembar uji: pose depan dan samping, gaya rambut, 12 ekspresi, kedip |
| `uji_model.py` | Si Kamu dari empat sisi + close-up kepala |
| `uji_pemeran.py` | Seluruh pemeran: dua barisan dan potret |
| `uji_efek.py` | Adegan sama tanpa dan dengan efek, dengan waktu |
| `uji_kerumunan.py` | Uji beban: kerumunan 28/60 figuran + efek penuh, cetak waktu bangun dan render |
| `uji_jalan.py` | Set jalan raya di tiga dunia + Si Kamu naik motor (shot S03), tampak lebar dan close-up |
| `uji_keyframe.py`, `uji_kerumunan_bentuk.py` | Uji regresi tanpa render (keyframe; semua formasi, peran, pose, ekspresi) |

## Pakai

```python
import sys; sys.path.insert(0, REPO)                      # akar repo
from andai.blender import cast, stage, lights, fx

sc = stage.fresh_scene(1080, 1920, samples=64)            # 30 fps, Cycles GPU
lights.setup(sc, 'sore', target=(0, 0, 2.2))              # pagi | siang | sore | malam
stage.floor('#B7B2A4', 300)
si_kamu = cast.kamu()
polisi = cast.tokoh('polisi')                             # kamu, tetangga, petugas, polisi, pejabat, peneliti, nenek, bayi, tukang_ban, ibu
orang = cast.kerumunan(24, 'lajur_penuh', seed=4, pusat=(0, 6), lebar=9, kedalaman=14)
si_kamu.place(-2, 0, yaw=20)
si_kamu.pose('berdiri'); si_kamu.expression('senyum')     # tanpa frame = langsung diset
si_kamu.expression('kaget', frame=60)                     # dengan frame = keyframe (ramp 3 frame)
si_kamu.pose('menunjuk', frame=60)                        # ramp 6 frame
si_kamu.walk(90, 150)                                     # siklus 8 frame, kunci tiap 2 frame
si_kamu.blink(frames=300)                                 # panggil terakhir, setelah semua ekspresi
cam = stage.camera((0, -12.5, 3.2), (0, 3, 2.4), 50)
fx.dof(cam, si_kamu.j['kepala'], fstop=2.2); fx.motion_blur(sc); fx.bloom(sc)
fx.kabut(kepadatan=0.004); fx.debu((0, 4, 3), (9, 12, 5), 45, seed=2, frame0=1, frame1=300)
stage.render('/path/mutlak/out.png')
```

Aturan: atur keadaan **berurutan menurut waktu** (tiap pemanggilan menyimpan nilai lama di `frame - ramp`).
Lihat juga bagian 8 di `skills/andai/references/03-karakter-dan-set.md`.
