from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.asset_manifest import build_asset_manifest, resolve_asset_manifest
from app.assets import AssetDefinition, AssetResolutionResult
from app.geography import GeographyPlan
from app.geography_manifest import build_geography_manifest
from app.renderer import RenderPlan, SceneRenderPlan
from app.renderer_planner import build_render_plan
from app.render_pipeline import render_preview_bundle
from app.scene_renderer import render_scene_to_svg
from app.video_export import VideoExportSettings
from app.video_pipeline import export_render_plan
from app.narration import (
    LocalTTS,
    NarrationManifest,
    NarrationPlan,
    NarrationSettings,
    build_narration_manifest,
    build_narration_plan,
    generate_narration,
)
from app.subtitles import (
    SubtitleSyncReport,
    SubtitleTrack,
    build_subtitle_track,
    subtitle_track_to_srt,
    validate_subtitle_track,
    write_srt_file,
)
from .models import PlanRequest, ScenePlan
from .planner import create_plan
from .ai.factory import get_provider_info


class NarrationManifestRequest(BaseModel):
    plan: ScenePlan
    narration: NarrationPlan


class SubtitleSyncRequest(BaseModel):
    plan: ScenePlan
    narration_manifest: NarrationManifest | None = None


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
    "/api/subtitles/plan",
    response_model=SubtitleTrack,
)
def subtitle_plan(plan: ScenePlan):
    return build_subtitle_track(
        plan
    )


@app.post(
    "/api/subtitles/sync",
    response_model=SubtitleSyncReport,
)
def subtitle_sync(
    request: SubtitleSyncRequest,
):
    track = build_subtitle_track(
        request.plan,
        request.narration_manifest,
    )

    return validate_subtitle_track(
        request.plan,
        track,
    )


@app.post("/api/subtitles/srt")
def subtitle_srt(plan: ScenePlan):
    track = build_subtitle_track(plan)

    return {
        "cue_count": len(track.cues),
        "srt": subtitle_track_to_srt(track),
    }


@app.post("/api/subtitles/generate")
def subtitle_generate(
    plan: ScenePlan,
):
    track = build_subtitle_track(
        plan
    )

    validation = validate_subtitle_track(
        plan,
        track,
    )

    output_path = write_srt_file(
        track
    )

    return {
        "cue_count": len(track.cues),
        "output_file": output_path,
        "srt": subtitle_track_to_srt(track),
        "sync_valid": validation.valid,
        "sync_issues": [
            issue.model_dump()
            for issue in validation.issues
        ],
    }


@app.get("/api/subtitles/file/{filename}")
def subtitle_file(filename: str):
    output_dir = Path("outputs/subtitles")
    file_path = output_dir / Path(filename).name

    if not file_path.exists() or file_path.suffix.lower() != ".srt":
        raise HTTPException(
            status_code=404,
            detail="Subtitle file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/x-subrip",
        filename=file_path.name,
    )


@app.post("/api/narration/plan", response_model=NarrationPlan)
def narration_plan(plan: ScenePlan):
    return build_narration_plan(plan)


@app.post(
    "/api/narration/manifest",
    response_model=NarrationManifest,
)
def narration_manifest(
    request: NarrationManifestRequest,
):
    return build_narration_manifest(
        request.plan,
        request.narration,
    )


@app.post("/api/narration/generate", response_model=NarrationPlan)
def narration_generate(payload: dict[str, Any]):
    settings_data = payload.pop("_narration_settings", None)

    plan = ScenePlan.model_validate(payload)

    narration = build_narration_plan(plan)

    if not narration.segments:
        return narration

    settings = (
        NarrationSettings(**settings_data)
        if isinstance(settings_data, dict)
        else None
    )

    return generate_narration(
        narration,
        settings=settings,
    )


@app.get("/api/narration/voices")
def narration_voices():
    return {
        "voices": LocalTTS().list_voices()
    }


@app.get("/api/narration/file/{filename}")
def narration_file(filename: str):
    output_dir = Path("backend/outputs/narration")
    file_path = output_dir / Path(filename).name

    if not file_path.exists() or file_path.suffix.lower() != ".wav":
        raise HTTPException(
            status_code=404,
            detail="Narration file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="audio/wav",
        filename=file_path.name,
    )


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


@app.post("/api/render/export")
def render_export(plan: ScenePlan):
    result = export_render_plan(plan)

    return result.model_dump()


@app.get("/api/render/video/{filename}")
def render_video_file(filename: str):
    output_dir = Path(
        "outputs/video_export/videos"
    )

    file_path = output_dir / Path(filename).name

    if (
        not file_path.exists()
        or file_path.suffix.lower() != ".mp4"
    ):
        raise HTTPException(
            status_code=404,
            detail="Video file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=file_path.name,
    )


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