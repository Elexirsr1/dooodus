"""Props: wax candles with animated flames and lights, iron candelabras, roses and scattered petals."""
import math
import random
import zlib

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

from . import materials as M
from .util import add_noise, circle_profile, collection, lathe, sweep

FLAME_COLOR = (1.0, 0.50, 0.19)
DAIS_STEPS = ((3.0, 0.32), (3.4, 0.16))  # (circumradius, top height) of the octagonal steps, inner first


def dais_height(x, y):
    """Top surface height at (x, y): octagonal steps with flat faces toward the axes."""
    for circ, top in DAIS_STEPS:
        apothem = circ * math.cos(math.pi / 8)
        if max(x * math.cos(k * math.pi / 4) + y * math.sin(k * math.pi / 4) for k in range(8)) <= apothem - 0.03:
            return top
    return 0.0


def tilt_euler(direction, tilt, spin):
    """Euler that spins an object about Z then leans its +Z axis by `tilt` toward planar angle `direction`."""
    axis = Vector((-math.sin(direction), math.cos(direction), 0.0))
    m = Matrix.Rotation(tilt, 3, axis) @ Matrix.Rotation(spin, 3, "Z")
    return m.to_euler()


# ----------------------------------------------------------------------------- candles

def _candle_mesh(name, radius, height, seed):
    rnd = random.Random(seed)
    drips = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(0.18, 0.7) * height, rnd.uniform(0.0035, 0.008))
             for _ in range(rnd.randint(3, 6))]
    melt = height - 0.004

    def radial(a, z, r):
        bump = 0.0
        for (da, dl, dw) in drips:
            ang = (a - da + math.pi) % (2 * math.pi) - math.pi
            run = (z - (melt - dl)) / 0.012
            if run <= 0:
                continue
            bump += 0.0024 * math.exp(-((ang * r) / dw) ** 2) * min(run, 1.0) ** 0.5
        return r + bump

    prof = [(radius * 0.97, 0.0)]
    zs = [0.002] + [k * 0.008 for k in range(1, int(melt / 0.008) + 1)] + [melt]
    for z in zs:
        prof.append((radius, z))
    prof += [(radius * 0.985, height), (radius * 0.93, height + 0.0015), (radius * 0.80, height - 0.002),
             (radius * 0.45, height - 0.008), (0.0, height - 0.009)]
    bm = bmesh.new()
    lathe(bm, prof, 28, radial_fn=radial)
    # wick (material slot 1), slightly bent
    w0 = height - 0.009
    lathe(bm, [(0.0012, w0), (0.0011, w0 + 0.006), (0.0009, w0 + 0.011), (0.0, w0 + 0.013)], 8, mat=1,
          center=(0.0006, 0.0, 0.0))
    me = bpy.data.meshes.new(name)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.get("wax_ivory"))
    me.materials.append(M.get("wick"))
    return me, w0 + 0.012


def _flame_mesh():
    me = bpy.data.meshes.get("Flame_Unit")
    if me:
        return me
    bm = bmesh.new()
    prof = []
    for k in range(17):
        t = k / 16
        r = 0.14 * math.sin(math.pi * t ** 0.55) ** 0.9 * (1 - 0.12 * t)
        prof.append((r if 0 < k < 16 else 0.0, t))
    lathe(bm, prof, 16)
    me = bpy.data.meshes.new("Flame_Unit")
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.get("flame"))
    return me


