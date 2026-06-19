"""Display formatting for prices and quantities. Pure, no GUI imports."""

from __future__ import annotations

from decimal import Decimal

EM_DASH = "—"


def format_money(value: Decimal | None) -> str:
    """Format a money value with thousands separators and 2 decimals.

    ``None`` renders as an em dash (used when there is no position yet).
    """
    if value is None:
        return EM_DASH
    return f"{value:,.2f}"


def format_qty(value: Decimal) -> str:
    """Format a quantity with thousands separators and up to 8 decimals.

    Trailing zeros (and a bare decimal point) are trimmed, so ``1.0`` shows
    as ``1`` and ``1.50000000`` shows as ``1.5``.
    """
    text = f"{value:,.8f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text
