"""Build-only check (no rendering) of every crowd formation, every role and every cast member in each pose.
  blender -b --python andai/blender/uji_kerumunan_bentuk.py     (prints OK lines and ALL OK)"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from andai.blender import cast, stage, poses

stage.fresh_scene(64, 64, 1, device='CPU')
ok = True
for sebar in ('deret', 'lajur_penuh', 'antre_lajur', 'serobot_lajur', 'acak'):
    cs = cast.kerumunan(9, sebar, seed=1)
    spread = max(c.root.location.x for c in cs) - min(c.root.location.x for c in cs)
    print('OK  ', f'{sebar:14s}', len(cs), 'characters, x spread', round(spread, 2))
    ok &= len(cs) == 9
for peran in cast.PERAN:
    c = cast.warga(1, 1, peran); print('OK  ', 'peran', peran, c.spec['tinggi'])
for nama in cast.PEMERAN:
    c = cast.tokoh(nama)
    for p in list(poses.POSES) + ['jalan']:
        c.pose(p, 0.3)
    for e in poses.EKSPRESI:
        c.expression(e)
    c.expression('tawa', frame=10); c.pose('duduk', frame=10); c.blink(60)
    print('OK  ', nama, 'all poses + expressions + keyframes')
print('ALL OK' if ok else 'SOME FAILED')
