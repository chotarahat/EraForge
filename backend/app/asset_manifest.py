from collections import defaultdict
import re

from app.asset_planner import build_asset_requirements
from app.asset_library import LocalAssetLibrary
from app.assets import AssetDefinition, AssetRequirement
from app.models import Scene, ScenePlan


def make_asset_id(asset_type: str, name: str) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "_",
        name.strip().lower(),
    ).strip("_")

    return f"asset_{asset_type}_{slug}"


def build_asset_manifest(plan: ScenePlan) -> list[AssetDefinition]:
    asset_scenes: dict[tuple[str, str], set[str]] = defaultdict(set)
    asset_info: dict[tuple[str, str], tuple[str, str]] = {}

    for scene in plan.scenes:
        requirements = build_asset_requirements(scene)

        for requirement in requirements:
            key = (
                requirement.type,
                requirement.name.strip().lower(),
            )

            asset_scenes[key].add(scene.id)

            if key not in asset_info:
                asset_info[key] = (
                    requirement.name,
                    requirement.source,
                )

    assets: list[AssetDefinition] = []

    for key, scene_ids in sorted(asset_scenes.items()):
        asset_type, normalized_name = key
        name, source = asset_info[key]

        assets.append(
            AssetDefinition(
                id=make_asset_id(asset_type, name),
                type=asset_type,
                name=name,
                source=source,
                status="required",
                metadata={
                    "scene_ids": sorted(scene_ids),
                },
            )
        )

    return assets


def resolve_asset_manifest(
    plan,
    asset_root: str = "backend/assets",
):
    library = LocalAssetLibrary(asset_root)

    requirements: list[AssetRequirement] = []

    for scene in plan.scenes:
        requirements.extend(
            build_asset_requirements(scene)
        )

    unique_requirements: dict[
        tuple[str, str],
        AssetRequirement,
    ] = {}

    for requirement in requirements:
        key = (
            requirement.type,
            requirement.name.strip().lower(),
        )

        unique_requirements[key] = requirement

    resolved, missing = library.resolve(
        unique_requirements.values()
    )

    placeholders: list[AssetDefinition] = []

    for requirement in missing:
        normalized_name = requirement.name.strip().lower()
        slug = re.sub(
            r"[^a-z0-9]+",
            "_",
            normalized_name,
        ).strip("_")

        placeholders.append(
            AssetDefinition(
                id=f"placeholder_{requirement.type}_{slug}",
                type=requirement.type,
                name=requirement.name,
                source="placeholder",
                path=None,
                status="placeholder",
                metadata={
                    "original_source": requirement.source,
                },
            )
        )

    return resolved, missing, placeholders