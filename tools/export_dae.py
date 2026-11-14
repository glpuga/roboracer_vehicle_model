"""Derive dae/<part>.dae from every usd/<part>.usdc.

Collada export was removed in Blender 5.0, so this runs in Blender 4.2 LTS (tools/docker/blender42/Dockerfile).
The .usdc files are themselves exported from the source .blend files by tools/export_usd.py, so the
.blend files stay the single source of truth. Normally run through tools/export_all.sh.
"""
import glob
import os

import bpy

assert bpy.app.version[:2] == (4, 2), f"needs Blender 4.2 LTS, got {bpy.app.version_string}"

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(REPO_DIR, "dae"), exist_ok=True)
sources = sorted(glob.glob(os.path.join(REPO_DIR, "usd", "*.usdc")))
assert sources, "no usd/*.usdc; run tools/export_usd.py first"

for src in sources:
    out = os.path.join(REPO_DIR, "dae", os.path.basename(src)[:-len(".usdc")] + ".dae")
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
