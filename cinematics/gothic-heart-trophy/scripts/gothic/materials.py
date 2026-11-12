"""PBR material library for the Gothic Heart Trophy scene (Cycles).

Shaders are tuned for CPU render cost: UV-mapped textures with tangent-space normal maps, low-octave
noise, a cheap shadow-ray branch for stained glass and faked candle translucency."""
import bpy

from .util import NodeBuilder, load_image, new_material, principled

_CACHE = {}
STONE = ("stone_floor", "stone_wall", "stone_carved", "stone_slate")


def get(name):
    """Return a cached material by key, building it on first use."""
    if name not in _CACHE:
        _CACHE[name] = BUILDERS[name]()
    return _CACHE[name]


def stone_material_names():
    return {get(k).name for k in STONE}


def _noise(nb, vec, scale, detail=2.0, rough=0.55, loc=(-900, -300), dims="3D", w=None):
    n = nb.new("ShaderNodeTexNoise", loc, props={"noise_dimensions": dims},
               inputs={"Scale": scale, "Detail": detail, "Roughness": rough})
    if vec is not None:
        nb.set(n, "Vector", vec)
    if w is not None:
        nb.set(n, "W", w)
    return n


def _gray(nb, value, loc):
    return nb.new("ShaderNodeCombineXYZ", loc, inputs={"X": value, "Y": value, "Z": value}).outputs[0]


# ----------------------------------------------------------------------------- metals

def silver():
    mat, nb, out = new_material("Silver_Polished")
    tc = nb.new("ShaderNodeTexCoord", (-1200, 0))
    smudge = _noise(nb, tc.outputs["Object"], 9.0, 2.0, 0.6, (-950, -200))
    rough = nb.map_range(smudge.outputs["Fac"], 0.3, 0.75, 0.11, 0.19, (-650, -200))
    bsdf = principled(nb, (300, 0), base=(0.955, 0.945, 0.925), metallic=1.0, roughness=rough,
                      spec_tint=(0.99, 0.98, 0.96))
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


def black_enamel():
    mat, nb, out = new_material("Black_Enamel")
    bsdf = principled(nb, (300, 0), base=(0.006, 0.006, 0.007), metallic=0.0, roughness=0.06, spec=0.6,
                      coat=0.6, coat_rough=0.03)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


def gold():
    mat, nb, out = new_material("Gold_Polished")
    tc = nb.new("ShaderNodeTexCoord", (-1200, 0))
    smudge = _noise(nb, tc.outputs["Object"], 14.0, 2.0, 0.6, (-950, -200))
    rough = nb.map_range(smudge.outputs["Fac"], 0.3, 0.75, 0.12, 0.24, (-650, -200))
    bsdf = principled(nb, (300, 0), base=(0.95, 0.64, 0.25), metallic=1.0, roughness=rough,
                      spec_tint=(1.0, 0.86, 0.58))
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


def gold_emblem():
    """Heraldic gold with a faint molten glow toward grazing edges (after the glowing reference crown)."""
    mat, nb, out = new_material("Gold_Emblem_Glow")
    tc = nb.new("ShaderNodeTexCoord", (-1200, 0))
    smudge = _noise(nb, tc.outputs["Object"], 14.0, 2.0, 0.6, (-950, -200))
    rough = nb.map_range(smudge.outputs["Fac"], 0.3, 0.75, 0.12, 0.22, (-650, -200))
    lw = nb.new("ShaderNodeLayerWeight", (-950, 250), inputs={"Blend": 0.45})
    glow = nb.map_range(lw.outputs["Facing"], 0.0, 1.0, 0.35, 1.6, (-650, 250))
    bsdf = principled(nb, (300, 0), base=(0.95, 0.62, 0.22), metallic=1.0, roughness=rough,
                      spec_tint=(1.0, 0.84, 0.52), emission=(1.0, 0.40, 0.09), emission_strength=glow)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    mat.cycles.emission_sampling = "NONE"
    return mat


def iron():
    mat, nb, out = new_material("Iron_Wrought")
    tc = nb.new("ShaderNodeTexCoord", (-1200, 0))
    n = _noise(nb, tc.outputs["Object"], 22.0, 2.0, 0.62, (-950, -200))
    rough = nb.map_range(n.outputs["Fac"], 0.3, 0.7, 0.34, 0.62, (-650, -200))
    col = nb.mix_color("MIX", nb.map_range(n.outputs["Fac"], 0.45, 0.7, 0.0, 1.0, (-650, 100)),
                       (0.030, 0.028, 0.026, 1), (0.055, 0.040, 0.030, 1), (-400, 100))
    bsdf = principled(nb, (300, 0), base=col, metallic=0.85, roughness=rough)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


# ----------------------------------------------------------------------------- gems / emission

