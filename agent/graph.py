"""Super simple LangGraph pricing agent."""

from __future__ import annotations

from langchain.agents import create_agent

from .model import build_model
from .schema import PARAM_TO_LABEL
from .tools import calculate_price

SYSTEM_PROMPT = (
    "You quote print jobs using the calculate_price tool. "
    "That tool writes inputs to the live Pricing Tool spreadsheet and returns "
    "Cost, Curved Cost, Curve, Final Price, Wait & Save, Express, and turnaround days. "
    "Use the sheet field names via the tool arguments. "
    f"Available inputs: {', '.join(PARAM_TO_LABEL.values())}. "
    "Only send fields the user specified or that you must change. "
    "Then summarize the quote clearly."
)


def build_agent():
    return create_agent(
        build_model(),
        tools=[calculate_price],
        system_prompt=SYSTEM_PROMPT,
        name="pricing_agent",
    )
