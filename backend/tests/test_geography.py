import unittest

from pydantic import ValidationError

from app.geography import (
    GeoMarker,
    GeoOperation,
    GeoPoint,
    GeoRegion,
    GeoRoute,
    GeographyPlan,
)


class TestGeographyModels(unittest.TestCase):

    def test_valid_geo_point(self):
        point = GeoPoint(
            latitude=23.8103,
            longitude=90.4125,
        )

        self.assertEqual(point.latitude, 23.8103)
        self.assertEqual(point.longitude, 90.4125)

    def test_invalid_geo_point(self):
        with self.assertRaises(ValidationError):
            GeoPoint(
                latitude=100,
                longitude=0,
            )

    def test_valid_route(self):
        route = GeoRoute(
            id="route_001",
            name="River Route",
            points=[
                GeoPoint(
                    latitude=23.8,
                    longitude=90.4,
                ),
                GeoPoint(
                    latitude=22.5,
                    longitude=90.2,
                ),
            ],
        )

        self.assertEqual(len(route.points), 2)

    def test_valid_geography_plan(self):
        plan = GeographyPlan(
            enabled=True,
            map_source="local",
            center=GeoPoint(
                latitude=23.8,
                longitude=90.4,
            ),
            zoom_level=2.0,
            regions=[
                GeoRegion(
                    id="bangladesh",
                    name="Bangladesh",
                )
            ],
            markers=[
                GeoMarker(
                    id="dhaka",
                    name="Dhaka",
                    position=GeoPoint(
                        latitude=23.8103,
                        longitude=90.4125,
                    ),
                )
            ],
            operations=[
                GeoOperation(
                    type="zoom",
                    zoom_level=4.0,
                    duration=2.0,
                )
            ],
        )

        self.assertTrue(plan.enabled)
        self.assertEqual(plan.map_source, "local")
        self.assertEqual(len(plan.regions), 1)
        self.assertEqual(len(plan.markers), 1)
        self.assertEqual(len(plan.operations), 1)

    def test_invalid_operation(self):
        with self.assertRaises(ValidationError):
            GeoOperation(
                type="rotate",
                duration=1,
            )


if __name__ == "__main__":
    unittest.main()