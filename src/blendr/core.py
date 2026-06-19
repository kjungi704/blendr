"""Pure math for a position's weighted-average entry price.

No GUI imports live here so this module is fully unit-testable.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class Fill:
    """A single buy: a price and the quantity bought at it (both > 0)."""

    price: Decimal
    quantity: Decimal


def parse_decimal(text: str) -> Decimal:
    """Parse user input into a positive, finite Decimal.

    Trims whitespace and thousands separators. Raises ``ValueError`` for
    blank, non-numeric, non-finite, or non-positive input.
    """
    cleaned = text.strip().replace(",", "")
    if not cleaned:
        raise ValueError("Enter a value.")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"'{text.strip()}' is not a number.") from None
    if not value.is_finite():
        raise ValueError("Value must be a finite number.")
    if value <= 0:
        raise ValueError("Value must be greater than 0.")
    return value


def total_quantity(fills: Iterable[Fill]) -> Decimal:
    """Sum of all fill quantities."""
    return sum((f.quantity for f in fills), Decimal("0"))


def total_cost(fills: Iterable[Fill]) -> Decimal:
    """Sum of price * quantity across all fills."""
    return sum((f.price * f.quantity for f in fills), Decimal("0"))


def average_entry_price(fills: Iterable[Fill]) -> Decimal | None:
    """Quantity-weighted average entry price, or None when there is no position."""
    fills = list(fills)
    quantity = total_quantity(fills)
    if quantity == 0:
        return None
    return total_cost(fills) / quantity
