from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.asset_manifest import build_asset_manifest
from app.assets import AssetDefinition
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