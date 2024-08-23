import calendar
from dataclasses import dataclass, field

import duckdb
import pandas as pd

from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper
from japan_avg_hotel_price_finder.configure_logging import main_logger


@dataclass
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

    japan_regions: dict = field(default_factory=lambda: {
        "Hokkaido": ["Hokkaido"],
        "Tohoku": ["Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima"],
        "Kanto": ["Ibaraki", "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa"],
        "Chubu": ["Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu", "Shizuoka", "Aichi"],
        "Kansai": ["Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama"],
        "Chugoku": ["Tottori", "Shimane", "Okayama", "Hiroshima", "Yamaguchi"],
        "Shikoku": ["Tokushima", "Kagawa", "Ehime", "Kochi"],
        "Kyushu": ["Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima"],
        "Okinawa": ["Okinawa"]
    })

    duckdb_path: str = ''
    region: str = ''

    start_month: int = 1  # month to start scraping
    end_month: int = 12  # last month to scrape

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
                self._load_to_duckdb(df)
            else:
                main_logger.warning(f"No data found for {self.city} for {calendar.month_name[self.month]} {self.year}")

    def _load_to_duckdb(self, prefecture_hotel_data: pd.DataFrame) -> None:
        """
        Load hotel data to DuckDB
        :param prefecture_hotel_data: DataFrame with the whole-year hotel data of the given prefecture.
        :return: None
        """
        main_logger.info(f"Loading hotel data to DuckDB {self.duckdb_path}...")
        with duckdb.connect(self.duckdb_path) as conn:
            create_table_q = '''
            CREATE SEQUENCE if not exists id_sequence  START 1;
            create table if not exists JapanHotels (
                ID             INTEGER DEFAULT nextval('id_sequence'),
                Hotel          TEXT    not null,
                Price          FLOAT    not null,
                Review         FLOAT    not null,
                "Price/Review" FLOAT    not null,
                Date           DATE    not null,
                Region          TEXT    not null,
                Prefecture      text    not null,
                Location       TEXT    not null,                
                AsOfDate       TIMESTAMP  not null
            );    
            '''
            conn.sql(create_table_q)

            conn.register("temp_hotel_data", prefecture_hotel_data)

            insert_data_q = '''
            INSERT INTO JapanHotels (Hotel, Price, Review, "Price/Review", Date, Region, Prefecture, Location, AsOfDate)
            SELECT Hotel, Price, Review, "Price/Review", temp_hotel_data.Date, Region, City, Location, temp_hotel_data.AsOf 
            FROM temp_hotel_data
            '''
            conn.sql(insert_data_q)


if __name__ == '__main__':
    pass
