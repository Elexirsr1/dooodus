"""The centerpiece: a polished silver trophy crowned by a faceted ruby heart and a sunburst of blades."""
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import materials as M
from .util import FONT_DIR, bevel, circle_profile, collection, empty, finish_bmesh, frame_matrix, lathe, subsurf, sweep

HEART_Z = 0.715          # heart origin above the trophy base (local)
HEART_SCALE = 0.25 / 32  # classic heart curve is 32 units wide -> 25 cm
SPIKE_CENTER = Vector((0.0, 0.066, HEART_Z + 0.005))  # just behind the gem's back table (y=0.046)


def heart_outline(n=28, scale=HEART_SCALE):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * scale, y * scale))
    # k=0 is the cleft at the top; reverse so the outline runs counter-clockwise viewed from the front
    return pts


def faceted_heart(bm, n=28, scale=HEART_SCALE, depth=0.046, crown=0.030, girdle=0.002, z=0.0,
                  crown_scale=0.66, table_scale=0.34):
    """Brilliant-style faceted heart in the XZ plane (front faces -Y)."""
    out = heart_outline(n, scale)
    cx = sum(p[0] for p in out) / n
    cz = sum(p[1] for p in out) / n
    mids = [((out[i][0] + out[(i + 1) % n][0]) / 2, (out[i][1] + out[(i + 1) % n][1]) / 2) for i in range(n)]

    def ring(points, s, y):
        return [bm.verts.new((cx + (px - cx) * s, y, z + cz + (pz - cz) * s)) for (px, pz) in points]

    gf, gb = ring(out, 1.0, -girdle), ring(out, 1.0, girdle)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((gf[i], gf[j], gb[j], gb[i]))
    for sign, g in ((-1, gf), (1, gb)):
        c = ring(mids, crown_scale, sign * crown)
        t = ring(out, table_scale, sign * depth)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((g[i], g[j], c[i]))
            bm.faces.new((g[j], c[j], c[i]))
            bm.faces.new((c[i], c[j], t[j]))
            bm.faces.new((c[i], t[j], t[i]))
        bm.faces.new(t if sign > 0 else list(reversed(t)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return out


def blade(bm, base, direction, length, width, depth, widest=0.22, root=0.06, front=Vector((0, -1, 0))):
    """Four-sided double pyramid: a crisp faceted spike."""
    d = direction.normalized()
    side = d.cross(front)
    if side.length < 1e-6:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    dep = side.cross(d).normalized()
    mid = base + d * length * widest
    ring = [bm.verts.new(mid + side * width / 2), bm.verts.new(mid + dep * depth / 2),
            bm.verts.new(mid - side * width / 2), bm.verts.new(mid - dep * depth / 2)]
    tip = bm.verts.new(base + d * length)
    rt = bm.verts.new(base - d * length * root)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((ring[i], ring[j], tip))
        bm.faces.new((ring[j], ring[i], rt))


def star3d(bm, center, rx, ry, inner, depth, points=4, rotation=0.0):
    """Faceted bi-pyramidal star in the XZ plane (apex front and back)."""
    n = points * 2
    ring = []
    for k in range(n):
        a = math.pi / 2 + rotation + 2 * math.pi * k / n
        if k % 2 == 0:
            r_x, r_z = rx, ry
        else:
            r_x = r_z = inner
        ring.append(bm.verts.new(center + Vector((r_x * math.cos(a), 0, r_z * math.sin(a)))))
    f = bm.verts.new(center + Vector((0, -depth, 0)))
    b = bm.verts.new(center + Vector((0, depth, 0)))
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((ring[j], ring[k], f))
        bm.faces.new((ring[k], ring[j], b))


def _base(coll, root, silver):
    bm = bmesh.new()
    prof = [(0.235, 0.000), (0.235, 0.028), (0.229, 0.034), (0.213, 0.034), (0.213, 0.054), (0.207, 0.060),
            (0.192, 0.060), (0.168, 0.198), (0.183, 0.201), (0.188, 0.206), (0.188, 0.217), (0.182, 0.224),
            (0.172, 0.226), (0.074, 0.296), (0.074, 0.310), (0.066, 0.318), (0.0, 0.318)]
    lathe(bm, prof, 8, angle_offset=math.pi / 8)
    # pyramidal studs on the lower step, one per octagon corner
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        c = Vector((0.221 * math.cos(a), 0.221 * math.sin(a), 0.034))
        blade(bm, c, Vector((0, 0, 1)), 0.022, 0.016, 0.016, widest=0.18, root=0.0)
    ob = finish_bmesh(bm, "Trophy_Base", coll, [silver], parent=root)
    bevel(ob, 0.0014, 1, 25)

    # bead moulding along the cornice
    bm = bmesh.new()
    R = 0.192
    corners = [Vector((R * math.cos(math.pi / 8 + k * math.pi / 4), R * math.sin(math.pi / 8 + k * math.pi / 4),
                       0.2115)) for k in range(8)]
    for k in range(8):
        a, b = corners[k], corners[(k + 1) % 8]
        for s in range(9):
            p = a.lerp(b, (s + 0.5) / 9)
            bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.0042, matrix=Matrix.Translation(p))
    beads = finish_bmesh(bm, "Trophy_Beads", coll, [silver], smooth=True, parent=root)
    return ob, beads


def _plaque(coll, root, silver, enamel):
    tilt = math.atan2(0.192 - 0.168, 0.198 - 0.060)
    zc = 0.129
    rc = 0.192 - (0.192 - 0.168) * (zc - 0.060) / 0.138
    apothem = rc * math.cos(math.pi / 8)
    up = Vector((0, math.sin(tilt), math.cos(tilt)))
    outward = Vector((0, -math.cos(tilt), math.sin(tilt)))
    center = Vector((0, -apothem, zc))
    mtx = frame_matrix(center, (1, 0, 0), up)  # local x right, local y up the face, local z out of the face
    bm = bmesh.new()
    w, h, t = 0.112, 0.088, 0.004
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    lo = [bm.verts.new(mtx @ Vector((x, y, 0.0))) for (x, y) in pts]
    hi = [bm.verts.new(mtx @ Vector((x, y, t))) for (x, y) in pts]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    panel = finish_bmesh(bm, "Trophy_Plaque", coll, [enamel], parent=root)
    bm = bmesh.new()
    rr, hw, hh = 0.006, w * 0.52, h * 0.53
    rounded = []
    for (cx, cy, a0) in ((hw - rr, -hh + rr, -90), (hw - rr, hh - rr, 0), (-hw + rr, hh - rr, 90),
                         (-hw + rr, -hh + rr, 180)):
        for s in range(7):
            a = math.radians(a0 + 90 * s / 6)
            rounded.append(mtx @ Vector((cx + rr * math.cos(a), cy + rr * math.sin(a), t)))
    sweep(bm, rounded, circle_profile(0.0022, 8), normal0=outward, closed=True)
    border = finish_bmesh(bm, "Trophy_Plaque_Border", coll, [silver], smooth=True, parent=root)

    font_path = os.path.join(FONT_DIR, "UnifrakturMaguntia-Book.ttf")
    font = bpy.data.fonts.load(font_path, check_existing=True)
    cu = bpy.data.curves.new("Trophy_Plaque_Text", "FONT")
    cu.body = "Slay"
    cu.font = font
    cu.size = 0.046
    cu.extrude = 0.0012
    cu.bevel_depth = 0.0004
    cu.bevel_resolution = 1
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.resolution_u = 6
    txt = bpy.data.objects.new("Trophy_Plaque_Text", cu)
    coll.objects.link(txt)
    txt.parent = root
    # parent inverse is identity, so the basis is expressed directly in trophy-local space
    txt.matrix_basis = mtx @ Matrix.Translation((0, -0.002, t + 0.0012))
    txt.data.materials.append(silver)
    return panel, border, txt


def _stem(coll, root, silver, enamel):
    z0, z1 = 0.318, 0.596
    bm = bmesh.new()
    rings = []
    steps = 14
    for k in range(steps + 1):
        t = k / steps
        z = z0 + (z1 - z0) * t
        a = 0.017 + 0.045 * (1 - t) ** 1.6
        b = 0.013 + 0.032 * (1 - t) ** 1.6
        c = 0.0065 - 0.003 * t
        corners = [Vector((0, -b)), Vector((a, 0)), Vector((0, b)), Vector((-a, 0))]
        pts = []
        for i in range(4):
            cur, prv, nxt = corners[i], corners[i - 1], corners[(i + 1) % 4]
            pts.append(cur + (prv - cur).normalized() * c)
            pts.append(cur + (nxt - cur).normalized() * c)
        rings.append([bm.verts.new((p.x, p.y, z)) for p in pts])
    for k in range(steps):
        A, B = rings[k], rings[k + 1]
        for i in range(8):
            j = (i + 1) % 8
            f = bm.faces.new((A[i], A[j], B[j], B[i]))
            f.material_index = 0 if i % 2 == 0 else 1
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    stem = finish_bmesh(bm, "Trophy_Stem", coll, [silver, enamel], parent=root)
    bevel(stem, 0.0008, 1, 25)
    # collar rings and the claw cup that receives the heart tip
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.316), (0.068, 0.316), (0.072, 0.320), (0.072, 0.326), (0.060, 0.332), (0.0, 0.332)], 8,
          angle_offset=math.pi / 8)
    lathe(bm, [(0.0, 0.578), (0.022, 0.580), (0.028, 0.590), (0.027, 0.598), (0.018, 0.602), (0.0, 0.602)], 8,
          angle_offset=math.pi / 8)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        p = Vector((0.022 * math.cos(a), 0.016 * math.sin(a), 0.594))
        blade(bm, p, Vector((math.cos(a) * 0.5, math.sin(a) * 0.35, 1.0)), 0.04, 0.008, 0.006, widest=0.25,
              root=0.05)
    cup = finish_bmesh(bm, "Trophy_Collars", coll, [silver], parent=root)
    bevel(cup, 0.0008, 1, 25)
    return stem, cup


