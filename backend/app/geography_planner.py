from app.geography import (
    GeoOperation,
    GeoPoint,
    GeoRegion,
    GeographyPlan,
)
from app.models import Scene


GEOGRAPHY_REGISTRY = {
    "bangladesh": {
        "id": "bangladesh",
        "name": "Bangladesh",
        "center": (23.685, 90.356),
    },
    "south asia": {
        "id": "south_asia",
        "name": "South Asia",
        "center": (22.0, 79.0),
    },
    "indian subcontinent": {
        "id": "indian_subcontinent",
        "name": "Indian Subcontinent",
        "center": (22.0, 79.0),
    },
    "india": {
        "id": "india",
        "name": "India",
        "center": (22.5, 79.0),
    },
    "bay of bengal": {
        "id": "bay_of_bengal",
        "name": "Bay of Bengal",
        "center": (15.0, 88.0),
    },
    "himalayas": {
        "id": "himalayas",
        "name": "Himalayas",
        "center": (28.0, 84.0),
    },
    "ganges": {
        "id": "ganges",
        "name": "Ganges",
        "center": (25.5, 83.0),
    },
    "brahmaputra": {
        "id": "brahmaputra",
        "name": "Brahmaputra",
        "center": (26.5, 91.0),
    },
}


def normalize_text(value: str) -> str:
    return " ".join(
        value.strip().lower().split()
    )


def find_geography_matches(
    scene: Scene,
) -> list[dict]:
    text_parts = [
        scene.title,
        scene.visual,
        scene.location,
        *scene.asset_hints,
    ]

    text = normalize_text(
        " ".join(
            part
            for part in text_parts
            if part
        )
    )

    matches: list[dict] = []
    seen: set[str] = set()

    for alias, entry in GEOGRAPHY_REGISTRY.items():
        if alias in text and entry["id"] not in seen:
            matches.append(entry)
            seen.add(entry["id"])

    return matches


def build_geography_plan(
    scene: Scene,
) -> GeographyPlan:
    matches = find_geography_matches(scene)

    text = normalize_text(
        " ".join(
            [
                scene.title,
                scene.visual,
                scene.animation,
                scene.camera,
                scene.location or "",
                *scene.asset_hints,
            ]
        )
    )

    has_map_hint = any(
        "map" in hint.lower()
        for hint in scene.asset_hints
    )

    map_in_visual = "map" in scene.visual.lower()

    enabled = bool(
        matches
        or has_map_hint
        or map_in_visual
    )

    if not enabled:
        return GeographyPlan(enabled=False)

    regions = [
        GeoRegion(
            id=entry["id"],
            name=entry["name"],
            source_id=entry["id"],
        )
        for entry in matches
    ]

    center = None

    if matches:
        latitude = sum(
            entry["center"][0]
            for entry in matches
        ) / len(matches)

        longitude = sum(
            entry["center"][1]
            for entry in matches
        ) / len(matches)

        center = GeoPoint(
            latitude=latitude,
            longitude=longitude,
        )

    operations: list[GeoOperation] = []

    if regions:
        operations.append(
            GeoOperation(
                type="show_region",
                target_id=regions[0].id,
                duration=1.0,
            )
        )

    if any(
        keyword in text
        for keyword in [
            "highlight",
            "highlighted",
            "emphasize",
            "focus on",
        ]
    ):
        if regions:
            operations.append(
                GeoOperation(
                    type="highlight_region",
                    target_id=regions[0].id,
                    duration=1.5,
                )
            )

    if any(
        keyword in text
        for keyword in [
            "zoom in",
            "zoom into",
            "zoom closer",
            "zoom",
        ]
    ):
        operations.append(
            GeoOperation(
                type="zoom",
                zoom_level=3.0,
                duration=1.5,
            )
        )

    if any(
        keyword in text
        for keyword in [
            "zoom out",
            "pull out",
            "zoom back",
        ]
    ):
        operations.append(
            GeoOperation(
                type="zoom",
                zoom_level=1.0,
                duration=1.5,
            )
        )

    if any(
        keyword in text
        for keyword in [
            "pan left",
            "move left",
        ]
    ):
        operations.append(
            GeoOperation(
                type="pan",
                position=GeoPoint(
                    latitude=center.latitude
                    if center
                    else 0.0,
                    longitude=(
                        center.longitude - 5
                        if center
                        else -5.0
                    ),
                ),
                duration=1.5,
            )
        )

    if any(
        keyword in text
        for keyword in [
            "pan right",
            "move right",
        ]
    ):
        operations.append(
            GeoOperation(
                type="pan",
                position=GeoPoint(
                    latitude=center.latitude
                    if center
                    else 0.0,
                    longitude=(
                        center.longitude + 5
                        if center
                        else 5.0
                    ),
                ),
                duration=1.5,
            )
        )

    if any(
        keyword in text
        for keyword in [
            "marker",
            "mark the location",
            "pin the location",
            "location marker",
        ]
    ):
        if regions:
            operations.append(
                GeoOperation(
                    type="place_marker",
                    target_id=regions[0].id,
                    duration=1.0,
                )
            )

    return GeographyPlan(
        enabled=True,
        map_source="local",
        center=center,
        zoom_level=1.0,
        regions=regions,
        operations=operations,
    )