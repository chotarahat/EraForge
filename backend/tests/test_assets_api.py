import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestAssetsAPI(unittest.TestCase):

    def test_asset_plan_endpoint(self):
        payload = {
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
                    "visual": "A map of South Asia",
                    "animation": "Fade in",
                    "camera": "Wide shot",
                    "caption": "Opening",
                    "location": "South Asia",
                    "asset_hints": [
                        "map",
                        "mountains",
                    ],
                },
                {
                    "id": "scene_2",
                    "start": 5,
                    "end": 10,
                    "title": "Rivers",
                    "narration": "Rivers",
                    "visual": "Rivers flowing",
                    "animation": "Pan",
                    "camera": "Wide shot",
                    "caption": "Rivers",
                    "location": "South Asia",
                    "asset_hints": [
                        "map",
                        "rivers",
                    ],
                },
            ],
        }

        response = client.post(
            "/api/assets/plan",
            json=payload,
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data), 3)

        names = {asset["name"] for asset in data}

        self.assertEqual(
            names,
            {"map", "mountains", "rivers"},
        )

    def test_invalid_scene_plan_is_rejected(self):
        payload = {
            "title": "Invalid",
            "summary": "Invalid",
            "total_duration": 10,
            "aspect_ratio": "9:16",
            "style": "animated historical documentary",
            "scenes": [],
        }

        response = client.post(
            "/api/assets/plan",
            json=payload,
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()