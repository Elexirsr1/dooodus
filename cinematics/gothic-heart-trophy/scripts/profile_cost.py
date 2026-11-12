"""A/B profile render cost by toggling scene components (low resolution, fixed samples, one session).

Usage: blender -b scene.blend -P scripts/profile_cost.py -- --frame 1200 --percent 25 --samples 8
"""
import argparse
import sys
import time

import bpy


def render_time(scene):
    t = time.time()
    bpy.ops.render.render(write_still=False)
    return time.time() - t


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--frame", type=int, default=1200)
    p.add_argument("--percent", type=int, default=25)
    p.add_argument("--samples", type=int, default=8)
    a = p.parse_args(argv)
    scene = bpy.context.scene
    scene.frame_set(a.frame)
    scene.render.resolution_percentage = a.percent
    scene.cycles.samples = a.samples
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.render.use_compositing = False
    scene.render.use_persistent_data = False

    def objs(pred):
        return [o for o in scene.objects if pred(o)]

    groups = {
        "dust": objs(lambda o: o.name == "Dust_Motes"),
        "beams": objs(lambda o: o.name.endswith("_Beam")),
        "window_glass": objs(lambda o: o.name.startswith("Window_") and o.name.endswith("_Glass")),
        "flames": objs(lambda o: o.name.startswith("Flame_")),
        "candle_lights": objs(lambda o: o.name.startswith("CandleLight_")),
        "window_suns": objs(lambda o: o.name.endswith("_Sun")),
        "area_lights": objs(lambda o: o.type == "LIGHT" and o.data.type == "AREA"),
        "roses": objs(lambda o: o.name.startswith(("Rose_", "Petal_"))),
        "candles": objs(lambda o: o.name.startswith(("Candle_", "Candelabra_"))),
    }
    base = render_time(scene)  # warm-up (shader compile, BVH)
    base = render_time(scene)
    print(f"[profile] baseline {base:.2f}s", flush=True)
    for name, obs in groups.items():
        for o in obs:
            o.hide_render = True
        t = render_time(scene)
        for o in obs:
            o.hide_render = False
        print(f"[profile] without {name:14s} ({len(obs):3d} obj): {t:.2f}s  ({(base - t) / base * 100:+.0f}% saved)",
              flush=True)
    w = scene.world
    old = w.cycles.sampling_method
    w.cycles.sampling_method = "NONE"
    t = render_time(scene)
    w.cycles.sampling_method = old
    print(f"[profile] world sampling NONE: {t:.2f}s ({(base - t) / base * 100:+.0f}%)", flush=True)
    cy = scene.cycles
    saved = (cy.glossy_bounces, cy.diffuse_bounces, cy.transmission_bounces)
    cy.glossy_bounces, cy.diffuse_bounces, cy.transmission_bounces = 1, 0, 4
    t = render_time(scene)
    cy.glossy_bounces, cy.diffuse_bounces, cy.transmission_bounces = saved
    print(f"[profile] bounces g1 d0 t4: {t:.2f}s ({(base - t) / base * 100:+.0f}%)", flush=True)
    mats = {}
    for m in bpy.data.materials:
        mats[m.name] = m
    # replace every material with a plain diffuse to see the shading share
    plain = bpy.data.materials.new("PLAIN")
    swaps = []
    for o in scene.objects:
        if o.type in {"MESH", "FONT"}:
            for s in o.material_slots:
                swaps.append((s, s.link, s.material))
    for s, link, m in swaps:
        s.material = plain
    t = render_time(scene)
    for s, link, m in swaps:
        s.material = m
    print(f"[profile] all materials plain: {t:.2f}s ({(base - t) / base * 100:+.0f}%)", flush=True)


if __name__ == "__main__":
    main()
