"""Download the CC0 assets used by the scene (Poly Haven textures, OFL blackletter font).

Run with any Python 3:  python3 scripts/fetch_assets.py
Files land in assets/ and are packed into the .blend by build_scene.py, so this only
needs to run when rebuilding the scene from scratch.
"""
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_DIR = os.path.join(ROOT, "assets", "textures")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

# asset id -> resolution
TEXTURES = {
    "large_floor_tiles_02": "2k",
    "stone_block_wall": "2k",
    "granite_tile": "2k",
}
# Displacement (not a tangent-space normal map) because materials use box projection
# without UVs; the height map drives a Bump node instead.
MAPS = {"Diffuse": "diff", "Displacement": "disp", "Rough": "rough"}

FONTS = {
    # SIL Open Font License, Google Fonts repository
    "UnifrakturMaguntia-Book.ttf":
        "https://github.com/google/fonts/raw/main/ofl/unifrakturmaguntia/UnifrakturMaguntia-Book.ttf",
}


def fetch(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        print("exists", os.path.relpath(dst, ROOT))
        return
    req = urllib.request.Request(url, headers={"User-Agent": "gothic-heart-trophy/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dst, "wb") as f:
        f.write(r.read())
    print("fetched", os.path.relpath(dst, ROOT), os.path.getsize(dst))


def main():
    os.makedirs(TEX_DIR, exist_ok=True)
    os.makedirs(FONT_DIR, exist_ok=True)
    for asset, res in TEXTURES.items():
        req = urllib.request.Request("https://api.polyhaven.com/files/" + asset,
                                     headers={"User-Agent": "gothic-heart-trophy/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            files = json.load(r)
        for key, short in MAPS.items():
            url = files[key][res]["jpg"]["url"]
            fetch(url, os.path.join(TEX_DIR, f"{asset}_{short}_{res}.jpg"))
    for name, url in FONTS.items():
        fetch(url, os.path.join(FONT_DIR, name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
