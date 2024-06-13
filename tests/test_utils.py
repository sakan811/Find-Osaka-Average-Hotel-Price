import datetime
from calendar import monthrange

import pytest

from japan_avg_hotel_price_finder.utils import check_if_current_date_has_passed, find_missing_dates, find_csv_files, convert_csv_to_df


def test_check_if_current_date_has_passed():
    result = check_if_current_date_has_passed(2022, 5, 1)
    assert result is True

    today = datetime.datetime.today()
    day = today.day
    month = today.month
    year = today.year
    result = check_if_current_date_has_passed(year, month, day)
    assert result is False


def test_find_missing_dates():
    today = datetime.datetime.today()
    month = today.month + 1
    year = today.year
    days_in_month = monthrange(year, month)[1]

    first_day_of_month = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
    third_day_of_month = datetime.datetime(year, month, 3).strftime('%Y-%m-%d')
    fifth_day_of_month = datetime.datetime(year, month, 5).strftime('%Y-%m-%d')

    dates_in_db = {first_day_of_month, third_day_of_month, fifth_day_of_month}

    result = find_missing_dates(dates_in_db, days_in_month, today, month, year)

    expected_missing_dates = []
    for day in range(1, days_in_month + 1):
        date_str = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
        if date_str not in dates_in_db:
            expected_missing_dates.append(date_str)

    assert result == expected_missing_dates


def test_find_csv_files():
    directory = 'test_find_csv_files'
    csv_files = find_csv_files(directory)
    assert len(csv_files) > 0

    directory_2 = 'test_find_csv_files_2'
    csv_files = find_csv_files(directory_2)
    assert len(csv_files) == 0


def test_convert_csv_to_df():
    directory = 'test_find_csv_files'
    csv_files = find_csv_files(directory)
    df = convert_csv_to_df(csv_files)
    assert not df.empty

    directory_2 = 'test_find_csv_files_2'
    csv_files = find_csv_files(directory_2)
    df = convert_csv_to_df(csv_files)
    assert df is None


if __name__ == '__main__':
    pytest.main()