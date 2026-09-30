import unittest

from app.asset_manifest import build_asset_manifest
from app.models import ScenePlan


def make_plan():
    return ScenePlan(
        title="Test History",
        summary="Test summary",
        total_duration=15,
        aspect_ratio="9:16",
        style="animated historical documentary",
        scenes=[
            {
                "id": "scene_1",
                "start": 0,
                "end": 5,
                "title": "Mountains",
                "narration": "Mountains",
                "visual": "Mountains",
                "animation": "Pan",
                "camera": "Wide",
                "caption": "Mountains",
                "location": "Himalayas",
                "asset_hints": [
                    "map",
                    "Himalayas",
                ],
            },
            {
                "id": "scene_2",
                "start": 5,
                "end": 10,
                "title": "Rivers",
                "narration": "Rivers",
                "visual": "Rivers",
                "animation": "Pan",
                "camera": "Wide",
                "caption": "Rivers",
                "location": "South Asia",
                "asset_hints": [
                    "map",
                    "rivers",
                ],
            },
            {
                "id": "scene_3",
                "start": 10,
                "end": 15,
                "title": "Delta",
                "narration": "Delta",
                "visual": "Delta",
                "animation": "Zoom",
                "camera": "Wide",
                "caption": "Delta",
                "location": "Bay of Bengal",
                "asset_hints": [
                    "rivers",
                    "delta",
                ],
            },
        ],
    )


class TestAssetManifest(unittest.TestCase):

    def test_assets_are_deduplicated(self):
        plan = make_plan()

        manifest = build_asset_manifest(plan)

        names = [asset.name for asset in manifest]

        self.assertEqual(
            names.count("map"),
            1,
        )

        self.assertEqual(
            names.count("rivers"),
            1,
        )

    def test_asset_ids_are_deterministic(self):
        plan = make_plan()

        manifest_one = build_asset_manifest(plan)
        manifest_two = build_asset_manifest(plan)

        ids_one = [asset.id for asset in manifest_one]
        ids_two = [asset.id for asset in manifest_two]

        self.assertEqual(ids_one, ids_two)

        map_asset = next(
            asset
            for asset in manifest_one
            if asset.name == "map"
        )

        self.assertEqual(
            map_asset.id,
            "asset_map_map",
        )

    def test_scene_relationships_are_preserved(self):
        plan = make_plan()

        manifest = build_asset_manifest(plan)

        map_asset = next(
            asset
            for asset in manifest
            if asset.name == "map"
        )

        self.assertEqual(
            map_asset.metadata["scene_ids"],
            ["scene_1", "scene_2"],
        )

        rivers_asset = next(
            asset
            for asset in manifest
            if asset.name == "rivers"
        )

        self.assertEqual(
            rivers_asset.metadata["scene_ids"],
            ["scene_2", "scene_3"],
        )


if __name__ == "__main__":
    unittest.main()