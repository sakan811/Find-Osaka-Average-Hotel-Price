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

from japan_avg_hotel_price_finder.scrape import scrape, transform_data
from japan_avg_hotel_price_finder.thread_scrape import ThreadScrape

logger.add('osaka_hotel_daily_scraper.log',
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {thread} |  {name} | {module} | {function} | {line} | {message}",
           mode='w')


class AutomatedThreadScrape(ThreadScrape):
    def __init__(self, city, group_adults, num_rooms, group_children, selected_currency, start_day, month, year,
                 nights):
        """
        Scrape hotel data from the start day to the end of the same month using Thread Pool executor.
        :param city: City where the hotels are located.
        :param group_adults: Number of adults.
        :param num_rooms: Number of rooms.
        :param group_children: Number of children.
        :param selected_currency: Currency of the room price.
        :param start_day: Day of the month to start scraping.
        :param month: Month to start scraping.
        :param year: Year to start scraping.
        :param nights: Number of nights (Length of stay).
        """
        super().__init__(city, group_adults, num_rooms, group_children, selected_currency, start_day, month, year,
                         nights)

    def thread_scrape(self) -> pd.DataFrame:
        """
        Scrape hotel data from the start day to the end of the same month using Thread Pool executor.
        :return: Pandas dataframe containing hotel data.
        """
        logger.info('Scraping hotel data using Pool Thread executor...')

        # Determine the total number of days in the specified month
        total_days = calendar.monthrange(self.year, self.month)[1]

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

            current_date = datetime(self.year, self.month, day)
            check_in = current_date.strftime('%Y-%m-%d')
            check_out = (current_date + timedelta(days=self.nights)).strftime('%Y-%m-%d')

            df = self.start_daily_scraping_process(
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

    @staticmethod
    def start_daily_scraping_process(
            city: str,
            check_in: str,
            check_out: str,
            group_adults: str,
            num_rooms: str,
            group_children: str,
            selected_currency: str) -> pd.DataFrame:
        """
        Main function to start the web scraping process.
        :param city: City name.
        :param check_in: Check-in date.
        :param check_out: Check-out date.
        :param group_adults: Number of adults.
        :param num_rooms: Number of rooms.
        :param group_children: Number of children.
        :param selected_currency: Currency name.
        :return: None.
                Return a Pandas DataFrame for testing purpose only.
        """
        logger.info("Starting web-scraping...")

        # Create a DataFrame to store the data
        data = {'Hotel': [], 'Price': [], 'Review': []}

        url = (f'https://www.booking.com/searchresults.en-gb.html?ss={city}&checkin'
               f'={check_in}&checkout={check_out}&group_adults={group_adults}'
               f'&no_rooms={num_rooms}&group_children={group_children}'
               f'&selected_currency={selected_currency}&nflt=ht_id%3D204')

        scrape(url, data)

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data)

        df['City'] = city

        # Hotel data of the given date
        df['Date'] = check_in

        # Date which the data was collected
        df['AsOf'] = datetime.today()

        df_filtered = transform_data(df)

        return df_filtered


# Define booking parameters for the hotel search.
city = 'Osaka'
group_adults = '1'
num_rooms = '1'
group_children = '0'
selected_currency = 'USD'

# Initialize argument parser
parser = argparse.ArgumentParser(description='Specify the month for data scraping.')
parser.add_argument('--month', type=int, help='Month to scrape data for (1-12)', required=True)
args = parser.parse_args()

# Extract the month value from the command line argument
month = args.month

# Specify the start date and duration of stay for data scraping
today = datetime.today()

if month == 12:
    end_date = datetime(today.year + 1, 1, 1) - timedelta(days=1)
else:
    end_date = datetime(today.year, month + 1, 1) - timedelta(days=1)
nights = 1

start_day = 1

# Can only scrape data from the current date onward
if month == today.month:
    start_day = today.day

# Initialize an empty DataFrame to collect all data
all_data = pd.DataFrame()

# Can only scrape data from the current date onward
if month < today.month:
    logger.info(f'{calendar.month_name[month]} has already passed. The current month is {calendar.month_name[today.month]}')
    all_data.to_csv(f'osaka_month_{month}_daily_hotel_data.csv', index=False)
else:
    # Loop from today until the end of the year
    current_date = datetime(today.year, month, start_day)  # Start from the first day of the current month

    logger.info(f'Scrape data for {calendar.month_name[month]}')

    start_day = current_date.day
    month = current_date.month
    year = current_date.year

    # Initialize and run the scraper
    thread_scrape = AutomatedThreadScrape(city, group_adults, num_rooms, group_children, selected_currency, start_day, month,
                                          year, nights)
    df = thread_scrape.thread_scrape()

    # Append the data to the all_data DataFrame
    all_data = pd.concat([all_data, df], ignore_index=True)

    # Move to the next day
    current_date += timedelta(days=1)

    # Save the collected data to a CSV file
    all_data.to_csv(f'osaka_month_{month}_daily_hotel_data.csv', index=False)
