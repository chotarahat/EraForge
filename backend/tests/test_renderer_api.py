import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestRendererAPI(unittest.TestCase):

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
                    "animation": "Zoom into the map",
                    "camera": "Zoom in",
                    "caption": "Bangladesh",
                    "location": "Bangladesh",
                    "asset_hints": [
                        "map",
                        "background",
                    ],
                },
                {
                    "id": "scene_2",
                    "start": 5,
                    "end": 10,
                    "title": "Character",
                    "narration": "Character",
                    "visual": "Historical portrait",
                    "animation": "Fade in",
                    "camera": "Static shot",
                    "caption": "Character",
                    "location": "Unknown",
                    "asset_hints": [
                        "character",
                    ],
                },
            ],
        }

    def test_render_plan_endpoint(self):
        response = client.post(
            "/api/render/plan",
            json=self.make_payload(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["title"],
            "Test History",
        )

        self.assertEqual(
            data["total_duration"],
            10,
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
            data["fps"],
            30,
        )

        self.assertEqual(
            len(data["scenes"]),
            2,
        )

        self.assertEqual(
            data["scenes"][0]["scene_id"],
            "scene_1",
        )

    def test_invalid_scene_plan_is_rejected(self):
        payload = self.make_payload()
        payload["scenes"] = []

        response = client.post(
            "/api/render/plan",
            json=payload,
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()