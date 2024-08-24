import asyncio
import calendar
import datetime
import sqlite3
import argparse
from calendar import monthrange
from dataclasses import dataclass

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.utils import save_scraped_data, \
    get_count_of_date_by_mth_asof_today_query, get_dates_of_each_month_asof_today_query


def find_missing_dates(dates_in_db: set[str],
                       days_in_month: int,
                       month: int,
                       year: int,
                       timezone=None) -> list[str]:
    """
    Find missing dates of the given month.
    Only check date from today onward.
    :param dates_in_db: Dates of that month in the database of the current AsOf Date.
                        Date format: '%Y-%m-%d'.
    :param days_in_month: Total days in the given month.
    :param month: Month.
    :param year: Year.
    :param timezone: Timezone, default is None, mostly for testing purpose.
    :returns: Missing Dates as a list.
    """
    main_logger.info(f"Find missing date of {calendar.month_name[month]} {year}.")
    if timezone:
        today: datetime = datetime.datetime.now(timezone)
    else:
        today: datetime = datetime.datetime.today()

    # convert date string to a date object
    dates_in_db_date_obj: list[datetime] = [datetime.datetime.strptime(date, '%Y-%m-%d').date()
                                            for date in dates_in_db]

    # filter out past date
    filtered_dates: list[datetime] = [date for date in dates_in_db_date_obj if date >= today.date()]

    today_date_obj: datetime.date = today.date()
    missing_dates_list: list[str] = []

    # find missing dates of the given month
    for day in range(1, days_in_month + 1):
        date_to_check: datetime = datetime.datetime(year, month, day)
        date_to_check_str: str = date_to_check.strftime('%Y-%m-%d')
        date_to_check_date_obj: datetime.date = date_to_check.date()
        if date_to_check_date_obj < today_date_obj:
            main_logger.warning(f"{date_to_check_str} has passed. Skip this date.")
        else:
            if date_to_check_date_obj not in filtered_dates:
                missing_dates_list.append(date_to_check_str)

    return missing_dates_list


async def scrape_missing_dates(missing_dates_list: list[str] = None, is_test: bool = False, test_db: str = None,
                               param_dictionary: dict = None, country: str = 'Japan'):
    """
    Scrape missing dates with BasicScraper and load them into a database.
    :param missing_dates_list: Missing dates.
    :param is_test: Whether this function is executed for testing purposes.
    :param test_db: Test database, default is None.
    :param param_dictionary: Dictionary of parameters, default is None.
    :param country: Country where the hotels are located, default is Japan.
    :return: None
    """
    main_logger.info("Scraping missing dates...")
    if missing_dates_list:
        for date in missing_dates_list:
            check_in = date
            check_out_date_obj = datetime.datetime.strptime(check_in, '%Y-%m-%d') + datetime.timedelta(days=1)
            check_out = check_out_date_obj.strftime('%Y-%m-%d')

            if param_dictionary is None:
                main_logger.warning('The parameter dictionary which contains parameters for scraper is None. '
                                    'Please parse it to this function.')

            city = param_dictionary['city']
            group_adults = param_dictionary['group_adults']
            group_children = param_dictionary['group_children']
            num_rooms = param_dictionary['num_rooms']
            selected_currency = param_dictionary['selected_currency']
            scrape_only_hotel = param_dictionary['scrape_only_hotel']
            sqlite_name = param_dictionary['sqlite_name']

            scraper = BasicGraphQLScraper(check_in=check_in, check_out=check_out, city=city, group_adults=group_adults,
                                          group_children=group_children, num_rooms=num_rooms,
                                          selected_currency=selected_currency,
                                          scrape_only_hotel=scrape_only_hotel, sqlite_name=sqlite_name, country=country)
            df = await scraper.scrape_graphql()

            if is_test:
                save_scraped_data(dataframe=df, db=test_db)
            else:
                save_scraped_data(dataframe=df, db=scraper.sqlite_name)
    else:
        main_logger.warning(f"Missing dates is None. No missing dates to scrape.")


