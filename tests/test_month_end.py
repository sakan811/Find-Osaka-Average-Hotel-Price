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
import pytest
import pytz

from japan_avg_hotel_price_finder.scrape_until_month_end import MonthEndBasicScraper
from set_details import Details


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

    start_day = 1
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
    df = month_end.scrape_until_month_end(timezone=city_timezone)

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
    df = month_end.scrape_until_month_end(timezone=city_timezone)

    assert df is None


if __name__ == '__main__':
    pytest.main()
