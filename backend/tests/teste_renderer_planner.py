import unittest

from app.models import ScenePlan
from app.renderer_planner import (
    build_render_plan,
    build_scene_render_plan,
    parse_animation_type,
    parse_camera_type,
)


class TestRendererPlanner(unittest.TestCase):

    def make_plan(self):
        return ScenePlan(
            title="Test History",
            summary="Test summary",
            total_duration=10,
            aspect_ratio="9:16",
            style="animated historical documentary",
            scenes=[
                {
                    "id": "scene_1",
                    "start": 0,
                    "end": 5,
                    "title": "Bangladesh",
                    "narration": "Bangladesh",
                    "visual": "A map of Bangladesh",
                    "animation": "Zoom into the map",
                    "camera": "Zoom in",
                    "caption": "Bangladesh",
                    "location": "Bangladesh",
                    "asset_hints": [
                        "map",
                        "background",
                    ],
                },
                {
                    "id": "scene_2",
                    "start": 5,
                    "end": 10,
                    "title": "Character",
                    "narration": "Character",
                    "visual": "Historical portrait",
                    "animation": "Fade in",
                    "camera": "Static shot",
                    "caption": "Character",
                    "location": "Unknown",
                    "asset_hints": [
                        "character",
                    ],
                },
            ],
        )

    def test_animation_parser(self):
        self.assertEqual(
            parse_animation_type(
                "Zoom into the scene"
            ),
            "zoom",
        )

        self.assertEqual(
            parse_animation_type(
                "Fade in slowly"
            ),
            "fade_in",
        )

    def test_camera_parser(self):
        self.assertEqual(
            parse_camera_type("Zoom in"),
            "zoom",
        )

        self.assertEqual(
            parse_camera_type("Pan right"),
            "pan",
        )

        self.assertEqual(
            parse_camera_type("Static shot"),
            "static",
        )

    def test_scene_render_plan(self):
        plan = self.make_plan()

        scene_plan = build_scene_render_plan(
            plan.scenes[0]
        )

        self.assertEqual(
            scene_plan.scene_id,
            "scene_1",
        )

        self.assertGreaterEqual(
            len(scene_plan.layers),
            2,
        )

        self.assertEqual(
            scene_plan.camera.type,
            "zoom",
        )

        self.assertGreaterEqual(
            len(scene_plan.animations),
            1,
        )

    def test_render_plan_uses_vertical_dimensions(self):
        plan = self.make_plan()

        render_plan = build_render_plan(plan)

        self.assertEqual(
            render_plan.width,
            1080,
        )

        self.assertEqual(
            render_plan.height,
            1920,
        )

        self.assertEqual(
            render_plan.fps,
            30,
        )

        self.assertEqual(
            len(render_plan.scenes),
            2,
        )

    def test_render_plan_contains_geography_metadata(self):
        plan = self.make_plan()

        render_plan = build_render_plan(plan)

        scene = render_plan.scenes[0]

        self.assertIn(
            "geography",
            scene.metadata,
        )

        self.assertTrue(
            scene.metadata["geography"]["enabled"]
        )


if __name__ == "__main__":
    unittest.main()