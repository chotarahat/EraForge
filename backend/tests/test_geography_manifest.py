import unittest

from app.geography_manifest import build_geography_manifest
from app.models import ScenePlan


class TestGeographyManifest(unittest.TestCase):

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
                    "animation": "Zoom",
                    "camera": "Wide",
                    "caption": "Bangladesh",
                    "location": "Bangladesh",
                    "asset_hints": ["map"],
                },
                {
                    "id": "scene_2",
                    "start": 5,
                    "end": 10,
                    "title": "Character",
                    "narration": "Character",
                    "visual": "A historical portrait",
                    "animation": "Fade",
                    "camera": "Close",
                    "caption": "Character",
                    "location": "Unknown",
                    "asset_hints": [
                        "character",
                        "illustration",
                    ],
                },
            ],
        )

    def test_manifest_contains_all_scenes(self):
        plan = self.make_plan()

        manifest = build_geography_manifest(plan)

        self.assertEqual(
            set(manifest.keys()),
            {
                "scene_1",
                "scene_2",
            },
        )

    def test_geographic_scene_is_enabled(self):
        plan = self.make_plan()

        manifest = build_geography_manifest(plan)

        self.assertTrue(
            manifest["scene_1"].enabled
        )

        self.assertEqual(
            manifest["scene_1"].regions[0].id,
            "bangladesh",
        )

    def test_non_geographic_scene_is_disabled(self):
        plan = self.make_plan()

        manifest = build_geography_manifest(plan)

        self.assertFalse(
            manifest["scene_2"].enabled
        )

        self.assertEqual(
            len(manifest["scene_2"].regions),
            0,
        )

    def test_operations_are_preserved(self):
        plan = self.make_plan()

        manifest = build_geography_manifest(plan)

        operations = (
            manifest["scene_1"].operations
        )

        self.assertEqual(
            len(operations),
            2,
        )

        self.assertEqual(
            operations[0].type,
            "show_region",
        )

        self.assertEqual(
            operations[1].type,
            "zoom",
        )


if __name__ == "__main__":
    unittest.main()