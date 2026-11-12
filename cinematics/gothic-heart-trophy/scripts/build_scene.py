"""Build the Gothic Heart Trophy scene and save the .blend.

Usage:
  blender -b --factory-startup -P scripts/build_scene.py -- [--out gothic_heart_trophy.blend] [--no-pack]
"""
import argparse
import os
import sys
import time

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gothic import (architecture, camera_rig, effects, lighting, materials, props, render_setup, shield,  # noqa: E402
                    trophy, util)


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=os.path.join(util.ROOT, "gothic_heart_trophy.blend"))
    p.add_argument("--no-pack", action="store_true")
    return p.parse_args(argv)


def main():
    args = parse_args()
    t0 = time.time()
    scene = util.reset_scene()
    root = scene.collection

    arch = architecture.build(root)
    print(f"[build] architecture {time.time() - t0:.1f}s, windows={len(arch['windows'])}")
    tro = trophy.build(root, (0.0, 0.0, architecture.ALTAR_TOP))
    shi = shield.build(root, (0.0, architecture.REREDOS_Y + 0.15, 2.75), tilt_deg=3.0)
    pro = props.build(root, architecture.ALTAR_TOP, architecture.DAIS_TOP)
    print(f"[build] trophy/shield/props {time.time() - t0:.1f}s, candles={pro['kit'].count}")
    cam = camera_rig.build(root, tro["heart"])
    lighting.build(root, scene, arch, tro, shi)
    effects.build(root, scene, cam["camera"])
    render_setup.configure(scene)
    # stone shaders sample UV-mapped textures: give every stone mesh planar per-face UVs (in metres)
    stone = materials.stone_material_names()
    for me in bpy.data.meshes:
        if any(m is not None and m.name in stone for m in me.materials):
            util.add_box_uvs(me)
    scene.frame_set(1)

    if not args.no_pack:
        bpy.ops.file.pack_all()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.out), compress=True)
    stats = dict(objects=len(bpy.data.objects), meshes=len(bpy.data.meshes), materials=len(bpy.data.materials),
                 lights=len([o for o in bpy.data.objects if o.type == "LIGHT"]), images=len(bpy.data.images))
    print(f"[build] saved {args.out} in {time.time() - t0:.1f}s {stats}")


if __name__ == "__main__":
    main()
