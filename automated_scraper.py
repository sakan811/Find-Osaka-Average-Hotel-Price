import argparse
import asyncio
import calendar
import os
from dataclasses import dataclass

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper

# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--month', type=int, help='Month to scrape data for (1-12)')
parser.add_argument('--japan', type=bool, default=False, help='Whether to scrape hotels from all city in Japan')
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
            raise OSError

        csv_file_name = f'{self.city}_hotel_data_{month_name}_{self.year}.csv'
        csv_file_path = os.path.join(path, csv_file_name)

        df.to_csv(csv_file_path, index=False)


if __name__ == '__main__':
    if not args.month:
        main_logger.warning('Please specify month to scrape data with --month argument')
    else:
        scraper = AutomatedScraper(city='Osaka', year=2024, month=args.month, start_day=1, check_in='',
                                   check_out='', group_adults=1, group_children=0, num_rooms=1, nights=1,
                                   selected_currency='USD', sqlite_name='', scrape_only_hotel=True,
                                   country='Japan')
        main_logger.info(f'Setting month to scrape to {args.month} for {scraper.__class__.__name__}...')

        asyncio.run(scraper.main())