class CandleKit:
    """Shared candle meshes (by size preset) + per-instance flame/light with procedural flicker."""

    PRESETS = {
        "pillar_l": (0.045, 0.34), "pillar_m": (0.036, 0.24), "pillar_s": (0.032, 0.15),
        "votive": (0.026, 0.075), "taper": (0.017, 0.26), "taper_s": (0.016, 0.18),
    }

    def __init__(self, coll, seed=7):
        self.coll = coll
        self.rnd = random.Random(seed)
        self.meshes = {}
        self.count = 0
        self.lights = []
        self.flames = []

    def _mesh(self, preset):
        key = (preset, self.rnd.randint(0, 1))
        if key not in self.meshes:
            r, h = self.PRESETS[preset]
            self.meshes[key] = _candle_mesh(f"Candle_{preset}_{key[1]}", r, h, zlib.crc32(f"{preset}{key[1]}".encode()))
        return self.meshes[key]

    def add(self, location, preset="pillar_m", wax="wax_ivory", energy=None, parent=None, height_scale=1.0):
        me, flame_z = self._mesh(preset)
        self.count += 1
        idx = self.count
        loc = Vector(location)
        ob = bpy.data.objects.new(f"Candle_{idx:03d}", me)
        ob.location = loc
        ob.rotation_euler = (0, 0, self.rnd.uniform(0, 2 * math.pi))
        ob.scale = (1, 1, height_scale)
        self.coll.objects.link(ob)
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = M.get(wax)
        ob.material_slots[1].link = "OBJECT"
        ob.material_slots[1].material = M.get("wick")
        tip = loc + Vector((0, 0, flame_z * height_scale - 0.002))
        r = self.PRESETS[preset][0]
        size = 0.030 + 0.20 * r  # bigger wicks on fatter candles
        fl = bpy.data.objects.new(f"Flame_{idx:03d}", _flame_mesh())
        fl.location = tip
        fl.scale = (size, size, size)
        self.coll.objects.link(fl)
        fl.visible_shadow = False
        fl.visible_diffuse = False
        fl.visible_volume_scatter = False
        ph = self.rnd.uniform(0, 1000)
        add_noise(fl, "scale", 2, size, size * 0.10, 9.0, ph)
        add_noise(fl, "scale", 0, size, size * 0.05, 7.0, ph + 31)
        add_noise(fl, "scale", 1, size, size * 0.05, 7.0, ph + 31)
        add_noise(fl, "rotation_euler", 0, 0.0, 0.05, 22.0, ph + 57)
        add_noise(fl, "rotation_euler", 1, 0.0, 0.05, 25.0, ph + 83)
        ld = bpy.data.lights.new(f"CandleLight_{idx:03d}", "POINT")
        ld.color = FLAME_COLOR
        ld.shadow_soft_size = 0.007
        e = energy if energy is not None else (0.9 + 9.0 * r)
        ld.energy = e
        lo = bpy.data.objects.new(f"CandleLight_{idx:03d}", ld)
        lo.location = tip + Vector((0, 0, size * 0.6))  # lifted so the wax rim does not clip to white
        self.coll.objects.link(lo)
        lo.visible_glossy = False  # the flame mesh already shows up in reflections
        add_noise(ld, "energy", 0, e, e * 0.22, 11.0, ph + 7)
        self.lights.append(lo)
        self.flames.append(fl)
        return ob, fl, lo


# ----------------------------------------------------------------------------- candelabra

def candelabra_mesh():
    me = bpy.data.meshes.get("Candelabra_Iron")
    if me:
        return me
    bm = bmesh.new()
    # central shaft with knops
    prof = [(0.07, 0.0), (0.075, 0.03), (0.05, 0.06), (0.03, 0.10), (0.022, 0.16), (0.022, 0.40), (0.045, 0.44),
            (0.045, 0.47), (0.020, 0.51), (0.018, 0.82), (0.038, 0.86), (0.030, 0.90), (0.018, 0.93),
            (0.017, 1.22), (0.046, 1.27), (0.050, 1.30), (0.030, 1.33), (0.020, 1.38), (0.020, 1.43),
            (0.0, 1.43)]
    lathe(bm, prof, 16)
    # drip pans + sockets: centre and two arms
    pan = [(0.0, 0.0), (0.075, 0.0), (0.085, 0.012), (0.08, 0.016), (0.06, 0.006), (0.02, 0.006), (0.02, 0.05),
           (0.024, 0.055), (0.0, 0.055)]
    lathe(bm, [(r, z + 1.43) for (r, z) in pan], 20)
    for sx in (-1, 1):
        lathe(bm, [(r * 0.8, z * 0.8 + 1.37) for (r, z) in pan], 20, center=(sx * 0.27, 0.0, 0.0))
    # arms: S-curved bars from the shaft to each socket
    for sx in (-1, 1):
        path = []
        for k in range(17):
            t = k / 16
            x = sx * 0.27 * (t ** 0.9)
            z = 1.28 - 0.07 * math.sin(math.pi * t) + 0.09 * t ** 2
            path.append(Vector((x, 0.0, z)))
        sweep(bm, path, circle_profile(0.012, 8), normal0=Vector((0, 1, 0)))
        # small gothic spike below each arm end
        tip = Vector((sx * 0.27, 0, 1.37))
        lathe(bm, [(0.0, -0.09), (0.012, -0.03), (0.0, 0.0)], 8, center=tuple(tip))
    # tripod legs with scrolled feet
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        path = []
        for j in range(19):
            t = j / 18
            r = 0.04 + 0.30 * t
            z = 0.42 * (1 - t) ** 1.6 + 0.012
            path.append(Vector((r * ca, r * sa, z)))
        sweep(bm, path, circle_profile(0.013, 8))
        # curl at the foot
        for j in range(10):
            t = j / 9
            ang = math.pi * 1.4 * t
            rr = 0.045 * (1 - 0.5 * t)
            c = Vector(((0.34 + rr * math.sin(ang)) * ca, (0.34 + rr * math.sin(ang)) * sa, 0.055 - rr * math.cos(ang)))
            bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.014 * (1 - 0.4 * t),
                                      matrix=Matrix.Translation(c))
    me = bpy.data.meshes.new("Candelabra_Iron")
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        e.smooth = len(e.link_faces) != 2 or e.calc_face_angle(0.0) < math.radians(45)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.get("iron"))
    return me