def ruby():
    mat, nb, out = new_material("Ruby_Gem")
    bsdf = principled(nb, (300, 0), base=(1.0, 0.16, 0.12), roughness=0.0, ior=1.76, transmission=1.0,
                      spec=0.5)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    vol = nb.new("ShaderNodeVolumeAbsorption", (300, -300), inputs={"Color": (0.96, 0.05, 0.035, 1),
                                                                    "Density": 34.0})
    nb.link(vol.outputs[0], out.inputs["Volume"])
    mat.cycles.homogeneous_volume = True
    return mat


def gem_core():
    mat, nb, out = new_material("Gem_Core_Glow")
    tc = nb.new("ShaderNodeTexCoord", (-900, 0))
    n = _noise(nb, tc.outputs["Object"], 40.0, 2.0, 0.5, (-700, 0))
    strength = nb.map_range(n.outputs["Fac"], 0.3, 0.7, 0.55, 1.3, (-450, 0))
    em = nb.new("ShaderNodeEmission", (300, 0), inputs={"Color": (1.0, 0.035, 0.008, 1), "Strength": strength})
    nb.link(em.outputs[0], out.inputs["Surface"])
    mat.cycles.emission_sampling = "NONE"
    return mat


def flame():
    """Candle flame: blue root, orange body, hot yellow core; soft transparent edges."""
    mat, nb, out = new_material("Candle_Flame")
    tc = nb.new("ShaderNodeTexCoord", (-1400, 0))
    sep = nb.new("ShaderNodeSeparateXYZ", (-1200, 0), inputs={"Vector": tc.outputs["Object"]})
    h = sep.outputs["Z"]  # the flame mesh is 1 unit tall in object space (scaled per candle)
    ramp = nb.ramp(h, [(0.0, (0.10, 0.18, 1.0)), (0.07, (0.55, 0.32, 0.55)), (0.16, (1.0, 0.42, 0.06)),
                       (0.42, (1.0, 0.78, 0.38)), (0.80, (1.0, 0.50, 0.10)), (1.0, (0.85, 0.20, 0.02))],
                   (-800, 0))
    lw = nb.new("ShaderNodeLayerWeight", (-1000, -300), inputs={"Blend": 0.35})
    face = nb.math("SUBTRACT", 1.0, lw.outputs["Facing"], (-800, -300))
    core = nb.math("POWER", face, 1.6, (-600, -300))
    strength = nb.math("MULTIPLY", core, 38.0, (-400, -300))
    alpha = nb.math("POWER", face, 0.9, (-600, -500))
    root = nb.map_range(h, 0.0, 0.12, 0.25, 1.0, (-400, -550))
    alpha2 = nb.math("MULTIPLY", alpha, root, (-200, -500))
    em = nb.new("ShaderNodeEmission", (0, 0), inputs={"Color": ramp.outputs["Color"], "Strength": strength})
    tr = nb.new("ShaderNodeBsdfTransparent", (0, -200))
    mix = nb.new("ShaderNodeMixShader", (400, 0), inputs={"Fac": alpha2})
    nb.link(tr.outputs[0], mix.inputs[1])
    nb.link(em.outputs[0], mix.inputs[2])
    nb.link(mix.outputs[0], out.inputs["Surface"])
    mat.cycles.emission_sampling = "NONE"
    return mat


def wick():
    mat, nb, out = new_material("Candle_Wick")
    tc = nb.new("ShaderNodeTexCoord", (-900, 0))
    sep = nb.new("ShaderNodeSeparateXYZ", (-700, 0), inputs={"Vector": tc.outputs["Object"]})
    top = nb.new("ShaderNodeAttribute", (-900, 300), props={"attribute_type": "OBJECT", "attribute_name": "candle_top"})
    rel = nb.math("SUBTRACT", sep.outputs["Z"], top.outputs["Fac"], (-500, 100))
    glow = nb.map_range(rel, 0.0, 0.006, 0.0, 6.0, (-300, 0))
    bsdf = principled(nb, (200, 0), base=(0.01, 0.009, 0.008), roughness=0.8, emission=(1.0, 0.3, 0.05),
                      emission_strength=glow)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


# ----------------------------------------------------------------------------- stone

