# Traxxas 6873T wheel and Roboracer car parts

Visual models for the Roboracer / F1TENTH 1/10-scale car model used with ROS 2:

- the **Traxxas 6873T wheel** and tyre, sized like the stock Traxxas Slash tyre, in left (`_L`) and right (`_R`) versions;
- the **car body**, split into a **frame** and a **front axle module** so that the URDF can set the wheelbase as a parameter;
- independent **rear and front bumpers**, so the URDF can select either bumper separately;
- a **car assembly**, used only for rendering, that links the parts and the wheels.

All models use metres, with +Z up.

## Models

| Model | Source | Origin and axes | Contents |
|---|---|---|---|
| Wheel L / R | `blender/traxxas_6873T_wheel.blend` | Hub centre; wheel axis along X | Tyre (0.1095 m diameter, about 0.039 m wide) and rim with open spokes |
| Frame | `blender/roboracer_frame.blend` | Rear axle centre, at wheel-centre height; x forward, y left | Chassis plate up to the cut, rear suspension and shocks, nerf bars; no rear bumper |
| Front axle module | `blender/roboracer_front_axle.blend` | Front axle centre, at wheel-centre height; x forward, y left | Front bulkhead and gearbox, front plate section, front suspension and shocks; no front bumper or connecting skid ramp |
| Rear bumper | `blender/roboracer_rear_bumper.blend` | Rearmost X extent, centreline, at frame-origin height; x forward, y left | Tubular rear bumper, triangulated supports, mounting blocks and fasteners |
| Front bumper | `blender/roboracer_front_bumper.blend` | Frontmost X extent, centreline, at frame-origin height; x forward, y left | Rubber bumper, connecting skid ramp, mounting plate, blocks and fasteners |
| Center-of-mass marker | `blender/roboracer_center_of_mass.blend` | Sphere centre; x forward, y left | 0.100 m diameter sphere with a metallic-red/translucent-light-gray checkerboard |

- The frame and front axle module meet at a cut 0.272 m ahead of the frame origin, which is 0.052 m behind the front axle origin. That puts the nominal **wheelbase at 0.324 m**.
- Wheel centres sit at y = ±0.145 (**track 0.290 m**), 0.055 m above the ground.
- In the car the wheels are rotated about Z: +90° on the left side, −90° on the right, so the hubs face outwards.
- The rear bumper has one shallow face, three lower support triangles and two screw-mounted braces to a raised crossbar. Its top corner span is approximately 0.162 m, estimated from reference photos using the 0.186 m chassis plate width, rather than measured from the physical part.
- Both bumpers are independent parts, including their supports and fasteners. Their root frames are at the outermost X extent, y = 0 and axle-relative z = 0, not at their geometry centres. Place the rear bumper at **(-0.1348, 0, 0) m relative to the frame** and the front bumper at **(0.1671, 0, 0) m relative to the front axle**. At the nominal wheelbase, the front bumper origin is (0.4911, 0, 0) m relative to the frame. Both origins are 0.055 m above the ground in the assembly.
- The center-of-mass marker is a separate linked part, centred at (0.15532, 0, 0.01434) m relative to the rear-wheel midpoint, or 0.06934 m above the ground. Its 16 × 8 checkerboard uses two face-assigned materials, preserving the red/light-gray pattern in USD/DAE without texture files. Light-gray squares are 25% opaque and non-metallic, with IOR 1 to avoid refraction and better match DAE's diffuse transparency in USD/Omniverse. Red squares remain fully opaque and metallic in Blender/USD; DAE uses diffuse materials. Lighting, tone mapping and transparency support can still differ by viewer.

## Gallery

Each view has a studio backdrop and a MuJoCo-style checker floor with 0.1 m tiles. Each also has a DAE counterpart: the same camera, lights, floor and world, but model geometry and materials read from the actual exported Collada files.

