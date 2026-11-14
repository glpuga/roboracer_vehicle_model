"""Temporary model/stage preparation for native and exported-DAE renders."""
from pathlib import Path
import sys

import bpy
from mathutils import Vector
import numpy as np

MODELS = {
    "Traxxas_6873T_L": "traxxas_6873T_wheel_L",
    "Traxxas_6873T_R": "traxxas_6873T_wheel_R",
    "Roboracer_Frame": "roboracer_frame",
    "Roboracer_Front_Axle": "roboracer_front_axle",
    "Roboracer_Center_Of_Mass": "roboracer_center_of_mass",
}
PARTS = {
    "roboracer_frame": ("Roboracer_Frame", "Frame"),
    "roboracer_front_axle": ("Roboracer_Front_Axle", "Front_Axle"),
    "roboracer_center_of_mass": ("Roboracer_Center_Of_Mass", "COM_Marker"),
}
LAYER_FLAGS = ("exclude", "holdout", "indirect_only", "hide_viewport")


def collada_module(repo_dir):
    dependencies = str(Path(repo_dir) / "build" / "render_deps")
    if dependencies not in sys.path:
        sys.path.insert(0, dependencies)
    try:
        import collada
    except ModuleNotFoundError as error:
        raise SystemExit(
            f"[render] Missing DAE dependency {error.name!r}. Install "
            "tools/requirements-render.txt into build/render_deps; see AGENTS.md."
        ) from error
    return collada


def dae_material(effect):
    if effect.shadingtype != "lambert" or not isinstance(effect.diffuse, tuple):
        raise ValueError(f"{effect.id}: expected an untextured DAE Lambert material")
    if effect.opaque_mode != "A_ONE":
        raise ValueError(f"{effect.id}: unsupported DAE opacity mode {effect.opaque_mode!r}")
    opacity = effect.transparent[3] * effect.transparency if effect.transparent is not None else 1.0
    if not 0.0 <= opacity <= 1.0:
        raise ValueError(f"{effect.id}: invalid opacity {opacity}")
    material = bpy.data.materials.new(f"DAE_{effect.id}")
    material.diffuse_color = (*effect.diffuse[:3], opacity)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    diffuse = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse.inputs["Color"].default_value = effect.diffuse
    diffuse.inputs["Roughness"].default_value = 0.0
    surface = diffuse.outputs["BSDF"]
    if effect.emission is not None and any(effect.emission[:3]):
        emission = nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value = effect.emission
        add = nodes.new("ShaderNodeAddShader")
        links.new(surface, add.inputs[0])
        links.new(emission.outputs[0], add.inputs[1])
        surface = add.outputs[0]
    if opacity < 1.0:
        transparent = nodes.new("ShaderNodeBsdfTransparent")
        mix = nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = opacity
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(surface, mix.inputs[2])
        surface = mix.outputs[0]
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(surface, output.inputs["Surface"])
    return material


