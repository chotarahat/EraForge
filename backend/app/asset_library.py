from pathlib import Path
import re

from app.assets import AssetDefinition


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".gif",
    ".mp4",
    ".mov",
}


def normalize_asset_name(value: str) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        "_",
        value.strip().lower(),
    ).strip("_")


class LocalAssetLibrary:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def exists(self) -> bool:
        return self.root.exists()

    def scan(self) -> list[AssetDefinition]:
        if not self.root.exists():
            return []

        assets: list[AssetDefinition] = []

        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            relative = path.relative_to(self.root)
            parts = relative.parts

            if len(parts) >= 2:
                asset_type = parts[0]
            else:
                asset_type = "image"

            asset_type = (
                asset_type
                if asset_type in {
                    "map",
                    "character",
                    "location",
                    "background",
                    "landmark",
                    "icon",
                    "illustration",
                    "text",
                    "image",
                }
                else "image"
            )

            name = path.stem
            normalized_name = normalize_asset_name(name)

            assets.append(
                AssetDefinition(
                    id=f"asset_{asset_type}_{normalized_name}",
                    type=asset_type,
                    name=name,
                    source="local",
                    path=str(path),
                    status="available",
                    metadata={
                        "extension": path.suffix.lower(),
                        "relative_path": str(relative),
                    },
                )
            )

        return assets

    def find(
        self,
        asset_type: str,
        name: str,
    ) -> AssetDefinition | None:
        normalized_name = normalize_asset_name(name)

        for asset in self.scan():
            if (
                asset.type == asset_type
                and normalize_asset_name(asset.name)
                == normalized_name
            ):
                return asset

        return None

    def resolve(
        self,
        requirements,
    ) -> tuple[list[AssetDefinition], list]:
        resolved: list[AssetDefinition] = []
        missing = []

        for requirement in requirements:
            asset = self.find(
                requirement.type,
                requirement.name,
            )

            if asset is None:
                missing.append(requirement)
            else:
                resolved.append(asset)

        return resolved, missing