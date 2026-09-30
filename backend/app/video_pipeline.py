from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.frame_renderer import render_plan_frames
from app.renderer_planner import build_render_plan
from app.video_export import (
    VideoExportResult,
    VideoExportSettings,
    export_mp4,
)


class RenderVideoResult:
    def __init__(
        self,
        video: VideoExportResult,
        frame_count: int,
        frame_directory: str,
    ):
        self.video = video
        self.frame_count = frame_count
        self.frame_directory = frame_directory

    def model_dump(self) -> dict:
        return {
            "output_file": self.video.output_file,
            "duration": self.video.duration,
            "width": self.video.width,
            "height": self.video.height,
            "fps": self.video.fps,
            "frame_count": self.frame_count,
            "frame_directory": self.frame_directory,
        }


def export_render_plan(
    plan,
    settings: VideoExportSettings | None = None,
    output_root: str = "outputs/video_export",
) -> RenderVideoResult:
    render_plan = build_render_plan(plan)

    settings = settings or VideoExportSettings(
        fps=render_plan.fps
    )

    job_id = uuid4().hex[:12]

    root = Path(output_root)
    frame_directory = root / "frames" / job_id
    video_directory = root / "videos"

    frame_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    video_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame_files = render_plan_frames(
        render_plan,
        output_root=str(frame_directory),
    )

    if not frame_files:
        raise RuntimeError(
            "No video frames were generated."
        )

    frame_pattern = (
        frame_directory / "frame_%06d.png"
    )

    output_file = (
        video_directory
        / f"eraforge_{job_id}.mp4"
    )

    video = export_mp4(
        image_sequence=str(frame_pattern),
        output_file=str(output_file),
        width=render_plan.width,
        height=render_plan.height,
        fps=render_plan.fps,
        settings=settings,
    )

    return RenderVideoResult(
        video=video,
        frame_count=len(frame_files),
        frame_directory=str(frame_directory),
    )