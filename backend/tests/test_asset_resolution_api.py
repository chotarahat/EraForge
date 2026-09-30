import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestAssetResolutionAPI(unittest.TestCase):

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
                    "visual": "A map",
                    "animation": "Fade",
                    "camera": "Wide",
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
                    "visual": "Rivers",
                    "animation": "Pan",
                    "camera": "Wide",
                    "caption": "Rivers",
                    "location": "South Asia",
                    "asset_hints": [
                        "rivers",
                    ],
                },
            ],
        }

    def test_resolution_endpoint(self):
        response = client.post(
            "/api/assets/resolve",
            json=self.make_payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertIn("resolved", data)
        self.assertIn("missing", data)
        self.assertIn("placeholders", data)

        self.assertEqual(
            len(data["resolved"]),
            0,
        )

        self.assertEqual(
            len(data["missing"]),
            3,
        )
        self.assertEqual(
            len(data["placeholders"]),
            3,
        )

        self.assertTrue(
            all(
                asset["status"] == "placeholder"
                for asset in data["placeholders"]
            )
        )

    def test_invalid_scene_plan_is_rejected(self):
        payload = self.make_payload()

        payload["scenes"] = []

        response = client.post(
            "/api/assets/resolve",
            json=payload,
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()