"""Chat model used by the pricing agent."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from .settings import ModelSettings


def build_model(settings: ModelSettings | None = None) -> ChatOpenAI:
    settings = settings or ModelSettings.from_env()
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )
