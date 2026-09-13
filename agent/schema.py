"""Pydantic tool schema built from calc_info JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, create_model

CALC_INFO_DIR = Path(__file__).resolve().parent.parent / "calc_info"
_TYPE_MAP = {"string": str, "integer": int, "number": float}


def _load_json(name: str) -> dict[str, Any]:
    return json.loads((CALC_INFO_DIR / name).read_text())


def _param_name(label: str) -> str:
    cleaned = label.lower().replace("&", " and ").replace("/", " ")
    return re.sub(r"[^a-z0-9]+", "_", cleaned).strip("_")


def _field_description(label: str, spec: dict[str, Any]) -> str:
    parts = [spec.get("hint") or f"{label} for the pricing sheet."]
    options = spec.get("options") or []
    if options:
        parts.append("Options: " + ", ".join(str(option) for option in options) + ".")
    return " ".join(parts)


def _build_schema() -> tuple[type[BaseModel], dict[str, str], dict[str, Any]]:
    options = _load_json("input_options.json")
    fields: dict[str, Any] = {}
    param_to_label: dict[str, str] = {}
    for label, spec in options.items():
        param = _param_name(label)
        param_to_label[param] = label
        py_type = _TYPE_MAP[spec.get("type", "string")]
        fields[param] = (
            py_type | None,
            Field(default=None, description=_field_description(label, spec)),
        )
    model = create_model("CalculatePriceInput", __base__=BaseModel, **fields)
    return model, param_to_label, options


CalculatePriceInput, PARAM_TO_LABEL, INPUT_OPTIONS = _build_schema()
OUTPUT_NAMES = list(_load_json("input_output.json")["outputs"])
FACTORY_DEFAULTS = _load_json("factory_defaults.json")
