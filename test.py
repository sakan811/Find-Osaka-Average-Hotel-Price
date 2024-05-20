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
import calendar
import datetime

import pytest
import pytz

from automated_scraper import automated_scraper_main
from set_details import Details
from japan_avg_hotel_price_finder.scrape import BasicScraper
from japan_avg_hotel_price_finder.scrape_until_month_end import MonthEndBasicScraper
from japan_avg_hotel_price_finder.thread_scrape import ThreadPoolScraper


def test_thread_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Tokyo')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    start_day = 27
    month = today.month
    year = today.year
    last_day: int = calendar.monthrange(year, month)[1]
    nights = 1

    sqlite_name = 'test.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    thread_scrape = ThreadPoolScraper(hotel_stay)
    df = thread_scrape.thread_scrape()

    target_date_range: list[str] = [datetime.date(year, month, day).strftime('%Y-%m-%d') for day in
                                    range(start_day, last_day + 1)]
    unique_dates: list[str] = list(df['Date'].unique())

    target_date_range.sort()
    unique_dates.sort()

    assert not df.empty
    assert target_date_range == unique_dates


def test_until_month_end_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 0
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Tokyo')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()

    start_day = 27
    month = today.month
    year = today.year
    last_day: int = calendar.monthrange(year, month)[1]
    nights = 1

    sqlite_name = 'test.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    month_end = MonthEndBasicScraper(hotel_stay)
    df = month_end.scrape_until_month_end()

    target_date_range: list[str] = [datetime.date(year, month, day).strftime('%Y-%m-%d')
                                    for day in range(start_day, last_day + 1)]

    unique_dates: list[str] = list(df['Date'].unique())

    target_date_range.sort()
    unique_dates.sort()

    assert not df.empty
    assert target_date_range == unique_dates


def test_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Tokyo')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    month = today.month
    year = today.year
    check_in = datetime.date(year, month, today.day).strftime('%Y-%m-%d')
    check_out = datetime.date(year, month, today.day) + datetime.timedelta(days=1)
    check_out = check_out.strftime('%Y-%m-%d')

    sqlite_name = 'test.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        month=month, year=year, sqlite_name=sqlite_name
    )

    scraper = BasicScraper(hotel_stay)
    df = scraper.start_scraping_process(check_in, check_out)

    assert not df.empty


def test_weekly_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Tokyo')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    start_day = today.day
    last_day = calendar.monthrange(today.year, today.month)[1]
    month = today.month
    year = today.year

    sqlite_name = 'test.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, sqlite_name=sqlite_name
    )

    df = automated_scraper_main(month, hotel_stay)

    # Create the target date range in the specified timezone
    target_date_range: list[str] = [
        datetime.datetime(year, month, day, tzinfo=city_timezone).strftime('%Y-%m-%d')
        for day in range(start_day, last_day + 1)
    ]

    unique_dates: list[str] = list(df['Date'].unique())

    target_date_range.sort()
    unique_dates.sort()

    assert not df.empty
    assert target_date_range == unique_dates


if __name__ == '__main__':
    pytest.main([__file__])
