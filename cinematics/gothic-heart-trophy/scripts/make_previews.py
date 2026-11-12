"""Extract the key-moment preview stills from the final rendered frames (full quality, 1920x1080).

Writes renders/previews/NN_<moment>_fXXXX.jpg plus a contact sheet. Usage: python3 scripts/make_previews.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES = os.path.join(ROOT, "renders", "frames")
OUT = os.path.join(ROOT, "renders", "previews")
MOMENTS = [
    (1, "approach_start"), (300, "approach"), (560, "heart_closeup"), (680, "heart_facets"),
    (900, "orbit_reveal"), (1200, "orbit_rear"), (1500, "orbit_side"), (1800, "hero_shot"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for i, (f, name) in enumerate(MOMENTS, 1):
        src = os.path.join(FRAMES, f"frame_{f:04d}.png")
        if not os.path.exists(src):
            print(f"skip {f}: not rendered yet")
            continue
        dst = os.path.join(OUT, f"{i:02d}_{name}_f{f:04d}.jpg")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-q:v", "2", dst], check=True)
        made.append(dst)
        print("wrote", os.path.relpath(dst, ROOT))
    if len(made) == len(MOMENTS):
        inputs = []
        for p in made:
            inputs += ["-i", p]
        scale = "".join(f"[{k}:v]scale=640:360[v{k}];" for k in range(8))
        stack = "[v0][v1][v2][v3]hstack=4[a];[v4][v5][v6][v7]hstack=4[b];[a][b]vstack=2[o]"
        sheet = os.path.join(OUT, "contact_sheet.jpg")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex",
                        scale + stack, "-map", "[o]", "-q:v", "3", sheet], check=True)
        print("wrote", os.path.relpath(sheet, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
