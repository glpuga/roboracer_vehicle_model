#!/usr/bin/env bash
# Regenerate the derived usd/*.usdc and dae/*.dae files from blender/traxxas_6873T_wheel.blend.
# Usage: BLENDER=/path/to/blender-5.2.x/blender tools/export_all.sh
set -euo pipefail

cd "$(dirname "$0")/.."
BLENDER="${BLENDER:-blender}"
IMAGE=traxxas-blender42:4.2.23

"$BLENDER" --version | head -1 | grep -q '^Blender 5\.2\.' \
    || { echo "BLENDER must point to Blender 5.2.x (got: $("$BLENDER" --version | head -1))" >&2; exit 1; }

"$BLENDER" -b blender/traxxas_6873T_wheel.blend --python-exit-code 1 --python tools/export_usd.py

docker image inspect "$IMAGE" >/dev/null 2>&1 || docker build -t "$IMAGE" tools/docker/blender42
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/work "$IMAGE" \
    --python-exit-code 1 --python tools/export_dae.py