| | Studio (.blend) | Checker (.blend) | Studio (DAE) | Checker (DAE) |
|---|---|---|---|---|
| Car assembly | [![Car, studio](renders/roboracer_car_render.png)](renders/roboracer_car_render.png) | [![Car, checker](renders/roboracer_car_checker_render.png)](renders/roboracer_car_checker_render.png) | [![DAE car, studio](renders/roboracer_car_render_dae.png)](renders/roboracer_car_render_dae.png) | [![DAE car, checker](renders/roboracer_car_checker_render_dae.png)](renders/roboracer_car_checker_render_dae.png) |
| Single wheel | [![Wheel, studio](renders/traxxas_6873T_render.png)](renders/traxxas_6873T_render.png) | [![Wheel, checker](renders/traxxas_6873T_checker_render.png)](renders/traxxas_6873T_checker_render.png) | [![DAE wheel, studio](renders/traxxas_6873T_render_dae.png)](renders/traxxas_6873T_render_dae.png) | [![DAE wheel, checker](renders/traxxas_6873T_checker_render_dae.png)](renders/traxxas_6873T_checker_render_dae.png) |
| Wheel stack | [![Wheel stack, studio](renders/traxxas_6873T_stack_render.png)](renders/traxxas_6873T_stack_render.png) | [![Wheel stack, checker](renders/traxxas_6873T_stack_checker_render.png)](renders/traxxas_6873T_stack_checker_render.png) | [![DAE wheel stack, studio](renders/traxxas_6873T_stack_render_dae.png)](renders/traxxas_6873T_stack_render_dae.png) | [![DAE wheel stack, checker](renders/traxxas_6873T_stack_checker_render_dae.png)](renders/traxxas_6873T_stack_checker_render_dae.png) |
| Frame | [![Frame, studio](renders/roboracer_frame_render.png)](renders/roboracer_frame_render.png) | [![Frame, checker](renders/roboracer_frame_checker_render.png)](renders/roboracer_frame_checker_render.png) | [![DAE frame, studio](renders/roboracer_frame_render_dae.png)](renders/roboracer_frame_render_dae.png) | [![DAE frame, checker](renders/roboracer_frame_checker_render_dae.png)](renders/roboracer_frame_checker_render_dae.png) |
| Front axle | [![Front axle, studio](renders/roboracer_front_axle_render.png)](renders/roboracer_front_axle_render.png) | [![Front axle, checker](renders/roboracer_front_axle_checker_render.png)](renders/roboracer_front_axle_checker_render.png) | [![DAE front axle, studio](renders/roboracer_front_axle_render_dae.png)](renders/roboracer_front_axle_render_dae.png) | [![DAE front axle, checker](renders/roboracer_front_axle_checker_render_dae.png)](renders/roboracer_front_axle_checker_render_dae.png) |
| Rear bumper | [![Rear bumper, studio](renders/roboracer_rear_bumper_render.png)](renders/roboracer_rear_bumper_render.png) | [![Rear bumper, checker](renders/roboracer_rear_bumper_checker_render.png)](renders/roboracer_rear_bumper_checker_render.png) | [![DAE rear bumper, studio](renders/roboracer_rear_bumper_render_dae.png)](renders/roboracer_rear_bumper_render_dae.png) | [![DAE rear bumper, checker](renders/roboracer_rear_bumper_checker_render_dae.png)](renders/roboracer_rear_bumper_checker_render_dae.png) |
| Front bumper | [![Front bumper, studio](renders/roboracer_front_bumper_render.png)](renders/roboracer_front_bumper_render.png) | [![Front bumper, checker](renders/roboracer_front_bumper_checker_render.png)](renders/roboracer_front_bumper_checker_render.png) | [![DAE front bumper, studio](renders/roboracer_front_bumper_render_dae.png)](renders/roboracer_front_bumper_render_dae.png) | [![DAE front bumper, checker](renders/roboracer_front_bumper_checker_render_dae.png)](renders/roboracer_front_bumper_checker_render_dae.png) |
| Center-of-mass marker | [![Marker, studio](renders/roboracer_center_of_mass_render.png)](renders/roboracer_center_of_mass_render.png) | [![Marker, checker](renders/roboracer_center_of_mass_checker_render.png)](renders/roboracer_center_of_mass_checker_render.png) | [![DAE marker, studio](renders/roboracer_center_of_mass_render_dae.png)](renders/roboracer_center_of_mass_render_dae.png) | [![DAE marker, checker](renders/roboracer_center_of_mass_checker_render_dae.png)](renders/roboracer_center_of_mass_checker_render_dae.png) |

