import argparse
import asyncio
import calendar
import os
from dataclasses import dataclass

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper
from japan_avg_hotel_price_finder.japan_hotel_scraper import JapanScraper

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


@dataclass
class AutomatedJapanScraper(JapanScraper):
    async def scrape_japan_hotels(self) -> None:
        """
        Scrape Japan hotel data by Prefectures and Region
        :return: None
        """
        for region, prefectures in self.japan_regions.items():
            self.region = region
            main_logger.info(f"Scraping Japan hotels for region {self.region}")

            for prefecture in prefectures:
                main_logger.info(f"Scraping Japan hotels for city {prefecture}")

                self.city = prefecture
                await self._scrape_whole_year()

    async def _scrape_whole_year(self, start_month: int = 1, end_month: int = 12) -> None:
        """
        Scrape hotel data for the whole year
        :param start_month: Month to start scraping, default is 1.
        :param end_month: Month to end scraping, default is 12.
        :return: None
        """
        main_logger.info(f"Scraping Japan hotels for {self.city} for the whole year")
        for month in range(start_month, end_month + 1):
            self.month = month
            df = await self.scrape_whole_month()
            if not df.empty:
                df['Region'] = self.region

                month_name = calendar.month_name[self.month]

                path = 'scraped_japan_hotel_data_csv'
                try:
                    os.makedirs(path, exist_ok=True)
                except OSError as e:
                    main_logger.error(f"Error creating directory '{path}': {e}")
                    raise OSError

                csv_file_name = f'{self.city}_hotel_data_{month_name}_{self.year}.csv'
                csv_file_path = os.path.join(path, csv_file_name)

                df.to_csv(csv_file_path, index=False)
            else:
                main_logger.warning(f"No data found for {self.city} for {calendar.month_name[self.month]} {self.year}")


if __name__ == '__main__':
    if args.japan:
        scraper = AutomatedJapanScraper(sqlite_name='', check_in='', check_out='', city='', country='Japan')
        asyncio.run(scraper.scrape_japan_hotels())
    else:
        if not args.month:
            main_logger.warning('Please specify month to scrape data with --month argument')
        else:
            scraper = AutomatedScraper(city='Osaka', year=2024, month=args.month, start_day=1, check_in='', check_out='',
                                       group_adults=1, group_children=0, num_rooms=1, nights=1, selected_currency='USD',
                                       sqlite_name='', scrape_only_hotel=True, country='Japan')
            main_logger.info(f'Setting month to scrape to {args.month} for {scraper.__class__.__name__}...')

            asyncio.run(scraper.main())
