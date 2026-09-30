from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field


class VideoExportSettings(BaseModel):
    fps: int = Field(default=30, ge=1, le=120)
    video_codec: str = "libx264"
    pixel_format: str = "yuv420p"
    crf: int = Field(default=23, ge=0, le=51)


class VideoExportResult(BaseModel):
    output_file: str
    duration: float = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    fps: int = Field(gt=0)


def get_ffmpeg_path() -> str:
    path = shutil.which("ffmpeg")

    if not path:
        raise RuntimeError(
            "FFmpeg was not found on PATH."
        )

    return path


def build_ffmpeg_command(
    image_sequence: str,
    output_file: str,
    settings: VideoExportSettings,
) -> list[str]:
    ffmpeg = get_ffmpeg_path()

    return [
        ffmpeg,
        "-y",
        "-framerate",
        str(settings.fps),
        "-i",
        image_sequence,
        "-c:v",
        settings.video_codec,
        "-pix_fmt",
        settings.pixel_format,
        "-crf",
        str(settings.crf),
        "-movflags",
        "+faststart",
        output_file,
    ]


def export_mp4(
    image_sequence: str,
    output_file: str,
    width: int,
    height: int,
    fps: int = 30,
    settings: VideoExportSettings | None = None,
) -> VideoExportResult:
    settings = settings or VideoExportSettings(
        fps=fps
    )

    input_pattern = Path(image_sequence)

    if "%" not in input_pattern.name:
        raise ValueError(
            "image_sequence must be an FFmpeg sequence pattern "
            "such as frame_%06d.png"
        )

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = build_ffmpeg_command(
        image_sequence=image_sequence,
        output_file=str(output_path),
        settings=settings,
    )

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        raise RuntimeError(
            "FFmpeg export failed:\n"
            + process.stderr
        )

    if not output_path.exists():
        raise RuntimeError(
            "FFmpeg completed without creating output."
        )

    return VideoExportResult(
        output_file=str(output_path),
        duration=0.0,
        width=width,
        height=height,
        fps=settings.fps,
    )