import tempfile
import unittest
from pathlib import Path

from app.asset_manifest import resolve_asset_manifest
from app.models import ScenePlan


class TestAssetResolution(unittest.TestCase):

    def make_plan(self):
        return ScenePlan(
            title="Test",
            summary="Test",
            total_duration=10,
            aspect_ratio="9:16",
            style="documentary",
            scenes=[
                {
                    "id": "scene_1",
                    "start": 0,
                    "end": 5,
                    "title": "Opening",
                    "narration": "Opening",
                    "visual": "Map",
                    "animation": "Fade",
                    "camera": "Wide",
                    "caption": "Opening",
                    "location": "South Asia",
                    "asset_hints": [
                        "map",
                        "mountains",
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
            ],
        )

    def test_existing_assets_are_resolved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            map_dir = root / "map"
            map_dir.mkdir()

            (map_dir / "map.svg").write_text(
                "<svg></svg>",
                encoding="utf-8",
            )

            plan = self.make_plan()

            resolved, missing, placeholders = resolve_asset_manifest(
                plan,
                str(root),
            )

            self.assertEqual(len(resolved), 1)
            self.assertEqual(
                resolved[0].name,
                "map",
            )
            self.assertEqual(len(missing), 2)
            self.assertEqual(len(placeholders), 2)

    def test_missing_assets_are_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = self.make_plan()

            resolved, missing, placeholders = resolve_asset_manifest(
                plan,
                str(temp_dir),
            )

            self.assertEqual(len(resolved), 0)
            self.assertEqual(len(missing), 3)
            self.assertEqual(len(placeholders), 3)

            missing_names = {
                item.name
                for item in missing
            }

            self.assertEqual(
                missing_names,
                {
                    "map",
                    "mountains",
                    "rivers",
                },
            )

    def test_missing_assets_get_placeholders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = self.make_plan()

            resolved, missing, placeholders = (
                resolve_asset_manifest(
                    plan,
                    str(temp_dir),
                )
            )

            self.assertEqual(len(resolved), 0)
            self.assertEqual(len(missing), 3)
            self.assertEqual(len(placeholders), 3)

            self.assertTrue(
                all(
                    asset.status == "placeholder"
                    for asset in placeholders
                )
            )

            self.assertTrue(
                all(
                    asset.source == "placeholder"
                    for asset in placeholders
                )
            )


if __name__ == "__main__":
    unittest.main()