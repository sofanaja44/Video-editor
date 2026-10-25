"""Scene, render and light helpers shared by the Blender scripts (test sheets now, shot.py later)."""
import math
import bpy
from mathutils import Vector
from .materials import mat, srgb


def _enable_gpu(sc):
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
    sc.cycles.device = 'GPU'
    sc.cycles.denoising_use_gpu = True      # headless Blender denoises on the CPU by default: 20x slower


def fresh_scene(width, height, samples=64, device='GPU', fps=30):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y, sc.render.fps = width, height, fps
    sc.render.engine = 'CYCLES'
    sc.cycles.samples, sc.cycles.use_denoising, sc.cycles.max_bounces = samples, True, 4
    sc.cycles.device = 'CPU'
    if device == 'GPU':
        _enable_gpu(sc)
    sc.view_settings.view_transform = 'Khronos PBR Neutral'   # keeps the palette hexes true; AgX washes them out
    sc.cycles.volume_step_rate = 3.0                           # coarser steps: haze is smooth, 3x cheaper
    sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'   # crisper edges than colour-only denoising
    sc.render.image_settings.file_format = 'PNG'
    return sc


def sky(sc, hexc='#8FD3FF', strength=0.9):
    w = bpy.data.worlds.new('langit'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs[0].default_value = (*srgb(hexc), 1); bg.inputs[1].default_value = strength


def sun(rot_deg=(50, 0, -40), energy=4.0, hexc='#FFDDAD', angle_deg=8):
    bpy.ops.object.light_add(type='SUN', rotation=tuple(math.radians(a) for a in rot_deg))
    o = bpy.context.object
    o.data.energy, o.data.color, o.data.angle = energy, srgb(hexc), math.radians(angle_deg)
    return o


def floor(hexc='#9AA3AD', size=60):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    o = bpy.context.object
    o.data.materials.append(mat(hexc, 0.9))
    return o


def camera(loc, target, lens=50):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
