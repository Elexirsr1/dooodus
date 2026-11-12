"""Verify the saved scene: timeline, output settings, camera motion quality, clearance and framing.

Usage: blender -b gothic_heart_trophy.blend -P scripts/verify_scene.py -- [--step 1] [--json out.json]
Exits non-zero if a hard requirement fails.
"""
import argparse
import json
import math
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SKIP_PREFIX = ("Shaft_", "Dust_", "Flame_", "Window_")


def merged_bvh(objs, depsgraph):
    verts, polys = [], []
    for ob in objs:
        ev = ob.evaluated_get(depsgraph)
        me = ev.to_mesh()
        off = len(verts)
        mw = ev.matrix_world
        verts.extend(mw @ v.co for v in me.vertices)
        polys.extend([off + i for i in p.vertices] for p in me.polygons)
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys, epsilon=0.0) if polys else None


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            inside = not inside
    return inside


def beam_volumes():
    vols = []
    for ob in bpy.data.objects:
        if ob.name.endswith("_Beam") and "beam_dir" in ob:
            d = Vector(ob["beam_dir"])
            L = ob["beam_length"]
            n = len(ob.data.vertices) // 2
            ring = [ob.matrix_world @ ob.data.vertices[i].co for i in range(n)]
            axis = 0 if abs(d.x) > abs(d.y) and abs(ring[0].x - ring[1].x) < 1e-3 else 1
            # window plane is constant along the wall normal; pick the coordinate that is constant on the ring
            spread = [max(p[k] for p in ring) - min(p[k] for p in ring) for k in range(3)]
            axis = 0 if spread[0] < spread[1] else 1
            plane = sum(p[axis] for p in ring) / n
            other = 1 - axis
            poly = [(p[other], p.z) for p in ring]
            vols.append((ob.name, d, L, axis, plane, other, poly))
    return vols


