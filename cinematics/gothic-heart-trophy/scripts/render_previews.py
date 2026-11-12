"""Render still frames from the saved scene (layout checks and final preview stills).

Usage:
  blender -b gothic_heart_trophy.blend -P scripts/render_previews.py -- \
      --frames 1,360,720 [--percent 50] [--samples 32] [--out renders/previews] [--prefix preview]
"""
import argparse
import os
import sys
import time

import bpy


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--frames", default="1,360,720,1200,1680,1800")
    p.add_argument("--percent", type=int, default=100)
    p.add_argument("--samples", type=int, default=0, help="0 keeps the scene setting")
    p.add_argument("--threshold", type=float, default=0.0)
    p.add_argument("--out", default="")
    p.add_argument("--prefix", default="preview")
    p.add_argument("--no-compositor", action="store_true")
    a = p.parse_args(argv)
    scene = bpy.context.scene
    root = os.path.dirname(bpy.data.filepath)
    out = a.out or os.path.join(root, "renders", "previews")
    os.makedirs(out, exist_ok=True)
    scene.render.resolution_percentage = a.percent
    if a.samples:
        scene.cycles.samples = a.samples
        scene.cycles.adaptive_min_samples = min(scene.cycles.adaptive_min_samples, a.samples)
    if a.threshold:
        scene.cycles.adaptive_threshold = a.threshold
    if a.no_compositor:
        scene.render.use_compositing = False
    for f in [int(x) for x in a.frames.split(",") if x.strip()]:
        scene.frame_set(f)
        scene.render.filepath = os.path.join(out, f"{a.prefix}_{f:04d}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"[preview] frame {f} -> {scene.render.filepath} in {time.time() - t:.1f}s", flush=True)


if __name__ == "__main__":
    main()
