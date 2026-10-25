"""Set `jalan_raya`: four-lane city road along X with a crossing street at x = 45, sidewalks, building rows,
trees, street lamps and a zebra crossing. Traffic that drives toward +X uses the far lanes (left-hand traffic).
Named points: lajur_kiri (far outer lane, +X), lajur_kanan (far inner lane, +X), lajur_lawan_1/2 (near lanes, -X),
simpang, trotoar, pulau_jalan, tiang (traffic-light corner)."""
import math
from .. import geo
from ..materials import mat, fasad, darker
from . import daftar, Set

PAL = {
    'andai': dict(aspal='#6A6F78', garis='#F6F3E8', kuning='#F2C94C', trotoar='#D8D0C0', tanah='#9ECF8B',
                  gedung=['#F2B7C6', '#A9D6C1', '#F6D48B', '#B9C8F2', '#F7C6A3', '#CDE7B0'], jendela='#BFE3FF',
                  atap='#C4553F', daun='#5CC27A', batang='#8B6B4A'),
    'nyata': dict(aspal='#4B5058', garis='#CFCFCA', kuning='#BFA650', trotoar='#8F8F89', tanah='#7C8A74',
                  gedung=['#8A9099', '#7C8794', '#9AA0A8', '#6E7A86', '#A39E96'], jendela='#9FB4C8',
                  atap='#5E6E80', daun='#5F7A5C', batang='#5A4A3A'),
}
PAL['netral'] = PAL['andai']
SIMPANG_X, JALAN_W = 45.0, 24.0


def _celah(x0, x1, a=SIMPANG_X - 14, b=SIMPANG_X + 14):
    """Split [x0, x1] around the crossing street, giving the pieces that remain."""
    out = []
    if x0 < a:
        out.append((x0, min(x1, a)))
    if x1 > b:
        out.append((max(x0, b), x1))
    return out


