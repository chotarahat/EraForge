from .assets import AssetRequirement
from typing import Literal
from pydantic import BaseModel, Field, model_validator


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
    asset_requirements: list[AssetRequirement] = Field(default_factory=list)


class ScenePlan(BaseModel):
    title: str
    summary: str
    total_duration: float
    aspect_ratio: Literal["9:16", "16:9", "1:1"]
    style: str
    scenes: list[Scene]

    @model_validator(mode="after")
    def validate_timeline(self):
        if not self.scenes:
            raise ValueError("Scene plan must contain at least one scene.")

        if self.total_duration <= 0:
            raise ValueError("Total duration must be greater than zero.")

        previous_end = 0.0

        for index, scene in enumerate(self.scenes):
            if scene.start < 0:
                raise ValueError(
                    f"Scene {index + 1} starts before 0 seconds."
                )

            if scene.end <= scene.start:
                raise ValueError(
                    f"Scene {index + 1} must have a positive duration."
                )

            if scene.start < previous_end - 0.01:
                raise ValueError(
                    f"Scene {index + 1} overlaps the previous scene."
                )

            if scene.start > previous_end + 0.01:
                raise ValueError(
                    f"Scene {index + 1} creates a timeline gap."
                )

            previous_end = scene.end

        if abs(previous_end - self.total_duration) > 0.01:
            raise ValueError(
                f"Timeline ends at {previous_end:.3f}s but total duration "
                f"is {self.total_duration:.3f}s."
            )

        return self


class PlanRequest(BaseModel):
    script: str = Field(min_length=20, max_length=12000)
    duration: int = Field(default=60, ge=15, le=300)
    aspect_ratio: Literal["9:16", "16:9", "1:1"] = "9:16"
    style: str = "animated historical documentary"