`tools/render.py` renders both backgrounds by default; `--dae` switches the models to their exported counterparts and adds `_dae` to the filenames. Every part of the DAE car is converted, including both bumpers, all four wheels and the center-of-mass marker. The standalone part stages are created in memory; no `.blend` is saved.

These are Blender renders of DAE's exported Lambert materials, not screenshots from Isaac Sim, RViz or Gazebo. Procedural shading and PBR metallic reflections are absent in DAE; transparency and lighting can still differ by viewer. See [AGENTS.md](AGENTS.md#rendering) for setup and commands.

## Layout

| Folder | Contents |
|---|---|
| [`blender/`](blender/) | Wheel, frame, front axle, rear/front bumper and center-of-mass `.blend` files, **the sources of truth**. `roboracer_car.blend` is the assembly: it only links the other files and holds the car render scene. The wheel file also holds the two wheel render scenes. |
| [`usd/`](usd/) | One `.usdc` per wheel side and per car part, exported from the `.blend` files. **Never edit these by hand.** |
| [`dae/`](dae/) | The same models as Collada (e.g. for URDF, RViz or Gazebo), exported from the `.usdc` files. **Never edit these by hand.** |
| [`renders/`](renders/) | Native Blender and exported-DAE reference images. |
| [`tools/`](tools/) | Python export and render scripts, the `export_all.sh` wrapper, and the Dockerfile in `tools/docker/`. |
| `build/` | Scratch output, such as test renders. Ignored by git. |

## Car assembly parameters

The root empty `Roboracer_Car` in `roboracer_car.blend` sits at the rear axle centre and has two custom properties:

- `wheelbase` (default 0.324 m) moves the front axle module, front bumper and front wheels;
- `track` (default 0.290 m) moves every wheel to y = ±track/2.

The drivers use simple expressions, so they work without enabling Python auto-run. Changing the wheelbase opens a gap, or an overlap, in the chassis plate at the cut. That is expected, and the URDF will behave the same way.

**URDF migration:** the frame and front-axle exports no longer contain their bumpers. Add `roboracer_rear_bumper` and `roboracer_front_bumper` as separate meshes or fixed child links, using the offsets above with no rotation. Each has matching `.usdc` and `.dae` exports and a root named `Roboracer_Rear_Bumper` or `Roboracer_Front_Bumper`. Existing frame/front-axle origins and the assembled car geometry are unchanged.

## Quick start

These commands need Blender 5.3.x. The `.dae` export also needs Docker.

```bash
# Regenerate usd/ and dae/ after changing a source .blend
BLENDER=/path/to/blender-5.3.x/blender tools/export_all.sh

# Render the reference scenes into build/renders/
/path/to/blender-5.3.x/blender -b blender/roboracer_car.blend --python tools/render.py
/path/to/blender-5.3.x/blender -b blender/traxxas_6873T_wheel.blend --python tools/render.py

# Standalone parts (also creates studio/checker views in memory)
/path/to/blender-5.3.x/blender -b blender/roboracer_frame.blend --python tools/render.py
/path/to/blender-5.3.x/blender -b blender/roboracer_front_axle.blend --python tools/render.py
/path/to/blender-5.3.x/blender -b blender/roboracer_center_of_mass.blend --python tools/render.py
/path/to/blender-5.3.x/blender -b blender/roboracer_rear_bumper.blend --python tools/render.py
/path/to/blender-5.3.x/blender -b blender/roboracer_front_bumper.blend --python tools/render.py

# DAE counterparts; install the optional reader first (see AGENTS.md)
/path/to/blender-5.3.x/blender -b blender/roboracer_car.blend --python tools/render.py -- --dae
```

See [AGENTS.md](AGENTS.md) for the full procedures and rules. They apply to both people and AI agents.

## Modelling provenance

