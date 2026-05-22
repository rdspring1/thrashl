import pytest

from currency import parse_currency, round_cents


def test_parse_currency():
    assert parse_currency("$1,234.56") == 1234.56


def test_parse_currency_empty():
    with pytest.raises(ValueError):
        parse_currency("")


def test_round_cents():
    assert round_cents(1.234) == 1.23
