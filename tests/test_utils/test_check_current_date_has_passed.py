import datetime

import pytest

from japan_avg_hotel_price_finder.utils import check_if_current_date_has_passed


def test_check_if_current_date_has_passed():
    result = check_if_current_date_has_passed(2022, 5, 1)
    assert result is True

    today = datetime.datetime.today()
    day = today.day
    month = today.month
    year = today.year
    result = check_if_current_date_has_passed(year, month, day)
    assert result is False


def test_handles_leap_years_correctly():
    # Given
    year, month, day = 2020, 2, 29

    # When
    result = check_if_current_date_has_passed(year, month, day)

    # Then
    assert result is True


def test_returns_false_when_given_date_is_today():
    # Given
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    day = today.day

    # When
    result = check_if_current_date_has_passed(year, month, day)

    # Then
    assert result is False


def test_handles_end_of_month_dates_correctly():
    # Given
    year = 2022
    month = 1
    day = 31

    # When
    result = check_if_current_date_has_passed(year, month, day)

    # Then
    assert result is True


def test_handles_invalid_dates():
    # Given an invalid date like 30th February
    year = 2022
    month = 2
    day = 30

    # When checking if the current date has passed
    result = check_if_current_date_has_passed(year, month, day)

    # Then the result should be False as it's an invalid date
    assert result is False


if __name__ == '__main__':
    pytest.main()
