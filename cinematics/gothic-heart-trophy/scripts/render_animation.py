"""Resumable animation renderer: renders frames that do not exist yet, atomically, with a timing log.

Usage (one process per slice; frames are interleaved so several processes can share the range):
  blender -b gothic_heart_trophy.blend -P scripts/render_animation.py -- \
      [--start 1] [--end 1800] [--slice 0 --slices 1] [--threads 0] [--out renders/frames]
Frames are written as <out>/frame_0001.png ... frame_1800.png.
"""
import argparse
import os
import sys
import time

import bpy


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=1800)
    p.add_argument("--slice", type=int, default=0)
    p.add_argument("--slices", type=int, default=1)
    p.add_argument("--threads", type=int, default=0, help="0 = all cores")
    p.add_argument("--out", default="")
    a = p.parse_args(argv)
    scene = bpy.context.scene
    root = os.path.dirname(bpy.data.filepath)
    out = os.path.abspath(a.out or os.path.join(root, "renders", "frames"))
    os.makedirs(out, exist_ok=True)
    if a.threads:
        scene.render.threads_mode = "FIXED"
        scene.render.threads = a.threads
    scene.render.resolution_percentage = 100
    with open(os.path.join(out, "render.pid"), "w") as fh:  # lets render_watch.py tell alive from dead
        fh.write(str(os.getpid()))
    log = open(os.path.join(out, f"progress_slice{a.slice}.log"), "a", buffering=1)
    todo = [f for f in range(a.start, a.end + 1) if (f - a.start) % a.slices == a.slice
            and not os.path.exists(os.path.join(out, f"frame_{f:04d}.png"))]
    log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S')} slice {a.slice}/{a.slices}: {len(todo)} frames to render\n")
    durations = []
    for i, f in enumerate(todo):
        final = os.path.join(out, f"frame_{f:04d}.png")
        if os.path.exists(final):
            continue
        tmp = os.path.join(out, f".tmp_slice{a.slice}.png")
        scene.frame_set(f)
        scene.render.filepath = tmp
        t = time.time()
        bpy.ops.render.render(write_still=True)
        os.replace(tmp, final)  # atomic: a frame exists only once it is completely written
        dt = time.time() - t
        durations.append(dt)
        recent = durations[-20:]
        eta_h = (len(todo) - i - 1) * (sum(recent) / len(recent)) / 3600.0
        log.write(f"{time.strftime('%H:%M:%S')} frame {f} {dt:.1f}s eta_slice {eta_h:.2f}h\n")
        print(f"[anim] frame {f} {dt:.1f}s (slice eta {eta_h:.2f} h)", flush=True)
    log.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S')} slice {a.slice} done\n")


if __name__ == "__main__":
    main()
