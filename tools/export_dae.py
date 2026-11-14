"""Derive the wheel .dae files in dae/ from the exported .usdc files in usd/.

Collada export was removed in Blender 5.0, so this runs in Blender 4.2 LTS (tools/docker/blender42/Dockerfile).
The .usdc files are themselves exported from the .blend by tools/export_usd.py, so the .blend
stays the single source of truth. Normally run through tools/export_all.sh.
"""
import os

import bpy

assert bpy.app.version[:2] == (4, 2), f"needs Blender 4.2 LTS, got {bpy.app.version_string}"

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(REPO_DIR, "dae"), exist_ok=True)

for side in ("L", "R"):
    src = os.path.join(REPO_DIR, "usd", f"traxxas_6873T_wheel_{side}.usdc")
    out = os.path.join(REPO_DIR, "dae", f"traxxas_6873T_wheel_{side}.dae")
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
