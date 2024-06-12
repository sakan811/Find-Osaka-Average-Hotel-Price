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
from selenium.common import InvalidSessionIdException

from japan_avg_hotel_price_finder.scrape_until_month_end import MonthEndBasicScraper
from japan_avg_hotel_price_finder.utils import check_if_current_date_has_passed
from set_details import Details


class ThreadPoolScraper(MonthEndBasicScraper):
    def __init__(self, details: Details):
        """
        Initialize the ThreadPoolScraper class with the following parameters:
        :param details: Details dataclass object.
        """
        super().__init__(details)

    def thread_scrape(self, to_sqlite: bool = False, max_workers: int = 9) -> None | pd.DataFrame:
        """
        Scrape hotel data from the start day to the end of the same month using Thread Pool executor.
        :param to_sqlite: If True, save the scraped data to a SQLite database, else save it to CSV.
        :param max_workers: Maximum number of threads to use.
                            Default is 9.
        :return: None or a Pandas dataframe.
        """
        logger.info('Scraping hotel data using Thread Pool executor...')

        # Determine the last day of the given month
        last_day: int = calendar.monthrange(self.year, self.month)[1]

        # Define a list to store the result DataFrame from each thread
        results = []

        today = datetime.today()
        if self.month < today.month:
            month_name = calendar.month_name[self.month]
            logger.warning(f'The current month to scrape has passed. Skip {month_name} {self.year}.')
        else:
            # Define a function to perform scraping for each date
            def scrape_each_date(day: int) -> None:
                """
                Scrape hotel data of the given date.
                :param day: Day of the month.
                :return: None
                """
                logger.info('Scraping hotel data of the given date...')

                current_date_has_passed: bool = check_if_current_date_has_passed(self.year, self.month, day)

                current_date = datetime(self.year, self.month, day)
                if current_date_has_passed:
                    logger.warning(f'The current day of the month to scrape was passed. Skip {self.year}-{self.month}-{day}.')
                else:
                    check_in: str = current_date.strftime('%Y-%m-%d')
                    check_out: str = (current_date + timedelta(days=self.nights)).strftime('%Y-%m-%d')

                    df = self.start_scraping_process(check_in, check_out, to_sqlite)

                    # Append the result to the 'results' list
                    results.append(df)

            # Create a thread pool with a specified maximum threads
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit tasks for each date within the specified range
                futures = [executor.submit(scrape_each_date, day) for day in range(self.start_day, last_day + 1)]

                # Wait for all tasks to complete
                for future in futures:
                    try:
                        future.result()
                    except InvalidSessionIdException as e:
                        logger.error(e)
                        logger.error('Tried to run command without establishing a connection')

            # Concatenate all DataFrames in the 'results' list into a single DataFrame
            df = pd.concat(results, ignore_index=True)

            return df


if __name__ == '__main__':
    pass
