import unittest

from app.asset_planner import (
    build_asset_requirements,
    infer_asset_type,
)
from app.models import Scene


def make_scene(asset_hints):
    return Scene(
        id="scene_1",
        start=0,
        end=5,
        title="Test Scene",
        narration="Test narration",
        visual="Test visual",
        animation="Fade in",
        camera="Wide shot",
        caption="Test caption",
        location="Test location",
        asset_hints=asset_hints,
    )


class TestAssetPlanner(unittest.TestCase):

    def test_map_type(self):
        self.assertEqual(
            infer_asset_type("map"),
            "map",
        )

    def test_landscape_type(self):
        self.assertEqual(
            infer_asset_type("landscape"),
            "background",
        )

    def test_unknown_defaults_to_illustration(self):
        self.assertEqual(
            infer_asset_type("sediment"),
            "illustration",
        )

    def test_build_requirements(self):
        scene = make_scene(
            [
                "mountains",
                "rivers",
                "map",
            ]
        )

        requirements = build_asset_requirements(scene)

        self.assertEqual(len(requirements), 3)
        self.assertEqual(requirements[0].name, "mountains")
        self.assertEqual(requirements[0].type, "illustration")
        self.assertEqual(requirements[1].name, "rivers")
        self.assertEqual(requirements[2].type, "map")

    def test_duplicate_hints_are_removed(self):
        scene = make_scene(
            [
                "map",
                "map",
                "MAP",
            ]
        )

        requirements = build_asset_requirements(scene)

        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].type, "map")


if __name__ == "__main__":
    unittest.main()