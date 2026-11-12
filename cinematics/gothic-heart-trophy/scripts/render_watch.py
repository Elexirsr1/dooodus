"""Exit 0 when the animation render is complete or no render process is alive; exit 1 while it runs.

Used as a wake-up predicate while the long render runs: python3 scripts/render_watch.py
"""
import glob
import os
import subprocess
import sys

FRAMES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders", "frames")


def main():
    done = len(glob.glob(os.path.join(FRAMES, "frame_*.png")))
    if done >= 1800:
        print(f"render complete: {done} frames")
        return 0
    running = subprocess.run(["pgrep", "-f", "render_animation.py"], capture_output=True).returncode == 0
    if not running:
        print(f"render process not running with {done}/1800 frames")
        return 0
    print(f"rendering: {done}/1800 frames")
    return 1


if __name__ == "__main__":
    sys.exit(main())
