import calendar
import datetime

import pandas as pd
from loguru import logger

from japan_avg_hotel_price_finder.graphql_scraper import scrape_graphql
from japan_avg_hotel_price_finder.utils import check_if_current_date_has_passed
from set_details import Details


def scrape_whole_month(details: Details, hotel_filter: bool = False, timezone=None) -> pd.DataFrame:
    """
    Scrape data from the GraphQL endpoint for the whole month.
    :param details: Details dataclass object.
    :param hotel_filter: If True, only scrape the hotel property data.
                        Default is False.
    :param timezone: Timezone.
                    Default is None.
    :return: Pandas Dataframe.
    """
    # Determine the last day of the given month
    last_day: int = calendar.monthrange(details.year, details.month)[1]

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
                                selected_currency=details.selected_currency, hotel_filter=hotel_filter)
            df_list.append(df)

        df = pd.concat(df_list)
        return df


if __name__ == '__main__':
    pass
