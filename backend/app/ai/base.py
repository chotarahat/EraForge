from typing import Protocol


class AIProvider(Protocol):
    name: str
    model: str

    def generate_json(self, system_prompt: str, user_prompt: str, schema: dict) -> str:
        ...