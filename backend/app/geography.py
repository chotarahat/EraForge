from typing import Literal

from pydantic import BaseModel, Field


GeoOperationType = Literal[
    "show_region",
    "highlight_region",
    "place_marker",
    "draw_route",
    "pan",
    "zoom",
    "reset_view",
]


class GeoPoint(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class GeoRegion(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    source_id: str | None = None


class GeoMarker(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    position: GeoPoint
    icon: str = "marker"


class GeoRoute(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    points: list[GeoPoint] = Field(min_length=2)


class GeoOperation(BaseModel):
    type: GeoOperationType
    target_id: str | None = None
    position: GeoPoint | None = None
    duration: float = Field(default=1.0, gt=0)
    zoom_level: float | None = Field(default=None, gt=0)


class GeographyPlan(BaseModel):
    enabled: bool = False
    map_source: str = "local"
    center: GeoPoint | None = None
    zoom_level: float = Field(default=1.0, gt=0)

    regions: list[GeoRegion] = Field(default_factory=list)
    markers: list[GeoMarker] = Field(default_factory=list)
    routes: list[GeoRoute] = Field(default_factory=list)
    operations: list[GeoOperation] = Field(default_factory=list)