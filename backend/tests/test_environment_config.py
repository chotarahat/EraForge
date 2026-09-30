import os
import unittest
from unittest.mock import patch

from app.security import (
    get_allowed_hosts,
    get_allowed_origins,
    get_docs_enabled,
    get_max_request_bytes,
)


class TestEnvironmentConfig(unittest.TestCase):
    def test_allowed_origins_from_environment(self):
        with patch.dict(
            os.environ,
            {
                "ERAFORGE_ALLOWED_ORIGINS": (
                    "https://example.com,https://app.example.com"
                )
            },
            clear=True,
        ):
            self.assertEqual(
                get_allowed_origins(),
                [
                    "https://example.com",
                    "https://app.example.com",
                ],
            )

    def test_allowed_hosts_from_environment(self):
        with patch.dict(
            os.environ,
            {
                "ERAFORGE_ALLOWED_HOSTS": (
                    "example.com,api.example.com"
                )
            },
            clear=True,
        ):
            self.assertEqual(
                get_allowed_hosts(),
                [
                    "example.com",
                    "api.example.com",
                ],
            )

    def test_docs_environment(self):
        with patch.dict(
            os.environ,
            {"ERAFORGE_ENABLE_DOCS": "false"},
            clear=True,
        ):
            self.assertFalse(get_docs_enabled())

    def test_request_limit_environment(self):
        with patch.dict(
            os.environ,
            {"ERAFORGE_MAX_REQUEST_BYTES": "4096"},
            clear=True,
        ):
            self.assertEqual(
                get_max_request_bytes(),
                4096,
            )


if __name__ == "__main__":
    unittest.main()