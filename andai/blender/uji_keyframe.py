"""Numeric check of the keyframed paths (walk cycle, place, pose ramp, expression, hold) - no rendering.

  blender -b --python andai/blender/uji_keyframe.py      (prints OK/FAIL lines and ALL OK)
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from andai.blender import cast, stage, poses
sc = stage.fresh_scene(64, 64, 1, device='CPU')
c = cast.kamu()
c.walk(11, 27, cycle=8, step=2)
c.place(0, 0, frame=11); c.place(8, 0, frame=27, ramp=16)
c.pose('berdiri', frame=34, ramp=4)
c.expression('kaget', frame=40, ramp=3)
ok = True
def chk(label, got, want, tol=1e-3):
    global ok
    good = abs(got - want) < tol; ok &= good
    print(('OK  ' if good else 'FAIL'), label, round(got, 4), 'want', round(want, 4))
paha, lutut = c.j['paha_L'], c.j['lutut_L']
sc.frame_set(1);  chk('paha_L f1 (still standing)', paha.rotation_euler.x, 0)
sc.frame_set(1);  chk('lutut_L f1 (still standing)', lutut.rotation_euler.x, 0)
sc.frame_set(11); chk('lutut_L f11 (walk starts)', lutut.rotation_euler.x, math.radians(poses.jalan(0)['lutut_L']))
for f, ph in ((11, 0), (13, .25), (15, .5), (17, .75), (19, 0)):
    sc.frame_set(f); chk(f'paha_L f{f}', paha.rotation_euler.x, -math.radians(poses.jalan(ph)['paha_L']))
sc.frame_set(11); chk('x f11', c.root.location.x, 0)
sc.frame_set(19); chk('x f19', c.root.location.x, 4, 0.05)
sc.frame_set(27); chk('x f27', c.root.location.x, 8)
sc.frame_set(34); chk('paha_L f34 (berdiri)', paha.rotation_euler.x, 0)
sc.frame_set(1);  chk('eye scale f1 (netral)', c.face['eye']['L'][0].scale.x, 1.0)
sc.frame_set(40); chk('eye scale f40 (kaget)', c.face['eye']['L'][0].scale.x, 1.3)
sc.frame_set(60); chk('eye scale f60 (holds)', c.face['eye']['L'][0].scale.x, 1.3)
print('ALL OK' if ok else 'SOME FAILED')
