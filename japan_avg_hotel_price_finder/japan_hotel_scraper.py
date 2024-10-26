import calendar
import sqlite3

import duckdb
import pandas as pd
from pydantic import Field

from japan_avg_hotel_price_finder.sql.save_to_db import save_scraped_data
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper
from japan_avg_hotel_price_finder.configure_logging import main_logger


class JapanScraper(WholeMonthGraphQLScraper):
    """
    Web scraper class for scraping Japan hotel data from every region.

    Attributes:
        country (str): The country where the hotels are located.
        group_adults (str): Number of adults.
        num_rooms (str): Number of rooms.
        group_children (str): Number of children.
        selected_currency (str): Currency of the room price.
        scrape_only_hotel (bool): Whether to scrape only the hotel property data.
        start_day (int): Day to start scraping.
        year (int): Year to start scraping.
        nights (int): Number of nights (Length of stay) which defines the room price.
                    For example, nights = 1 means scraping the hotel with room price for 1 night.
    """

    japan_regions: dict[str, list[str]] = {
        "Hokkaido": ["Hokkaido"],
        "Tohoku": ["Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima"],
        "Kanto": ["Ibaraki", "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa"],
        "Chubu": ["Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu", "Shizuoka", "Aichi"],
        "Kansai": ["Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama"],
        "Chugoku": ["Tottori", "Shimane", "Okayama", "Hiroshima", "Yamaguchi"],
        "Shikoku": ["Tokushima", "Kagawa", "Ehime", "Kochi"],
        "Kyushu": ["Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima"],
        "Okinawa": ["Okinawa"]
    }

    region: str = ''

    start_month: int = Field(1, gt=0, le=12)  # month to start scraping
    end_month: int = Field(12, gt=0, le=12)  # last month to scrape

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

    async def _scrape_whole_year(self) -> None:
        """
        Scrape hotel data for the whole year
        :return: None
        """
        main_logger.info(f"Scraping Japan hotels for {self.city} for the whole year")
        for month in range(self.start_month, self.end_month + 1):
            self.month = month
            df = await self.scrape_whole_month()
            if not df.empty:
                df['Region'] = self.region
                self._load_to_sqlite(df)
            else:
                main_logger.warning(f"No data found for {self.city} for {calendar.month_name[self.month]} {self.year}")

    def _load_to_sqlite(self, prefecture_hotel_data: pd.DataFrame) -> None:
        """
        Load hotel data of all Japan Prefectures to SQlite
        :param prefecture_hotel_data: DataFrame with the whole-year hotel data of the given prefecture.
        :return: None
        """
        main_logger.info(f"Loading hotel data to SQLite {self.sqlite_name}...")

        # Rename 'City' column to 'Prefecture'
        prefecture_hotel_data = prefecture_hotel_data.rename(columns={'City': 'Prefecture'})

        with sqlite3.connect(self.sqlite_name) as conn:
            create_table_q = '''
            CREATE TABLE IF NOT EXISTS JapanHotels (
                ID             INTEGER PRIMARY KEY AUTOINCREMENT,
                Hotel          TEXT NOT NULL,
                Price          FLOAT NOT NULL,
                Review         FLOAT NOT NULL,
                "Price/Review" FLOAT NOT NULL,
                Date           DATE NOT NULL,
                Region         TEXT NOT NULL,
                Prefecture     TEXT NOT NULL,
                Location       TEXT NOT NULL,                
                AsOf       TIMESTAMP NOT NULL
            );    
            '''
            conn.execute(create_table_q)

            prefecture_hotel_data.to_sql('JapanHotels', conn, if_exists='append', index=False,
                                         dtype={
                                             'Hotel': 'TEXT',
                                             'Price': 'FLOAT',
                                             'Review': 'FLOAT',
                                             'Price/Review': 'FLOAT',
                                             'Date': 'DATE',
                                             'Region': 'TEXT',
                                             'Prefecture': 'TEXT',
                                             'Location': 'TEXT',
                                             'AsOf': 'TIMESTAMP'
                                         })

        main_logger.info(f"Hotel data for {self.city} loaded to SQLite successfully.")


if __name__ == '__main__':
    pass
