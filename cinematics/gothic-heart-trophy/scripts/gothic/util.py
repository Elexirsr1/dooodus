"""Shared helpers for the Gothic Heart Trophy scene: collections, bmesh builders, node trees, keyframes."""
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEX_DIR = os.path.join(ROOT, "assets", "textures")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")


# ----------------------------------------------------------------------------- scene / collections

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "GothicHeart"
    return scene


def collection(name, parent=None):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(coll)
    return coll


def empty(name, coll, location=(0, 0, 0), display="PLAIN_AXES", size=0.25, parent=None):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = display
    ob.empty_display_size = size
    ob.location = location
    coll.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def set_visibility(ob, camera=True, diffuse=True, glossy=True, transmission=True, scatter=True, shadow=True):
    ob.visible_camera = camera
    ob.visible_diffuse = diffuse
    ob.visible_glossy = glossy
    ob.visible_transmission = transmission
    ob.visible_volume_scatter = scatter
    ob.visible_shadow = shadow


# ----------------------------------------------------------------------------- mesh construction

def finish_bmesh(bm, name, coll, materials=(), smooth=False, sharp_angle=None, location=(0, 0, 0),
                 parent=None, recalc_normals=False, data=None):
    """Write a bmesh into a new object. sharp_angle (radians) marks edges sharp above that angle."""
    if recalc_normals:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if sharp_angle is not None:
        smooth = True
        for e in bm.edges:
            if len(e.link_faces) == 2:
                e.smooth = e.calc_face_angle(0.0) < sharp_angle
            else:
                e.smooth = True
    for f in bm.faces:
        f.smooth = smooth
    me = data or bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in materials:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    coll.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def linked_copy(ob, name, coll, location=None, rotation=None, scale=None, parent=None):
    dup = bpy.data.objects.new(name, ob.data)
    coll.objects.link(dup)
    dup.location = location if location is not None else ob.location
    if rotation is not None:
        dup.rotation_euler = rotation
    if scale is not None:
        dup.scale = scale if hasattr(scale, "__len__") else (scale, scale, scale)
    if parent is not None:
        dup.parent = parent
    for mod in ob.modifiers:  # replicate simple modifiers (bevels)
        m = dup.modifiers.new(mod.name, mod.type)
        for attr in ("width", "segments", "limit_method", "angle_limit", "levels", "render_levels"):
            if hasattr(mod, attr):
                setattr(m, attr, getattr(mod, attr))
    return dup


def bevel(ob, width=0.0015, segments=1, angle=30.0):
    mod = ob.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle)
    mod.use_clamp_overlap = True
    return mod


def subsurf(ob, levels=1, render_levels=None):
    mod = ob.modifiers.new("Subdivision", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels if render_levels is None else render_levels
    return mod


def lathe(bm, profile, segments, angle_offset=0.0, center=(0.0, 0.0, 0.0), cap_bottom=True, cap_top=True,
          mat=0, radial_fn=None):
    """Revolve a (radius, z) profile (bottom to top) around Z. Returns the rings of BMVerts.

    radial_fn(angle, z, r) -> r lets callers displace the surface (melted wax, drips)."""
    cx, cy, cz = center
    rings = []
    for (r, z) in profile:
        if r <= 1e-9:
            v = bm.verts.new((cx, cy, cz + z))
            rings.append([v] * segments)
            continue
        ring = []
        for i in range(segments):
            a = angle_offset + 2.0 * math.pi * i / segments
            rr = radial_fn(a, z, r) if radial_fn else r
            ring.append(bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), cz + z)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        A, B = rings[k], rings[k + 1]
        a_pt, b_pt = A[0] is A[-1], B[0] is B[-1]
        for i in range(segments):
            j = (i + 1) % segments
            if a_pt and b_pt:
                continue
            if a_pt:
                f = bm.faces.new((A[0], B[j], B[i]))
            elif b_pt:
                f = bm.faces.new((A[i], A[j], B[0]))
            else:
                f = bm.faces.new((A[i], A[j], B[j], B[i]))
            f.material_index = mat
    if cap_bottom and rings[0][0] is not rings[0][-1]:
        bm.faces.new(list(reversed(rings[0]))).material_index = mat
    if cap_top and rings[-1][0] is not rings[-1][-1]:
        bm.faces.new(rings[-1]).material_index = mat
    return rings


