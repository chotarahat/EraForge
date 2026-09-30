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


def _normalize_timing(data: dict, target_duration: int) -> dict:
    """Normalize AI timing to seconds and validate the generated timeline."""
    total_duration = float(data.get("total_duration", 0))
    scenes = data.get("scenes", [])

    if not scenes:
        raise RuntimeError("AI returned a scene plan with no scenes")

    # Some local models naturally express timestamps in milliseconds.
    # Convert to seconds when the generated total is approximately target * 1000.
    if abs(total_duration - target_duration) <= 1:
        scale = 1.0
    elif abs((total_duration / 1000) - target_duration) <= 1:
        scale = 0.001
    else:
        raise RuntimeError(
            f"AI returned an invalid total duration of {total_duration}. "
            f"Expected approximately {target_duration} seconds."
        )

    normalized_scenes = []

    for scene in scenes:
        start = float(scene["start"]) * scale
        end = float(scene["end"]) * scale

        normalized_scene = {
            **scene,
            "start": round(start, 3),
            "end": round(end, 3),
        }
        normalized_scenes.append(normalized_scene)

    # Validate sequential timing.
    previous_end = 0.0

    for index, scene in enumerate(normalized_scenes):
        start = scene["start"]
        end = scene["end"]

        if end <= start:
            raise RuntimeError(
                f"Scene {index + 1} has invalid timing: {start} → {end}."
            )

        if abs(start - previous_end) > 0.05:
            raise RuntimeError(
                f"Scene {index + 1} breaks timeline continuity. "
                f"Expected start around {previous_end}, got {start}."
            )

        previous_end = end

    # Normalize the final boundary to the requested duration when it is
    # within a small tolerance.
    if abs(previous_end - target_duration) > 1:
        raise RuntimeError(
            f"Scene timeline ends at {previous_end}s instead of "
            f"{target_duration}s."
        )

    normalized_data = {
        **data,
        "total_duration": float(target_duration),
        "scenes": normalized_scenes,
    }

    return normalized_data


def create_plan(request: PlanRequest) -> ScenePlan:
    user_prompt = build_user_prompt(
        request.script, request.duration, request.aspect_ratio, request.style
    )

    output = create_provider().generate_json(
        SYSTEM_PROMPT,
        user_prompt,
        SCENE_SCHEMA,
    )

    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "AI provider returned invalid JSON despite structured output"
        ) from exc

    normalized_data = _normalize_timing(data, request.duration)

    return ScenePlan.model_validate(normalized_data)
