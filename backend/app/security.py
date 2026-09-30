from __future__ import annotations

import os


def get_allowed_origins() -> list[str]:
    raw = os.getenv(
        "ERAFORGE_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    origins = [
        origin.strip()
        for origin in raw.split(",")
        if origin.strip()
    ]

    return origins


def get_docs_enabled() -> bool:
    return os.getenv(
        "ERAFORGE_ENABLE_DOCS",
        "true",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }