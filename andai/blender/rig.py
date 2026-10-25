"""Character rig from code (bible 03 §2): joints are empties, body parts rigid meshes, face parts small meshes.

Runs inside Blender (bpy). Units: 1u = 1 scene unit, Z up, the character faces -Y, standing height ~4.3u.
Everything that changes over time (pose, expression, blink) goes through `_put`, which either sets the value
(frame=None) or keyframes it with a short ramp, so states must be set in time order.
"""
import math
import os
import random
import bpy
from . import geo, poses
from .materials import mat, darker

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FONT_ZZZ = os.path.join(REPO, 'assets', 'fonts', 'Bangers-Regular.ttf')

# body layout, relative to the parent joint (see poses.py for leg segment lengths)
TORSO_DZ, NECK_DZ, HEAD_DZ = 0.2, 0.85, 0.93        # torso centre / head joint above hip, head centre above head joint
SHOULDER = (0.72, 0.0, 0.82)                         # relative to the torso joint (x mirrored)
UPPER_ARM, FOREARM = 0.5, 0.45
# head "kacang": ellipsoid-ish lathe, cheeks 12% wider at z = -0.35 (relative to the head centre)
HEAD_A, HEAD_B, HEAD_DEPTH = 1.25, 1.05, 0.95
HOME = 1e-4                                          # "hidden" scale: parts pop in and out by scale (bible §2.2)

# hairline heights (front/back/sides, relative to head centre) and outer scale per style
RAMBUT = {
    'cepak':    dict(depan=0.92, belakang=0.30, samping=-0.10, skala=1.05),
    'jambul':   dict(depan=0.92, belakang=0.25, samping=-0.10, skala=1.05),
    'kuncir':   dict(depan=0.90, belakang=0.25, samping=-0.10, skala=1.05),
    'keriting': dict(depan=0.85, belakang=0.10, samping=-0.20, skala=1.10),
    'bob':      dict(depan=0.95, belakang=-0.65, samping=-0.55, skala=1.07),
}


def head_r(z):
    """Head radius at height z (head-centre frame)."""
    t = max(0.0, 1 - (z / HEAD_A) ** 2)
    return HEAD_B * math.sqrt(t) * (1 + 0.12 * math.exp(-(((z + 0.35) / 0.5) ** 2)))


def front_y(x, z):
    """Y of the head's front surface at (x, z); features are glued there."""
    return -HEAD_DEPTH * math.sqrt(max(head_r(z) ** 2 - x * x, 1e-4))


def yaw_at(x, z):
    return math.asin(max(-0.9, min(0.9, x / max(head_r(z), 1e-3))))


def _rad(d):
    return math.radians(d)