def place_candelabra(coll, kit, location, rot_z, name):
    ob = bpy.data.objects.new(name, candelabra_mesh())
    ob.location = location
    ob.rotation_euler = (0, 0, rot_z)
    coll.objects.link(ob)
    m = Matrix.Translation(location) @ Euler((0, 0, rot_z)).to_matrix().to_4x4()
    kit.add(m @ Vector((0, 0, 1.43 + 0.045)), "taper", "wax_ivory", energy=1.6)
    for sx in (-1, 1):
        kit.add(m @ Vector((sx * 0.27, 0, 1.37 + 0.036)), "taper_s", "wax_ivory", energy=1.4)
    return ob


# ----------------------------------------------------------------------------- roses

def _petal(bm, phi, r0, z0, L, W, tilt, cup, curl, rnd, mat=0, nu=7, nv=7):
    grid = []
    wave = rnd.uniform(0, 6.28)
    rot = Matrix.Rotation(phi, 3, "Z")
    for j in range(nv):
        v = j / (nv - 1)
        width = W * math.sin(math.pi * (0.10 + 0.82 * v)) ** 0.8 * (0.45 + 0.55 * v ** 0.45)
        row = []
        for i in range(nu):
            u = -1 + 2 * i / (nu - 1)
            x = u * width
            y = -cup * width * 0.55 * u * u * (0.35 + 0.65 * v)
            y += curl * L * v ** 3 * (1.0 - 0.35 * u * u)
            y += 0.07 * W * math.sin(4.5 * u + wave) * v ** 2
            z = v * L
            yy = y * math.cos(tilt) + z * math.sin(tilt)
            zz = -y * math.sin(tilt) + z * math.cos(tilt)
            p = rot @ Vector((x, r0 + yy, z0 + zz))
            row.append(bm.verts.new(p))
        grid.append(row)
    for j in range(nv - 1):
        for i in range(nu - 1):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])).material_index = mat


