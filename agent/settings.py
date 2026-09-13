"""Environment-backed settings for the pricing agent."""

from __future__ import annotations

import os

from dotenv import load_dotenv


class ModelSettings:
    """Chat model connection settings loaded from the environment."""

    def __init__(self, model: str, api_key: str | None, base_url: str) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    @classmethod
    def from_env(cls) -> ModelSettings:
        load_dotenv()
        return cls(
            model=os.getenv("AGENT_MODEL", "openai/gpt-5.6-luna"),
            api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
        )
