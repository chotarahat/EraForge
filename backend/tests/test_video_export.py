import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.video_export import (
    VideoExportSettings,
    build_ffmpeg_command,
    export_mp4,
    get_ffmpeg_path,
)


class TestVideoExport(unittest.TestCase):
    def test_default_settings(self):
        settings = VideoExportSettings()

        self.assertEqual(
            settings.fps,
            30,
        )

        self.assertEqual(
            settings.video_codec,
            "libx264",
        )

        self.assertEqual(
            settings.pixel_format,
            "yuv420p",
        )

        self.assertEqual(
            settings.crf,
            23,
        )

    def test_custom_settings(self):
        settings = VideoExportSettings(
            fps=60,
            video_codec="libx265",
            pixel_format="yuv420p",
            crf=20,
        )

        self.assertEqual(
            settings.fps,
            60,
        )

        self.assertEqual(
            settings.video_codec,
            "libx265",
        )

        self.assertEqual(
            settings.crf,
            20,
        )

    @patch(
        "app.video_export.shutil.which",
        return_value="ffmpeg",
    )
    def test_ffmpeg_path(self, mock_which):
        path = get_ffmpeg_path()

        self.assertEqual(
            path,
            "ffmpeg",
        )

        mock_which.assert_called_once_with(
            "ffmpeg"
        )

    @patch(
        "app.video_export.shutil.which",
        return_value=None,
    )
    def test_ffmpeg_missing(self, mock_which):
        with self.assertRaises(RuntimeError):
            get_ffmpeg_path()

    @patch(
        "app.video_export.get_ffmpeg_path",
        return_value="ffmpeg",
    )
    def test_build_ffmpeg_command(self, mock_path):
        settings = VideoExportSettings(
            fps=30,
            video_codec="libx264",
            pixel_format="yuv420p",
            crf=23,
        )

        command = build_ffmpeg_command(
            "outputs/video_frames/frame_%06d.png",
            "outputs/videos/test.mp4",
            settings,
        )

        self.assertEqual(
            command[0],
            "ffmpeg",
        )

        self.assertIn(
            "-framerate",
            command,
        )

        self.assertIn(
            "30",
            command,
        )

        self.assertIn(
            "-i",
            command,
        )

        self.assertIn(
            "outputs/video_frames/frame_%06d.png",
            command,
        )

        self.assertIn(
            "outputs/videos/test.mp4",
            command,
        )

        mock_path.assert_called_once()

    def test_invalid_sequence_pattern(self):
        with self.assertRaises(ValueError):
            export_mp4(
                image_sequence="frame.png",
                output_file="test.mp4",
                width=320,
                height=480,
            )

    @patch(
        "app.video_export.subprocess.run"
    )
    @patch(
        "app.video_export.get_ffmpeg_path",
        return_value="ffmpeg",
    )
    def test_export_mp4(
        self,
        mock_path,
        mock_run,
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = (
                Path(temp_dir)
                / "test.mp4"
            )

            output_path.write_bytes(
                b"fake mp4"
            )

            result = export_mp4(
                image_sequence=(
                    str(
                        Path(temp_dir)
                        / "frame_%06d.png"
                    )
                ),
                output_file=str(output_path),
                width=320,
                height=480,
                fps=2,
            )

            self.assertEqual(
                result.output_file,
                str(output_path),
            )

            self.assertEqual(
                result.width,
                320,
            )

            self.assertEqual(
                result.height,
                480,
            )

            self.assertEqual(
                result.fps,
                2,
            )

            mock_run.assert_called_once()