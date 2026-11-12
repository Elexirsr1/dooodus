"""Render one frame at full resolution with explicit quality settings (fresh session, for A/B quality tests).

Usage: blender -b scene.blend -P scripts/quality_test.py -- --frame 600 --samples 4 --diffuse 1 --out x.png
"""
import argparse
import sys
import time

import bpy


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--frame", type=int, required=True)
    p.add_argument("--samples", type=int, default=4)
    p.add_argument("--min-samples", type=int, default=0)
    p.add_argument("--threshold", type=float, default=0.0)
    p.add_argument("--diffuse", type=int, default=1)
    p.add_argument("--quality", default="HIGH")
    p.add_argument("--percent", type=int, default=100)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    scene = bpy.context.scene
    cy = scene.cycles
    scene.frame_set(a.frame)
    scene.render.resolution_percentage = a.percent
    scene.render.use_persistent_data = False
    cy.samples = a.samples
    cy.use_adaptive_sampling = a.threshold > 0
    if a.threshold > 0:
        cy.adaptive_threshold = a.threshold
        cy.adaptive_min_samples = a.min_samples or max(1, a.samples // 2)
    cy.diffuse_bounces = a.diffuse
    cy.denoising_quality = a.quality
    scene.render.filepath = a.out
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"[quality] frame {a.frame} spp {a.samples} diffuse {a.diffuse} {a.quality} -> {time.time() - t:.1f}s", flush=True)


if __name__ == "__main__":
    main()
