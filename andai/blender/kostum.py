"""Costume and accessory builders (bible 03 §3). Each takes the Character first and is listed in a cast spec as
`ekstra=[('nama', {kwargs}), ...]`. Pieces are parented to the joint they move with (torso -> `badan`,
skirts -> `pinggul`, head gear and glasses -> `head_c`).

Frames: head parts use the head-centre frame (see rig.head_r / front_y); torso parts use the `badan` frame
(origin at the hip, torso centre at z = rig.TORSO_DZ, torso radius 0.62 x 0.5 deep, scaled by spec 'lebar').
"""
import math
import bpy
from . import geo
from .materials import mat, darker
from .rig import head_r, front_y, yaw_at, HEAD_A, HEAD_DEPTH, TORSO_DZ


def _smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def torso_r(z):
    """Unscaled torso radius at height z (badan frame): capsule r 0.62, cylinder part 0.7 long."""
    d = abs(z - TORSO_DZ) - 0.35
    return 0.62 if d <= 0 else math.sqrt(max(0.62 ** 2 - d * d, 0.0))


def torso_front(c, x, z, margin=0.0):
    """Y of the torso's front surface at (x, z), including the width factor."""
    w = c.spec.get('lebar', 1.0)
    rx = (torso_r(z) + margin) * w
    return -0.8 * w * (torso_r(z) + margin) * math.sqrt(max(0.0, 1 - (x / max(rx, 1e-3)) ** 2))


def torso_patch(c, nama, z0, z1, margin, material, gap_deg=0.0, nv=14, tebal=0.03):
    """Surface wrapped around the torso between heights z0..z1; `gap_deg` leaves an opening at the front."""
    w = c.spec.get('lebar', 1.0)
    gap = math.radians(gap_deg)

    def fn(u, v):
        th = 1.5 * math.pi + gap + u * (2 * math.pi - 2 * gap)
        z = z0 + (z1 - z0) * v
        r = torso_r(z) + margin
        return (r * w * math.cos(th), 0.8 * w * r * math.sin(th), z)

    o = geo.surface(f'{c.name}.{nama}', fn, 56, nv, material, wrap=gap_deg == 0, parent=c.j['badan'])
    md = o.modifiers.new('tebal', 'SOLIDIFY'); md.thickness = tebal; md.offset = 0
    return o


def _head_loop(nama, c, z, scale, tebal, material, parent=None):
    """Closed tube around the head at height z."""
    r = head_r(z) * scale
    pts = [(r * math.cos(a), HEAD_DEPTH * r * math.sin(a), z) for a in (2 * math.pi * i / 40 for i in range(40))]
    return geo.tube(f'{c.name}.{nama}', pts, tebal, material, closed=True, sides=8, up=(0, 0, 1), parent=parent or c.head_c)


# ---- clothing ---------------------------------------------------------------------------------
def rok(c, panjang=0.6, atas=0.66, bawah=0.85, warna=None, pola=None, tepi=None):
    """Skirt / dress skirt / loose tunic hem, hanging from the hip (moves with the pelvis)."""
    s = c.spec
    m = mat(warna or s['baju'], 0.7, sheen=0.3, bump=0.5, pola=pola if pola is not None else s.get('baju_pola')) \
        if (warna or s['baju']) else c.m['skin']
    top, bot = 0.3, -panjang
    prof = [(0.0, top + 0.02), (atas * 0.98, top)]
    n = 10
    for i in range(1, n + 1):
        t = i / n
        prof.append((atas + (bawah - atas) * t ** 1.25, top + (bot - top) * t))
    prof.append((bawah * 0.97, bot - 0.02)); prof.append((0.0, bot - 0.02))
    w = s.get('lebar', 1.0)
    o = geo.lathe(f'{c.name}.rok', prof, m, 56, depth=0.82, parent=c.j['pinggul'], scale=(w, w, 1))
    if tepi:
        pts = [(bawah * 0.985 * math.cos(a), 0.82 * bawah * 0.985 * math.sin(a), bot) for a in (2 * math.pi * i / 48 for i in range(48))]
        geo.tube(f'{c.name}.rok_tepi', pts, 0.035, mat(tepi, 0.6), closed=True, sides=8, up=(0, 0, 1),
                 parent=c.j['pinggul'], scale=(w, w, 1))
    return o


