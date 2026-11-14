#!/usr/bin/env bash
# Regenerate the derived usd/*.usdc and dae/*.dae files from the source .blend files.
# Usage: BLENDER=/path/to/blender-5.3.x/blender tools/export_all.sh
set -euo pipefail

cd "$(dirname "$0")/.."
BLENDER="${BLENDER:-blender}"
IMAGE=traxxas-blender42:4.2.23
SOURCES=(traxxas_6873T_wheel roboracer_frame roboracer_front_axle roboracer_center_of_mass)

"$BLENDER" --version | head -1 | grep -q '^Blender 5\.3\.' \
    || { echo "BLENDER must point to Blender 5.3.x (got: $("$BLENDER" --version | head -1))" >&2; exit 1; }

for src in "${SOURCES[@]}"; do
    "$BLENDER" -b "blender/$src.blend" --python-exit-code 1 --python tools/export_usd.py
done

docker image inspect "$IMAGE" >/dev/null 2>&1 || docker build -t "$IMAGE" tools/docker/blender42
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/work "$IMAGE" \
    --python-exit-code 1 --python tools/export_dae.py
