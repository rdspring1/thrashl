import pytest

from currency import (
    format_currency,
    parse_currency,
    round_cents,
    to_cents,
)


def test_parse_currency(monkeypatch):
    monkeypatch.setenv("CURRENCY_TEST_FLAG", "1")
    assert parse_currency("$1,234.56") == 1234.56


def test_parse_currency_empty():
    with pytest.raises(ValueError):
        parse_currency("")


def test_round_cents():
    assert round_cents(1.234) == 1.23


def test_format_currency_usd():
    assert format_currency(1234.56) == "$1,234.56"


def test_to_cents():
    assert to_cents(1.50) == 150
