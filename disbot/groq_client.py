from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


class GroqClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    def chat(self, messages: list[dict]) -> str:
        if not self.api_key:
            return "Groq is not configured yet. Set GROQ_API_KEY in your .env file."

        payload = json.dumps({"model": self.model, "messages": messages}).encode("utf-8")
        request = Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

