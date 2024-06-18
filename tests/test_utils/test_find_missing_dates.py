import calendar
import datetime
from calendar import monthrange

from japan_avg_hotel_price_finder.utils import find_missing_dates


def test_find_missing_dates():
    today = datetime.datetime.today()
    month = today.month + 1
    year = today.year
    days_in_month = monthrange(year, month)[1]

    first_day_of_month = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
    third_day_of_month = datetime.datetime(year, month, 3).strftime('%Y-%m-%d')
    fifth_day_of_month = datetime.datetime(year, month, 5).strftime('%Y-%m-%d')

    dates_in_db = {first_day_of_month, third_day_of_month, fifth_day_of_month}

    result = find_missing_dates(dates_in_db, days_in_month, month, year)

    expected_missing_dates = []
    for day in range(1, days_in_month + 1):
        date_str = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
        if date_str not in dates_in_db:
            expected_missing_dates.append(date_str)

    # The missing dates should be all dates of the given month that are not the dates of the given month in the database
    assert result == expected_missing_dates


def test_handles_empty_set_of_dates():
    # Given
    dates_in_db = set()
    days_in_month = 30
    today = datetime.datetime.today()
    month = 9
    year = today.year + 1

    # When
    missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year)
    expected_missing_dates = [datetime.datetime(year, month, day).strftime('%Y-%m-%d') for day in range(1, days_in_month + 1)]
    # The missing dates should be all dates of the given month that are not the dates of the given month in the database
    assert missing_dates == expected_missing_dates


def test_handles_leap_year_feb_missing_dates():
    # Given
    today = datetime.datetime.today()
    month = 2
    year = today.year + 1
    dates_in_db = {f'{year}-02-01', f'{year}-02-02', f'{year}-02-03', f'{year}-02-04', f'{year}-02-06'}

    # Determine the number of days in February for the given year
    if calendar.isleap(year):
        days_in_month = 29
    else:
        days_in_month = 28

    # When
    missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year)

    expected_missing_dates = []
    for day in range(1, days_in_month + 1):
        date_str = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
        if date_str not in dates_in_db:
            expected_missing_dates.append(date_str)

    # The missing dates should be all dates of the given month that are not the dates of the given month in the database
    assert missing_dates == expected_missing_dates


def test_past_dates_in_db():
    dates_in_db = {'2020-03-01', '2020-03-02', '2020-03-03', '2020-03-04'}
    days_in_month = 31
    month = 3
    year = 2020
    missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year)

    assert missing_dates == []