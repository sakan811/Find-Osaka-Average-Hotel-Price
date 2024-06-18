import argparse
import calendar
import datetime

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.graphql_scraper import scrape_graphql
from japan_avg_hotel_price_finder.utils import check_if_current_date_has_passed, save_scraped_data
from set_details import Details

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')
logger.setLevel(level="INFO")

parser = argparse.ArgumentParser(description='Parser that control which way to scrape the hotel data.')
parser.add_argument('--month', type=int, default=False, help='Month to scrape data for (1-12)')
args = parser.parse_args()

details = Details()
if args.month:
    month = args.month
    details = Details(month=month)


def scrape_whole_month(details: Details, timezone=None) -> pd.DataFrame:
    """
    Scrape data from the whole month.
    :param details: Details dataclass object.
    :param timezone: Timezone.
                    Default is None.
    :return: Pandas Dataframe.
    """
    # Determine the last day of the given month
    last_day: int = calendar.monthrange(details.year, details.month)[1]

    if timezone is not None:
        today = datetime.datetime.now(timezone)
    else:
        today = datetime.datetime.today()

    if details.year < today.year:
        logger.warning(f'The current year to scrape has passed. Skip {details.year}.')
        df = pd.DataFrame()
        return df
    else:
        if details.month < today.month:
            month_name = calendar.month_name[details.month]
            logger.warning(f'The current month to scrape has passed. Skip {month_name} {details.year}.')
            df = pd.DataFrame()
            return df
        else:
            df_list = []
            for day in range(details.start_day, last_day + 1):
                date_has_passed = check_if_current_date_has_passed(details.year, details.month, day, timezone)
                if date_has_passed:
                    logger.warning(f'The current date has passed. Skip {details.year}-{details.month}-{day}.')
                else:
                    current_date: datetime = datetime.datetime(details.year, details.month, day)
                    check_in: str = current_date.strftime('%Y-%m-%d')
                    check_out: str = (current_date + datetime.timedelta(days=details.nights)).strftime('%Y-%m-%d')
                    df = scrape_graphql(city=details.city, check_in=check_in, check_out=check_out,
                                        num_rooms=details.num_rooms, group_adults=details.group_adults,
                                        group_children=details.group_children,
                                        selected_currency=details.selected_currency)
                    df_list.append(df)

            df = pd.concat(df_list)
            return df


if __name__ == '__main__':
    # city = 'Osaka'
    # check_in = '2024-07-01'
    # check_out = '2024-07-02'
    # selected_currency = 'USD'
    # df = scrape_graphql(city, check_in, check_out, selected_currency)
    df = scrape_whole_month(details)
    save_scraped_data(dataframe=df, city=details.city, month=details.month, year=details.year)

