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
import datetime

import pandas as pd
from loguru import logger

from japan_avg_hotel_price_finder.thread_scrape import ThreadScrape

logger.add('japan_avg_hotel_price_month.log',
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {thread} |  {name} | {module} | {function} | {line} | {message}",
           mode='w')

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
today = datetime.date.today()
end_date = datetime.date(today.year, month + 1, 1) - datetime.timedelta(days=1)
nights = 1

# Initialize an empty DataFrame to collect all data
all_data = pd.DataFrame()

# Loop from today until the end of the year
current_date = datetime.date(today.year, month, 1)  # Start from the first day of the current month
while current_date <= end_date:
    start_day = current_date.day
    month = current_date.month
    year = current_date.year

    # Initialize and run the scraper
    thread_scrape = ThreadScrape(city, group_adults, num_rooms, group_children, selected_currency, start_day, month,
                                 year, nights)
    df = thread_scrape.thread_scrape()

    # Append the data to the all_data DataFrame
    all_data = all_data.append(df, ignore_index=True)

    # Move to the next day
    current_date += datetime.timedelta(days=1)

# Save the collected data to a CSV file
all_data.to_csv(f'osaka_month_{month}_daily_hotel_data.csv', index=False)


