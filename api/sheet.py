"""Named-field API for the Pricing Tool workbook."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .connection import GraphConnection
from .spreadsheet import Spreadsheet

CALC_INFO_DIR = Path(__file__).resolve().parent.parent / "calc_info"
SHEET_NAME = "Pricing Tool"
_A1 = re.compile(r"^([A-Z]+)(\d+)$")


def _load_json(name: str) -> dict[str, Any]:
    return json.loads((CALC_INFO_DIR / name).read_text())


def _cell_value(payload: dict[str, Any]) -> Any:
    values = payload.get("values") or [[None]]
    if not values or not values[0]:
        return None
    return values[0][0]


def _parse_a1(cell: str) -> tuple[str, int]:
    match = _A1.match(cell)
    if not match:
        raise ValueError(f"Unsupported cell address: {cell}")
    return match.group(1), int(match.group(2))


def _col_index(col: str) -> int:
    n = 0
    for char in col:
        n = n * 26 + (ord(char) - 64)
    return n


def _col_letter(index: int) -> str:
    letters: list[str] = []
    while index:
        index, remainder = divmod(index - 1, 26)
        letters.append(chr(65 + remainder))
    return "".join(reversed(letters))


def _grid_value(grid: list[list[Any]], row: int, col: int) -> Any:
    if row >= len(grid) or col >= len(grid[row]):
        return None
    return grid[row][col]


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
        return self._read_cells(self.output_cells)

    def set_input(self, name: str, value: Any) -> Any:
        return self.set_inputs({name: value})[name]

    def set_inputs(self, values: dict[str, Any]) -> dict[str, Any]:
        by_column: dict[str, dict[int, Any]] = {}
        written: dict[str, Any] = {}
        for name, value in values.items():
            col, row = _parse_a1(self._require_input(name))
            coerced = self._coerce(name, value)
            by_column.setdefault(col, {})[row] = coerced
            written[name] = coerced
        for col, rows in by_column.items():
            self._write_column(col, rows)
        return written

    def quote(self, values: dict[str, Any] | None = None) -> dict[str, Any]:
        if values:
            self.set_inputs(values)
        return self.get_outputs()

    def _read(self, cell: str) -> Any:
        return _cell_value(self.spreadsheet.read_range(SHEET_NAME, cell))

    def _read_cells(self, cells: dict[str, str]) -> dict[str, Any]:
        parsed = {name: _parse_a1(cell) for name, cell in cells.items()}
        cols = [_col_index(col) for col, _ in parsed.values()]
        rows = [row for _, row in parsed.values()]
        min_col, max_col = min(cols), max(cols)
        min_row, max_row = min(rows), max(rows)
        address = f"{_col_letter(min_col)}{min_row}:{_col_letter(max_col)}{max_row}"
        grid = self.spreadsheet.read_range(SHEET_NAME, address).get("values") or []
        values: dict[str, Any] = {}
        for name, (col, row) in parsed.items():
            values[name] = _grid_value(grid, row - min_row, _col_index(col) - min_col)
        return values

    def _write_column(self, col: str, rows: dict[int, Any]) -> None:
        min_row, max_row = min(rows), max(rows)
        address = f"{col}{min_row}:{col}{max_row}"
        if max_row - min_row + 1 == len(rows):
            payload = [[rows[row]] for row in range(min_row, max_row + 1)]
        else:
            current = self.spreadsheet.read_range(SHEET_NAME, address).get("values") or []
            payload = []
            for offset, row in enumerate(range(min_row, max_row + 1)):
                if row in rows:
                    payload.append([rows[row]])
                else:
                    payload.append([_grid_value(current, offset, 0)])
        self.spreadsheet.update_range(SHEET_NAME, address, payload)

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
