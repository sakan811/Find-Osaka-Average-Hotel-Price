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

from japan_avg_hotel_price_finder.scrape import start_scraping_process
from japan_avg_hotel_price_finder.scrape_each_date import ScrapeUntilMonthEnd


class ThreadScrape(ScrapeUntilMonthEnd):
    def __init__(
            self,
            city: str,
            group_adults: str,
            num_rooms: str,
            group_children: str,
            selected_currency: str,
            start_day: int,
            month: int,
            year: int,
            nights: int):
        """
        Initialize this class with hotel booking and date details.
        :param city: City name where the hotels are located.
        :param group_adults: Number of adults.
        :param num_rooms: Number of rooms.
        :param group_children: Number of children.
        :param selected_currency: Currency of the room price.
        :param start_day: Day of the month to start scraping.
        :param month: Month to start scraping.
        :param year: Year of the month to start scraping.
        :param nights: Number of nights (Length of stay).
        """
        self.start_day = start_day
        self.month = month
        self.year = year
        self.nights = nights
        super().__init__(city, group_adults, num_rooms, group_children, selected_currency)

    def thread_scrape(self) -> None | pd.DataFrame:
        """
        Scrape hotel data from the start day to the end of the same month using Thread Pool executor.
        :return: None.
                Return Pandas dataframe for testing purpose.
        """
        logger.info('Scraping hotel data using Thread Pool executor...')

        # Determine the total number of days in the specified month
        total_days = calendar.monthrange(self.year, self.month)[1]

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
            check_in = current_date.strftime('%Y-%m-%d')
            check_out = (current_date + timedelta(days=self.nights)).strftime('%Y-%m-%d')

            df = start_scraping_process(
                self.city,
                check_in,
                check_out,
                self.group_adults,
                self.num_rooms,
                self.group_children,
                self.selected_currency
            )

            # Append the result to the 'results' list
            results.append(df)

        # Create a thread pool with a maximum of 5 threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for each date within the specified range
            futures = [executor.submit(scrape_each_date, day) for day in range(self.start_day, total_days + 1)]

            # Wait for all tasks to complete
            for future in futures:
                future.result()

        # Concatenate all DataFrames in the 'results' list into a single DataFrame
        df = pd.concat(results, ignore_index=True)

        return df


if __name__ == '__main__':
    pass
