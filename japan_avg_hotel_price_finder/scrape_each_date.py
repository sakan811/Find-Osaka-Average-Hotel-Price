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
from datetime import datetime, timedelta

import pandas as pd
from loguru import logger

from japan_avg_hotel_price_finder.scrape import start_scraping_process


class ScrapeEachDate:
    def __init__(self, city, group_adults, num_rooms, group_children, selected_currency):

        self.city = city
        self.group_adults = group_adults
        self.num_rooms = num_rooms
        self.group_children = group_children
        self.selected_currency = selected_currency

    def scrape_until_month_end(self, start_day: int, month: int, year: int, nights: int) -> None | pd.DataFrame:
        """
        Scrape hotel data (hotel name, room price, review score) for a specified number of nights,
        starting from a given date until the end of the same month.

        :param start_day: The day of the month from which to start scraping.
        :param month: The month for which data is to be scraped.
        :param year: The year for which data is to be scraped.
        :param nights: The number of consecutive nights for each hotel stay to be included in the data.
                   For example, if nights=3, the scraper will collect price data for a 3-night stay at each hotel.
        :return: None.
                Return a Pandas DataFrame when testing only.
        """
        logger.info(f'Scraping data from {start_day}-{calendar.month_name[month]}-{year} '
                    f'to the end of {calendar.month_name[month]}-{year}...')

        # Determine the first and last day of the current month
        start_date = datetime(year, month, start_day)

        # To get the last day of the month, we add one month to the first day of the month and then subtract one day
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=nights)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=nights)

        df_list = []

        logger.info('Loop through each day of the month')
        current_date = start_date
        while current_date <= end_date:
            check_in = current_date.strftime('%Y-%m-%d')
            check_out = (current_date + timedelta(days=nights)).strftime('%Y-%m-%d')
            logger.info(f'Scrape data for {nights} nights. Check-in: {check_in}, Check-out: {check_out}')

            current_date += timedelta(days=1)

            df = start_scraping_process(
                    self.city, check_in, check_out, self.group_adults, self.num_rooms,
                    self.group_children, self.selected_currency
                )

            df_list.append(df)

        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df


if __name__ == '__main__':
    pass