def sweep(bm, path, profile, normal0=None, closed=False, caps=True, mat=0, scale_fn=None, twist=0.0):
    """Sweep a closed CCW 2D profile [(u, v)] along a 3D path using parallel-transport frames.

    u runs along the frame normal N, v along the binormal B = T x N."""
    path = [Vector(p) for p in path]
    n = len(path)
    tangents = []
    for i in range(n):
        if closed:
            t = path[(i + 1) % n] - path[(i - 1) % n]
        elif i == 0:
            t = path[1] - path[0]
        elif i == n - 1:
            t = path[-1] - path[-2]
        else:
            t = path[i + 1] - path[i - 1]
        tangents.append(t.normalized())
    t0 = tangents[0]
    ref = Vector(normal0) if normal0 is not None else (Vector((0, 0, 1)) if abs(t0.z) < 0.9 else Vector((1, 0, 0)))
    N = (ref - t0 * ref.dot(t0)).normalized()
    rings = []
    for i in range(n):
        T = tangents[i]
        if i > 0:
            q = tangents[i - 1].rotation_difference(T)
            N = q @ N
            N = (N - T * N.dot(T)).normalized()
        B = T.cross(N)
        s = scale_fn(i / max(n - 1, 1)) if scale_fn else 1.0
        tw = twist * i / max(n - 1, 1)
        ct, st = math.cos(tw), math.sin(tw)
        ring = []
        for (u, v) in profile:
            uu, vv = u * ct - v * st, u * st + v * ct
            ring.append(bm.verts.new(path[i] + (N * uu + B * vv) * s))
        rings.append(ring)
    m = len(profile)
    segs = n if closed else n - 1
    for i in range(segs):
        A, Bv = rings[i], rings[(i + 1) % n]
        for j in range(m):
            k = (j + 1) % m
            bm.faces.new((A[j], A[k], Bv[k], Bv[j])).material_index = mat
    if caps and not closed:
        bm.faces.new(list(reversed(rings[0]))).material_index = mat
        bm.faces.new(rings[-1]).material_index = mat
    return rings


def box(bm, center, size, mat=0, matrix=None):
    cx, cy, cz = center
    sx, sy, sz = (s / 2.0 for s in size)
    pts = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
           (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    vs = []
    for p in pts:
        v = Vector(p)
        if matrix is not None:
            v = matrix @ v
        vs.append(bm.verts.new((cx + v.x, cy + v.y, cz + v.z)))
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f]).material_index = mat
    return vs


