from typing import Literal
from pydantic import BaseModel, Field


class Scene(BaseModel):
    id: str = Field(description="Stable scene identifier such as scene-01")
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    title: str = Field(description="Short human-readable scene title")
    narration: str = Field(description="Narration associated with this scene")
    visual: str = Field(description="What should be visible in the scene")
    animation: str = Field(description="How the visual should move or change")
    camera: str = Field(description="Camera movement such as zoom, pan, orbit or static")
    caption: str = Field(description="Short on-screen caption")
    location: str | None = Field(default=None, description="Geographic place if relevant")
    asset_hints: list[str] = Field(default_factory=list, description="Suggested asset categories")


class ScenePlan(BaseModel):
    title: str
    summary: str
    total_duration: float
    aspect_ratio: Literal["9:16", "16:9", "1:1"]
    style: str
    scenes: list[Scene]


class PlanRequest(BaseModel):
    script: str = Field(min_length=20, max_length=12000)
    duration: int = Field(default=60, ge=15, le=300)
    aspect_ratio: Literal["9:16", "16:9", "1:1"] = "9:16"
    style: str = "animated historical documentary"
