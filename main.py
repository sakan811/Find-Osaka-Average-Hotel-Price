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

import argparse
import datetime

from loguru import logger

from japan_avg_hotel_price_finder.scrape import BasicScraper
from japan_avg_hotel_price_finder.thread_scrape import ThreadPoolScraper
from japan_avg_hotel_price_finder.scrape_until_month_end import MonthEndBasicScraper
from set_details import Details

logger.add('japan_avg_hotel_price_month.log',
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {thread} |  {name} | {module} | {function} | {line} | {message}",
           mode='w')

# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--thread_pool', type=bool, default=False, help='Use thread pool')
parser.add_argument('--month_end', type=bool, default=False, help='Scrape until month end')
parser.add_argument('--scraper', type=bool, default=True, help='Use basic scraper')
args = parser.parse_args()

# Set booking details.
city: str = 'Osaka'
check_in: str = '2024-12-11'
check_out: str = '2024-12-12'
group_adults: int = 1
num_rooms: int = 1
group_children: int = 0
selected_currency: str = 'USD'

# Set the start date and number of nights when using Thread Pool Scraper or Month End Scraper
start_day: int = 1
month: int = 6
year: int = 2024
nights: int = 1

# Set SQLite database name
sqlite_name: str = 'avg_japan_hotel_price.db'

details = Details(
    city=city, check_in=check_in, check_out=check_out, group_adults=group_adults,
    num_rooms=num_rooms, group_children=group_children, selected_currency=selected_currency,
    start_day=start_day, month=month, year=year, nights=nights,
    sqlite_name=sqlite_name
)


if args.thread_pool:
    logger.info('Using thread pool scraper')
    thread_scrape = ThreadPoolScraper(details)
    thread_scrape.thread_scrape()
elif args.month_end:
    logger.info('Using month end scraper')
    month_end = MonthEndBasicScraper(details)
    month_end.scrape_until_month_end()
elif args.scraper:
    logger.info('Using basic scraper')
    check_in = details.check_in
    check_out = details.check_out
    scraper = BasicScraper(details)
    scraper.start_scraping_process(check_in, check_out)




