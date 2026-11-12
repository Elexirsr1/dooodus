"""Full-resolution per-sample cost under specific toggles (2 vs 4 spp deltas, one session).

Usage: blender -b scene.blend -P scripts/profile_toggles.py -- --frame 1200
"""
import argparse
import sys
import time

import bpy


def per_sample(scene, label):
    cy = scene.cycles
    out = []
    for s in (2, 4):
        cy.samples = s
        t = time.time()
        bpy.ops.render.render(write_still=False)
        out.append(time.time() - t)
    ps = (out[1] - out[0]) / 2
    print(f"[toggle] {label:40s} per-sample {ps:5.2f}s  (2spp {out[0]:.1f}s, 4spp {out[1]:.1f}s)", flush=True)
    return ps


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--frame", type=int, default=1200)
    a = p.parse_args(argv)
    scene = bpy.context.scene
    cy = scene.cycles
    scene.frame_set(a.frame)
    scene.render.use_persistent_data = True
    cy.use_adaptive_sampling = False
    cy.use_denoising = False
    scene.render.use_compositing = False
    cy.samples = 1
    bpy.ops.render.render(write_still=False)  # warm-up
    per_sample(scene, "baseline")
    bpy.data.materials["Candle_Wick"].cycles.emission_sampling = "NONE"
    per_sample(scene, "wick emission sampling NONE")
    cy.diffuse_bounces = 0
    per_sample(scene, "+ diffuse bounces 0")
    cy.diffuse_bounces = 1
    links = []
    for o in scene.objects:
        if o.type == "LIGHT" and o.light_linking.receiver_collection is not None:
            links.append((o, o.light_linking.receiver_collection))
            o.light_linking.receiver_collection = None
    per_sample(scene, f"light linking removed ({len(links)} lights)")
    for o, c in links:
        o.light_linking.receiver_collection = c
    cy.use_light_tree = False
    per_sample(scene, "light tree off")
    cy.use_light_tree = True
    hidden = [o for o in scene.objects if o.name.startswith("CandleLight_")]
    for o in hidden:
        o.hide_render = True
    per_sample(scene, "candle lights hidden")
    for o in hidden:
        o.hide_render = False
    cy.max_bounces = 1
    per_sample(scene, "max bounces 1 (direct + 1)")


if __name__ == "__main__":
    main()