The parts were created in Blender with AI-assisted modelling using [MCP for Blender](https://github.com/ahujasid/mcp-for-blender). Scripted part extraction, export, validation and reference rendering use Blender's Python API and the tools in this repository. MCP for Blender is a modelling aid, not a requirement for regenerating the exports or renders.

## External dependencies and licence review

Reviewed on **2026-11-14** against the tracked scripts, installed Python distributions, Blender's bundled licence manifests, the export container's package copyright files and upstream licences. This covers the direct toolchain and declared Python dependencies, not a complete SBOM of Blender, Ubuntu, GPU drivers or an independently installed MCP server.

### Script and authoring dependencies

| Dependency | Use / reviewed version | Licence |
|---|---|---|
| [Blender](https://docs.blender.org/manual/en/latest/getting_started/about/license.html), including `bpy`, `mathutils` and `bpy_extras` | Modelling, USD export, rendering and tests: 5.3.x; Collada export only: 4.2.23 | **GPL-3.0-or-later**; bundled libraries have additional licences listed in Blender's `license/license.md` and `license/licenses.json` |
| [CPython and standard library](https://docs.python.org/3/license.html) | Supplied by each Blender build; includes the XML parser and test runner | PSF-2.0 and the accompanying historical/component notices |
| [NumPy](https://numpy.org/doc/stable/license.html) | Geometry conversion and tests; 2.3.4 in the reviewed Blender 5.3 build | BSD-3-Clause for NumPy; retain any binary-build dependency notices |
| [PyCollada](https://github.com/pycollada/pycollada) | Actual DAE geometry/material reader; pinned to 0.9.3 | BSD-3-Clause, verified in the installed `COPYING` |
| [python-dateutil](https://github.com/dateutil/dateutil/blob/master/LICENSE) | PyCollada dependency; pinned to 4.0.0 | BSD-3-Clause applies to all code according to its installed licence; also contains Apache-2.0 notices for eligible contributions |
| [tzdata](https://github.com/python/tzdata/blob/master/LICENSE) | Declared dependency of python-dateutil 4.0.0; **missing from the reviewed installation**, see findings below | Apache-2.0 for the package; [IANA time-zone data](https://github.com/eggert/tz/blob/main/LICENSE) is public domain, subject to its listed exceptions |
| [six](https://github.com/benjaminp/six) | Pinned to 1.17.0, although not used by the current reader dependency chain | MIT |
| [pip](https://github.com/pypa/pip/blob/main/LICENSE.txt) | Optional Python dependency installation | MIT; its vendored components retain their own notices |
| [Docker CLI](https://github.com/docker/cli/blob/master/LICENSE) / [Moby Engine](https://github.com/moby/moby) | Builds and runs the Collada exporter | Apache-2.0 for these projects; Docker Desktop is not required and has separate product terms |
| Bash, grep, tar and basic utilities | Export wrapper and container build | GNU Bash/grep/tar and GNU coreutils: GPL-3.0-or-later. The reviewed host's `head`, `dirname`, `id` and `sha256sum` are [uutils coreutils](https://github.com/uutils/coreutils/blob/main/LICENSE), MIT; the container uses GNU utilities |
| [Git](https://git-scm.com/about/free-and-open-source) | Contributor version-control workflow, not an export/render dependency | GPL-2.0-only overall, with additional component notices |
| [MCP for Blender](https://github.com/ahujasid/mcp-for-blender/blob/main/LICENSE) | Optional AI-assisted authoring; not required by the repository scripts | MIT. Its reviewed upstream manifest also declares the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk/blob/main/LICENSE) (MIT) and [HTTPX](https://github.com/encode/httpx/blob/master/LICENSE.md) (BSD-3-Clause); the full resolved server environment is not pinned here |
| GPU backends and drivers | Optional OptiX/CUDA/HIP/oneAPI/Metal acceleration; CPU rendering is supported | Vendor/component-specific terms; some are proprietary. They are not relicensed by this repository |

`tools/requirements-render.txt` pins the extra reader packages; NumPy and Blender's Python modules come from Blender. PyCollada's optional `lxml` extras are not installed or required by this workflow.

### Export-container packages

The Dockerfile uses `ubuntu:24.04` and installs the packages below. Ubuntu itself has **no single covering licence**. These entries summarize the reviewed packages, not every transitive OS library. Package versions can change on rebuild because the apt packages and base-image digest are not pinned.

| Explicit package(s) | Licence notes |
|---|---|
| `ca-certificates` | GPL-2.0-or-later for the packaging/tools; MPL-2.0 for Mozilla certificate data |
| `curl` | curl licence (permissive); its package retains additional per-file notices |
| `xz-utils` | Reviewed container version 5.4.5: public-domain core plus GPL-2.0-or-later helpers and LGPL-2.1-or-later components |
| `libx11-6`, `libxi6`, `libxxf86vm1`, `libxfixes3`, `libxrender1`, `libxkbcommon0`, `libsm6`, `libice6` | MIT/X11-style permissive licences, with package-specific notices |
| `libgl1`, `libegl1` | Primarily MIT, with Apache-2.0/BSD notices; source-package notices also cover GPL-licensed build/documentation files |
| `libglu1-mesa` | SGI-B-2.0 for library code; its copyright file explicitly opts legacy SGI 1.1 files into version 2.0. Debian packaging has GPL-2.0-or-later notices |
| `libgomp1` | GPL-3.0-or-later **with GCC Runtime Library Exception 3.1**; do not omit the exception when assessing linking obligations |

APT/dpkg and other base-image tools also carry their own licences, including GPL licences. Inspect `/usr/share/doc/<package>/copyright` in the built image and Blender's bundled licence manifests before redistributing that image; this table is not a substitute for their notices or corresponding-source obligations.

### GPL compatibility and findings

- **This is not a GPL-free toolchain.** Blender is GPL, as are several command-line/container tools. Using a GPL program to create independent output does not automatically make that output GPL. Blender's [own documentation](https://docs.blender.org/manual/en/latest/getting_started/about/license.html) explicitly distinguishes the application from the artwork, so using Blender does not by itself require these models, exports or renders to be relicensed.
- **Blender API scripts need separate care.** These scripts import Blender modules directly; they are not merely unrelated executables invoked by a shell. [Apache-2.0 is compatible with GPLv3 in one direction](https://www.apache.org/licenses/GPL-compatibility.html): Apache code can enter a GPLv3 combined work, but GPL code cannot simply be redistributed as Apache-only. The GPL status of Blender-dependent scripts, including separately distributed scripts, needs assessment before redistribution as an Apache-only product; not bundling Blender does not by itself settle this. A Blender-linked add-on or combined application must respect applicable GPL terms. This review does not certify such distribution as Apache-only.
- No incompatible licence was identified among NumPy and the separately installed/declared reader packages; the Blender API caveat above still applies. MIT/BSD/PSF/Apache notices need to be retained when redistributing those dependencies. A package's permissive top-level licence does not replace the notices of its bundled components.
- The repository tracks its own scripts/assets and a Docker recipe, not Blender binaries, the built container or installed reader packages. Redistributing those third-party components requires a separate complete licence/notice and source-availability check. External assets imported through MCP also need their own asset-licence review.
- **Dependency-closure finding, not a licence conflict:** `pip check` reports that pinned python-dateutil 4.0.0 requires `tzdata`, which the current `--no-deps` installation instructions do not install. The rendering tests pass, but the declared Python dependency set is incomplete. `six` is also still pinned despite no longer being required by the current PyCollada/dateutil dependency chain. No dependency versions or installation instructions were changed as part of this review.

This is a technical inventory and compatibility assessment, not legal advice or a redistribution compliance certificate. Recheck it when changing dependency versions or distribution methods.

## License

The repository's original models, exports, renders, scripts and documentation are offered under the [Apache License, Version 2.0](LICENSE). External tools and libraries retain their own licences and obligations, as described above.

"Traxxas" and "Slash" are trademarks of Traxxas, L.P. The models are independent recreations, and the license grants no rights to those trademarks. See section 6 of the license.
