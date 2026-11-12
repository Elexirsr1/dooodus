"""Print the evaluated camera state at key frames (debug / verification helper)."""
import math
import sys

import bpy

scene = bpy.context.scene
cam = scene.camera
aim = bpy.data.objects["CAM_Aim"]
pivot = bpy.data.objects["CAM_Pivot"]
frames = [int(x) for x in (sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else
                           "1,180,360,460,560,640,720,721,800,900,1200,1500,1680,1740,1800").split(",")]
for f in frames:
    scene.frame_set(f)
    p = cam.matrix_world.translation
    t = aim.matrix_world.translation
    r = math.hypot(p.x, p.y)
    print(f"[cam] f={f:4d} pos=({p.x:6.3f},{p.y:6.3f},{p.z:5.3f}) r={r:5.3f} theta={math.degrees(pivot.rotation_euler.z):8.3f} "
          f"aim_z={t.z:5.3f} lens={cam.data.lens:5.1f} fstop={cam.data.dof.aperture_fstop:4.2f} "
          f"dist={(p - t).length:5.3f}")
