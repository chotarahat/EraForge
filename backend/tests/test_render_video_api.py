import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


class TestRenderVideoAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        cls.output_dir = Path(
            "outputs/video_export/videos"
        )

        cls.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        cls.test_file = (
            cls.output_dir / "test_video.mp4"
        )

        cls.test_file.write_bytes(
            b"fake mp4 data"
        )

    @classmethod
    def tearDownClass(cls):
        if cls.test_file.exists():
            cls.test_file.unlink()

    def test_video_file_returns_mp4(self):
        response = self.client.get(
            "/api/render/video/test_video.mp4"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.headers["content-type"],
            "video/mp4",
        )

    def test_missing_video_returns_404(self):
        response = self.client.get(
            "/api/render/video/missing.mp4"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_non_mp4_is_rejected(self):
        response = self.client.get(
            "/api/render/video/test.txt"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_path_traversal_is_rejected(self):
        response = self.client.get(
            "/api/render/video/../test_video.mp4"
        )

        self.assertEqual(
            response.status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()