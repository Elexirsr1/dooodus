"""Black Gothic heraldic shield with a faceted gold crown emblem and thorn vines (after the reference)."""
import math
import random

import bmesh
from mathutils import Matrix, Vector

from . import materials as M
from .util import circle_profile, collection, empty, finish_bmesh, polygon_offset, resample_closed, sweep

TOP, TIP, HALF_W = 1.15, -1.42, 1.0


def _bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def outline(count=240):
    """Heater-shield silhouette (u, v), counter-clockwise viewed from the front."""
    right = [_bezier((0.0, TIP), (0.78, -0.86), (1.035, 0.28), (HALF_W, TOP), i / 48) for i in range(49)]
    top = [(HALF_W - 2 * HALF_W * i / 30, 1.07 + 0.08 * (HALF_W - 2 * HALF_W * i / 30) ** 2) for i in range(1, 30)]
    left = [(-x, y) for (x, y) in reversed(right)]
    pts = right + top + left[:-1]
    return resample_closed(pts, count)


def bulge(u, v):
    """Depth of the curved face toward the viewer (cylindrical with a gentle vertical crown)."""
    return 0.10 * (1 - (u / 1.06) ** 2) + 0.025 * (1 - ((v + 0.15) / 1.45) ** 2)


def _shield_body(coll, parent):
    out = outline()
    n = len(out)
    cu = sum(p[0] for p in out) / n
    cv = sum(p[1] for p in out) / n
    # (inset, height above the field plane, material of the band starting here) from the outer edge in
    bands = [(0.000, 0.000, 1), (0.020, 0.040, 1), (0.055, 0.048, 1), (0.085, 0.040, 1), (0.100, 0.012, 0),
             (0.112, 0.012, 2), (0.116, 0.021, 2), (0.128, 0.021, 2), (0.132, 0.012, 0), (0.150, 0.012, 0)]
    bm = bmesh.new()
    rings = []
    for inset, h, _ in bands:
        poly = polygon_offset(out, inset) if inset > 0 else out
        rings.append([bm.verts.new((u, -(h + bulge(u, v)), v)) for (u, v) in poly])
    inner = polygon_offset(out, 0.150)
    for s in (0.84, 0.68, 0.52, 0.36, 0.2):
        rings.append([bm.verts.new((cu + (u - cu) * s, -(0.012 + bulge(cu + (u - cu) * s, cv + (v - cv) * s)),
                                    cv + (v - cv) * s)) for (u, v) in inner])
        bands.append((None, None, 0))
    center = bm.verts.new((cu, -(0.012 + bulge(cu, cv)), cv))
    for k in range(len(rings) - 1):
        A, B = rings[k], rings[k + 1]
        mat = bands[k][2] if k < len(bands) else 0
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((A[i], B[i], B[j], A[j])).material_index = mat
    for i in range(n):
        bm.faces.new((rings[-1][i], center, rings[-1][(i + 1) % n])).material_index = 0
    # back shell and side wall
    back = [bm.verts.new((u, 0.05 - bulge(u, v), v)) for (u, v) in out]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((rings[0][j], back[j], back[i], rings[0][i])).material_index = 1
    bm.faces.new(back).material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = finish_bmesh(bm, "Shield_Body", coll, [M.get("shield_lacquer"), M.get("iron"), M.get("gold")],
                      sharp_angle=math.radians(28), parent=parent)
    return ob, out


def _on_face(u, v, lift):
    return Vector((u, -(0.012 + bulge(u, v) + lift), v))


def _blade(bm, b, t, width, ridge, widest=0.3):
    """Kite-shaped faceted blade lying on the shield face from b to t (2D shield coords)."""
    b2, t2 = Vector(b), Vector(t)
    d = (t2 - b2)
    side = Vector((-d.y, d.x)).normalized()
    w = b2 + d * widest
    L, R = w - side * width / 2, w + side * width / 2
    pts = [b2, R, t2, L]
    base = [bm.verts.new(_on_face(p.x, p.y, 0.0)) for p in pts]
    top = [bm.verts.new(_on_face(p.x, p.y, 0.004)) for p in pts]
    apex = bm.verts.new(_on_face(w.x, w.y, ridge))
    ridge_hi = bm.verts.new(_on_face(b2.x + d.x * 0.62, b2.y + d.y * 0.62, ridge * 0.55))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((base[i], base[j], top[j], top[i]))
    bm.faces.new(list(reversed(base)))
    # facets: lower pair meet at the apex, upper pair run along a ridge toward the point
    bm.faces.new((top[0], top[1], apex))
    bm.faces.new((top[3], top[0], apex))
    bm.faces.new((top[1], ridge_hi, apex))
    bm.faces.new((top[1], top[2], ridge_hi))
    bm.faces.new((top[2], top[3], ridge_hi))
    bm.faces.new((top[3], apex, ridge_hi))


def _star(bm, c, up, down, side, inner, ridge):
    pts = []
    for k in range(8):
        a = math.pi / 2 + k * math.pi / 4
        r = (up if k == 0 else down if k == 4 else side if k in (2, 6) else inner)
        pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    base = [bm.verts.new(_on_face(u, v, 0.0)) for (u, v) in pts]
    apex = bm.verts.new(_on_face(c[0], c[1], ridge))
    for k in range(8):
        j = (k + 1) % 8
        bm.faces.new((base[k], base[j], apex))
    bm.faces.new(list(reversed(base)))


