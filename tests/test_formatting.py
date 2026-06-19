from decimal import Decimal

from blendr.formatting import EM_DASH, format_money, format_qty


def test_format_money_two_decimals():
    assert format_money(Decimal("30000")) == "30,000.00"


def test_format_money_thousands_separator():
    assert format_money(Decimal("1234567.5")) == "1,234,567.50"


def test_format_money_small_value():
    assert format_money(Decimal("0.5")) == "0.50"


def test_format_money_none_is_em_dash():
    assert format_money(None) == EM_DASH


def test_format_qty_trims_trailing_zeros():
    assert format_qty(Decimal("1.50000000")) == "1.5"


def test_format_qty_whole_number_has_no_decimal_point():
    assert format_qty(Decimal("1.0")) == "1"


def test_format_qty_thousands_separator():
    assert format_qty(Decimal("12345.5")) == "12,345.5"


def test_format_qty_caps_at_eight_decimals():
    assert format_qty(Decimal("0.123456789")) == "0.12345679"  # rounded to 8 dp


def test_format_qty_zero():
    assert format_qty(Decimal("0")) == "0"
