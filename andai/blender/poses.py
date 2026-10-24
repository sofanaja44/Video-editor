"""Pose and expression tables (bible 03 §2.3-2.4). Pure data and maths: no bpy, so it can be unit-tested.

Sides are the character's own: `_L` = character's left (+X), `_R` = character's right (-X). It faces -Y.
Limb angles in degrees, forward-positive: bahu=(maju, samping), siku/lutut = flexion, paha = maju,
badan = lean forward, kepala = (tilt toward +X, turn toward +X).
"""
import math

# segment lengths (joint to joint) and ankle-to-sole distance, in scene units; see rig.py for the build
THIGH, SHIN, SOLE = 0.5, 0.5, 0.27

DEFAULT_POSE = dict(pinggul_z=None, badan=0.0, kepala=(0.0, 0.0),
                    bahu_L=(0.0, 8.0), bahu_R=(0.0, 8.0), siku_L=8.0, siku_R=8.0,
                    paha_L=0.0, paha_R=0.0, lutut_L=0.0, lutut_R=0.0)

POSES = {
    'berdiri': {},
    'duduk': dict(paha_L=90, paha_R=90, lutut_L=90, lutut_R=90, badan=4,
                  bahu_L=(28, 6), bahu_R=(28, 6), siku_L=75, siku_R=75),
    'menunjuk': dict(bahu_R=(25, 78), siku_R=0, kepala=(0, -12), badan=-2),
    'angkat_bahu': dict(bahu_L=(8, 38), bahu_R=(8, 38), siku_L=100, siku_R=100, kepala=(9, 0)),
    'pegang': dict(bahu_R=(42, 6), siku_R=78, kepala=(0, -6)),
}


def jalan(phase):
    """Walk cycle, phase 0..1 (0 = passing pose, 0.25 = widest stride)."""
    s, c = math.sin(2 * math.pi * phase), math.cos(2 * math.pi * phase)
    return dict(paha_L=30 * s, paha_R=-30 * s,
                lutut_L=6 + 36 * max(0.0, c), lutut_R=6 + 36 * max(0.0, -c),
                bahu_L=(-24 * s, 8), bahu_R=(24 * s, 8), siku_L=24, siku_R=24, badan=5)


def resolve(pose, phase=0.0):
    """Name or dict -> full joint dict (defaults filled in), plus the hip height that keeps a foot on the floor."""
    p = dict(DEFAULT_POSE)
    if isinstance(pose, str):
        p.update(jalan(phase) if pose == 'jalan' else POSES[pose])
    else:
        p.update(pose)
    if p['pinggul_z'] is None:
        reach = []
        for side in 'LR':
            a, k = math.radians(p['paha_' + side]), math.radians(p['lutut_' + side])
            reach.append(THIGH * math.cos(a) + SHIN * math.cos(a - k))
        p['pinggul_z'] = max(reach) + SOLE
    return p


def lerp_pose(a, b, t):
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        out[k] = tuple(x + (y - x) * t for x, y in zip(va, vb)) if isinstance(va, tuple) else va + (vb - va) * t
    return out


# alis=(sudut, naik): sudut > 0 raises the inner end (sad), < 0 lowers it (sly). alis_L/alis_R override one side.
# mata_senang: laughing eyes drawn as ^ ^ arcs. kelopak >= 0.95 shows closed-eye arcs.
# mulut = (bentuk, lebar). aksesori: names toggled with a scale pop.
EKSPRESI = {
    'netral':        dict(alis=(0, 0.0), mata=1.0, kelopak=0.0, pupil=(0, 0), kilau=1.0, mulut=('garis', 1.0)),
    'senyum':        dict(alis=(0, 0.05), mata=0.9, kelopak=0.2, mulut=('senyum', 1.0)),
    'tawa':          dict(alis=(0, 0.12), mata_senang=True, mulut=('tawa_terbuka', 1.0)),
    'kaget':         dict(alis=(8, 0.22), mata=1.3, mulut=('o', 1.0), aksesori=['kaget_garis']),
    'bengong':       dict(alis=(0, 0.02), mata=1.1, pupil=(0, 0.6), mulut=('o', 0.6)),
    'bingung':       dict(alis_L=(-8, 0.18), alis_R=(10, -0.04), mulut=('gelombang', 1.0)),
    'malu_keringat': dict(alis=(-12, -0.03), mata=0.9, pupil=(0.7, 0), mulut=('gelombang', 1.0),
                          aksesori=['keringat', 'blush']),
    'sedih':         dict(alis=(24, 0.0), kilau=1.9, mulut=('cemberut', 1.0)),
    'licik':         dict(alis=(-20, -0.02), kelopak=0.5, mulut=('seringai', 1.0)),
    'mata_bintang':  dict(alis=(0, 0.1), bintang=True, mulut=('tawa_terbuka', 1.0)),
    'lelah':         dict(alis=(0, -0.03), kelopak=0.6, mulut=('garis_turun', 1.0)),
    'tidur':         dict(alis=(0, 0.0), kelopak=1.0, mulut=('o', 0.6), aksesori=['zzz']),
}
DEFAULT_EXPR = dict(alis=(0, 0.0), alis_L=None, alis_R=None, mata=1.0, kelopak=0.0, pupil=(0, 0), kilau=1.0,
                    bintang=False, mata_senang=False, mulut=('garis', 1.0), aksesori=[])


def resolve_expr(name):
    e = dict(DEFAULT_EXPR)
    e.update(EKSPRESI[name])
    e['alis_L'] = e['alis_L'] or e['alis']
    e['alis_R'] = e['alis_R'] or e['alis']
    return e