def _textured_stone(name, prefix, size_m, hue_sat_val=(0.5, 1.0, 1.0), tint=(1, 1, 1), rough=(0.45, 0.9),
                    normal=0.8, variation=(0.75, 1.1), dirt=0.35, spec=0.5):
    """UV-mapped PBR stone: diffuse + roughness + OpenGL normal map, broken up by one large noise."""
    mat, nb, out = new_material(name)
    uvn = nb.new("ShaderNodeUVMap", (-1800, 0), props={"uv_map": "UVMap"})
    mapping = nb.new("ShaderNodeMapping", (-1600, 0), inputs={"Vector": uvn.outputs["UV"],
                                                               "Scale": (1.0 / size_m,) * 3})

    def img(kind, cs, loc):
        n = nb.new("ShaderNodeTexImage", loc, props={"interpolation": "Linear"})
        n.image = load_image(f"{prefix}_{kind}_2k.jpg", cs)
        nb.set(n, "Vector", mapping.outputs["Vector"])
        return n

    diff = img("diff", "sRGB", (-1300, 300))
    rgh = img("rough", "Non-Color", (-1300, 0))
    nor = img("nor_gl", "Non-Color", (-1300, -300))
    hsv = nb.new("ShaderNodeHueSaturation", (-1000, 300), inputs={
        "Hue": hue_sat_val[0], "Saturation": hue_sat_val[1], "Value": hue_sat_val[2],
        "Color": diff.outputs["Color"]})
    tc = nb.new("ShaderNodeTexCoord", (-1600, 700))
    big = _noise(nb, tc.outputs["Object"], 0.45, 2.0, 0.6, (-1300, 650))
    var = nb.map_range(big.outputs["Fac"], 0.3, 0.7, variation[0], variation[1], (-1000, 650))
    grime = nb.map_range(big.outputs["Fac"], 0.56, 0.74, 0.0, dirt, (-1000, 900))
    col = nb.mix_color("MULTIPLY", 1.0, hsv.outputs["Color"], tuple(tint) + (1,), (-750, 300))
    col = nb.mix_color("MULTIPLY", 1.0, col, _gray(nb, var, (-750, 650)), (-550, 400))
    col = nb.mix_color("MIX", grime, col, (0.012, 0.010, 0.009, 1), (-350, 400))
    r = nb.map_range(rgh.outputs["Color"], 0.0, 1.0, rough[0], rough[1], (-750, 0))
    r = nb.math("ADD", r, nb.math("MULTIPLY", grime, 0.25, (-750, -150)), (-550, 0), clamp=True)
    nmap = nb.new("ShaderNodeNormalMap", (-550, -300), props={"space": "TANGENT", "uv_map": "UVMap"},
                  inputs={"Strength": normal, "Color": nor.outputs["Color"]})
    bsdf = principled(nb, (200, 0), base=col, roughness=r, normal=nmap.outputs["Normal"], spec=spec)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


def stone_floor():
    # 3 m texture of 1 m tiles, darkened and cooled for the nave floor; slightly polished by wear
    return _textured_stone("Stone_Floor", "large_floor_tiles_02", 3.0, (0.5, 0.55, 0.42), (0.92, 0.95, 1.0),
                           rough=(0.22, 0.62), normal=0.7, variation=(0.6, 1.15), dirt=0.55)


def stone_wall():
    return _textured_stone("Stone_Wall", "stone_block_wall", 2.1, (0.5, 0.22, 0.62), (0.95, 0.93, 0.9),
                           rough=(0.55, 0.95), normal=1.0, variation=(0.65, 1.15), dirt=0.45)


def stone_carved():
    """Smoother dressed stone for piers, tracery and the reredos."""
    return _textured_stone("Stone_Carved", "stone_block_wall", 4.2, (0.5, 0.18, 0.72), (0.95, 0.93, 0.9),
                           rough=(0.45, 0.85), normal=0.5, variation=(0.7, 1.12), dirt=0.35)


def stone_slate():
    return _textured_stone("Stone_Slate_Dais", "granite_tile", 2.3, (0.5, 0.6, 0.55), (0.95, 0.95, 1.0),
                           rough=(0.12, 0.42), normal=0.6, variation=(0.7, 1.1), dirt=0.3)


def black_marble():
    """Polished black marble with fine gold and smoke veins (altar)."""
    mat, nb, out = new_material("Marble_Black_Gold")
    tc = nb.new("ShaderNodeTexCoord", (-1800, 0))
    warp = _noise(nb, tc.outputs["Object"], 1.4, 3.0, 0.62, (-1600, -200))
    wv = nb.vmath("SCALE", warp.outputs["Color"], None, (-1400, -200))
    wv.node.inputs["Scale"].default_value = 0.9
    pos = nb.vmath("ADD", tc.outputs["Object"], wv, (-1200, 0))
    wave = nb.new("ShaderNodeTexWave", (-1000, 0), props={"wave_type": "BANDS", "bands_direction": "DIAGONAL"},
                  inputs={"Vector": pos, "Scale": 1.1, "Distortion": 6.0, "Detail": 3.0, "Detail Scale": 1.5,
                          "Detail Roughness": 0.6})
    vein = nb.map_range(wave.outputs["Fac"], 0.0, 0.035, 1.0, 0.0, (-800, 0))
    smoke = nb.map_range(warp.outputs["Fac"], 0.5, 0.72, 0.0, 0.3, (-800, -400))
    col = nb.mix_color("MIX", smoke, (0.016, 0.015, 0.017, 1), (0.05, 0.048, 0.052, 1), (-550, -200))
    col = nb.mix_color("MIX", vein, col, (0.55, 0.36, 0.12, 1), (-350, 0))
    metal = nb.math("MULTIPLY", vein, 0.9, (-350, -350))
    rough = nb.map_range(vein, 0.0, 1.0, 0.07, 0.2, (-350, -500))
    bsdf = principled(nb, (200, 0), base=col, metallic=metal, roughness=rough, spec=0.55)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


