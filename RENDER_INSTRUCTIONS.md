# Render instructions — Traxxas 6873T wheel

Instructions for an agent (or a person) to re-render the two final images on a machine with a GPU.

## What you need

- **This folder.** Only `traxxas_6873T_wheel.blend` and `render.py` are needed to render. The `.blend` file is self-contained (no textures or linked files).
- **Blender 5.2.x.** The file was saved with Blender 5.2.1 LTS. Older versions may open it wrong.
  - Official builds: <https://download.blender.org/release/Blender5.2/>
  - On Linux you can just unpack the tarball and run `./blender`. No install needed.
- **A GPU with a recent driver.**
  - Blender's renderer (Cycles) supports these GPU types: OptiX or CUDA (NVIDIA), HIP (AMD), oneAPI (Intel), Metal (Apple).
  - The scenes are small (about 80k triangles per wheel), so any GPU with 2 GB or more of memory is enough.

## Model

- Units are metres, Z up, and the wheel axis is X. The tyre is 0.1095 m in diameter (the stock Traxxas Slash size) and about 0.039 m wide. The rim has no back plate.
- The `.blend` is the source of truth. The `.usdc` and `.dae` files are derived from it. See [README.md](README.md) for how to regenerate them.

## Scenes in the file

| Scene | Content | Camera | Resolution | Samples | Output file |
|---|---|---|---|---|---|
| `Scene` | Single wheel in a studio set | `Camera` | 1920×1280 | 160 | `traxxas_6873T_render.png` |
| `Stack` | 3 wheels stacked plus 1 standing | `StackCam` | 2400×1600 | 256 | `traxxas_6873T_stack_render.png` |

Both scenes already have their lighting, materials, depth of field and denoising set up. **Don't change the scenes**; only use the options below.

## Steps

1. **Check the GPU and driver.** On NVIDIA, run `nvidia-smi`; it should list the GPU.

2. **Do a quick test render** (about 20 s). It confirms the GPU works:

   ```bash
   cd /path/to/traxxas_6873T
   /path/to/blender -b traxxas_6873T_wheel.blend --python render.py -- \
       --percent 25 --samples 16 --no-cpu-fallback --out renders_test
   ```

   Look for `OK on OPTIX` (or `CUDA`, `HIP`, …) in the `[render]` lines.
   - If it says `all devices failed`, the GPU isn't usable. See [Troubleshooting](#troubleshooting).
   - `--no-cpu-fallback` makes the test fail loudly instead of quietly rendering on the CPU.

3. **Do the full render:**

   ```bash
   /path/to/blender -b traxxas_6873T_wheel.blend --python render.py -- --out renders
   ```

   It renders both scenes. The `SUMMARY` at the end lists the device used and the output path for each.

4. **Check the results:**
   - `renders/traxxas_6873T_render.png` should be 1920×1280, and `renders/traxxas_6873T_stack_render.png` should be 2400×1600.
   - Compare them with the reference images in this folder: [traxxas_6873T_render.png](traxxas_6873T_render.png) and [traxxas_6873T_stack_render.png](traxxas_6873T_stack_render.png). These were rendered with OptiX on an RTX 2060.
   - The GPU output should look the same: same framing and colours, with slightly different noise. The images should not be black, cropped, or missing a wheel.

5. **Report back:**
   - which device was used and how long each scene took (both appear in the `[render]` lines);
   - the output file paths;
   - any warnings.

   Don't overwrite the reference images. Output goes to `renders/` by default.

## `render.py` options

Everything after the `--` goes to the script:

| Option | Default | Notes |
|---|---|---|
| `--scenes NAME …` | `Scene Stack` | Render only some of the scenes, e.g. `--scenes Stack` |
| `--out DIR` | `./renders` | Created if missing |
| `--device DEV` | `auto` | `auto` tries OPTIX → CUDA → HIP → ONEAPI → METAL, then CPU. Or force one, e.g. `--device CUDA` |
| `--samples N` | the scene's own value | On a fast GPU, `--samples 1024` gives cleaner images |
| `--percent P` | `100` | `200` gives 2× the resolution (e.g. 4800×3200 for `Stack`) |
| `--no-cpu-fallback` | off | Fail instead of falling back to the CPU |

The script never saves the `.blend` file; all overrides apply only to that run.

## Expected timings

| Scene | CPU only (16 threads) | OptiX, RTX 2060 |
|---|---|---|
| `Scene` | about 80–90 s | about 20 s |
| `Stack` | about 10 min | about 46 s |

## Troubleshooting

- **`Failed to load CUDA kernel … (Invalid kernel image)`:** the NVIDIA driver is too old for the GPU code that ships with this Blender build. This is what happened on the original machine (GTX 1660 SUPER). Update the driver, or use a Blender build that matches the installed driver.
- **Blender crashes about 1 s after loading the file, and the crash log shows `libze_loader` / `zeInitDrivers`:** the Intel oneAPI (Level Zero) device probe crashed. Cycles runs this probe even when you pass `--device OPTIX`. To skip it, run Blender with `ONEAPI_DEVICE_SELECTOR='opencl:*'` set in the environment, e.g. `ONEAPI_DEVICE_SELECTOR='opencl:*' /path/to/blender -b …`. NVIDIA rendering is not affected.
- **`OPTIX: no devices`, but CUDA works:** OptiX needs a newer driver or an RTX card. CUDA gives the same image, just more slowly. Nothing needs fixing.
- **Only `CPU` in the summary:** no GPU backend worked. Rerun with `--no-cpu-fallback` to see each failure.
- **The image looks different from the reference:** check that the Blender version is 5.2.x (`blender --version`). Don't open and re-save the `.blend` in another version.
