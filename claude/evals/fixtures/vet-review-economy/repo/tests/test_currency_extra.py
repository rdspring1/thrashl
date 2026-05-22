from currency import parse_currency


def test_parse_currency_again():
    assert parse_currency("$1,234.56") == 1234.56
