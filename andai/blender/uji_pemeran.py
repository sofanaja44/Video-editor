"""Whole-cast sheets: full-body line-ups and head-and-shoulders portraits, lit with the 'siang' preset.
  blender -b --python andai/blender/uji_pemeran.py -- OUT_DIR [SAMPLES]"""
import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from andai.blender import cast, stage, lights

args = sys.argv[sys.argv.index('--') + 1:]
out = os.path.abspath(args[0]); os.makedirs(out, exist_ok=True)
samples = int(args[1]) if len(args) > 1 else 64
NAMA = list(cast.PEMERAN)


def timed(label, path):
    t = time.time(); stage.render(path); print(f'{label}: {time.time() - t:.1f}s', flush=True)


def studio(w, h, waktu='siang', target=(0, 0, 2.0)):
    sc = stage.fresh_scene(w, h, samples)
    lights.setup(sc, waktu, target=target)
    stage.floor('#B7B2A4', 300)
    return sc


# full-body line-ups: five characters each, turned a little so the 3D shape reads
for tag, nama_grup in (('1', NAMA[:5]), ('2', NAMA[5:])):
    studio(2400, 1000, target=(0, 0, 2.2))
    for i, nama in enumerate(nama_grup):
        c = cast.tokoh(nama)
        c.place((i - 2) * 4.4, 0, 14 if i % 2 else -10)
        c.pose('berdiri')
    stage.camera((0, -33, 2.6), (0, 0, 2.3), 50)
    timed(f'pemeran_{tag}', f'{out}/pemeran_{tag}.png')

# portraits: one render per character, head and shoulders, tiled afterwards
for i, nama in enumerate(NAMA):
    studio(540, 540)
    c = cast.tokoh(nama)
    s = c.root.scale[0]
    zc = (1.27 + 0.85 + 0.93) * s + (0.9 * (c.spec.get('kepala_skala', 1) - 1)) * s
    c.place(0, 0, 18)
    stage.camera((2.6, -9.0 * s ** 0.5, zc + 0.2), (0, 0, zc - 0.2), 85)
    timed(f'potret {nama}', f'{out}/potret_{i:02d}_{nama}.png')
