import calendar
from typing import Any

import pandas as pd
from pydantic import Field, ConfigDict
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.sql.db_model import Base, JapanHotel
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper


class JapanScraper(WholeMonthGraphQLScraper):
    """
    Web scraper class for scraping Japan hotel data from every region.

    Attributes:
        country (str): The country where the hotels are located.
        group_adults (str): Number of adults, default is 1.
        num_rooms (str): Number of rooms, default is 1.
        group_children (str): Number of children, default is 0.
        selected_currency (str): Currency of the room price, default is USD.
        scrape_only_hotel (bool): Whether to scrape only the hotel property data, default is True
        start_day (int): Day to start scraping, default is 1.
        month (int): Month to start scraping, default is January.
        year (int): Year to start scraping, default is the current year.
        nights (int): Number of nights (Length of stay) which defines the room price.
                    For example, nights = 1 means scraping the hotel with room price for 1 night.
                    Default is 1.
        japan_regions (dict[str, list[str]]): Dictionary of Japan regions and their prefectures.
        region (str): The current region being scraped.
        start_month (int): Month to start scraping (1-12), default is 1.
        end_month (int): Last month to scrape (1-12), default is 12.
        engine (Engine): SQLAlchemy engine.
    """
    engine: Engine

    model_config = ConfigDict(arbitrary_types_allowed=True)

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

    def map_prefecture_to_region(self, prefecture: str) -> str:
        """
        Map a prefecture to its corresponding region.
        :param prefecture: Prefecture to map
        :return: the Region to which the prefecture belongs
        """
        for region, prefectures in self.japan_regions.items():
            if prefecture in prefectures:
                return region
        return "Unknown"  # If the prefecture is not found in any region

    def create_prefecture_region_mapping(self) -> dict[Any, list[str]]:
        """
        Create a mapping of prefectures to regions based on the input city.
        :return: A dictionary mapping prefectures to regions.
        """
        # Split the comma-separated string into a list of prefectures
        prefectures = [prefecture.strip() for prefecture in self.city.split(',')]

        # Create a new dictionary mapping each prefecture to its region
        new_japan_regions = {}
        for prefecture in prefectures:
            region = self.map_prefecture_to_region(prefecture)
            if region in new_japan_regions:
                new_japan_regions[region].append(prefecture)
            else:
                new_japan_regions[region] = [prefecture]

        # Return the japan_regions with the new mapping
        return new_japan_regions

    async def scrape_japan_hotels(self) -> None:
        """
        Scrape Japan hotel data by Prefectures and Region
        :return: None
        """
        if self.city:
            japan_regions_to_be_used = self.create_prefecture_region_mapping()
        else:
            japan_regions_to_be_used = self.japan_regions

        for region, prefectures in japan_regions_to_be_used.items():
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
                self._load_to_database(df)
            else:
                main_logger.warning(f"No data found for {self.city} for {calendar.month_name[self.month]} {self.year}")

    def _load_to_database(self, prefecture_hotel_data: pd.DataFrame) -> None:
        """
        Load hotel data of all Japan Prefectures to a database using SQLAlchemy ORM
        :param prefecture_hotel_data: DataFrame with the whole-year hotel data of the given prefecture.
        :return: None
        """
        main_logger.info("Loading hotel data to database...")

        # Rename 'City' column to 'Prefecture'
        prefecture_hotel_data = prefecture_hotel_data.rename(columns={'City': 'Prefecture'})

        # Rename Price/Review column
        prefecture_hotel_data.rename(columns={'Price/Review': 'PriceReview'}, inplace=True)

        # Create all tables
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Convert DataFrame to list of dictionaries
            records = prefecture_hotel_data.to_dict('records')

            # Create HotelPrice objects
            hotel_prices = [JapanHotel(**record) for record in records]

            # Bulk insert records
            session.bulk_save_objects(hotel_prices)

            session.commit()
            main_logger.info(f"Hotel data for {self.city} loaded to a database successfully.")
        except Exception as e:
            session.rollback()
            main_logger.error(f"An error occurred while saving data: {str(e)}")
            raise
        finally:
            session.close()


if __name__ == '__main__':
    pass
