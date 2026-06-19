from decimal import Decimal

import pytest

from blendr.core import (
    Fill,
    average_entry_price,
    parse_decimal,
    total_cost,
    total_quantity,
)


def test_parse_decimal_parses_plain_number():
    assert parse_decimal("28000") == Decimal("28000")


def test_parse_decimal_strips_thousands_separators():
    assert parse_decimal("28,000.50") == Decimal("28000.50")


def test_parse_decimal_strips_surrounding_whitespace():
    assert parse_decimal("  30000  ") == Decimal("30000")


def test_parse_decimal_rejects_blank():
    with pytest.raises(ValueError):
        parse_decimal("   ")


def test_parse_decimal_rejects_non_numeric():
    with pytest.raises(ValueError):
        parse_decimal("abc")


def test_parse_decimal_rejects_zero():
    with pytest.raises(ValueError):
        parse_decimal("0")


def test_parse_decimal_rejects_negative():
    with pytest.raises(ValueError):
        parse_decimal("-5")


def test_parse_decimal_rejects_nan():
    with pytest.raises(ValueError):
        parse_decimal("nan")


def test_parse_decimal_rejects_infinity():
    with pytest.raises(ValueError):
        parse_decimal("inf")


def test_total_quantity_of_empty_is_zero():
    assert total_quantity([]) == Decimal("0")


def test_total_quantity_sums_quantities():
    fills = [Fill(Decimal("30000"), Decimal("0.5")), Fill(Decimal("25000"), Decimal("0.3"))]
    assert total_quantity(fills) == Decimal("0.8")


def test_total_cost_of_empty_is_zero():
    assert total_cost([]) == Decimal("0")


def test_total_cost_sums_price_times_quantity():
    fills = [Fill(Decimal("30000"), Decimal("0.5")), Fill(Decimal("25000"), Decimal("0.2"))]
    assert total_cost(fills) == Decimal("20000")  # 15000 + 5000


def test_average_entry_price_of_empty_is_none():
    assert average_entry_price([]) is None


def test_average_entry_price_single_fill_is_that_price():
    fills = [Fill(Decimal("30000"), Decimal("0.5"))]
    assert average_entry_price(fills) == Decimal("30000")


def test_average_entry_price_is_quantity_weighted():
    # (30000*0.5 + 25000*0.5) / 1.0 = 27500
    fills = [Fill(Decimal("30000"), Decimal("0.5")), Fill(Decimal("25000"), Decimal("0.5"))]
    assert average_entry_price(fills) == Decimal("27500")


def test_average_entry_price_weights_by_size_not_count():
    # 0.1 @ 10000 and 0.9 @ 20000 -> (1000 + 18000) / 1.0 = 19000
    fills = [Fill(Decimal("10000"), Decimal("0.1")), Fill(Decimal("20000"), Decimal("0.9"))]
    assert average_entry_price(fills) == Decimal("19000")