@dataclass
class MissingDateChecker:
    """
    Scrape missing hotel booking dates from a database using a BasicGraphQLScraper.
    It only checks the data scraped today, UTC Time.

    Attributes:
        sqlite_name (str): Path to SQLite database.
        city (str): City where the hotels are located.
    """
    sqlite_name: str
    city: str

    def find_missing_dates_in_db(self) -> list:
        main_logger.info(f"Checking if all dates were scraped in {self.sqlite_name}...")
        missing_date_list = []

        with sqlite3.connect(self.sqlite_name) as con:
            main_logger.info(
                f'Get a distinct date count of each month for today scraped data, UTC time, for city {self.city}...')
            query = get_count_of_date_by_mth_asof_today_query()
            cursor = con.execute(query, (self.city,))
            result = cursor.fetchall()
            cursor.close()

            if not result:
                today = datetime.datetime.now(datetime.timezone.utc).date()
                main_logger.warning(f"No scraped data for today, {today}, UTC time for city {self.city}.")
                return missing_date_list

            today = datetime.datetime.today()
            year = today.year
            current_month = today.strftime('%Y-%m')

            for row in result:
                month_str, count = row
                date_obj = datetime.datetime.strptime(month_str, '%Y-%m')
                month = date_obj.month
                days_in_month = monthrange(year, month)[1]

                is_current_month = (month_str == current_month)
                expected_count = days_in_month - today.day + 1 if is_current_month else days_in_month

                if count == expected_count:
                    main_logger.info(f"All dates of {calendar.month_name[month]} {year} were scraped")
                else:
                    main_logger.warning(f"Not all dates of {calendar.month_name[month]} {year} were scraped")
                    dates_in_db, end_date, start_date = self.find_dates_of_the_month_in_db(days_in_month, month, year)
                    new_missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year)
                    missing_date_list.extend(new_missing_dates)
                    main_logger.warning(f"Missing dates in {start_date} to {end_date}: {new_missing_dates}")

        return missing_date_list

    def find_dates_of_the_month_in_db(self, days_in_month, month, year) -> tuple:
        """
        Find dates of the given month in the Database.
        :param days_in_month: Total days in the given month.
        :param month: Month.
        :param year: Year.

        :return: Tuple of (Dates in the database, End Date, Start Date).
                Date format for all values in the Tuple: '%Y-%m-%d'.
        """
        main_logger.info(f'Get dates of {calendar.month_name[month]} {year} in the database for {self.city}...')
        main_logger.info(f'As of today, UTC time')

        query = get_dates_of_each_month_asof_today_query()
        start_date = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
        end_date = datetime.datetime(year, month, days_in_month).strftime('%Y-%m-%d')

        with sqlite3.connect(self.sqlite_name) as con:
            cursor = con.execute(query, (start_date, end_date, self.city))
            result = cursor.fetchall()
            cursor.close()

        dates_in_db = set([row[0] for row in result])
        return dates_in_db, end_date, start_date


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parser to define SQLite database path.')
    parser.add_argument('--sqlite_name', type=str, default='avg_japan_hotel_price_test.db',
                        help='SQLite database path, default is "avg_japan_hotel_price_test.db"')
    parser.add_argument('--city', type=str, help='City where the hotels are located', required=True)
    parser.add_argument('--group_adults', type=int, default=1, help='Number of Adults, default is 1')
    parser.add_argument('--num_rooms', type=int, default=1, help='Number of Rooms, default is 1')
    parser.add_argument('--group_children', type=int, default=0, help='Number of Children, default is 0')
    parser.add_argument('--selected_currency', type=str, default='USD', help='Room price currency, default is "USD"')
    parser.add_argument('--scrape_only_hotel', type=bool, default=True, help='Whether to scrape only hotel properties, '
                                                                             'default is True')
    args = parser.parse_args()

    param_dict = {
        'city': args.city,
        'group_adults': args.group_adults,
        'num_rooms': args.num_rooms,
        'group_children': args.group_children,
        'selected_currency': args.selected_currency,
        'scrape_only_hotel': args.scrape_only_hotel,
        'sqlite_name': args.sqlite_name
    }

    db_path = args.sqlite_name
    missing_date_checker = MissingDateChecker(sqlite_name=db_path, city=args.city)
    missing_dates = missing_date_checker.find_missing_dates_in_db()
    asyncio.run(scrape_missing_dates(missing_dates, param_dictionary=param_dict))
