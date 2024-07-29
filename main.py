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
import asyncio

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.utils import save_scraped_data
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper

logger = configure_logging_with_file(log_dir='logs', log_file='main.log', logger_name='main')

# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--scraper', type=bool, default=True, help='Use basic GraphQL scraper')
parser.add_argument('--whole_mth', type=bool, default=False, help='Use Whole-Month GraphQL scraper')
args = parser.parse_args()

if __name__ == '__main__':
    if args.whole_mth:
        logger.info('Using Whole-Month GraphQL scraper...')
        scraper = WholeMonthGraphQLScraper()

        df = asyncio.run(scraper.scrape_whole_month())

        save_scraped_data(dataframe=df, db=scraper.sqlite_name)
    else:
        logger.info('Using basic GraphQL scraper...')
        scraper = BasicGraphQLScraper()

        df = asyncio.run(scraper.scrape_graphql())

        save_scraped_data(dataframe=df, db=scraper.sqlite_name)
