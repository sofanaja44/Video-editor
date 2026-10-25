"""Set library (bible 03 §5). `bangun(nama, dunia, waktu, seed)` builds a set and returns a `Set` with named points.

Points are `(x, y, z, yaw_deg)`: where to put a character or prop; yaw > 0 turns the front (-Y) toward +X.
"""
import random

SETS = {}


def daftar(nama):
    def deko(fn):
        SETS[nama] = fn
        return fn
    return deko


class Konteks:
    def __init__(self, dunia='andai', waktu='siang', seed=0):
        self.dunia, self.waktu, self.seed = dunia, waktu, seed
        self.rng = random.Random(f'{seed}-{dunia}-{waktu}')
        self.malam = waktu == 'malam'


class Set:
    def __init__(self, nama):
        self.nama = nama
        self.titik = {}
        self.kamera = dict(loc=(0, -34, 3.2), target=(0, 6, 2.5), lensa=50)
        self.penghalang = []          # (object, y_centre): things that may stand between camera and subject

    def pandang(self, cam_loc, fokus):
        """Hide (for rendering) the blockers whose centre lies between the camera and the subject along Y."""
        lo, hi = sorted((cam_loc[1], fokus[1]))
        n = 0
        for o, yc in self.penghalang:
            hilang = lo - 2 < yc < hi + 2
            o.hide_render = o.hide_viewport = hilang
            n += hilang
        return n

    def di(self, nama):
        return self.titik[nama]


def bangun(nama, dunia='andai', waktu='siang', seed=0):
    from . import jalan_raya    # noqa: F401  (importing registers the sets)
    return SETS[nama](Konteks(dunia, waktu, seed))