def _heart(coll, root, silver):
    bm = bmesh.new()
    outline = faceted_heart(bm, z=HEART_Z)
    gem = finish_bmesh(bm, "Trophy_Heart_Ruby", coll, [M.get("ruby")], parent=root)
    gem.visible_shadow = False  # lets the internal red light escape onto the silverwork
    bm = bmesh.new()
    faceted_heart(bm, scale=HEART_SCALE * 0.48, depth=0.019, crown=0.014, girdle=0.004, z=HEART_Z - 0.008,
                  crown_scale=0.7, table_scale=0.45)
    core = finish_bmesh(bm, "Trophy_Heart_Core", coll, [M.get("gem_core")], smooth=True, parent=root)
    subsurf(core, 2)
    core.visible_shadow = False
    core.visible_diffuse = False
    core.visible_glossy = False

    # silver bezel hugging the girdle, studded with beads front and back
    bm = bmesh.new()
    n = len(outline)
    cx = sum(p[0] for p in outline) / n
    cz = sum(p[1] for p in outline) / n
    path = []
    for (x, z) in outline:
        v = Vector((x - cx, z - cz))
        path.append(Vector((x + v.normalized().x * 0.0035, 0.0, HEART_Z + z + v.normalized().y * 0.0035)))
    sweep(bm, path, [(-0.0045, -0.0072), (0.0045, -0.0072), (0.0045, 0.0072), (-0.0045, 0.0072)],
          normal0=Vector((0, 1, 0)).cross((path[1] - path[-1]).normalized()), closed=True)
    for k in range(0, n, 2):
        if k in (0, n // 2):
            continue
        for y in (-0.0085, 0.0085):
            p = Vector((path[k].x, y, path[k].z))
            bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.0048, matrix=Matrix.Translation(p))
    bezel = finish_bmesh(bm, "Trophy_Heart_Bezel", coll, [silver], sharp_angle=math.radians(50), parent=root)
    return gem, core, bezel


