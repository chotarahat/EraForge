from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.asset_manifest import build_asset_manifest, resolve_asset_manifest
from app.assets import AssetDefinition, AssetResolutionResult
from app.geography import GeographyPlan
from app.geography_manifest import build_geography_manifest
from app.renderer import RenderPlan, SceneRenderPlan
from app.renderer_planner import build_render_plan
from app.render_pipeline import render_preview_bundle
from app.scene_renderer import render_scene_to_svg
from .models import PlanRequest, ScenePlan
from .planner import create_plan
from .ai.factory import get_provider_info

app = FastAPI(title="EraForge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "eraforge-api",
        "version": "0.1.0",
        **get_provider_info(),
    }


@app.post("/api/plan")
def plan(request: PlanRequest):
    try:
        result = create_plan(request)
        return result.model_dump()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Scene planning failed: {exc}") from exc
@app.post("/api/validate-plan")
def validate_plan(plan: ScenePlan):
    return {
        "valid": True,
        "plan": plan.model_dump(),
    }


@app.post("/api/assets/plan", response_model=list[AssetDefinition])
def create_asset_plan(plan: ScenePlan):
    return build_asset_manifest(plan)


@app.post(
    "/api/geography/plan",
    response_model=dict[str, GeographyPlan],
)
def create_geography_plan(plan: ScenePlan):
    return build_geography_manifest(plan)


@app.post(
    "/api/render/plan",
    response_model=RenderPlan,
)
def create_render_plan(plan: ScenePlan):
    return build_render_plan(plan)


@app.post("/api/render/preview")
def render_preview(plan: ScenePlan):
    render_plan = build_render_plan(plan)

    result = render_preview_bundle(
        render_plan
    )

    return {
        "title": render_plan.title,
        "total_duration": render_plan.total_duration,
        "width": render_plan.width,
        "height": render_plan.height,
        "scene_count": len(
            render_plan.scenes
        ),
        "output_dir": result.output_dir,
        "scene_files": result.scene_files,
    }


@app.get("/api/render/file/{filename}")
def get_render_file(filename: str):
    output_dir = Path("backend/outputs/render_preview")
    file_path = output_dir / Path(filename).name

    if not file_path.exists() or file_path.suffix.lower() != ".svg":
        raise HTTPException(status_code=404, detail="Render file not found")

    return FileResponse(
        path=file_path,
        media_type="image/svg+xml",
        filename=file_path.name,
    )


@app.post("/api/render/scene")
def render_scene_preview(scene: SceneRenderPlan):
    width = 1080
    height = 1920

    svg = render_scene_to_svg(
        scene,
        width=width,
        height=height,
    )

    return {
        "scene_id": scene.scene_id,
        "width": width,
        "height": height,
        "svg": svg,
    }


@app.post(
    "/api/assets/resolve",
    response_model=AssetResolutionResult,
)
def resolve_assets(plan: ScenePlan):
    resolved, missing, placeholders = resolve_asset_manifest(plan)

    return AssetResolutionResult(
        resolved=resolved,
        missing=missing,
        placeholders=placeholders,
    )