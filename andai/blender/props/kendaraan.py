"""Vehicles in toy scale (a rider is ~4.3u tall): motorbike, hatchback, minibus (angkot), bus.
Front = -Y, wheels roll about X. Sockets: motor has `dudukan`, `setang_L/R`, `pijakan_L/R`, `knalpot`."""
import math
from .. import geo
from ..materials import mat, darker
from . import Prop, daftar

BAN = '#1B1B1F'
LOGAM = '#C9CDD3'
KACA = '#1E2530'


def _roda(p, x, y, R, tebal=0.2, ban=BAN, pelek=LOGAM):
    """Tyre = closed tube ring in the YZ plane, rim = flattened disc, hub cap in the middle."""
    n = p.nama
    pts = [(x, y + R * math.cos(a), R + R * math.sin(a)) for a in (2 * math.pi * i / 28 for i in range(28))]
    geo.tube(f'{n}.ban', pts, tebal, mat(ban, 0.85), closed=True, sides=10, up=(1, 0, 0), parent=p.root)
    geo.sphere(f'{n}.pelek', 1, mat(pelek, 0.35), 24, 12, parent=p.root, loc=(x, y, R), scale=(0.06, R * 0.72, R * 0.72))
    geo.sphere(f'{n}.tutup_roda', 1, mat(darker(pelek, 0.7), 0.4), 12, 8, parent=p.root, loc=(x + math.copysign(0.07, x) if x else 0.07, y, R),
               scale=(0.05, R * 0.28, R * 0.28))


@daftar('motor')
def motor(warna='#C8333B'):
    """Underbone motorbike (bebek): seat top 1.5u, footrests 1.1u, handlebar 2.5u (see poses.MOTOR_PINGGUL_Z)."""
    p = Prop('motor'); n = p.nama; r = p.root
    body, hitam, logam = mat(warna, 0.4, sheen=0.1), mat('#1D1D20', 0.6, sheen=0.2), mat(LOGAM, 0.3)
    R = 0.8
    _roda(p, 0, -1.6, R); _roda(p, 0, 1.6, R)
    for yc, a0, a1 in ((-1.6, 25, 160), (1.6, 20, 150)):         # mudguards over each wheel
        pts = [(0, yc + (R + 0.16) * math.cos(math.radians(a)), R + (R + 0.16) * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 10)]
        geo.tube(f'{n}.sepatbor', pts, 0.1, body, sides=8, up=(1, 0, 0), parent=r)
    geo.rbox(f'{n}.penutup', (0.72, 1.7, 0.75), 0.2, body, parent=r, loc=(0, 0.1, 1.05))
    geo.rbox(f'{n}.jok', (0.68, 1.55, 0.3), 0.12, hitam, parent=r, loc=(0, 0.65, 1.35))
    geo.rbox(f'{n}.ekor', (0.64, 1.0, 0.42), 0.16, body, parent=r, loc=(0, 1.75, 1.25))
    geo.rbox(f'{n}.lampu_belakang', (0.34, 0.08, 0.16), 0.03, mat('#FF2A2A', 0.3, emit=1.5), parent=r, loc=(0, 2.27, 1.3))
    geo.rbox(f'{n}.mesin', (0.56, 0.95, 0.55), 0.14, mat('#4A4D55', 0.5), parent=r, loc=(0, 0.15, 0.62))
    geo.rbox(f'{n}.perisai', (0.82, 0.22, 1.25), 0.1, body, parent=r, loc=(0, -0.85, 1.45), rot=(-0.28, 0, 0))
    geo.tube(f'{n}.garpu', [(0, -1.6, R), (0, -1.1, 1.65), (0, -0.7, 2.4)], 0.07, logam, sides=8, parent=r)
    geo.tube(f'{n}.setang', [(-0.66, -0.62, 2.5), (0, -0.7, 2.5), (0.66, -0.62, 2.5)], 0.055, hitam, sides=8, parent=r)
    for sx in (-1, 1):
        geo.sphere(f'{n}.genggam', 0.09, hitam, 10, 8, parent=r, loc=(sx * 0.66, -0.6, 2.5))
        geo.rbox(f'{n}.pijakan', (0.26, 0.36, 0.06), 0.02, logam, parent=r, loc=(sx * 0.5, -0.02, 1.08))
    geo.sphere(f'{n}.lampu_depan', 1, mat('#FFF6D8', 0.2, emit=2.0), 20, 12, parent=r, loc=(0, -1.0, 2.2), scale=(0.3, 0.2, 0.27))
    geo.tube(f'{n}.knalpot', [(0.3, -0.2, 0.55), (0.34, 1.2, 0.5), (0.34, 2.1, 0.68)], 0.1, logam, sides=8, parent=r)
    p.socket('dudukan', (0, 0.35, 1.5)); p.socket('setang_L', (0.66, -0.6, 2.5)); p.socket('setang_R', (-0.66, -0.6, 2.5))
    p.socket('pijakan_L', (0.5, -0.02, 1.1)); p.socket('pijakan_R', (-0.5, -0.02, 1.1)); p.socket('knalpot', (0.34, 2.2, 0.68))
    return p