def load_dae(path, repo_dir):
    """Read our triangulated exports, baking scene transforms but not source shaders."""
    collada = collada_module(repo_dir)
    document = collada.Collada(str(path))
    if document.assetInfo.unitmeter != 1.0 or document.assetInfo.upaxis != "Z_UP":
        raise ValueError(f"{path}: expected metres and Z up")
    if document.scene is None or document.images:
        raise ValueError(f"{path}: expected an untextured DAE scene")
    collection = bpy.data.collections.new(f"DAE_{path.stem}")
    collection["dae_source"] = str(path)
    materials = {}
    for geometry in document.scene.objects("geometry"):
        primitives = list(geometry.primitives())
        if not primitives or any(not isinstance(p, collada.triangleset.BoundTriangleSet)
                                 for p in primitives):
            raise ValueError(f"{path}: {geometry.original.id} is not triangulated")
        vertices = primitives[0].vertex
        if any(not np.array_equal(p.vertex, vertices) for p in primitives):
            raise ValueError(f"{path}: inconsistent position sources in {geometry.original.id}")
        linear = geometry.matrix[:3, :3]
        order = [0, 2, 1] if np.linalg.det(linear) < 0 else [0, 1, 2]
        faces, normals, uv, indices, slots = [], [], [], [], []
        for index, primitive in enumerate(primitives):
            if primitive.material is None or primitive.original.normal is None:
                raise ValueError(f"{path}: missing material or normals in {geometry.original.id}")
            faces.extend(primitive.vertex_index[:, order].tolist())
            transformed = primitive.original.normal[primitive.normal_index[:, order]]
            transformed = transformed @ np.linalg.inv(linear)
            lengths = np.linalg.norm(transformed, axis=2, keepdims=True)
            if np.any(lengths == 0):
                raise ValueError(f"{path}: zero-length normals in {geometry.original.id}")
            normals.extend((transformed / lengths).reshape(-1, 3).tolist())
            if primitive.texcoordset:
                uv.extend(primitive.texcoordset[0][
                    primitive.texcoord_indexset[0][:, order]].reshape(-1, 2).tolist())
            effect = primitive.material.effect
            if effect.id not in materials:
                materials[effect.id] = dae_material(effect)
            slots.append(materials[effect.id])
            indices.extend([index] * len(primitive))
        mesh = bpy.data.meshes.new(f"DAE_{geometry.original.id}")
        mesh.from_pydata(vertices.tolist(), [], faces)
        mesh.update()
        for material in slots:
            mesh.materials.append(material)
        for polygon, index in zip(mesh.polygons, indices):
            polygon.material_index = index
            polygon.use_smooth = True
        mesh.normals_split_custom_set(normals)
        if uv:
            if len(uv) != len(mesh.loops):
                raise ValueError(f"{path}: incomplete UV coordinates in {geometry.original.id}")
            mesh.uv_layers.new(name="UVMap").data.foreach_set("uv", np.asarray(uv).ravel())
        obj = bpy.data.objects.new(mesh.name, mesh)
        obj["dae_source"] = str(path)
        collection.objects.link(obj)
    if not collection.objects:
        raise ValueError(f"{path}: no mesh geometry")
    print(f"[render] DAE {path.name}: {len(collection.objects)} meshes, "
          f"{len(materials)} exported Lambert materials")
    return collection


def layer_collections(layer):
    yield layer
    for child in layer.children:
        yield from layer_collections(child)


def replace_models_with_dae(repo_dir):
    sources = {collection: Path(repo_dir) / "dae" / f"{stem}.dae"
               for name, stem in MODELS.items()
               if (collection := bpy.data.collections.get(name)) is not None}
    if not sources:
        raise ValueError("[render] No known model collections to convert")
    states = {}
    for scene in bpy.data.scenes:
        for view_layer in scene.view_layers:
            view_layer.update()
            for layer in layer_collections(view_layer.layer_collection):
                if layer.collection in sources:
                    key = (scene, view_layer.name, layer.collection)
                    states.setdefault(key, []).append(
                        tuple(getattr(layer, flag) for flag in LAYER_FLAGS))
    replacements = {}
    for source, path in sources.items():
        converted = load_dae(path, repo_dir)
        converted.instance_offset = source.instance_offset
        converted.hide_render = source.hide_render
        replacements[source] = converted
    for obj in bpy.data.objects:
        if obj.instance_collection in replacements:
            obj.instance_collection = replacements[obj.instance_collection]
    parents = list(bpy.data.collections) + [scene.collection for scene in bpy.data.scenes]
    for parent in parents:
        for source, converted in replacements.items():
            if source.name in parent.children:
                parent.children.link(converted)
                parent.children.unlink(source)
    for (scene, name, source), flags in states.items():
        scene.view_layers[name].update()
        layers = [layer for layer in layer_collections(scene.view_layers[name].layer_collection)
                  if layer.collection == replacements[source]]
        if len(layers) != len(flags):
            raise ValueError(f"[render] Lost collection visibility for {scene.name}/{source.name}")
        for layer, values in zip(layers, flags):
            for flag, value in zip(LAYER_FLAGS, values):
                setattr(layer, flag, value)
    return replacements


