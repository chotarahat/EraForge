import unittest

from pydantic import ValidationError

from app.assets import AssetDefinition, AssetRequirement


class TestAssetModels(unittest.TestCase):

    def test_valid_asset_requirement(self):
        asset = AssetRequirement(
            type="map",
            name="south_asia_map",
        )

        self.assertEqual(asset.type, "map")
        self.assertEqual(asset.name, "south_asia_map")
        self.assertEqual(asset.source, "local")
        self.assertEqual(asset.status, "required")

    def test_valid_asset_definition(self):
        asset = AssetDefinition(
            id="asset_map_001",
            type="map",
            name="south_asia_map",
            source="natural_earth",
            path="assets/maps/south_asia.svg",
            status="available",
            license="Public Domain",
            metadata={
                "region": "South Asia",
            },
        )

        self.assertEqual(asset.id, "asset_map_001")
        self.assertEqual(asset.type, "map")
        self.assertEqual(asset.status, "available")
        self.assertEqual(
            asset.metadata["region"],
            "South Asia",
        )

    def test_invalid_asset_type(self):
        with self.assertRaises(ValidationError):
            AssetRequirement(
                type="video",
                name="invalid_asset",
            )

    def test_invalid_asset_status(self):
        with self.assertRaises(ValidationError):
            AssetDefinition(
                id="asset_001",
                type="image",
                name="test_image",
                source="local",
                status="downloaded",
            )

    def test_empty_asset_name(self):
        with self.assertRaises(ValidationError):
            AssetRequirement(
                type="image",
                name="",
            )


if __name__ == "__main__":
    unittest.main()