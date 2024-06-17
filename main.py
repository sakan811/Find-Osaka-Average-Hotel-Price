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

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.scrape import BasicScraper
from japan_avg_hotel_price_finder.thread_scrape import ThreadPoolScraper
from japan_avg_hotel_price_finder.utils import check_csv_if_all_date_was_scraped, check_db_if_all_date_was_scraped, \
    save_scraped_data
from set_details import Details

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')


# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--thread_pool', type=bool, default=False, help='Use thread pool')
parser.add_argument('--scraper', type=bool, default=True, help='Use basic scraper')
parser.add_argument('--to_sqlite', type=bool, default=False, help='Use basic scraper')
parser.add_argument('--month', type=int, default=False, help='Month to scrape data for (1-12)')
parser.add_argument('--workers', type=int, default=False,
                    help='Number of thread to use when using Thread Pool Scraper')
args = parser.parse_args()

details = Details()

if args.thread_pool and args.month_end:
    logger.warning('Cannot use both --thread_pool and --month_end at the same time. Please use one of them at a time.')
elif args.thread_pool:
    logger.info('Using thread pool scraper')
    if args.month:
        month = args.month
        details = Details(month=month)

    thread_scrape = ThreadPoolScraper(details)
    to_sqlite = args.to_sqlite

    if args.workers:
        workers = args.workers
        if to_sqlite:
            data_tuple = thread_scrape.thread_scrape(max_workers=workers)
            df = data_tuple[0]
            save_scraped_data(dataframe=df, details_dataclass=details, to_sqlite=to_sqlite)
            check_db_if_all_date_was_scraped(details.sqlite_name)
        else:
            df, city, check_in, check_out = thread_scrape.thread_scrape(max_workers=workers)
            save_scraped_data(dataframe=df, city=city, check_in=check_in,
                              check_out=check_out)
            check_csv_if_all_date_was_scraped()
    else:
        if to_sqlite:
            data_tuple = thread_scrape.thread_scrape()
            df = data_tuple[0]
            save_scraped_data(dataframe=df, details_dataclass=details, to_sqlite=to_sqlite)
            check_db_if_all_date_was_scraped(details.sqlite_name)
        else:
            df, city, check_in, check_out = thread_scrape.thread_scrape()
            save_scraped_data(dataframe=df, city=city, check_in=check_in,
                              check_out=check_out)
            check_csv_if_all_date_was_scraped()
elif args.scraper:
    logger.info('Using basic scraper')
    check_in = details.check_in
    check_out = details.check_out
    to_sqlite = args.to_sqlite
    scraper = BasicScraper(details)

    if to_sqlite:
        data_tuple = scraper.start_scraping_process(check_in, check_out)
        df = data_tuple[0]
        save_scraped_data(dataframe=df, details_dataclass=details, to_sqlite=to_sqlite)
    else:
        df, city, check_in, check_out = scraper.start_scraping_process(check_in, check_out)
        save_scraped_data(dataframe=df, city=city, check_in=check_in,
                          check_out=check_out)




