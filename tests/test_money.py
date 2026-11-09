import pytest

from inventory_app.services.errors import ValidationError
from inventory_app.services.money import CurrencyFormat, format_money, parse_money, to_plain


def test_format_cop():
    assert format_money(1234567) == "$ 1.234.567"
    assert format_money(0) == "$ 0"
    assert format_money(-5000) == "-$ 5.000"


def test_format_with_decimals():
    assert format_money(123456, "US$", 2) == "US$ 1.234,56"
    assert format_money(5, "US$", 2) == "US$ 0,05"
    assert to_plain(123456, 2) == "1234.56"


@pytest.mark.parametrize("text,expected", [
    ("1234567", 1234567), ("1.234.567", 1234567), ("$ 50.000", 50000), (" 0 ", 0),
])
def test_parse_cop(text, expected):
    assert parse_money(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "-5", "12,5", "1.2.3", "1.23"])
def test_parse_cop_invalid(text):
    with pytest.raises(ValidationError):
        parse_money(text)


def test_parse_with_decimals():
    assert parse_money("1.234,56", 2) == 123456
    assert parse_money("10", 2) == 1000
    assert parse_money("10,5", 2) == 1050
    with pytest.raises(ValidationError):
        parse_money("10,555", 2)


def test_currency_format_object():
    f = CurrencyFormat("COP", "$", 0)
    assert f.format(1500) == "$ 1.500"
    assert f.parse("1.500") == 1500
