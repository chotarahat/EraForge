import tempfile
import unittest
from pathlib import Path

from app.models import ScenePlan
from app.render_pipeline import render_preview_bundle
from app.renderer_planner import build_render_plan


class TestRenderPipeline(unittest.TestCase):

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
                    "title": "Opening",
                    "narration": "Opening",
                    "visual": "A map of Bangladesh",
                    "animation": "Zoom",
                    "camera": "Zoom in",
                    "caption": "Opening",
                    "location": "Bangladesh",
                    "asset_hints": ["map"],
                },
                {
                    "id": "scene_2",
                    "start": 5,
                    "end": 10,
                    "title": "Rivers",
                    "narration": "Rivers",
                    "visual": "Rivers",
                    "animation": "Fade in",
                    "camera": "Static",
                    "caption": "Rivers",
                    "location": "Bangladesh",
                    "asset_hints": ["rivers"],
                },
            ],
        )

    def test_preview_bundle_creates_scene_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = self.make_plan()
            render_plan = build_render_plan(plan)

            result = render_preview_bundle(
                render_plan,
                temp_dir,
            )

            self.assertEqual(
                len(result.scene_files),
                2,
            )

            for file_path in result.scene_files:
                path = Path(file_path)

                self.assertTrue(
                    path.exists()
                )

                self.assertEqual(
                    path.suffix,
                    ".svg",
                )

                content = path.read_text(
                    encoding="utf-8"
                )

                self.assertIn(
                    "<svg",
                    content,
                )

    def test_output_directory_is_created(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = (
                Path(temp_dir)
                / "nested"
                / "preview"
            )

            plan = self.make_plan()
            render_plan = build_render_plan(plan)

            result = render_preview_bundle(
                render_plan,
                str(output_dir),
            )

            self.assertTrue(
                Path(result.output_dir).exists()
            )


if __name__ == "__main__":
    unittest.main()