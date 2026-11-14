"""Export the collections of one source .blend to usd/.

Run with Blender 5.3.x from the repo root, once per source file (tools/export_all.sh does this):
    blender -b blender/roboracer_frame.blend --python tools/export_usd.py
"""
import os
from contextlib import contextmanager

import bpy

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_DIR, "usd")

# Source file -> [(collection, output name)]. The assembly (roboracer_car.blend) is never exported.
EXPORTS = {
    "traxxas_6873T_wheel.blend": [("Traxxas_6873T_L", "traxxas_6873T_wheel_L"),
                                  ("Traxxas_6873T_R", "traxxas_6873T_wheel_R")],
    "roboracer_frame.blend": [("Roboracer_Frame", "roboracer_frame")],
    "roboracer_front_axle.blend": [("Roboracer_Front_Axle", "roboracer_front_axle")],
    "roboracer_center_of_mass.blend": [("Roboracer_Center_Of_Mass", "roboracer_center_of_mass")],
}


@contextmanager
def preserve_constant_alpha():
    changed = []
    try:
        for material in bpy.data.materials:
            if not material.use_nodes:
                continue
            for node in material.node_tree.nodes:
                if node.type != 'BSDF_PRINCIPLED':
                    continue
                alpha = node.inputs['Alpha']
                transmission = node.inputs['Transmission Weight']
                if (not alpha.is_linked and alpha.default_value < 1.0
                        and not transmission.is_linked and transmission.default_value == 0.0):
                    # Blender 5.3 overwrites USD opacity with 1 - Transmission Weight.
                    # Compensate only during export; leave the source shader unchanged.
                    changed.append((transmission, transmission.default_value))
                    transmission.default_value = 1.0 - alpha.default_value
        yield
    finally:
        for socket, value in changed:
            socket.default_value = value


def find_layer_collection(layer_coll, name):
    if layer_coll.collection.name == name:
        return layer_coll
    for child in layer_coll.children:
        found = find_layer_collection(child, name)
        if found:
            return found
    return None


source = os.path.basename(bpy.data.filepath)
assert source in EXPORTS, f"{source} is not an export source; known: {sorted(EXPORTS)}"
os.makedirs(OUT_DIR, exist_ok=True)

for coll_name, out_name in EXPORTS[source]:
    # Use the first scene that contains the collection.
    scene = next(s for s in bpy.data.scenes
                 if find_layer_collection(s.view_layers[0].layer_collection, coll_name))
    assert scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1.0, \
        "the .blend must be in metres (unit scale 1.0)"
    view_layer = scene.view_layers[0]
    # Render setups may exclude a collection from the view layer, and the exporter skips excluded
    # objects. This change is never saved.
    find_layer_collection(view_layer.layer_collection, coll_name).exclude = False
    out = os.path.join(OUT_DIR, f"{out_name}.usdc")
    with bpy.context.temp_override(scene=scene, view_layer=view_layer), preserve_constant_alpha():
        bpy.ops.wm.usd_export(
            filepath=out,
            collection=coll_name,
            root_prim_path=f"/{coll_name}",
            evaluation_mode='RENDER',
            export_meshes=True,
            export_materials=True,
            generate_preview_surface=True,
            export_normals=True,
            export_uvmaps=True,
            export_cameras=False,
            export_lights=False,
            export_animation=False,
            convert_world_material=False,
            convert_scene_units='METERS',
            export_global_up_selection='Z',
            export_global_forward_selection='NEGATIVE_Y',
            convert_orientation=False,
        )
    print(f"[export] {coll_name} -> {out}")