def model_bounds(collection):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = [obj.matrix_world @ Vector(corner)
              for obj in collection.all_objects if obj.type == "MESH"
              for corner in obj.evaluated_get(depsgraph).bound_box]
    if not points:
        raise ValueError(f"{collection.name}: no mesh bounds")
    return (Vector(tuple(min(point[i] for point in points) for i in range(3))),
            Vector(tuple(max(point[i] for point in points) for i in range(3))))


def create_part_scenes(repo_dir):
    """Borrow the car's stage, fitting copies to a part without saving any .blend."""
    stem = Path(bpy.data.filepath).stem
    if stem not in PARTS:
        return {}
    collection_name, scene_name = PARTS[stem]
    model = bpy.data.collections[collection_name]
    low, high = model_bounds(model)
    dimensions = high - low
    target = Vector((0, 0, dimensions.z / 2))
    offset = Vector((-(low.x + high.x) / 2, -(low.y + high.y) / 2, -low.z))
    with bpy.data.libraries.load(str(Path(repo_dir) / "blender/roboracer_car.blend"),
                                 link=True) as (_, loaded):
        loaded.collections = ["Render_Stage", "Ground_Studio", "Ground_Checker"]
        loaded.worlds = ["World", "World_Checker"]
    stage, studio, checker = loaded.collections
    render_stage = bpy.data.collections.new("Part_Render_Stage")
    copies = {}
    reference_target = next(obj for obj in stage.objects if obj.type == "EMPTY")
    scale = max(dimensions) / 0.6259
    for original in stage.objects:
        obj = original.copy()
        if original.data is not None:
            obj.data = original.data.copy()
        obj.location = target + (original.location - reference_target.location) * scale
        if obj.type == "LIGHT":
            obj.data.energy *= scale * scale
            obj.data.size *= scale
        render_stage.objects.link(obj)
        copies[original] = obj
    for obj in copies.values():
        for constraint in obj.constraints:
            if getattr(constraint, "target", None) in copies:
                constraint.target = copies[constraint.target]
    original_camera = next(obj for obj in stage.objects if obj.type == "CAMERA")
    camera = copies[original_camera]
    camera.constraints.clear()
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = (target - camera.location).to_track_quat("-Z", "Y")
    camera.data.type = "ORTHO"
    camera.data.clip_start *= scale
    camera.data.clip_end *= scale
    inverse_rotation = camera.rotation_quaternion.inverted()
    corners = [Vector((x, y, z)) + offset for x in (low.x, high.x)
               for y in (low.y, high.y) for z in (low.z, high.z)]
    projected = [inverse_rotation @ (point - target) for point in corners]
    width = max(p.x for p in projected) - min(p.x for p in projected)
    height = max(p.y for p in projected) - min(p.y for p in projected)
    camera.data.ortho_scale = max(width, height * 1.6) * 1.3
    instance = bpy.data.objects.new(f"Part_{collection_name}", None)
    instance.instance_type = "COLLECTION"
    instance.instance_collection = model
    instance.location = offset
    model_collection = bpy.data.collections.new("Part_Model")
    model_collection.objects.link(instance)
    outputs = {}
    for suffix, floor, world in [("", studio, loaded.worlds[0]),
                                 ("_Checker", checker, loaded.worlds[1])]:
        scene = bpy.data.scenes.new(scene_name + suffix)
        for child in (model_collection, render_stage, floor):
            scene.collection.children.link(child)
        scene.camera = camera
        scene.world = world
        scene.unit_settings.system = "METRIC"
        scene.unit_settings.scale_length = 1.0
        scene.render.resolution_x = 1600
        scene.render.resolution_y = 1000
        scene.cycles.samples = 128
        scene.cycles.use_denoising = True
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        outputs[scene.name] = stem + ("_checker_render" if suffix else "_render")
    return outputs
