"""Traffic light (bible 03 §6.2): pole, arm, black housing with three lenses; `status` lights one of them."""
from .. import geo
from ..materials import mat
from . import Prop, daftar


@daftar('lampu_lalu_lintas')
def lampu_lalu_lintas(status='hijau', tinggi=6.5):
    p = Prop('lampu_lalu_lintas'); n, r = p.nama, p.root
    tiang = mat('#4A4D55', 0.5)
    geo.capsule(f'{n}.tiang', 0.14, tinggi - 0.3, tiang, parent=r, loc=(0, 0, (tinggi - 0.3) / 2 + 0.14))
    geo.rbox(f'{n}.kotak', (0.95, 0.7, 2.5), 0.2, mat('#17181B', 0.45), parent=r, loc=(0, -0.2, tinggi - 0.9))
    for i, (nama, hexc) in enumerate((('merah', '#FF3B30'), ('kuning', '#FFC400'), ('hijau', '#22D45A'))):
        nyala = nama == status
        geo.sphere(f'{n}.lensa_{nama}', 1, mat(hexc if nyala else '#2B2D31', 0.2, emit=4.0 if nyala else 0.0), 16, 10,
                   parent=r, loc=(0, -0.58, tinggi - 0.9 + (0.78 - 0.78 * i)), scale=(0.27, 0.12, 0.27))
    p.socket('lensa', (0, -0.7, tinggi - 0.9))
    return p
