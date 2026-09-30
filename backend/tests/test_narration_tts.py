import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.narration import (
    LocalTTS,
    NarrationPlan,
    NarrationSegment,
    NarrationSettings,
    generate_narration,
)


def create_test_wav(path: Path, duration: float = 1.0):
    sample_rate = 16000
    frames = int(sample_rate * duration)

    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(b"\x00\x00" * frames)


class FakeEngine:
    def __init__(self):
        self.properties = {}

    def getProperty(self, name):
        if name == "voices":
            return [
                SimpleNamespace(
                    id="voice-1",
                    name="Test Voice",
                ),
                SimpleNamespace(
                    id="voice-2",
                    name="Second Voice",
                ),
            ]

        return None

    def setProperty(self, name, value):
        self.properties[name] = value

    def save_to_file(self, text, path):
        create_test_wav(Path(path), duration=1.5)

    def runAndWait(self):
        return None

    def stop(self):
        return None


class TestLocalTTS(unittest.TestCase):
    @patch("pyttsx3.init")
    def test_list_voices(self, mock_init):
        mock_init.return_value = FakeEngine()

        tts = LocalTTS()

        voices = tts.list_voices()

        self.assertEqual(len(voices), 2)
        self.assertEqual(voices[0]["id"], "voice-1")
        self.assertEqual(voices[0]["name"], "Test Voice")

    @patch("pyttsx3.init")
    def test_synthesize_creates_wav(self, mock_init):
        mock_init.return_value = FakeEngine()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "scene.wav"

            settings = NarrationSettings(
                voice="voice-1",
                rate=180,
                volume=0.8,
            )

            tts = LocalTTS(settings)

            duration = tts.synthesize(
                "This is a test narration.",
                output_path,
            )

            self.assertTrue(output_path.exists())
            self.assertGreater(duration, 0)
            self.assertAlmostEqual(duration, 1.5, places=1)

            engine = mock_init.return_value

            self.assertEqual(
                engine.properties["voice"],
                "voice-1",
            )
            self.assertEqual(
                engine.properties["rate"],
                180,
            )
            self.assertEqual(
                engine.properties["volume"],
                0.8,
            )

    @patch("pyttsx3.init")
    def test_generate_narration(self, mock_init):
        mock_init.return_value = FakeEngine()

        narration_plan = NarrationPlan(
            segments=[
                NarrationSegment(
                    scene_id="scene_1",
                    text="The first narration.",
                ),
                NarrationSegment(
                    scene_id="scene_2",
                    text="The second narration.",
                ),
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_narration(
                narration_plan,
                output_root=temp_dir,
            )

            self.assertEqual(len(result.segments), 2)

            for index, segment in enumerate(
                result.segments,
                start=1,
            ):
                self.assertEqual(
                    segment.scene_id,
                    f"scene_{index}",
                )
                self.assertTrue(segment.audio_file)
                self.assertGreater(
                    segment.duration_seconds,
                    0,
                )

                self.assertTrue(
                    Path(segment.audio_file).exists()
                )

    @patch("pyttsx3.init")
    def test_missing_output_file_raises_error(self, mock_init):
        class BrokenEngine(FakeEngine):
            def save_to_file(self, text, path):
                return None

        mock_init.return_value = BrokenEngine()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "missing.wav"

            tts = LocalTTS()

            with self.assertRaises(RuntimeError):
                tts.synthesize(
                    "This should fail.",
                    output_path,
                )


if __name__ == "__main__":
    unittest.main()