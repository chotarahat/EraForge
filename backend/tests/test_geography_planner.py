import unittest

from app.geography_planner import (
    build_geography_plan,
    find_geography_matches,
)
from app.models import Scene


def make_scene(
    title="Test Scene",
    visual="A map of Bangladesh",
    animation="Fade",
    camera="Wide",
    location="Bangladesh",
    asset_hints=None,
):
    return Scene(
        id="scene_1",
        start=0,
        end=5,
        title=title,
        narration="Test narration",
        visual=visual,
        animation=animation,
        camera=camera,
        caption="Test",
        location=location,
        asset_hints=asset_hints or [],
    )


class TestGeographyPlanner(unittest.TestCase):

    def test_bangladesh_is_detected(self):
        scene = make_scene()

        matches = find_geography_matches(scene)

        ids = {
            item["id"]
            for item in matches
        }

        self.assertIn(
            "bangladesh",
            ids,
        )

    def test_multiple_geographies_are_detected(self):
        scene = make_scene(
            visual=(
                "Map of the Himalayas and "
                "Bay of Bengal"
            ),
            location="South Asia",
            asset_hints=[
                "map",
                "himalayas",
                "bay of bengal",
            ],
        )

        matches = find_geography_matches(scene)

        ids = {
            item["id"]
            for item in matches
        }

        self.assertIn(
            "himalayas",
            ids,
        )

        self.assertIn(
            "bay_of_bengal",
            ids,
        )

    def test_duplicate_matches_are_removed(self):
        scene = make_scene(
            visual="Bangladesh map",
            location="Bangladesh",
            asset_hints=[
                "Bangladesh",
                "map",
            ],
        )

        matches = find_geography_matches(scene)

        ids = [
            item["id"]
            for item in matches
        ]

        self.assertEqual(
            ids.count("bangladesh"),
            1,
        )

    def test_map_hint_enables_geography(self):
        scene = make_scene(
            visual="Ancient landscape",
            location="Unknown",
            asset_hints=["map"],
        )

        plan = build_geography_plan(scene)

        self.assertTrue(plan.enabled)
        self.assertEqual(
            plan.map_source,
            "local",
        )

    def test_geography_plan_contains_region_and_operation(self):
        scene = make_scene()

        plan = build_geography_plan(scene)

        self.assertTrue(plan.enabled)
        self.assertEqual(
            len(plan.regions),
            1,
        )
        self.assertEqual(
            plan.regions[0].id,
            "bangladesh",
        )
        self.assertEqual(
            len(plan.operations),
            1,
        )
        self.assertEqual(
            plan.operations[0].type,
            "show_region",
        )

    def test_highlight_operation_is_detected(self):
        scene = make_scene(
            visual="Map of Bangladesh",
            asset_hints=[
                "map",
                "highlight",
            ],
        )

        plan = build_geography_plan(scene)

        operation_types = [
            operation.type
            for operation in plan.operations
        ]

        self.assertIn(
            "highlight_region",
            operation_types,
        )

    def test_zoom_operation_is_detected(self):
        scene = make_scene(
            visual="Zoom into Bangladesh on the map",
            asset_hints=[
                "map",
            ],
        )

        plan = build_geography_plan(scene)

        operation_types = [
            operation.type
            for operation in plan.operations
        ]

        self.assertIn(
            "zoom",
            operation_types,
        )

    def test_pan_operation_is_detected(self):
        scene = make_scene(
            visual="Map of South Asia",
            animation="Pan right across the map",
            camera="Pan right",
            asset_hints=[
                "map",
            ],
        )

        plan = build_geography_plan(scene)

        operation_types = [
            operation.type
            for operation in plan.operations
        ]

        self.assertIn(
            "pan",
            operation_types,
        )

    def test_marker_operation_is_detected(self):
        scene = make_scene(
            visual="Map with a location marker",
            asset_hints=[
                "map",
            ],
        )

        plan = build_geography_plan(scene)

        operation_types = [
            operation.type
            for operation in plan.operations
        ]

        self.assertIn(
            "place_marker",
            operation_types,
        )

    def test_non_geographic_scene_is_disabled(self):
        scene = make_scene(
            visual="A portrait of an ancient ruler",
            location="Unknown",
            asset_hints=[
                "character",
                "illustration",
            ],
        )

        plan = build_geography_plan(scene)

        self.assertFalse(plan.enabled)
        self.assertEqual(
            len(plan.regions),
            0,
        )
        self.assertEqual(
            len(plan.operations),
            0,
        )


if __name__ == "__main__":
    unittest.main()