def kerudung(c, warna, motif=None, bukaan=(0.98, 1.02, -0.15), panjang=1.62):
    """Hijab: a shell over the head that drapes onto the shoulders, with the face cut out by an oval Boolean."""
    n = c.name
    m = mat(warna, 0.7, sheen=0.5, bump=0.5, pola=motif)
    X0, Z0, zc = bukaan
    top = HEAD_A + 0.03

    def fn(u, v):
        th = 2 * math.pi * u
        f = (1 - math.sin(th)) / 2
        z_low = -panjang - 0.28 * (1 - f)
        z = z_low + (top - z_low) * math.sin(v * math.pi / 2)
        drape = _smooth(0.55, 1.45, -z)
        r = head_r(z) * 1.13 + 0.9 * drape
        d = HEAD_DEPTH - 0.38 * drape
        return (r * math.cos(th), d * r * math.sin(th), z)

    hood = geo.surface(f'{n}.kerudung', fn, 72, 28, m, parent=c.head_c)
    md = hood.modifiers.new('tebal', 'SOLIDIFY'); md.thickness = 0.06; md.offset = 0
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.0, depth=3.2, rotation=(math.pi / 2, 0, 0),
                                        location=(0, -1.65, zc))
    cut = bpy.context.object; cut.name = f'{n}.kerudung_potong'
    cut.scale = (X0, 1.0, Z0)
    cut.parent = c.head_c
    cut.hide_render = True; cut.hide_viewport = True
    bl = hood.modifiers.new('wajah', 'BOOLEAN'); bl.operation = 'DIFFERENCE'; bl.object = cut; bl.solver = 'EXACT'
    return hood


def saku_dada(c, jumlah=2, warna=None, z=0.36):
    """Patch pockets with a small flap on the chest."""
    w = c.spec.get('lebar', 1.0)
    col = warna or darker(c.spec['baju'], 0.86)
    m = mat(col, 0.7, sheen=0.3, bump=0.5)
    xs = (-0.27, 0.27) if jumlah == 2 else (0.27,)
    for x in xs:
        x *= w
        yaw = math.asin(max(-0.9, min(0.9, x / (0.62 * w))))
        y = torso_front(c, x, z, 0.0) - 0.01
        geo.rbox(f'{c.name}.saku', (0.3, 0.07, 0.26), 0.025, m, parent=c.j['badan'], loc=(x, y, z), rot=(0, 0, yaw))
        geo.rbox(f'{c.name}.saku_tutup', (0.31, 0.08, 0.06), 0.02, m, parent=c.j['badan'], loc=(x, y - 0.005, z + 0.15), rot=(0, 0, yaw))


def sabuk(c, warna='#2B2420', z=-0.12, tebal=0.13, gesper='#D9B64A'):
    """Belt around the waist with a buckle."""
    torso_patch(c, 'sabuk', z - tebal / 2, z + tebal / 2, 0.02, mat(warna, 0.4, sheen=0.1), tebal=0.02)
    y = torso_front(c, 0, z, 0.03)
    geo.rbox(f'{c.name}.gesper', (0.14, 0.05, 0.12), 0.02, mat(gesper, 0.3), parent=c.j['badan'], loc=(0, y - 0.01, z))


