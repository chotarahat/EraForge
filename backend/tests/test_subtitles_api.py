import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestSubtitlesAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def payload(self):
        return {
            "title": "Subtitle Test",
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
        }

    def test_subtitle_plan_endpoint(self):
        response = self.client.post(
            "/api/subtitles/plan",
            json=self.payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            len(data["cues"]),
            2,
        )

        self.assertEqual(
            data["cues"][0]["text"],
            "History begins here.",
        )

    def test_srt_endpoint(self):
        response = self.client.post(
            "/api/subtitles/srt",
            json=self.payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["cue_count"],
            2,
        )

        self.assertIn(
            "History begins here.",
            data["srt"],
        )

        self.assertIn(
            "-->",
            data["srt"],
        )

    def test_invalid_plan_is_rejected(self):
        response = self.client.post(
            "/api/subtitles/plan",
            json={
                "title": "Invalid",
                "scenes": [],
            },
        )

        self.assertEqual(
            response.status_code,
            422,
        )

    def test_subtitle_generate_endpoint(self):
        response = self.client.post(
            "/api/subtitles/generate",
            json=self.payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["cue_count"],
            2,
        )

        self.assertTrue(
            data["output_file"].endswith(
                "subtitles.srt"
            )
        )

        self.assertIn(
            "History begins here.",
            data["srt"],
        )


if __name__ == "__main__":
    unittest.main()