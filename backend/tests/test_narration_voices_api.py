import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TestNarrationVoicesAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @patch("app.main.LocalTTS.list_voices")
    def test_voice_list_endpoint(self, mock_list_voices):
        mock_list_voices.return_value = [
            {
                "id": "voice-1",
                "name": "Test Voice",
            },
            {
                "id": "voice-2",
                "name": "Another Voice",
            },
        ]

        response = self.client.get("/api/narration/voices")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("voices", data)
        self.assertEqual(len(data["voices"]), 2)
        self.assertEqual(
            data["voices"][0]["name"],
            "Test Voice",
        )

        mock_list_voices.assert_called_once()


if __name__ == "__main__":
    unittest.main()