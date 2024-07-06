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
from japan_avg_hotel_price_finder.graphql_scraper import scrape_graphql
from japan_avg_hotel_price_finder.utils import save_scraped_data
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import scrape_whole_month
from set_details import Details

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')
logger.setLevel(level="INFO")


# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--scraper', type=bool, default=True, help='Use basic GraphQL scraper')
parser.add_argument('--whole_mth', type=bool, default=False, help='Use Whole-Month GraphQL scraper')
parser.add_argument('--to_sqlite', type=bool, default=False, help='Save data to SQLite database')
parser.add_argument('--month', type=int, default=False, help='Month to scrape data for (1-12)')

args = parser.parse_args()

details = Details()

city = details.city
check_in = details.check_in
check_out = details.check_out
group_adults = details.group_adults
group_children = details.group_children
num_rooms = details.num_rooms
selected_currency = details.selected_currency
hotel_filter = details.scrape_only_hotel

if args.whole_mth:
    logger.info('Using Whole-Month GraphQL scraper')
    to_sqlite = args.to_sqlite

    if args.month:
        month = args.month
        details = Details(month=month)

    df = scrape_whole_month(details=details, hotel_filter=True)

    if to_sqlite:
        save_scraped_data(dataframe=df, details_dataclass=details, to_sqlite=to_sqlite)
    else:
        save_scraped_data(dataframe=df, city=city, month=details.month, year=details.year)

elif args.scraper:
    logger.info('Using basic GraphQL scraper')
    to_sqlite = args.to_sqlite

    df = scrape_graphql(city=city, check_in=check_in, check_out=check_out, num_rooms=num_rooms, group_adults=group_adults,
                        group_children=group_children, selected_currency=selected_currency, hotel_filter=hotel_filter)

    if to_sqlite:
        save_scraped_data(dataframe=df, details_dataclass=details, to_sqlite=to_sqlite)
    else:
        save_scraped_data(dataframe=df, city=city, check_in=check_in, check_out=check_out)


if __name__ == '__main__':
    pass



