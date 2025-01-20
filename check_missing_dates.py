import argparse
import asyncio
import calendar
import datetime
import os
from calendar import monthrange
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, func, Engine, extract, Date, String, Row, FunctionElement
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import sessionmaker, Session

from japan_avg_hotel_price_finder.booking_details import BookingDetails
from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.date_utils.date_utils import format_date, calculate_check_out_date
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.sql.db_model import HotelPrice
from japan_avg_hotel_price_finder.sql.save_to_db import save_scraped_data

load_dotenv(dotenv_path='.env')

postgres_host = os.getenv('POSTGRES_HOST')
postgres_port = os.getenv('POSTGRES_PORT')
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_db = os.getenv('POSTGRES_DB')


def find_missing_dates(dates_in_db: set[str],
                       days_in_month: int,
                       month: int,
                       year: int,
                       today: datetime.datetime) -> list[str]:
    """
    Find missing dates of the given month.
    :param dates_in_db: Dates of that month in the database of the current AsOf Date.
                        Date format: '%Y-%m-%d'.
    :param days_in_month: Total days in the given month.
    :param month: Month.
    :param year: Year.
    :param today: Datetime object of today, used to find the missing dates.
    :returns: Missing Dates as a list.
    """
    main_logger.info(f"Find missing date of {calendar.month_name[month]} {year}.")

    # convert date string to a date object
    dates_in_db_date_obj = convert_to_date_obj(dates_in_db)

    # filter out past date
    filtered_dates = filter_past_date(dates_in_db_date_obj, today)

    today_date_obj: datetime.date = today.date()
    missing_dates_list: list[str] = []

    # find missing dates of the given month
    for day in range(1, days_in_month + 1):
        date_to_check: datetime.date = datetime.datetime(year, month, day).date()
        date_to_check_str: str = format_date(date_to_check)
        if date_to_check < today_date_obj:
            main_logger.warning(f"{date_to_check_str} has passed. Skip this date.")
        else:
            if date_to_check not in filtered_dates:
                missing_dates_list.append(date_to_check_str)

    return missing_dates_list


def convert_to_date_obj(dates_in_db: set[str]) -> list[datetime.date]:
    """
    Convert a list of date strings to date objects.
    :param dates_in_db: A set of date strings in 'YYYY-MM-DD' format.
    :return: A list of datetime.date objects corresponding to the input date strings.
    """
    dates_in_db_date_obj: list[datetime.date] = [datetime.datetime.strptime(date, '%Y-%m-%d').date()
                                                 for date in dates_in_db]
    return dates_in_db_date_obj


def filter_past_date(dates_in_db_date_obj: list[datetime.date], today: datetime.datetime) -> list[datetime.date]:
    """
    Filter out past dates from a list of dates.
    :param dates_in_db_date_obj: A list of date objects to filter.
    :param today: The reference date used for filtering.
    :return: A new list containing only the dates from the input list
             that are equal to or greater than the reference date.
    """
    filtered_dates: list[datetime.date] = [date for date in dates_in_db_date_obj if date >= today.date()]
    return filtered_dates


async def scrape_missing_dates(missing_dates_list: list[str] = None,
                               booking_details_class: 'BookingDetails' = None,
                               country: str = 'Japan',
                               engine: Engine = None) -> None:
    """
    Scrape missing dates with BasicScraper and load them into a database.
    :param missing_dates_list: Missing dates.
    :param booking_details_class: Dataclass of booking details as parameters, default is None.
    :param country: Country where the hotels are located, default is Japan.
    :param engine: SQLAlchemy engine.
    :return: None
    """
    main_logger.info("Scraping missing dates...")
    if missing_dates_list:
        for date in missing_dates_list:
            check_in: str = date
            check_in_date_obj = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date_obj: datetime.date = calculate_check_out_date(current_date=check_in_date_obj, nights=1)
            check_out: str = format_date(check_out_date_obj)

            if booking_details_class is None:
                main_logger.warning('The BookingDetailsParam class which contains attributes for scraper is None.')

            city = booking_details_class.city
            group_adults = booking_details_class.group_adults
            group_children = booking_details_class.group_children
            num_rooms = booking_details_class.num_rooms
            selected_currency = booking_details_class.selected_currency
            scrape_only_hotel = booking_details_class.scrape_only_hotel

            scraper = BasicGraphQLScraper(check_in=check_in, check_out=check_out, city=city, group_adults=group_adults,
                                          group_children=group_children, num_rooms=num_rooms,
                                          selected_currency=selected_currency,
                                          scrape_only_hotel=scrape_only_hotel, country=country)
            df = await scraper.scrape_graphql()

            save_scraped_data(dataframe=df, engine=engine)
    else:
        main_logger.warning("Missing dates is None. No missing dates to scrape.")