# ----------------------------------------------------------------------------- fabrics / organics

def _velvet(name, base, sheen_tint, rough=0.85, translucent=0.0):
    mat, nb, out = new_material(name)
    tc = nb.new("ShaderNodeTexCoord", (-1000, 0))
    n = _noise(nb, tc.outputs["Object"], 18.0, 2.0, 0.6, (-800, -200))
    var = nb.map_range(n.outputs["Fac"], 0.3, 0.7, 0.8, 1.1, (-600, -200))
    col = nb.mix_color("MULTIPLY", 1.0, tuple(base) + (1,), _gray(nb, var, (-600, 0)), (-400, 0))
    bsdf = principled(nb, (100, 0), base=col, roughness=rough, sheen=1.0, sheen_rough=0.32,
                      sheen_tint=tuple(sheen_tint) + (1,), spec=0.25)
    if translucent > 0:
        tl = nb.new("ShaderNodeBsdfTranslucent", (100, -400), inputs={"Color": col})
        mix = nb.new("ShaderNodeMixShader", (500, 0), inputs={"Fac": translucent})
        nb.link(bsdf.outputs[0], mix.inputs[1])
        nb.link(tl.outputs[0], mix.inputs[2])
        nb.link(mix.outputs[0], out.inputs["Surface"])
    else:
        nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


def velvet_crimson():
    return _velvet("Velvet_Crimson", (0.13, 0.004, 0.009), (0.9, 0.18, 0.22))


def rose_red():
    return _velvet("Rose_Petal_Red", (0.30, 0.004, 0.014), (1.0, 0.25, 0.30), rough=0.7, translucent=0.18)


def rose_black():
    return _velvet("Rose_Petal_Black", (0.010, 0.003, 0.005), (0.30, 0.06, 0.09), rough=0.65, translucent=0.05)


def leaf():
    mat, nb, out = new_material("Rose_Leaf")
    bsdf = principled(nb, (100, 0), base=(0.006, 0.018, 0.006), roughness=0.42, sheen=0.4,
                      sheen_tint=(0.4, 0.5, 0.4, 1))
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


def carpet():
    """Crimson velvet runner with a gold embroidered border (border keyed off object-space X)."""
    mat, nb, out = new_material("Carpet_Runner")
    tc = nb.new("ShaderNodeTexCoord", (-1400, 0))
    sep = nb.new("ShaderNodeSeparateXYZ", (-1200, 0), inputs={"Vector": tc.outputs["Object"]})
    ax = nb.math("ABSOLUTE", sep.outputs["X"], None, (-1000, 0))
    border = nb.map_range(ax, 0.985, 0.99, 0.0, 1.0, (-800, 0))
    inner_line = nb.math("MULTIPLY", nb.map_range(ax, 0.925, 0.93, 0.0, 1.0, (-800, -200)),
                         nb.map_range(ax, 0.945, 0.94, 1.0, 0.0, (-800, -400)), (-600, -300))
    trim = nb.math("MAXIMUM", border, inner_line, (-400, -100))
    n = _noise(nb, tc.outputs["Object"], 25.0, 2.0, 0.6, (-1000, 400))
    var = nb.map_range(n.outputs["Fac"], 0.3, 0.7, 0.75, 1.1, (-800, 400))
    base_red = nb.mix_color("MULTIPLY", 1.0, (0.10, 0.003, 0.007, 1), _gray(nb, var, (-500, 500)), (-300, 400))
    col = nb.mix_color("MIX", trim, base_red, (0.26, 0.15, 0.035, 1), (-100, 300))
    sheen_tint = nb.mix_color("MIX", trim, (0.9, 0.2, 0.25, 1), (1.0, 0.8, 0.4, 1), (-100, 0))
    metal = nb.math("MULTIPLY", trim, 0.6, (-100, -200))
    rough = nb.map_range(trim, 0.0, 1.0, 0.9, 0.35, (-100, -400))
    bsdf = principled(nb, (300, 0), base=col, roughness=rough, metallic=metal, sheen=1.0, sheen_rough=0.35,
                      sheen_tint=sheen_tint, spec=0.25)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


def _wax(name, base, glow=(1.0, 0.42, 0.12), glow_strength=1.6):
    """Wax without subsurface rays: the flame-lit top glows through an emission falloff instead.

    Each candle object carries a `candle_top` property (object-space height of its rim)."""
    mat, nb, out = new_material(name)
    tc = nb.new("ShaderNodeTexCoord", (-900, 0))
    sep = nb.new("ShaderNodeSeparateXYZ", (-700, 0), inputs={"Vector": tc.outputs["Object"]})
    top = nb.new("ShaderNodeAttribute", (-900, 300), props={"attribute_type": "OBJECT", "attribute_name": "candle_top"})
    depth = nb.math("MAXIMUM", nb.math("SUBTRACT", top.outputs["Fac"], sep.outputs["Z"], (-500, 200)), 0.0, (-350, 200))
    falloff = nb.math("EXPONENT", nb.math("MULTIPLY", depth, -1.0 / 0.028, (-200, 200)), None, (-50, 200))
    strength = nb.math("MULTIPLY", falloff, glow_strength, (100, 250))
    bsdf = principled(nb, (300, 0), base=tuple(base) + (1,), roughness=0.4, spec=0.4, emission=tuple(glow) + (1,),
                      emission_strength=strength)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    mat.cycles.emission_sampling = "NONE"
    return mat


