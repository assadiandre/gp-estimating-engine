"""Excel workbook helpers on top of an authenticated Graph connection."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .connection import GRAPH_BASE, GraphAPIError, GraphConnection


class Spreadsheet:
    """Read and write ranges in the connected Excel workbook."""

    def __init__(self, connection: GraphConnection) -> None:
        self.connection = connection

    def get_worksheets(self) -> list[dict[str, Any]]:
        payload = self.connection.request("GET", f"{self._workbook_url()}/worksheets")
        return payload.get("value", [])

    def read_range(self, sheet_name: str, address: str) -> dict[str, Any]:
        return self.connection.request("GET", self._range_url(sheet_name, address))

    def update_range(
        self,
        sheet_name: str,
        address: str,
        values: list[list[Any]],
    ) -> dict[str, Any]:
        return self.connection.request(
            "PATCH",
            self._range_url(sheet_name, address),
            json_body={"values": values},
        )

    def _workbook_url(self) -> str:
        if not self.connection.item_id:
            raise GraphAPIError("item_id is not set. Call resolve_item_id() first.")
        encoded_user = quote(self.connection.user_email)
        return (
            f"{GRAPH_BASE}/users/{encoded_user}/drive/items/"
            f"{self.connection.item_id}/workbook"
        )

    def _range_url(self, sheet_name: str, address: str) -> str:
        encoded_sheet = quote(sheet_name, safe="")
        encoded_address = quote(address, safe=":")
        return (
            f"{self._workbook_url()}/worksheets('{encoded_sheet}')"
            f"/range(address='{encoded_address}')"
        )
