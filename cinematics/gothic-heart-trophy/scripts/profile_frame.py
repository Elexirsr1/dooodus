"""Full-resolution cost breakdown in one session: per-sample time, denoiser and compositor overhead.

Usage: blender -b scene.blend -P scripts/profile_frame.py -- --frame 1200 [--hide-beams]
"""
import argparse
import sys
import time

import bpy


def timed(scene, label):
    t = time.time()
    bpy.ops.render.render(write_still=False)
    dt = time.time() - t
    print(f"[frame-profile] {label}: {dt:.2f}s", flush=True)
    return dt


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--frame", type=int, default=1200)
    p.add_argument("--hide-beams", action="store_true")
    a = p.parse_args(argv)
    scene = bpy.context.scene
    cy = scene.cycles
    scene.frame_set(a.frame)
    scene.render.resolution_percentage = 100
    scene.render.use_persistent_data = True
    cy.use_adaptive_sampling = False
    if a.hide_beams:
        for o in scene.objects:
            if o.name.endswith("_Beam"):
                o.hide_render = True

    def setup(samples, denoise, comp, quality="HIGH"):
        cy.samples = samples
        cy.use_denoising = denoise
        cy.denoising_quality = quality
        scene.render.use_compositing = comp

    setup(1, False, False)
    timed(scene, "warm-up 1 spp (BVH + shaders)")
    setup(2, False, False)
    t2 = timed(scene, "2 spp raw")
    setup(6, False, False)
    t6 = timed(scene, "6 spp raw")
    print(f"[frame-profile] per-sample {(t6 - t2) / 4:.2f}s, fixed overhead {t2 - 2 * (t6 - t2) / 4:.2f}s", flush=True)
    setup(2, True, False, "HIGH")
    print(f"[frame-profile] OIDN HIGH cost ~{timed(scene, '2 spp + OIDN HIGH') - t2:.2f}s", flush=True)
    setup(2, True, False, "BALANCED")
    print(f"[frame-profile] OIDN BALANCED cost ~{timed(scene, '2 spp + OIDN BALANCED') - t2:.2f}s", flush=True)
    setup(2, False, True)
    print(f"[frame-profile] compositor cost ~{timed(scene, '2 spp + compositor') - t2:.2f}s", flush=True)


if __name__ == "__main__":
    main()
