#    Copyright 2024 Sakan Nirattisaykul
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import datetime
import sqlite3
from calendar import monthrange

import pytest
import pytz


from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.scrape import BasicScraper
from japan_avg_hotel_price_finder.scrape_until_month_end import MonthEndBasicScraper
from japan_avg_hotel_price_finder.thread_scrape import ThreadPoolScraper
from japan_avg_hotel_price_finder.utils import check_db_if_all_date_was_scraped, \
    get_count_of_date_by_mth_asof_today_query, check_csv_if_all_date_was_scraped, find_csv_files, convert_csv_to_df
from set_details import Details

logger = configure_logging_with_file('test.log', 'test')


def test_check_if_all_date_was_scraped_csv() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 0
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

    thread_scrape = ThreadPoolScraper(hotel_stay)
    thread_scrape.thread_scrape()
    check_csv_if_all_date_was_scraped()

    with sqlite3.connect(sqlite_name) as conn:
        directory = 'scraped_hotel_data_csv'
        csv_files: list = find_csv_files(directory)
        if csv_files:
            df = convert_csv_to_df(csv_files)
            df.to_sql('HotelPrice', conn, if_exists='replace', index=False)

        query = get_count_of_date_by_mth_asof_today_query()
        result = conn.execute(query).fetchall()
        days_in_month = monthrange(year, month)[1]
        for row in result:
            assert row[1] == days_in_month


def test_thread_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    start_day = 27
    month = today.month
    year = today.year
    nights = 1

    sqlite_name = 'test_thread_scraper.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    thread_scrape = ThreadPoolScraper(hotel_stay)
    df = thread_scrape.thread_scrape()

    assert not df.empty


def test_thread_scraper_past_month() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    start_day = 27
    month = today.month - 1
    year = today.year
    nights = 1

    sqlite_name = 'test_thread_scraper_past_month.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    thread_scrape = ThreadPoolScraper(hotel_stay)
    df = thread_scrape.thread_scrape()

    assert df is None


def test_until_month_end_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 0
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()

    start_day = 27
    month = today.month
    year = today.year
    nights = 1

    sqlite_name = 'test_until_month_end_scraper.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    month_end = MonthEndBasicScraper(hotel_stay)
    df = month_end.scrape_until_month_end()

    assert not df.empty


def test_until_month_end_scraper_past_month() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 0
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()

    start_day = 27
    month = today.month - 1
    year = today.year
    nights = 1

    sqlite_name = 'test_until_month_end_scraper_past_month.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    month_end = MonthEndBasicScraper(hotel_stay)
    df = month_end.scrape_until_month_end()

    assert df is None


def test_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    month = today.month
    year = today.year
    check_in = datetime.date(year, month, 25).strftime('%Y-%m-%d')
    check_out = datetime.date(year, month, 25) + datetime.timedelta(days=1)
    check_out = check_out.strftime('%Y-%m-%d')

    sqlite_name = 'test_scraper.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        month=month, year=year, sqlite_name=sqlite_name
    )

    scraper = BasicScraper(hotel_stay)
    df = scraper.start_scraping_process(check_in, check_out)

    assert not df.empty


def test_check_if_all_date_was_scraped() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 0
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
    thread_scrape.thread_scrape(to_sqlite=True)
    check_db_if_all_date_was_scraped(sqlite_name)

    with sqlite3.connect(sqlite_name) as conn:
        query = get_count_of_date_by_mth_asof_today_query()
        result = conn.execute(query).fetchall()
        days_in_month = monthrange(year, month)[1]
        for row in result:
            assert row[1] == days_in_month


if __name__ == '__main__':
    pytest.main()
