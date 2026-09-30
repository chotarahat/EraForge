import os


class OpenAIProvider:
    name = "openai"

    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def generate_json(self, system_prompt: str, user_prompt: str, schema: dict) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when AI_PROVIDER=openai")

        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "eraforge_scene_plan",
                    "strict": True,
                    "schema": schema,
                }
            },
        )
        if not response.output_text:
            raise RuntimeError("OpenAI returned an empty scene plan")
        return response.output_text