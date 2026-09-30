import unittest

from app.renderer import (
    RenderLayer,
    SceneRenderPlan,
)
from app.scene_renderer import render_scene_to_svg


class TestSceneRenderer(unittest.TestCase):

    def make_scene(self):
        return SceneRenderPlan(
            scene_id="scene_1",
            start=0,
            end=5,
            layers=[
                RenderLayer(
                    id="background",
                    type="background",
                ),
                RenderLayer(
                    id="map",
                    type="map",
                    metadata={
                        "asset_hint": "map",
                    },
                ),
                RenderLayer(
                    id="caption",
                    type="text",
                    text="Bangladesh",
                ),
            ],
        )

    def test_svg_is_generated(self):
        scene = self.make_scene()

        svg = render_scene_to_svg(scene)

        self.assertIn(
            "<svg",
            svg,
        )

        self.assertIn(
            "</svg>",
            svg,
        )

    def test_background_is_rendered(self):
        scene = self.make_scene()

        svg = render_scene_to_svg(scene)

        self.assertIn(
            'fill="#0a0d11"',
            svg,
        )

    def test_text_layer_is_rendered(self):
        scene = self.make_scene()

        svg = render_scene_to_svg(scene)

        self.assertIn(
            "Bangladesh",
            svg,
        )

    def test_asset_placeholder_is_rendered(self):
        scene = self.make_scene()

        svg = render_scene_to_svg(scene)

        self.assertIn(
            "map",
            svg,
        )

    def test_fade_in_animation_is_rendered(self):
        from app.renderer import AnimationInstruction, SceneRenderPlan

        scene = SceneRenderPlan(
            scene_id="scene_1",
            start=0,
            end=5,
            layers=[
                {
                    "id": "background",
                    "type": "background",
                },
                {
                    "id": "visual_1",
                    "type": "image",
                    "asset_id": "asset_map_map",
                },
            ],
            animations=[
                AnimationInstruction(
                    type="fade_in",
                    start=0,
                    end=2,
                )
            ],
        )

        svg = render_scene_to_svg(scene)

        assert '<animate attributeName="opacity"' in svg
        assert 'from="0"' in svg
        assert 'to="1"' in svg

    def test_slide_animation_is_rendered(self):
        from app.renderer import AnimationInstruction, SceneRenderPlan

        scene = SceneRenderPlan(
            scene_id="scene_2",
            start=0,
            end=5,
            layers=[
                {
                    "id": "background",
                    "type": "background",
                },
                {
                    "id": "visual_2",
                    "type": "image",
                    "asset_id": "asset_map_map",
                },
            ],
            animations=[
                AnimationInstruction(
                    type="slide",
                    start=0,
                    end=1.5,
                    direction="left",
                )
            ],
        )

        svg = render_scene_to_svg(scene)

        assert '<animateTransform' in svg
        assert 'type="translate"' in svg

    def test_zoom_camera_animation_is_rendered(self):
        from app.renderer import CameraInstruction, SceneRenderPlan

        scene = SceneRenderPlan(
            scene_id="scene_3",
            start=0,
            end=5,
            layers=[
                {
                    "id": "background",
                    "type": "background",
                },
                {
                    "id": "visual_3",
                    "type": "image",
                    "asset_id": "asset_map_map",
                },
            ],
            camera=CameraInstruction(
                type="zoom",
                start=0,
                end=3,
                zoom_from=1.0,
                zoom_to=1.25,
            ),
        )

        svg = render_scene_to_svg(scene)

        assert '<animateTransform' in svg
        assert 'type="scale"' in svg
        assert 'from="1.0"' in svg
        assert 'to="1.25"' in svg


if __name__ == "__main__":
    unittest.main()