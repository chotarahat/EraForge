import unittest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestSecurityHeaders(unittest.TestCase):
    def test_security_headers_are_present(self):
        response = client.get("/api/health")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.headers["X-Content-Type-Options"],
            "nosniff",
        )

        self.assertEqual(
            response.headers["X-Frame-Options"],
            "DENY",
        )

        self.assertEqual(
            response.headers["Referrer-Policy"],
            "strict-origin-when-cross-origin",
        )

        self.assertEqual(
            response.headers["Permissions-Policy"],
            "camera=(), microphone=(), geolocation=()",
        )


if __name__ == "__main__":
    unittest.main()