import datetime
import sqlite3
from calendar import monthrange

import pytest
import pytz

from japan_avg_hotel_price_finder.thread_scrape import ThreadPoolScraper
from japan_avg_hotel_price_finder.utils import check_if_current_date_has_passed, find_missing_dates, find_csv_files, \
    convert_csv_to_df, get_count_of_date_by_mth_asof_today_query, \
    check_in_db_if_all_date_was_scraped, save_scraped_data, check_in_csv_dir_if_all_date_was_scraped
from set_details import Details


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
    directory = 'tests/test_find_csv_files'
    csv_files = find_csv_files(directory)
    print(csv_files)
    assert len(csv_files) > 0

    directory_2 = 'tests/test_find_csv_files_2'
    csv_files = find_csv_files(directory_2)
    assert len(csv_files) == 0


def test_convert_csv_to_df():
    directory = 'tests/test_find_csv_files'
    csv_files = find_csv_files(directory)
    df = convert_csv_to_df(csv_files)
    assert not df.empty

    directory_2 = 'tests/test_find_csv_files_2'
    csv_files = find_csv_files(directory_2)
    df = convert_csv_to_df(csv_files)
    assert df is None

@pytest.mark.skip
def test_check_if_all_date_was_scraped_csv() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()

    start_day = 5

    if today.month == 12:
        month = 1
        year = today.year + 1
    else:
        month = today.month + 1
        year = today.year

    nights = 1

    sqlite_name = 'test_check_if_all_date_was_scraped_csv.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    directory = 'test_check_if_all_date_was_scraped_csv'

    thread_scrape = ThreadPoolScraper(hotel_stay)
    df, city, month, year = thread_scrape.thread_scrape(timezone=city_timezone, max_workers=2)
    save_scraped_data(dataframe=df, city=city, month=month,
                      year=year, save_dir=directory)
    check_in_csv_dir_if_all_date_was_scraped(directory)

    with sqlite3.connect(sqlite_name) as conn:
        directory = 'test_check_if_all_date_was_scraped_csv'
        csv_files: list = find_csv_files(directory)
        if csv_files:
            df = convert_csv_to_df(csv_files)
            df.to_sql('HotelPrice', conn, if_exists='replace', index=False)

        query = get_count_of_date_by_mth_asof_today_query()
        result = conn.execute(query).fetchall()
        days_in_month = monthrange(year, month)[1]
        for row in result:
            assert row[1] == days_in_month


@pytest.mark.skip
def test_check_if_all_date_was_scraped() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()

    start_day = 15

    if today.month == 12:
        month = 1
        year = today.year + 1
    else:
        month = today.month + 1
        year = today.year

    nights = 1

    sqlite_name = 'test_check_if_all_date_was_scraped.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    thread_scrape = ThreadPoolScraper(hotel_stay)
    data_tuple = thread_scrape.thread_scrape(timezone=city_timezone, max_workers=2)
    df = data_tuple[0]
    save_scraped_data(dataframe=df, details_dataclass=hotel_stay, to_sqlite=True)
    check_in_db_if_all_date_was_scraped(hotel_stay.sqlite_name)

    with sqlite3.connect(sqlite_name) as conn:
        query = get_count_of_date_by_mth_asof_today_query()
        result = conn.execute(query).fetchall()
        days_in_month = monthrange(year, month)[1]
        for row in result:
            assert row[1] == days_in_month


if __name__ == '__main__':
    pytest.main()
