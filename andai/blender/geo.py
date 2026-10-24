"""Mesh and joint primitives built from code (Blender is Z-up; characters face -Y, toward the camera)."""
import math
import bmesh
import bpy
from mathutils import Vector


def _link(o, parent=None, loc=None, rot=None, scale=None):
    bpy.context.scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    if loc is not None:
        o.location = loc
    if rot is not None:
        o.rotation_euler = rot
    if scale is not None:
        o.scale = scale
    return o


def empty(name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Joint (the three.js Object3D of the design docs)."""
    return _link(bpy.data.objects.new(name, None), parent, loc, rot)


def mesh_obj(name, verts, faces, material, parent=None, loc=None, rot=None, scale=None, smooth=True, weld=0.0):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    if weld:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=weld)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)   # outward on closed meshes whatever the winding
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.materials.append(material)
    return _link(bpy.data.objects.new(name, me), parent, loc, rot, scale)


def lathe(name, profile, material, segments=48, depth=1.0, **kw):
    """Surface of revolution about Z. profile = [(r, z), ...] bottom to top; r == 0 makes a pole."""
    verts, faces, rings = [], [], []
    for r, z in profile:
        if r < 1e-6:
            verts.append((0, 0, z)); rings.append([len(verts) - 1])
        else:
            ids = []
            for j in range(segments):
                a = 2 * math.pi * j / segments
                verts.append((r * math.cos(a), r * math.sin(a) * depth, z)); ids.append(len(verts) - 1)
            rings.append(ids)
    for lo, hi in zip(rings, rings[1:]):
        if len(lo) == 1 or len(hi) == 1:
            pole, ring = (lo[0], hi) if len(lo) == 1 else (hi[0], lo)
            faces += [(pole, ring[j], ring[(j + 1) % segments]) for j in range(segments)]
        else:
            faces += [(lo[j], lo[(j + 1) % segments], hi[(j + 1) % segments], hi[j]) for j in range(segments)]
    return mesh_obj(name, verts, faces, material, **kw)


def sphere(name, r, material, segments=24, rings=14, **kw):
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    return lathe(name, prof, material, segments, **kw)


def capsule(name, r, length, material, segments=24, cap_rings=7, **kw):
    """Capsule along Z, `length` = distance between the two cap centres."""
    h = length / 2
    prof = [(r * math.sin(math.pi / 2 * i / cap_rings), -h - r * math.cos(math.pi / 2 * i / cap_rings))
            for i in range(cap_rings + 1)]
    prof += [(r * math.cos(math.pi / 2 * i / cap_rings), h + r * math.sin(math.pi / 2 * i / cap_rings))
             for i in range(cap_rings + 1)]
    return lathe(name, prof, material, segments, **kw)


def tube(name, pts, r, material, closed=False, sides=10, cap_rings=3, up=(0, 1, 0), **kw):
    """Round tube along a polyline. `up` fixes the cross-section frame, so it suits curves drawn on a
    surface whose normal is `up` (mouths, brows). Open tubes get hemispherical end caps."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    verts, faces = [], []

    def tangent(i):
        a, b = (pts[i - 1], pts[(i + 1) % n]) if closed else (pts[max(i - 1, 0)], pts[min(i + 1, n - 1)])
        return (b - a).normalized()

    def ring(center, t, rad):
        u = Vector(up); u = (u - t * u.dot(t)).normalized(); w = t.cross(u)
        ids = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            verts.append(center + rad * (math.cos(a) * u + math.sin(a) * w)); ids.append(len(verts) - 1)
        return ids

    def pole(p):
        verts.append(p); return [len(verts) - 1]

    body = [ring(p, tangent(i), r) for i, p in enumerate(pts)]
    if closed:
        seq = body + [body[0]]
    else:
        t0, t1 = tangent(0), tangent(n - 1)
        ang = [math.pi / 2 * k / (cap_rings + 1) for k in range(1, cap_rings + 1)]
        head = [pole(pts[0] - t0 * r)] + [ring(pts[0] - t0 * r * math.sin(al), t0, r * math.cos(al)) for al in reversed(ang)]
        tail = [ring(pts[-1] + t1 * r * math.sin(al), t1, r * math.cos(al)) for al in ang] + [pole(pts[-1] + t1 * r)]
        seq = head + body + tail
    for lo, hi in zip(seq, seq[1:]):
        if len(lo) == 1 or len(hi) == 1:
            pl, rg = (lo[0], hi) if len(lo) == 1 else (hi[0], lo)
            faces += [(pl, rg[k], rg[(k + 1) % sides]) for k in range(sides)]
        else:
            faces += [(lo[k], lo[(k + 1) % sides], hi[(k + 1) % sides], hi[k]) for k in range(sides)]
    return mesh_obj(name, verts, faces, material, **kw)


def flat_poly(name, pts, thick, material, **kw):
    """Extruded convex polygon in the XZ plane (extruded toward +Y); used for the open-mouth shape."""
    n = len(pts)
    verts = [(x, 0, z) for x, z in pts] + [(x, thick, z) for x, z in pts]
    faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return mesh_obj(name, verts, faces, material, **kw)


def star(name, r_out, r_in, thick, material, points=5, **kw):
    """Five-point star in the XZ plane, thickened along Y."""
    pts = [((r_out if i % 2 == 0 else r_in) * math.sin(math.pi * i / points),
            (r_out if i % 2 == 0 else r_in) * math.cos(math.pi * i / points)) for i in range(2 * points)]
    n = len(pts)
    verts = [(x, -thick / 2, z) for x, z in pts] + [(x, thick / 2, z) for x, z in pts] + [(0, -thick / 2, 0), (0, thick / 2, 0)]
    faces = [(2 * n, i, (i + 1) % n) for i in range(n)] + [(2 * n + 1, n + (i + 1) % n, n + i) for i in range(n)]
    faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return mesh_obj(name, verts, faces, material, smooth=False, **kw)


def surface(name, fn, nu, nv, material, wrap=True, **kw):
    """Parametric grid surface: fn(u, v) -> (x, y, z), u in [0, 1) around (wraps if `wrap`), v in [0, 1].
    Rows that collapse to one point (poles) are welded, so a cap can close with a single vertex."""
    cols = nu if wrap else nu + 1
    verts = [fn(i / nu, j / nv) for i in range(cols) for j in range(nv + 1)]
    faces = []
    for i in range(nu):
        i2 = (i + 1) % cols
        for j in range(nv):
            faces.append((i * (nv + 1) + j, i2 * (nv + 1) + j, i2 * (nv + 1) + j + 1, i * (nv + 1) + j + 1))
    return mesh_obj(name, verts, faces, material, weld=1e-5, **kw)


def rbox(name, size, radius, material, segments=3, **kw):
    """Box with rounded edges (pockets, visors, buckles); size = (x, y, z) full extents."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=radius, segments=segments, profile=0.5, affect='EDGES')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.materials.append(material)
    return _link(bpy.data.objects.new(name, me), kw.get('parent'), kw.get('loc'), kw.get('rot'), kw.get('scale'))
