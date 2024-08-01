import argparse
import asyncio
import calendar
import os
from dataclasses import dataclass

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file, main_logger
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper

script_logger = configure_logging_with_file(log_dir='logs', log_file='automated_scraper.log', logger_name='automated_scraper')

# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--month', type=int, default=False, help='Month to scrape data for (1-12)')
args = parser.parse_args()


@dataclass
class AutomatedScraper(WholeMonthGraphQLScraper):
    async def main(self):
        df = await self.scrape_whole_month()

        month_name = calendar.month_name[self.month]

        path = 'scraped_hotel_data_csv'
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            main_logger.error(f"Error creating directory '{path}': {e}")

        csv_file_name = f'{self.city}_hotel_data_{month_name}_{self.year}.csv'
        csv_file_path = os.path.join(path, csv_file_name)

        df.to_csv(csv_file_path, index=False)


if __name__ == '__main__':
    scraper = AutomatedScraper()

    if args.month:
        main_logger.info(f'Setting month to scrape to {args.month} for {scraper.__class__.__name__}...')
        scraper = AutomatedScraper(month=args.month)

    asyncio.run(scraper.main())
