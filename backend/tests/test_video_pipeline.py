import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.video_export import (
    VideoExportResult,
    VideoExportSettings,
)
from app.video_pipeline import (
    export_render_plan,
)


def make_plan():
    from app.models import Scene, ScenePlan

    return ScenePlan(
        title="Video Export Test",
        summary="Video export pipeline test.",
        total_duration=2,
        aspect_ratio="9:16",
        style="documentary",
        scenes=[
            Scene(
                id="scene_1",
                title="Opening",
                start=0,
                end=1,
                narration="Opening scene.",
                caption="Opening",
                visual="Historical scene",
                animation="Fade in",
                camera="Static",
                location="",
                asset_hints=[],
            ),
            Scene(
                id="scene_2",
                title="Second",
                start=1,
                end=2,
                narration="Second scene.",
                caption="Second",
                visual="Historical scene",
                animation="Fade in",
                camera="Static",
                location="",
                asset_hints=[],
            ),
        ],
    )


class TestVideoPipeline(unittest.TestCase):
    @patch("app.video_pipeline.export_mp4")
    @patch("app.video_pipeline.render_plan_frames")
    def test_export_render_plan(
        self,
        mock_frames,
        mock_export,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_dir = Path(temp_dir) / "frames"

            frame_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            frame_1 = frame_dir / "frame_000001.png"
            frame_2 = frame_dir / "frame_000002.png"

            frame_1.write_bytes(b"frame1")
            frame_2.write_bytes(b"frame2")

            mock_frames.return_value = [
                str(frame_1),
                str(frame_2),
            ]

            mock_export.return_value = (
                VideoExportResult(
                    output_file=(
                        f"{temp_dir}/video.mp4"
                    ),
                    duration=2.0,
                    width=1080,
                    height=1920,
                    fps=30,
                )
            )

            result = export_render_plan(
                make_plan(),
                output_root=temp_dir,
            )

            self.assertEqual(
                result.frame_count,
                2,
            )

            self.assertEqual(
                result.video.width,
                1080,
            )

            self.assertEqual(
                result.video.height,
                1920,
            )

            mock_frames.assert_called_once()

            mock_export.assert_called_once()

    @patch("app.video_pipeline.export_mp4")
    @patch("app.video_pipeline.render_plan_frames")
    def test_custom_settings_are_passed(
        self,
        mock_frames,
        mock_export,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_dir = (
                Path(temp_dir) / "frames"
            )

            frame_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            frame_file = (
                frame_dir / "frame_000001.png"
            )

            frame_file.write_bytes(
                b"frame"
            )

            mock_frames.return_value = [
                str(frame_file)
            ]

            mock_export.return_value = (
                VideoExportResult(
                    output_file=(
                        f"{temp_dir}/video.mp4"
                    ),
                    duration=1.0,
                    width=1080,
                    height=1920,
                    fps=60,
                )
            )

            settings = VideoExportSettings(
                fps=60,
                crf=20,
            )

            export_render_plan(
                make_plan(),
                settings=settings,
                output_root=temp_dir,
            )

            call = mock_export.call_args

            self.assertEqual(
                call.kwargs["fps"],
                30,
            )

            self.assertEqual(
                call.kwargs["settings"],
                settings,
            )

    @patch("app.video_pipeline.render_plan_frames")
    def test_no_frames_raises_error(
        self,
        mock_frames,
    ):
        mock_frames.return_value = []

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(RuntimeError):
                export_render_plan(
                    make_plan(),
                    output_root=temp_dir,
                )


if __name__ == "__main__":
    unittest.main()