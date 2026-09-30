import io
import json
import unittest
from unittest.mock import patch

from backend.app.ai.factory import create_provider, get_provider_info
from backend.app.ai.ollama_provider import OllamaProvider


class AIProviderTests(unittest.TestCase):
    def test_ollama_is_the_default_provider(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(get_provider_info(), {"provider": "ollama", "model": "qwen2.5:7b"})
            self.assertIsInstance(create_provider(), OllamaProvider)

    @patch("backend.app.ai.ollama_provider.urlopen")
    def test_ollama_receives_schema_and_returns_content(self, urlopen):
        scene_plan = {"title": "A test plan"}
        urlopen.return_value.__enter__.return_value = io.BytesIO(
            json.dumps({"message": {"content": json.dumps(scene_plan)}}).encode("utf-8")
        )
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}

        result = OllamaProvider().generate_json("system prompt", "user prompt", schema)

        self.assertEqual(json.loads(result), scene_plan)
        request = urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(request.full_url, "http://localhost:11434/api/chat")
        self.assertEqual(body["format"], schema)
        self.assertFalse(body["stream"])

    def test_openai_is_selected_explicitly(self):
        with patch.dict("os.environ", {"AI_PROVIDER": "openai"}, clear=True):
            self.assertEqual(get_provider_info()["provider"], "openai")

    @patch("backend.app.ai.ollama_provider.urlopen", side_effect=TimeoutError)
    def test_ollama_timeout_is_not_reported_as_connection_failure(self, _urlopen):
        provider = OllamaProvider()

        with self.assertRaisesRegex(RuntimeError, "did not finish generating"):
            provider.generate_json("system", "user", {"type": "object"})


if __name__ == "__main__":
    unittest.main()