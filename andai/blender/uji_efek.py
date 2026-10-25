"""Effects test: the same shot plain vs with lights/DOF/fog/dust/bloom/motion blur, with render times.
  blender -b --python andai/blender/uji_efek.py -- OUT_DIR"""
import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import bpy
from andai.blender import cast, stage, lights, fx

args = sys.argv[sys.argv.index('--') + 1:]
out = os.path.abspath(args[0]); os.makedirs(out, exist_ok=True)
W, H = 1080, 1920


def shot(label, samples, efek, waktu='siang'):
    sc = stage.fresh_scene(W, H, samples)
    if efek:
        lights.setup(sc, waktu, target=(0, 0, 2.2))
    else:
        stage.sky(sc, '#BFD4E8', 0.9); stage.sun()
    stage.floor('#A9A596' if efek else '#9AA3AD', 200)
    hero = cast.kamu(); hero.expression('senyum')
    hero.place(-1.2, 0, 15, frame=1); hero.place(1.2, 0, 15, frame=31, ramp=30)
    hero.walk(1, 31, cycle=16, step=1, ramp_in=0)
    for i, (x, y) in enumerate(((-3.2, 5), (2.8, 9), (-1.5, 14), (3.0, 20), (0.2, 28))):
        w = cast.warga(i + 1, seed=3); w.place(x, y, 180 + 10 * i); w.pose('berdiri'); w.expression('netral')
    cam = stage.camera((0, -11.5, 2.7), (0, 0, 2.3), 50)
    if efek:
        fx.dof(cam, hero.j['kepala'], fstop=2.0)
        fx.motion_blur(sc, 0.5)
        fx.kabut(sc, 0.008, '#EAF2FF')
        fx.debu((0, 2, 3), (9, 10, 5), 90, seed=5, frame0=1, frame1=31)
        fx.bloom(sc, 0.4, 1.0, 0.6)
    sc.frame_set(15)
    t = time.time(); stage.render(f'{out}/{label}.png'); print(f'RENDER {label} @{samples} spp: {time.time() - t:.2f}s', flush=True)


shot('dasar', 64, False)
shot('efek_64', 64, True)
shot('efek_128', 128, True)
for w in ('pagi', 'sore', 'malam'):
    shot(f'efek_{w}', 64, True, w)
