"""Lighting presets per time of day (bible 04 §6.3): gradient sky that also lights the scene, a soft sun,
a fill light from the camera side and a rim light from behind. World grade (andai/nyata) is done in compositing;
only the fog differs here (see fx.kabut)."""
import math
import bpy
from .materials import srgb

WAKTU = {
    'pagi':  dict(arah=(38, 0, -65), matahari='#FFD6A0', daya=3.4, zenit='#7DBFF2', cakrawala='#FFE6C4', tanah='#B9B1A4',
                  langit=0.95, isi=0.9, pinggir=1.2, pinggir_warna='#FFE2B8', eksposur=-0.2),
    'siang': dict(arah=(58, 0, -40), matahari='#FFF0DC', daya=4.4, zenit='#6FB8F0', cakrawala='#E6F2FF', tanah='#B4B7BA',
                  langit=0.88, isi=0.9, pinggir=1.0, pinggir_warna='#FFFFFF', eksposur=-0.25),
    'sore':  dict(arah=(76, 0, -75), matahari='#FF9A52', daya=3.8, zenit='#6A9AD4', cakrawala='#FFC08A', tanah='#A89A8C',
                  langit=0.85, isi=0.8, pinggir=1.8, pinggir_warna='#FFB070', eksposur=-0.2),
    'malam': dict(arah=(48, 0, 140), matahari='#9DB4FF', daya=0.7, zenit='#141B38', cakrawala='#33447A', tanah='#1F2433',
                  langit=0.6, isi=0.5, pinggir=1.2, pinggir_warna='#9DB4FF', eksposur=0.3),
}


def langit(sc, zenit, cakrawala, tanah, kekuatan=1.0):
    """Vertical three-stop gradient world: ground colour below the horizon, horizon glow, zenith above."""
    w = bpy.data.worlds.new('langit'); sc.world = w; w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes['Background']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    rng = nt.nodes.new('ShaderNodeMapRange')
    rng.inputs['From Min'].default_value, rng.inputs['From Max'].default_value = -1.0, 1.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    el = ramp.color_ramp.elements
    el[0].position, el[0].color = 0.0, (*srgb(tanah), 1)
    el[1].position, el[1].color = 1.0, (*srgb(zenit), 1)
    for pos, col in ((0.47, tanah), (0.52, cakrawala), (0.64, zenit)):
        e = el.new(pos); e.color = (*srgb(col), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Z'], rng.inputs['Value'])
    nt.links.new(rng.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = kekuatan
    return w


def _spot(name, loc, target, watt, hexc, radius=2.0, sudut=70):
    """Soft spot aimed at `target`. (Area lights were tried first: their one-sided plane cut the floor with a hard edge.)"""
    from mathutils import Vector
    bpy.ops.object.light_add(type='SPOT', location=loc)
    o = bpy.context.object; o.name = name
    o.data.energy, o.data.color = watt, srgb(hexc)
    o.data.shadow_soft_size, o.data.spot_size, o.data.spot_blend = radius, math.radians(sudut), 1.0
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


def setup(sc, waktu='siang', target=(0, 0, 2.2), jarak=14.0):
    """Sky + sun + fill + rim for the given time of day, aimed at `target` (the action area)."""
    p = WAKTU[waktu]
    sc.view_settings.exposure = p['eksposur']
    langit(sc, p['zenit'], p['cakrawala'], p['tanah'], p['langit'])
    bpy.ops.object.light_add(type='SUN', rotation=tuple(math.radians(a) for a in p['arah']))
    sun = bpy.context.object; sun.name = f'matahari_{waktu}'
    sun.data.energy, sun.data.color, sun.data.angle = p['daya'], srgb(p['matahari']), math.radians(6)
    tx, ty, tz = target
    fill = _spot('isi', (tx - 0.6 * jarak, ty - jarak, tz + 4.0), target, 7000 * p['isi'], p['cakrawala'], 3.0, 80)
    rim = _spot('pinggir', (tx + 0.45 * jarak, ty + jarak, tz + 5.5), target, 10000 * p['pinggir'], p['pinggir_warna'], 1.5, 55)
    return dict(sun=sun, isi=fill, pinggir=rim)
