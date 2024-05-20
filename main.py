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

from loguru import logger

from japan_avg_hotel_price_finder.scrape import Scraper
from japan_avg_hotel_price_finder.thread_scrape import ThreadScraper
from japan_avg_hotel_price_finder.scrape_until_month_end import ScrapeUntilMonthEnd
from set_details import Details

logger.add('japan_avg_hotel_price_month.log',
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {thread} |  {name} | {module} | {function} | {line} | {message}",
           mode='w')

# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--thread_pool', type=bool, default=False, help='Use thread pool')
parser.add_argument('--month_end', type=bool, default=False, help='Scrape until month end')
parser.add_argument('--check_in', type=str, default=False, help='Check-in date')
parser.add_argument('--check_out', type=str, default=False, help='Check-out date')
args = parser.parse_args()

details = Details()

check_in = args.check_in
check_out = args.check_out

if args.thread_pool:
    thread_scrape = ThreadScraper(details)
    thread_scrape.thread_scrape()
elif args.month_end:
    month_end = ScrapeUntilMonthEnd(details)
    month_end.scrape_until_month_end()
else:
    scraper = Scraper(details)
    scraper.start_scraping_process(check_in, check_out)



