"""LangChain tool that quotes the Pricing Tool workbook."""

from __future__ import annotations

from typing import Any

from langchain.tools import tool

from api import PricingSheet

from .schema import (
    FACTORY_DEFAULTS,
    CalculatePriceInput,
    INPUT_OPTIONS,
    OUTPUT_NAMES,
    PARAM_TO_LABEL,
)

_sheet: PricingSheet | None = None


def _get_sheet() -> PricingSheet:
    global _sheet
    if _sheet is None:
        _sheet = PricingSheet.connect()
    return _sheet


def _normalize(label: str, value: Any) -> Any:
    expected = INPUT_OPTIONS.get(label, {}).get("type", "string")
    if expected == "integer" and isinstance(value, float) and value.is_integer():
        return int(value)
    return value


@tool(
    "calculate_price",
    description=(
        "Set Pricing Tool inputs and return every quote output "
        f"({', '.join(OUTPUT_NAMES)}). "
        "Pass only the fields that should change; omitted fields keep their current sheet values."
    ),
    args_schema=CalculatePriceInput,
)
def calculate_price(**kwargs: Any) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for param, value in kwargs.items():
        if value is None:
            continue
        label = PARAM_TO_LABEL[param]
        values[label] = _normalize(label, value)
    return _get_sheet().quote(values or None)


@tool(
    "reset_factory_defaults",
    description=(
        "Reset Pricing Tool inputs to factory defaults and return every quote output "
        f"({', '.join(OUTPUT_NAMES)}). "
        "Use this to start a fresh quote or when the user asks to reset the sheet."
    ),
)
def reset_factory_defaults() -> dict[str, Any]:
    return _get_sheet().quote(FACTORY_DEFAULTS)
