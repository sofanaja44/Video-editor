"""Cast definitions (bible 03 §3). Every character is fictional; extras are derived from seed + number so
`warga_2` looks the same in every shot of an episode. Colours are the bible's palette."""
import random
from .materials import KULIT
from .rig import Character

PALET_FIGURAN = ['#5B8DEF', '#E85D75', '#F2B84B', '#4FA88B', '#9C6FB0', '#E8743B', '#6C7A89', '#3FA34D']
GAYA_RAMBUT = ['cepak', 'jambul', 'kuncir', 'keriting', 'bob', 'botak']
RAMBUT_WARNA = ['#1C1A1A', '#2B1D14', '#4A3020', '#1C1A1A']

KAMU = dict(kulit=KULIT['sawo'], baju='#E8743B', celana='#2F4A6D', alas='#3FA34D', alas_jenis='sandal',
            rambut='#1C1A1A', gaya_rambut='jambul', lengan='pendek')

# Bu Tetangga: square headscarf and a dotted house dress (daster)
TETANGGA = dict(kulit=KULIT['sawo'], baju='#F2B84B', baju_pola=('titik', '#FFF1CC', 2.4), celana='#F2B84B',
                alas='#E85D75', alas_jenis='sandal', rambut='#2B1D14', gaya_rambut='botak', lengan='pendek',
                bulu_mata=True, lebar=1.1, tinggi=0.97, hidung=0.9, ekspresi='senyum',
                ekstra=[('rok', dict(panjang=0.78, atas=0.66, bawah=0.92)), ('kerudung', dict(warna='#4FA88B'))])

# service officer: cream uniform with two chest pockets, ID lanyard without emblem
PETUGAS = dict(kulit=KULIT['sawo'], baju='#D9C7A1', celana='#5B4A3A', alas='#2B2B2B', alas_jenis='sepatu',
               rambut='#1C1A1A', gaya_rambut='cepak', lengan='pendek', ekspresi='netral',
               ekstra=[('saku_dada', dict(jumlah=2)), ('sabuk', dict(warna='#3A2E22')), ('tali_id', {})])

# police: dark brown uniform, peaked cap, black boots, no emblem or rank
POLISI = dict(kulit=KULIT['sawo'], baju='#6B4F33', celana='#4A3524', alas='#17181B', alas_jenis='bot',
              rambut='#1C1A1A', gaya_rambut='cepak', lengan='panjang', lebar=1.1, ekspresi='netral',
              ekstra=[('saku_dada', dict(jumlah=2)), ('sabuk', dict(warna='#17181B')), ('topi_pet', dict(warna='#6B4F33'))])

# corrupt-official archetype: black suit, red tie, round sunglasses, moustache, round belly
PEJABAT = dict(kulit=KULIT['terang'], baju='#22252B', celana='#22252B', alas='#101114', alas_jenis='sepatu',
               rambut='#2A2A2E', gaya_rambut='cepak', lengan='panjang', lebar=1.28, tinggi=1.02, ekspresi='licik',
               ekstra=[('dasi_jas', dict(dasi='#C8333B')), ('kacamata', dict(gelap=True, bingkai='#0E1014')),
                       ('kumis', {})])

# researcher / economist: yellow hard hat, round glasses, orange safety vest
PENELITI = dict(kulit=KULIT['sawo'], baju='#F4F1E8', celana='#5B4A3A', alas='#5A4632', alas_jenis='bot',
                rambut='#1C1A1A', gaya_rambut='cepak', lengan='panjang', ekspresi='netral',
                ekstra=[('rompi', dict(warna='#E57A2E')), ('helm_proyek', dict(warna='#F5C542')),
                        ('kacamata', dict(bingkai='#2B2D42'))])

# grandmother: white hair in a bun, glasses, purple kebaya, batik skirt, a stoop
NENEK = dict(kulit=KULIT['terang'], baju='#9C6FB0', celana='#6B3F2A', alas='#6B4F33', alas_jenis='sandal',
             rambut='#ECECF1', gaya_rambut='cepak', lengan='panjang', tinggi=0.9, bungkuk=10, hidung=1.1,
             ekspresi='senyum',
             ekstra=[('rok', dict(panjang=1.0, atas=0.64, bawah=0.78, warna='#6B3F2A', pola=('ombak', '#C79A4E', 5.0),
                                  tepi='#C79A4E')),
                     ('sanggul', {}), ('kacamata', dict(bingkai='#8A8F99', ukuran=0.3))])

# baby: head ~70% of the body, bare skin, white diaper
BAYI = dict(kulit=KULIT['terang'], baju=None, celana=None, alas='#F2C9A0', alas_jenis='tanpa', rambut='#1C1A1A',
            gaya_rambut='botak', lengan='tanpa', tinggi=0.5, kepala_skala=1.4, mata_besar=1.15, hidung=0.6,
            ekspresi='senyum', ekstra=[('popok', {}), ('jambul_bayi', {})])

