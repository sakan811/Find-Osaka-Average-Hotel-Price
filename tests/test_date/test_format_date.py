import pytest
from datetime import date
from japan_avg_hotel_price_finder.date_utils.date_utils import format_date


def test_format_date_regular_dates():
    # Test regular dates
    assert format_date(date(2023, 1, 1)) == "2023-01-01"
    assert format_date(date(2023, 12, 31)) == "2023-12-31"
    assert format_date(date(2023, 7, 15)) == "2023-07-15"


def test_format_date_leap_year():
    # Test leap year date
    assert format_date(date(2024, 2, 29)) == "2024-02-29"


def test_format_date_single_digit_month_and_day():
    # Test single-digit month and day
    assert format_date(date(2023, 1, 1)) == "2023-01-01"
    assert format_date(date(2023, 9, 9)) == "2023-09-09"


def test_format_date_edge_cases():
    # Test first day of the year
    assert format_date(date(2023, 1, 1)) == "2023-01-01"

    # Test last day of the year
    assert format_date(date(2023, 12, 31)) == "2023-12-31"


def test_format_date_different_centuries():
    # Test dates from different centuries
    assert format_date(date(1999, 12, 31)) == "1999-12-31"
    assert format_date(date(2000, 1, 1)) == "2000-01-01"
    assert format_date(date(2100, 1, 1)) == "2100-01-01"


def test_format_date_invalid_input():
    # Test invalid input
    with pytest.raises(AttributeError):
        format_date("2023-01-01")  # String instead of date object

    with pytest.raises(AttributeError):
        format_date(2023)  # Integer instead of date object


def test_format_date_extreme_dates():
    # Test extreme past and future dates
    assert format_date(date(1, 1, 1)) == "0001-01-01"
    assert format_date(date(9999, 12, 31)) == "9999-12-31"
