"""Prop library (bible 03 §6). `PROPS[id](**params)` builds a prop and returns a `Prop` with named sockets.

Props face -Y like characters (front = -Y); `place` moves and turns them; `titik['nama']` are empties for
attaching riders, hands, smoke and so on.
"""
import math
from .. import geo

PROPS = {}


def daftar(nama):
    def deko(fn):
        PROPS[nama] = fn
        return fn
    return deko


class Prop:
    def __init__(self, nama):
        self.nama = nama
        self.root = geo.empty(nama)
        self.titik = {}

    def socket(self, nama, loc, rot=(0, 0, 0)):
        self.titik[nama] = geo.empty(f'{self.root.name}.{nama}', self.root, loc, rot)
        return self.titik[nama]

    def place(self, x=0.0, y=0.0, z=0.0, yaw=0.0):
        """yaw in degrees, positive turns the front toward +X."""
        self.root.location = (x, y, z)
        self.root.rotation_euler = (0, 0, math.radians(yaw))
        return self


def buat(nama, **kw):
    from . import kendaraan, lampu    # noqa: F401  (importing registers the props)
    return PROPS[nama](**kw)
