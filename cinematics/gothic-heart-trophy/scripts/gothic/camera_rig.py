"""Camera rig and the 15 s / 1800 frame move.

Rig: CAM_Pivot (Z rotation = azimuth around the trophy) -> CAM_Main (local Y = -distance, Z = height),
CAM_Main tracks CAM_Aim, which is also the depth-of-field focus target.

Every channel is keyed with exact cubic-Hermite Bezier handles (see util.hermite_keys), so velocity is
continuous across all segment boundaries. Slopes are degrees or metres per frame.

  1-360     approach down the nave toward the altar
  361-720   push in to a close-up of the ruby heart, drifting slowly across its facets
  721-1680  one continuous 360 degree orbit (exactly 360 deg between frames 721 and 1680)
  1681-1800 settle into a low hero angle and hold
"""
import math

import bpy
from mathutils import Vector

from .util import collection, empty, hermite_keys

FPS = 120
SEGMENTS = (("Approach", 1), ("Heart close-up", 361), ("Orbit 360", 721), ("Hero", 1681))

ORBIT_START, ORBIT_END = 721, 1680
THETA_721 = 4.0  # orbit ends 360 deg later at -356, the hero settles near frontal (-0.8)
OMEGA_IN, OMEGA_OUT = 0.06, 0.08  # deg/frame entering and leaving the orbit
# solve the cruise rate so the orbit covers exactly 360 degrees with linear speed ramps 721-900 and 1500-1680
OMEGA = (360.0 - 179 * OMEGA_IN / 2 - 180 * OMEGA_OUT / 2) / (179 / 2 + 600 + 180 / 2)
THETA_900 = THETA_721 - 179 * (OMEGA_IN + OMEGA) / 2
THETA_1500 = THETA_900 - 600 * OMEGA
THETA_1680 = THETA_721 - 360.0
THETA_1800 = THETA_1680 - 120 * OMEGA_OUT / 2


def channels(heart_z):
    """Key tables: (frame, value, slope|None)."""
    theta = [(1, 14.0, 0.0), (360, 11.0, None), (560, 9.5, -0.015), (ORBIT_START, THETA_721, -OMEGA_IN),
             (900, THETA_900, -OMEGA), (1500, THETA_1500, -OMEGA), (ORBIT_END, THETA_1680, -OMEGA_OUT),
             (1800, THETA_1800, 0.0)]
    dist = [(1, 7.4, 0.0), (360, 4.0, -0.0145), (560, 1.40, -0.0016), (ORBIT_START, 1.28, 0.0), (900, 2.80, 0.004),
            (1200, 2.95, None), (1500, 2.90, None), (ORBIT_END, 3.40, 0.0045), (1800, 3.70, 0.0)]
    height = [(1, 1.85, 0.0), (360, 2.05, None), (560, 2.06, None), (ORBIT_START, 2.02, None), (900, 2.12, None),
              (1200, 2.40, None), (1500, 2.10, None), (ORBIT_END, 1.62, None), (1800, 1.45, 0.0)]
    aim_z = [(1, 2.45, 0.0), (360, 2.02, None), (560, heart_z, None), (ORBIT_START, heart_z, 0.0), (900, 1.82, None),
             (1500, 1.82, None), (ORBIT_END, 1.98, None), (1800, 2.05, 0.0)]
    lens = [(1, 30.0, 0.0), (360, 36.0, None), (560, 58.0, None), (ORBIT_START, 60.0, 0.0), (900, 40.0, None),
            (1500, 40.0, None), (ORBIT_END, 33.0, None), (1800, 32.0, 0.0)]
    fstop = [(1, 5.6, 0.0), (360, 4.0, None), (560, 2.4, None), (ORBIT_START, 2.4, 0.0), (900, 3.2, None),
             (ORBIT_END, 4.0, None), (1800, 4.5, 0.0)]
    return dict(theta=theta, dist=dist, height=height, aim_z=aim_z, lens=lens, fstop=fstop)


def build(root, heart_world):
    coll = collection("Camera_Rig", root)
    pivot = empty("CAM_Pivot", coll, (0, 0, 0), display="CIRCLE", size=1.0)
    aim = empty("CAM_Aim", coll, (0, 0, heart_world.z), display="SPHERE", size=0.05)
    cd = bpy.data.cameras.new("CAM_Main")
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0
    cd.clip_start = 0.05
    cd.clip_end = 200.0
    cd.dof.use_dof = True
    cd.dof.focus_object = aim
    cd.dof.aperture_blades = 7
    cd.dof.aperture_rotation = math.radians(12)
    cam = bpy.data.objects.new("CAM_Main", cd)
    coll.objects.link(cam)
    cam.parent = pivot
    tr = cam.constraints.new("TRACK_TO")
    tr.target = aim
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"
    bpy.context.scene.camera = cam

    ch = channels(heart_world.z)
    hermite_keys(pivot, "rotation_euler", 2, [(f, math.radians(v), None if m is None else math.radians(m))
                                               for (f, v, m) in ch["theta"]])
    hermite_keys(cam, "location", 1, [(f, -v, None if m is None else -m) for (f, v, m) in ch["dist"]])
    hermite_keys(cam, "location", 2, ch["height"])
    hermite_keys(cam, "location", 0, [(1, 0.0, 0.0), (1800, 0.0, 0.0)])
    hermite_keys(aim, "location", 2, ch["aim_z"])
    hermite_keys(aim, "location", 0, [(1, heart_world.x, 0.0), (1800, heart_world.x, 0.0)])
    hermite_keys(aim, "location", 1, [(1, heart_world.y, 0.0), (1800, heart_world.y, 0.0)])
    hermite_keys(cd, "lens", 0, ch["lens"])
    _key_fstop(cd, ch["fstop"])

    scene = bpy.context.scene
    for name, frame in SEGMENTS:
        scene.timeline_markers.new(name, frame=frame)
    return dict(collection=coll, camera=cam, pivot=pivot, aim=aim)


def _key_fstop(cd, keys):
    """dof.aperture_fstop lives on a nested struct; key it through the camera datablock path."""
    from .util import find_fcurve, monotone_slopes
    times = [k[0] for k in keys]
    values = [k[1] for k in keys]
    auto = monotone_slopes(times, values)
    for f, v in zip(times, values):
        cd.dof.aperture_fstop = v
        cd.keyframe_insert("dof.aperture_fstop", frame=f)
    fc = find_fcurve(cd, "dof.aperture_fstop", 0)
    for i, kp in enumerate(sorted(fc.keyframe_points, key=lambda k: k.co.x)):
        f, v = times[i], values[i]
        m = keys[i][2] if keys[i][2] is not None else auto[i]
        dl = (f - times[i - 1]) if i > 0 else 10.0
        dr = (times[i + 1] - f) if i < len(times) - 1 else 10.0
        kp.interpolation = "BEZIER"
        kp.handle_left_type = kp.handle_right_type = "FREE"
        kp.handle_left = (f - dl / 3, v - m * dl / 3)
        kp.handle_right = (f + dr / 3, v + m * dr / 3)
