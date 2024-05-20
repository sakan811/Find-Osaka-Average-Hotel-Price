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
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import pandas as pd
from loguru import logger

from japan_avg_hotel_price_finder.hotel_stay import HotelStay
from japan_avg_hotel_price_finder.scrape_until_month_end import ScrapeUntilMonthEnd


class ThreadScraper(ScrapeUntilMonthEnd):
    def __init__(
            self,
            hotel_stay: HotelStay,
            start_day: int,
            month: int,
            year: int,
            nights: int):
        """
        Initialize the ThreadScraper class with the following parameters:
        :param hotel_stay: HotelStay dataclass object.
        :param start_day: Day to start scraping.
        :param month: Month to start scraping.
        :param year: Year to start scraping.
        :param nights: Number of nights (Length of stay) which defines the room price.
                        For example, nights = 1 means scraping the hotel with room price for 1 night.
        """
        super().__init__(hotel_stay, start_day, month, year, nights)

    def thread_scrape(self) -> None | pd.DataFrame:
        """
        Scrape hotel data from the start day to the end of the same month using Thread Pool executor.
        :return: None.
                Return Pandas dataframe for testing purpose.
        """
        logger.info('Scraping hotel data using Thread Pool executor...')

        # Determine the last day of the given month
        last_day: int = calendar.monthrange(self.year, self.month)[1]

        # Define a list to store the result DataFrame from each thread
        results = []

        # Define a function to perform scraping for each date
        def scrape_each_date(day: int):
            """
            Scrape hotel data of the given date.
            :param day: Day of the month.
            :return: None
            """
            logger.info('Scraping hotel data of the given date...')

            current_date = datetime(self.year, self.month, day)
            check_in: str = current_date.strftime('%Y-%m-%d')
            check_out: str = (current_date + timedelta(days=self.nights)).strftime('%Y-%m-%d')

            df = self.start_scraping_process(check_in, check_out)

            # Append the result to the 'results' list
            results.append(df)

        # Create a thread pool with a maximum of 5 threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for each date within the specified range
            futures: list = [executor.submit(scrape_each_date, day) for day in range(self.start_day, last_day + 1)]

            # Wait for all tasks to complete
            for future in futures:
                future.result()

        # Concatenate all DataFrames in the 'results' list into a single DataFrame
        df = pd.concat(results, ignore_index=True)

        return df


if __name__ == '__main__':
    pass
