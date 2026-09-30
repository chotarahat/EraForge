from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.models import ScenePlan


PROJECTS_ROOT = Path("outputs/projects")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _project_path(project_id: str) -> Path:
    return PROJECTS_ROOT / f"{project_id}.json"


def _validate_project_id(project_id: str) -> str:
    if not project_id:
        raise ValueError("Project ID is required.")

    if Path(project_id).name != project_id:
        raise ValueError("Invalid project ID.")

    return project_id


def create_project(
    name: str,
    scene_plan: ScenePlan | None = None,
    script: str = "",
    duration: float = 60,
) -> dict:
    name = name.strip()

    if not name:
        raise ValueError("Project name is required.")

    PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

    project_id = uuid4().hex[:12]
    now = _utc_now().isoformat()

    project = {
        "id": project_id,
        "name": name,
        "created_at": now,
        "updated_at": now,
        "script": script,
        "duration": duration,
        "scene_plan": scene_plan.model_dump() if scene_plan else None,
    }

    _project_path(project_id).write_text(
        json.dumps(project, indent=2),
        encoding="utf-8",
    )

    return project

def list_projects() -> list[dict]:
    PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

    projects: list[dict] = []

    for path in PROJECTS_ROOT.glob("*.json"):
        try:
            project = json.loads(path.read_text(encoding="utf-8"))
            projects.append(
                {
                    "id": project["id"],
                    "name": project["name"],
                    "created_at": project["created_at"],
                    "updated_at": project["updated_at"],
                }
            )
        except (OSError, json.JSONDecodeError, KeyError):
            continue

    projects.sort(
        key=lambda item: item["updated_at"],
        reverse=True,
    )

    return projects


def get_project(project_id: str) -> dict | None:
    project_id = _validate_project_id(project_id)
    path = _project_path(project_id)

    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def update_project(
    project_id: str,
    name: str | None = None,
    scene_plan: ScenePlan | None = None,
    script: str | None = None,
    duration: float | None = None,
) -> dict | None:
    project = get_project(project_id)

    if project is None:
        return None

    if name is not None:
        name = name.strip()

        if not name:
            raise ValueError("Project name is required.")

        project["name"] = name

    if scene_plan is not None:
        project["scene_plan"] = scene_plan.model_dump()

    if script is not None:
        project["script"] = script

    if duration is not None:
        project["duration"] = duration

    project["updated_at"] = _utc_now().isoformat()

    _project_path(project_id).write_text(
        json.dumps(project, indent=2),
        encoding="utf-8",
    )

    return project

def delete_project(project_id: str) -> bool:
    project_id = _validate_project_id(project_id)
    path = _project_path(project_id)

    if not path.exists():
        return False

    path.unlink()
    return True