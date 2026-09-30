import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app.frame_renderer import render_plan_frames
from app.renderer import RenderPlan


def make_render_plan():
    return RenderPlan(
        title="Frame Test",
        total_duration=2,
        width=320,
        height=480,
        fps=2,
        scenes=[
            {
                "scene_id": "scene_1",
                "start": 0,
                "end": 1,
                "layers": [
                    {
                        "id": "background",
                        "type": "background",
                    },
                    {
                        "id": "caption",
                        "type": "text",
                        "text": "Scene One",
                    },
                ],
            },
            {
                "scene_id": "scene_2",
                "start": 1,
                "end": 2,
                "layers": [
                    {
                        "id": "background",
                        "type": "background",
                    },
                    {
                        "id": "visual",
                        "type": "shape",
                    },
                ],
            },
        ],
    )


class TestFrameRenderer(unittest.TestCase):
    def test_frames_are_created(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            files = render_plan_frames(
                make_render_plan(),
                output_root=temp_dir,
            )

            self.assertEqual(
                len(files),
                4,
            )

            for file in files:
                path = Path(file)

                self.assertTrue(
                    path.exists()
                )

                self.assertEqual(
                    path.suffix.lower(),
                    ".png",
                )

    def test_frame_dimensions_are_correct(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            files = render_plan_frames(
                make_render_plan(),
                output_root=temp_dir,
            )

            with Image.open(files[0]) as image:
                self.assertEqual(
                    image.size,
                    (320, 480),
                )

    def test_frame_files_are_sequential(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            files = render_plan_frames(
                make_render_plan(),
                output_root=temp_dir,
            )

            names = [
                Path(file).name
                for file in files
            ]

            self.assertEqual(
                names,
                [
                    "frame_000001.png",
                    "frame_000002.png",
                    "frame_000003.png",
                    "frame_000004.png",
                ],
            )


if __name__ == "__main__":
    unittest.main()