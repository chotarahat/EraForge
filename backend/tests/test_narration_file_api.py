import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TestNarrationFileAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        cls.output_dir = Path("backend/outputs/narration")
        cls.output_dir.mkdir(parents=True, exist_ok=True)

        cls.test_file = cls.output_dir / "test_narration.wav"
        cls.test_file.write_bytes(
            b"RIFF"
            + b"\x00\x00\x00\x00"
            + b"WAVE"
        )

    @classmethod
    def tearDownClass(cls):
        if cls.test_file.exists():
            cls.test_file.unlink()

    def test_narration_file_returns_audio(self):
        response = self.client.get(
            "/api/narration/file/test_narration.wav"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["content-type"],
            "audio/wav",
        )

    def test_missing_narration_file_returns_404(self):
        response = self.client.get(
            "/api/narration/file/missing.wav"
        )

        self.assertEqual(response.status_code, 404)

    def test_non_wav_file_is_rejected(self):
        response = self.client.get(
            "/api/narration/file/test.txt"
        )

        self.assertEqual(response.status_code, 404)

    def test_path_traversal_is_rejected(self):
        response = self.client.get(
            "/api/narration/file/../test_narration.wav"
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()