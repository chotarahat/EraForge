import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestRequestLimits(unittest.TestCase):
    def test_normal_request_is_allowed(self):
        response = client.get(
            "/api/health",
            headers={
                "host": "testserver",
                "content-length": "10",
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_oversized_request_is_rejected(self):
        response = client.get(
            "/api/health",
            headers={
                "host": "testserver",
                "content-length": str(10 * 1024 * 1024 + 1),
            },
        )

        self.assertEqual(response.status_code, 413)

        self.assertEqual(
            response.json()["detail"],
            "Request body is too large.",
        )

    def test_invalid_content_length_is_rejected(self):
        response = client.get(
            "/api/health",
            headers={
                "host": "testserver",
                "content-length": "invalid",
            },
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json()["detail"],
            "Invalid Content-Length header.",
        )


if __name__ == "__main__":
    unittest.main()