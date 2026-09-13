"""Read the current Pricing Tool quote through the Graph API."""

from __future__ import annotations

import json
import sys

from api import GraphAPIError, PricingSheet


def main() -> None:
    print("Connecting to Microsoft Graph...")
    sheet = PricingSheet.connect()
    print(f"item_id: {sheet.connection.item_id}")

    print("\nInputs:")
    print(json.dumps(sheet.get_inputs(), indent=2))

    print("\nOutputs:")
    print(json.dumps(sheet.get_outputs(), indent=2))


if __name__ == "__main__":
    try:
        main()
    except GraphAPIError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