def inside_beam(p, vol):
    _, d, L, axis, plane, other, poly = vol
    if abs(d[axis]) < 1e-6:
        return False
    s = (p[axis] - plane) / d[axis]
    if s < 0 or s > L:
        return False
    q = p - d * s
    return point_in_poly((q[other], q.z), poly)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--json", default="")
    a = ap.parse_args(argv)
    scene = bpy.context.scene
    r = scene.render
    report = {"checks": {}, "stats": {}}
    hard_fail = []

    def check(name, ok, detail):
        report["checks"][name] = {"ok": bool(ok), "detail": detail}
        print(f"[verify] {'PASS' if ok else 'FAIL'} {name}: {detail}", flush=True)
        if not ok:
            hard_fail.append(name)

    check("frame_range", scene.frame_start == 1 and scene.frame_end == 1800,
          f"{scene.frame_start}-{scene.frame_end} ({scene.frame_end - scene.frame_start + 1} frames)")
    check("fps", r.fps == 120 and abs(r.fps_base - 1.0) < 1e-9, f"{r.fps}/{r.fps_base}")
    check("duration_s", abs((scene.frame_end - scene.frame_start + 1) / (r.fps / r.fps_base) - 15.0) < 1e-9,
          f"{(scene.frame_end - scene.frame_start + 1) / (r.fps / r.fps_base):.3f} s")
    check("resolution", (r.resolution_x, r.resolution_y, r.resolution_percentage) == (1920, 1080, 100),
          f"{r.resolution_x}x{r.resolution_y} @ {r.resolution_percentage}%")
    check("engine", r.engine == "CYCLES", r.engine)
    check("color_management", scene.view_settings.view_transform == "AgX",
          f"{scene.view_settings.view_transform} / {scene.view_settings.look}")
    missing = [i.name for i in bpy.data.images if i.source == "FILE" and not i.packed_file]
    check("textures_packed", not missing, f"unpacked: {missing}" if missing else "all image files packed")
    fonts = [f.name for f in bpy.data.fonts if f.filepath and not f.packed_file and f.name != "Bfont Regular"]
    check("fonts_packed", not fonts, f"unpacked: {fonts}" if fonts else "fonts packed")
    no_mat = [o.name for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) and
              (not o.material_slots or any(s.material is None for s in o.material_slots))
              and o.name != "Dust_Motes"]
    check("materials_assigned", not no_mat, f"{len(no_mat)} meshes without material: {no_mat[:8]}")

    cam = scene.camera
    trophy_parts = [o for o in bpy.data.collections["Trophy"].all_objects if o.type == "MESH"]
    heart = bpy.data.objects["Trophy_Heart_Ruby"]
    dg = bpy.context.evaluated_depsgraph_get()
    obstacles = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith(SKIP_PREFIX)
                 and o not in trophy_parts and o.visible_camera]
    scene.frame_set(1)
    dg = bpy.context.evaluated_depsgraph_get()
    bvh_static = merged_bvh(obstacles, dg)
    bvh_trophy = merged_bvh(trophy_parts, dg)
    beams = beam_volumes()
    heart_c = sum((heart.matrix_world @ v.co for v in heart.data.vertices), Vector()) / len(heart.data.vertices)
    bbox_pts = []
    for o in trophy_parts:
        bbox_pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    top = max(bbox_pts, key=lambda p: p.z)
    base = Vector((0, 0, min(p.z for p in bbox_pts)))

    frames = list(range(scene.frame_start, scene.frame_end + 1, a.step))
    pos, fwd = [], []
    min_clear = (1e9, None, None)
    min_clear_trophy = (1e9, None)
    in_beam, blocked, heart_out, trophy_out = [], [], [], []
    for f in frames:
        scene.frame_set(f)
        mw = cam.matrix_world
        p = mw.translation.copy()
        pos.append(p)
        fwd.append((mw.to_3x3() @ Vector((0, 0, -1))).normalized())
        hit = bvh_static.find_nearest(p)
        if hit[0] is not None and hit[3] < min_clear[0]:
            min_clear = (hit[3], f, tuple(round(c, 3) for c in hit[0]))
        ht = bvh_trophy.find_nearest(p)
        if ht[0] is not None and ht[3] < min_clear_trophy[0]:
            min_clear_trophy = (ht[3], f)
        for vol in beams:
            if inside_beam(p, vol):
                in_beam.append((f, vol[0]))
        to_heart = heart_c - p
        h = bvh_static.ray_cast(p, to_heart.normalized(), to_heart.length - 0.12)
        if h[0] is not None:
            blocked.append(f)
        v = world_to_camera_view(scene, cam, heart_c)
        if not (0.0 <= v.x <= 1.0 and 0.0 <= v.y <= 1.0 and v.z > 0):
            heart_out.append(f)
        if f >= 900:  # 721-900 is the planned pull-back out of the gem close-up
            vt, vb = world_to_camera_view(scene, cam, top), world_to_camera_view(scene, cam, base)
            if not (0 <= vt.y <= 1 and 0 <= vb.y <= 1 and 0 <= vt.x <= 1 and 0 <= vb.x <= 1):
                trophy_out.append(f)

    fps = r.fps / r.fps_base
    dt = a.step / fps
    speeds = [(pos[i + 1] - pos[i]).length / dt for i in range(len(pos) - 1)]
    accs = [abs(speeds[i + 1] - speeds[i]) / dt for i in range(len(speeds) - 1)]
    vel = [(pos[i + 1] - pos[i]) / dt for i in range(len(pos) - 1)]
    accv = [((vel[i + 1] - vel[i]) / dt).length for i in range(len(vel) - 1)]
    jerk = [abs(accv[i + 1] - accv[i]) / dt for i in range(len(accv) - 1)]
    ang = [math.degrees(fwd[i].angle(fwd[i + 1], 0.0)) / dt for i in range(len(fwd) - 1)]
    report["stats"] = {
        "max_speed_m_s": round(max(speeds), 3), "max_accel_m_s2": round(max(accv), 3),
        "max_jerk_m_s3": round(max(jerk), 2), "max_view_rotation_deg_s": round(max(ang), 2),
        "min_clearance_m": round(min_clear[0], 3), "min_clearance_frame": min_clear[1],
        "min_clearance_point": min_clear[2], "min_trophy_clearance_m": round(min_clear_trophy[0], 3),
        "min_trophy_clearance_frame": min_clear_trophy[1],
    }
    pivot = bpy.data.objects["CAM_Pivot"]
    scene.frame_set(721)
    th0 = pivot.rotation_euler.z
    scene.frame_set(1680)
    th1 = pivot.rotation_euler.z
    check("orbit_360", abs(abs(math.degrees(th1 - th0)) - 360.0) < 0.01,
          f"azimuth change 721->1680 = {math.degrees(th1 - th0):.4f} deg")
    check("camera_clearance", min_clear[0] > 0.25, f"min distance to scene geometry {min_clear[0]:.3f} m at frame "
          f"{min_clear[1]} (nearest point {min_clear[2]})")
    check("trophy_clearance", min_clear_trophy[0] > 0.3, f"min distance to trophy {min_clear_trophy[0]:.3f} m "
          f"at frame {min_clear_trophy[1]}")
    check("camera_outside_light_shafts", not in_beam, f"{len(in_beam)} frame(s) inside a shaft volume "
          f"{in_beam[:5]}")
    check("heart_unobstructed", not blocked, f"{len(blocked)} frame(s) with geometry between lens and heart "
          f"{blocked[:10]}")
    check("heart_in_frame", not heart_out, f"{len(heart_out)} frame(s) with the heart outside the frame "
          f"{heart_out[:10]}")
    check("trophy_in_frame_orbit_hero", not trophy_out, f"{len(trophy_out)} frame(s) 900-1800 cropping the "
          f"trophy {trophy_out[:10]}")
    print("[verify] stats", json.dumps(report["stats"]), flush=True)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(report, fh, indent=2)
    if hard_fail:
        print(f"[verify] FAILED: {hard_fail}", flush=True)
        sys.exit(1)
    print("[verify] ALL CHECKS PASSED", flush=True)


if __name__ == "__main__":
    main()
