import pytest

from currency import parse_currency


@pytest.mark.parametrize(
    "text, expected",
    [
        ("$10.00", 10.00),
        ("$1,234.50", 1234.50),
        ("$0.25", 0.25),
    ],
)
def test_parse_currency_happy_path(text, expected):
    assert parse_currency(text) == expected
