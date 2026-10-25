"""Close, 3/4 and side views of Si Kamu to judge model quality.   blender -b --python uji_model.py -- OUT_DIR [SAMPLES]"""
import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from andai.blender import cast, stage

args = sys.argv[sys.argv.index('--') + 1:]
out = os.path.abspath(args[0]); os.makedirs(out, exist_ok=True)
samples = int(args[1]) if len(args) > 1 else 64

sc = stage.fresh_scene(1500, 1000, samples)
stage.sky(sc, '#BFD4E8', 0.9); stage.sun(); stage.floor()
for i, yaw in enumerate((0, 40, 90, 180)):
    c = cast.kamu(); c.place((i - 1.5) * 3.4, 0, yaw); c.pose('berdiri'); c.expression('senyum')
stage.camera((0, -22, 2.4), (0, 0, 2.3), 50)
t = time.time(); stage.render(f'{out}/model_kamu.png'); print(f'model_kamu: {time.time() - t:.1f}s')

# head close-up from 3/4 view
sc = stage.fresh_scene(1000, 1000, samples)
stage.sky(sc, '#BFD4E8', 0.9); stage.sun(); stage.floor()
c = cast.kamu(); c.place(0, 0, 25); c.expression('senyum')
stage.camera((3.5, -9.0, 3.4), (0, 0, 2.9), 85)
t = time.time(); stage.render(f'{out}/kepala_34.png'); print(f'kepala_34: {time.time() - t:.1f}s')