def tali_id(c, warna='#2B6CB0', kartu='#F4F4F4'):
    """Lanyard with a blank ID card (the service officer; bible: no emblem)."""
    pts = []                                     # one strand: shoulder (x 0.24, z 0.9) down to the card (x 0, z 0)
    for i in range(11):
        t = i / 10
        x, z = 0.24 * (1 - t), 0.9 * (1 - t)
        pts.append((x, torso_front(c, x, z, 0.012), z))
    m = mat(warna, 0.6)
    for sx in (-1, 1):
        geo.tube(f'{c.name}.tali', [(sx * p[0], p[1], p[2]) for p in pts], 0.022, m, sides=6, parent=c.j['badan'])
    z = 0.0
    geo.rbox(f'{c.name}.kartu', (0.22, 0.03, 0.3), 0.012, mat(kartu, 0.5), parent=c.j['badan'],
             loc=(0, torso_front(c, 0, z, 0.012) - 0.015, z + 0.02))


def dasi_jas(c, kemeja='#F4F4F4', dasi='#C8333B', kancing='#14161A'):
    """Open jacket look: white shirt V, tie, centre seam and two buttons on the (already dark) torso."""
    w = c.spec.get('lebar', 1.0)
    shirt = mat(kemeja, 0.6, sheen=0.3, bump=0.3)
    y = torso_front(c, 0.12, 0.5, 0.0) - 0.02
    geo.flat_poly(f'{c.name}.kemeja_v', [(-0.3 * w, 1.0), (0.3 * w, 1.0), (0.0, -0.1)], 0.14, shirt,
                  parent=c.j['badan'], loc=(0, y, 0), smooth=False)
    tie = mat(dasi, 0.45, sheen=0.4, bump=0.3)
    yt = y - 0.025
    geo.flat_poly(f'{c.name}.dasi_simpul', [(-0.07, 0.92), (0.07, 0.92), (0.055, 0.78), (-0.055, 0.78)], 0.1, tie,
                  parent=c.j['badan'], loc=(0, yt, 0), smooth=False)
    geo.flat_poly(f'{c.name}.dasi', [(-0.06, 0.8), (0.06, 0.8), (0.12, 0.05), (0.0, -0.12), (-0.12, 0.05)], 0.1, tie,
                  parent=c.j['badan'], loc=(0, yt - 0.01, 0), smooth=False)
    for z in (-0.35, -0.55):
        geo.sphere(f'{c.name}.kancing', 0.05, mat(kancing, 0.3), 12, 8, parent=c.j['badan'],
                   loc=(0.06, torso_front(c, 0.06, z, 0.0) - 0.02, z))


def rompi(c, warna='#E57A2E', pita='#F4F4F4'):
    """Safety vest open at the front, with two reflective bands."""
    torso_patch(c, 'rompi', -0.62, 0.95, 0.035, mat(warna, 0.65, sheen=0.3, bump=0.5), gap_deg=16)
    refl = mat(pita, 0.35, emit=0.25)
    for z0, z1 in ((-0.28, -0.14), (0.28, 0.42)):
        torso_patch(c, 'rompi_pita', z0, z1, 0.045, refl, gap_deg=16, nv=2, tebal=0.02)


def handuk(c, warna='#F4F4F4', garis='#3B6FB5'):
    """Towel round the neck with two ends hanging on the chest."""
    w = c.spec.get('lebar', 1.0)
    m = mat(warna, 0.8, sheen=0.4, bump=0.8, pola=('garis', garis, 22.0))
    z = 0.86
    pts = [(0.66 * w * math.cos(a), 0.5 * w * math.sin(a), z) for a in (2 * math.pi * i / 40 for i in range(40))]
    geo.tube(f'{c.name}.handuk', pts, 0.1, m, closed=True, sides=10, up=(0, 0, 1), parent=c.j['badan'])
    for x, dz in ((-0.2, 0.0), (0.2, -0.12)):
        zc = 0.38 + dz
        geo.rbox(f'{c.name}.handuk_ujung', (0.2, 0.06, 0.85), 0.025, m, parent=c.j['badan'],
                 loc=(x * w, torso_front(c, x * w, zc, 0.0) - 0.03, zc), rot=(0, 0, math.asin(x / 0.62)))


