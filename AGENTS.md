# AGENTS.md: procedures for this repo

These procedures apply to anyone changing this repo, whether a person or an AI agent. See [README.md](README.md) for what the repo contains.

## Ground rules

1. **The source `.blend` files are the source of truth.**
   - `blender/traxxas_6873T_wheel.blend` (wheel), `blender/roboracer_frame.blend` (frame), `blender/roboracer_front_axle.blend` (front axle module) and `blender/roboracer_center_of_mass.blend` (center-of-mass marker).
   - All modelling and material changes go into these files.
   - Open and save them only with **Blender 5.3.x**. Saving with another version may change how they open or render.
2. **The car assembly is only a render.**
   - `blender/roboracer_car.blend` *links* the part collections and the wheel collections from the source files in the same folder. It must never hold copies of their geometry or materials.
   - Never use "Make Local" or append parts into it. The only local data allowed are:
     - the root empty `Roboracer_Car` and its drivers;
     - the instance empties `Car_*`;
     - the render stage: `Render_Stage` (camera and lights, shared by both scenes), `Ground_Studio` and `Ground_Checker` (one floor per scene), and the worlds.
   - To change how the car looks, edit the source file. The assembly picks up the change automatically.
3. **Never edit `usd/*.usdc` or `dae/*.dae` directly.**
   - Don't edit them by hand, with scripts, or by importing them into another tool and exporting again.
   - They are always regenerated from the source `.blend` files with `tools/export_all.sh` (see [Exporting](#exporting-usd-and-dae)).
4. **Keep the units and frame conventions.**
   - Metres (scene unit scale 1.0) and Z up. `tools/export_usd.py` refuses to export otherwise.
   - Wheel: origin at the hub centre, wheel axis along X.
   - Frame: origin at the rear axle centre, at wheel-centre height; x forward, y left.
   - Front axle module: origin at the front axle centre, at wheel-centre height; x forward, y left.
   - Center-of-mass marker: origin at the sphere centre; x forward, y left. The assembly places it at (0.15532, 0, 0.01434) m relative to the rear-wheel midpoint.
   - Each car part file has one collection with a root empty of the same name at the origin (`Roboracer_Frame`, `Roboracer_Front_Axle`), and every object is parented to that root.
   - Changing an origin, an axis or the cut position is a breaking change for the URDF.
5. **A change to a source `.blend` and its regenerated exports go in the same commit.**
   - Don't commit re-exports without a `.blend` change. Exports are not byte-identical between runs, because Blender writes USD prims in a varying order and the `.dae` records the export time.
   - `tools/export_all.sh` re-exports every model. Before committing, use `git checkout` to restore the exports of models whose `.blend` didn't change.
6. **Don't change the render scenes** (cameras, lights, world, render settings) unless that is the task.
7. **Never overwrite files without a backup.**
   - Blender keeps the previous save as `*.blend1`, which git ignores.
   - Scratch output goes to `build/`, which git also ignores.

## Tools you need

| Tool | Used for | Notes |
|---|---|---|
| Blender 5.3.x | Editing, USD export, rendering | Official builds: <https://download.blender.org/release/Blender5.3/>. On Linux you can unpack the tarball and run `./blender`; no install needed. |
| Docker | `.dae` export | `tools/export_all.sh` builds the image `traxxas-blender42:4.2.23` from `tools/docker/blender42/Dockerfile` on first use. |
| Git | Version control | Commit identity: `glpuga`. |

Blender 4.2 is only needed for the Collada export, and the Docker image provides it. Don't install it or use it for anything else.

## Editing the wheel

1. **Open the file** `blender/traxxas_6873T_wheel.blend` in Blender 5.3.x.
2. **Edit the wheel parts.** They are in the collections `Traxxas_6873T_L` and `Traxxas_6873T_R`, each under an empty named `Traxxas_6873T_WheelTire_L` or `_R`.
   - Apply every change to both sides.
   - The render scenes show these collections through the `Stack_*_Inst` / `Standing_Inst` instance empties, and the car assembly links them, so all renders update automatically.
3. **Keep real-world sizes in metres.** If you rescale something, also scale whatever depends on size:
   - bevel modifier widths;
   - light sizes, and their power by the square of the scale factor;
   - camera clipping and depth-of-field distances;
   - noise texture `Scale` for textures using Object coordinates, and bump `Distance`.

   Afterwards, compare a test render with the references (see [Rendering](#rendering)).
4. **Save in Blender 5.3.x.**
5. **Regenerate the exports** (see [Exporting](#exporting-usd-and-dae)).
6. **Re-render the references** if the wheel's appearance changed (the wheel scenes and the car), and copy the images into `renders/`.
7. **Commit** the `.blend`, its `usd/` and `dae/` files and, if they changed, `renders/`, all together.

## Editing a car part

1. **Open the part file** (`blender/roboracer_frame.blend`, `blender/roboracer_front_axle.blend` or `blender/roboracer_center_of_mass.blend`) in Blender 5.3.x.
2. **Edit the objects under the root empty.** Keep every object parented to the root, and leave the root at the origin with no rotation or scale.
3. **Keep real-world sizes in metres**, as for the wheel.
4. **Save**, then **regenerate the exports** (see [Exporting](#exporting-usd-and-dae)).
5. **Re-render the car** (see [Rendering](#rendering)) if its appearance changed, and copy the image into `renders/`.
6. **Commit** the `.blend`, its `usd/` and `dae/` files and, if it changed, `renders/`, all together.

**Adding a new part:**
- Create `blender/<part>.blend` following ground rule 4.
- Add it to `EXPORTS` in `tools/export_usd.py` and to `SOURCES` in `tools/export_all.sh`.
- Link its collection into `roboracer_car.blend` (File → Link) and place an instance empty under `Roboracer_Car`.

## Exporting USD and DAE

```bash
BLENDER=/path/to/blender-5.3.x/blender tools/export_all.sh
```

The script runs two steps:

1. **USD.** Blender 5.3 runs `tools/export_usd.py` on each source file. The `EXPORTS` table in the script maps each source file to its collections:

   | Source | Collection | Output |
   |---|---|---|
   | `traxxas_6873T_wheel.blend` | `Traxxas_6873T_L`, `Traxxas_6873T_R` | `usd/traxxas_6873T_wheel_L.usdc`, `_R.usdc` |
   | `roboracer_frame.blend` | `Roboracer_Frame` | `usd/roboracer_frame.usdc` |
   | `roboracer_front_axle.blend` | `Roboracer_Front_Axle` | `usd/roboracer_front_axle.usdc` |
   | `roboracer_center_of_mass.blend` | `Roboracer_Center_Of_Mass` | `usd/roboracer_center_of_mass.usdc` |

   - Each root prim is named after its collection (e.g. `/Roboracer_Frame`), and `metersPerUnit` is 1.
   - Modifiers are applied, and materials are written as UsdPreviewSurface.
   - The wheel file's `Scene` view layer excludes the L collection. The script includes it only for the export and never saves the `.blend`.
   - The assembly `roboracer_car.blend` is never exported. The URDF assembles the parts itself.
2. **Collada.** Blender 5.0 removed the Collada exporter, so this step uses Blender 4.2.23 LTS in Docker:
   - `tools/export_dae.py` imports every `usd/*.usdc` and exports the matching `dae/*.dae`, with `<unit meter="1"/>` and triangulated meshes.
   - The Blender download in the image is checked against its SHA-256.

**Materials in exports.** USD and DAE consumers only see the Principled BSDF *default* values, not procedural node graphs. When a node drives a material input, keep that input's default set to a sensible flat colour or roughness.

The center-of-mass marker uses two face-assigned materials so its checkerboard survives USD/DAE export without texture files. Preserve those assignments when editing the sphere.

Light-gray marker squares are 25% opaque, non-metallic and non-refractive (IOR 1) to better match DAE's diffuse transparency in USD/Omniverse; red squares remain fully opaque and metallic in Blender/USD. Keep the Principled Alpha and material display alpha consistent. `tools/export_usd.py` temporarily compensates for Blender 5.3 overwriting constant alpha with its transmission mapping; it restores the shader after export and never saves the source.

**Check the result:** `git status` should show changes only in `usd/` and `dae/`. Expected sizes, measured over the mesh points (min → max, metres):

| Model | Meshes | Bounds |
|---|---|---|
| Wheel L / R | 33 | about 0.039 × 0.1095 × 0.1095 (X × Y × Z), centred on the hub |
| Frame | 4 | (-0.135, -0.137, -0.008) → (0.272, 0.137, 0.092) |
| Front axle module | 3 | (-0.052, -0.153, -0.008) → (0.167, 0.153, 0.070) |
| Center-of-mass marker | 1 | (-0.050, -0.050, -0.050) → (0.050, 0.050, 0.050) |

## Rendering

There are three render setups, each in two versions: a studio backdrop, and a MuJoCo-style checker floor. Their lighting, materials and denoising are already set up.

| File | Scene | Content | Camera | Resolution | Samples | Output file |
|---|---|---|---|---|---|---|
| `traxxas_6873T_wheel.blend` | `Scene` | Single wheel in a studio set | `Camera` | 1920×1280 | 160 | `traxxas_6873T_render.png` |
| `traxxas_6873T_wheel.blend` | `Scene_Checker` | Same, on the checker floor | `Camera` | 1920×1280 | 160 | `traxxas_6873T_checker_render.png` |
| `traxxas_6873T_wheel.blend` | `Stack` | 3 wheels stacked plus 1 standing | `StackCam` | 2400×1600 | 256 | `traxxas_6873T_stack_render.png` |
| `traxxas_6873T_wheel.blend` | `Stack_Checker` | Same, on the checker floor | `StackCam` | 2400×1600 | 256 | `traxxas_6873T_stack_checker_render.png` |
| `roboracer_car.blend` | `Car` | Assembled car | `Camera` | 1600×1000 | 128 | `roboracer_car_render.png` |
| `roboracer_car.blend` | `Car_Checker` | Same, on the checker floor | `Camera` | 1600×1000 | 128 | `roboracer_car_checker_render.png` |

**How the checker versions are built.** Each `*_Checker` scene reuses its studio scene's camera, lights and models (the same objects, linked into both scenes), so changing them updates both versions. Each version has its own floor and world:
- The studio floor (`Ground` in `Scene`, the `Cyc` backdrop in `Stack`, `Ground_Studio` in the car) is replaced by a flat plane using the `Ground_Checker` material.
- That material copies MuJoCo's default `groundplane` look: tiles in sRGB (0.2, 0.3, 0.4) and (0.1, 0.2, 0.3), with (0.8, 0.8, 0.8) edge lines. The tiles are 0.1 m, aligned with the model origin.
- The camera sees a plain dark background. Lighting still comes from each setup's own sources:
  - The wheel scenes get most of their light from the studio sky (`World` and `StackWorld`), so their checker worlds (`World_Checker_Scene` and `World_Checker_Stack`) reuse that sky for lighting and reflections, and switch to dark only for camera rays (Light Path → Is Camera Ray).
  - The car scene is lit by its area lights, so `World_Checker` is just a dark background.

By default `tools/render.py` renders every one of these scenes found in the file it is given.

1. **Do a quick test render** (a few seconds on a GPU). It confirms the GPU works:

   ```bash
   /path/to/blender -b blender/traxxas_6873T_wheel.blend --python tools/render.py -- \
       --percent 25 --samples 16 --no-cpu-fallback --out build/renders_test
   ```

   Look for `OK on OPTIX` (or `CUDA`, `HIP`, …) in the `[render]` lines.
2. **Do the full render.** Output goes to `build/renders/` by default:

   ```bash
   /path/to/blender -b blender/traxxas_6873T_wheel.blend --python tools/render.py
   /path/to/blender -b blender/roboracer_car.blend --python tools/render.py
   ```

3. **Check the results.**
   - Compare them with `renders/`: they should have the same framing and colours, with only slightly different noise.
   - The images should not be black or cropped, and no wheel or part should be missing.
4. **Update the references** only if a model's appearance changed on purpose: copy the new images from `build/renders/` into `renders/`. Otherwise, don't overwrite `renders/`.

**`tools/render.py` options.** Everything after the `--` goes to the script:

| Option | Default | Notes |
|---|---|---|
| `--scenes NAME …` | the file's scenes from the table above | Render only some of the scenes |
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
| `Scene_Checker` | — | about 16 s |
| `Stack_Checker` | — | about 29 s |
| `Car` | — | about 12 s |
| `Car_Checker` | — | about 12 s |

### Render troubleshooting

- **Blender crashes about 1 s after loading, and the crash log shows `libze_loader` / `zeInitDrivers`:**
  - The Intel oneAPI device probe crashed. Cycles runs it even with `--device OPTIX`.
  - Fix: run Blender with `ONEAPI_DEVICE_SELECTOR='opencl:*'` set in the environment.
- **`Failed to load CUDA kernel … (Invalid kernel image)`:** the NVIDIA driver is too old for this Blender build. Update the driver.
- **`OPTIX: no devices`, but CUDA works:** OptiX needs an RTX card or a newer driver. CUDA gives the same image, just more slowly.
- **Only `CPU` in the summary:** no GPU backend worked. Rerun with `--no-cpu-fallback` to see each failure.
- **The image looks different from the reference:** check the Blender version (`blender --version`). It must be 5.3.x.
- **Parts or wheels are missing from the car render:** a linked file was not found. All source files must stay in `blender/` next to `roboracer_car.blend`. In Blender, use File → External Data → Report Missing Files.

## Commits

- **Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):** `<type>[optional scope][!]: <description>`.
  - The description is lowercase and in the imperative mood, without a trailing full stop.
  - Add a body with bullets explaining what changed and why.
- **Types:**

  | Type | Use for |
  |---|---|
  | `feat` | Changes to a model (a new part, or new geometry or material in a `.blend`) |
  | `fix` | Model or tooling bugs |
  | `refactor` | Restructuring with no visible change to the model |
  | `docs` | Documentation only |
  | `build` | Docker images and export tooling environments |
  | `chore` | Housekeeping, e.g. `.gitignore` |

- **Breaking changes:** mark them with `!` (e.g. `feat!:`) and add a `BREAKING CHANGE:` footer. A change is breaking if it affects people who use the exports, e.g. new units, a different axis convention, a moved origin or cut, renamed prims or nodes, or moved file paths.
- **Scopes** (optional): `wheel`, `frame`, `front-axle`, `assembly`, `tools`.
- **One logical change per commit**, with each `.blend` and its exports committed together.
- **AI-assisted commits:** add the trailer `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
