"""Headless renderer for the scenes in blender/traxxas_6873T_wheel.blend and blender/roboracer_car.blend.

Usage (from the repo root):
  blender -b blender/<file>.blend --python tools/render.py -- [options]

Options:
  --scenes NAME [NAME ...]  Scenes to render (default: every scene listed in OUTPUT_NAMES)
  --out DIR                 Output directory (default: build/renders in the repo)
  --device DEV              auto | OPTIX | CUDA | HIP | ONEAPI | METAL | CPU (default: auto)
  --samples N               Override Cycles samples (default: keep the scene's value)
  --percent P               Resolution percentage (default: 100)
  --no-cpu-fallback         Fail instead of falling back to CPU if no GPU backend works
"""
import argparse
import os
import sys
import time

import bpy

GPU_ORDER = ["OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"]
OUTPUT_NAMES = {
    "Scene": "traxxas_6873T_render",  # traxxas_6873T_wheel.blend
    "Stack": "traxxas_6873T_stack_render",  # traxxas_6873T_wheel.blend
    "Scene_Checker": "traxxas_6873T_checker_render",  # traxxas_6873T_wheel.blend
    "Stack_Checker": "traxxas_6873T_stack_checker_render",  # traxxas_6873T_wheel.blend
    "Car": "roboracer_car_render",  # roboracer_car.blend
    "Car_Checker": "roboracer_car_checker_render",  # roboracer_car.blend
}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="render.py")
    p.add_argument("--scenes", nargs="+", default=None)
    p.add_argument("--out", default=None)
    p.add_argument("--device", default="auto")
    p.add_argument("--samples", type=int, default=None)
    p.add_argument("--percent", type=int, default=100)
    p.add_argument("--no-cpu-fallback", action="store_true")
    return p.parse_args(argv)


def enable_backend(backend):
    """Enable all devices of a GPU backend. Returns the device names, or [] if unavailable."""
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = backend
    except TypeError:
        return []
    prefs.get_devices()
    names = []
    for d in prefs.devices:
        d.use = d.type == backend
        if d.use:
            names.append(d.name)
    return names


def candidate_devices(requested, allow_cpu):
    order = GPU_ORDER if requested == "auto" else [requested]
    out = [b for b in order if b != "CPU"]
    if requested == "CPU" or allow_cpu:
        out.append("CPU")
    return out


def render_scene(scn, path, devices):
    for dev in devices:
        if dev == "CPU":
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "NONE"
            scn.cycles.device = "CPU"
            names = ["CPU"]
        else:
            names = enable_backend(dev)
            if not names:
                print(f"[render] {dev}: no devices, skipping")
                continue
            scn.cycles.device = "GPU"
        print(f"[render] {scn.name}: trying {dev} {names}")
        t = time.time()
        try:
            bpy.ops.render.render(write_still=True, scene=scn.name)
        except RuntimeError as e:
            # e.g. "Failed to load CUDA kernel" when the driver is too old for this Blender build
            print(f"[render] {scn.name}: {dev} failed: {str(e).strip().splitlines()[0]}")
            continue
        if not os.path.isfile(path):
            print(f"[render] {scn.name}: {dev} produced no file")
            continue
        print(f"[render] {scn.name}: OK on {dev} in {time.time() - t:.1f}s -> {path}")
        return dev
    raise SystemExit(f"[render] {scn.name}: all devices failed ({devices})")


def main():
    a = parse_args()
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.abspath(a.out or os.path.join(repo_dir, "build", "renders"))
    os.makedirs(out_dir, exist_ok=True)
    devices = candidate_devices(a.device.upper() if a.device != "auto" else "auto",
                                allow_cpu=not a.no_cpu_fallback)
    summary = []
    scenes = a.scenes or [n for n in OUTPUT_NAMES if n in bpy.data.scenes]
    for name in scenes:
        scn = bpy.data.scenes.get(name)
        if scn is None:
            raise SystemExit(f"[render] unknown scene {name!r}; available: {[s.name for s in bpy.data.scenes]}")
        scn.render.engine = "CYCLES"
        scn.render.resolution_percentage = a.percent
        if a.samples:
            scn.cycles.samples = a.samples
        scn.render.image_settings.file_format = "PNG"
        path = os.path.join(out_dir, OUTPUT_NAMES.get(name, name) + ".png")
        scn.render.filepath = path
        if os.path.exists(path):
            os.remove(path)
        used = render_scene(scn, path, devices)
        summary.append((name, used, path))
    print("[render] SUMMARY")
    for name, used, path in summary:
        print(f"[render]   {name}: {used} -> {path}")


main()