@daftar('jalan_raya')
def jalan_raya(ctx):
    s = Set('jalan_raya'); p = PAL[ctx.dunia]; rng = ctx.rng; X0, X1 = -220.0, 220.0
    # ground, road, crossing street
    geo.rbox('tanah', (700, 700, 0.3), 0.05, mat(p['tanah'], 0.95), loc=(0, 0, -0.45))
    aspal = mat(p['aspal'], 0.9, bump=0.4)
    geo.rbox('jalan', (X1 - X0, JALAN_W, 0.26), 0.06, aspal, loc=((X0 + X1) / 2, 0, -0.13))
    geo.rbox('jalan_silang', (JALAN_W, 460, 0.26), 0.06, aspal, loc=(SIMPANG_X, 0, -0.125))
    garis, kuning = mat(p['garis'], 0.6), mat(p['kuning'], 0.6)
    for a, b in _celah(X0, X1):                                     # centre double line + edge lines
        for y in (-0.22, 0.22):
            geo.rbox('marka_tengah', (b - a, 0.16, 0.03), 0.01, kuning, loc=((a + b) / 2, y, 0.012))
        for y in (-11.5, 11.5):
            geo.rbox('marka_tepi', (b - a, 0.2, 0.03), 0.01, garis, loc=((a + b) / 2, y, 0.012))
        x = a + 1.5
        while x < b - 3:                                           # dashed lane lines
            for y in (-6.0, 6.0):
                geo.rbox('marka_putus', (3.0, 0.18, 0.03), 0.01, garis, loc=(x + 1.5, y, 0.012))
            x += 6.5
    for xc in (SIMPANG_X - 17, SIMPANG_X + 17):                    # zebra crossings
        for k in range(12):
            geo.rbox('zebra', (3.6, 1.1, 0.03), 0.01, garis, loc=(xc, -10.5 + k * 1.9, 0.012))
    # sidewalks (split around the crossing street) with kerbs
    trot = mat(p['trotoar'], 0.85, bump=0.3)
    for y in (-15.0, 15.0):
        for a, b in _celah(X0, X1):
            geo.rbox('trotoar', (b - a, 6.0, 0.4), 0.08, trot, loc=((a + b) / 2, y, 0.17))
    # buildings: far row (visible from the usual camera) and a near row (reverse shots), two layers deep
    for yc, tebal, tinggi_min, tinggi_maks in ((29.0, 14.0, 12, 30), (52.0, 18.0, 22, 52), (-31.0, 14.0, 12, 30)):
        x = X0
        while x < X1:
            w = rng.uniform(13, 21)
            if SIMPANG_X - 15 < x + w / 2 < SIMPANG_X + 15:
                x += 30; continue
            h = rng.uniform(tinggi_min, tinggi_maks) * (1.25 if ctx.dunia == 'nyata' else 1.0)
            warna = rng.choice(p['gedung'])
            gd = geo.rbox('gedung', (w, tebal, h), 0.35, fasad(warna, p['jendela'], ctx.malam, rng.uniform(1.4, 2.0), rng.uniform(1.8, 2.4)),
                          loc=(x + w / 2, yc, h / 2))
            s.penghalang.append((gd, yc))
            if ctx.dunia != 'nyata' and rng.random() < 0.5:         # pitched roof for the warm world
                s.penghalang.append((geo.lathe('atap', [(0, h + 3.0), (w * 0.55, h)], mat(p['atap'], 0.7), 4, parent=None,
                                               loc=(x + w / 2, yc, 0), rot=(0, 0, math.pi / 4), scale=(1, tebal / w, 1)), yc))
            else:
                s.penghalang.append((geo.rbox('atap', (w + 0.5, tebal + 0.5, 0.6), 0.15, mat(darker(warna, 0.7), 0.8),
                                              loc=(x + w / 2, yc, h + 0.3)), yc))
            x += w + rng.uniform(1.0, 2.5)
    # trees along the far sidewalk, street lamps on both
    daun, batang = mat(p['daun'], 0.7, sheen=0.2, bump=0.5), mat(p['batang'], 0.8)
    for a, b in _celah(X0, X1):
        x = a + 6
        while x < b - 4:
            geo.capsule('batang', 0.28, 2.6, batang, parent=None, loc=(x, 16.2, 1.6))
            for dx, dz, r in ((0, 4.2, 1.9), (-1.2, 3.4, 1.4), (1.2, 3.6, 1.5)):
                geo.sphere('daun', r, daun, 14, 9, loc=(x + dx, 16.2, dz))
            x += rng.uniform(12, 17)
    lampu = mat('#FFE9B0', 0.3, emit=6.0 if ctx.malam else 0.4)
    tiang = mat('#4A4D55', 0.5)
    for a, b in _celah(X0, X1):
        x = a + 10
        while x < b - 4:
            for y, arah in ((-13.2, 1), (13.2, -1)):
                geo.capsule('tiang_jalan', 0.13, 7.0, tiang, 10, 4, loc=(x, y, 3.6))
                geo.tube('lengan_lampu', [(x, y, 7.2), (x, y + arah * 1.4, 7.7), (x, y + arah * 2.8, 7.4)], 0.09, tiang, sides=6)
                geo.sphere('kepala_lampu', 1, lampu, 12, 8, loc=(x, y + arah * 2.9, 7.35), scale=(0.5, 0.3, 0.2))
            x += 30
    # named points
    for nama, (x, y, z, yaw) in dict(lajur_kiri=(0, 9, 0, 90), lajur_kanan=(0, 3, 0, 90), lajur_lawan_1=(0, -3, 0, -90),
                                      lajur_lawan_2=(0, -9, 0, -90), simpang=(SIMPANG_X, 0, 0, 0), trotoar=(0, -15, 0, 0),
                                      pulau_jalan=(0, 0, 0, 0), tiang=(SIMPANG_X - 14.5, 12.8, 0, 0)).items():
        s.titik[nama] = (x, y, z, yaw)
    s.kamera = dict(loc=(0, -34, 3.4), target=(0, 6, 2.6), lensa=50)
    return s
