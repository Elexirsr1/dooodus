"""Render, colour-management and output settings (Cycles CPU, 1920x1080 @ 120 fps, frames 1-1800)."""
import bpy

RES = (1920, 1080)
FPS = 120
FRAMES = (1, 1800)


def configure(scene, samples=96, adaptive_threshold=0.02, min_samples=24):
    r = scene.render
    r.engine = "CYCLES"
    cy = scene.cycles
    cy.device = "CPU"
    r.resolution_x, r.resolution_y = RES
    r.resolution_percentage = 100
    r.pixel_aspect_x = r.pixel_aspect_y = 1.0
    r.fps, r.fps_base = FPS, 1.0
    scene.frame_start, scene.frame_end = FRAMES
    scene.frame_step = 1

    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = adaptive_threshold
    cy.adaptive_min_samples = min_samples
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    cy.denoising_prefilter = "ACCURATE"
    cy.denoising_quality = "HIGH"
    cy.use_light_tree = True
    cy.max_bounces = 10
    cy.diffuse_bounces = 2
    cy.glossy_bounces = 4
    cy.transmission_bounces = 8
    cy.volume_bounces = 0
    cy.transparent_max_bounces = 32
    cy.sample_clamp_direct = 0.0
    cy.sample_clamp_indirect = 6.0
    cy.blur_glossy = 0.6
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.use_animated_seed = False  # residual noise stays put between frames instead of boiling
    cy.seed = 7
    cy.pixel_filter_type = "BLACKMAN_HARRIS"
    cy.filter_width = 1.5

    r.use_motion_blur = True
    r.motion_blur_shutter = 0.5    # 180 degree shutter at 120 fps
    r.use_persistent_data = True   # keep BVH/textures between frames of the animation
    r.film_transparent = False
    r.use_compositing = True
    r.use_sequencer = False
    r.dither_intensity = 1.0

    vs = scene.view_settings
    scene.display_settings.display_device = "sRGB"
    vs.view_transform = "AgX"
    try:
        vs.look = "AgX - Medium High Contrast"
    except TypeError:
        vs.look = "None"
    vs.exposure = 0.6
    vs.gamma = 1.0

    img = r.image_settings
    img.file_format = "PNG"
    img.color_mode = "RGB"
    img.color_depth = "8"
    img.compression = 15
    r.filepath = "//renders/frames/frame_"
    r.use_file_extension = True
    r.use_overwrite = True
    r.use_placeholder = False
    return scene
