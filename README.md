# Traxxas 6873T wheel

Model of the Traxxas 6873T wheel: a 109.5 mm tyre, the stock size for the Traxxas Slash. There are left (`_L`) and right (`_R`) versions.

All files use metres, Z up, and the wheel axis is X. The tyre is 0.1095 m in diameter and about 0.039 m wide.

## Files

| File | Role |
|---|---|
| `traxxas_6873T_wheel.blend` | **Source of truth.** All modelling changes go here. |
| `traxxas_6873T_wheel_L.usdc`, `_R.usdc` | Exported from the `.blend`. |
| `traxxas_6873T_wheel_L.dae`, `_R.dae` | Exported from the `.usdc` files (Collada, e.g. for ROS 2 / RViz / Gazebo). |
| `tools/` | Export scripts and the Blender 4.2 Docker image used for the `.dae` export. |
| `render.py`, `RENDER_INSTRUCTIONS.md` | Render the reference images. |

## Rules for editing

- **Edit only the `.blend` file, and only with Blender 5.2.x.** The `.blend` is the source of truth.
- **Never edit the `.usdc` or `.dae` files directly.** Don't edit them by hand, with scripts, or by importing and re-exporting them in another tool. Any direct edit is lost the next time the files are exported.
- **After changing the `.blend`, regenerate both export formats and commit them together** with the `.blend` in the same commit.
- **Keep the `.blend` in metres** (scene unit scale 1.0). `tools/export_usd.py` refuses to export otherwise.

## Regenerating the exports

You need Blender 5.2.x and Docker. Run:

```bash
BLENDER=/path/to/blender-5.2.x/blender tools/export_all.sh
```

This runs two steps:

1. **USD.** Blender 5.2 runs `tools/export_usd.py`, which exports the collections `Traxxas_6873T_L` and `Traxxas_6873T_R` to `traxxas_6873T_wheel_L.usdc` and `traxxas_6873T_wheel_R.usdc`. The root prim is `/Traxxas_6873T_L` or `/Traxxas_6873T_R`, and `metersPerUnit` is 1.
2. **Collada.** Blender 5.0 removed the Collada exporter, so this step uses Blender 4.2.23 LTS in Docker:
   - The image `traxxas-blender42:4.2.23` is built from `tools/blender42/Dockerfile` on first use. The Blender download is checked against its SHA-256.
   - In the container, `tools/export_dae.py` imports each `.usdc` and exports the matching `.dae`, with units in metres (`<unit meter="1"/>`).

Then check the result with `git status`. Only the `.usdc` and `.dae` files should have changed.

Exports are not byte-identical between runs, even when the `.blend` hasn't changed. Blender writes USD prims in a varying order, and the `.dae` records the export time. Only regenerate and commit exports when the `.blend` has actually changed.
