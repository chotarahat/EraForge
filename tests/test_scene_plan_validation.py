import unittest

from pydantic import ValidationError

from backend.app.models import ScenePlan


def make_scene(scene_id, start, end):
    return {
        "id": scene_id,
        "start": start,
        "end": end,
        "title": f"Scene {scene_id}",
        "narration": "Narration",
        "visual": "Visual",
        "animation": "Animation",
        "camera": "Camera",
        "caption": "Caption",
        "location": None,
        "asset_hints": [],
    }


def make_plan(scenes, duration):
    return {
        "title": "Test",
        "summary": "Test plan",
        "total_duration": duration,
        "aspect_ratio": "9:16",
        "style": "animated historical documentary",
        "scenes": scenes,
    }


class ScenePlanValidationTests(unittest.TestCase):
    def test_valid_timeline(self):
        plan = ScenePlan.model_validate(
            make_plan(
                [
                    make_scene("1", 0, 5),
                    make_scene("2", 5, 10),
                ],
                10,
            )
        )

        self.assertEqual(plan.total_duration, 10)

    def test_gap_is_rejected(self):
        with self.assertRaises(ValidationError):
            ScenePlan.model_validate(
                make_plan(
                    [
                        make_scene("1", 0, 5),
                        make_scene("2", 6, 10),
                    ],
                    10,
                )
            )

    def test_overlap_is_rejected(self):
        with self.assertRaises(ValidationError):
            ScenePlan.model_validate(
                make_plan(
                    [
                        make_scene("1", 0, 6),
                        make_scene("2", 5, 10),
                    ],
                    10,
                )
            )

    def test_wrong_final_duration_is_rejected(self):
        with self.assertRaises(ValidationError):
            ScenePlan.model_validate(
                make_plan(
                    [
                        make_scene("1", 0, 4),
                        make_scene("2", 4, 9),
                    ],
                    10,
                )
            )

    def test_negative_start_is_rejected(self):
        with self.assertRaises(ValidationError):
            ScenePlan.model_validate(
                make_plan(
                    [
                        make_scene("1", -1, 5),
                    ],
                    5,
                )
            )


if __name__ == "__main__":
    unittest.main()