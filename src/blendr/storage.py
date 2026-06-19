"""Save and load a list of fills as JSON. Pure, no GUI imports.

Decimals are stored as strings so values stay exact across a round trip.
A malformed file raises ``ValueError`` for the GUI to surface.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from os import PathLike
from pathlib import Path

from blendr.core import Fill, parse_decimal


def save(fills: Iterable[Fill], path: str | PathLike[str]) -> None:
    """Write the fills to ``path`` as a JSON list of price/quantity strings."""
    data = [{"price": str(f.price), "quantity": str(f.quantity)} for f in fills]
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load(path: str | PathLike[str]) -> list[Fill]:
    """Read fills from ``path``, validating structure and values.

    Raises ``ValueError`` if the file is not valid JSON, is not a list, or
    contains an entry missing/with an invalid price or quantity.
    """
    raw = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Not a valid blendr file: {e}") from e

    if not isinstance(data, list):
        raise ValueError("File must contain a list of fills.")

    fills: list[Fill] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict) or "price" not in item or "quantity" not in item:
            raise ValueError(f"Fill #{index} is missing a price or quantity.")
        price = parse_decimal(str(item["price"]))
        quantity = parse_decimal(str(item["quantity"]))
        fills.append(Fill(price, quantity))
    return fills