def circle_profile(radius, n=12, rx=None, ry=None):
    rx = radius if rx is None else rx
    ry = radius if ry is None else ry
    return [(rx * math.cos(2 * math.pi * i / n), ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rect_profile(w, h, chamfer=0.0):
    hw, hh = w / 2.0, h / 2.0
    if chamfer <= 0:
        return [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    c = chamfer
    return [(-hw + c, -hh), (hw - c, -hh), (hw, -hh + c), (hw, hh - c), (hw - c, hh), (-hw + c, hh),
            (-hw, hh - c), (-hw, -hh + c)]


def pointed_arch(span, radius_factor=1.0, n=16):
    """Centerline of a pointed arch in 2D (x, y) from (-span/2, 0) over the apex to (span/2, 0)."""
    R = span * radius_factor
    cxl = -span / 2.0 + R
    h = math.sqrt(max(R * R - cxl * cxl, 1e-9))
    a0, a1 = math.pi, math.atan2(h, -cxl)
    left = [(cxl + R * math.cos(a0 + (a1 - a0) * i / n), R * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    right = [(-x, y) for (x, y) in reversed(left[:-1])]
    return left + right, h


def lancet_outline(width, spring, radius_factor=1.0, n=16, sill=0.0):
    """Closed CCW outline (x, z) of a lancet opening: rectangle up to the springline plus a pointed head."""
    arch, h = pointed_arch(width, radius_factor, n)
    pts = [(-width / 2.0, sill), (width / 2.0, sill)]
    for (x, y) in reversed(arch):  # right springing -> apex -> left springing
        pts.append((x, spring + y))
    return pts, spring + h


def polygon_offset(pts, d):
    """Offset a closed CCW polygon inward by d (negative d grows it). Miter joins."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e0 = (p1 - p0).normalized()
        e1 = (p2 - p1).normalized()
        n0 = Vector((-e0.y, e0.x))
        n1 = Vector((-e1.y, e1.x))
        nm = (n0 + n1)
        if nm.length < 1e-6:
            nm = n0
        nm.normalize()
        denom = max(nm.dot(n0), 0.25)
        q = p1 + nm * (d / denom)
        out.append((q.x, q.y))
    return out


def resample_closed(pts, count):
    """Resample a closed polyline to `count` points evenly spaced by arc length."""
    P = [Vector(p) for p in pts]
    segs = [(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]
    lengths = [(b - a).length for a, b in segs]
    total = sum(lengths)
    out = []
    for k in range(count):
        target = total * k / count
        acc = 0.0
        for (a, b), L in zip(segs, lengths):
            if acc + L >= target - 1e-12:
                t = (target - acc) / L if L > 0 else 0.0
                q = a.lerp(b, t)
                out.append(tuple(q))
                break
            acc += L
    return out


def frame_matrix(origin, x_axis, y_axis):
    x = Vector(x_axis).normalized()
    y = Vector(y_axis)
    y = (y - x * y.dot(x)).normalized()
    z = x.cross(y)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(origin)
    return m


# ----------------------------------------------------------------------------- node trees

class NodeBuilder:
    """Tiny helper around a node tree. new() accepts props={...} and inputs={name_or_index: value_or_socket}."""

    def __init__(self, tree, clear=True):
        self.tree = tree
        if clear:
            for n in list(tree.nodes):
                tree.nodes.remove(n)

    def new(self, idname, loc=(0, 0), props=None, inputs=None, label=None):
        n = self.tree.nodes.new(idname)
        n.location = loc
        if label:
            n.label = label
        for k, v in (props or {}).items():
            setattr(n, k, v)
        for k, v in (inputs or {}).items():
            self.set(n, k, v)
        return n

    def set(self, node, key, value):
        sock = node.inputs[key]
        if isinstance(value, bpy.types.NodeSocket):
            self.tree.links.new(value, sock)
        else:
            if hasattr(sock, "default_value"):
                dv = sock.default_value
                if hasattr(dv, "__len__") and not isinstance(value, str):
                    if not hasattr(value, "__len__"):
                        value = [value] * len(dv)
                    value = list(value)
                    if len(value) < len(dv):
                        value = value + [1.0] * (len(dv) - len(value))
                    sock.default_value = value[:len(dv)]
                else:
                    sock.default_value = value
        return sock

    def link(self, a, b):
        return self.tree.links.new(a, b)

    # convenience math helpers ------------------------------------------------
    def math(self, op, a, b=None, loc=(0, 0), clamp=False):
        n = self.new("ShaderNodeMath", loc, props={"operation": op, "use_clamp": clamp})
        self.set(n, 0, a)
        if b is not None:
            self.set(n, 1, b)
        return n.outputs[0]

    def vmath(self, op, a, b=None, loc=(0, 0)):
        n = self.new("ShaderNodeVectorMath", loc, props={"operation": op})
        self.set(n, 0, a)
        if b is not None:
            self.set(n, 1, b)
        out = n.outputs["Value"] if op in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else n.outputs["Vector"]
        return out

    def mix_color(self, blend, fac, a, b, loc=(0, 0), clamp=False):
        n = self.new("ShaderNodeMix", loc, props={"data_type": "RGBA", "blend_type": blend, "clamp_result": clamp})
        self.set(n, "Factor", fac)
        self.set(n, 6, a)
        self.set(n, 7, b)
        return n.outputs[2]

    def map_range(self, value, fmin, fmax, tmin, tmax, loc=(0, 0), clamp=True, interp="LINEAR"):
        n = self.new("ShaderNodeMapRange", loc, props={"clamp": clamp, "interpolation_type": interp})
        self.set(n, "Value", value)
        self.set(n, "From Min", fmin)
        self.set(n, "From Max", fmax)
        self.set(n, "To Min", tmin)
        self.set(n, "To Max", tmax)
        return n.outputs["Result"]

    def ramp(self, fac, stops, loc=(0, 0), interp="LINEAR"):
        n = self.new("ShaderNodeValToRGB", loc)
        cr = n.color_ramp
        cr.interpolation = interp
        while len(cr.elements) > 1:
            cr.elements.remove(cr.elements[-1])
        cr.elements[0].position = stops[0][0]
        cr.elements[0].color = tuple(stops[0][1]) + ((1.0,) if len(stops[0][1]) == 3 else ())
        for pos, col in stops[1:]:
            e = cr.elements.new(pos)
            e.color = tuple(col) + ((1.0,) if len(col) == 3 else ())
        self.set(n, "Fac", fac)
        return n


def new_material(name):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nb = NodeBuilder(mat.node_tree)
    out = nb.new("ShaderNodeOutputMaterial", (900, 0))
    return mat, nb, out


def principled(nb, loc=(400, 0), **inputs):
    names = {
        "base": "Base Color", "metallic": "Metallic", "roughness": "Roughness", "ior": "IOR",
        "alpha": "Alpha", "normal": "Normal", "sss": "Subsurface Weight", "sss_radius": "Subsurface Radius",
        "sss_scale": "Subsurface Scale", "spec": "Specular IOR Level", "spec_tint": "Specular Tint",
        "aniso": "Anisotropic", "aniso_rot": "Anisotropic Rotation", "transmission": "Transmission Weight",
        "coat": "Coat Weight", "coat_rough": "Coat Roughness", "coat_ior": "Coat IOR", "coat_tint": "Coat Tint",
        "sheen": "Sheen Weight", "sheen_rough": "Sheen Roughness", "sheen_tint": "Sheen Tint",
        "emission": "Emission Color", "emission_strength": "Emission Strength",
        "thin_film": "Thin Film Thickness", "coat_normal": "Coat Normal",
    }
    n = nb.new("ShaderNodeBsdfPrincipled", loc)
    for k, v in inputs.items():
        nb.set(n, names.get(k, k), v)
    return n


def load_image(filename, colorspace="sRGB", directory=TEX_DIR):
    path = os.path.join(directory, filename)
    img = bpy.data.images.get(filename)
    if img is None:
        img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    return img


# ----------------------------------------------------------------------------- animation

def find_fcurve(id_data, data_path, index=0):
    """F-curve lookup that understands slotted actions (Blender 4.4+ may store object-data keys, e.g. camera
    lens, as a second slot inside the object's action, which the legacy Action.fcurves cannot see)."""
    ad = id_data.animation_data
    if ad is None or ad.action is None:
        return None
    act = ad.action
    slot = getattr(ad, "action_slot", None)
    if slot is not None:
        try:
            from bpy_extras import anim_utils
            bag = anim_utils.action_get_channelbag_for_slot(act, slot)
            if bag is not None:
                fc = bag.fcurves.find(data_path, index=index)
                if fc is not None:
                    return fc
        except (ImportError, AttributeError):
            pass
    try:
        return act.fcurves.find(data_path, index=index)
    except AttributeError:
        return None


def monotone_slopes(times, values):
    """Fritsch-Carlson slopes (per frame) for a monotone-preserving cubic Hermite curve."""
    n = len(times)
    if n < 2:
        return [0.0] * n
    d = [(values[i + 1] - values[i]) / (times[i + 1] - times[i]) for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1 = 2 * (times[i + 1] - times[i]) + (times[i] - times[i - 1])
            w2 = (times[i + 1] - times[i]) + 2 * (times[i] - times[i - 1])
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    return m


def hermite_keys(id_data, data_path, index, keys, extrapolate="CONSTANT"):
    """Insert Bezier keys that reproduce an exact cubic Hermite curve.

    keys: list of (frame, value, slope_or_None). Slopes are units per frame; None = monotone auto."""
    times = [k[0] for k in keys]
    values = [k[1] for k in keys]
    auto = monotone_slopes(times, values)
    slopes = [k[2] if (len(k) > 2 and k[2] is not None) else auto[i] for i, k in enumerate(keys)]
    target = id_data
    for f, v in zip(times, values):
        prop = getattr(target, data_path)
        if hasattr(prop, "__len__"):
            prop[index] = v
        else:
            setattr(target, data_path, v)
        target.keyframe_insert(data_path, index=index if hasattr(prop, "__len__") else -1, frame=f)
    fc = find_fcurve(target, data_path, index if hasattr(getattr(target, data_path), "__len__") else 0)
    fc.extrapolation = extrapolate
    kps = sorted(fc.keyframe_points, key=lambda k: k.co.x)
    for i, kp in enumerate(kps):
        f, v, m = times[i], values[i], slopes[i]
        kp.co = (f, v)
        kp.interpolation = "BEZIER"
        kp.handle_left_type = "FREE"
        kp.handle_right_type = "FREE"
        dl = (f - times[i - 1]) if i > 0 else 10.0
        dr = (times[i + 1] - f) if i < len(times) - 1 else 10.0
        kp.handle_left = (f - dl / 3.0, v - m * dl / 3.0)
        kp.handle_right = (f + dr / 3.0, v + m * dr / 3.0)
    return fc


def add_noise(id_data, data_path, index, base, strength, scale, phase, frame=1, offset=0.0):
    """Static key + procedural F-curve noise (flicker/wobble) without any Python drivers."""
    prop = getattr(id_data, data_path)
    if hasattr(prop, "__len__"):
        prop[index] = base
        id_data.keyframe_insert(data_path, index=index, frame=frame)
        fc = find_fcurve(id_data, data_path, index)
    else:
        setattr(id_data, data_path, base)
        id_data.keyframe_insert(data_path, frame=frame)
        fc = find_fcurve(id_data, data_path, 0)
    mod = fc.modifiers.new("NOISE")
    mod.blend_type = "ADD"
    mod.strength = strength
    mod.scale = scale
    mod.phase = phase
    mod.offset = offset
    mod.depth = 1
    return fc
