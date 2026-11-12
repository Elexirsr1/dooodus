"""Lighting: sunlit stained-glass spots with matching light shafts, trophy and shield key/rim lights
(light-linked), the ruby's red glow, and a soft cool fill."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import materials as M
from .architecture import WINDOW_TYPES
from .util import collection, finish_bmesh, lancet_outline

SUN = (1.0, 0.87, 0.70)


def aim(ob, target):
    d = Vector(target) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def light(coll, name, kind, location, energy, color, target=None, size=None, spot=None, blend=0.2, radius=None,
          receivers=None, **vis):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size
    if kind == "SPOT":
        ld.spot_size = math.radians(spot)
        ld.spot_blend = blend
    if radius is not None:
        ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld)
    ob.location = location
    coll.objects.link(ob)
    if target is not None:
        aim(ob, target)
    if receivers is not None:
        ob.light_linking.receiver_collection = receivers
    for k, v in vis.items():
        setattr(ob, k, v)
    return ob


def world(scene):
    w = bpy.data.worlds.new("World_Cathedral")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.010, 0.013, 0.020, 1.0)
    bg.inputs["Strength"].default_value = 0.4
    w.mist_settings.start = 1.5
    w.mist_settings.depth = 42.0
    w.mist_settings.falloff = "LINEAR"
    scene.world = w
    return w


def _clip_above(poly, zc):
    """Sutherland-Hodgman clip of a closed (x, z) polygon to z >= zc."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ina, inb = a[1] >= zc, b[1] >= zc
        if ina:
            out.append(a)
        if ina != inb:
            t = (zc - a[1]) / (b[1] - a[1])
            out.append((a[0] + t * (b[0] - a[0]), zc))
    return out


def find_window(windows, wall, bay):
    for w in windows:
        if w["wall"] == wall and w["bay"] == bay:
            return w
    raise KeyError((wall, bay))


def shaft(coll, w, direction, power, beam_strength, clip_z=None, pale=0.0, name=None, beam_color=SUN):
    """Exterior spot shining along `direction` through window record `w`, plus a matching fake shaft."""
    d = Vector(direction).normalized()
    wt = WINDOW_TYPES[w["kind"]]
    span = wt["spring"] - wt["sill"]
    outline, apex = lancet_outline(wt["width"], span, 1.0, 22)
    if clip_z is not None:
        outline = _clip_above(outline, clip_z)
    pane_m = w["matrix"] @ Matrix.Translation((0, 0, w["sill_z"]))
    world_pts = [pane_m @ Vector((x, 0.0, z)) for (x, z) in outline]
    center = sum(world_pts, Vector()) / len(world_pts)
    radius = max((p - center).length for p in world_pts)
    name = name or f"Shaft_{w['wall']}_{w['bay']:+d}"
    w["pane"]["glass_tint_mix"] = pale

    dist = 24.0
    spot = light(coll, f"{name}_Sun", "SPOT", center - d * dist, power, SUN, target=center,
                 spot=2 * math.degrees(math.atan(radius * 1.12 / dist)), blend=0.06, radius=0.18,
                 visible_glossy=False, visible_diffuse=False)

    # beam prism: window outline extruded along the light direction until it is below the floor
    length = (max(p.z for p in world_pts) + 0.6) / max(-d.z, 0.2)
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in world_pts]
    b = [bm.verts.new(p + d * length) for p in world_pts]
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    interior = w["interior"]
    axis = "X" if abs(interior.x) > 0.5 else "Y"
    plane = pane_m.translation.x if axis == "X" else pane_m.translation.y
    mat = M.light_beam(f"Beam_{name}", axis, plane, tuple(d), beam_strength, beam_color, length)
    beam = finish_bmesh(bm, f"{name}_Beam", coll, [mat])
    for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission",
                 "visible_volume_scatter"):
        setattr(beam, attr, False)
    beam["beam_dir"] = tuple(d)
    beam["beam_length"] = length
    return spot, beam


