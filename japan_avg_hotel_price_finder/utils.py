import calendar
import datetime
import os
import sqlite3
from calendar import monthrange

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.migrate_to_sqlite import migrate_data_to_sqlite
from japan_avg_hotel_price_finder.scrape import BasicScraper
from set_details import Details

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')


def check_if_current_date_has_passed(year: int, month: int, day: int, timezone=None) -> bool:
    """
    Check if the current date has passed the given day of the month.
    :param year: The year of the date to check.
    :param month: The month of the date to check.
    :param day: The day of the month to check.
    :param timezone: Set timezone.
                    Default is None.
    :return: True if the current date has passed the given day, False otherwise.
    """
    if timezone is not None:
        today = datetime.datetime.now(timezone)
    else:
        today = datetime.datetime.today()
    today_for_check = today.strftime('%Y-%m-%d')

    try:
        current_date_for_check = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
        if current_date_for_check < today_for_check:
            return True
        else:
            return False
    except ValueError:
        logger.error("Invalid date. Returning False")
        return False


def find_missing_dates_in_db(sqlite_db: str) -> list:
    """
    Find the missing dates in the SQlite database that were scraped today.
    Only check for the data that were scraped today.
    :param sqlite_db: Path to the SQLite database.
    :returns: List of missing dates of each month.
    """
    logger.info("Checking if all date was scraped...")
    missing_dates = []
    with sqlite3.connect(sqlite_db) as con:
        query = get_count_of_date_by_mth_asof_today_query()
        cursor = con.execute(query)
        result = cursor.fetchall()
        cursor.close()

        today = datetime.datetime.today()
        year = today.year
        formatted_today = today.strftime('%Y-%m')
        for row in result:
            if row[0] == formatted_today:
                month = today.month
                today_date = today.day
                days_in_month = monthrange(year, month)[1]
                scraped_date = days_in_month - today_date + 1
                if scraped_date == row[1]:
                    logger.info(f"All date of {calendar.month_name[month]} {year} was scraped")
                else:
                    logger.warning(f"Not all date of {calendar.month_name[month]} {year} was scraped")
                    dates_in_db, end_date, start_date = find_dates_of_the_month_in_db(sqlite_db, days_in_month, month,
                                                                                      year)

                    missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year)
                    logger.warning(f"Missing dates in {start_date} to {end_date}: {missing_dates}")
            else:
                date_obj = datetime.datetime.strptime(row[0], '%Y-%m')
                month = date_obj.month
                days_in_month = monthrange(year, month)[1]
                if days_in_month == row[1]:
                    logger.info(f"All date of {calendar.month_name[month]} {year} was scraped")
                else:
                    logger.warning(f"Not all date of {calendar.month_name[month]} {year} was scraped")
                    dates_in_db, end_date, start_date = find_dates_of_the_month_in_db(sqlite_db, days_in_month, month,
                                                                                      year)

                    missing_dates = find_missing_dates(dates_in_db, days_in_month, month, year)
                    logger.warning(f"Missing dates in {start_date} to {end_date}: {missing_dates}")

    return missing_dates


def check_in_db_if_all_date_was_scraped(db: str, to_sqlite: bool = False) -> None:
    """
    Check inside the SQLite database if all dates of each month were scraped today.
    :param db: Path to the SQLite database.
    :param to_sqlite: If True, after scraping the missing dates, load the scraped data to the SQLite database,
                    else save to CSV.
    :returns: None.
    """
    logger.info(f"Checking in the SQLite database '{db}' if any date was not scraped today...")
    missing_dates = find_missing_dates_in_db(db)
    scrape_missing_dates(db=db, missing_dates=missing_dates, to_sqlite=to_sqlite)