def wax_ivory():
    return _wax("Wax_Ivory", (0.50, 0.42, 0.30))


def wax_red():
    return _wax("Wax_Red", (0.32, 0.012, 0.016), (1.0, 0.18, 0.06), 1.2)


def wax_black():
    return _wax("Wax_Black", (0.02, 0.016, 0.016), (0.8, 0.22, 0.06), 0.5)


def shield_lacquer():
    mat, nb, out = new_material("Shield_Black_Lacquer")
    tc = nb.new("ShaderNodeTexCoord", (-1200, 0))
    vor = nb.new("ShaderNodeTexVoronoi", (-950, -200), props={"feature": "F1"},
                 inputs={"Vector": tc.outputs["Object"], "Scale": 9.0})
    big = _noise(nb, tc.outputs["Object"], 2.0, 2.0, 0.6, (-950, 200))
    rough = nb.map_range(big.outputs["Fac"], 0.3, 0.7, 0.22, 0.42, (-650, 200))
    bump = nb.new("ShaderNodeBump", (-650, -200), inputs={"Strength": 0.15, "Distance": 0.004,
                                                          "Height": vor.outputs["Distance"]})
    bsdf = principled(nb, (300, 0), base=(0.012, 0.0115, 0.013), metallic=0.25, roughness=rough, spec=0.5,
                      coat=1.0, coat_rough=0.07, normal=bump.outputs[0])
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


def thorn_iron():
    """Blackened iron thorns with faint ember glow in the crevices (nod to the glowing reference)."""
    mat, nb, out = new_material("Thorn_Iron_Ember")
    tc = nb.new("ShaderNodeTexCoord", (-1200, 0))
    n = _noise(nb, tc.outputs["Object"], 30.0, 2.0, 0.65, (-950, -200))
    ember = nb.map_range(n.outputs["Fac"], 0.60, 0.70, 0.0, 1.6, (-650, -200))
    bsdf = principled(nb, (300, 0), base=(0.02, 0.017, 0.016), metallic=0.8, roughness=0.38,
                      emission=(1.0, 0.22, 0.03), emission_strength=ember)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    mat.cycles.emission_sampling = "NONE"
    return mat


# ----------------------------------------------------------------------------- stained glass, beams, dust

