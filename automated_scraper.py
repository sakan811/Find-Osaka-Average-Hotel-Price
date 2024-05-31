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

import argparse
import calendar
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import pandas as pd
from loguru import logger
from pandas import DataFrame

from set_details import Details
from japan_avg_hotel_price_finder.thread_scrape import ThreadPoolScraper

logger.add('osaka_hotel_weekly_scraper.log',
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {thread} |  {name} | {module} | {function} | {line} | {message}",
           mode='w')


class AutomatedThreadPoolScraper(ThreadPoolScraper):
    def __init__(self, details: Details):
        """
        Scrape hotel data from the start day to the end of the same month using Thread Pool executor.
        :param details: Details data class object.
        """
        super().__init__(details)

    def thread_scrape(self) -> pd.DataFrame:
        """
        Scrape hotel data from the start day to the end of the same month using Thread Pool executor.
        :return: Pandas dataframe containing hotel data.
        """
        logger.info('Scraping hotel data using Pool Thread executor...')

        start_day = self.details.start_day

        # Determine the last day of the given month
        last_day: int = calendar.monthrange(self.details.year, self.details.month)[1]

        # Define a list to store the result DataFrame from each thread
        results = []

        # Define a function to perform scraping for each date
        def scrape_each_date(day) -> None:
            """
            Scrape hotel data of the given date.
            :param day: Day of the month.
            :return: None
            """
            logger.info('Scraping each date...')

            current_date = datetime(self.details.year, self.details.month, day)
            check_in = current_date.strftime('%Y-%m-%d')
            check_out = (current_date + timedelta(days=self.details.nights)).strftime('%Y-%m-%d')

            df = self.start_weekly_scraping_process(check_in, check_out)

            # Append the result to the 'results' list
            results.append(df)

        # Create a thread pool with a maximum of 5 threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for each date within the specified range
            futures = [executor.submit(scrape_each_date, day) for day in range(start_day, last_day + 1)]

            # Wait for all tasks to complete
            for future in futures:
                future.result()

        # Concatenate all DataFrames in the 'results' list into a single DataFrame
        df = pd.concat(results, ignore_index=True)

        return df

    def start_weekly_scraping_process(
            self,
            check_in: str,
            check_out: str) -> pd.DataFrame:
        """
        Main function to start the web scraping process.
        :param check_in: Check-in date.
        :param check_out: Check-out date.
        :return: None.
                Return a Pandas DataFrame for testing purpose only.
        """
        logger.info("Starting web-scraping...")

        city = self.details.city
        group_adults = self.details.group_adults
        group_children = self.details.group_children
        num_rooms = self.details.num_rooms
        selected_currency = self.details.selected_currency

        url = (f'https://www.booking.com/searchresults.en-gb.html?ss={city}&checkin'
               f'={check_in}&checkout={check_out}&group_adults={group_adults}'
               f'&no_rooms={num_rooms}&group_children={group_children}'
               f'&selected_currency={selected_currency}&nflt=ht_id%3D204')

        dataframe = self._scrape(url)

        df_filtered = None
        # Create a DataFrame from the collected data
        try:
            df = pd.DataFrame(dataframe)
            df['City'] = city

            # Hotel data of the given date
            df['Date'] = check_in

            # Date which the data was collected
            df['AsOf'] = datetime.now()

            df_filtered = self._transform_data(df)
        except ValueError as e:
            logger.error(e)
            logger.error(f'Error when creating a DataFrame for {check_in} to {check_out} data')
        finally:
            return df_filtered


def automated_scraper_main(month: int, details: Details) -> None | DataFrame:
    """
    Automated scraper main function.
    :param month: Month to start scraping.
    :param details: HotelStay dataclass object.
    :return: None
            Return a Pandas DataFrame for testing purpose only.
    """
    details.month = month

    # Initialize an empty DataFrame to collect all data
    all_data = pd.DataFrame()

    today = datetime.today()

    # Can only scrape data from the current date onward
    if month < today.month:
        logger.info(
            f'{calendar.month_name[month]} has already passed. The current month is {calendar.month_name[today.month]}'
        )
        all_data.to_csv(f'osaka_month_{month}_daily_hotel_data.csv', index=False)
    else:
        # Can only scrape data from the today onward
        if month == today.month:
            details.start_day = today.day

        logger.info(f'Scraping data for {calendar.month_name[month]}...')

        # Initialize and run the scraper
        automated_scraper = AutomatedThreadPoolScraper(details)
        df = automated_scraper.thread_scrape()

        # Append the data to the all_data DataFrame
        all_data = pd.concat([all_data, df], ignore_index=True)

        # Save the collected data to a CSV file
        all_data.to_csv(f'osaka_month_{month}_daily_hotel_data.csv', index=False)

    return all_data


if __name__ == '__main__':
    # Define booking parameters for the hotel search.
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    today = datetime.today()
    start_day: int = 1
    year: int = today.year

    details = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms, group_children=group_children,
        selected_currency=selected_currency, start_day=start_day, year=year
    )

    # Initialize argument parser
    parser = argparse.ArgumentParser(description='Specify the month for data scraping.')
    parser.add_argument('--month', type=int, help='Month to scrape data for (1-12)', required=True)
    args = parser.parse_args()

    # Extract the month value from the command line argument
    month = args.month

    automated_scraper_main(month, details)
