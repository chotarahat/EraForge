import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.narration import NarrationPlan, NarrationSegment


class TestNarrationAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def sample_payload(self):
        return {
            "title": "Test History",
            "summary": "A short historical test story.",
            "total_duration": 5,
            "aspect_ratio": "9:16",
            "style": "documentary",
            "scenes": [
                {
                    "id": "scene_1",
                    "title": "Opening",
                    "start": 0,
                    "end": 5,
                    "narration": "History begins here.",
                    "caption": "History begins.",
                    "visual": "Historical scene",
                    "animation": "Fade in",
                    "camera": "Static",
                    "location": "Bangladesh",
                    "asset_hints": [],
                }
            ],
        }

    def test_narration_plan_endpoint(self):
        response = self.client.post(
            "/api/narration/plan",
            json=self.sample_payload(),
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data["segments"]), 1)
        self.assertEqual(
            data["segments"][0]["scene_id"],
            "scene_1",
        )

    @patch("app.main.generate_narration")
    def test_narration_generate_endpoint(self, mock_generate):
        mock_generate.return_value = NarrationPlan(
            segments=[
                NarrationSegment(
                    scene_id="scene_1",
                    text="History begins here.",
                    audio_file=(
                        "backend/outputs/narration/"
                        "scene_001_scene_1.wav"
                    ),
                    duration_seconds=2.5,
                )
            ]
        )

        response = self.client.post(
            "/api/narration/generate",
            json=self.sample_payload(),
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data["segments"]), 1)
        self.assertEqual(
            data["segments"][0]["audio_file"],
            "backend/outputs/narration/scene_001_scene_1.wav",
        )

        mock_generate.assert_called_once()

    def test_invalid_scene_plan_is_rejected(self):
        response = self.client.post(
            "/api/narration/plan",
            json={
                "title": "Invalid",
                "summary": "",
                "total_duration": 0,
                "aspect_ratio": "9:16",
                "style": "documentary",
                "scenes": [],
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()