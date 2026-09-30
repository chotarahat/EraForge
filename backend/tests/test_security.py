import os
import unittest
from unittest.mock import patch

from app.security import (
    get_allowed_hosts,
    get_allowed_origins,
    get_docs_enabled,
)


class TestSecurity(unittest.TestCase):
    def test_default_allowed_origins(self):
        with patch.dict(os.environ, {}, clear=True):
            origins = get_allowed_origins()

        self.assertEqual(
            origins,
            [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ],
        )

    def test_custom_allowed_origins(self):
        with patch.dict(
            os.environ,
            {
                "ERAFORGE_ALLOWED_ORIGINS": (
                    "https://example.com,https://app.example.com"
                )
            },
            clear=True,
        ):
            origins = get_allowed_origins()

        self.assertEqual(
            origins,
            [
                "https://example.com",
                "https://app.example.com",
            ],
        )

    def test_default_allowed_hosts(self):
        with patch.dict(os.environ, {}, clear=True):
            hosts = get_allowed_hosts()

        self.assertEqual(
            hosts,
            [
                "localhost",
                "127.0.0.1",
                "testserver",
            ],
        )

    def test_custom_allowed_hosts(self):
        with patch.dict(
            os.environ,
            {
                "ERAFORGE_ALLOWED_HOSTS": (
                    "example.com,api.example.com"
                )
            },
            clear=True,
        ):
            hosts = get_allowed_hosts()

        self.assertEqual(
            hosts,
            [
                "example.com",
                "api.example.com",
            ],
        )

    def test_docs_enabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(get_docs_enabled())

    def test_docs_can_be_disabled(self):
        with patch.dict(
            os.environ,
            {"ERAFORGE_ENABLE_DOCS": "false"},
            clear=True,
        ):
            self.assertFalse(get_docs_enabled())

    def test_docs_accepts_true_values(self):
        for value in ("1", "true", "yes", "on"):
            with self.subTest(value=value):
                with patch.dict(
                    os.environ,
                    {"ERAFORGE_ENABLE_DOCS": value},
                    clear=True,
                ):
                    self.assertTrue(get_docs_enabled())


if __name__ == "__main__":
    unittest.main()