def _crown(coll, parent):
    gold = M.get("gold")
    bm = bmesh.new()
    blades = [((0.0, -0.32), (0.0, 0.62), 0.15), ((-0.20, -0.34), (-0.37, 0.46), 0.13),
              ((0.20, -0.34), (0.37, 0.46), 0.13), ((-0.39, -0.39), (-0.67, 0.17), 0.11),
              ((0.39, -0.39), (0.67, 0.17), 0.11)]
    for b, t, w in blades:
        _blade(bm, b, t, w, 0.05)
    _star(bm, (0.0, 0.84), 0.17, 0.11, 0.11, 0.035, 0.05)
    # circlet: an ellipse whose front arc stands proud of the back arc, reading as a 3D crown band
    path = []
    for k in range(96):
        a = 2 * math.pi * k / 96
        u, v = 0.53 * math.cos(a), -0.44 + 0.115 * math.sin(a)
        path.append(_on_face(u, v, 0.045 - 0.028 * math.sin(a)))
    t0 = (path[1] - path[-1]).normalized()
    # u (band height) stays in the shield plane, v (thickness) points out of it
    sweep(bm, path, circle_profile(0.034, 14, rx=0.040, ry=0.030), normal0=Vector((0, 1, 0)).cross(t0),
          closed=True)
    for k in range(14):
        a = math.pi + math.pi * (k + 0.5) / 14
        u, v = 0.53 * math.cos(a), -0.44 + 0.115 * math.sin(a)
        p = _on_face(u, v, 0.045 - 0.028 * math.sin(a) + 0.036)
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.011, matrix=Matrix.Translation(p))
    crown = finish_bmesh(bm, "Shield_Crown_Gold", coll, [M.get("gold_emblem")], sharp_angle=math.radians(30),
                         parent=parent)
    bm = bmesh.new()
    for (u, v) in ((-0.27, -0.545), (0.0, -0.565), (0.27, -0.545)):
        p = _on_face(u, v, 0.075)
        bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=0.042,
                                  matrix=Matrix.Translation(p) @ Matrix.Diagonal((1.0, 0.5, 1.15, 1.0)))
    jewels = finish_bmesh(bm, "Shield_Crown_Rubies", coll, [M.get("ruby")], smooth=True, parent=parent)
    return crown, jewels


def _vine(bm, out, s0, s1, seed, thorn_every=0.045):
    """Thorny vine meandering along the rim between arc-length fractions s0..s1 of the outline."""
    rnd = random.Random(seed)
    n = len(out)
    pts = [Vector(p) for p in out]
    cum = [0.0]
    for i in range(1, n + 1):
        cum.append(cum[-1] + (pts[i % n] - pts[i - 1]).length)
    total = cum[-1]

    def at(s):
        d = (s % 1.0) * total
        for i in range(n):
            if cum[i + 1] >= d:
                t = (d - cum[i]) / max(cum[i + 1] - cum[i], 1e-9)
                a, b = pts[i], pts[(i + 1) % n]
                e = (b - a).normalized()
                return a.lerp(b, t), Vector((e.y, -e.x))  # outward normal for a CCW outline
        return pts[0], Vector((0, 1))

    steps = int(abs(s1 - s0) * total / 0.012)
    path = []
    for k in range(steps + 1):
        s = s0 + (s1 - s0) * k / steps
        p, nrm = at(s)
        ph = 2 * math.pi * (s * total) / 0.42
        radial = -0.035 + 0.06 * math.sin(ph + seed)
        u, v = p.x + nrm.x * radial, p.y + nrm.y * radial
        lift = 0.085 + 0.02 * math.cos(ph * 1.7 + seed)  # rim top sits at 0.048: keep the vine clear of it
        path.append(Vector((u, -(lift + max(bulge(u, v), 0.0)), v)))
    rings = sweep(bm, path, circle_profile(0.011, 8), normal0=Vector((0, -1, 0)), caps=True,
                  scale_fn=lambda t: 0.55 + 0.45 * math.sin(math.pi * min(max(t, 0.02), 0.98)))
    L = 0.0
    nxt = rnd.uniform(0.0, thorn_every)
    for k in range(1, len(path)):
        seg = (path[k] - path[k - 1]).length
        L += seg
        if L < nxt:
            continue
        nxt = L + thorn_every * rnd.uniform(0.7, 1.3)
        T = (path[k] - path[k - 1]).normalized()
        a = rnd.uniform(0, 2 * math.pi)
        side = T.cross(Vector((0, -1, 0)))
        if side.length < 1e-5:
            side = T.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(T)
        d = (side * math.cos(a) + up * math.sin(a)) * 0.85 + T * 0.35
        length = rnd.uniform(0.03, 0.06)
        _thorn(bm, path[k], d.normalized(), length, 0.0075)


def _thorn(bm, base, d, length, radius, segs=6):
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-5:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    up = side.cross(d)
    ring = [bm.verts.new(base + (side * math.cos(2 * math.pi * i / segs) + up * math.sin(2 * math.pi * i / segs))
                         * radius) for i in range(segs)]
    tip = bm.verts.new(base + d * length)
    for i in range(segs):
        bm.faces.new((ring[i], ring[(i + 1) % segs], tip))


def build(root_coll, location, tilt_deg=3.0):
    coll = collection("Shield", root_coll)
    root = empty("SHIELD_Root", coll, location, display="ARROWS", size=0.4)
    root.rotation_euler = (math.radians(tilt_deg), 0, 0)
    body, out = _shield_body(coll, root)
    crown, jewels = _crown(coll, root)
    bm = bmesh.new()
    _vine(bm, out, 0.27, 0.50, 1.3)   # upper right flank, round the corner and along the top
    _vine(bm, out, 0.86, 1.07, 4.1)   # lower left flank, past the tip
    vines = finish_bmesh(bm, "Shield_Thorn_Vines", coll, [M.get("thorn")], sharp_angle=math.radians(50), parent=root)
    return dict(collection=coll, root=root, body=body, crown=crown, jewels=jewels, vines=vines)
