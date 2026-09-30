from app.geography_manifest import build_geography_manifest
from app.models import ScenePlan
from app.renderer import (
    AnimationInstruction,
    CameraInstruction,
    RenderLayer,
    RenderPlan,
    SceneRenderPlan,
)


def parse_animation_type(animation: str) -> str:
    text = animation.lower()

    if "fade" in text:
        return "fade_in"

    if "slide" in text:
        return "slide"

    if "scale" in text:
        return "scale"

    if "highlight" in text:
        return "highlight"

    if "zoom" in text:
        return "zoom"

    if "pan" in text:
        return "pan"

    if "reveal" in text:
        return "reveal"

    return "fade_in"


def parse_camera_type(camera: str) -> str:
    text = camera.lower()

    if "zoom" in text:
        return "zoom"

    if "pan" in text:
        return "pan"

    return "static"


def build_scene_render_plan(
    scene,
    geography_plan=None,
) -> SceneRenderPlan:
    layers = [
        RenderLayer(
            id=f"{scene.id}_background",
            type="background",
            text=None,
            metadata={
                "visual": scene.visual,
            },
        )
    ]

    if scene.caption.strip():
        layers.append(
            RenderLayer(
                id=f"{scene.id}_caption",
                type="text",
                text=scene.caption,
                metadata={
                    "role": "caption",
                },
            )
        )

    for index, hint in enumerate(scene.asset_hints):
        normalized = hint.strip()

        if not normalized:
            continue

        asset_type = "image"

        if "map" in normalized.lower():
            asset_type = "map"
        elif "icon" in normalized.lower():
            asset_type = "shape"
        elif "landmark" in normalized.lower():
            asset_type = "image"
        elif "character" in normalized.lower():
            asset_type = "image"
        elif "location" in normalized.lower():
            asset_type = "image"
        elif "background" in normalized.lower():
            asset_type = "background"
        elif "illustration" in normalized.lower():
            asset_type = "image"

        layers.append(
            RenderLayer(
                id=f"{scene.id}_asset_{index + 1}",
                type=asset_type,
                metadata={
                    "asset_hint": normalized,
                },
            )
        )

    animations = []

    if scene.animation.strip():
        animation_type = parse_animation_type(
            scene.animation
        )

        duration = min(
            1.0,
            max(
                0.1,
                scene.end - scene.start,
            ),
        )

        animations.append(
            AnimationInstruction(
                type=animation_type,
                start=0,
                end=duration,
            )
        )

    camera_type = parse_camera_type(scene.camera)

    camera = CameraInstruction(
        type=camera_type,
        start=0,
        end=max(
            0.1,
            scene.end - scene.start,
        ),
    )

    if camera_type == "zoom":
        camera.zoom_from = 1.0
        camera.zoom_to = 1.2

    render_metadata = {
        "narration": scene.narration,
        "visual": scene.visual,
        "animation": scene.animation,
        "camera": scene.camera,
        "location": scene.location,
        "geography_enabled": bool(
            geography_plan and geography_plan.enabled
        ),
    }

    if geography_plan:
        render_metadata["geography"] = (
            geography_plan.model_dump()
        )

    return SceneRenderPlan(
        scene_id=scene.id,
        start=scene.start,
        end=scene.end,
        layers=layers,
        animations=animations,
        camera=camera,
        metadata=render_metadata,
    )


def build_render_plan(
    plan: ScenePlan,
) -> RenderPlan:
    geography_manifest = build_geography_manifest(
        plan
    )

    scenes = [
        build_scene_render_plan(
            scene,
            geography_manifest.get(scene.id),
        )
        for scene in plan.scenes
    ]

    if plan.aspect_ratio == "9:16":
        width = 1080
        height = 1920
    elif plan.aspect_ratio == "16:9":
        width = 1920
        height = 1080
    else:
        width = 1080
        height = 1080

    return RenderPlan(
        title=plan.title,
        total_duration=plan.total_duration,
        width=width,
        height=height,
        fps=30,
        scenes=scenes,
    )