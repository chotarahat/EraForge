import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestGeographyAPI(unittest.TestCase):

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
                    "title": "Bangladesh",
                    "narration": "Bangladesh",
                    "visual": "A map of Bangladesh",
                    "animation": "Zoom",
                    "camera": "Wide",
                    "caption": "Bangladesh",
                    "location": "Bangladesh",
                    "asset_hints": ["map"],
                },
                {
                    "id": "scene_2",
                    "start": 5,
                    "end": 10,
                    "title": "Portrait",
                    "narration": "Portrait",
                    "visual": "Historical portrait",
                    "animation": "Fade",
                    "camera": "Close",
                    "caption": "Portrait",
                    "location": "Unknown",
                    "asset_hints": ["character"],
                },
            ],
        }

    def test_geography_plan_endpoint(self):
        response = client.post(
            "/api/geography/plan",
            json=self.make_payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertIn(
            "scene_1",
            data,
        )

        self.assertIn(
            "scene_2",
            data,
        )

        self.assertTrue(
            data["scene_1"]["enabled"]
        )

        self.assertFalse(
            data["scene_2"]["enabled"]
        )

    def test_invalid_scene_plan_is_rejected(self):
        payload = self.make_payload()
        payload["scenes"] = []

        response = client.post(
            "/api/geography/plan",
            json=payload,
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()