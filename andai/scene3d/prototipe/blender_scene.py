"""Blender version of the prototype shot, for render-speed comparison.

Usage (bpy module):   python blender_scene.py ENGINE OUT.jpg SAMPLES [CPU|GPU]
Usage (Blender app):  blender -b --python blender_scene.py -- ENGINE OUT.jpg SAMPLES [CPU|GPU]
ENGINE: CYCLES | BLENDER_EEVEE | BLENDER_WORKBENCH. OUT must be an absolute path.
"""
import bpy, math, sys, time
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
engine, out, samples = args[0], args[1], int(args[2])
device = args[3] if len(args) > 3 else "CPU"
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.engine = engine
if engine == 'CYCLES':
    sc.cycles.device = device; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    if device == 'GPU':
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for backend in ('OPTIX', 'CUDA', 'HIP', 'ONEAPI'):
            try:
                prefs.compute_device_type = backend
                prefs.get_devices()
                if any(d.type == backend for d in prefs.devices):
                    break
            except TypeError:
                continue
        for d in prefs.devices:
            d.use = d.type != 'CPU'
        print('cycles devices:', [(d.name, d.type, d.use) for d in prefs.devices])
sc.view_settings.view_transform = 'AgX'
sc.render.image_settings.file_format = 'JPEG'

world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.78, 1.0, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 0.9

def mat(hexc, rough=0.55):
    m = bpy.data.materials.new(hexc); m.use_nodes = True
    c = tuple(int(hexc[i:i+2], 16) / 255 for i in (1, 3, 5))
    c = tuple(x ** 2.2 for x in c)
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Roughness'].default_value = rough
    return m

def obj(kind, loc, scale=(1, 1, 1), m=None, rot=(0, 0, 0), parent=None, **kw):
    getattr(bpy.ops.mesh, f'primitive_{kind}_add')(location=loc, rotation=rot, **kw)
    o = bpy.context.object; o.scale = scale
    if m: o.data.materials.append(m)
    if kind in ('uv_sphere', 'cylinder', 'cone'):
        bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o

# world (Blender: Z up)
obj('cube', (0, 0, -0.05), (30, 4, 0.05), mat('#55595f', 0.9))
obj('cube', (0, 5.2, 0.12), (30, 1.5, 0.12), mat('#c9c2b6', 0.8))
cols = ['#f2b7c6', '#a9d6c1', '#f6d48b', '#b9c8f2']
for i in range(4):
    x = -7.5 + i * 5
    obj('cube', (x, 9.5, 1.75), (2.2, 1.6, 1.5), mat(cols[i]))
    obj('cone', (x, 9.5, 4.05), (3.4, 2.5, 0.8), mat('#c4553f'), rot=(0, 0, math.pi / 4), vertices=4)
    obj('cube', (x + 1.0, 7.88, 1.95), (0.5, 0.05, 0.4), mat('#dff3ff', 0.2))
    for k in range(-4, 5):
        obj('cube', (x + k * 0.5, 6.9, 0.7), (0.04, 0.04, 0.45), mat('#2f3b4a'))
obj('cylinder', (2.4, 4.6, 3), (0.1, 0.1, 3), mat('#8a8f96'), vertices=16)

skin, shirt, jeans, hair = mat('#c98e5a', 0.45), mat('#e8743b', 0.7), mat('#2f4a6d', 0.8), mat('#1c1a1a', 0.6)
X, Y = 0.2, 2.2
obj('uv_sphere', (X, Y, 3.05), (1.05, 1.0, 1.2), skin, segments=48, ring_count=32)
obj('uv_sphere', (X, Y - 0.05, 2.7), (1.12, 0.98, 0.85), skin, segments=48, ring_count=32)
obj('uv_sphere', (X, Y + 0.03, 3.25), (1.08, 1.04, 1.12), hair, segments=48, ring_count=32)
for dx, ry in [(-0.25, -0.5), (0.05, -0.1), (0.32, 0.4)]:
    obj('cone', (X + dx, Y + 0.1, 4.3), (0.22, 0.22, 0.3), hair, rot=(0.5, ry, 0), vertices=16)
for s in (-1, 1):
    obj('uv_sphere', (X + s * 0.36, Y - 0.86, 3.13), (0.25, 0.12, 0.29), mat('#ffffff', 0.2))
    obj('uv_sphere', (X + s * 0.34, Y - 0.97, 3.11), (0.11, 0.05, 0.11), mat('#141414', 0.15))
    obj('cylinder', (X + s * 0.36, Y - 0.88, 3.55), (0.05, 0.05, 0.16), hair, rot=(0, math.pi / 2 + s * 0.12, 0), vertices=12)
    obj('cylinder', (X + s * 0.28, Y, 0.6), (0.17, 0.17, 0.55), jeans, vertices=24)
    obj('uv_sphere', (X + s * 0.28, Y - 0.08, 0.05), (0.25, 0.37, 0.12), mat('#3fa34d', 0.6))
    obj('cylinder', (X + s * 0.75, Y, 1.55), (0.15, 0.15, 0.5), shirt, rot=(0, s * 0.15, 0), vertices=24)
    obj('uv_sphere', (X + s * 0.82, Y, 0.98), (0.2, 0.2, 0.2), skin)
obj('torus', (X, Y - 0.93, 2.55), (1, 1, 1), mat('#5a1f1f', 0.4), rot=(math.pi / 2, 0, 0), major_radius=0.22, minor_radius=0.045)
obj('uv_sphere', (X, Y, 1.45), (0.62, 0.5, 0.95), shirt, segments=48, ring_count=32)

bpy.ops.object.light_add(type='SUN', rotation=(math.radians(50), 0, math.radians(-40)))
sun = bpy.context.object; sun.data.energy = 4.0; sun.data.angle = math.radians(8); sun.data.color = (1.0, 0.86, 0.68)
bpy.ops.object.camera_add(location=(X - 2.2, Y - 9.5, 2.75))
cam = bpy.context.object; cam.data.lens = 50; sc.camera = cam
d = Vector((X, Y, 2.3)) - cam.location; cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
sc.render.filepath = out
t = time.time(); bpy.ops.render.render(write_still=True); print(f'{engine} {device} samples={samples} render {time.time() - t:.1f}s')
