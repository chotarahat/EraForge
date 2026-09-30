import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestSceneRendererAPI(unittest.TestCase):

    def test_scene_render_endpoint(self):
        payload = {
            "scene_id": "scene_1",
            "start": 0,
            "end": 5,
            "layers": [
                {
                    "id": "background",
                    "type": "background",
                },
                {
                    "id": "caption",
                    "type": "text",
                    "text": "Bangladesh",
                },
            ],
            "animations": [],
            "camera": {
                "type": "static",
                "start": 0,
                "end": 5,
            },
        }

        response = client.post(
            "/api/render/scene",
            json=payload,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["scene_id"],
            "scene_1",
        )

        self.assertEqual(
            data["width"],
            1080,
        )

        self.assertEqual(
            data["height"],
            1920,
        )

        self.assertIn(
            "<svg",
            data["svg"],
        )

        self.assertIn(
            "Bangladesh",
            data["svg"],
        )

    def test_invalid_scene_is_rejected(self):
        payload = {
            "scene_id": "scene_1",
            "start": 0,
            "end": 5,
            "layers": [
                {
                    "id": "invalid",
                    "type": "video",
                }
            ],
            "animations": [],
            "camera": {
                "type": "static",
                "start": 0,
                "end": 5,
            },
        }

        response = client.post(
            "/api/render/scene",
            json=payload,
        )

        self.assertEqual(
            response.status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()