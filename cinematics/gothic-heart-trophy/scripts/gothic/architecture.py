"""Cathedral architecture: floor, dais, altar, piers, arcades, traceried windows, vaults and reredos.

Coordinate system: the trophy stands on the altar at the origin, the nave runs along -Y toward the
west door, the apse is at +Y. Units are metres."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import materials as M
from .util import (box, circle_profile, collection, finish_bmesh, frame_matrix, lancet_outline, lathe,
                   linked_copy, pointed_arch, rect_profile, sweep)

PIER_X = 4.5
PIER_Y = [5.7, 1.5, -2.7, -6.9, -11.1, -15.3, -19.5, -23.7, -27.9]
BAYS = [(PIER_Y[i] + PIER_Y[i + 1]) / 2.0 for i in range(len(PIER_Y) - 1)]
AISLE_X = 8.5          # inner face of the aisle walls
WALL_T = 1.0
APSE_Y = 8.5           # inner face of the east (apse) wall
WEST_Y = -30.0         # inner face of the west wall
CAP_Z = 8.6            # top of pier capitals / arch springing
AISLE_ROOF_Z = 12.5
CLERE_X = 4.5
CLERE_T = 0.7
VAULT_Z = 19.5
DAIS_R = (3.4, 3.0)    # circumradius of the two octagonal steps
DAIS_TOP = 0.32
ALTAR_TOP = 1.27
REREDOS_Y = 3.9        # front face of the reredos
NICHE_W, NICHE_RF, NICHE_SPRING, NICHE_SILL = 2.7, 0.72, 2.9, 1.05
SIDE_ARCH_X = (-2.5, -1.95, 1.95, 2.5)

WINDOW_TYPES = {
    "aisle": dict(width=2.2, sill=2.2, spring=8.0),
    "clere": dict(width=1.6, sill=13.4, spring=17.0),
    "apse_c": dict(width=2.4, sill=5.6, spring=12.4),
    "apse_s": dict(width=1.8, sill=2.6, spring=9.8),
    "apse_a": dict(width=1.6, sill=3.0, spring=8.4),
}


# ----------------------------------------------------------------------------- helpers

def _wall_frame(origin, interior):
    """Window frame: local x along the wall, local z up, local -y toward the interior."""
    y_axis = -Vector(interior).normalized()
    x_axis = y_axis.cross(Vector((0, 0, 1)))
    return frame_matrix(origin, x_axis, y_axis)


def _apply_boolean(ob, cutter_ob):
    mod = ob.modifiers.new("Cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter_ob
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    old = ob.data
    ob.modifiers.remove(mod)
    ob.data = me
    me.name = old.name
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cutter_ob, do_unlink=True)


def _cutter_object(coll, prisms):
    """prisms: list of (matrix, outline[(x,z)], y0, y1) -> one joined manifold cutter object."""
    bm = bmesh.new()
    for (mat, outline, y0, y1) in prisms:
        front = [bm.verts.new(mat @ Vector((x, y0, z))) for (x, z) in outline]
        back = [bm.verts.new(mat @ Vector((x, y1, z))) for (x, z) in outline]
        n = len(outline)
        bm.faces.new(front)
        bm.faces.new(list(reversed(back)))
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((front[j], front[i], back[i], back[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return finish_bmesh(bm, "Cutter", coll)


def _planar_path(points2d):
    return [Vector((x, 0.0, z)) for (x, z) in points2d]


def _sweep_planar(bm, pts2d, profile, closed=False, y=0.0, mat=0, caps=True):
    path = [Vector((x, y, z)) for (x, z) in pts2d]
    if closed:
        t0 = (path[1] - path[-1]).normalized()
    else:
        t0 = (path[1] - path[0]).normalized()
    n0 = Vector((0, 1, 0)).cross(t0)
    return sweep(bm, path, profile, normal0=n0, closed=closed, caps=caps, mat=mat)


def _circle2d(cx, cz, r, n=40):
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ----------------------------------------------------------------------------- floor, dais, carpet

def build_floor(coll):
    bm = bmesh.new()
    xs, ys = (-AISLE_X - 0.2, AISLE_X + 0.2), (WEST_Y - 0.3, APSE_Y + 0.3)
    v = [bm.verts.new((xs[0], ys[0], 0)), bm.verts.new((xs[1], ys[0], 0)),
         bm.verts.new((xs[1], ys[1], 0)), bm.verts.new((xs[0], ys[1], 0))]
    bm.faces.new(v)
    floor = finish_bmesh(bm, "Floor_Nave", coll, [M.get("stone_floor")])

    # carpet runner leading up the nave to the dais (local X spans the runner width)
    bm = bmesh.new()
    front_y = -DAIS_R[0] * math.cos(math.pi / 8) - 0.02
    prof = [(-1.1, 0.0), (1.1, 0.0), (1.1, 0.010), (1.085, 0.014), (-1.085, 0.014), (-1.1, 0.010)]
    ys_list = [WEST_Y + 0.5 + i * (front_y - WEST_Y - 0.5) / 24 for i in range(25)]
    rings = []
    for yy in ys_list:
        rings.append([bm.verts.new((x, yy, z)) for (x, z) in prof])
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        for j in range(len(prof)):
            k = (j + 1) % len(prof)
            bm.faces.new((A[j], A[k], B[k], B[j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    carpet = finish_bmesh(bm, "Carpet_Runner", coll, [M.get("carpet")], sharp_angle=math.radians(40))
    return floor, carpet


def build_dais(coll):
    bm = bmesh.new()
    r1, r2 = DAIS_R
    prof = [(r1, 0.0), (r1, 0.145), (r1 - 0.015, 0.16), (r2, 0.16), (r2, 0.305), (r2 - 0.015, DAIS_TOP),
            (0.0, DAIS_TOP)]
    lathe(bm, prof, 8, angle_offset=math.pi / 8, cap_bottom=False)
    return finish_bmesh(bm, "Dais_Steps", coll, [M.get("stone_slate")], sharp_angle=math.radians(30))


# ----------------------------------------------------------------------------- altar

def build_altar(coll):
    marble, gold = M.get("marble"), M.get("gold")
    bm = bmesh.new()
    z0 = DAIS_TOP
    box(bm, (0, 0, z0 + 0.05), (2.02, 1.27, 0.10))           # plinth
    box(bm, (0, 0, z0 + 0.115), (1.92, 1.17, 0.03))          # plinth fillet
    box(bm, (0, 0, (z0 + 0.13 + 1.17) / 2.0), (1.80, 1.05, 1.17 - z0 - 0.13))  # body
    box(bm, (0, 0, 1.155), (1.9, 1.15, 0.03))                # top bed moulding
    box(bm, (0, 0, ALTAR_TOP - 0.05), (2.04, 1.24, 0.10))    # mensa (top slab)
    altar = finish_bmesh(bm, "Altar_Marble", coll, [marble], sharp_angle=math.radians(30))
    bev = altar.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.008
    bev.segments = 2
    bev.limit_method = "ANGLE"

    # gilded blind arcade on the front face: three pointed arches on slender colonnettes
    bm = bmesh.new()
    face_y = -0.525 - 0.012
    prof = circle_profile(0.011, 10)
    for cx in (-0.56, 0.0, 0.56):
        arch, h = pointed_arch(0.44, 0.72, 14)
        spring = 0.80
        pts = [(cx - 0.22, z0 + 0.16)] + [(cx + x, spring + y) for (x, y) in arch] + [(cx + 0.22, z0 + 0.16)]
        _sweep_planar(bm, pts, prof, y=face_y)
        # capitals on the colonnettes
        for sx in (-0.22, 0.22):
            lathe(bm, [(0.0, spring - 0.035), (0.022, spring - 0.03), (0.026, spring - 0.005), (0.0, spring)],
                  12, center=(cx + sx, face_y, 0.0))
    # central quatrefoil medallion with a ruby heart cabochon
    qc = (0.0, 0.70)
    for (ox, oz) in ((0.055, 0), (-0.055, 0), (0, 0.055), (0, -0.055)):
        _sweep_planar(bm, _circle2d(qc[0] + ox, qc[1] + oz, 0.06, 28), circle_profile(0.008, 8), closed=True,
                      y=face_y - 0.004)
    _sweep_planar(bm, _circle2d(qc[0], qc[1], 0.14, 48), circle_profile(0.009, 8), closed=True, y=face_y - 0.004)
    arcade = finish_bmesh(bm, "Altar_Gilded_Arcade", coll, [gold], smooth=True)

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=0.035,
                              matrix=Matrix.Translation((0, face_y - 0.004, qc[1])) @ Matrix.Diagonal((1, 0.45, 1, 1)))
    gem = finish_bmesh(bm, "Altar_Cabochon", coll, [M.get("ruby")], smooth=True)
    return altar, arcade, gem


# ----------------------------------------------------------------------------- piers and arcades

def build_pier_mesh(coll):
    bm = bmesh.new()
    lathe(bm, [(0.92, 0.0), (0.92, 0.40), (0.88, 0.45), (0.0, 0.45)], 8, angle_offset=math.pi / 8, cap_bottom=False)
    lathe(bm, [(0.76, 0.45), (0.76, 0.50), (0.72, 0.55), (0.66, 0.57), (0.66, 0.60), (0.58, 0.64), (0.0, 0.64)],
          32, cap_bottom=False)
    lathe(bm, [(0.50, 0.62), (0.50, 7.92)], 32, cap_bottom=False, cap_top=False)
    for k in range(8):
        a = k * math.pi / 4
        major = k % 2 == 0
        r, d = (0.14, 0.52) if major else (0.085, 0.53)
        c = (d * math.cos(a), d * math.sin(a), 0.0)
        lathe(bm, [(r + 0.035, 0.62), (r + 0.035, 0.68), (r, 0.72), (r, 7.86), (r + 0.03, 7.90),
                   (r + 0.03, 7.94)], 16, center=c, cap_bottom=False, cap_top=False)
    lathe(bm, [(0.60, 7.90), (0.66, 7.96), (0.76, 8.16), (0.88, 8.34), (0.92, 8.42), (0.0, 8.42)], 32,
          cap_bottom=False)
    lathe(bm, [(1.04, 8.40), (1.04, 8.52), (1.0, CAP_Z), (0.0, CAP_Z)], 8, angle_offset=math.pi / 8)
    return finish_bmesh(bm, "Pier_Clustered", coll, [M.get("stone_carved")], sharp_angle=math.radians(35))


def build_piers(coll):
    proto = build_pier_mesh(coll)
    proto.location = (-PIER_X, PIER_Y[0], 0)
    proto.name = "Pier_L_00"
    piers = [proto]
    for side, sx in (("L", -1), ("R", 1)):
        for i, y in enumerate(PIER_Y):
            if side == "L" and i == 0:
                continue
            piers.append(linked_copy(proto, f"Pier_{side}_{i:02d}", coll, location=(sx * PIER_X, y, 0)))
    return piers


def build_arcades(coll):
    """Clerestory walls above the arcade (with arch heads and window openings cut) plus arch mouldings."""
    stone, carved = M.get("stone_wall"), M.get("stone_carved")
    windows = []
    objs = []
    for side, sx in (("L", -1), ("R", 1)):
        bm = bmesh.new()
        y0, y1 = WEST_Y - 0.2, APSE_Y + 0.2
        box(bm, (sx * CLERE_X, (y0 + y1) / 2, (CAP_Z + VAULT_Z) / 2), (CLERE_T, y1 - y0, VAULT_Z - CAP_Z))
        wall = finish_bmesh(bm, f"Clerestory_Wall_{side}", coll, [stone])
        prisms = []
        interior = Vector((-sx, 0, 0))
        for i in range(len(PIER_Y) - 1):
            ya, yb = PIER_Y[i + 1], PIER_Y[i]
            span = yb - ya
            mid = (ya + yb) / 2.0
            m = _wall_frame((sx * CLERE_X, mid, 0.0), interior)
            outline, _ = lancet_outline(span - 0.5, CAP_Z, (span - 0.25) / (span - 0.5), 18, sill=CAP_Z - 1.0)
            prisms.append((m, outline, -1.0, 1.0))
            wt = WINDOW_TYPES["clere"]
            ow, _ = lancet_outline(wt["width"], wt["spring"], 1.0, 18, sill=wt["sill"])
            prisms.append((m, ow, -1.0, 1.0))
            windows.append(dict(kind="clere", matrix=m, wall=f"clere_{side}", bay=i, interior=interior,
                                center=Vector((sx * CLERE_X, mid, 0.0)), thickness=CLERE_T))
        _apply_boolean(wall, _cutter_object(coll, prisms))
        objs.append(wall)

        # arch mouldings and vaulting shafts
        bm = bmesh.new()
        prof = rect_profile(0.42, 0.82, 0.06)
        for i in range(len(PIER_Y) - 1):
            ya, yb = PIER_Y[i + 1], PIER_Y[i]
            arch, _ = pointed_arch(yb - ya, 1.0, 22)
            m = _wall_frame((sx * CLERE_X, (ya + yb) / 2.0, 0.0), interior)
            path = [m @ Vector((x, 0.0, CAP_Z + z)) for (x, z) in arch]
            t0 = (path[1] - path[0]).normalized()
            sweep(bm, path, prof, normal0=Vector((1, 0, 0)).cross(t0), caps=True)
        for y in PIER_Y:
            lathe(bm, [(0.13, CAP_Z), (0.13, VAULT_Z)], 16, center=(sx * (CLERE_X - 0.42), y, 0.0), cap_bottom=False)
            lathe(bm, [(0.22, VAULT_Z - 0.35), (0.25, VAULT_Z - 0.2), (0.25, VAULT_Z), (0.0, VAULT_Z)], 16,
                  center=(sx * (CLERE_X - 0.42), y, 0.0), cap_bottom=False)
        objs.append(finish_bmesh(bm, f"Arcade_Mouldings_{side}", coll, [carved], sharp_angle=math.radians(40)))
    return objs, windows


# ----------------------------------------------------------------------------- outer walls, vaults

def build_walls(coll):
    stone = M.get("stone_wall")
    windows = []
    objs = []
    # aisle walls
    for side, sx in (("L", -1), ("R", 1)):
        bm = bmesh.new()
        xc = sx * (AISLE_X + WALL_T / 2)
        box(bm, (xc, (WEST_Y + APSE_Y) / 2, AISLE_ROOF_Z / 2), (WALL_T, APSE_Y - WEST_Y + 2 * WALL_T, AISLE_ROOF_Z))
        wall = finish_bmesh(bm, f"Aisle_Wall_{side}", coll, [stone])
        prisms = []
        interior = Vector((-sx, 0, 0))
        wt = WINDOW_TYPES["aisle"]
        for i, yb in enumerate(BAYS):
            m = _wall_frame((xc, yb, 0.0), interior)
            ow, _ = lancet_outline(wt["width"], wt["spring"], 1.0, 18, sill=wt["sill"])
            prisms.append((m, ow, -1.0, 1.0))
            windows.append(dict(kind="aisle", matrix=m, wall=f"aisle_{side}", bay=i, interior=interior,
                                center=Vector((xc, yb, 0.0)), thickness=WALL_T))
        _apply_boolean(wall, _cutter_object(coll, prisms))
        objs.append(wall)
        # aisle ceiling slab
        bm = bmesh.new()
        box(bm, (sx * (CLERE_X + AISLE_X) / 2, (WEST_Y + APSE_Y) / 2, AISLE_ROOF_Z + 0.25),
            (AISLE_X - CLERE_X, APSE_Y - WEST_Y, 0.5))
        objs.append(finish_bmesh(bm, f"Aisle_Ceiling_{side}", coll, [stone]))

    # east (apse) wall
    bm = bmesh.new()
    yc = APSE_Y + WALL_T / 2
    box(bm, (0, yc, (VAULT_Z + 8) / 2), (2 * (AISLE_X + WALL_T), WALL_T, VAULT_Z + 8))
    wall = finish_bmesh(bm, "Apse_Wall", coll, [stone])
    prisms = []
    interior = Vector((0, -1, 0))
    for kind, x in (("apse_c", 0.0), ("apse_s", -3.3), ("apse_s", 3.3), ("apse_a", -6.5), ("apse_a", 6.5)):
        wt = WINDOW_TYPES[kind]
        m = _wall_frame((x, yc, 0.0), interior)
        ow, _ = lancet_outline(wt["width"], wt["spring"], 1.0, 18, sill=wt["sill"])
        prisms.append((m, ow, -1.0, 1.0))
        windows.append(dict(kind=kind, matrix=m, wall="apse", bay=int(x), interior=interior,
                            center=Vector((x, yc, 0.0)), thickness=WALL_T))
    _apply_boolean(wall, _cutter_object(coll, prisms))
    objs.append(wall)

    # west wall with the great rose
    bm = bmesh.new()
    yc = WEST_Y - WALL_T / 2
    box(bm, (0, yc, (VAULT_Z + 8) / 2), (2 * (AISLE_X + WALL_T), WALL_T, VAULT_Z + 8))
    wall = finish_bmesh(bm, "West_Wall", coll, [stone])
    interior = Vector((0, 1, 0))
    m = _wall_frame((0.0, yc, 0.0), interior)
    rose = _circle2d(0.0, 12.0, 3.1, 64)
    door, _ = lancet_outline(3.2, 4.6, 1.0, 18, sill=-0.5)
    # local -y faces the nave, so the portal recess is cut from the interior face back to y=+0.25
    _apply_boolean(wall, _cutter_object(coll, [(m, rose, -1.0, 1.0), (m, door, -1.0, 0.25)]))
    windows.append(dict(kind="rose", matrix=m, wall="west", bay=0, interior=interior,
                        center=Vector((0.0, yc, 0.0)), thickness=WALL_T))
    objs.append(wall)
    # dark doors inside the west portal
    bm = bmesh.new()
    door_in, _ = lancet_outline(3.2, 4.6, 1.0, 18, sill=0.0)
    vs = [bm.verts.new(m @ Vector((x, 0.25, z))) for (x, z) in door_in]
    bm.faces.new(vs)
    objs.append(finish_bmesh(bm, "West_Doors", coll, [M.get("iron")]))
    return objs, windows


def build_vaults(coll):
    stone, carved = M.get("stone_wall"), M.get("stone_carved")
    arch, h = pointed_arch(2 * (CLERE_X + CLERE_T / 2), 0.78, 28)
    bm = bmesh.new()
    rows = []
    for y in (WEST_Y - 0.5, APSE_Y + 0.5):
        rows.append([bm.verts.new((x, y, VAULT_Z + z)) for (x, z) in arch])
    for j in range(len(arch) - 1):
        bm.faces.new((rows[0][j + 1], rows[0][j], rows[1][j], rows[1][j + 1]))
    vault = finish_bmesh(bm, "Nave_Vault", coll, [stone], smooth=True)
    bm = bmesh.new()
    rib, _ = pointed_arch(2 * CLERE_X - 0.9, 0.78 * (2 * (CLERE_X + CLERE_T / 2)) / (2 * CLERE_X - 0.9), 28)
    for y in PIER_Y:
        path = [Vector((x, y, VAULT_Z + z)) for (x, z) in rib]
        t0 = (path[1] - path[0]).normalized()
        sweep(bm, path, rect_profile(0.32, 0.36, 0.05), normal0=Vector((0, 1, 0)).cross(t0))
    ribs = finish_bmesh(bm, "Nave_Ribs", coll, [carved], sharp_angle=math.radians(40))
    return [vault, ribs]


# ----------------------------------------------------------------------------- windows (glass + tracery)

def _tracery_mesh(kind, coll):
    wt = WINDOW_TYPES[kind]
    W, S = wt["width"], wt["spring"] - wt["sill"]
    bm = bmesh.new()
    prof = rect_profile(0.10 * W / 2.2 + 0.03, 0.24, 0.025)
    # mullion
    _sweep_planar(bm, [(0.0, 0.0), (0.0, S + 0.02)], prof)
    # two lights with pointed heads
    for cx in (-W / 4, W / 4):
        arch, sh = pointed_arch(W / 2, 1.0, 14)
        _sweep_planar(bm, [(cx + x, S + y) for (x, y) in arch], prof)
    # oculus with a quatrefoil above the lights
    sub_apex = S + (W / 2) * math.sqrt(3) / 2
    _, main_h = pointed_arch(W, 1.0, 4)
    main_apex = S + main_h
    r = (main_apex - sub_apex) * 0.36
    cz = sub_apex + r + 0.04
    _sweep_planar(bm, _circle2d(0.0, cz, r, 36), prof, closed=True)
    fr = r * 0.42
    for (ox, oz) in ((fr, 0), (-fr, 0), (0, fr), (0, -fr)):
        _sweep_planar(bm, _circle2d(ox, cz + oz, fr * 0.95, 24), rect_profile(0.05, 0.16, 0.012), closed=True)
    # interior roll moulding around the opening
    outline, _ = lancet_outline(W, S, 1.0, 22)
    _sweep_planar(bm, outline, circle_profile(0.07, 10), closed=True, y=-0.36)
    for f in bm.faces:
        f.material_index = 0
    me = bpy.data.meshes.new(f"Tracery_{kind}")
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        e.smooth = len(e.link_faces) != 2 or e.calc_face_angle(0.0) < math.radians(40)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.get("stone_carved"))
    return me


def _pane_mesh(kind):
    wt = WINDOW_TYPES[kind]
    W, S = wt["width"], wt["spring"] - wt["sill"]
    outline, _ = lancet_outline(W, S, 1.0, 22)
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0.0, z)) for (x, z) in outline]
    bm.faces.new(vs)
    me = bpy.data.meshes.new(f"Glass_{kind}")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.get("stained_glass"))
    return me


def _rose_meshes():
    bm = bmesh.new()
    R = 3.1
    vs = [bm.verts.new((x, 0.0, z)) for (x, z) in _circle2d(0.0, 0.0, R + 0.05, 72)]
    bm.faces.new(vs)
    pane = bpy.data.meshes.new("Glass_rose")
    bm.to_mesh(pane)
    bm.free()
    pane.materials.append(M.get("stained_glass"))
    bm = bmesh.new()
    prof = rect_profile(0.13, 0.26, 0.03)
    for rr in (R - 0.05, 1.05, 0.5):
        _sweep_planar(bm, _circle2d(0.0, 0.0, rr, 72), prof, closed=True)
    for k in range(12):
        a = 2 * math.pi * k / 12
        ca, sa = math.cos(a), math.sin(a)
        _sweep_planar(bm, [(1.05 * ca, 1.05 * sa), ((R - 0.05) * ca, (R - 0.05) * sa)], prof)
        b = a + math.pi / 12
        _sweep_planar(bm, _circle2d(2.25 * math.cos(b), 2.25 * math.sin(b), 0.42, 28), prof, closed=True)
    for k in range(6):
        a = 2 * math.pi * k / 6
        _sweep_planar(bm, [(0.5 * math.cos(a), 0.5 * math.sin(a)), (1.05 * math.cos(a), 1.05 * math.sin(a))], prof)
    tr = bpy.data.meshes.new("Tracery_rose")
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(tr)
    bm.free()
    tr.materials.append(M.get("stone_carved"))
    return pane, tr


def build_windows(coll, windows, brightness_fn):
    """Instantiate glass panes and tracery for every window record; annotates records with objects."""
    tracery, panes = {}, {}
    rose_pane, rose_tr = _rose_meshes()
    for i, w in enumerate(windows):
        kind = w["kind"]
        if kind == "rose":
            m = w["matrix"] @ Matrix.Translation((0, 0, 12.0))
            pane_me, tr_me, width, sill = rose_pane, rose_tr, 6.2, 12.0
        else:
            if kind not in tracery:
                tracery[kind] = _tracery_mesh(kind, coll)
                panes[kind] = _pane_mesh(kind)
            wt = WINDOW_TYPES[kind]
            m = w["matrix"] @ Matrix.Translation((0, 0, wt["sill"]))
            pane_me, tr_me, width, sill = panes[kind], tracery[kind], wt["width"], wt["sill"]
        pane = bpy.data.objects.new(f"Window_{w['wall']}_{w['bay']:+d}_Glass", pane_me)
        pane.matrix_world = m
        coll.objects.link(pane)
        pane["glass_width"] = width
        pane["glass_brightness"] = brightness_fn(w)
        pane.visible_diffuse = False  # windows read as luminous for camera/glossy; spots do the lighting
        tro = bpy.data.objects.new(f"Window_{w['wall']}_{w['bay']:+d}_Tracery", tr_me)
        tro.matrix_world = m @ Matrix.Translation((0, -0.0, 0))
        coll.objects.link(tro)
        w["pane"], w["tracery"], w["width"], w["sill_z"] = pane, tro, width, sill
    return windows


# ----------------------------------------------------------------------------- reredos

def build_reredos(coll):
    carved, gold, stone = M.get("stone_carved"), M.get("gold"), M.get("stone_wall")
    y0, depth = REREDOS_Y, 0.7
    bm = bmesh.new()
    box(bm, (0, y0 + depth / 2, 0.175), (5.9, depth + 0.2, 0.35))
    box(bm, (0, y0 + depth / 2, (0.35 + 4.82) / 2), (5.6, depth, 4.82 - 0.35))
    box(bm, (0, y0 + depth / 2, 4.91), (5.9, depth + 0.16, 0.18))
    # gable panel above the niche
    gable = [(-1.5, 4.80), (1.5, 4.80), (0.0, 6.05)]
    gv = [bm.verts.new((x, y0 + 0.05, z)) for (x, z) in gable] + [bm.verts.new((x, y0 + 0.45, z)) for (x, z) in gable]
    bm.faces.new((gv[0], gv[1], gv[2]))
    bm.faces.new((gv[5], gv[4], gv[3]))
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((gv[j], gv[i], gv[i + 3], gv[j + 3]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    body = finish_bmesh(bm, "Reredos_Body", coll, [carved])
    m = frame_matrix((0, y0, 0), (1, 0, 0), (0, 1, 0))
    niche, _ = lancet_outline(NICHE_W, NICHE_SPRING, NICHE_RF, 26, sill=NICHE_SILL)
    prisms = [(m, niche, -0.2, 0.42)]
    for cx in SIDE_ARCH_X:
        o, _ = lancet_outline(0.42, 3.25, 1.0, 14, sill=1.75)
        prisms.append((m @ Matrix.Translation((cx, 0, 0)), o, -0.2, 0.05))
    _apply_boolean(body, _cutter_object(coll, prisms))

    def arch_path(outline):  # left sill -> left springing -> apex -> right springing -> right sill
        return [outline[0]] + list(reversed(outline[2:])) + [outline[1]]

    # mouldings: gilded roll around the niche, stone hood, side arcades, gable copings, pinnacles
    bm_g, bm_s = bmesh.new(), bmesh.new()
    roll = circle_profile(0.03, 10)
    R = NICHE_W * NICHE_RF
    outline, _ = lancet_outline(NICHE_W + 0.08, NICHE_SPRING, (R + 0.04) / (NICHE_W + 0.08), 30, sill=NICHE_SILL)
    _sweep_planar(bm_g, arch_path(outline), roll, y=y0 - 0.02)
    hood, _ = lancet_outline(NICHE_W + 0.34, NICHE_SPRING, (R + 0.17) / (NICHE_W + 0.34), 30, sill=NICHE_SPRING)
    _sweep_planar(bm_s, list(reversed(hood[2:])), rect_profile(0.14, 0.14, 0.03), y=y0 - 0.06)
    for cx in SIDE_ARCH_X:
        o, _ = lancet_outline(0.42 + 0.05, 3.25, (0.42 + 0.025) / (0.42 + 0.05), 14, sill=1.75)
        _sweep_planar(bm_g, [(cx + x, z) for (x, z) in arch_path(o)], circle_profile(0.014, 8), y=y0 - 0.012)
    cop = [(-1.62, 4.74), (0.0, 6.12), (1.62, 4.74)]
    for a, b in ((cop[0], cop[1]), (cop[1], cop[2])):
        _sweep_planar(bm_s, [a, b], rect_profile(0.16, 0.22, 0.03), y=y0 + 0.02)
    # gilded crockets climbing the gable
    for (a, b, side) in ((cop[0], cop[1], -1), (cop[2], cop[1], 1)):
        for k in range(1, 6):
            t = k / 6.0
            p = Vector((a[0] + (b[0] - a[0]) * t, y0 - 0.03, a[1] + (b[1] - a[1]) * t))
            _spike(bm_g, p, Vector((side * 0.55, 0, 0.83)), 0.13, 0.045, 0.03)
    _star(bm_g, Vector((0, y0 - 0.12, 6.32)), 0.24, 0.07, 0.05)
    _spike(bm_g, Vector((0, y0 - 0.12, 6.10)), Vector((0, 0, 1)), 0.5, 0.05, 0.05)
    # gable roundel with an eight-point star
    _sweep_planar(bm_g, _circle2d(0.0, 5.32, 0.36, 40), circle_profile(0.02, 8), closed=True, y=y0 + 0.03)
    _star(bm_g, Vector((0, y0 + 0.02, 5.32)), 0.3, 0.1, 0.04, points=8)
    # pinnacles
    for px in (-2.8, -1.62, 1.62, 2.8):
        lathe(bm_s, [(0.24, 4.95), (0.24, 5.95), (0.27, 6.0), (0.27, 6.08), (0.0, 6.9)], 4,
              angle_offset=math.pi / 4, center=(px, y0 + 0.3, 0.0), cap_bottom=False)
        bmesh.ops.create_uvsphere(bm_g, u_segments=16, v_segments=8, radius=0.055,
                                  matrix=Matrix.Translation((px, y0 + 0.3, 6.95)))
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            for h in (6.25, 6.55):
                rr = 0.27 * (6.9 - h) / 0.82
                p = Vector((px + rr * math.cos(a), y0 + 0.3 + rr * math.sin(a), h))
                _spike(bm_g, p, Vector((math.cos(a) * 0.6, math.sin(a) * 0.6, 0.8)), 0.11, 0.035, 0.025)
    # candle ledges for votives
    for sx in (-1, 1):
        box(bm_s, (sx * 2.17, y0 - 0.09, 1.34), (1.12, 0.2, 0.08))
    gilt = finish_bmesh(bm_g, "Reredos_Gilding", coll, [gold], sharp_angle=math.radians(40))
    trim = finish_bmesh(bm_s, "Reredos_Mouldings", coll, [carved], sharp_angle=math.radians(40))

    # crimson velvet drape behind the shield and its gilded rod
    bm = bmesh.new()
    nx, nz = 96, 28
    x0, x1, z0, z1 = -NICHE_W / 2 + 0.03, NICHE_W / 2 - 0.03, NICHE_SILL + 0.01, NICHE_SPRING - 0.02
    yb = y0 + 0.40
    grid = []
    for j in range(nz + 1):
        z = z0 + (z1 - z0) * j / nz
        row = []
        top = (z - z0) / (z1 - z0)
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            fold = 0.034 * math.sin(x * 2 * math.pi * 3.1 + 0.6 * math.sin(z * 2.3)) * (0.55 + 0.45 * top)
            fold += 0.012 * math.sin(x * 2 * math.pi * 7.3 + 1.3)
            row.append(bm.verts.new((x, yb - 0.04 - fold, z)))
        grid.append(row)
    for j in range(nz):
        for i in range(nx):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    drape = finish_bmesh(bm, "Reredos_Drape", coll, [M.get("velvet")], smooth=True)
    bm = bmesh.new()
    rx = NICHE_W / 2 + 0.01
    _sweep_planar(bm, [(-rx, z1 + 0.03), (rx, z1 + 0.03)], circle_profile(0.018, 12), y=yb - 0.08)
    for sx in (-1, 1):
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.035,
                                  matrix=Matrix.Translation((sx * (rx + 0.01), yb - 0.08, z1 + 0.03)))
    rod = finish_bmesh(bm, "Reredos_Drape_Rod", coll, [gold], smooth=True)
    return [body, gilt, trim, drape, rod]


def _spike(bm, base, direction, length, width, depth):
    d = direction.normalized()
    side = d.cross(Vector((0, 1, 0)))
    if side.length < 1e-4:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    dep = side.cross(d).normalized()
    mid = base + d * length * 0.22
    ring = [bm.verts.new(mid + side * width / 2), bm.verts.new(mid + dep * depth / 2),
            bm.verts.new(mid - side * width / 2), bm.verts.new(mid - dep * depth / 2)]
    tip = bm.verts.new(base + d * length)
    root = bm.verts.new(base - d * length * 0.08)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((ring[i], ring[j], tip))
        bm.faces.new((ring[j], ring[i], root))


def _star(bm, center, outer, inner, depth, points=4):
    """Faceted star in the XZ plane facing -Y (front apex raised toward the viewer)."""
    n = points * 2
    ring = []
    for k in range(n):
        a = math.pi / 2 + 2 * math.pi * k / n
        r = outer if k % 2 == 0 else inner
        ring.append(bm.verts.new(center + Vector((r * math.cos(a), 0, r * math.sin(a)))))
    front = bm.verts.new(center + Vector((0, -depth, 0)))
    back = bm.verts.new(center + Vector((0, depth * 0.6, 0)))
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((ring[j], ring[k], front))
        bm.faces.new((ring[k], ring[j], back))


def window_brightness(w):
    """Emission strength of each window: sunlit south aisle and apse glow hotter than the shaded side."""
    return {"aisle_L": 4.5, "clere_L": 4.0, "apse": 5.5, "west": 3.0}.get(w["wall"], 1.8)


def build(root):
    coll = collection("Architecture", root)
    floor, carpet = build_floor(coll)
    dais = build_dais(coll)
    altar = build_altar(coll)
    piers = build_piers(coll)
    arcades, clere_windows = build_arcades(coll)
    walls, wall_windows = build_walls(coll)
    vaults = build_vaults(coll)
    reredos = build_reredos(coll)
    windows = build_windows(collection("Windows", root), wall_windows + clere_windows, window_brightness)
    return dict(collection=coll, windows=windows, floor=floor, carpet=carpet, dais=dais, altar=altar,
                piers=piers, reredos=reredos)