def rose_mesh(name, openness=0.6, petals=22, stem=0.0, seed=1):
    me = bpy.data.meshes.get(name)
    if me:
        return me
    rnd = random.Random(seed)
    bm = bmesh.new()
    golden = math.radians(137.508)
    for k in range(petals):
        t = k / (petals - 1)
        L = 0.019 + 0.030 * t ** 0.8
        W = 0.011 + 0.022 * t ** 0.9
        r0 = 0.0015 + 0.011 * t ** 1.1
        tilt = math.radians(4 + (10 + 72 * openness) * t ** 1.5)
        cup = 0.85 - 0.45 * t * openness
        curl = (0.15 + 0.55 * openness) * t ** 2
        _petal(bm, k * golden + rnd.uniform(-0.15, 0.15), r0, -0.010 * t, L, W, tilt, cup, curl, rnd)
    for k in range(5):  # sepals
        _petal(bm, k * 2 * math.pi / 5 + 0.3, 0.008, -0.010, 0.028, 0.006, math.radians(118), 0.3, 0.1, rnd, mat=1,
               nu=5, nv=5)
    if stem > 0:
        path = [Vector((0.012 * math.sin(math.pi * s), 0.0, -0.012 - stem * s)) for s in [i / 14 for i in range(15)]]
        sweep(bm, path, circle_profile(0.0034, 8), mat=1)
        for s, side in ((0.38, 1), (0.66, -1)):
            p = path[int(s * 14)]
            leaf_rot = math.radians(90 * side)
            sub = bmesh.new()
            _petal(sub, 0.0, 0.0, 0.0, 0.055, 0.020, math.radians(60), 0.25, 0.25, rnd, mat=1, nu=5, nv=6)
            mtx = Matrix.Translation(p) @ Matrix.Rotation(leaf_rot, 4, "Z") @ Matrix.Rotation(math.radians(180), 4, "X")
            for v in sub.verts:
                v.co = mtx @ v.co
            tmp = bpy.data.meshes.new("_leaf_tmp")
            sub.to_mesh(tmp)
            sub.free()
            bm.from_mesh(tmp)
            bpy.data.meshes.remove(tmp)
    me = bpy.data.meshes.new(name)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.get("rose_red"))
    me.materials.append(M.get("leaf"))
    return me


def petal_mesh(name, seed):
    me = bpy.data.meshes.get(name)
    if me:
        return me
    rnd = random.Random(seed)
    bm = bmesh.new()
    _petal(bm, 0.0, 0.0, 0.0, 0.04 + rnd.uniform(-0.005, 0.008), 0.024, math.radians(rnd.uniform(70, 90)),
           rnd.uniform(0.3, 0.8), rnd.uniform(0.1, 0.5), rnd, nu=7, nv=7)
    me = bpy.data.meshes.new(name)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.get("rose_red"))
    return me


def place(coll, me, name, location, rotation, scale, petal_mat):
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    ob.rotation_euler = rotation
    ob.scale = (scale, scale, scale)
    coll.objects.link(ob)
    ob.material_slots[0].link = "OBJECT"
    ob.material_slots[0].material = M.get(petal_mat)
    return ob


# ----------------------------------------------------------------------------- layout