def _sunburst(coll, root, silver):
    bm = bmesh.new()
    spikes = [  # (angle from vertical in degrees, length, width, depth)
        (0, 0.43, 0.050, 0.032),
        (22.5, 0.25, 0.030, 0.021), (45, 0.345, 0.046, 0.030), (67.5, 0.235, 0.029, 0.020),
        (90, 0.305, 0.043, 0.028), (112.5, 0.20, 0.027, 0.019), (135, 0.225, 0.036, 0.024),
    ]
    for ang, L, w, d in spikes:
        for s in ((1,) if ang == 0 else (1, -1)):
            a = math.radians(ang) * s
            direction = Vector((math.sin(a), 0, math.cos(a)))
            blade(bm, SPIKE_CENTER + direction * 0.02, direction, L, w, d, widest=0.24, root=0.05)
    star3d(bm, SPIKE_CENTER + Vector((0, -0.006, 0.305)), 0.072, 0.086, 0.019, 0.022)
    star3d(bm, SPIKE_CENTER + Vector((0, -0.004, 0.305)), 0.036, 0.036, 0.012, 0.015, rotation=math.pi / 4)
    burst = finish_bmesh(bm, "Trophy_Sunburst", coll, [silver], parent=root)
    bevel(burst, 0.0011, 1, 20)
    return (burst,)


def build(root_coll, location):
    coll = collection("Trophy", root_coll)
    root = empty("TROPHY_Root", coll, location, display="ARROWS", size=0.3)
    silver, enamel = M.get("silver"), M.get("black_enamel")
    parts = []
    parts += _base(coll, root, silver)
    parts += _plaque(coll, root, silver, enamel)
    parts += _stem(coll, root, silver, enamel)
    parts += _heart(coll, root, silver)
    parts += _sunburst(coll, root, silver)
    heart_world = Vector(location) + Vector((0, 0, HEART_Z - 0.01))
    return dict(collection=coll, root=root, parts=parts, heart=heart_world,
                top=Vector(location) + Vector((0, 0, HEART_Z + 0.44)))