def check_in_csv_dir_if_all_date_was_scraped(directory: str = 'scraped_hotel_data_csv') -> None:
    """
    Check inside the CSV files directory if all dates of each month were scraped today.
    :param directory: Path to the CSV files directory.
                    Default is 'scraped_hotel_data_csv' folder.
    :returns: None
    """
    logger.info(f"Checking CSV files in the {directory} directory if all date was scraped today...")
    temp_db = 'temp_db.db'
    try:
        csv_files: list = find_csv_files(directory)
        if csv_files:
            df = convert_csv_to_df(csv_files)

            logger.info("Create a temporary SQLite database to insert the data to check if all date was scraped today.")

            with sqlite3.connect(temp_db) as con:
                df.to_sql('HotelPrice', con, if_exists='replace', index=False)

            check_in_db_if_all_date_was_scraped(temp_db)
        else:
            logger.warning("No CSV files were found")
    except FileNotFoundError as e:
        logger.error(e)
        logger.error(f"{directory} folder not found.")
    except Exception as e:
        logger.error(e)
        logger.error(f"An unexpected error occurred")

    if os.path.exists(temp_db):
        try:
            os.remove(temp_db)
            logger.info("Temporary database deleted.")
        except PermissionError as e:
            logger.error(e)
            logger.error(f"Could not remove {temp_db}. it is being used by another process.")
            logger.info("Truncate the HotelPrice table in the temporary database.")
            with sqlite3.connect(temp_db) as con:
                con.execute("DELETE FROM HotelPrice")
            logger.warning("Please delete the temporary database manually after the web-scraping process finishes.")


def get_count_of_date_by_mth_asof_today_query():
    """
    Query a count of dates of each month, where the AsOf is today.
    returns: SQLite query.
    """
    query = '''
        SELECT strftime('%Y-%m', Date) AS Month, count(distinct Date) AS DistinctDateCount, date(AsOf) AS AsOfDate
        FROM HotelPrice
        WHERE AsOf LIKE date('now') || '%'
        GROUP BY Month;
        '''
    return query


def scrape_with_basic_scraper(db: str, date, to_sqlite: bool = False):
    """
    Scrape the date with BasicScraper.
    :param db: SQLite database path.
    :param date: The given date to scrape.
    :param to_sqlite: If True, load the data to the SQLite database, else save to CSV.
                    Set to False as default.
    :return: None
    """
    logger.info("Scrape the date with BasicScraper.")
    check_in = date
    check_out_datetime_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
    check_out = (check_out_datetime_obj + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    details = Details(check_in=check_in, check_out=check_out, sqlite_name=db)
    scraper = BasicScraper(details)
    if to_sqlite:
        data_tuple = scraper.start_scraping_process(details.check_in, details.check_out)
        df = data_tuple[0]
        save_scraped_data(dataframe=df, details_dataclass=details, to_sqlite=to_sqlite)
    else:
        df, city, check_in, check_out = scraper.start_scraping_process(details.check_in, details.check_out)
        save_scraped_data(dataframe=df, city=city, check_in=check_in,
                          check_out=check_out)


def find_missing_dates(
        dates_in_db: set[str],
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
    logger.info(f"Find missing date of {calendar.month_name[month]} {year}.")
    if timezone:
        today = datetime.datetime.now(timezone)
    else:
        today = datetime.datetime.today()

    dates_in_db_date_obj = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in dates_in_db]
    filtered_dates = [date for date in dates_in_db_date_obj if date >= today.date()]

    today_date_obj = today.date()
    missing_dates = []
    for day in range(1, days_in_month + 1):
        date_to_check = datetime.datetime(year, month, day)
        date_to_check_str = date_to_check.strftime('%Y-%m-%d')
        date_to_check_date_obj = date_to_check.date()
        if date_to_check_date_obj < today_date_obj:
            logger.warning(f"{date_to_check_str} has passed. Skip this date.")
        else:
            if date_to_check_date_obj not in filtered_dates:
                missing_dates.append(date_to_check_str)
    return missing_dates


def find_dates_of_the_month_in_db(db: str, days_in_month, month, year) -> tuple:
    """
    Find Dates of the month on the Database.

    :param db: Sqlite database path.
    :param days_in_month: Total days in the given month.
    :param month: Month.
    :param year: Year.

    :return: Tuple of (Dates in the database, End Date, Start Date).
            Date format for all values in the Tuple: '%Y-%m-%d'.
    """
    query = get_dates_of_each_month_asof_today_query()
    start_date = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime.datetime(year, month, days_in_month).strftime('%Y-%m-%d')

    with sqlite3.connect(db) as con:
        cursor = con.execute(query, (start_date, end_date))
        result = cursor.fetchall()
        cursor.close()

    dates_in_db = set([row[0] for row in result])
    return dates_in_db, end_date, start_date


def scrape_missing_dates(db: str = None, missing_dates: list = None, to_sqlite: bool = False):
    """
    Scrape missing dates with BasicScraper.
    :param db: SQLite database path.
    :param missing_dates: Missing dates.
    :param to_sqlite: If True, load the data to the SQLite database, else save to CSV.
                Set to False as default.
    :return: None
    """
    if missing_dates:
        for date in missing_dates:
            scrape_with_basic_scraper(db, date, to_sqlite)
    else:
        logger.warning(f"Missing dates is None. No missing dates to scrape.")


def get_dates_of_each_month_asof_today_query():
    """
    Query dates of each month, where the AsOf is today.
    returns: SQLite query.
    """
    query = '''
                    SELECT strftime('%Y-%m-%d', Date) AS Date, date(AsOf) AS AsOfDate
                    FROM HotelPrice
                    WHERE AsOf LIKE date('now') || '%' and Date BETWEEN ? AND ?
                    GROUP BY Date;
                    '''
    return query


def find_csv_files(directory) -> list:
    """
    Find CSV files in the given directory.
    :param directory: Directory to find CSV files.
    :returns: List of CSV files.
    """
    csv_files = []

    logger.info("Find all .csv files in the directory and its subdirectories")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))

    return csv_files