# tire repairman: sleeveless vest, towel round the neck, backwards red cap, grease marks
TUKANG_BAN = dict(kulit=KULIT['gelap'], baju='#EDEDED', celana='#3B3F4A', alas='#4A4A4A', alas_jenis='sandal',
                  rambut='#1C1A1A', gaya_rambut='cepak', lengan='tanpa', lebar=1.15, ekspresi='netral',
                  ekstra=[('handuk', {}), ('noda', dict(jumlah=3)), ('topi_pet', dict(warna='#C8333B', balik=True, visor='#C8333B'))])

# the protagonist's mother: patterned-free scarf, loose long shirt
IBU = dict(kulit=KULIT['sawo'], baju='#F4E3C3', celana='#5B4A3A', alas='#8D5A3B', alas_jenis='sandal',
           rambut='#2B1D14', gaya_rambut='botak', lengan='panjang', bulu_mata=True, lebar=1.08, ekspresi='senyum',
           ekstra=[('rok', dict(panjang=0.6, atas=0.66, bawah=0.84)), ('kerudung', dict(warna='#B5546A'))])

PEMERAN = dict(kamu=KAMU, tetangga=TETANGGA, petugas=PETUGAS, polisi=POLISI, pejabat=PEJABAT, peneliti=PENELITI,
               nenek=NENEK, bayi=BAYI, tukang_ban=TUKANG_BAN, ibu=IBU)


def tokoh(nama, seed=0):
    """Build a named cast member: tokoh('polisi')."""
    return Character(PEMERAN[nama], nama, seed)


def kamu(seed=0):
    """Si Kamu: the protagonist, standing in for the viewer."""
    return tokoh('kamu', seed)


# roles for numbered extras: extra pieces that turn a plain extra into e.g. a minibus driver
PERAN = {
    'sopir_angkot': dict(lengan='pendek', ekstra=[('topi_pet', dict(warna='#3FA34D', balik=False, visor='#2B7A3A')), ('sabuk', dict(warna='#2B2420'))]),
    'anak': dict(tinggi=0.7, kepala_skala=1.12, mata_besar=1.08, lebar=0.9),
}


def spec_warga(nomor, seed=0, peran=None):
    rng = random.Random(f'{seed}-warga-{nomor}')
    s = dict(kulit=rng.choice(list(KULIT.values())), baju=rng.choice(PALET_FIGURAN),
             celana=rng.choice(['#2F4A6D', '#5B4A3A', '#3B3F4A', '#6C7A89']),
             alas=rng.choice(['#3FA34D', '#E85D75', '#4A4A4A', '#F2B84B']), alas_jenis=rng.choice(['sandal', 'sepatu']),
             rambut=rng.choice(RAMBUT_WARNA), gaya_rambut=rng.choice(GAYA_RAMBUT),
             lengan=rng.choice(['pendek', 'panjang']), tinggi=round(rng.uniform(0.92, 1.06), 3),
             lebar=round(rng.uniform(0.9, 1.18), 3))
    s.update(PERAN.get(peran, {}))
    return s


def warga(nomor, seed=0, peran=None):
    """Numbered extra (fixed look from seed + number), optionally with a role from PERAN."""
    return Character(spec_warga(nomor, seed, peran), f'warga_{nomor}', seed)


def kerumunan(jumlah, sebar='acak', seed=0, pusat=(0.0, 0.0), lebar=8.0, kedalaman=6.0, mulai=1):
    """A group of numbered extras. sebar: 'deret' (one row), 'lajur_penuh' (filled block), 'antre_lajur' (queue away
    from the camera), 'serobot_lajur' (staggered diagonal), 'acak'. Returns the list of Characters."""
    rng = random.Random(f'{seed}-kerumunan-{sebar}')
    cx, cy = pusat
    out = []
    cols = max(1, int(round((jumlah * lebar / max(kedalaman, 1e-3)) ** 0.5)))
    for i in range(jumlah):
        c = warga(mulai + i, seed)
        if sebar == 'deret':
            x, y, yaw = cx + (i - (jumlah - 1) / 2) * lebar / max(jumlah - 1, 1), cy, 0
        elif sebar == 'lajur_penuh':
            r, k = divmod(i, cols)
            x = cx + (k - (cols - 1) / 2) * lebar / max(cols - 1, 1) + rng.uniform(-0.25, 0.25)
            y = cy + r * kedalaman / max((jumlah - 1) // cols, 1) + rng.uniform(-0.25, 0.25)
            yaw = rng.uniform(-12, 12)
        elif sebar == 'antre_lajur':
            x, y, yaw = cx + rng.uniform(-0.15, 0.15), cy + i * kedalaman / max(jumlah - 1, 1), rng.uniform(-6, 6)
        elif sebar == 'serobot_lajur':
            x = cx + ((i % 3) - 1) * lebar / 3 + (i // 3) * 0.4
            y, yaw = cy + (i // 3) * kedalaman / max(jumlah // 3, 1), rng.uniform(-25, 25)
        else:
            x, y, yaw = cx + rng.uniform(-0.5, 0.5) * lebar, cy + rng.uniform(0, kedalaman), rng.uniform(-180, 180)
        c.place(x, y, yaw)
        out.append(c)
    return out
