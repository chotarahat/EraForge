from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_allowed_origins() -> list[str]:
    raw = os.environ.get(
        "ERAFORGE_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    return [
        origin.strip()
        for origin in raw.split(",")
        if origin.strip()
    ]


def get_allowed_hosts() -> list[str]:
    raw = os.environ.get(
        "ERAFORGE_ALLOWED_HOSTS",
        "localhost,127.0.0.1,testserver",
    )

    return [
        host.strip()
        for host in raw.split(",")
        if host.strip()
    ]


def get_docs_enabled() -> bool:
    return os.environ.get(
        "ERAFORGE_ENABLE_DOCS",
        "true",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
def get_max_request_bytes() -> int:
    raw = os.environ.get(
        "ERAFORGE_MAX_REQUEST_BYTES",
        str(10 * 1024 * 1024),
    )

    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(
            "ERAFORGE_MAX_REQUEST_BYTES must be an integer."
        ) from exc

    if value <= 0:
        raise ValueError(
            "ERAFORGE_MAX_REQUEST_BYTES must be greater than zero."
        )

    return value