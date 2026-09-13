"""Super simple LangGraph pricing agent."""

from __future__ import annotations

from langchain.agents import create_agent

from .model import build_model
from .prompt import SYSTEM_PROMPT
from .tools import calculate_price, reset_factory_defaults


def build_agent():
    return create_agent(
        build_model(),
        tools=[calculate_price, reset_factory_defaults],
        system_prompt=SYSTEM_PROMPT,
        name="pricing_agent",
    )
