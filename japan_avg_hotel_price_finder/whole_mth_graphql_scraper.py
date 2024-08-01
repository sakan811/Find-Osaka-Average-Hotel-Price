import calendar
import datetime
from dataclasses import dataclass

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file, main_logger
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.utils import check_if_current_date_has_passed


script_logger = configure_logging_with_file(log_dir='logs', log_file='whole_mth_graphql_scraper.log',
                                            logger_name='whole_mth_graphql_scraper')


@dataclass
class WholeMonthGraphQLScraper(BasicGraphQLScraper):
    """
    A dataclass designed to scrape hotel booking details from a GraphQL endpoint for the whole month.
    """
    async def scrape_whole_month(self, timezone=None) -> pd.DataFrame:
        """
        Scrape data from the GraphQL endpoint for the whole month.
        :param timezone: Timezone.
                        Default is None.
        :return: Pandas Dataframe.
        """
        main_logger.info('Using Whole-Month GraphQL scraper...')

        # Determine the last day of the given month
        last_day: int = calendar.monthrange(self.year, self.month)[1]
        script_logger.debug(f'Last day of {calendar.month_name[self.month]}-{self.year}: {last_day}')

        df_list = []
        for day in range(self.start_day, last_day + 1):
            script_logger.debug(f'Process day {day} of {calendar.month_name[self.month]}-{self.year}')

            date_has_passed: bool = check_if_current_date_has_passed(self.year, self.month, day, timezone)

            if date_has_passed:
                main_logger.warning(f'The current date has passed. Skip {self.year}-{self.month}-{day}.')
            else:
                current_date: datetime = datetime.datetime(self.year, self.month, day)
                script_logger.debug(f'The current date is {current_date}')

                self.check_in: str = current_date.strftime('%Y-%m-%d')
                script_logger.debug(f'Check-in date is {self.check_in}')

                self.check_out: str = (current_date + datetime.timedelta(days=self.nights)).strftime('%Y-%m-%d')
                script_logger.debug(f'Check-out date is {self.check_out}')
                script_logger.debug(f'Nights: {self.nights}')

                df = await self.scrape_graphql()
                df_list.append(df)

        if df_list:
            return pd.concat(df_list)
        else:
            return pd.DataFrame()


if __name__ == '__main__':
    pass
