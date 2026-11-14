# Traxxas 6873T wheel

3D model of the Traxxas 6873T wheel and tyre, sized like the stock Traxxas Slash tyre. It is meant for the Roboracer / F1TENTH 1/10-scale car model used with ROS 2. There are left (`_L`) and right (`_R`) versions.

| Property | Value |
|---|---|
| Units | metres |
| Up axis | +Z |
| Wheel axis | X |
| Tyre diameter | 0.1095 m |
| Tyre width | about 0.039 m |

The rim has open spokes, with no back plate.

![Wheel](renders/traxxas_6873T_render.png)

## Layout

| Folder | Contents |
|---|---|
| [`blender/`](blender/) | `traxxas_6873T_wheel.blend`, **the source of truth**. Saved with Blender 5.2.x. It also holds the two render scenes. |
| [`usd/`](usd/) | `traxxas_6873T_wheel_L.usdc` and `_R.usdc`, exported from the `.blend`. **Never edit these by hand.** |
| [`dae/`](dae/) | `traxxas_6873T_wheel_L.dae` and `_R.dae` (Collada, e.g. for RViz or Gazebo), exported from the `.usdc` files. **Never edit these by hand.** |
| [`renders/`](renders/) | Reference images rendered from the `.blend`. |
| [`tools/`](tools/) | Python export and render scripts, the `export_all.sh` wrapper, and the Dockerfile in `tools/docker/`. |
| `build/` | Scratch output, such as test renders. Ignored by git. |

## Quick start

These commands need Blender 5.2.x. The `.dae` export also needs Docker.

```bash
# Regenerate usd/ and dae/ after changing the .blend
BLENDER=/path/to/blender-5.2.x/blender tools/export_all.sh

# Render the reference scenes into build/renders/
/path/to/blender-5.2.x/blender -b blender/traxxas_6873T_wheel.blend --python tools/render.py
```

See [AGENTS.md](AGENTS.md) for the full procedures and rules. They apply to both people and AI agents.
