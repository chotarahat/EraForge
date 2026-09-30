from pathlib import Path
import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestRenderFileAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.output_dir = Path("backend/outputs/render_preview")
        cls.output_dir.mkdir(parents=True, exist_ok=True)

        cls.test_file = cls.output_dir / "test_scene.svg"
        cls.test_file.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"></svg>',
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        if cls.test_file.exists():
            cls.test_file.unlink()

    def test_render_file_returns_svg(self):
        response = self.client.get("/api/render/file/test_scene.svg")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/svg+xml")
        self.assertIn("<svg", response.text)

    def test_missing_render_file_returns_404(self):
        response = self.client.get(
            "/api/render/file/does_not_exist.svg"
        )

        self.assertEqual(response.status_code, 404)

    def test_path_traversal_is_rejected(self):
        response = self.client.get(
            "/api/render/file/../test_scene.svg"
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()