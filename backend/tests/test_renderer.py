import unittest

from pydantic import ValidationError

from app.renderer import (
    AnimationInstruction,
    CameraInstruction,
    RenderLayer,
    RenderPlan,
    RenderPosition,
    RenderSize,
    SceneRenderPlan,
)


class TestRendererModels(unittest.TestCase):

    def test_valid_render_layer(self):
        layer = RenderLayer(
            id="layer_001",
            type="image",
            asset_id="asset_image_background",
            position=RenderPosition(
                x=0,
                y=0,
            ),
            size=RenderSize(
                width=1080,
                height=1920,
            ),
        )

        self.assertEqual(
            layer.type,
            "image",
        )

        self.assertEqual(
            layer.asset_id,
            "asset_image_background",
        )

    def test_valid_animation(self):
        animation = AnimationInstruction(
            type="zoom",
            start=0,
            end=2,
            from_value=1.0,
            to_value=1.2,
        )

        self.assertEqual(
            animation.type,
            "zoom",
        )

        self.assertEqual(
            animation.end,
            2,
        )

    def test_invalid_animation_timing(self):
        with self.assertRaises(ValidationError):
            AnimationInstruction(
                type="fade_in",
                start=2,
                end=1,
            )

    def test_valid_camera(self):
        camera = CameraInstruction(
            type="zoom",
            start=0,
            end=3,
            zoom_from=1.0,
            zoom_to=2.0,
        )

        self.assertEqual(
            camera.type,
            "zoom",
        )

    def test_valid_scene_render_plan(self):
        scene = SceneRenderPlan(
            scene_id="scene_1",
            start=0,
            end=5,
            layers=[
                RenderLayer(
                    id="background",
                    type="background",
                )
            ],
            animations=[
                AnimationInstruction(
                    type="fade_in",
                    start=0,
                    end=1,
                )
            ],
            camera=CameraInstruction(
                type="static"
            ),
        )

        self.assertEqual(
            scene.scene_id,
            "scene_1",
        )

        self.assertEqual(
            len(scene.layers),
            1,
        )

        self.assertEqual(
            len(scene.animations),
            1,
        )

    def test_valid_render_plan(self):
        plan = RenderPlan(
            title="Test Video",
            total_duration=10,
            width=1080,
            height=1920,
            fps=30,
            scenes=[
                SceneRenderPlan(
                    scene_id="scene_1",
                    start=0,
                    end=5,
                ),
                SceneRenderPlan(
                    scene_id="scene_2",
                    start=5,
                    end=10,
                ),
            ],
        )

        self.assertEqual(
            plan.total_duration,
            10,
        )

        self.assertEqual(
            len(plan.scenes),
            2,
        )

    def test_invalid_layer_type(self):
        with self.assertRaises(ValidationError):
            RenderLayer(
                id="layer_001",
                type="video",
            )


if __name__ == "__main__":
    unittest.main()