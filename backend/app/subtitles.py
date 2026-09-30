from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field

from app.models import ScenePlan


class SubtitleCue(BaseModel):
    index: int = Field(ge=1)
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    text: str = Field(min_length=1)

    def model_post_init(self, __context) -> None:
        if self.end <= self.start:
            raise ValueError("Subtitle cue end must be greater than start")


class SubtitleTrack(BaseModel):
    cues: list[SubtitleCue] = Field(default_factory=list)


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())

    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+", text)

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

    weights = [max(len(text), 1) for text in texts]
    total_weight = sum(weights)

    return [
        total_duration * weight / total_weight
        for weight in weights
    ]


def build_subtitle_track(
    plan: ScenePlan,
) -> SubtitleTrack:
    cues: list[SubtitleCue] = []
    cue_index = 1

    for scene in plan.scenes:
        narration = (scene.narration or "").strip()

        if not narration:
            continue

        sentences = split_sentences(narration)

        if not sentences:
            continue

        scene_duration = scene.end - scene.start
        durations = _allocate_duration(
            sentences,
            scene_duration,
        )

        current_time = scene.start

        for text, duration in zip(sentences, durations):
            cue_end = current_time + duration

            cues.append(
                SubtitleCue(
                    index=cue_index,
                    start=round(current_time, 3),
                    end=round(cue_end, 3),
                    text=text,
                )
            )

            cue_index += 1
            current_time = cue_end

    return SubtitleTrack(cues=cues)


def format_srt_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    secs = milliseconds // 1000
    milliseconds %= 1000

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{milliseconds:03d}"
    )


def subtitle_track_to_srt(track: SubtitleTrack) -> str:
    blocks: list[str] = []

    for cue in track.cues:
        blocks.append(
            "\n".join(
                [
                    str(cue.index),
                    (
                        f"{format_srt_timestamp(cue.start)}"
                        f" --> "
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
    output_path: str = "backend/outputs/subtitles/subtitles.srt",
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