def stained_glass_group():
    ng = bpy.data.node_groups.get("StainedGlass")
    if ng:
        return ng
    ng = bpy.data.node_groups.new("StainedGlass", "ShaderNodeTree")
    ng.interface.new_socket("Vector", in_out="INPUT", socket_type="NodeSocketVector")
    s_w = ng.interface.new_socket("Width", in_out="INPUT", socket_type="NodeSocketFloat")
    s_w.default_value = 2.0
    ng.interface.new_socket("Seed", in_out="INPUT", socket_type="NodeSocketFloat")
    ng.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    ng.interface.new_socket("Glass", in_out="OUTPUT", socket_type="NodeSocketColor")
    ng.interface.new_socket("Lead", in_out="OUTPUT", socket_type="NodeSocketFloat")
    nb = NodeBuilder(ng)
    gi = nb.new("NodeGroupInput", (-2400, 0))
    go = nb.new("NodeGroupOutput", (1600, 0))
    sep = nb.new("ShaderNodeSeparateXYZ", (-2200, 0), inputs={"Vector": gi.outputs["Vector"]})
    u, v = sep.outputs["X"], sep.outputs["Z"]
    seed = nb.math("MULTIPLY", gi.outputs["Seed"], 7.31, (-2200, -300))
    p3 = nb.new("ShaderNodeCombineXYZ", (-2000, 0), inputs={"X": u, "Y": v, "Z": seed}).outputs[0]
    # medallions stacked up the light
    vrel = nb.new("ShaderNodeMath", (-2000, -400), props={"operation": "WRAP"},
                  inputs={0: nb.math("SUBTRACT", v, 1.05, (-2200, -500)), 1: 0.68, 2: -0.68}).outputs[0]
    dist = nb.vmath("LENGTH", nb.new("ShaderNodeCombineXYZ", (-1800, -400), inputs={"X": u, "Y": vrel}).outputs[0],
                    None, (-1600, -400))
    rm = nb.math("MINIMUM", nb.math("MULTIPLY", gi.outputs["Width"], 0.36, (-1800, -700)), 0.52, (-1600, -700))
    rin = nb.math("SUBTRACT", rm, 0.06, (-1400, -700))
    in_med = nb.math("LESS_THAN", dist, rin, (-1400, -400))
    in_ring = nb.math("SUBTRACT", nb.math("LESS_THAN", dist, rm, (-1400, -550)), in_med, (-1200, -500))
    au = nb.math("ABSOLUTE", u, None, (-1800, 300))
    bedge = nb.math("SUBTRACT", nb.math("MULTIPLY", gi.outputs["Width"], 0.5, (-1800, 500)), 0.11, (-1600, 500))
    in_border = nb.math("GREATER_THAN", au, bedge, (-1400, 400))

    def cells(scale, loc):
        c = nb.new("ShaderNodeTexVoronoi", loc, props={"voronoi_dimensions": "3D", "feature": "F1"},
                   inputs={"Vector": p3, "Scale": scale, "Randomness": 0.85})
        e = nb.new("ShaderNodeTexVoronoi", (loc[0], loc[1] - 250), props={"voronoi_dimensions": "3D",
                                                                          "feature": "DISTANCE_TO_EDGE"},
                   inputs={"Vector": p3, "Scale": scale, "Randomness": 0.85})
        lead = nb.math("LESS_THAN", e.outputs["Distance"], 0.045, (loc[0] + 200, loc[1] - 250))
        sepc = nb.new("ShaderNodeSeparateColor", (loc[0] + 200, loc[1]), inputs={"Color": c.outputs["Color"]})
        return sepc.outputs[0], sepc.outputs[1], lead

    bg_r, bg_g, bg_lead = cells(4.4, (-1400, 1400))
    md_r, md_g, md_lead = cells(9.5, (-1400, 900))
    bd_r, bd_g, bd_lead = cells(12.0, (-1400, 2000))
    bg = nb.ramp(bg_r, BG_PALETTE, (-1000, 1400), "CONSTANT")
    md = nb.ramp(md_r, [(0.0, (0.62, 0.012, 0.02)), (0.32, (0.92, 0.55, 0.08)), (0.52, (0.80, 0.74, 0.60)),
                        (0.64, (0.03, 0.30, 0.09)), (0.80, (0.04, 0.16, 0.62)), (0.92, (0.45, 0.01, 0.03))],
                 (-1000, 900), "CONSTANT")
    bd = nb.ramp(bd_r, [(0.0, (0.60, 0.012, 0.02)), (0.5, (0.90, 0.52, 0.06)), (0.8, (0.03, 0.10, 0.55))],
                 (-1000, 2000), "CONSTANT")
    ring_col = nb.ramp(bd_g, [(0.0, (0.92, 0.56, 0.07)), (0.55, (0.62, 0.012, 0.02))], (-1000, 600), "CONSTANT")
    col = nb.mix_color("MIX", in_med, bg.outputs["Color"], md.outputs["Color"], (-700, 1000))
    col = nb.mix_color("MIX", in_ring, col, ring_col.outputs["Color"], (-500, 900))
    col = nb.mix_color("MIX", in_border, col, bd.outputs["Color"], (-300, 900))
    # per-piece luminance variation + fine streaks in the glass
    pv = nb.mix_color("MIX", in_med, _gray(nb, bg_g, (-700, 600)), _gray(nb, md_g, (-700, 450)), (-500, 550))
    pvf = nb.map_range(nb.new("ShaderNodeSeparateColor", (-300, 550), inputs={"Color": pv}).outputs[0],
                       0.0, 1.0, 0.65, 1.25, (-100, 550))
    streak = nb.new("ShaderNodeTexNoise", (-700, 200), inputs={"Vector": p3, "Scale": 22.0, "Detail": 2.0})
    sf = nb.map_range(streak.outputs["Fac"], 0.3, 0.7, 0.85, 1.12, (-500, 200))
    g = nb.math("MULTIPLY", pvf, sf, (100, 400))
    glass = nb.mix_color("MULTIPLY", 1.0, col, _gray(nb, g, (300, 500)), (500, 800))
    # lead came: cell edges of the active zone + ring and border outlines
    lead = nb.math("ADD", nb.math("MULTIPLY", bg_lead, nb.math("SUBTRACT", 1.0, in_med, (-700, -150)), (-500, -200)),
                   nb.math("MULTIPLY", md_lead, in_med, (-500, -350)), (-300, -250))
    lead = nb.math("MAXIMUM", lead, nb.math("MULTIPLY", in_ring, bd_lead, (-300, -450)), (-100, -300))
    lead = nb.math("ADD", nb.math("MULTIPLY", lead, nb.math("SUBTRACT", 1.0, in_border, (100, -150)), (300, -200)),
                   nb.math("MULTIPLY", bd_lead, in_border, (300, -400)), (500, -300))
    ring1 = nb.math("LESS_THAN", nb.math("ABSOLUTE", nb.math("SUBTRACT", dist, rm, (-1200, -900)), None,
                                         (-1000, -900)), 0.012, (-800, -900))
    ring2 = nb.math("LESS_THAN", nb.math("ABSOLUTE", nb.math("SUBTRACT", dist, rin, (-1200, -1100)), None,
                                         (-1000, -1100)), 0.012, (-800, -1100))
    bline = nb.math("LESS_THAN", nb.math("ABSOLUTE", nb.math("SUBTRACT", au, bedge, (-1200, -1300)), None,
                                         (-1000, -1300)), 0.012, (-800, -1300))
    lead = nb.math("MAXIMUM", lead, nb.math("MAXIMUM", ring1, nb.math("MAXIMUM", ring2, bline, (-600, -1200)),
                                            (-400, -1100)), (700, -400), clamp=True)
    final = nb.mix_color("MIX", lead, glass, (0.0, 0.0, 0.0, 1), (1000, 300))
    nb.link(final, go.inputs["Color"])
    nb.link(glass, go.inputs["Glass"])
    nb.link(lead, go.inputs["Lead"])
    return ng