def build(root, altar_top, dais_top):
    coll = collection("Props", root)
    candles = collection("Candles", coll)
    roses = collection("Roses", coll)
    kit = CandleKit(candles)
    rnd = random.Random(11)

    # altar: tall clusters on the back corners, low votives in front so nothing crowds the trophy
    for (cx, cy) in ((-0.82, 0.38), (0.82, 0.38)):
        s = 1 if cx > 0 else -1
        kit.add((cx, cy, altar_top), "pillar_l", "wax_ivory")
        kit.add((cx - s * 0.11, cy + 0.07, altar_top), "pillar_m", "wax_red")
        kit.add((cx - s * 0.03, cy - 0.11, altar_top), "pillar_s", "wax_ivory")
    for (cx, cy) in ((-0.84, -0.40), (0.84, -0.40)):
        s = 1 if cx > 0 else -1
        kit.add((cx, cy, altar_top), "votive", "wax_ivory", energy=0.8)
        kit.add((cx - s * 0.09, cy + 0.05, altar_top), "votive", "wax_red", energy=0.8)

    # votives on the reredos ledges
    for sx in (-1, 1):
        for k in range(5):
            kit.add((sx * (1.72 + 0.22 * k), 3.80, 1.38), "votive", "wax_red" if k % 2 else "wax_ivory", energy=0.9)

    # floor clusters around the dais, outside the camera's orbit
    cluster_az = (-62, -28, 28, 62, 118, -118)
    for az in cluster_az:
        a = math.radians(az)
        base = Vector((3.65 * math.sin(a), -3.65 * math.cos(a), 0.0))
        for j, (dx, dy, preset, wax) in enumerate(((0, 0, "pillar_l", "wax_ivory"), (0.11, 0.07, "pillar_m", "wax_black"),
                                                   (-0.09, 0.09, "pillar_s", "wax_ivory"),
                                                   (0.04, -0.12, "votive", "wax_red"))):
            kit.add(base + Vector((dx, dy, 0)), preset, wax, height_scale=rnd.uniform(0.85, 1.25))

    # candelabras flanking the sanctuary
    for i, (az, r) in enumerate(((40, 4.3), (-40, 4.3), (90, 3.95), (-90, 3.95), (140, 4.3), (-140, 4.3))):
        a = math.radians(az)
        place_candelabra(candles, kit, Vector((r * math.sin(a), -r * math.cos(a), 0.0)), a, f"Candelabra_{i}")

    # roses: nestled round the trophy foot (front left open for the plaque), on the altar, on the steps
    bloom = rose_mesh("Rose_Bloom", 0.85, 24, seed=3)
    half = rose_mesh("Rose_Half", 0.5, 21, seed=5)
    bud = rose_mesh("Rose_Bud", 0.12, 14, seed=8)
    bloom_s = rose_mesh("Rose_Bloom_Stem", 0.8, 24, stem=0.26, seed=13)
    half_s = rose_mesh("Rose_Half_Stem", 0.45, 20, stem=0.24, seed=21)
    k = 0
    for az in (-150, -112, -72, -34, 34, 72, 112, 150, 180):
        a = math.radians(az - 90)  # az measured from the front (-Y); front +/-30 deg left clear for the plaque
        rr = 0.33 + rnd.uniform(-0.02, 0.03)
        p = (rr * math.cos(a), rr * math.sin(a), altar_top + 0.012)
        me = (bloom, half, bud)[k % 3]
        place(roses, me, f"Rose_Altar_{k:02d}", p, tilt_euler(a, rnd.uniform(0.35, 0.7), rnd.uniform(0, 6.28)),
              rnd.uniform(1.15, 1.45), "rose_black" if k % 2 else "rose_red")
        k += 1
    for (x, y, rz) in ((-0.55, 0.42, 0.4), (0.58, 0.44, -0.6), (-0.62, -0.47, 2.6), (0.60, -0.50, 3.6)):
        place(roses, (bloom_s, half_s)[k % 2], f"Rose_Altar_{k:02d}", (x, y, altar_top + 0.034),
              (math.radians(84), 0, rz), rnd.uniform(1.1, 1.3), "rose_red" if k % 2 else "rose_black")
        k += 1
    for az in (-75, -40, -15, 15, 40, 75, 105, -105):
        a = math.radians(az)
        for j in range(3):
            rr = 3.18 + rnd.uniform(-0.25, 0.1)
            aa = a + rnd.uniform(-0.09, 0.09)
            x, y = rr * math.sin(aa), -rr * math.cos(aa)
            p = (x, y, dais_height(x, y) + (0.04 if j == 0 else 0.008))
            if j == 0:
                me, rot = (bloom_s, half_s)[k % 2], (math.radians(86), 0, aa + rnd.uniform(-0.8, 0.8))
            else:
                me = (bloom, half, bud)[k % 3]
                rot = tilt_euler(rnd.uniform(0, 6.28), rnd.uniform(0.2, 0.9), rnd.uniform(0, 6.28))
            place(roses, me, f"Rose_Steps_{k:02d}", p, rot, rnd.uniform(1.2, 1.6), "rose_black" if k % 3 else "rose_red")
            k += 1

    # scattered petals
    petals = [petal_mesh(f"Petal_{i}", 40 + i) for i in range(4)]
    spots = []
    for _ in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.42, 0.95)
        spots.append(((rr * math.cos(a) * 1.0, rr * math.sin(a) * 0.55, altar_top + 0.003), True))
    for _ in range(46):
        a = rnd.uniform(math.radians(-110), math.radians(110))
        rr = rnd.uniform(2.6, 3.9)
        x, y = rr * math.sin(a), -rr * math.cos(a)
        spots.append(((x, y, dais_height(x, y) + 0.003), False))
    for i, (p, on_altar) in enumerate(spots):
        if on_altar and abs(p[0]) < 0.3 and abs(p[1]) < 0.3:
            continue
        place(roses, petals[i % 4], f"Petal_{i:03d}", p,
              (rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15), rnd.uniform(0, 6.28)),  # petal mesh already lies flat
              rnd.uniform(0.8, 1.15), "rose_black" if i % 3 else "rose_red")
    return dict(collection=coll, kit=kit)
