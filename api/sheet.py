"""Named-field API for the Pricing Tool workbook."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .connection import GraphConnection
from .spreadsheet import Spreadsheet

CALC_INFO_DIR = Path(__file__).resolve().parent.parent / "calc_info"
SHEET_NAME = "Pricing Tool"


def _load_json(name: str) -> dict[str, Any]:
    return json.loads((CALC_INFO_DIR / name).read_text())


def _cell_value(payload: dict[str, Any]) -> Any:
    values = payload.get("values") or [[None]]
    if not values or not values[0]:
        return None
    return values[0][0]


class PricingSheet:
    """Read and write Pricing Tool fields by name via Microsoft Graph."""

    def __init__(self, connection: GraphConnection) -> None:
        self.connection = connection
        self.spreadsheet = Spreadsheet(connection)
        mapping = _load_json("input_output.json")
        self.input_cells: dict[str, str] = mapping["inputs"]
        self.output_cells: dict[str, str] = mapping["outputs"]
        self.input_options: dict[str, Any] = _load_json("input_options.json")

    @classmethod
    def connect(cls) -> PricingSheet:
        return cls(GraphConnection.from_env().connect())

    def schema(self) -> dict[str, Any]:
        return self.input_options

    def get_input(self, name: str) -> Any:
        return self._read(self._require_input(name))

    def get_output(self, name: str) -> Any:
        return self._read(self._require_output(name))

    def get_inputs(self) -> dict[str, Any]:
        column_b = (self.spreadsheet.read_range(SHEET_NAME, "B1:B34").get("values") or [])
        values: dict[str, Any] = {}
        for name, cell in self.input_cells.items():
            if cell.startswith("B") and cell[1:].isdigit():
                row = int(cell[1:])
                values[name] = column_b[row - 1][0] if row <= len(column_b) else None
            else:
                values[name] = self._read(cell)
        return values

    def get_outputs(self) -> dict[str, Any]:
        return {name: self._read(cell) for name, cell in self.output_cells.items()}

    def set_input(self, name: str, value: Any) -> Any:
        cell = self._require_input(name)
        coerced = self._coerce(name, value)
        updated = self.spreadsheet.update_range(SHEET_NAME, cell, [[coerced]])
        return _cell_value(updated)

    def set_inputs(self, values: dict[str, Any]) -> dict[str, Any]:
        return {name: self.set_input(name, value) for name, value in values.items()}

    def quote(self, values: dict[str, Any] | None = None) -> dict[str, Any]:
        if values:
            self.set_inputs(values)
        return self.get_outputs()

    def _read(self, cell: str) -> Any:
        return _cell_value(self.spreadsheet.read_range(SHEET_NAME, cell))

    def _require_input(self, name: str) -> str:
        try:
            return self.input_cells[name]
        except KeyError as exc:
            known = ", ".join(self.input_cells)
            raise KeyError(f"Unknown input {name!r}. Expected one of: {known}") from exc

    def _require_output(self, name: str) -> str:
        try:
            return self.output_cells[name]
        except KeyError as exc:
            known = ", ".join(self.output_cells)
            raise KeyError(f"Unknown output {name!r}. Expected one of: {known}") from exc

    def _coerce(self, name: str, value: Any) -> Any:
        spec = self.input_options.get(name, {})
        expected = spec.get("type", "string")
        hint = spec.get("hint") or ""
        options = spec.get("options") or []

        if expected == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer. {hint}".strip())
        elif expected == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number. {hint}".strip())
        elif expected == "string":
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string. {hint}".strip())

        if options and value not in options:
            raise ValueError(
                f"{name} must be one of {options}. {hint}".strip()
            )
        return value
