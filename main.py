import argparse
import asyncio

from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.utils import save_scraped_data
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper

# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--scraper', type=bool, default=True, help='Use basic GraphQL scraper')
parser.add_argument('--whole_mth', type=bool, default=False, help='Use Whole-Month GraphQL scraper')
args = parser.parse_args()

if __name__ == '__main__':
    if args.whole_mth:
        scraper = WholeMonthGraphQLScraper()

        df = asyncio.run(scraper.scrape_whole_month())

        save_scraped_data(dataframe=df, db=scraper.sqlite_name)
    else:
        scraper = BasicGraphQLScraper()

        df = asyncio.run(scraper.scrape_graphql())

        save_scraped_data(dataframe=df, db=scraper.sqlite_name)
