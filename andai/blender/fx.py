"""Render effects that stay physical (Cycles): depth of field, motion blur, fog, drifting dust, bloom.
Film grain, vignette and the world grade belong to the Python compositing step (motion/fx.py)."""
import math
import random
import bpy
from .materials import mat, srgb


def dof(cam, fokus, fstop=2.8):
    """Depth of field focused on an object (or a distance in scene units); lower f-stop = blurrier background."""
    d = cam.data.dof
    d.use_dof = True
    d.aperture_fstop = fstop
    if isinstance(fokus, (int, float)):
        d.focus_distance = fokus
    else:
        d.focus_object = fokus


def motion_blur(sc, shutter=0.5):
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = shutter


def volume_kotak(pusat, ukuran, kepadatan, warna='#FFFFFF', anisotropi=0.3, nama='kabut'):
    """A box filled with scattering haze. Keep it finite: an infinite world volume hides the sky and costs more."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pusat)
    o = bpy.context.object; o.name = nama
    o.scale = ukuran
    m = bpy.data.materials.new(nama); m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes['Principled BSDF'])            # volume only: no surface, rays pass through
    vs = nt.nodes.new('ShaderNodeVolumeScatter')
    vs.inputs['Color'].default_value = (*srgb(warna), 1)
    vs.inputs['Density'].default_value = kepadatan
    vs.inputs['Anisotropy'].default_value = anisotropi
    nt.links.new(vs.outputs['Volume'], nt.nodes['Material Output'].inputs['Volume'])
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


def kabut(pusat=(0, 25, 12), ukuran=(140, 140, 40), kepadatan=0.006, warna='#FFFFFF'):
    """Atmospheric haze for depth (bible: thin in Dunia Andai, thick and grey in Dunia Nyata)."""
    return volume_kotak(pusat, ukuran, kepadatan, warna)


def debu(pusat, ukuran, jumlah=45, seed=0, frame0=1, frame1=150, laju=0.6):
    """Dust motes floating in a box (bible 6.3 `debu_melayang`): tiny glowing spheres on slow linear drifts.
    Deterministic per seed. With depth of field the near ones turn into soft bokeh discs."""
    rng = random.Random(seed)
    m = mat('#FFF3D6', 0.5, emit=1.6)
    pref = bpy.context.preferences.edit
    old = pref.keyframe_new_interpolation_type
    pref.keyframe_new_interpolation_type = 'LINEAR'
    out = []
    try:
        for i in range(jumlah):
            p = [pusat[k] + rng.uniform(-0.5, 0.5) * ukuran[k] for k in range(3)]
            bpy.ops.mesh.primitive_uv_sphere_add(radius=rng.uniform(0.02, 0.05), segments=8, ring_count=6, location=p)
            o = bpy.context.object; o.name = f'debu_{i}'; o.data.materials.append(m)
            o.keyframe_insert('location', frame=frame0)
            drift = (rng.uniform(-1, 1) * laju, rng.uniform(-1, 1) * laju * 0.5, rng.uniform(0.1, 1) * laju * 0.6)
            o.location = (p[0] + drift[0], p[1] + drift[1], p[2] + drift[2])
            o.keyframe_insert('location', frame=frame1)
            out.append(o)
    finally:
        pref.keyframe_new_interpolation_type = old
    return out


def bloom(sc, kekuatan=0.35, ambang=1.0, ukuran=0.55):
    """Soft glow around bright areas via the compositor (Blender 5: a compositor node group)."""
    ng = bpy.data.node_groups.new('andai_komposit', 'CompositorNodeTree')
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers')
    gl = ng.nodes.new('CompositorNodeGlare')
    out = ng.nodes.new('NodeGroupOutput')
    gl.inputs['Type'].default_value = 'Bloom'
    gl.inputs['Strength'].default_value = kekuatan
    gl.inputs['Threshold'].default_value = ambang
    gl.inputs['Size'].default_value = ukuran
    ng.links.new(rl.outputs['Image'], gl.inputs['Image'])
    ng.links.new(gl.outputs['Image'], out.inputs['Image'])
    sc.compositing_node_group = ng
    sc.render.use_compositing = True
