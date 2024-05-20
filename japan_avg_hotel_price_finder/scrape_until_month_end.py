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

from japan_avg_hotel_price_finder.scrape import Scraper
from japan_avg_hotel_price_finder.hotel_stay import HotelStay


class ScrapeUntilMonthEnd(Scraper):
    def __init__(
            self,
            hotel_stay: HotelStay,
            start_day: int,
            month: int,
            year: int,
            nights: int):
        """
        Initialize the ScrapeUntilMonthEnd class with the following parameters:
        :param hotel_stay: HotelStay dataclass object.
        :param start_day: Day to start scraping.
        :param month: Month to start scraping.
        :param year: Year to start scraping.
        :param nights: Number of nights (Length of stay) which defines the room price.
                        For example, nights = 1 means scraping the hotel with room price for 1 night.
        """
        super().__init__(hotel_stay)
        self.start_day = start_day
        self.month = month
        self.year = year
        self.nights = nights

    def scrape_until_month_end(self) -> None | pd.DataFrame:
        """
        Scrape hotel data (hotel name, room price, review score)
        starting from a given start day until the end of the same month.
        :return: None.
                Return a Pandas DataFrame for testing purpose only.
        """
        logger.info(f'Scraping data from {self.start_day}-{calendar.month_name[self.month]}-{self.year} '
                    f'to the end of {calendar.month_name[self.month]}-{self.year}...')

        # Determine the first and last day of the current month
        start_date = datetime(self.year, self.month, self.start_day)

        # To get the last day of the month, we add one month to the first day of the month and then subtract one day
        if self.month == 12:
            end_date = datetime(self.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(self.year, self.month + 1, 1) - timedelta(days=1)

        df_list = []

        logger.info('Loop through each day of the month')
        current_date = start_date
        while current_date <= end_date:
            check_in = current_date.strftime('%Y-%m-%d')
            check_out = (current_date + timedelta(days=self.nights)).strftime('%Y-%m-%d')
            logger.info(f'Scrape data for {self.nights} nights. Check-in: {check_in}, Check-out: {check_out}')

            current_date += timedelta(days=1)

            df = self.start_scraping_process(check_in, check_out)

            df_list.append(df)

        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df


if __name__ == '__main__':
    pass