def get_date_count_by_month(session: Session, city: str, as_of: datetime.date = None) -> list[tuple[str, int]]:
    """
    Get a distinct date count of each month for today's scraped data, for a specific city.
    :param session: SQLAlchemy session
    :param city: City name.
    :param as_of: The date to filter AsOf by.
                    If None, use the current date.
    :return: List of tuples containing (month, count)
    """
    dialect = session.bind.dialect

    if isinstance(dialect, postgresql.dialect):
        # PostgreSQL version
        month_expr: FunctionElement = func.concat(
            extract('year', func.cast(HotelPrice.Date, Date)).cast(String),
            '-',
            func.lpad(extract('month', func.cast(HotelPrice.Date, Date)).cast(String), 2, '0')
        )
    elif isinstance(dialect, sqlite.dialect):
        # SQLite version
        month_expr: FunctionElement = func.strftime('%Y-%m', func.date(HotelPrice.Date))
    else:
        raise NotImplementedError(f"Unsupported dialect: {dialect}")

    query = (
        session.query(
            month_expr.label('month'),
            func.count(func.distinct(HotelPrice.Date)).label('count')
        )
        .filter(HotelPrice.City == city)
    )

    if as_of is not None:
        query = query.filter(func.date(HotelPrice.AsOf) == as_of)
    else:
        query = query.filter(func.date(HotelPrice.AsOf) == func.current_date())

    return query.group_by('month').all()


@dataclass
class MissingDateChecker:
    """
    Scrape missing hotel booking dates from a database using a BasicGraphQLScraper.
    It only checks the data scraped today, UTC Time.

    Attributes:
        city (str): City where the hotels are located.
        engine (Engine): SQLAlchemy engine.
    """
    city: str

    # sqlalchemy
    engine: Any = field(init=True)
    Session: Any = field(init=False)

    def __post_init__(self):
        self.Session = sessionmaker(bind=self.engine)

    def find_missing_dates_in_db(self, year: int) -> list[str]:
        """
        Find missing dates in the database using SQLAlchemy ORM.
        :param year: Year of the dates to check whether they are missing.
        :return: List of missing dates.
        """
        main_logger.info("Checking if all dates were scraped in a database...")
        missing_date_list: list[str] = []

        session = self.Session()
        try:
            main_logger.info(f'Get a distinct date count of each month for today scraped data, '
                             f'UTC time, for city {self.city}...')

            count_of_date_by_mth_as_of_today = get_date_count_by_month(session, self.city)

            if not count_of_date_by_mth_as_of_today:
                today = datetime.datetime.now(datetime.timezone.utc).date()
                main_logger.warning(f"No scraped data for today, {today}, UTC time for city {self.city} in  a database")
                return missing_date_list

            today = datetime.datetime.today()
            current_month: str = today.strftime('%Y-%m')

            self.check_missing_dates(count_of_date_by_mth_as_of_today, current_month, missing_date_list, today, year)
        except Exception as e:
            main_logger.error(f"An error occurred while querying the database: {str(e)}")
            return missing_date_list
        finally:
            session.close()

        return missing_date_list

    def check_missing_dates(self,
                            count_of_date_by_mth_as_of_today_list: list[tuple],
                            current_month: str,
                            missing_date_list: list[str],
                            today: datetime,
                            year: int) -> None:
        """
        Check missing dates of each month.
        :param count_of_date_by_mth_as_of_today_list: Count of dates by month as of today as a list of Tuple.
        :param current_month: Current month.
        :param missing_date_list: List of missing dates.
        :param today: Today's date used to check missing dates.
        :param year: Year of the dates to check whether they are missing.
        :return: None
        """
        main_logger.info(f"Check missing dates of each month in the database for {self.city}...")
        for row in count_of_date_by_mth_as_of_today_list:
            month_str, count = row[:2]
            date_obj = datetime.datetime.strptime(month_str, '%Y-%m')
            month: int = date_obj.month
            days_in_month: int = monthrange(year, month)[1]

            is_current_month: bool = (month_str == current_month)
            expected_count = days_in_month - today.day + 1 if is_current_month else days_in_month

            if count == expected_count:
                main_logger.info(f"All dates of {calendar.month_name[month]} {year} were scraped")
            else:
                main_logger.warning(f"Not all dates of {calendar.month_name[month]} {year} were scraped")
                dates_in_db, end_date, start_date = self.find_dates_of_the_month_in_db(days_in_month, month, year)
                new_missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year, today)
                missing_date_list.extend(new_missing_dates)
                main_logger.warning(f"Missing dates in {start_date} to {end_date}: {new_missing_dates}")

    def find_dates_of_the_month_in_db(self, days_in_month: int, month: int, year: int) -> tuple[set[str], str, str]:
        """
        Find dates of the given month in the Database.
        :param days_in_month: Total days in the given month.
        :param month: Month.
        :param year: Year.
        :return: Tuple of (Dates in the database, End Date, Start Date).
                Date format for all values in the Tuple: '%Y-%m-%d'.
        """
        main_logger.info(f'Get dates of {calendar.month_name[month]} {year} in the database for {self.city}...')
        main_logger.info('As of today, UTC time')

        start_date: str = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
        end_date: str = datetime.datetime(year, month, days_in_month).strftime('%Y-%m-%d')

        session = self.Session()
        try:
            result = get_dates_in_db(session=session, start_date=start_date, end_date=end_date, city=self.city)
            dates_in_db: set[str] = set(row.Date for row in result)
            return dates_in_db, end_date, start_date
        finally:
            session.close()


