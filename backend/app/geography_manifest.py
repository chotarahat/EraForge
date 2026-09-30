from app.geography import GeographyPlan
from app.geography_planner import build_geography_plan
from app.models import ScenePlan


def build_geography_manifest(
    plan: ScenePlan,
) -> dict[str, GeographyPlan]:
    manifest: dict[str, GeographyPlan] = {}

    for scene in plan.scenes:
        manifest[scene.id] = build_geography_plan(scene)

    return manifest