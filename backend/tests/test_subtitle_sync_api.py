import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestSubtitleSyncAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def payload(self):
        return {
            "plan": {
                "title": "Subtitle Sync",
                "summary": "Subtitle synchronization test",
                "total_duration": 5,
                "aspect_ratio": "9:16",
                "style": "documentary",
                "scenes": [
                    {
                        "id": "scene_1",
                        "title": "Opening",
                        "start": 0,
                        "end": 5,
                        "narration": (
                            "History begins here. "
                            "The story continues."
                        ),
                        "caption": "Opening",
                        "visual": "Historical scene",
                        "animation": "Fade in",
                        "camera": "Static",
                        "location": "",
                        "asset_hints": [],
                    }
                ],
            },
            "narration_manifest": {
                "segments": [
                    {
                        "scene_id": "scene_1",
                        "start": 0,
                        "end": 5,
                        "text": (
                            "History begins here. "
                            "The story continues."
                        ),
                        "audio_file": "scene_1.wav",
                        "audio_duration": 3.0,
                        "fits_scene": True,
                    }
                ]
            },
        }

    def test_sync_endpoint(self):
        response = self.client.post(
            "/api/subtitles/sync",
            json=self.payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertTrue(
            data["valid"]
        )

        self.assertEqual(
            data["issues"],
            [],
        )

    def test_sync_without_manifest(self):
        payload = self.payload()

        payload["narration_manifest"] = None

        response = self.client.post(
            "/api/subtitles/sync",
            json=payload,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            response.json()["valid"]
        )

    def test_invalid_sync_request(self):
        response = self.client.post(
            "/api/subtitles/sync",
            json={
                "plan": {
                    "title": "Invalid",
                    "scenes": [],
                }
            },
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()