BG_PALETTE = [(0.0, (0.010, 0.030, 0.33)), (0.30, (0.030, 0.11, 0.58)), (0.52, (0.012, 0.022, 0.24)),
              (0.66, (0.50, 0.012, 0.025)), (0.78, (0.12, 0.02, 0.34)), (0.90, (0.85, 0.48, 0.05)),
              (0.96, (0.03, 0.30, 0.10))]


def stained_glass():
    """Window pane: the full leaded pattern for camera/glossy rays; shadow rays (the exterior sun spots
    projecting colour onto the floor) see a one-Voronoi version, so the expensive branch is skipped."""
    mat, nb, out = new_material("Stained_Glass")
    tc = nb.new("ShaderNodeTexCoord", (-1200, 0))
    info = nb.new("ShaderNodeObjectInfo", (-1200, -300))
    width = nb.new("ShaderNodeAttribute", (-1200, 300), props={"attribute_type": "OBJECT",
                                                              "attribute_name": "glass_width"})
    bright = nb.new("ShaderNodeAttribute", (-1200, 500), props={"attribute_type": "OBJECT",
                                                               "attribute_name": "glass_brightness"})
    pale = nb.new("ShaderNodeAttribute", (-1200, 700), props={"attribute_type": "OBJECT",
                                                             "attribute_name": "glass_tint_mix"})
    grp = nb.new("ShaderNodeGroup", (-900, 200))
    grp.node_tree = stained_glass_group()
    nb.set(grp, "Vector", tc.outputs["Object"])
    nb.set(grp, "Width", width.outputs["Fac"])
    nb.set(grp, "Seed", info.outputs["Random"])
    em = nb.new("ShaderNodeEmission", (-400, 200), inputs={"Color": grp.outputs["Color"],
                                                           "Strength": bright.outputs["Fac"]})
    # cheap shadow pattern
    sv = nb.new("ShaderNodeTexVoronoi", (-900, -300), props={"voronoi_dimensions": "3D", "feature": "F1"},
                inputs={"Vector": tc.outputs["Object"], "Scale": 4.4, "Randomness": 0.85})
    sc = nb.new("ShaderNodeSeparateColor", (-700, -300), inputs={"Color": sv.outputs["Color"]})
    sramp = nb.ramp(sc.outputs[0], BG_PALETTE, (-550, -300), "CONSTANT")
    trans_col = nb.mix_color("MULTIPLY", 1.0, sramp.outputs["Color"], (1.6, 1.6, 1.6, 1), (-350, -300), clamp=True)
    trans_col = nb.mix_color("MIX", pale.outputs["Fac"], trans_col, (0.95, 0.88, 0.76, 1), (-200, -300))
    tr = nb.new("ShaderNodeBsdfTransparent", (-50, -200), inputs={"Color": trans_col})
    lp = nb.new("ShaderNodeLightPath", (-400, 500))
    mix = nb.new("ShaderNodeMixShader", (200, 0), inputs={"Fac": lp.outputs["Is Shadow Ray"]})
    nb.link(em.outputs[0], mix.inputs[1])
    nb.link(tr.outputs[0], mix.inputs[2])
    nb.link(mix.outputs[0], out.inputs["Surface"])
    mat.cycles.emission_sampling = "NONE"
    return mat


