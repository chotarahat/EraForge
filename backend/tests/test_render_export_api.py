import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.video_pipeline import RenderVideoResult
from app.video_export import VideoExportResult


class TestRenderExportAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def payload(self):
        return {
            "title": "Render Export Test",
            "summary": "MP4 export test.",
            "total_duration": 2,
            "aspect_ratio": "9:16",
            "style": "documentary",
            "scenes": [
                {
                    "id": "scene_1",
                    "title": "Opening",
                    "start": 0,
                    "end": 2,
                    "narration": "Opening scene.",
                    "caption": "Opening",
                    "visual": "Historical scene",
                    "animation": "Fade in",
                    "camera": "Static",
                    "location": "",
                    "asset_hints": [],
                }
            ],
        }

    @patch("app.main.export_render_plan")
    def test_render_export_endpoint(
        self,
        mock_export,
    ):
        mock_export.return_value = (
            RenderVideoResult(
                video=VideoExportResult(
                    output_file=(
                        "outputs/video_export/videos/"
                        "eraforge_test.mp4"
                    ),
                    duration=2.0,
                    width=1080,
                    height=1920,
                    fps=30,
                ),
                frame_count=60,
                frame_directory=(
                    "outputs/video_export/frames/test"
                ),
            )
        )

        response = self.client.post(
            "/api/render/export",
            json=self.payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["width"],
            1080,
        )

        self.assertEqual(
            data["height"],
            1920,
        )

        self.assertEqual(
            data["fps"],
            30,
        )

        self.assertEqual(
            data["frame_count"],
            60,
        )

        mock_export.assert_called_once()

    def test_invalid_plan_is_rejected(self):
        response = self.client.post(
            "/api/render/export",
            json={
                "title": "Invalid",
                "scenes": [],
            },
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()