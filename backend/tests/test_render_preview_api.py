import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestRenderPreviewAPI(unittest.TestCase):

    def make_payload(self):
        return {
            "title": "Test History",
            "summary": "Test summary",
            "total_duration": 10,
            "aspect_ratio": "9:16",
            "style": "animated historical documentary",
            "scenes": [
                {
                    "id": "scene_1",
                    "start": 0,
                    "end": 5,
                    "title": "Opening",
                    "narration": "Opening",
                    "visual": "A map of Bangladesh",
                    "animation": "Zoom",
                    "camera": "Zoom in",
                    "caption": "Opening",
                    "location": "Bangladesh",
                    "asset_hints": ["map"],
                },
                {
                    "id": "scene_2",
                    "start": 5,
                    "end": 10,
                    "title": "Rivers",
                    "narration": "Rivers",
                    "visual": "Rivers",
                    "animation": "Fade",
                    "camera": "Static",
                    "caption": "Rivers",
                    "location": "Bangladesh",
                    "asset_hints": ["rivers"],
                },
            ],
        }

    def test_preview_endpoint(self):
        response = client.post(
            "/api/render/preview",
            json=self.make_payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["scene_count"],
            2,
        )

        self.assertEqual(
            data["width"],
            1080,
        )

        self.assertEqual(
            data["height"],
            1920,
        )

        self.assertEqual(
            len(data["scene_files"]),
            2,
        )

    def test_invalid_plan_is_rejected(self):
        payload = self.make_payload()
        payload["scenes"] = []

        response = client.post(
            "/api/render/preview",
            json=payload,
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()