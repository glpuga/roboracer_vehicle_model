# AGENTS.md: procedures for this repo

These procedures apply to anyone changing this repo, whether a person or an AI agent. See [README.md](README.md) for what the repo contains.

## Ground rules

1. **The `.blend` is the source of truth.**
   - All modelling changes go into `blender/traxxas_6873T_wheel.blend`.
   - Open and save it only with **Blender 5.2.x**. Saving with another version may change how it opens or renders.
2. **Never edit `usd/*.usdc` or `dae/*.dae` directly.**
   - Don't edit them by hand, with scripts, or by importing them into another tool and exporting again.
   - They are always regenerated from the `.blend` with `tools/export_all.sh` (see [Exporting](#exporting-usd-and-dae)).
3. **Keep the model in metres.**
   - The scene unit scale must be 1.0, with Z up and the wheel axis along X.
   - `tools/export_usd.py` refuses to export otherwise.
4. **A change to the `.blend` and its regenerated exports go in the same commit.**
   - Don't commit re-exports without a `.blend` change. Exports are not byte-identical between runs, because Blender writes USD prims in a varying order and the `.dae` records the export time.
5. **Don't change the render scenes** (cameras, lights, world, render settings) unless that is the task.
6. **Never overwrite files without a backup.**
   - Blender keeps the previous save as `*.blend1`, which git ignores.
   - Scratch output goes to `build/`, which git also ignores.

## Tools you need

| Tool | Used for | Notes |
|---|---|---|
| Blender 5.2.x | Editing, USD export, rendering | Official builds: <https://download.blender.org/release/Blender5.2/>. On Linux you can unpack the tarball and run `./blender`; no install needed. |
| Docker | `.dae` export | `tools/export_all.sh` builds the image `traxxas-blender42:4.2.23` from `tools/docker/blender42/Dockerfile` on first use. |
| Git | Version control | Commit identity: `glpuga`. |

Blender 4.2 is only needed for the Collada export, and the Docker image provides it. Don't install it or use it for anything else.

## Editing the model

1. **Open the file** `blender/traxxas_6873T_wheel.blend` in Blender 5.2.x.
2. **Edit the wheel parts.** They are in the collections `Traxxas_6873T_L` and `Traxxas_6873T_R`, each under an empty named `Traxxas_6873T_WheelTire_L` or `_R`.
   - Apply every change to both sides.
   - The render scenes show these collections through the `Stack_*_Inst` / `Standing_Inst` instance empties, so the renders update automatically.
3. **Keep real-world sizes in metres.** If you rescale something, also scale whatever depends on size:
   - bevel modifier widths;
   - light sizes, and their power by the square of the scale factor;
   - camera clipping and depth-of-field distances;
   - noise texture `Scale` for textures using Object coordinates, and bump `Distance`.

   Afterwards, compare a test render with the references (see [Rendering](#rendering)).
4. **Save in Blender 5.2.x.**
5. **Regenerate the exports** (see [Exporting](#exporting-usd-and-dae)).
6. **Re-render the references** if the wheel's appearance changed, and copy the images into `renders/`.
7. **Commit** the `.blend`, `usd/`, `dae/` and, if they changed, `renders/`, all together.

## Exporting USD and DAE

```bash
BLENDER=/path/to/blender-5.2.x/blender tools/export_all.sh
```

The script runs two steps:

1. **USD.** Blender 5.2 runs `tools/export_usd.py`:
   - It exports the collections `Traxxas_6873T_L` and `Traxxas_6873T_R` to `usd/traxxas_6873T_wheel_L.usdc` and `_R.usdc`.
   - The root prim is `/Traxxas_6873T_L` or `/Traxxas_6873T_R`, and `metersPerUnit` is 1.
   - Modifiers are applied, and materials are written as UsdPreviewSurface.
   - The `Scene` view layer excludes the L collection. The script includes it only for the export and never saves the `.blend`.
2. **Collada.** Blender 5.0 removed the Collada exporter, so this step uses Blender 4.2.23 LTS in Docker:
   - `tools/export_dae.py` imports each `.usdc` and exports `dae/*.dae`, with `<unit meter="1"/>` and triangulated meshes.
   - The Blender download in the image is checked against its SHA-256.

**Check the result:**
- `git status` should show changes only in `usd/` and `dae/`.
- Both formats should have 33 meshes and measure about 0.039 × 0.1095 × 0.1095 m (X × Y × Z).

## Rendering

The `.blend` has two scenes. Their lighting, materials, depth of field and denoising are already set up.

| Scene | Content | Camera | Resolution | Samples | Output file |
|---|---|---|---|---|---|
| `Scene` | Single wheel in a studio set | `Camera` | 1920×1280 | 160 | `traxxas_6873T_render.png` |
| `Stack` | 3 wheels stacked plus 1 standing | `StackCam` | 2400×1600 | 256 | `traxxas_6873T_stack_render.png` |

1. **Do a quick test render** (a few seconds on a GPU). It confirms the GPU works:

   ```bash
   /path/to/blender -b blender/traxxas_6873T_wheel.blend --python tools/render.py -- \
       --percent 25 --samples 16 --no-cpu-fallback --out build/renders_test
   ```

   Look for `OK on OPTIX` (or `CUDA`, `HIP`, …) in the `[render]` lines.
2. **Do the full render.** Output goes to `build/renders/` by default:

   ```bash
   /path/to/blender -b blender/traxxas_6873T_wheel.blend --python tools/render.py
   ```

3. **Check the results.**
   - Compare them with `renders/`: they should have the same framing and colours, with only slightly different noise.
   - The images should not be black or cropped, and no wheel should be missing.
4. **Update the references** only if the wheel's appearance changed on purpose: copy the new images from `build/renders/` into `renders/`. Otherwise, don't overwrite `renders/`.

**`tools/render.py` options.** Everything after the `--` goes to the script:

| Option | Default | Notes |
|---|---|---|
| `--scenes NAME …` | `Scene Stack` | Render only some of the scenes |
| `--out DIR` | `build/renders` | Created if missing |
| `--device DEV` | `auto` | `auto` tries OPTIX → CUDA → HIP → ONEAPI → METAL, then CPU. Or force one, e.g. `--device OPTIX` |
| `--samples N` | the scene's own value | |
| `--percent P` | `100` | Resolution percentage |
| `--no-cpu-fallback` | off | Fail instead of falling back to the CPU |

The script never saves the `.blend`.

**Expected timings:**

| Scene | CPU only (16 threads) | OptiX, RTX 2060 |
|---|---|---|
| `Scene` | about 80–90 s | about 20 s |
| `Stack` | about 10 min | about 46 s |

### Render troubleshooting

- **Blender crashes about 1 s after loading, and the crash log shows `libze_loader` / `zeInitDrivers`:**
  - The Intel oneAPI device probe crashed. Cycles runs it even with `--device OPTIX`.
  - Fix: run Blender with `ONEAPI_DEVICE_SELECTOR='opencl:*'` set in the environment.
- **`Failed to load CUDA kernel … (Invalid kernel image)`:** the NVIDIA driver is too old for this Blender build. Update the driver.
- **`OPTIX: no devices`, but CUDA works:** OptiX needs an RTX card or a newer driver. CUDA gives the same image, just more slowly.
- **Only `CPU` in the summary:** no GPU backend worked. Rerun with `--no-cpu-fallback` to see each failure.
- **The image looks different from the reference:** check the Blender version (`blender --version`). It must be 5.2.x.

## Commits

- **Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):** `<type>[optional scope][!]: <description>`.
  - The description is lowercase and in the imperative mood, without a trailing full stop.
  - Add a body with bullets explaining what changed and why.
- **Types:**

  | Type | Use for |
  |---|---|
  | `feat` | Changes to the model (a new part, or new geometry or material in the `.blend`) |
  | `fix` | Model or tooling bugs |
  | `refactor` | Restructuring with no visible change to the model |
  | `docs` | Documentation only |
  | `build` | Docker images and export tooling environments |
  | `chore` | Housekeeping, e.g. `.gitignore` |

- **Breaking changes:** mark them with `!` (e.g. `feat!:`) and add a `BREAKING CHANGE:` footer. A change is breaking if it affects people who use the exports, e.g. new units, a different axis convention, renamed prims or nodes, or moved file paths.
- **Scope:** one logical change per commit, with the `.blend` and its exports committed together.
- **AI-assisted commits:** add the trailer `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
