import tempfile
import unittest
from pathlib import Path

from app.subtitles import (
    SubtitleTrack,
    SubtitleCue,
    write_srt_file,
)


class TestSubtitleFile(unittest.TestCase):
    def test_write_srt_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = (
                Path(temp_dir) / "subtitles.srt"
            )

            track = SubtitleTrack(
                cues=[
                    SubtitleCue(
                        index=1,
                        start=0,
                        end=2,
                        text="Hello EraForge.",
                    )
                ]
            )

            result = write_srt_file(
                track,
                str(output_path),
            )

            self.assertEqual(
                result,
                str(output_path),
            )

            self.assertTrue(
                output_path.exists()
            )

            content = output_path.read_text(
                encoding="utf-8"
            )

            self.assertIn(
                "Hello EraForge.",
                content,
            )

    def test_empty_track_creates_empty_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = (
                Path(temp_dir) / "empty.srt"
            )

            write_srt_file(
                SubtitleTrack(),
                str(output_path),
            )

            self.assertTrue(
                output_path.exists()
            )

            self.assertEqual(
                output_path.read_text(
                    encoding="utf-8"
                ),
                "",
            )


if __name__ == "__main__":
    unittest.main()