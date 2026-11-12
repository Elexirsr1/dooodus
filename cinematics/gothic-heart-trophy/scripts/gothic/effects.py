"""Atmosphere: drifting dust motes (geometry nodes) and the compositing stack (layered fog, bloom,
subtle chromatic aberration, vignette, grade)."""
import bpy

from . import materials as M
from .util import NodeBuilder, collection


def dust(root, camera_ob, count=14000, bounds=((-8.4, 6.5), (-20.0, 5.0), (0.15, 9.0)), seed=3):
    coll = collection("Atmosphere", root)
    me = bpy.data.meshes.new("Dust_Host")
    ob = bpy.data.objects.new("Dust_Motes", me)
    coll.objects.link(ob)
    ob.visible_shadow = False
    ng = bpy.data.node_groups.new("DustMotes", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    nb = NodeBuilder(ng)
    gi = nb.new("NodeGroupInput", (-1400, 0))
    go = nb.new("NodeGroupOutput", (1200, 0))
    rpos = nb.new("FunctionNodeRandomValue", (-1200, 200), props={"data_type": "FLOAT_VECTOR"})
    rpos.inputs[0].default_value = (bounds[0][0], bounds[1][0], bounds[2][0])
    rpos.inputs[1].default_value = (bounds[0][1], bounds[1][1], bounds[2][1])
    rpos.inputs[8].default_value = seed
    rrad = nb.new("FunctionNodeRandomValue", (-1200, -100), props={"data_type": "FLOAT"})
    rrad.inputs[2].default_value = 0.0011
    rrad.inputs[3].default_value = 0.0032
    rrad.inputs[8].default_value = seed + 1
    pts = nb.new("GeometryNodePoints", (-950, 0), inputs={"Count": count})
    nb.link(rpos.outputs[0], pts.inputs["Position"])
    nb.link(rrad.outputs[1], pts.inputs["Radius"])
    # slow turbulent drift + a faint updraft from the candles
    t = nb.new("GeometryNodeInputSceneTime", (-1200, -400))
    pos = nb.new("GeometryNodeInputPosition", (-1200, -600))
    sp = nb.vmath("SCALE", pos.outputs[0], None, (-1000, -600))
    sp.node.inputs["Scale"].default_value = 0.35
    w = nb.math("MULTIPLY", t.outputs["Seconds"], 0.12, (-1000, -400))
    noise = nb.new("ShaderNodeTexNoise", (-800, -500), props={"noise_dimensions": "4D"},
                   inputs={"Vector": sp, "W": w, "Scale": 1.0, "Detail": 1.0})
    centered = nb.vmath("SUBTRACT", noise.outputs["Color"], (0.5, 0.5, 0.5), (-600, -500))
    drift = nb.vmath("SCALE", centered, None, (-450, -500))
    drift.node.inputs["Scale"].default_value = 1.3
    rise = nb.new("ShaderNodeCombineXYZ", (-600, -750), inputs={"Z": nb.math("MULTIPLY", t.outputs["Seconds"], 0.012,
                                                                            (-800, -750))})
    offset = nb.vmath("ADD", drift, rise.outputs[0], (-300, -550))
    setp = nb.new("GeometryNodeSetPosition", (-650, 0))
    nb.link(pts.outputs[0], setp.inputs["Geometry"])
    nb.link(offset, setp.inputs["Offset"])
    # never let a mote drift into the lens
    info = nb.new("GeometryNodeObjectInfo", (-650, -300), props={"transform_space": "ORIGINAL"})
    info.inputs["Object"].default_value = camera_ob
    pos2 = nb.new("GeometryNodeInputPosition", (-650, -500))
    dist = nb.vmath("DISTANCE", pos2.outputs[0], info.outputs["Location"], (-450, -350))
    near = nb.math("LESS_THAN", dist, 0.9, (-250, -350))
    delete = nb.new("GeometryNodeDeleteGeometry", (-100, 0), props={"domain": "POINT"})
    nb.link(setp.outputs[0], delete.inputs["Geometry"])
    nb.link(near, delete.inputs["Selection"])
    setm = nb.new("GeometryNodeSetMaterial", (300, 0))
    setm.inputs["Material"].default_value = M.get("dust")
    nb.link(delete.outputs[0], setm.inputs["Geometry"])
    nb.link(setm.outputs[0], go.inputs[0])
    mod = ob.modifiers.new("DustMotes", "NODES")
    mod.node_group = ng
    return ob


def compositor(scene):
    scene.use_nodes = True
    vl = scene.view_layers[0]
    vl.use_pass_mist = True
    vl.use_pass_position = True
    nb = NodeBuilder(scene.node_tree)
    rl = nb.new("CompositorNodeRLayers", (-1600, 0))

    # layered fog: mist depth x height falloff; the fog colour is a heavily blurred copy of the frame,
    # so it glows near windows and flames (cheap, temporally stable single-scatter look)
    sep = nb.new("CompositorNodeSeparateXYZ", (-1400, -500), inputs={"Vector": rl.outputs["Position"]})

    def cmath(op, a, b=None, loc=(0, 0), clamp=False):
        n = nb.new("CompositorNodeMath", loc, props={"operation": op, "use_clamp": clamp})
        nb.set(n, 0, a)
        if b is not None:
            nb.set(n, 1, b)
        return n.outputs[0]

    zpos = cmath("MAXIMUM", sep.outputs["Z"], 0.0, (-1200, -500))
    hf = cmath("EXPONENT", cmath("MULTIPLY", zpos, -1.0 / 3.5, (-1050, -500)), None, (-900, -500))
    height_term = cmath("ADD", cmath("MULTIPLY", hf, 0.75, (-750, -500)), 0.35, (-600, -500))
    fog = cmath("MULTIPLY", rl.outputs["Mist"], height_term, (-450, -400))
    fog = cmath("MULTIPLY", fog, 0.45, (-300, -400), clamp=True)

    small = nb.new("CompositorNodeScale", (-1300, 300), props={"space": "RELATIVE"},
                   inputs={"Image": rl.outputs["Image"], "X": 0.125, "Y": 0.125})
    blur = nb.new("CompositorNodeBlur", (-1100, 300), props={"filter_type": "FAST_GAUSS"},
                  inputs={"Image": small.outputs[0]})
    blur.inputs["Size"].default_value = (22.0, 22.0)
    big = nb.new("CompositorNodeScale", (-900, 300), props={"space": "RELATIVE"},
                 inputs={"Image": blur.outputs[0], "X": 8.0, "Y": 8.0})
    scatter = nb.new("CompositorNodeMixRGB", (-700, 300), props={"blend_type": "MULTIPLY"},
                     inputs={"Fac": 1.0, 1: big.outputs[0], 2: (0.5, 0.48, 0.5, 1.0)})
    fogcol = nb.new("CompositorNodeMixRGB", (-500, 300), props={"blend_type": "ADD"},
                    inputs={"Fac": 1.0, 1: scatter.outputs[0], 2: (0.0045, 0.0050, 0.0068, 1.0)})
    fogged = nb.new("CompositorNodeMixRGB", (-300, 100), props={"blend_type": "MIX"},
                    inputs={"Fac": fog, 1: rl.outputs["Image"], 2: fogcol.outputs[0]})

    glare = nb.new("CompositorNodeGlare", (-50, 100), props={"glare_type": "BLOOM", "quality": "HIGH"},
                   inputs={"Image": fogged.outputs[0], "Threshold": 1.4, "Smoothness": 0.35, "Strength": 0.32,
                           "Size": 0.62, "Saturation": 1.0})
    streak = nb.new("CompositorNodeGlare", (200, 100), props={"glare_type": "STREAKS", "quality": "MEDIUM"},
                    inputs={"Image": glare.outputs["Image"], "Threshold": 9.0, "Smoothness": 0.3, "Strength": 0.07,
                            "Streaks": 2, "Streaks Angle": 0.0, "Fade": 0.88, "Iterations": 3})
    lens = nb.new("CompositorNodeLensdist", (450, 100), inputs={"Image": streak.outputs["Image"],
                                                                "Dispersion": 0.006})
    # vignette
    ell = nb.new("CompositorNodeEllipseMask", (200, -300))
    ell.inputs["Position"].default_value = (0.5, 0.5)
    ell.inputs["Size"].default_value = (0.98, 0.88)
    vblur = nb.new("CompositorNodeBlur", (400, -300), props={"filter_type": "FAST_GAUSS"},
                   inputs={"Image": ell.outputs[0]})
    vblur.inputs["Size"].default_value = (360.0, 360.0)
    vmap = nb.new("CompositorNodeMapRange", (600, -300), props={"use_clamp": True},
                  inputs={"Value": vblur.outputs[0], "From Min": 0.0, "From Max": 1.0, "To Min": 0.58, "To Max": 1.0})
    vig = nb.new("CompositorNodeMixRGB", (700, 100), props={"blend_type": "MULTIPLY"},
                 inputs={"Fac": 1.0, 1: lens.outputs[0], 2: vmap.outputs[0]})
    grade = nb.new("CompositorNodeColorBalance", (950, 100), props={"correction_method": "LIFT_GAMMA_GAIN"})
    nb.link(vig.outputs[0], grade.inputs[1])
    grade.inputs[3].default_value = (0.985, 0.995, 1.02, 1.0)   # lift: cool the shadows a touch
    grade.inputs[5].default_value = (1.0, 0.995, 0.99, 1.0)     # gamma
    grade.inputs[7].default_value = (1.03, 1.0, 0.965, 1.0)     # gain: warm highlights
    comp = nb.new("CompositorNodeComposite", (1250, 100))
    nb.link(grade.outputs[0], comp.inputs["Image"])
    view = nb.new("CompositorNodeViewer", (1250, -100))
    nb.link(grade.outputs[0], view.inputs["Image"])
    return scene.node_tree


def build(root, scene, camera_ob):
    motes = dust(root, camera_ob)
    compositor(scene)
    return dict(dust=motes)