def _badan_kotak(p, panjang, lebar, tinggi_bawah, tinggi_kabin, warna, kab_len, kab_y, R, jendela='#1E2530', jalur=None):
    """Shared box body: lower body + cabin + window band + lights."""
    n, r = p.nama, p.root
    body = mat(warna, 0.4, sheen=0.1)
    z0 = R + 0.1
    geo.rbox(f'{n}.badan', (lebar, panjang, tinggi_bawah), 0.45, body, parent=r, loc=(0, 0, z0 + tinggi_bawah / 2))
    zc = z0 + tinggi_bawah + tinggi_kabin / 2 - 0.15
    geo.rbox(f'{n}.kabin', (lebar * 0.86, kab_len, tinggi_kabin), 0.4, body, parent=r, loc=(0, kab_y, zc))
    geo.rbox(f'{n}.kaca', (lebar * 0.86 + 0.06, kab_len - 0.9, tinggi_kabin * 0.62), 0.12, mat(jendela, 0.08), parent=r,
             loc=(0, kab_y, zc + tinggi_kabin * 0.05))
    geo.rbox(f'{n}.kaca_depan', (lebar * 0.7, kab_len + 0.08, tinggi_kabin * 0.55), 0.12, mat(jendela, 0.08), parent=r,
             loc=(0, kab_y, zc + tinggi_kabin * 0.05))
    if jalur:
        geo.rbox(f'{n}.jalur', (lebar + 0.05, panjang * 0.98, tinggi_bawah * 0.22), 0.05, mat(jalur, 0.5), parent=r,
                 loc=(0, 0, z0 + tinggi_bawah * 0.5))
    for sx in (-1, 1):
        geo.sphere(f'{n}.lampu_depan', 1, mat('#FFF6D8', 0.2, emit=1.8), 16, 10, parent=r,
                   loc=(sx * lebar * 0.32, -panjang / 2 - 0.02, z0 + tinggi_bawah * 0.62), scale=(0.34, 0.12, 0.2))
        geo.sphere(f'{n}.lampu_belakang', 1, mat('#FF2A2A', 0.3, emit=1.4), 16, 10, parent=r,
                   loc=(sx * lebar * 0.34, panjang / 2 + 0.02, z0 + tinggi_bawah * 0.62), scale=(0.3, 0.1, 0.18))
    geo.rbox(f'{n}.bumper_depan', (lebar * 0.98, 0.34, 0.42), 0.14, mat('#2A2C31', 0.5), parent=r, loc=(0, -panjang / 2 - 0.05, z0 + 0.35))
    geo.rbox(f'{n}.bumper_belakang', (lebar * 0.98, 0.34, 0.42), 0.14, mat('#2A2C31', 0.5), parent=r, loc=(0, panjang / 2 + 0.05, z0 + 0.35))


@daftar('mobil')
def mobil(warna='#5B8DEF'):
    """Toy hatchback, 7u long."""
    p = Prop('mobil'); R = 0.7
    _badan_kotak(p, 7.0, 3.2, 1.3, 1.25, warna, 3.9, 0.6, R)
    for sx in (-1, 1):
        for y in (-2.25, 2.25):
            _roda(p, sx * 1.6, y, R, 0.24)
    return p


@daftar('angkot')
def angkot(warna='#3FA34D', jalur='#F4F4F4', kosong=False):
    """Boxy minibus with a light stripe (public minivan)."""
    p = Prop('angkot'); R = 0.8
    _badan_kotak(p, 9.6, 3.5, 1.8, 1.7, warna, 8.0, 0.2, R, jalur=jalur)
    for sx in (-1, 1):
        for y in (-3.1, 3.1):
            _roda(p, sx * 1.72, y, R, 0.26)
    return p


@daftar('bus')
def bus(warna='#2F6FBE', jalur='#F4F4F4'):
    """Long city bus, 16u."""
    p = Prop('bus'); R = 0.95
    _badan_kotak(p, 16.0, 3.7, 2.4, 2.0, warna, 14.4, 0.0, R, jalur=jalur)
    for sx in (-1, 1):
        for y in (-5.4, 4.6, 6.4):
            _roda(p, sx * 1.8, y, R, 0.3)
    return p
