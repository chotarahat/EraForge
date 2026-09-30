import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestNarrationManifestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def payload(self):
        return {
            "plan": {
                "title": "Test History",
                "summary": "Narration test",
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
                        "location": "",
                        "asset_hints": [],
                    }
                ],
            },
            "narration": {
                "segments": [
                    {
                        "scene_id": "scene_1",
                        "text": "History begins here.",
                        "audio_file": (
                            "outputs/narration/scene_001_scene_1.wav"
                        ),
                        "duration_seconds": 2.5,
                    }
                ]
            },
        }

    def test_manifest_endpoint(self):
        response = self.client.post(
            "/api/narration/manifest",
            json=self.payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            len(data["segments"]),
            1,
        )

        self.assertEqual(
            data["segments"][0]["scene_id"],
            "scene_1",
        )

        self.assertTrue(
            data["segments"][0]["fits_scene"]
        )

    def test_invalid_manifest_request(self):
        response = self.client.post(
            "/api/narration/manifest",
            json={
                "plan": {
                    "title": "Invalid",
                    "scenes": [],
                },
                "narration": {
                    "segments": []
                },
            },
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()