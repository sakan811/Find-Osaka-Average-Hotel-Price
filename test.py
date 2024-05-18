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

from japan_avg_hotel_price_finder.scrape_each_date import ScrapeEachDate


def test_full_process() -> None:
    city = 'Osaka'
    group_adults = '1'
    num_rooms = '1'
    group_children = '0'
    selected_currency = 'USD'

    today = datetime.date.today()
    start_day = 29
    month = today.month
    year = today.year
    nights = 1

    scrape_each_date = ScrapeEachDate(city, group_adults, num_rooms, selected_currency, group_children)
    df = scrape_each_date.scrape_until_month_end(start_day, month, year, nights)

    assert not df.empty


if __name__ == '__main__':
    pytest.main([__file__])