def popok(c, warna='#F8F8F8', perekat='#6FB1E6'):
    """Diaper: a puffy squashed sphere round the hips with two tape tabs."""
    m = mat(warna, 0.7, sheen=0.4, bump=0.4)
    geo.sphere(f'{c.name}.popok', 1, m, 32, 16, parent=c.j['pinggul'], loc=(0, 0, -0.12), scale=(0.74, 0.6, 0.5))
    for sx in (-1, 1):
        geo.rbox(f'{c.name}.perekat', (0.16, 0.04, 0.1), 0.015, mat(perekat, 0.5), parent=c.j['pinggul'],
                 loc=(sx * 0.5, -0.34, 0.12), rot=(0, 0, sx * 0.9))


def noda(c, jumlah=3, warna='#6A6258', seed=0):
    """Grease smears on the shirt (tire repairman): flat diagonal streaks, not round spots."""
    import random
    rng = random.Random(f'{seed}-{c.name}-noda')
    m = mat(warna, 0.95)
    for _ in range(jumlah):
        x, z = rng.uniform(-0.38, 0.38), rng.uniform(-0.3, 0.55)
        geo.sphere(f'{c.name}.noda', 1, m, 12, 8, parent=c.j['badan'], loc=(x, torso_front(c, x, z, 0.0), z),
                   rot=(0, rng.uniform(-0.9, 0.9), 0), scale=(rng.uniform(0.12, 0.22), 0.012, rng.uniform(0.025, 0.045)))


# ---- head gear ---------------------------------------------------------------------------------
def _dome(c, nama, material, z0, tinggi, besar=1.1, tonjol=0.07):
    prof, n = [], 14
    for i in range(n + 1):
        t = i / n
        z = z0 + tinggi * t
        r = (head_r(z) * besar + tonjol * math.sin(math.pi * t)) if i < n else 0.0
        prof.append((r, z))
    return geo.lathe(f'{c.name}.{nama}', prof, material, 56, depth=HEAD_DEPTH, parent=c.head_c)


def topi_pet(c, warna='#6B4F33', balik=False, visor='#17181B', z0=0.74, tinggi=0.72):
    """Peaked cap (police) or a baseball cap worn backwards. No emblem (bible)."""
    m = mat(warna, 0.6, sheen=0.35, bump=0.5)
    _dome(c, 'topi', m, z0, tinggi, besar=1.1, tonjol=0.1)
    _head_loop('topi_pita', c, z0 + 0.03, 1.115, 0.065, mat(darker(warna, 0.7), 0.5), c.head_c)
    geo.sphere(f'{c.name}.topi_kancing', 0.07, m, 12, 8, parent=c.head_c, loc=(0, 0, z0 + tinggi + 0.0))
    ys = 1.0 if balik else -1.0
    geo.sphere(f'{c.name}.topi_visor', 1, mat(visor, 0.3), 32, 10, parent=c.head_c, loc=(0, ys * 0.98, z0 + 0.0),
               rot=(-ys * 0.22, 0, 0), scale=(0.52, 0.42, 0.05))


def helm_proyek(c, warna='#F5C542'):
    """Construction hard hat: dome, all-round brim, longer front peak and a ridge over the top."""
    m = mat(warna, 0.4, sheen=0.1)
    z0 = 0.66
    _dome(c, 'helm', m, z0, 0.62, besar=1.12, tonjol=0.05)
    geo.sphere(f'{c.name}.helm_tepi', 1, m, 40, 10, parent=c.head_c, loc=(0, 0, z0 - 0.02), scale=(1.3, 1.24, 0.07))
    geo.sphere(f'{c.name}.helm_jambul', 1, m, 28, 10, parent=c.head_c, loc=(0, -0.95, z0 - 0.0), rot=(0.12, 0, 0),
               scale=(0.6, 0.55, 0.06))
    ridge = []                                   # arc over the crown, front (-Y) to back (+Y), on the dome surface
    for i in range(15):
        a = math.radians(-82 + 164 * i / 14)
        z = z0 + 0.62 * math.cos(a)
        y = math.copysign(HEAD_DEPTH * (head_r(z) * 1.12 + 0.05), a)
        ridge.append((0, y, z + 0.04))
    geo.tube(f'{c.name}.helm_rusuk', ridge, 0.06, m, sides=8, parent=c.head_c)


