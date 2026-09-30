from pathlib import Path
import wave

from pydantic import BaseModel, Field

from app.models import ScenePlan


class NarrationSegment(BaseModel):
    scene_id: str
    text: str
    audio_file: str | None = None
    duration_seconds: float = Field(default=0.0, ge=0)


class NarrationPlan(BaseModel):
    segments: list[NarrationSegment] = Field(default_factory=list)


class NarrationManifestSegment(BaseModel):
    scene_id: str
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    text: str
    audio_file: str | None = None
    audio_duration: float = Field(default=0.0, ge=0)
    fits_scene: bool = True


class NarrationManifest(BaseModel):
    segments: list[NarrationManifestSegment] = Field(
        default_factory=list
    )


class NarrationSettings(BaseModel):
    voice: str | None = None
    rate: int = Field(default=170, ge=80, le=300)
    volume: float = Field(default=1.0, ge=0.0, le=1.0)


def build_narration_plan(plan: ScenePlan) -> NarrationPlan:
    segments = []

    for scene in plan.scenes:
        text = (scene.narration or "").strip()

        if not text:
            continue

        segments.append(
            NarrationSegment(
                scene_id=scene.id,
                text=text,
            )
        )

    return NarrationPlan(segments=segments)


def build_narration_manifest(
    plan: ScenePlan,
    narration: NarrationPlan,
) -> NarrationManifest:
    narration_by_scene = {
        segment.scene_id: segment
        for segment in narration.segments
    }

    segments: list[NarrationManifestSegment] = []

    for scene in plan.scenes:
        segment = narration_by_scene.get(scene.id)

        if segment is None:
            continue

        scene_duration = scene.end - scene.start

        segments.append(
            NarrationManifestSegment(
                scene_id=scene.id,
                start=scene.start,
                end=scene.end,
                text=segment.text,
                audio_file=segment.audio_file,
                audio_duration=segment.duration_seconds,
                fits_scene=(
                    segment.duration_seconds <= scene_duration
                ),
            )
        )

    return NarrationManifest(segments=segments)


def _wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()

    if rate <= 0:
        return 0.0

    return frames / float(rate)


class LocalTTS:
    def __init__(self, settings: NarrationSettings | None = None):
        self.settings = settings or NarrationSettings()

    def list_voices(self) -> list[dict[str, str]]:
        import pyttsx3

        engine = pyttsx3.init()

        try:
            voices = []

            for voice in engine.getProperty("voices") or []:
                voices.append(
                    {
                        "id": str(getattr(voice, "id", "")),
                        "name": str(getattr(voice, "name", "")),
                    }
                )

            return voices
        finally:
            engine.stop()

    def synthesize(self, text: str, output_path: Path) -> float:
        import pyttsx3

        text = text.strip()

        if not text:
            raise ValueError("Narration text cannot be empty")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        engine = pyttsx3.init()

        try:
            engine.setProperty(
                "rate",
                self.settings.rate,
            )

            engine.setProperty(
                "volume",
                self.settings.volume,
            )

            if self.settings.voice:
                engine.setProperty(
                    "voice",
                    self.settings.voice,
                )

            engine.save_to_file(
                text,
                str(output_path),
            )

            engine.runAndWait()
        finally:
            engine.stop()

        if not output_path.exists():
            raise RuntimeError(
                f"TTS engine did not create output file: {output_path}"
            )

        duration = _wav_duration(output_path)

        if duration <= 0:
            raise RuntimeError(
                f"Generated narration has invalid duration: {output_path}"
            )

        return duration


def generate_narration(
    narration_plan: NarrationPlan,
    output_root: str = "backend/outputs/narration",
    settings: NarrationSettings | None = None,
) -> NarrationPlan:
    output_dir = Path(output_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    tts = LocalTTS(settings)

    generated_segments: list[NarrationSegment] = []

    for index, segment in enumerate(narration_plan.segments, start=1):
        safe_scene_id = "".join(
            char if char.isalnum() or char in "-_" else "_"
            for char in segment.scene_id
        )

        filename = f"scene_{index:03d}_{safe_scene_id}.wav"
        output_path = output_dir / filename

        duration = tts.synthesize(
            segment.text,
            output_path,
        )

        generated_segments.append(
            NarrationSegment(
                scene_id=segment.scene_id,
                text=segment.text,
                audio_file=str(output_path),
                duration_seconds=duration,
            )
        )

    return NarrationPlan(segments=generated_segments)