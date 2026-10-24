"""Palette and matte "toy" materials (bible 03 §1: roughness 0.45-0.8, never glossy plastic)."""
import bpy

PALET = {
    'brand.oranye': '#FF8A3D', 'brand.tinta': '#2B2D42', 'caption.sorot': '#FFD23F',
    'andai.langit': '#8FD3FF', 'andai.cahaya': '#FFD9A0', 'andai.daun': '#5CC27A',
    'nyata.abu': '#8A9099', 'nyata.dingin': '#5E6E80', 'nyata.kabut': '#C9CED6', 'nyata.bahaya': '#E5484D',
    'malam.langit': '#1D2547', 'malam.lampu': '#FFC56B',
}
KULIT = {'terang': '#F2C9A0', 'sawo': '#C98E5A', 'gelap': '#8D5A3B'}


def srgb(hexc):
    """'#RRGGBB' -> linear RGB tuple (Blender colour inputs are linear)."""
    c = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def darker(hexc, f=0.8):
    """Same hue, scaled brightness (f < 1 darker, > 1 lighter, clamped)."""
    c = [min(255, int(int(hexc[i:i + 2], 16) * f)) for i in (1, 3, 5)]
    return '#%02X%02X%02X' % tuple(c)


def mat(hexc, rough=0.6, emit=0.0, alpha=1.0, sss=0.0, sheen=0.0, bump=0.0, pola=None):
    """Shared Principled material, looked up by its parameters so repeated parts reuse one datablock.

    sss    skin-like subsurface (soft, warm light bleed); sheen = soft cloth rim; bump = fine fabric grain.
    pola   (jenis, hex2, skala) pattern in object space: 'titik' dots, 'garis' stripes, 'kotak' checks, 'ombak' waves.
    """
    name = f'andai:{hexc}:{rough}:{emit}:{alpha}:{sss}:{sheen}:{bump}:{pola}'
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(hexc), 1)
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*srgb(hexc), 1)
        b.inputs['Emission Strength'].default_value = emit
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.2)
        b.inputs['Subsurface Scale'].default_value = 0.06
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
        b.inputs['Sheen Roughness'].default_value = 0.45
    if bump or pola:
        coord = nt.nodes.new('ShaderNodeTexCoord')
    if bump:
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 90.0
        noise.inputs['Detail'].default_value = 4.0
        nt.links.new(coord.outputs['Object'], noise.inputs['Vector'])
        bp = nt.nodes.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = bump
        bp.inputs['Distance'].default_value = 0.01
        nt.links.new(noise.outputs['Fac'], bp.inputs['Height'])
        nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    if pola:
        _pattern(nt, b, coord, hexc, *pola)
    return m


def _pattern(nt, bsdf, coord, hex1, jenis, hex2, skala):
    """Two-colour pattern into Base Color: a hard-edged mask (0/1) mixes `hex1` and `hex2`."""
    n = nt.nodes
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (skala, skala, skala)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    if jenis == 'titik':          # regular lattice of dots (Voronoi with no randomness)
        t = n.new('ShaderNodeTexVoronoi'); t.feature = 'F1'; t.inputs['Randomness'].default_value = 0.0
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); src = t.outputs['Distance']
        ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[1].position = 0.34
        ramp.color_ramp.elements[0].color = (1, 1, 1, 1); ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    elif jenis == 'kotak':
        t = n.new('ShaderNodeTexChecker')
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); src = t.outputs['Fac']
        ramp.color_ramp.elements[1].position = 0.5
    elif jenis == 'ombak':
        t = n.new('ShaderNodeTexWave'); t.wave_type = 'BANDS'; t.bands_direction = 'Z'
        t.inputs['Distortion'].default_value = 3.0; t.inputs['Detail'].default_value = 1.0
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); src = t.outputs['Fac']
        ramp.color_ramp.elements[1].position = 0.5
    else:                         # 'garis': horizontal stripes
        t = n.new('ShaderNodeTexWave'); t.wave_type = 'BANDS'; t.bands_direction = 'Z'
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); src = t.outputs['Fac']
        ramp.color_ramp.elements[1].position = 0.5
    nt.links.new(src, ramp.inputs['Fac'])
    mix = n.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (*srgb(hex1), 1)      # A (mask 0): base colour
    mix.inputs[7].default_value = (*srgb(hex2), 1)      # B (mask 1): pattern colour
    nt.links.new(ramp.outputs['Color'], mix.inputs[0])
    nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