def build(root, scene, arch, trophy, shield):
    coll = collection("Lighting", root)
    shafts = collection("Light_Shafts", coll)
    world(scene)
    windows = arch["windows"]
    heart = trophy["heart"]

    # receiver collections for light linking (not linked to the scene)
    ll_trophy = bpy.data.collections.new("LL_Trophy_Receivers")
    for ob in trophy["collection"].all_objects:
        if ob.type in {"MESH", "FONT"}:
            ll_trophy.objects.link(ob)
    ll_shield = bpy.data.collections.new("LL_Shield_Receivers")
    for ob in shield["collection"].all_objects:
        if ob.type == "MESH":
            ll_shield.objects.link(ob)
    for ob in arch["reredos"]:
        ll_shield.objects.link(ob)

    # --- sun through stained glass ---------------------------------------------------------------
    # clerestory light falling steeply onto the trophy (pale gold so the silver is not blotched)
    w = find_window(windows, "clere_L", 1)
    wt = WINDOW_TYPES["clere"]
    wc = w["matrix"] @ Vector((0, 0, (wt["sill"] + wt["spring"]) / 2 + 0.5))
    d_trophy = (Vector((0.0, 0.05, 1.95)) - wc).normalized()
    shaft(shafts, w, d_trophy, 120000.0, 0.075, pale=0.72, name="Shaft_Trophy")
    # south aisle windows down the nave: long raking shafts across the floor (two, to bound render cost:
    # every shaft a camera ray crosses costs two extra intersections)
    d_aisle = Vector((0.58, -0.08, -0.81))
    for bay in (3, 5):
        shaft(shafts, find_window(windows, "aisle_L", bay), d_aisle, 160000.0, 0.068)
    # apse side lancets: shafts falling beside the reredos, framing the shield
    d_apse = Vector((0.0, -0.5, -0.866))
    for bay in (-3, 3):
        shaft(shafts, find_window(windows, "apse", bay), d_apse, 140000.0, 0.062)

    # --- trophy: softboxes the silver can reflect, cool and gold rims (all linked to the trophy only) --
    tl = collection("Trophy_Lights", coll)
    light(tl, "Trophy_Key_Softbox", "AREA", (-1.6, -2.1, 3.2), 150.0, (1.0, 0.95, 0.88), target=heart,
          size=(1.4, 0.9), receivers=ll_trophy, visible_camera=False)
    light(tl, "Trophy_Top_Softbox", "AREA", (0.2, -0.3, 4.4), 140.0, (1.0, 0.96, 0.92), target=heart,
          size=(1.8, 1.8), receivers=ll_trophy, visible_camera=False)
    light(tl, "Trophy_Fill_Strip", "AREA", (1.9, -1.2, 1.7), 60.0, (0.82, 0.88, 1.0), target=heart - Vector((0, 0, 0.3)),
          size=(0.35, 1.8), receivers=ll_trophy, visible_camera=False)
    light(tl, "Trophy_Back_Strip", "AREA", (-0.6, 2.3, 2.2), 70.0, (0.9, 0.92, 1.0), target=heart,
          size=(0.35, 1.8), receivers=ll_trophy, visible_camera=False)
    light(tl, "Trophy_Floor_Bounce", "AREA", (0.0, -1.6, 0.9), 35.0, (1.0, 0.82, 0.6),
          target=heart - Vector((0, 0, 0.55)), size=(1.6, 0.5), receivers=ll_trophy, visible_camera=False)
    light(tl, "Trophy_Rim_Cool", "SPOT", (-1.5, 2.4, 3.1), 320.0, (0.80, 0.88, 1.0), target=heart,
          spot=34, blend=0.5, radius=0.35, receivers=ll_trophy)
    light(tl, "Trophy_Rim_Gold", "SPOT", (1.7, 2.2, 2.6), 340.0, (1.0, 0.74, 0.40), target=heart - Vector((0, 0, 0.2)),
          spot=34, blend=0.5, radius=0.35, receivers=ll_trophy)
    # ruby glow: lights the silverwork red from within (the gem does not cast shadows)
    gem = light(tl, "Ruby_Glow", "POINT", heart + Vector((0, -0.005, 0.0)), 9.0, (1.0, 0.07, 0.02), radius=0.035,
                visible_glossy=False)

    # --- shield: big softbox for the lacquer and gold to reflect, warm key, ember glow ----------------
    sl = collection("Shield_Lights", coll)
    light(sl, "Shield_Softbox", "AREA", (0.0, -0.8, 5.6), 170.0, (1.0, 0.92, 0.82), target=(0, 4.05, 2.9),
          size=(3.2, 0.9), receivers=ll_shield, visible_camera=False)
    light(sl, "Shield_Key", "SPOT", (0.4, 1.5, 6.2), 420.0, (1.0, 0.86, 0.66), target=(0, 4.0, 3.0), spot=42,
          blend=0.6, radius=0.5, receivers=ll_shield)
    light(sl, "Shield_Gold_Glint", "SPOT", (2.4, 2.8, 4.7), 160.0, (1.0, 0.70, 0.36), target=(0, 4.0, 3.2), spot=30,
          blend=0.5, radius=0.3, receivers=ll_shield)
    light(sl, "Shield_Ember", "POINT", (0.0, 3.55, 3.15), 22.0, (1.0, 0.28, 0.05), radius=0.4, receivers=ll_shield,
          visible_glossy=False)

    # --- soft cool fill high in the nave so the stone never drops to pure black --------------------
    light(coll, "Nave_Fill", "AREA", (0.0, -8.0, 18.0), 2600.0, (0.55, 0.66, 1.0), target=(0, -8.0, 0),
          size=(7.0, 26.0), visible_camera=False, visible_glossy=False)
    light(coll, "Sanctuary_Fill", "AREA", (0.0, 1.0, 9.0), 520.0, (0.75, 0.70, 0.80), target=(0, 1.0, 0),
          size=(6.0, 6.0), visible_camera=False, visible_glossy=False)
    return dict(collection=coll, gem_light=gem)
