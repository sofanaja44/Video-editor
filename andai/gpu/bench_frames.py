"""Steady-state render time per frame for the prototype shot (one Blender session, N frames).

The first frame of a session includes kernel loading, so judge speed from the later frames.
Usage: blender -b --python andai/gpu/bench_frames.py -- ENGINE OUT.jpg SAMPLES [CPU|GPU] [FRAMES]
"""
import os, sys, time

args = sys.argv[sys.argv.index("--") + 1:]
frames = int(args[4]) if len(args) > 4 else 4
scene_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scene3d", "prototipe", "blender_scene.py")
# Build the scene from the prototype, minus its final single-frame render line.
exec(compile(open(scene_py).read().rstrip("\n").rsplit("\n", 1)[0], scene_py, "exec"))

sc.render.use_persistent_data = True
for i in range(frames):
    cam.location.x = X - 2.2 + i * 0.1
    sc.render.filepath = os.path.splitext(out)[0] + f"_{i}.jpg"
    t = time.time(); bpy.ops.render.render(write_still=True)
    print(f"frame {i} {engine} {device} samples={samples} render {time.time() - t:.2f}s", flush=True)
