"""Export the wheel USDC files from traxxas_6873T_wheel.blend (the source of truth).

Run with Blender 5.2.x from the repo folder:
    blender -b traxxas_6873T_wheel.blend --python tools/export_usd.py
"""
import os

import bpy

OUT_DIR = os.path.dirname(bpy.data.filepath)

scene = bpy.data.scenes["Scene"]
assert scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1.0, \
    "the .blend must be in metres (unit scale 1.0)"

for side in ("L", "R"):
    coll = bpy.data.collections[f"Traxxas_6873T_{side}"]
    out = os.path.join(OUT_DIR, f"traxxas_6873T_wheel_{side}.usdc")
    # The render setup excludes one side from the view layer; the exporter skips excluded objects.
    # This change is never saved.
    layer_coll = scene.view_layers[0].layer_collection.children[coll.name]
    layer_coll.exclude = False
    with bpy.context.temp_override(scene=scene, view_layer=scene.view_layers[0]):
        bpy.ops.wm.usd_export(
            filepath=out,
            collection=coll.name,
            root_prim_path=f"/{coll.name}",
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
    print(f"[export] {coll.name} -> {out}")
