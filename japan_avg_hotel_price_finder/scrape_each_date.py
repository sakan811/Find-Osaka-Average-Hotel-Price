import calendar
from datetime import datetime, timedelta

import pandas as pd
from loguru import logger

from japan_avg_hotel_price_finder.scrape import start_scraping_process


class ScrapeEachDate:
    def __init__(self, city, group_adults, num_rooms, group_children, selected_currency):

        self.city = city
        self.group_adults = group_adults
        self.num_rooms = num_rooms
        self.group_children = group_children
        self.selected_currency = selected_currency

    def scrape_until_month_end(self, start_day: int, month: int, year: int, nights: int) -> None | pd.DataFrame:
        """
        Scrape data starting from the start date to the end of the same month.

        :param start_day: Start day.
        :param month: Month of the start day.
        :param year: Year of the start day.
        :param nights: Number of nights for the room price of the scraped property data.
                        For example, nights=3 means scraping for 3-night room price data of each property.
        :return: Pandas DataFrame (Optional).
        """
        logger.info(f'Scraping data from {start_day}-{calendar.month_name[month]}-{year} '
                    f'to the end of {calendar.month_name[month]}-{year}...')

        # Determine the first and last day of the current month
        start_date = datetime(year, month, start_day)

        # To get the last day of the month, we add one month to the first day of the month and then subtract one day
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=nights)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=nights)

        df_list = []

        logger.info('Loop through each day of the month')
        current_date = start_date
        while current_date <= end_date:
            check_in = current_date.strftime('%Y-%m-%d')
            check_out = (current_date + timedelta(days=nights)).strftime('%Y-%m-%d')
            logger.info(f'Scrape data for {nights} nights. Check-in: {check_in}, Check-out: {check_out}')

            current_date += timedelta(days=1)

            df = start_scraping_process(
                    self.city, check_in, check_out, self.group_adults, self.num_rooms,
                    self.group_children, self.selected_currency
                )

            df_list.append(df)

        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df


if __name__ == '__main__':
    pass
