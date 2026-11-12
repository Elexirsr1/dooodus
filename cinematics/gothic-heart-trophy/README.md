# Gothic Heart Trophy — cinematic Blender scene

A 15-second Gothic dark-fantasy cinematic built entirely with the Blender Python API (Blender 4.5.16 LTS,
Cycles). A polished silver trophy crowned by a faceted ruby heart and a sunburst of blades stands on a
black-and-gold marble altar, in front of a black heraldic shield with a glowing gold crown, inside a
stained-glass cathedral.

| | |
|---|---|
| Resolution | 1920 × 1080 |
| Frame rate | 120 fps |
| Frames | 1 – 1800 (15.000 s) |
| Engine | Cycles (CPU), AgX view transform, *Medium High Contrast* look |
| Video | H.264 High @ L5.2, yuv420p, BT.709, CRF 15 (`output/gothic_heart_trophy_1080p120.mp4`) |

## Files

- `gothic_heart_trophy.blend` — the complete, editable scene. All textures and the font are packed, so it
  opens anywhere without the `assets/` folder.
- `scripts/` — everything that builds, renders, verifies and encodes the project (see below).
- `assets/` — the external sources that are packed into the .blend: three CC0 PBR texture sets from
  [Poly Haven](https://polyhaven.com) (`large_floor_tiles_02`, `stone_block_wall`, `granite_tile`;
  diffuse, roughness and OpenGL normal maps at 2K) and the SIL OFL font *UnifrakturMaguntia* for the plaque.
- `renders/previews/` — full-quality stills of the key moments, taken from the final render.
- `renders/verify_scene.json` — results of the automated scene/camera checks.

## Rebuilding and rendering

```bash
python3 scripts/fetch_assets.py                                   # only needed if assets/ is missing
blender -b --factory-startup -P scripts/build_scene.py            # writes gothic_heart_trophy.blend
blender -b gothic_heart_trophy.blend -P scripts/verify_scene.py   # timeline, packing, camera checks
blender -b gothic_heart_trophy.blend -P scripts/render_animation.py -- --start 1 --end 1800
python3 scripts/encode_video.py                                   # PNG sequence -> MP4 + ffprobe check
python3 scripts/make_previews.py                                  # key-moment stills
```

`render_animation.py` is resumable: it skips frames that already exist and writes each frame atomically.
`render_previews.py` renders arbitrary stills at any resolution/sample count for look development.

## Scene structure

| Collection | Contents |
|---|---|
| Architecture | Nave floor, carpet runner, octagonal slate dais, marble altar with a gilded blind arcade, 18 clustered piers, arcade arches and clerestory walls, aisle/apse/west walls, ribbed vault, and the reredos (pinnacles, gilded crockets, crimson velvet drape) whose niche holds the shield |
| Windows | 38 traceried windows (lancets with oculus/quatrefoil tracery and a west rose) with a procedural leaded stained-glass shader |
| Trophy | Octagonal stepped silver base with bead moulding and a blackletter *Slay* plaque, faceted black-enamel/silver stem, brilliant-faceted ruby heart with a glowing core and beaded bezel, sunburst of blades and four-point stars |
| Shield | Curved heater shield (iron rim, gold inlay, hammered black lacquer), faceted gold W-crown with a star and ruby cabochons, ember-tinted thorn vines — after the reference |
| Props | 62 wax candles with animated flames and flickering lights, six wrought-iron candelabras, black and red roses, scattered petals |
| Lighting | Exterior sun spots shining through the stained glass (coloured pools on the floor), five fake volumetric light shafts, light-linked softboxes/rims for the trophy and shield, the ruby's red glow, cool fills |
| Atmosphere | ~7,000 drifting dust motes (geometry nodes, kept away from the lens) |
| Camera_Rig | `CAM_Pivot` (azimuth) → `CAM_Main` (distance/height) tracking `CAM_Aim` (also the focus target) |

## Camera

Timeline markers name each segment. Every channel is keyed with exact cubic-Hermite Bézier handles; the
position channels use clamped C2 splines (continuous acceleration), aim/lens/f-stop use overshoot-free
monotone curves.

| Frames | Time | Move |
|---|---|---|
| 1 – 360 | 0 – 3 s | Slow approach down the nave toward the altar (30 → 36 mm) |
| 361 – 720 | 3 – 6 s | Push into a close-up of the ruby heart (≈60 mm, f/2.4), drifting across its facets |
| 721 – 1680 | 6 – 14 s | One continuous orbit, exactly 360° of azimuth between frames 721 and 1680 |
| 1681 – 1800 | 14 – 15 s | Settles into a low, frontal hero angle with the crown framing the heart, then holds |

`scripts/verify_scene.py` checks every frame: exact 360° orbit, camera clearance from all geometry
(≥ 0.88 m) and from the trophy (≥ 1.0 m), the lens never enters a light-shaft volume, the heart is never
occluded or out of frame, the full trophy stays in frame from frame 900 onward, plus speed/acceleration/jerk
statistics.

## Render settings and why

Rendering happened on a 2-vCPU CPU-only machine, so the scene was profiled and tuned for cost without
touching resolution, frame rate, duration or the camera move:

- 4 samples per pixel with OpenImageDenoise (albedo + normal, *High* quality, accurate prefilter),
  fixed seed so residual noise does not boil; ~9 s per full-frame sample pass + ~9 s denoise.
- Bounces: diffuse 1, glossy 2, transmission 4, transparent 16; indirect clamp 4; filter glossy 1.0;
  caustics off. Persistent data keeps the BVH between frames. Motion blur off (a 180° shutter at 120 fps
  is only 1/240 s).
- Stone uses per-face planar UVs with tangent-space normal maps instead of box projection + bump;
  stained glass evaluates a one-Voronoi pattern for shadow rays and the full leaded pattern only for
  camera/glossy rays; candle wax fakes subsurface glow with an emission falloff; the light shafts are
  additive emissive prisms (cheap and temporally stable) rather than a scattering volume.
- Fog, bloom, a faint anamorphic streak, slight chromatic aberration, vignette and a gentle grade are done
  in the compositor (≈0.3 s per frame). The layered fog is mist depth × a height falloff, coloured by a
  heavily blurred copy of the frame so it glows near windows and flames.
