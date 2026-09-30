import unittest
from unittest.mock import patch

from app.video_export import (
    VideoExportSettings,
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


if __name__ == "__main__":
    unittest.main()