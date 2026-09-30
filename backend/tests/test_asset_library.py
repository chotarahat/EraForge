import tempfile
import unittest
from pathlib import Path

from app.asset_library import LocalAssetLibrary


class TestLocalAssetLibrary(unittest.TestCase):

    def test_scan_finds_local_assets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            map_dir = root / "map"
            map_dir.mkdir()

            asset_file = map_dir / "south_asia.svg"
            asset_file.write_text(
                "<svg></svg>",
                encoding="utf-8",
            )

            library = LocalAssetLibrary(root)

            assets = library.scan()

            self.assertEqual(len(assets), 1)
            self.assertEqual(
                assets[0].name,
                "south_asia",
            )
            self.assertEqual(
                assets[0].type,
                "map",
            )
            self.assertEqual(
                assets[0].source,
                "local",
            )
            self.assertEqual(
                assets[0].status,
                "available",
            )

    def test_find_asset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            image_dir = root / "background"
            image_dir.mkdir()

            asset_file = image_dir / "ancient_landscape.png"
            asset_file.write_bytes(b"test")

            library = LocalAssetLibrary(root)

            asset = library.find(
                "background",
                "Ancient Landscape",
            )

            self.assertIsNotNone(asset)
            self.assertEqual(
                asset.name,
                "ancient_landscape",
            )

    def test_missing_asset_returns_none(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            library = LocalAssetLibrary(temp_dir)

            asset = library.find(
                "map",
                "missing_map",
            )

            self.assertIsNone(asset)

    def test_unsupported_files_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            image_dir = root / "image"
            image_dir.mkdir()

            (image_dir / "valid.png").write_bytes(b"test")
            (image_dir / "ignored.txt").write_text(
                "ignored",
                encoding="utf-8",
            )

            library = LocalAssetLibrary(root)

            assets = library.scan()

            self.assertEqual(len(assets), 1)
            self.assertEqual(
                assets[0].name,
                "valid",
            )


if __name__ == "__main__":
    unittest.main()