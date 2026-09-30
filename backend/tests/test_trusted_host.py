import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestTrustedHost(unittest.TestCase):
    def test_allowed_host(self):
        response = client.get(
            "/api/health",
            headers={"host": "localhost"},
        )

        self.assertEqual(response.status_code, 200)

    def test_loopback_host(self):
        response = client.get(
            "/api/health",
            headers={"host": "127.0.0.1"},
        )

        self.assertEqual(response.status_code, 200)

    def test_invalid_host_is_rejected(self):
        response = client.get(
            "/api/health",
            headers={"host": "evil.example"},
        )

        self.assertEqual(response.status_code, 400)
    def test_testclient_host_is_allowed(self):
        response = client.get(
            "/api/health",
            headers={"host": "testserver"},
        )

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()