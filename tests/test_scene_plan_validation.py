import sys
from pathlib import Path
import unittest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "backend"),
)

from app.models import ScenePlan


class ScenePlanValidationTests(unittest.TestCase):
    def test_valid_timeline(self):
        plan = ScenePlan(
            title="Test",
            summary="Test summary",
            total_duration=8,
            aspect_ratio="9:16",
            style="documentary",
            scenes=[
                {
                    "id": "scene_1",
                    "title": "Opening",
                    "start": 0,
                    "end": 4,
                    "narration": "Opening",
                    "caption": "Opening",
                    "visual": "Background",
                    "animation": "Fade in",
                    "camera": "Static",
                    "location": "",
                    "asset_hints": [],
                },
                {
                    "id": "scene_2",
                    "title": "Second",
                    "start": 4,
                    "end": 8,
                    "narration": "Second",
                    "caption": "Second",
                    "visual": "Background",
                    "animation": "Fade in",
                    "camera": "Static",
                    "location": "",
                    "asset_hints": [],
                },
            ],
        )

        self.assertEqual(plan.total_duration, 8)

    def test_negative_start_is_rejected(self):
        with self.assertRaises(Exception):
            ScenePlan(
                title="Test",
                summary="Test summary",
                total_duration=4,
                aspect_ratio="9:16",
                style="documentary",
                scenes=[
                    {
                        "id": "scene_1",
                        "title": "Opening",
                        "start": -1,
                        "end": 4,
                        "narration": "Opening",
                        "caption": "Opening",
                        "visual": "Background",
                        "animation": "Fade in",
                        "camera": "Static",
                        "location": "",
                        "asset_hints": [],
                    }
                ],
            )

    def test_overlap_is_rejected(self):
        with self.assertRaises(Exception):
            ScenePlan(
                title="Test",
                summary="Test summary",
                total_duration=8,
                aspect_ratio="9:16",
                style="documentary",
                scenes=[
                    {
                        "id": "scene_1",
                        "title": "Opening",
                        "start": 0,
                        "end": 5,
                        "narration": "Opening",
                        "caption": "Opening",
                        "visual": "Background",
                        "animation": "Fade in",
                        "camera": "Static",
                        "location": "",
                        "asset_hints": [],
                    },
                    {
                        "id": "scene_2",
                        "title": "Second",
                        "start": 4,
                        "end": 8,
                        "narration": "Second",
                        "caption": "Second",
                        "visual": "Background",
                        "animation": "Fade in",
                        "camera": "Static",
                        "location": "",
                        "asset_hints": [],
                    },
                ],
            )

    def test_gap_is_rejected(self):
        with self.assertRaises(Exception):
            ScenePlan(
                title="Test",
                summary="Test summary",
                total_duration=9,
                aspect_ratio="9:16",
                style="documentary",
                scenes=[
                    {
                        "id": "scene_1",
                        "title": "Opening",
                        "start": 0,
                        "end": 4,
                        "narration": "Opening",
                        "caption": "Opening",
                        "visual": "Background",
                        "animation": "Fade in",
                        "camera": "Static",
                        "location": "",
                        "asset_hints": [],
                    },
                    {
                        "id": "scene_2",
                        "title": "Second",
                        "start": 5,
                        "end": 9,
                        "narration": "Second",
                        "caption": "Second",
                        "visual": "Background",
                        "animation": "Fade in",
                        "camera": "Static",
                        "location": "",
                        "asset_hints": [],
                    },
                ],
            )

    def test_wrong_final_duration_is_rejected(self):
        with self.assertRaises(Exception):
            ScenePlan(
                title="Test",
                summary="Test summary",
                total_duration=10,
                aspect_ratio="9:16",
                style="documentary",
                scenes=[
                    {
                        "id": "scene_1",
                        "title": "Opening",
                        "start": 0,
                        "end": 4,
                        "narration": "Opening",
                        "caption": "Opening",
                        "visual": "Background",
                        "animation": "Fade in",
                        "camera": "Static",
                        "location": "",
                        "asset_hints": [],
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()