import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str | None = None, base_url: str | None = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.timeout_seconds = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "900"))

    def generate_json(self, system_prompt: str, user_prompt: str, schema: dict) -> str:
        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "format": schema,
            "stream": False,
            "options": {"num_ctx": 8192, "num_predict": 4096},
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(request_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                raise RuntimeError(
                    f"Ollama model '{self.model}' was not found. Run `ollama pull {self.model}`."
                ) from exc
            raise RuntimeError(f"Ollama request failed with HTTP {exc.code}") from exc
        except TimeoutError as exc:
            raise RuntimeError(
                f"Ollama did not finish generating within {self.timeout_seconds} seconds. "
                "A smaller model or faster hardware may be needed."
            ) from exc
        except (URLError, OSError) as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.base_url}. Start Ollama and try again."
            ) from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned an invalid response") from exc

        content = result.get("message", {}).get("content")
        if not content:
            raise RuntimeError("Ollama returned an empty scene plan")
        return content