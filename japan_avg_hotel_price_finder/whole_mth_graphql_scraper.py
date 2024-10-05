import calendar
import datetime
from datetime import date

import pandas as pd
from pydantic import Field

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.date_utils.date_utils import check_if_current_date_has_passed, format_date
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper


class WholeMonthGraphQLScraper(BasicGraphQLScraper):
    """
    A dataclass designed to scrape hotel booking details from a GraphQL endpoint for the whole month.

    Attributes:
        city (str): The city where the hotels are located.
        country (str): The country where the hotels are located.
        group_adults (str): Number of adults.
        num_rooms (str): Number of rooms.
        group_children (str): Number of children.
        selected_currency (str): Currency of the room price.
        scrape_only_hotel (bool): Whether to scrape only the hotel property data.
        start_day (int): Day to start scraping.
        month (int): Month to start scraping.
        year (int): Year to start scraping.
        nights (int): Number of nights (Length of stay) which defines the room price.
                    For example, nights = 1 means scraping the hotel with room price for 1 night.
        sqlite_name (str): Name of SQLite database to store the scraped data.
    """
    # Set the start day, month, year, and length of stay
    year: int = Field(datetime.datetime.now().year, gt=0)
    month: int = Field(datetime.datetime.now().month, gt=0, le=12)
    start_day: int = Field(1, gt=0, le=31)
    nights: int = Field(1, gt=0)

    async def scrape_whole_month(self, timezone=None) -> pd.DataFrame:
        """
        Scrape data from the GraphQL endpoint for the whole month.
        :param timezone: Timezone.
                        Default is None.
        :return: Pandas Dataframe containing hotel data from the whole month.
        """
        main_logger.info('Using Whole-Month GraphQL scraper...')

        # Determine the last day of the given month
        last_day: int = await self._find_last_day_of_the_month()
        main_logger.debug(f'Last day of {calendar.month_name[self.month]}-{self.year}: {last_day}')

        df_list = []
        for day in range(self.start_day, last_day + 1):
            main_logger.debug(f'Process day {day} of {calendar.month_name[self.month]}-{self.year}')

            date_has_passed: bool = check_if_current_date_has_passed(self.year, self.month, day, timezone)

            if date_has_passed:
                main_logger.warning(f'The current date has passed. Skip {self.year}-{self.month}-{day}.')
            else:
                current_date: datetime = datetime.datetime(self.year, self.month, day)
                main_logger.debug(f'The current date is {current_date}')

                self.check_in: str = format_date(current_date)
                main_logger.debug(f'Check-in date is {self.check_in}')

                check_out: date = self._calculate_check_out_date(current_date=current_date)
                self.check_out: str = format_date(check_out)
                main_logger.debug(f'Check-out date is {self.check_out}')
                main_logger.debug(f'Nights: {self.nights}')

                df = await self.scrape_graphql()
                df_list.append(df)

        if df_list:
            return pd.concat(df_list)
        else:
            return pd.DataFrame()

    async def _find_last_day_of_the_month(self) -> int:
        """
        Calculates the last day of the month for the current year and month.
        Uses calendar.monthrange() to determine the number of days in the month.
        Assumes self.year and self.month are already set.
        :return: Last day of the given month.
        """
        try:
            if self.year <= 0:
                raise ValueError(f"Invalid year: {self.year}. Year must be positive.")
            if self.month < 1 or self.month > 12:
                raise ValueError(f"Invalid month: {self.month}. Month must be between 1 and 12.")
            last_day: int = calendar.monthrange(self.year, self.month)[1]
            return last_day
        except ValueError as e:
            main_logger.error(f"Invalid date: {self.year}-{self.month}. {str(e)}")
            raise
        except Exception as e:
            main_logger.error(f"Unexpected error: {str(e)}")
            raise

    def _calculate_check_out_date(self, current_date: datetime.date) -> date:
        """
        Calculates the check-out date for the current date.

        :param current_date: Current date.
        :return: Check-out date.
        """
        check_out_date = current_date + datetime.timedelta(days=self.nights)
        return check_out_date


if __name__ == '__main__':
    pass
