"""Run with Blender 5.3: blender -b --python-exit-code 1 --python tools/test_render_models.py."""
from pathlib import Path
import sys
import tempfile
import unittest

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import render_models as models

REPO = Path(__file__).resolve().parent.parent


def mesh_counts(meshes):
    counts = {}
    for scene in bpy.data.scenes:
        bpy.context.window.scene = scene
        scene.view_layers[0].update()
        counts[scene.name] = sum(
            item.object.type == "MESH" and item.object.original in meshes
            for item in bpy.context.evaluated_depsgraph_get().object_instances)
    return counts


class RenderModelsTests(unittest.TestCase):
    def test_dae_transform_normals_winding_and_opacity(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        collada = models.collada_module(REPO)
        document = collada.Collada()
        document.assetInfo.unitname = "meter"
        document.assetInfo.unitmeter = 1.0
        document.assetInfo.upaxis = "Z_UP"
        effect = collada.material.Effect(
            "effect", [], "lambert", diffuse=(0.2, 0.3, 0.4, 1),
            transparent=(0, 0, 0, 0.4))
        material = collada.material.Material("material", "material", effect)
        document.effects.append(effect)
        document.materials.append(material)
        vertices = collada.source.FloatSource(
            "vertices", np.array([[0, 0, 0], [1, 0, 0], [0, 1, 1]], dtype=float),
            ("X", "Y", "Z"))
        normals = collada.source.FloatSource(
            "normals", np.array([[0, -1, 1]], dtype=float), ("X", "Y", "Z"))
        geometry = collada.geometry.Geometry(document, "triangle", "triangle", [vertices, normals])
        inputs = collada.source.InputList()
        inputs.addInput(0, "VERTEX", "#vertices")
        inputs.addInput(1, "NORMAL", "#normals")
        geometry.primitives.append(geometry.createTriangleSet(
            np.array([0, 0, 1, 0, 2, 0]), inputs, "binding"))
        document.geometries.append(geometry)
        transform = np.diag([-2., 1., 0.5, 1.])
        transform[:3, 3] = (0.1, 0.2, 0.3)
        node = collada.scene.Node("root", children=[collada.scene.GeometryNode(
            geometry, [collada.scene.MaterialNode("binding", material, inputs=[])])],
            transforms=[collada.scene.MatrixTransform(transform.ravel())])
        scene = collada.scene.Scene("scene", [node])
        document.scenes.append(scene)
        document.scene = scene
        with tempfile.TemporaryDirectory(dir=REPO / "build", prefix="test-dae-") as directory:
            path = Path(directory) / "transformed.dae"
            with path.open("wb") as stream:
                document.write(stream)
            collection = models.load_dae(path, REPO)
        mesh = collection.objects[0].data
        np.testing.assert_allclose(
            [tuple(vertex.co) for vertex in mesh.vertices],
            [[0.1, 0.2, 0.3], [-1.9, 0.2, 0.3], [0.1, 1.2, 0.8]], atol=1e-6)
        self.assertEqual(tuple(mesh.polygons[0].vertices), (0, 2, 1))
        np.testing.assert_allclose(
            mesh.corner_normals[0].vector, [0, -1 / np.sqrt(5), 2 / np.sqrt(5)], atol=1e-4)
        material = mesh.materials[0]
        mix = next(node for node in material.node_tree.nodes if node.type == "MIX_SHADER")
        self.assertAlmostEqual(mix.inputs[0].default_value, 0.4)
        diffuse = next(node for node in material.node_tree.nodes if node.type == "BSDF_DIFFUSE")
        np.testing.assert_allclose(diffuse.inputs["Color"].default_value, (0.2, 0.3, 0.4, 1))

    def test_car_converts_every_instance_without_moving_stage(self):
        bpy.ops.wm.open_mainfile(filepath=str(REPO / "blender/roboracer_car.blend"))
        sources = [bpy.data.collections[name] for name in models.MODELS]
        meshes = {obj for collection in sources for obj in collection.objects if obj.type == "MESH"}
        counts = mesh_counts(meshes)
        instances = {obj.name: obj.matrix_world.copy()
                     for obj in bpy.data.objects if obj.instance_collection in sources}
        stage = {scene.name: (scene.camera, scene.world) for scene in bpy.data.scenes}
        replacements = models.replace_models_with_dae(REPO)
        converted = {obj for collection in replacements.values() for obj in collection.objects}
        self.assertEqual(mesh_counts(converted), counts)
        self.assertEqual(mesh_counts(meshes), {name: 0 for name in counts})
        for name, matrix in instances.items():
            instance = bpy.data.objects[name]
            self.assertIn(instance.instance_collection, replacements.values())
            self.assertEqual(instance.matrix_world, matrix)
        for scene in bpy.data.scenes:
            self.assertEqual((scene.camera, scene.world), stage[scene.name])
        for obj in converted:
            self.assertTrue(obj.get("dae_source"))

    def test_wheel_preserves_excluded_side_and_all_stack_instances(self):
        bpy.ops.wm.open_mainfile(filepath=str(REPO / "blender/traxxas_6873T_wheel.blend"))
        sources = [bpy.data.collections[name] for name in ("Traxxas_6873T_L", "Traxxas_6873T_R")]
        meshes = {obj for collection in sources for obj in collection.objects if obj.type == "MESH"}
        counts = mesh_counts(meshes)
        replacements = models.replace_models_with_dae(REPO)
        converted = {obj for collection in replacements.values() for obj in collection.objects}
        self.assertEqual(mesh_counts(converted), counts)
        self.assertEqual(mesh_counts(meshes), {name: 0 for name in counts})
        layers = models.layer_collections(bpy.data.scenes["Scene"].view_layers[0].layer_collection)
        left = next(layer for layer in layers if layer.collection == replacements[sources[0]])
        self.assertTrue(left.exclude)

    def test_bumpers_are_independent_and_follow_their_axles(self):
        for side, donor in (("Rear", "frame"), ("Front", "front_axle")):
            with self.subTest(side=side):
                bpy.ops.wm.open_mainfile(filepath=str(
                    REPO / "blender" / f"roboracer_{side.lower()}_bumper.blend"))
                name = f"Roboracer_{side}_Bumper"
                collection = bpy.data.collections[name]
                root = bpy.data.objects[name]
                self.assertIsNone(root.parent)
                self.assertEqual(root.matrix_world, Matrix.Identity(4))
                self.assertFalse(bpy.data.libraries)
                meshes = [obj for obj in collection.objects if obj.type == "MESH"]
                self.assertEqual(len(meshes), 1 if side == "Rear" else 2)
                self.assertTrue(all(mesh.parent == root for mesh in meshes))
                if side == "Front":
                    self.assertIn("Front_Bumper_Mount", collection.objects)
                low, high = models.model_bounds(collection)
                self.assertAlmostEqual(low.x if side == "Rear" else high.x, 0.0, places=6)
                self.assertAlmostEqual(low.y + high.y, 0.0, places=6)
                if side == "Front":
                    self.assertAlmostEqual(low.x, -0.1591, places=6)
                bpy.ops.wm.open_mainfile(filepath=str(REPO / "blender" / f"roboracer_{donor}.blend"))
                self.assertFalse(any("Bumper" in obj.name for obj in bpy.data.objects))
                if side == "Front":
                    _, high = models.model_bounds(bpy.data.collections["Roboracer_Front_Axle"])
                    self.assertLess(high.x, 0.04)

        bpy.ops.wm.open_mainfile(filepath=str(REPO / "blender/roboracer_car.blend"))
        root = bpy.data.objects["Roboracer_Car"]
        front = bpy.data.objects["Car_Front_Bumper"]
        rear = bpy.data.objects["Car_Rear_Bumper"]
        self.assertEqual(front.parent, bpy.data.objects["Car_Front_Axle"])
        self.assertEqual(rear.parent, bpy.data.objects["Car_Frame"])
        for instance in (front, rear):
            self.assertIsNotNone(instance.instance_collection.library)
            self.assertEqual(instance.instance_collection.library.filepath,
                             f"//roboracer_{'front' if instance == front else 'rear'}_bumper.blend")
        for wheelbase in (0.28, 0.324, 0.4):
            root["wheelbase"] = wheelbase
            root.update_tag()
            bpy.context.scene.frame_set(bpy.context.scene.frame_current)
            self.assertAlmostEqual(front.matrix_world.translation.x, wheelbase + 0.1671, places=6)
            self.assertAlmostEqual(rear.matrix_world.translation.x, -0.1348, places=6)
            for instance in (front, rear):
                self.assertAlmostEqual(instance.matrix_world.translation.z,
                                       root.matrix_world.translation.z, places=6)

    def test_standalone_parts_frame_both_versions_without_editing_sources(self):
        for stem in models.PARTS:
            with self.subTest(part=stem):
                path = REPO / "blender" / f"{stem}.blend"
                before = path.read_bytes()
                bpy.ops.wm.open_mainfile(filepath=str(path))
                collection = bpy.data.collections[models.PARTS[stem][0]]
                outputs = models.create_part_scenes(REPO)
                self.assertEqual(len(outputs), 2)
                scenes = [bpy.data.scenes[name] for name in outputs]
                self.assertEqual(scenes[0].camera, scenes[1].camera)
                low, high = models.model_bounds(collection)
                instance = next(obj for obj in scenes[0].objects if obj.instance_collection == collection)
                models.replace_models_with_dae(REPO)
                self.assertTrue(instance.instance_collection.get("dae_source"))
                bpy.context.window.scene = scenes[0]
                bpy.context.view_layer.update()
                for x in (low.x, high.x):
                    for y in (low.y, high.y):
                        for z in (low.z, high.z):
                            point = instance.matrix_world @ models.Vector((x, y, z))
                            projected = world_to_camera_view(scenes[0], scenes[0].camera, point)
                            self.assertTrue(0.05 < projected.x < 0.95)
                            self.assertTrue(0.05 < projected.y < 0.95)
                self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    result = unittest.main(argv=[__file__], verbosity=2, exit=False).result
    if not result.wasSuccessful():
        raise SystemExit(1)
