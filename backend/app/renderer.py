from typing import Any, Literal

from pydantic import BaseModel, Field


RenderLayerType = Literal[
    "background",
    "image",
    "svg",
    "map",
    "text",
    "shape",
    "marker",
    "route",
]


AnimationType = Literal[
    "fade_in",
    "fade_out",
    "slide",
    "scale",
    "pan",
    "zoom",
    "reveal",
    "highlight",
]


CameraType = Literal[
    "static",
    "pan",
    "zoom",
]


class RenderPosition(BaseModel):
    x: float = 0.0
    y: float = 0.0


class RenderSize(BaseModel):
    width: float | None = None
    height: float | None = None


class RenderLayer(BaseModel):
    id: str = Field(min_length=1)
    type: RenderLayerType
    asset_id: str | None = None
    text: str | None = None

    position: RenderPosition = Field(
        default_factory=RenderPosition
    )

    size: RenderSize = Field(
        default_factory=RenderSize
    )

    opacity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class AnimationInstruction(BaseModel):
    type: AnimationType
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    from_value: float | None = None
    to_value: float | None = None
    direction: str | None = None

    def model_post_init(self, __context):
        if self.end <= self.start:
            raise ValueError(
                "Animation end must be greater than start"
            )


class CameraInstruction(BaseModel):
    type: CameraType = "static"

    start: float = Field(
        default=0.0,
        ge=0,
    )

    end: float = Field(
        default=1.0,
        gt=0,
    )

    x: float | None = None
    y: float | None = None

    zoom_from: float | None = Field(
        default=None,
        gt=0,
    )

    zoom_to: float | None = Field(
        default=None,
        gt=0,
    )


class SceneRenderPlan(BaseModel):
    scene_id: str = Field(min_length=1)
    start: float = Field(ge=0)
    end: float = Field(gt=0)

    layers: list[RenderLayer] = Field(
        default_factory=list
    )

    animations: list[AnimationInstruction] = Field(
        default_factory=list
    )

    camera: CameraInstruction = Field(
        default_factory=CameraInstruction
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class RenderPlan(BaseModel):
    title: str = Field(min_length=1)
    total_duration: float = Field(gt=0)

    width: int = Field(
        default=1080,
        gt=0,
    )

    height: int = Field(
        default=1920,
        gt=0,
    )

    fps: int = Field(
        default=30,
        gt=0,
    )

    scenes: list[SceneRenderPlan] = Field(
        min_length=1
    )