def convert_csv_to_df(csv_files: list) -> pd.DataFrame:
    """
    Convert CSV files to Pandas DataFrame.
    :param csv_files: List of CSV files.
    :returns: Pandas DataFrame.
    """
    logger.info("Converting CSV files to Pandas DataFrame...")
    df_list = []
    for csv_file in csv_files:
        logger.info(f'Convert CSV: {csv_file} to DataFrame.')
        df = pd.read_csv(csv_file)
        df_list.append(df)

    if df_list:
        return pd.concat(df_list)


def save_scraped_data(
        dataframe: pd.DataFrame,
        details_dataclass: Details = None,
        city: str = None,
        check_in: str = None,
        check_out: str = None,
        month: int = None,
        year: int = None,
        to_sqlite: bool = False,
        save_dir='scraped_hotel_data_csv') -> None:
    """
    Save scraped data to CSV or SQLite database.
    The CSV files directory is created automatically if it doesn't exist.
    The default CSV files directory name is depended on the default value of 'save_dir' parameter.
    :param dataframe: Pandas DataFrame.
    :param details_dataclass: Details dataclass object.
                            Only needed if saving to SQLite database.
    :param city: City where the hotels are located.
                Only needed if saving to CSV file.
    :param check_in: Check-in date.
                    Only needed if saving to CSV file for Basic Scraper.
    :param check_out: Check-out date.
                    Only needed if saving to CSV file for Basic Scraper.
    :param month: Month number.
                Only needed if saving to CSV file for Thread Pool Scraper.
    :param year: Year.
                Only needed if saving to CSV file for Thread Pool Scraper.
    :param to_sqlite: If True, save the scraped data to a SQLite database, else save it to CSV.
    :param save_dir: Directory to save the scraped data as CSV.
                    Default is 'scraped_hotel_data_csv' folder.
    :return: None
    """
    logger.info("Saving scraped data...")
    if not dataframe.empty:
        if to_sqlite:
            logger.info('Save data to SQLite database')
            migrate_data_to_sqlite(dataframe, details_dataclass)
        else:
            logger.info('Save data to CSV')
            try:
                # Attempt to create the directory
                os.makedirs(save_dir)
                logger.info(f'Created {save_dir} directory')
            except FileExistsError:
                # If the directory already exists, log a message and continue
                logger.error(f'FileExistsError: {save_dir} directory already exists')

            if city and month and year:
                month_name = calendar.month_name[month]
                file_path = os.path.join(save_dir, f'{city}_hotel_data_{month_name}_{year}.csv')
                dataframe.to_csv(file_path, index=False)
            elif city and check_in and check_out:
                file_path = os.path.join(save_dir, f'{city}_hotel_data_{check_in}_to_{check_out}.csv')
                dataframe.to_csv(file_path, index=False)
            else:
                logger.warning("Cannot save data to CSV. "
                               "If a basic scraper was used, please enter city, check-in or check-out date. "
                               "If a thread pool scraper was used, please enter month and year. ")
    else:
        logger.warning('The dataframe is empty. No data to save')