def light_beam(name, axis, plane, direction, strength, color=(1.0, 0.86, 0.66), length=16.0):
    """Fake volumetric shaft: additive emission inside a prism extruded from a window along `direction`.

    Distance s from the window plane drives the fade; streaks come from noise in window space;
    facing ratio softens the silhouette, a phase term brightens it when looking toward the window, and a
    camera-distance fade avoids near-lens pops."""
    mat, nb, out = new_material(name)
    tc = nb.new("ShaderNodeTexCoord", (-2200, 0))
    sep = nb.new("ShaderNodeSeparateXYZ", (-2000, 0), inputs={"Vector": tc.outputs["Object"]})
    comp = {"X": 0, "Y": 1, "Z": 2}[axis]
    coord = sep.outputs[comp]
    s = nb.math("DIVIDE", nb.math("SUBTRACT", coord, plane, (-1800, 0)), direction[comp], (-1600, 0))
    s = nb.math("ABSOLUTE", s, None, (-1450, 0))
    d = nb.new("ShaderNodeCombineXYZ", (-1600, -300), inputs={"X": direction[0], "Y": direction[1], "Z": direction[2]})
    back = nb.vmath("SCALE", d.outputs[0], None, (-1400, -300))
    nb.link(s, back.node.inputs["Scale"])
    q = nb.vmath("SUBTRACT", tc.outputs["Object"], back, (-1200, -300))
    fade_in = nb.map_range(s, 0.0, 1.8, 0.0, 1.0, (-1200, 200), interp="SMOOTHSTEP")
    fade_out = nb.map_range(s, length * 0.35, length, 1.0, 0.0, (-1200, 400), interp="SMOOTHSTEP")
    streak_vec = nb.vmath("MULTIPLY", q, (2.2, 2.2, 2.2), (-1000, -300))
    sv = nb.vmath("ADD", streak_vec, nb.new("ShaderNodeCombineXYZ", (-1200, -600), inputs={
        "Z": nb.math("MULTIPLY", s, 0.06, (-1400, -600))}).outputs[0], (-850, -400))
    streak = nb.new("ShaderNodeTexNoise", (-700, -300), inputs={"Vector": sv, "Scale": 1.6, "Detail": 2.0,
                                                                 "Roughness": 0.6})
    streak_f = nb.map_range(streak.outputs["Fac"], 0.35, 0.68, 0.25, 1.15, (-500, -300))
    lw = nb.new("ShaderNodeLayerWeight", (-700, 200), inputs={"Blend": 0.5})
    face = nb.math("POWER", nb.math("SUBTRACT", 1.0, lw.outputs["Facing"], (-500, 200)), 1.8, (-300, 200))
    # Incoming points at the viewer, so looking into the light gives dot(Incoming, d) > 0
    geo = nb.new("ShaderNodeNewGeometry", (-900, 750))
    cosv = nb.vmath("DOT_PRODUCT", geo.outputs["Incoming"], d.outputs[0], (-700, 750))
    phase = nb.math("ADD", 0.55, nb.math("MULTIPLY", nb.math("MAXIMUM", cosv, 0.0, (-350, 800)), 1.6, (-200, 800)),
                    (0, 800))
    cam = nb.new("ShaderNodeCameraData", (-700, 500))
    camfade = nb.map_range(cam.outputs["View Distance"], 0.8, 3.5, 0.0, 1.0, (-500, 500), interp="SMOOTHSTEP")
    k = nb.math("MULTIPLY", fade_in, fade_out, (-300, 350))
    k = nb.math("MULTIPLY", k, streak_f, (-100, 300))
    k = nb.math("MULTIPLY", k, face, (100, 300))
    k = nb.math("MULTIPLY", k, camfade, (300, 300))
    k = nb.math("MULTIPLY", k, phase, (400, 450))
    k = nb.math("MULTIPLY", k, strength, (500, 300))
    em = nb.new("ShaderNodeEmission", (700, 100), inputs={"Color": tuple(color) + (1,), "Strength": k})
    tr = nb.new("ShaderNodeBsdfTransparent", (700, -100))
    add = nb.new("ShaderNodeAddShader", (900, 0))
    nb.link(em.outputs[0], add.inputs[0])
    nb.link(tr.outputs[0], add.inputs[1])
    nb.link(add.outputs[0], out.inputs["Surface"])
    out.location = (1100, 0)
    mat.cycles.emission_sampling = "NONE"
    return mat


def dust():
    mat, nb, out = new_material("Dust_Mote")
    bsdf = principled(nb, (100, 0), base=(0.85, 0.80, 0.72), roughness=0.9, spec=0.2,
                      emission=(1.0, 0.75, 0.5), emission_strength=0.04)
    nb.link(bsdf.outputs[0], out.inputs["Surface"])
    mat.cycles.emission_sampling = "NONE"
    return mat


BUILDERS = {
    "silver": silver, "black_enamel": black_enamel, "gold": gold, "gold_emblem": gold_emblem, "iron": iron,
    "ruby": ruby, "gem_core": gem_core, "flame": flame, "wick": wick, "stone_floor": stone_floor,
    "stone_wall": stone_wall, "stone_carved": stone_carved, "stone_slate": stone_slate, "marble": black_marble,
    "velvet": velvet_crimson, "rose_red": rose_red, "rose_black": rose_black, "leaf": leaf, "carpet": carpet,
    "wax_ivory": wax_ivory, "wax_red": wax_red, "wax_black": wax_black, "shield_lacquer": shield_lacquer,
    "thorn": thorn_iron, "stained_glass": stained_glass, "dust": dust,
}
