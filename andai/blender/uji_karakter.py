"""Character test sheets: poses, the 12 expressions, the cast line-up and a blink check.

  blender -b --python andai/blender/uji_karakter.py -- OUT_DIR [SAMPLES]
Writes poses.png, cast.png and ekspresi_XX_<nama>.png (tile them with ffmpeg, see uji_karakter.sh).
"""
import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from andai.blender import cast, poses, stage

args = sys.argv[sys.argv.index('--') + 1:]
out = os.path.abspath(args[0]); os.makedirs(out, exist_ok=True)
samples = int(args[1]) if len(args) > 1 else 48


def studio(w, h):
    sc = stage.fresh_scene(w, h, samples)
    stage.sky(sc, '#BFD4E8', 0.9); stage.sun(); stage.floor()
    return sc


def timed(label, path):
    t = time.time(); stage.render(path); print(f'{label}: {time.time() - t:.1f}s', flush=True)


# 1. poses (one Si Kamu per pose)
studio(2400, 1000)
lineup = [('berdiri', 0), ('jalan', 0.25), ('duduk', 0), ('menunjuk', 0), ('angkat_bahu', 0), ('pegang', 0)]
for i, (p, ph) in enumerate(lineup):
    c = cast.kamu(); c.place((i - 2.5) * 3.7, 0, 0); c.pose(p, ph)
    c.expression('senyum' if p != 'angkat_bahu' else 'bingung')
stage.camera((0, -34, 2.3), (0, 0, 2.3), 50)
timed('poses', f'{out}/poses.png')

# 1b. the same poses seen from the side (yaw 90: faces +X), to check joint signs
studio(2400, 1000)
for i, (p, ph) in enumerate(lineup):
    c = cast.kamu(); c.place((i - 2.5) * 3.7, 0, 90); c.pose(p, ph); c.expression('netral')
stage.camera((0, -34, 2.3), (0, 0, 2.3), 50)
timed('poses_samping', f'{out}/poses_samping.png')

# 1c. every hair style on Si Kamu's body
studio(2400, 900)
from andai.blender import rig
for i, st in enumerate(['cepak', 'jambul', 'kuncir', 'keriting', 'bob', 'botak']):
    c = rig.Character(dict(cast.KAMU, gaya_rambut=st), f'rambut_{st}'); c.place((i - 2.5) * 3.7, 0, 0 if i % 2 == 0 else 35)
stage.camera((0, -34, 2.3), (0, 0, 2.3), 50)
timed('rambut', f'{out}/rambut.png')

# 2. cast line-up: Si Kamu + 5 numbered extras
studio(2400, 900)
people = [cast.kamu()] + [cast.warga(n, seed=7) for n in range(1, 6)]
for i, c in enumerate(people):
    c.place((i - 2.5) * 3.7, 0, 0); c.expression('netral')
    print(c.name, c.spec['gaya_rambut'], c.spec['baju'], c.spec['kulit'])
stage.camera((0, -34, 2.3), (0, 0, 2.3), 50)
timed('cast', f'{out}/cast.png')

# 3. expressions: close-up of the head
studio(480, 480)
c = cast.kamu()
stage.camera((0, -10, 3.0), (0, 0, 3.0), 85)
for i, name in enumerate(poses.EKSPRESI):
    c.expression(name)
    timed(f'ekspresi {name}', f'{out}/ekspresi_{i:02d}_{name}.png')

# 4. blink check: keyed blinks on a character that smiles for 4 seconds
sc = studio(480, 480)
c = cast.kamu(); c.expression('senyum', frame=1); c.blink(120, fps=30); c.pose('berdiri', frame=1)
stage.camera((0, -10, 3.0), (0, 0, 3.0), 85)
eye = c.face['eye']['L'][0]
closed = []
for f in range(1, 121):
    sc.frame_set(f)
    if eye.scale.z < 0.5 * eye.scale.x:
        closed.append(f)
print('blink frames (eyes closed):', closed)
if closed:
    sc.frame_set(closed[0]); timed('kedip', f'{out}/kedip.png')
