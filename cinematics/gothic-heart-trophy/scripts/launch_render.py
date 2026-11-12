"""Start or resume the full animation render as a detached background process.

The render runs in its own session with stdin closed, so it outlives the shell that launched it; output is
appended to renders/render_main.log. Frames that already exist are skipped (see render_animation.py), and a
second render is refused while one is alive. Usage:
  python3 scripts/launch_render.py [--blender /path/to/blender] [--start 1] [--end 1800]
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_watch import FRAMES, alive  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--blender", default=shutil.which("blender"))
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=1800)
    a = p.parse_args()
    if not a.blender:
        print("blender not found on PATH; pass --blender", file=sys.stderr)
        return 2
    if alive():
        print("a render is already running (pid in renders/frames/render.pid)", file=sys.stderr)
        return 1
    os.makedirs(FRAMES, exist_ok=True)
    log = open(os.path.join(ROOT, "renders", "render_main.log"), "ab")
    cmd = [a.blender, "-b", os.path.join(ROOT, "gothic_heart_trophy.blend"),
           "-P", os.path.join(ROOT, "scripts", "render_animation.py"),
           "--", "--start", str(a.start), "--end", str(a.end)]
    proc = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True)
    print(f"render started: pid {proc.pid}, log renders/render_main.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