class Character:
    def __init__(self, spec, name='kamu', seed=0):
        self.spec, self.name, self.seed = spec, name, seed
        self.j = {}                    # joints
        self.face = {}                 # face parts
        self._expr_log = []            # (frame, resolved expression) in time order, for blinking
        self._keyed = set()            # (object name, property) that already have keyframes
        self.root = geo.empty(name)
        self._build_body()
        self._build_head()
        self._build_face()
        self._build_extra()
        self.pose('berdiri')
        self.expression(spec.get('ekspresi', 'netral'))

    # ---- construction -------------------------------------------------------------------------
    def _build_body(self):
        s, n = self.spec, self.name
        skin_m = mat(s['kulit'], 0.45, sss=0.25)
        self.m = dict(skin=skin_m,        # baju / celana = None means bare skin (baby)
                      shirt=mat(s['baju'], 0.7, sheen=0.3, bump=0.5, pola=s.get('baju_pola')) if s['baju'] else skin_m,
                      pants=mat(s['celana'], 0.75, sheen=0.2, bump=0.5) if s['celana'] else skin_m)
        skin, shirt, pants = self.m['skin'], self.m['shirt'], self.m['pants']
        j, w = self.j, s.get('lebar', 1.0)
        self.root.scale = (s.get('tinggi', 1.0),) * 3
        self.mata_k = s.get('mata_besar', 1.0)
        j['pinggul'] = geo.empty(f'{n}.pinggul', self.root, (0, 0, poses.SOLE + poses.THIGH + poses.SHIN))
        j['badan'] = geo.empty(f'{n}.badan', j['pinggul'])
        geo.capsule(f'{n}.torso', 0.62, 0.7, shirt, parent=j['badan'], loc=(0, 0, TORSO_DZ), scale=(w, 0.8 * w, 1))
        j['kepala'] = geo.empty(f'{n}.kepala', j['badan'], (0, 0, NECK_DZ))
        k = s.get('kepala_skala', 1.0)
        self.head_c = geo.empty(f'{n}.kepala_pusat', j['kepala'], (0, 0, HEAD_DZ + 0.9 * (k - 1)))
        self.head_c.scale = (k, k, k)
        lengan = s.get('lengan', 'pendek')
        sleeve = shirt if lengan == 'panjang' else skin                 # forearm
        upper = skin if lengan == 'tanpa' else shirt                    # upper arm
        for side, sx in (('L', 1), ('R', -1)):
            j['bahu_' + side] = b = geo.empty(f'{n}.bahu_{side}', j['badan'], (sx * (SHOULDER[0] + 0.62 * (w - 1)), 0, SHOULDER[2]))
            geo.capsule(f'{n}.lengan_atas_{side}', 0.15, UPPER_ARM, upper, parent=b, loc=(0, 0, -UPPER_ARM / 2))
            j['siku_' + side] = e = geo.empty(f'{n}.siku_{side}', b, (0, 0, -UPPER_ARM))
            geo.capsule(f'{n}.lengan_bawah_{side}', 0.15, FOREARM, sleeve, parent=e, loc=(0, 0, -FOREARM / 2))
            j['tangan_' + side] = h = geo.empty(f'{n}.tangan_{side}', e, (0, 0, -FOREARM))   # prop socket
            geo.sphere(f'{n}.telapak_{side}', 0.2, skin, parent=h, loc=(0, 0, -0.1))
            geo.sphere(f'{n}.jempol_{side}', 1, skin, 12, 8, parent=h, loc=(-sx * 0.15, -0.1, -0.06),
                       rot=(0, -sx * 0.5, 0), scale=(0.075, 0.115, 0.075))                    # mitten thumb
            j['paha_' + side] = p = geo.empty(f'{n}.paha_{side}', j['pinggul'], (sx * 0.28, 0, 0))
            geo.capsule(f'{n}.paha_{side}', 0.17, poses.THIGH, pants, parent=p, loc=(0, 0, -poses.THIGH / 2))
            j['lutut_' + side] = kn = geo.empty(f'{n}.lutut_{side}', p, (0, 0, -poses.THIGH))
            geo.capsule(f'{n}.betis_{side}', 0.17, poses.SHIN, pants, parent=kn, loc=(0, 0, -poses.SHIN / 2))
            j['kaki_' + side] = a = geo.empty(f'{n}.kaki_{side}', kn, (0, 0, -poses.SHIN))      # ankle
            self._shoe(a, side)

    def _build_extra(self):
        """Costume pieces from spec['ekstra'] = [(builder name in kostum.py, kwargs), ...]."""
        if self.spec.get('ekstra'):
            from . import kostum
            for nama, kw in self.spec['ekstra']:
                getattr(kostum, nama)(self, **kw)

    def _shoe(self, ankle, side):
        """Footwear (bible: no sharp edges). `sandal` = bare foot on a flat sole with a Y strap (jepit),
        `sepatu` = rounded shoe with a light sole, `bot` = shoe + shaft, `tanpa` = bare foot."""
        s, n = self.spec, self.name
        jenis, col = s.get('alas_jenis', 'sandal'), s['alas']
        floor = -poses.SOLE
        half = [(0, 0), (1, 0)] + [(math.cos(t), math.sin(t)) for t in (math.pi / 2 * i / 10 for i in range(1, 11))]
        foot = (0.19, 0.34, 0.12)                                          # ellipsoid radii
        fc = (0, -0.08, floor + 0.10)

        def bare_foot():
            geo.sphere(f'{n}.kaki_telanjang_{side}', 1, self.m['skin'], 20, 12, parent=ankle, loc=fc, scale=foot)

        if jenis in ('sandal', 'tanpa'):
            bare_foot()
        if jenis == 'sandal':
            geo.lathe(f'{n}.sol_{side}', half, mat(col, 0.7), 32, parent=ankle, loc=(0, -0.08, floor), scale=(0.27, 0.4, 0.07))
            strap = mat(darker(col, 0.7), 0.6)
            for sx in (-1, 1):
                pts = []
                for t in range(7):
                    u = t / 6
                    x, y = sx * 0.19 * u ** 0.8, -0.33 + 0.29 * u
                    zz = fc[2] + foot[2] * math.sqrt(max(0.0, 1 - (x / foot[0]) ** 2 - ((y - fc[1]) / foot[1]) ** 2)) + 0.025
                    pts.append((x, y, zz))
                geo.tube(f'{n}.tali_{side}', pts, 0.032, strap, sides=8, parent=ankle, up=(0, 0, 1))
        elif jenis in ('sepatu', 'bot'):
            geo.lathe(f'{n}.sepatu_{side}', half, mat(col, 0.55, sheen=0.1), 32, parent=ankle, loc=(0, -0.1, floor + 0.03),
                      scale=(0.27, 0.42, 0.24))
            geo.sphere(f'{n}.sol_{side}', 1, mat('#ECE9E2', 0.7), 24, 10, parent=ankle, loc=(0, -0.1, floor + 0.035),
                       scale=(0.285, 0.44, 0.045))
            if jenis == 'bot':
                geo.capsule(f'{n}.betis_bot_{side}', 0.2, 0.2, mat(col, 0.55), parent=ankle, loc=(0, 0.0, 0.02))

    def _build_head(self):
        s, n = self.spec, self.name
        prof = []
        for i in range(49):
            ph = math.pi * i / 48
            z = -HEAD_A * math.cos(ph)
            prof.append((head_r(z) if 0 < i < 48 else 0.0, z))
        geo.lathe(f'{n}.kepala_mesh', prof, mat(s['kulit'], 0.45), 64, depth=HEAD_DEPTH, parent=self.head_c)
        skin = self.m['skin']
        inner = mat(darker(s['kulit'], 0.82), 0.5, sss=0.2)
        for sx in (1, -1):                                   # ears: flattened ellipsoid + darker inner
            geo.sphere(f'{n}.telinga', 1, skin, 16, 10, parent=self.head_c, loc=(sx * 1.1, 0.1, -0.02),
                       rot=(0, 0, sx * 0.3), scale=(0.1, 0.17, 0.25))
            geo.sphere(f'{n}.telinga_dalam', 1, inner, 12, 8, parent=self.head_c, loc=(sx * 1.14, 0.06, -0.02),
                       rot=(0, 0, sx * 0.3), scale=(0.05, 0.1, 0.16))
        hid = s.get('hidung', 1.0)
        if hid:                                              # small soft nose bump
            geo.sphere(f'{n}.hidung', 1, skin, 16, 10, parent=self.head_c,
                       loc=(0, front_y(0, -0.27) - 0.03, -0.27), scale=(0.115 * hid, 0.1 * hid, 0.095 * hid))
        style = s.get('gaya_rambut', 'cepak')
        if style in RAMBUT:
            self._hair(style, mat(s['rambut'], 0.6, sheen=0.35, bump=0.7))

    def _hair(self, style, material):
        p, n = RAMBUT[style], self.name
        S, N, A = 64, 18, HEAD_A
        verts, faces, cols = [], [], []
        for jx in range(S):
            th = 2 * math.pi * jx / S
            f = (1 - math.sin(th)) / 2                          # 1 at the front (-Y), 0 at the back
            z_edge = p['belakang'] + (p['depan'] - p['belakang']) * f ** 1.4 + p['samping'] * (1 - f) * abs(math.cos(th))
            ph0 = math.acos(max(-1.0, min(1.0, -z_edge / A)))
            col = []
            for i in range(N):
                ph = ph0 + (math.pi - ph0) * i / N
                z = -A * math.cos(ph)
                r = head_r(z) * p['skala']
                verts.append((r * math.cos(th), HEAD_DEPTH * r * math.sin(th), z + 0.02)); col.append(len(verts) - 1)
            cols.append(col)
        verts.append((0, 0, A + 0.03)); pole = len(verts) - 1
        for jx in range(S):
            a, b = cols[jx], cols[(jx + 1) % S]
            faces += [(a[i], b[i], b[i + 1], a[i + 1]) for i in range(N - 1)] + [(a[N - 1], b[N - 1], pole)]
        hair = geo.mesh_obj(f'{n}.rambut', verts, faces, material, parent=self.head_c)
        md = hair.modifiers.new('tebal', 'SOLIDIFY'); md.thickness = 0.05; md.offset = 0
        rng = random.Random(f'{self.seed}-{n}-rambut')
        if style == 'jambul':
            cone = [(0, -0.05), (0.2, 0), (0.17, 0.12), (0.11, 0.28), (0.05, 0.4), (0, 0.46)]
            for dx, ry in ((-0.25, -0.5), (0.05, -0.1), (0.32, 0.4)):
                geo.lathe(f'{n}.jambul', cone, material, 20, parent=self.head_c, loc=(dx, 0.1, 1.2), rot=(0.5, ry, 0))
        elif style == 'kuncir':
            geo.sphere(f'{n}.ikat', 0.2, mat('#C8333B', 0.6), parent=self.head_c, loc=(0, 0.98, 0.5))
            geo.capsule(f'{n}.kuncir', 0.22, 0.55, material, parent=self.head_c, loc=(0, 1.3, 0.2), rot=(-2.4, 0, 0))
        elif style == 'keriting':
            for _ in range(46):
                th, z = rng.uniform(0, 2 * math.pi), rng.uniform(0.2, 1.15)
                if math.sin(th) < -0.6 and z < 0.75:
                    continue                                    # keep the face clear
                r = head_r(z) * 1.1
                geo.sphere(f'{n}.keriting', rng.uniform(0.16, 0.24), material, 12, 8, parent=self.head_c,
                           loc=(r * math.cos(th), HEAD_DEPTH * r * math.sin(th), z))

    def _build_face(self):
        n, F, s = self.name, self.face, self.spec
        dark = mat('#2A2020', 0.5)
        F['eye'], F['alis'], F['bintang'], F['kilau'], F['arc'] = {}, {}, {}, [], {}
        for side, sx in (('L', 1), ('R', -1)):
            x = sx * 0.38
            # eye: white ellipsoid + pupil + highlight, all squashed together by the eyelid (scale Z)
            ez = 0.08
            e = geo.empty(f'{n}.mata_{side}', self.head_c, (x, front_y(x, ez), ez), (0, 0, yaw_at(x, ez)))
            geo.sphere(f'{n}.mata_putih_{side}', 1, mat('#FFFFFF', 0.2), 20, 12, parent=e, scale=(0.25, 0.12, 0.29))
            pu = geo.empty(f'{n}.pupil_{side}', e, (0, -0.10, 0))
            geo.sphere(f'{n}.pupil_mesh_{side}', 1, mat('#141414', 0.15), 16, 10, parent=pu, scale=(0.11, 0.05, 0.11))
            ki = geo.sphere(f'{n}.kilau_{side}', 0.035, mat('#FFFFFF', 0.1, emit=1.0), 10, 6, parent=pu, loc=(-0.035, -0.05, 0.045))
            if s.get('bulu_mata'):                           # three lashes at the outer corner (squash with the lid)
                for li in range(3):
                    geo.tube(f'{n}.bulu_mata_{side}', [(sx * 0.2, -0.11, 0.1 + 0.03 * li),
                                                      (sx * (0.3 + 0.03 * li), -0.12, 0.17 + 0.07 * li),
                                                      (sx * (0.37 + 0.04 * li), -0.12, 0.2 + 0.1 * li)],
                             0.02, dark, sides=6, cap_rings=2, parent=e)
            F['eye'][side] = (e, pu)
            F['kilau'].append(ki)
            # eyebrow: capsule lying along X on the forehead
            bz = 0.52
            b = geo.empty(f'{n}.alis_{side}', self.head_c, (x, front_y(x, bz), bz), (0, 0, yaw_at(x, bz)))
            geo.capsule(f'{n}.alis_mesh_{side}', 0.05, 0.18, dark, 16, 5, parent=b, rot=(0, math.pi / 2, 0))
            F['alis'][side] = b
            st = geo.star(f'{n}.bintang_{side}', 0.3, 0.14, 0.12, mat('#FFC400', 0.4, emit=0.6),
                          parent=self.head_c, loc=(x, front_y(x, ez) - 0.05, ez))
            F['bintang'][side] = st
            # closed ('tutup') and laughing ('senang') eye lines, popped in by scale like the other face parts
            ae = geo.empty(f'{n}.kelopak_{side}', self.head_c, (x, front_y(x, ez), ez), (0, 0, yaw_at(x, ez)))
            F['arc'][side] = {}
            for key, fn, y in (('tutup', lambda t: 0.04 * t * t - 0.02, -0.10), ('senang', lambda t: -0.15 * t * t + 0.07, -0.06)):
                pts = [(0.27 * t, y, fn(t)) for t in (i / 6 - 1 for i in range(13))]
                F['arc'][side][key] = geo.tube(f'{n}.garis_mata_{key}_{side}', pts, 0.045, dark, parent=ae, scale=(HOME,) * 3)
        self._build_mouths()
        self._build_accessories()

    def _build_mouths(self):
        n, F = self.name, self.face
        z0 = -0.52
        y0 = front_y(0, z0)
        F['mulut'] = geo.empty(f'{n}.mulut', self.head_c, (0, y0, z0))
        lip = mat('#5A1F1F', 0.4)

        def on_surface(curve, xs):
            return [(x, front_y(x, z0 + curve(x)) - y0 - 0.01, curve(x)) for x in xs]

        def xs(w, k=15):
            return [w * (2 * i / (k - 1) - 1) for i in range(k)]

        shapes = {
            'garis': lambda x: 0.0,
            'senyum': lambda x: 0.17 * (x / 0.3) ** 2 - 0.02,
            'cemberut': lambda x: -0.15 * (x / 0.3) ** 2 + 0.02,
            'garis_turun': lambda x: -0.05 * (x / 0.3) ** 2,
            'gelombang': lambda x: 0.05 * math.sin(x * 22),
            'seringai': lambda x: 0.2 * ((x + 0.3) / 0.6) ** 2 - 0.05,
        }
        F['mulut_mesh'] = {}
        for key, fn in shapes.items():
            w = 0.22 if key == 'garis' else 0.3
            F['mulut_mesh'][key] = geo.tube(f'{n}.mulut_{key}', on_surface(fn, xs(w)), 0.045, lip, parent=F['mulut'])
        for key, r in (('o', 0.12), ('o_kecil', 0.075)):
            ring = [(r * math.cos(a), front_y(r * math.cos(a), z0 + r * math.sin(a)) - y0 - 0.01, r * math.sin(a))
                    for a in (2 * math.pi * i / 20 for i in range(20))]
            F['mulut_mesh'][key] = geo.tube(f'{n}.mulut_{key}', ring, 0.04, lip, closed=True, parent=F['mulut'])
        # open laugh: dark half-ellipse + tongue
        pts = [(0.3 * math.cos(math.pi * i / 12), -0.3 * math.sin(math.pi * i / 12)) for i in range(13)]
        laugh = geo.empty(f'{n}.mulut_tawa_terbuka', F['mulut'])
        geo.flat_poly(f'{n}.tawa_dalam', pts, 0.12, mat('#3A1010', 0.5), parent=laugh, loc=(0, -0.03, 0.08), smooth=False)
        geo.sphere(f'{n}.lidah', 1, mat('#E8707A', 0.5), 12, 8, parent=laugh, loc=(0, -0.05, -0.2), scale=(0.15, 0.04, 0.09))
        F['mulut_mesh']['tawa_terbuka'] = laugh

    def _build_accessories(self):
        n, F = self.name, self.face
        acc = F['aksesori'] = {}
        # sweat drop
        drop = [(0, -0.12)] + [(0.1 * math.sin(math.pi * i / 8), -0.02 - 0.1 * math.cos(math.pi * i / 8)) for i in range(1, 8)]
        drop += [(0.07, 0.04), (0.04, 0.14), (0, 0.24)]
        g = geo.empty(f'{n}.keringat', self.head_c, (0.95, -0.55, 0.5))
        geo.lathe(f'{n}.tetes', drop, mat('#8FD3FF', 0.2, emit=0.25), 16, parent=g, scale=(1.3,) * 3)
        acc['keringat'] = g
        # blush discs on the cheeks
        g = geo.empty(f'{n}.blush', self.head_c)
        for sx in (1, -1):
            x, z = sx * 0.66, -0.2
            geo.sphere(f'{n}.pipi', 1, mat('#FF8FA3', 0.6, alpha=0.6), 16, 8, parent=g,
                       loc=(x, front_y(x, z) - 0.0, z), rot=(0, 0, yaw_at(x, z)), scale=(0.2, 0.03, 0.13))
        acc['blush'] = g
        # shock lines above the head
        g = geo.empty(f'{n}.kaget_garis', self.head_c, (0, -0.25, 1.5))
        ink = mat('#2B2D42', 0.5)
        for ang in (-38, 0, 38):
            a = math.radians(ang)
            geo.capsule(f'{n}.garis_kejut', 0.035, 0.2, ink, 10, 4, parent=g, loc=(0.35 * math.sin(a), 0, 0.3 * math.cos(a)),
                        rot=(0, a, 0))
        acc['kaget_garis'] = g
        # zzz
        g = geo.empty(f'{n}.zzz', self.head_c, (1.0, -0.45, 1.25))
        font = bpy.data.fonts.load(FONT_ZZZ) if os.path.exists(FONT_ZZZ) else None
        for i, (sz, dx, dz) in enumerate(((0.38, 0, 0), (0.28, 0.34, 0.34), (0.2, 0.6, 0.62))):
            cu = bpy.data.curves.new(f'{n}.zzz{i}', 'FONT')
            cu.body, cu.size, cu.extrude, cu.align_x = 'Z', sz, 0.03, 'CENTER'
            if font:
                cu.font = font
            cu.materials.append(mat('#FFFFFF', 0.4, emit=0.6))
            ob = bpy.data.objects.new(f'{n}.zzz{i}', cu)
            geo._link(ob, g, (dx, 0, dz), (math.pi / 2, 0, 0))
        acc['zzz'] = g

    # ---- state setting ------------------------------------------------------------------------
    def _put(self, obj, attr, value, frame, ramp):
        value = tuple(value) if isinstance(value, (tuple, list)) else value
        cur = getattr(obj, attr)
        same = all(abs(a - b) < 1e-6 for a, b in zip(tuple(cur), value)) if isinstance(value, tuple) else abs(cur - value) < 1e-6
        first = (obj.name, attr) not in self._keyed
        if frame is None:
            setattr(obj, attr, value)
        elif not same:
            if ramp > 0:
                obj.keyframe_insert(attr, frame=frame - ramp)
            setattr(obj, attr, value)
            obj.keyframe_insert(attr, frame=frame)
            self._keyed.add((obj.name, attr))
        elif first:      # unchanged but never keyed: pin it, or later keys would extrapolate backwards
            obj.keyframe_insert(attr, frame=frame)
            self._keyed.add((obj.name, attr))

    def place(self, x=0.0, y=0.0, yaw=0.0, frame=None, ramp=0):
        """Move the whole character; yaw in degrees, positive turns the face toward +X."""
        self._put(self.root, 'location', (x, y, 0), frame, ramp)
        self._put(self.root, 'rotation_euler', (0, 0, _rad(yaw)), frame, ramp)

    def pose(self, pose='berdiri', phase=0.0, frame=None, ramp=6):
        p, j, put = poses.resolve(pose, phase), self.j, self._put
        p['badan'] += self.spec.get('bungkuk', 0.0)      # permanent stoop (grandmother)
        put(j['pinggul'], 'location', (0, 0, p['pinggul_z']), frame, ramp)
        put(j['badan'], 'rotation_euler', (-_rad(p['badan']), 0, 0), frame, ramp)
        tilt, turn = p['kepala']
        put(j['kepala'], 'rotation_euler', (0, _rad(tilt), _rad(turn)), frame, ramp)
        for side, sx in (('L', 1), ('R', -1)):
            maju, samping = p['bahu_' + side]
            put(j['bahu_' + side], 'rotation_euler', (-_rad(maju), -sx * _rad(samping), 0), frame, ramp)
            put(j['siku_' + side], 'rotation_euler', (-_rad(p['siku_' + side]), 0, 0), frame, ramp)
            a, k = p['paha_' + side], p['lutut_' + side]
            put(j['paha_' + side], 'rotation_euler', (-_rad(a), 0, 0), frame, ramp)
            put(j['lutut_' + side], 'rotation_euler', (_rad(k), 0, 0), frame, ramp)
            put(j['kaki_' + side], 'rotation_euler', (_rad(a - k), 0, 0), frame, ramp)   # keeps the sole flat

    def expression(self, name, frame=None, ramp=3):
        e, F, put = poses.resolve_expr(name), self.face, self._put
        for side, sx in (('L', 1), ('R', -1)):
            sudut, naik = e['alis_' + side]
            b = F['alis'][side]
            put(b, 'location', (b.location.x, b.location.y, 0.52 + naik), frame, ramp)
            put(b, 'rotation_euler', (0, sx * _rad(sudut), b.rotation_euler.z), frame, ramp)
            eye, pupil = F['eye'][side]
            closed = e['kelopak'] >= 0.95
            s = e['mata'] * self.mata_k * (0 if e['bintang'] or e['mata_senang'] else 1) or HOME
            put(eye, 'scale', (s, s, self._lid_z(s, e['kelopak'])), frame, ramp)
            for key, on in (('tutup', closed and not e['mata_senang']), ('senang', e['mata_senang'])):
                put(F['arc'][side][key], 'scale', (1, 1, 1) if on else (HOME,) * 3, frame, ramp)
            put(pupil, 'location', (0.11 * e['pupil'][0], -0.10, 0.13 * e['pupil'][1]), frame, ramp)
            bs = 1.0 if e['bintang'] else HOME
            put(F['bintang'][side], 'scale', (bs, bs, bs), frame, ramp)
        for ki in F['kilau']:
            put(ki, 'scale', (e['kilau'],) * 3, frame, ramp)
        shape, width = e['mulut']
        for key, ob in F['mulut_mesh'].items():
            on = key == shape
            put(ob, 'scale', (1, 1, 1) if on else (HOME,) * 3, frame, ramp)
        put(F['mulut'], 'scale', (width, 1, 1), frame, ramp)
        for key, g in F['aksesori'].items():
            put(g, 'scale', (1, 1, 1) if key in e['aksesori'] else (HOME,) * 3, frame, ramp)
        self._expr_log.append((frame if frame is not None else -10 ** 9, e))

    @staticmethod
    def _lid_z(s, lid):
        """Eye height scale for eyelid closure 0..1 (fully closed: a hairline, hidden behind the lid arc)."""
        return max(s * 0.02, HOME) if lid >= 0.95 else max(s * (1 - 0.9 * lid), HOME)

    def blink(self, frames, fps=30, seed=None):
        """Automatic blink every 2.5-4 s, 4 frames long, random per character (call after the expressions)."""
        rng = random.Random(f'{self.seed}-{self.name}-kedip' if seed is None else seed)
        change = [f for f, _ in self._expr_log]
        t = rng.uniform(1.0, 2.5) * fps
        while t < frames - 4:
            f = int(t)
            e = [x for fr, x in self._expr_log if fr <= f][-1]
            busy = any(f - 8 <= c <= f + 4 for c in change if c > -10 ** 8)
            if e['kelopak'] < 0.9 and not e['bintang'] and not busy:
                for side, (eye, _) in self.face['eye'].items():
                    s, arc = e['mata'] * self.mata_k, self.face['arc'][side]['tutup']
                    for fr, lid in ((f, e['kelopak']), (f + 1, 1.0), (f + 2, 1.0), (f + 3, e['kelopak'])):
                        eye.scale = (s, s, self._lid_z(s, lid))
                        eye.keyframe_insert('scale', frame=fr)
                        arc.scale = (1, 1, 1) if lid >= 0.95 else (HOME,) * 3
                        arc.keyframe_insert('scale', frame=fr)
            t += rng.uniform(2.5, 4.0) * fps

    def walk(self, frame0, frame1, cycle=8, step=2, ramp_in=6):
        """Key a walk cycle (`cycle` frames per full loop, one key every `step` frames). The first key blends
        in from the previous pose over `ramp_in` frames."""
        for f in range(frame0, frame1 + 1, step):
            self.pose('jalan', phase=((f - frame0) / cycle) % 1.0, frame=f, ramp=ramp_in if f == frame0 else 0)
