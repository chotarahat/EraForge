from __future__ import annotations

from pathlib import Path
import re

from pydantic import BaseModel, Field

from app.models import ScenePlan
from app.narration import NarrationManifest


class SubtitleCue(BaseModel):
    index: int = Field(ge=1)
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    text: str = Field(min_length=1)

    def model_post_init(self, __context) -> None:
        if self.end <= self.start:
            raise ValueError(
                "Subtitle cue end must be greater than start"
            )


class SubtitleTrack(BaseModel):
    cues: list[SubtitleCue] = Field(
        default_factory=list
    )


class SubtitleSyncIssue(BaseModel):
    scene_id: str | None = None
    type: str
    message: str


class SubtitleSyncReport(BaseModel):
    valid: bool
    issues: list[SubtitleSyncIssue] = Field(
        default_factory=list
    )


def split_sentences(text: str) -> list[str]:
    text = re.sub(
        r"\s+",
        " ",
        text.strip(),
    )

    if not text:
        return []

    parts = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def _allocate_duration(
    texts: list[str],
    total_duration: float,
) -> list[float]:
    if not texts:
        return []

    weights = [
        max(len(text), 1)
        for text in texts
    ]

    total_weight = sum(weights)

    return [
        total_duration * weight / total_weight
        for weight in weights
    ]


def _scene_narration_duration(
    scene_id: str,
    scene_duration: float,
    narration_manifest: NarrationManifest | None,
) -> float:
    if narration_manifest is None:
        return scene_duration

    for segment in narration_manifest.segments:
        if segment.scene_id != scene_id:
            continue

        if segment.audio_duration <= 0:
            return scene_duration

        return min(
            segment.audio_duration,
            scene_duration,
        )

    return scene_duration


def build_subtitle_track(
    plan: ScenePlan,
    narration_manifest: NarrationManifest | None = None,
) -> SubtitleTrack:
    cues: list[SubtitleCue] = []
    cue_index = 1

    for scene in plan.scenes:
        narration = (
            scene.narration or ""
        ).strip()

        if not narration:
            continue

        sentences = split_sentences(
            narration
        )

        if not sentences:
            continue

        scene_duration = scene.end - scene.start

        subtitle_duration = _scene_narration_duration(
            scene.id,
            scene_duration,
            narration_manifest,
        )

        durations = _allocate_duration(
            sentences,
            subtitle_duration,
        )

        current_time = scene.start

        for text, duration in zip(
            sentences,
            durations,
        ):
            cue_end = current_time + duration

            cues.append(
                SubtitleCue(
                    index=cue_index,
                    start=round(
                        current_time,
                        3,
                    ),
                    end=round(
                        cue_end,
                        3,
                    ),
                    text=text,
                )
            )

            cue_index += 1
            current_time = cue_end

    return SubtitleTrack(cues=cues)


def validate_subtitle_track(
    plan: ScenePlan,
    track: SubtitleTrack,
) -> SubtitleSyncReport:
    issues: list[SubtitleSyncIssue] = []

    previous_end = 0.0

    for cue in track.cues:
        if cue.start < previous_end:
            issues.append(
                SubtitleSyncIssue(
                    type="overlap",
                    message=(
                        f"Subtitle cue {cue.index} overlaps "
                        "the previous cue."
                    ),
                )
            )

        if cue.end <= cue.start:
            issues.append(
                SubtitleSyncIssue(
                    type="invalid_timing",
                    message=(
                        f"Subtitle cue {cue.index} "
                        "has invalid timing."
                    ),
                )
            )

        matching_scene = None

        for scene in plan.scenes:
            if (
                cue.start >= scene.start
                and cue.end <= scene.end
            ):
                matching_scene = scene
                break

        if matching_scene is None:
            issues.append(
                SubtitleSyncIssue(
                    type="outside_scene",
                    message=(
                        f"Subtitle cue {cue.index} "
                        "falls outside scene timing."
                    ),
                )
            )
        else:
            narration = (
                matching_scene.narration or ""
            ).strip()

            if not narration:
                issues.append(
                    SubtitleSyncIssue(
                        scene_id=matching_scene.id,
                        type="missing_narration",
                        message=(
                            f"Scene {matching_scene.id} "
                            "has subtitles but no narration."
                        ),
                    )
                )

        previous_end = max(
            previous_end,
            cue.end,
        )

    return SubtitleSyncReport(
        valid=not issues,
        issues=issues,
    )


def format_srt_timestamp(
    seconds: float,
) -> str:
    milliseconds = round(
        seconds * 1000
    )

    hours = (
        milliseconds
        // 3_600_000
    )

    milliseconds %= 3_600_000

    minutes = (
        milliseconds
        // 60_000
    )

    milliseconds %= 60_000

    secs = (
        milliseconds
        // 1000
    )

    milliseconds %= 1000

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{milliseconds:03d}"
    )


def subtitle_track_to_srt(
    track: SubtitleTrack,
) -> str:
    blocks: list[str] = []

    for cue in track.cues:
        blocks.append(
            "\n".join(
                [
                    str(cue.index),
                    (
                        f"{format_srt_timestamp(cue.start)}"
                        " --> "
                        f"{format_srt_timestamp(cue.end)}"
                    ),
                    cue.text,
                ]
            )
        )

    if not blocks:
        return ""

    return "\n\n".join(blocks) + "\n"


def write_srt_file(
    track: SubtitleTrack,
    output_path: str = (
        "outputs/subtitles/subtitles.srt"
    ),
) -> str:
    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        subtitle_track_to_srt(track),
        encoding="utf-8",
    )

    return str(path)