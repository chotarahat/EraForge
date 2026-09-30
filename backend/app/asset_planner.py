from app.assets import AssetRequirement
from app.models import Scene


ASSET_TYPE_RULES = {
    "map": "map",
    "maps": "map",
    "city": "location",
    "cities": "location",
    "location": "location",
    "locations": "location",
    "landmark": "landmark",
    "landmarks": "landmark",
    "character": "character",
    "characters": "character",
    "person": "character",
    "people": "character",
    "human": "character",
    "humans": "character",
    "background": "background",
    "landscape": "background",
    "illustration": "illustration",
    "illustrations": "illustration",
    "icon": "icon",
    "icons": "icon",
    "image": "image",
    "images": "image",
    "text": "text",
}


def infer_asset_type(hint: str) -> str:
    normalized = hint.strip().lower()

    for keyword, asset_type in ASSET_TYPE_RULES.items():
        if keyword in normalized:
            return asset_type

    return "illustration"


def build_asset_requirements(scene: Scene) -> list[AssetRequirement]:
    requirements: list[AssetRequirement] = []
    seen: set[tuple[str, str]] = set()

    for hint in scene.asset_hints:
        name = hint.strip()

        if not name:
            continue

        asset_type = infer_asset_type(name)
        key = (asset_type, name.lower())

        if key in seen:
            continue

        seen.add(key)

        requirements.append(
            AssetRequirement(
                type=asset_type,
                name=name,
                source="local",
                status="required",
            )
        )

    return requirements