import json
from decimal import Decimal

import pytest

from blendr.core import Fill
from blendr.storage import load, save


def test_save_then_load_round_trips(tmp_path):
    fills = [Fill(Decimal("30000"), Decimal("0.5")), Fill(Decimal("25000"), Decimal("0.25"))]
    path = tmp_path / "pos.json"
    save(fills, path)
    assert load(path) == fills


def test_save_writes_decimals_as_strings(tmp_path):
    path = tmp_path / "pos.json"
    save([Fill(Decimal("30000.123456"), Decimal("0.5"))], path)
    assert json.loads(path.read_text()) == [{"price": "30000.123456", "quantity": "0.5"}]


def test_load_preserves_decimal_exactness(tmp_path):
    # Values that float would mangle stay exact through save -> load.
    path = tmp_path / "pos.json"
    save([Fill(Decimal("0.1"), Decimal("0.2"))], path)
    loaded = load(path)
    assert loaded[0].price == Decimal("0.1")
    assert loaded[0].quantity == Decimal("0.2")


def test_save_then_load_empty_list(tmp_path):
    path = tmp_path / "empty.json"
    save([], path)
    assert load(path) == []


def test_load_rejects_malformed_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json")
    with pytest.raises(ValueError):
        load(path)


def test_load_rejects_non_list_top_level(tmp_path):
    path = tmp_path / "obj.json"
    path.write_text('{"price": "1", "quantity": "1"}')
    with pytest.raises(ValueError):
        load(path)


def test_load_rejects_missing_keys(tmp_path):
    path = tmp_path / "missing.json"
    path.write_text('[{"price": "30000"}]')
    with pytest.raises(ValueError):
        load(path)


def test_load_rejects_non_positive_values(tmp_path):
    path = tmp_path / "neg.json"
    path.write_text('[{"price": "-5", "quantity": "1"}]')
    with pytest.raises(ValueError):
        load(path)
