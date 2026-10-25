"""Road set test: wide establishing shot in three worlds, and Si Kamu on the motorbike (storyboard S03).
  blender -b --python andai/blender/uji_jalan.py -- OUT_DIR [SAMPLES]"""
import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import bpy
from mathutils import Vector
from andai.blender import cast, stage, lights, fx, camera, sets
from andai.blender.props import buat

args = sys.argv[sys.argv.index('--') + 1:]
out = os.path.abspath(args[0]); os.makedirs(out, exist_ok=True)
samples = int(args[1]) if len(args) > 1 else 64


def timed(label, path):
    t = time.time(); stage.render(path); print(f'{label}: {time.time() - t:.1f}s', flush=True)


def adegan(dunia, waktu, w=1080, h=1920):
    sc = stage.fresh_scene(w, h, samples)
    lights.setup(sc, waktu, target=(0, 6, 2.4))
    st = sets.bangun('jalan_raya', dunia, waktu, seed=62)
    return sc, st


# 1. wide, three worlds (S02: empty road, green light)
for dunia, waktu in (('andai', 'pagi'), ('nyata', 'pagi'), ('netral', 'malam')):
    sc, st = adegan(dunia, waktu)
    x, y, z, yaw = st.di('tiang')
    buat('lampu_lalu_lintas', status='hijau').place(x, y, 0, 0)
    for i, (xx, lane, warna) in enumerate(((-25, 'lajur_lawan_1', '#5B8DEF'), (-70, 'lajur_lawan_2', '#F2B84B'), (15, 'lajur_kanan', '#E85D75'))):
        ly = st.di(lane); buat('mobil', warna=warna).place(xx, ly[1], 0, ly[3])
    cam = camera.pasang(dict(gerak='pull_out', zoom=[1.0, 1.0], sudut='normal', jarak=48), (8, 6, 4.0), 1, 30, lensa=45)
    print('disembunyikan:', st.pandang(cam.location, (8, 6, 4)))
    if waktu != 'malam': fx.kabut(kepadatan=0.003 if dunia == 'andai' else 0.01, warna='#EAF2FF' if dunia == 'andai' else '#B8BEC8')
    timed(f'lebar_{dunia}_{waktu}', f'{out}/lebar_{dunia}_{waktu}.png')

# 2. S03: Si Kamu on the motorbike in the far outer lane, low-angle truck; then a close-up of the seat/pose
for label, spec, jarak, lensa in (('s03_naik_motor', dict(gerak='truck', geser=0.04, sudut='rendah'), 24, None),
                                  ('s03_cu', dict(gerak='cu', sudut='normal'), 9.5, 60)):
    sc, st = adegan('andai', 'pagi')
    x, y, z, yaw = st.di('lajur_kiri')
    m = buat('motor', warna='#C8333B'); m.place(10, y, 0, yaw)
    kamu = cast.kamu()
    kamu.root.parent = m.root; kamu.root.location = (0, 0.35, 0)
    kamu.pose('naik_motor'); kamu.expression('senyum')
    ly = st.di('lajur_kanan'); buat('mobil', warna='#5B8DEF').place(-30, ly[1], 0, ly[3])      # behind the rider, not in front of the lens
    buat('angkot').place(48, ly[1], 0, ly[3])
    cam = camera.pasang(spec, (10, y, 2.6), 1, 60, jarak=jarak, lensa=lensa)
    print('disembunyikan:', st.pandang(cam.location, (10, y, 2.6)))
    fx.dof(cam, m.root, 2.4); fx.kabut(kepadatan=0.003, warna='#EAF2FF'); fx.bloom(sc, 0.3)
    timed(label, f'{out}/{label}.png')