def kacamata(c, bentuk='bulat', bingkai='#2B2D42', gelap=False, ukuran=0.34):
    """Round glasses in front of the eyes (dark lenses for sunglasses). Rings follow the face surface."""
    n, fr = c.name, mat(bingkai, 0.35)
    ez = 0.08
    for sx in (-1, 1):
        cx = sx * 0.38
        pts = []
        for a in (2 * math.pi * i / 36 for i in range(36)):
            x, z = cx + ukuran * math.cos(a), ez + ukuran * math.sin(a)
            pts.append((x, front_y(x, z) - 0.19, z))
        geo.tube(f'{n}.kacamata_bingkai', pts, 0.032, fr, closed=True, sides=8, parent=c.head_c)
        if gelap:
            geo.sphere(f'{n}.lensa', 1, mat('#0E1014', 0.08), 24, 12, parent=c.head_c,
                       loc=(cx, front_y(cx, ez) - 0.19, ez), rot=(0, 0, yaw_at(cx, ez)), scale=(ukuran, 0.025, ukuran))
        # temple arm to the ear
        x0 = cx + sx * ukuran
        geo.tube(f'{n}.kacamata_tangkai', [(x0, front_y(x0, ez) - 0.19, ez), (sx * 1.0, -0.35, ez + 0.02), (sx * 1.1, 0.08, ez + 0.03)],
                 0.025, fr, sides=6, parent=c.head_c)
    x = 0.04
    geo.tube(f'{n}.kacamata_jembatan', [(-0.06, front_y(-0.06, ez + 0.05) - 0.19, ez + 0.05), (0, front_y(0, ez + 0.1) - 0.2, ez + 0.1),
                                        (0.06, front_y(0.06, ez + 0.05) - 0.19, ez + 0.05)], 0.028, fr, sides=6, parent=c.head_c)


def kumis(c, warna=None, z=-0.4):
    """Moustache: two thick tubes drooping from the centre."""
    m = mat(warna or c.spec['rambut'], 0.6, sheen=0.3, bump=0.7)
    for sx in (-1, 1):
        pts = []
        for i in range(8):
            t = i / 7
            x = sx * (0.03 + 0.34 * t)
            zz = z - 0.09 * t * t - 0.02
            pts.append((x, front_y(x, zz) - 0.05, zz))
        geo.tube(f'{c.name}.kumis', pts, 0.065, m, sides=8, parent=c.head_c)


def sanggul(c, warna=None, ukuran=0.4):
    """Hair bun on top-back of the head with a pin (grandmother)."""
    m = mat(warna or c.spec['rambut'], 0.6, sheen=0.4, bump=0.7)
    geo.sphere(f'{c.name}.sanggul', ukuran, m, 24, 14, parent=c.head_c, loc=(0, 0.78, 0.82))
    geo.tube(f'{c.name}.tusuk', [(-0.3, 1.0, 0.95), (0.3, 1.05, 0.8)], 0.025, mat('#D9B64A', 0.3), sides=6, parent=c.head_c)


def jambul_bayi(c, warna='#1C1A1A'):
    """A single curl on a baby's head."""
    m = mat(warna, 0.5, sheen=0.3)
    pts = []
    for i in range(14):
        t = i / 13
        a = t * 2.4 * math.pi
        pts.append((0.18 * math.sin(a) * (1 - 0.3 * t), -0.1 + 0.05 * math.cos(a), 1.2 + 0.32 * t + 0.1 * (1 - math.cos(a)) * 0.3))
    geo.tube(f'{c.name}.jambul_bayi', pts, 0.055, m, sides=8, parent=c.head_c)
