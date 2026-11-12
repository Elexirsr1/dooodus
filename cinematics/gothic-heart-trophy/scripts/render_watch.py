"""Wake-up predicate for the long render: exit 0 when it needs attention, 1 while it is healthy.

Exit 0 when all 1800 frames exist, when the render process (PID from renders/frames/render.pid) is gone,
or when no frame has finished for STALL_MIN minutes. Usage: python3 scripts/render_watch.py
"""
import glob
import os
import sys
import time

FRAMES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders", "frames")
STALL_MIN = 20


def alive():
    try:
        pid = int(open(os.path.join(FRAMES, "render.pid")).read().strip())
        cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ")
    except (OSError, ValueError):
        return False
    return b"blender" in cmd and b"render_animation.py" in cmd


def main():
    frames = glob.glob(os.path.join(FRAMES, "frame_*.png"))
    if len(frames) >= 1800:
        print(f"render complete: {len(frames)} frames")
        return 0
    if not alive():
        print(f"render process not running with {len(frames)}/1800 frames")
        return 0
    newest = max([os.path.getmtime(f) for f in frames] + [os.path.getmtime(os.path.join(FRAMES, "render.pid"))])
    idle = (time.time() - newest) / 60.0
    if idle > STALL_MIN:
        print(f"render stalled: no frame for {idle:.0f} min ({len(frames)}/1800 frames)")
        return 0
    print(f"rendering: {len(frames)}/1800 frames, last frame {idle:.1f} min ago")
    return 1


if __name__ == "__main__":
    sys.exit(main())
