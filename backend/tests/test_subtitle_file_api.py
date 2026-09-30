import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


class TestSubtitleFileAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        cls.output_dir = Path(
            "outputs/subtitles"
        )

        cls.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        cls.test_file = (
            cls.output_dir / "test.srt"
        )

        cls.test_file.write_text(
            "1\n"
            "00:00:00,000 --> 00:00:01,000\n"
            "Test subtitle.\n",
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        if cls.test_file.exists():
            cls.test_file.unlink()

    def test_subtitle_file_returns_srt(self):
        response = self.client.get(
            "/api/subtitles/file/test.srt"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "Test subtitle.",
            response.text,
        )

    def test_missing_subtitle_file_returns_404(self):
        response = self.client.get(
            "/api/subtitles/file/missing.srt"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_non_srt_file_is_rejected(self):
        response = self.client.get(
            "/api/subtitles/file/test.txt"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_path_traversal_is_rejected(self):
        response = self.client.get(
            "/api/subtitles/file/../test.srt"
        )

        self.assertEqual(
            response.status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()