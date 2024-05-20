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

from automated_scraper import automated_scraper_main
from japan_avg_hotel_price_finder.hotel_stay import HotelStay
from japan_avg_hotel_price_finder.scrape import Scraper
from japan_avg_hotel_price_finder.scrape_until_month_end import ScrapeUntilMonthEnd
from japan_avg_hotel_price_finder.thread_scrape import ThreadScraper


def test_thread_scraper() -> None:
    city = 'Osaka'
    group_adults = '1'
    num_rooms = '1'
    group_children = '0'
    selected_currency = 'USD'

    today = datetime.date.today()
    start_day = 27
    month = today.month
    year = today.year
    last_day: int = calendar.monthrange(year, month)[1]
    nights = 1

    hotel_stay = HotelStay(city, group_adults, num_rooms, group_children, selected_currency)

    thread_scrape = ThreadScraper(hotel_stay, start_day, month, year, nights)
    df = thread_scrape.thread_scrape()

    target_date_range: list[str] = [datetime.date(year, month, day).strftime('%Y-%m-%d') for day in
                                    range(start_day, last_day + 1)]
    unique_dates: list[str] = list(df['Date'].unique())

    assert not df.empty
    assert target_date_range == unique_dates


def test_until_month_end_scraper() -> None:
    city = 'Osaka'
    group_adults = '1'
    num_rooms = '1'
    group_children = '0'
    selected_currency = 'USD'

    today = datetime.date.today()
    start_day = 27
    month = today.month
    year = today.year
    last_day: int = calendar.monthrange(year, month)[1]
    nights = 1

    hotel_stay = HotelStay(city, group_adults, num_rooms, group_children, selected_currency)

    month_end = ScrapeUntilMonthEnd(hotel_stay, start_day, month, year, nights)
    df = month_end.scrape_until_month_end()

    target_date_range: list[str] = [datetime.date(year, month, day).strftime('%Y-%m-%d')
                                    for day in range(start_day, last_day + 1)]

    unique_dates: list[str] = list(df['Date'].unique())

    assert not df.empty
    assert target_date_range == unique_dates


def test_scraper() -> None:
    city = 'Osaka'
    group_adults = '1'
    num_rooms = '1'
    group_children = '0'
    selected_currency = 'USD'

    today = datetime.date.today()
    month = today.month
    year = today.year
    check_in = datetime.date(year, month, today.day).strftime('%Y-%m-%d')
    check_out = datetime.date(year, month, today.day) + datetime.timedelta(days=1)
    check_out = check_out.strftime('%Y-%m-%d')

    hotel_stay = HotelStay(city, group_adults, num_rooms, group_children, selected_currency)

    scraper = Scraper(hotel_stay)
    df = scraper.start_scraping_process(check_in, check_out)

    assert not df.empty


def test_weekly_scraper() -> None:
    city = 'Osaka'
    group_adults = '1'
    num_rooms = '1'
    group_children = '0'
    selected_currency = 'USD'

    hotel_stay = HotelStay(city, group_adults, num_rooms, group_children, selected_currency)

    today = datetime.date.today()
    start_day = today.day
    last_day = calendar.monthrange(today.year, today.month)[1]
    month = today.month
    year = today.year
    df = automated_scraper_main(month, hotel_stay)

    target_date_range: list[str] = [datetime.date(year, month, day).strftime('%Y-%m-%d')
                                    for day in range(start_day, last_day + 1)]

    unique_dates: list[str] = list(df['Date'].unique())

    assert not df.empty
    assert target_date_range == unique_dates


if __name__ == '__main__':
    pytest.main([__file__])
