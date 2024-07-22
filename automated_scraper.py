import argparse
import asyncio
import calendar
import os

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import scrape_whole_month
from set_details import Details

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')
logger.setLevel(level="INFO")


async def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
    parser.add_argument('--whole_mth', type=bool, default=False, help='Use Whole-Month GraphQL scraper')
    parser.add_argument('--month', type=int, default=False, help='Month to scrape data for (1-12)')
    args = parser.parse_args()

    details = Details()
    city = details.city

    month = details.month
    year = details.year
    if args.whole_mth:
        logger.info('Using Whole-Month GraphQL scraper')

        if args.month:
            month = args.month
            details = Details(month=month)

        df = await scrape_whole_month(details=details, hotel_filter=True)

        month_name = calendar.month_name[month]

        path = 'scraped_hotel_data_csv'
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating directory '{path}': {e}")

        csv_file_name = f'{city}_hotel_data_{month_name}_{year}.csv'
        csv_file_path = os.path.join(path, csv_file_name)

        df.to_csv(csv_file_path, index=False)
    else:
        logger.warning('Please set --whole_mth=True when running this script.')

if __name__ == '__main__':
    asyncio.run(main())
