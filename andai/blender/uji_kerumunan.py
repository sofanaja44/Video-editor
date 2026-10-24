"""Stress test: a crowd shot with every effect on; prints scene build time, object count and render time.
  blender -b --python andai/blender/uji_kerumunan.py -- OUT_DIR"""
import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import bpy
from andai.blender import cast, stage, lights, fx

args = sys.argv[sys.argv.index('--') + 1:]
out = os.path.abspath(args[0]); os.makedirs(out, exist_ok=True)


def shot(label, jumlah, samples, waktu='siang', efek=True, sebar='lajur_penuh'):
    t0 = time.time()
    sc = stage.fresh_scene(1080, 1920, samples)
    lights.setup(sc, waktu, target=(0, 6, 2.2))
    stage.floor('#B7B2A4', 300)
    hero = cast.tokoh('kamu'); hero.place(-1.0, -1.0, 20); hero.pose('berdiri'); hero.expression('kaget')
    pol = cast.tokoh('polisi'); pol.place(1.6, 0.5, -20); pol.pose('menunjuk')
    cast.kerumunan(jumlah, sebar, seed=4, pusat=(0, 5), lebar=9, kedalaman=16)
    cam = stage.camera((0, -12.5, 3.2), (0, 3, 2.4), 50)
    if efek:
        fx.dof(cam, hero.j['kepala'], 2.2); fx.motion_blur(sc); fx.kabut(kepadatan=0.004, warna='#EAF2FF')
        fx.debu((0, 4, 3), (9, 12, 5), 45, seed=2); fx.bloom(sc, 0.35)
    nobj = len(bpy.data.objects)
    t1 = time.time()
    stage.render(f'{out}/{label}.png')
    print(f'KERUMUNAN {label}: {jumlah} extras, {nobj} objects, build {t1 - t0:.1f}s, render {time.time() - t1:.1f}s', flush=True)


shot('kerumunan_28', 28, 64)
shot('kerumunan_28_128', 28, 128)
shot('kerumunan_60', 60, 64)
shot('kerumunan_sore', 28, 64, 'sore')
