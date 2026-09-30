import unittest

from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app


@app.get("/api/test/internal-error")
def test_internal_error():
    raise RuntimeError("secret internal error")


client = TestClient(
    app,
    raise_server_exceptions=False,
)


class TestErrorHandler(unittest.TestCase):
    def test_internal_errors_are_sanitized(self):
        response = client.get(
            "/api/test/internal-error",
            headers={"host": "testserver"},
        )

        self.assertEqual(response.status_code, 500)

        self.assertEqual(
            response.json(),
            {"detail": "Internal server error."},
        )

        self.assertNotIn(
            "secret internal error",
            response.text,
        )


if __name__ == "__main__":
    unittest.main()