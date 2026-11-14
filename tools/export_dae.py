"""Derive the wheel .dae files from the exported .usdc files.

Collada export was removed in Blender 5.0, so this runs in Blender 4.2 LTS (tools/blender42/Dockerfile).
The .usdc files are themselves exported from the .blend by tools/export_usd.py, so the .blend
stays the single source of truth. Run from the repo folder:
    blender -b --factory-startup --python tools/export_dae.py
"""
import os

import bpy

assert bpy.app.version[:2] == (4, 2), f"needs Blender 4.2 LTS, got {bpy.app.version_string}"

for side in ("L", "R"):
    src = f"traxxas_6873T_wheel_{side}.usdc"
    out = f"traxxas_6873T_wheel_{side}.dae"
    assert os.path.exists(src), f"missing {src}; run tools/export_usd.py first"

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    bpy.ops.wm.usd_import(filepath=src, import_materials=True, scale=1.0)

    bpy.ops.wm.collada_export(
        filepath=out,
        apply_modifiers=True,
        export_global_up_selection='Z',
        export_global_forward_selection='Y',
        apply_global_orientation=False,
        triangulate=True,
        use_texture_copies=False,
    )
    print(f"[export] {src} -> {out}")
