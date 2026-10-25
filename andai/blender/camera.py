"""Camera moves for one shot (bible 04 §6.4): push_in, pull_out, truck, cu, tilt, shake, orbit.

`pasang(spec, fokus, f0, f1)` builds a camera aimed at `fokus` (world point of the subject) from the storyboard's
`kamera` dict and keys it over frames f0..f1. Zoom is done by dollying (distance / zoom), as in a real push-in.
"""
import math
import random
import bpy
from mathutils import Vector

SUDUT = {'rendah': -9.0, 'normal': 5.0, 'tinggi': 24.0}      # elevation of the camera above the subject, degrees


def pasang(spec, fokus, f0=1, f1=60, jarak=None, lensa=None, azimut=0.0, seed=0, tinggi_min=0.9):
    gerak = spec.get('gerak', 'diam')
    cu = gerak == 'cu'
    lens = lensa or spec.get('lensa') or (70 if cu else 50)
    d = jarak or spec.get('jarak') or (8.0 if cu else 17.0)
    elev = math.radians(SUDUT.get(spec.get('sudut', 'normal'), 5.0))
    az = math.radians(spec.get('azimut', azimut))
    z0, z1 = spec.get('zoom', [1.0, 1.0])
    if cu and spec.get('zoom') is None:
        z0, z1 = 1.0, 1.05
    f = Vector(fokus)

    def posisi(zoom, geser=0.0, az_extra=0.0):
        dist = d / zoom
        a = az + az_extra
        z = max(tinggi_min, f.z + dist * math.sin(elev))        # a low angle still keeps the lens above the road
        return Vector((f.x + dist * math.sin(a) * math.cos(elev) + geser, f.y - dist * math.cos(a) * math.cos(elev), z))

    lebar = 2 * d * math.tan(math.atan(18.0 / lens))           # frame width at the subject (sensor-fit on the long side)
    geser = spec.get('geser', 0.0) * lebar if gerak == 'truck' else 0.0
    a0 = a1 = 0.0
    if gerak == 'orbit':
        a0, a1 = math.radians(-spec.get('derajat', 8)), math.radians(spec.get('derajat', 8))
    p0, p1 = posisi(z0, -geser / 2, a0), posisi(z1, geser / 2, a1)
    bpy.ops.object.camera_add(location=p0)
    cam = bpy.context.object; cam.name = 'kamera'
    cam.data.lens = lens
    mid = (p0 + p1) / 2
    cam.rotation_euler = (f - mid).to_track_quat('-Z', 'Y').to_euler()
    if gerak == 'tilt':                                         # pitch from a down-look to an up-look around the subject
        derajat = spec.get('derajat', 10)
        cam.rotation_euler.x += math.radians(-derajat / 2)
    cam.location = p0
    cam.keyframe_insert('location', frame=f0)
    if gerak == 'tilt':
        cam.keyframe_insert('rotation_euler', frame=f0)
        cam.rotation_euler.x += math.radians(derajat)
        cam.keyframe_insert('rotation_euler', frame=f1)
    cam.location = p1
    cam.keyframe_insert('location', frame=f1)
    if spec.get('getar'):                                       # handheld shake, deterministic
        rng = random.Random(seed)
        for fr in range(f0, f1 + 1, 2):
            t = (fr - f0) / max(f1 - f0, 1)
            cam.location = p0 + (p1 - p0) * t + Vector((rng.uniform(-1, 1), 0, rng.uniform(-1, 1))) * spec['getar']
            cam.keyframe_insert('location', frame=fr)
    bpy.context.scene.camera = cam
    return cam
