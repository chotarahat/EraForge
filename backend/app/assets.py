from typing import Any, Literal

from pydantic import BaseModel, Field


AssetType = Literal[
    "map",
    "character",
    "location",
    "background",
    "landmark",
    "icon",
    "illustration",
    "text",
    "image",
]

AssetStatus = Literal[
    "required",
    "available",
    "placeholder",
    "missing",
]


class AssetRequirement(BaseModel):
    """
    A scene-level request for a visual asset.

    This describes what a scene needs without resolving it to an
    actual file yet.
    """

    type: AssetType
    name: str = Field(min_length=1)
    source: str = Field(default="local", min_length=1)
    status: AssetStatus = "required"


class AssetDefinition(BaseModel):
    """
    A resolved or partially resolved asset.

    This is the canonical asset representation that the future
    asset resolver and renderer will consume.
    """

    id: str = Field(min_length=1)
    type: AssetType
    name: str = Field(min_length=1)
    source: str = Field(min_length=1)

    path: str | None = None
    status: AssetStatus = "required"
    license: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)