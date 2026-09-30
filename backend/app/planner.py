import json
import os
from pathlib import Path
from dotenv import load_dotenv
from .ai.factory import create_provider
from .models import PlanRequest, ScenePlan
from .prompts import SYSTEM_PROMPT, build_user_prompt


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


SCENE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "total_duration": {"type": "number"},
        "aspect_ratio": {"type": "string", "enum": ["9:16", "16:9", "1:1"]},
        "style": {"type": "string"},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "start": {"type": "number"},
                    "end": {"type": "number"},
                    "title": {"type": "string"},
                    "narration": {"type": "string"},
                    "visual": {"type": "string"},
                    "animation": {"type": "string"},
                    "camera": {"type": "string"},
                    "caption": {"type": "string"},
                    "location": {"type": ["string", "null"]},
                    "asset_hints": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "id", "start", "end", "title", "narration", "visual",
                    "animation", "camera", "caption", "location", "asset_hints"
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "summary", "total_duration", "aspect_ratio", "style", "scenes"],
    "additionalProperties": False,
}


def create_plan(request: PlanRequest) -> ScenePlan:
    user_prompt = build_user_prompt(
        request.script, request.duration, request.aspect_ratio, request.style
    )
    output = create_provider().generate_json(SYSTEM_PROMPT, user_prompt, SCENE_SCHEMA)

    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI provider returned invalid JSON despite structured output") from exc

    return ScenePlan.model_validate(data)