def get_dates_in_db(session: Session, start_date: str, end_date: str, city: str, as_of: datetime.date = None) -> list[Row]:
    """
    Retrieve dates from the database for a specific date range and city.
    :param session: SQLAlchemy session
    :param start_date: Start date of the range (format: 'YYYY-MM-DD')
    :param end_date: End date of the range (format: 'YYYY-MM-DD')
    :param city: City name
    :param as_of: The date to filter AsOf by.
                    If None, use the current date.
    :return: List of query results containing dates
    """
    dialect = session.bind.dialect

    if isinstance(dialect, postgresql.dialect):
        # PostgreSQL version
        date_expr: FunctionElement = func.to_char(func.cast(HotelPrice.Date, Date), 'YYYY-MM-DD')
    elif isinstance(dialect, sqlite.dialect):
        # SQLite version
        date_expr: FunctionElement = func.strftime('%Y-%m-%d', func.date(HotelPrice.Date))
    else:
        raise NotImplementedError(f"Unsupported dialect: {dialect}")

    query = (
        session.query(date_expr.label('Date'))
        .filter(HotelPrice.Date.between(start_date, end_date))
        .filter(HotelPrice.City == city)
    )

    if as_of is not None:
        query = query.filter(func.date(HotelPrice.AsOf) == as_of)
    else:
        query = query.filter(func.date(HotelPrice.AsOf) == func.current_date())

    return query.group_by(HotelPrice.Date).all()


def parse_arguments() -> argparse.Namespace:
    """
    Parse the command line arguments
    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='Parser which controls Missing Date Checker.')
    parser.add_argument('--city', type=str, help='City where the hotels are located', required=True)
    parser.add_argument('--group_adults', type=int, default=1, help='Number of Adults, default is 1')
    parser.add_argument('--num_rooms', type=int, default=1, help='Number of Rooms, default is 1')
    parser.add_argument('--group_children', type=int, default=0, help='Number of Children, default is 0')
    parser.add_argument('--selected_currency', type=str, default='USD',
                        help='Room price currency, default is "USD"')
    parser.add_argument('--scrape_only_hotel', type=bool, default=True,
                        help='Whether to scrape only hotel properties, default is True')
    parser.add_argument('--year', type=int, default=datetime.datetime.today().year,
                        help='Year of the dates to check whether they are missing, default is the current year.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    booking_details = BookingDetails(city=args.city, group_adults=args.group_adults,
                                     num_rooms=args.num_rooms, group_children=args.group_children,
                                     selected_currency=args.selected_currency,
                                     scrape_only_hotel=args.scrape_only_hotel)

    postgres_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    engine = create_engine(postgres_url)
    missing_date_checker = MissingDateChecker(engine=engine, city=args.city)
    missing_dates: list[str] = missing_date_checker.find_missing_dates_in_db(year=args.year)
    asyncio.run(scrape_missing_dates(missing_dates, booking_details_class=booking_details, engine=engine))
