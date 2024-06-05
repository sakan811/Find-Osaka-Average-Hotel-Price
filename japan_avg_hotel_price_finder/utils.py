import calendar
import os
import sqlite3
from calendar import monthrange
import datetime
from typing import LiteralString

import pandas as pd
from loguru import logger

from japan_avg_hotel_price_finder.scrape import BasicScraper
from set_details import Details


def check_if_current_date_has_passed(year, month, day):
    """
    Check if the current date has passed the given day of the month.
    :param year: The year of the date to check.
    :param month: The month of the date to check.
    :param day: The day of the month to check.
    :return: True if the current date has passed the given day, False otherwise.
    """
    today_for_check = datetime.datetime.today().strftime('%Y-%m-%d')
    current_date_for_check = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
    if current_date_for_check < today_for_check:
        return True
    else:
        return False


def find_missing_dates_in_db(sqlite: str) -> list:
    """
    Find the missing dates in the SQlite database that were scraped today.
    Only check for the data that were scraped today.
    :param sqlite: Path to the SQLite database.
    :returns: List of missing dates of each month.
    """
    logger.info("Checking if all date was scraped...")
    with sqlite3.connect(sqlite) as con:
        query = get_count_of_date_by_mth_asof_today_query()
        result = con.execute(query).fetchall()

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
                    dates_in_db, end_date, start_date = find_dates_of_the_month_in_db(con, days_in_month, month, year)

                    missing_dates = find_missing_dates(dates_in_db, days_in_month, start_date, end_date, today, month,
                                                       year)
            else:
                date_obj = datetime.datetime.strptime(row[0], '%Y-%m')
                month = date_obj.month
                days_in_month = monthrange(year, month)[1]
                if days_in_month == row[1]:
                    logger.info(f"All date of {calendar.month_name[month]} {year} was scraped")
                else:
                    logger.warning(f"Not all date of {calendar.month_name[month]} {year} was scraped")
                    dates_in_db, end_date, start_date = find_dates_of_the_month_in_db(con, days_in_month, month, year)

                    missing_dates = find_missing_dates(dates_in_db, days_in_month, start_date, end_date, today, month,
                                                       year)

    return missing_dates


def check_db_if_all_date_was_scraped(db) -> None:
    """
    Check inside the SQLite database if all dates of each month were scraped today.
    :param db: Path to the SQLite database.
    :returns: None
    """
    logger.info(f"Checking in the SQLite database '{db}' if any date was not scraped today...")
    missing_dates = find_missing_dates_in_db(db)
    scrape_missing_dates(missing_dates, to_sqlite=True)


def check_csv_if_all_date_was_scraped() -> None:
    """
    Check inside the CSV files directory if all dates of each month were scraped today.
    :returns: None
    """
    directory = 'scraped_hotel_data_csv'
    logger.info(f"Checking CSV files in the {directory} directory if all date was scraped today...")
    temp_db = 'temp_db.db'
    try:
        csv_files: list = find_csv_files(directory)
        df = convert_csv_to_df(csv_files)

        logger.info("Create a temporary SQLite database to insert the data to check if all date was scraped today.")
        with sqlite3.connect(temp_db) as con:
            df.to_sql('HotelPrice', con, if_exists='replace', index=False)

        missing_dates = find_missing_dates_in_db(temp_db)
        scrape_missing_dates(missing_dates)
    except FileNotFoundError as e:
        logger.error(e)
        logger.error(f"{directory} folder not found.")
    finally:
        logger.info("Delete the temporary SQLite database file")
        if os.path.exists(temp_db):
            os.remove(temp_db)
            logger.info("Temporary database deleted.")


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


def scrape_with_basic_scraper(date, to_sqlite: bool = False):
    """
    Scrape the date with BasicScraper.
    :param date: The given date to scrape.
    :param to_sqlite: If True, load the data to the SQLite database, else save to CSV.
                    Set to False as default.
    :return: None
    """
    logger.info("Scrape the date with BasicScraper.")
    check_in = date
    check_out_datetime_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
    check_out = (check_out_datetime_obj + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    details = Details(check_in=check_in, check_out=check_out)
    scraper = BasicScraper(details)
    scraper.start_scraping_process(details.check_in, details.check_out, to_sqlite)


def find_missing_dates(dates_in_db, days_in_month, start_date, end_date, today, month, year):
    """
    Find missing dates of the given month.
    :param dates_in_db: Dates of that month in the database of the current AsOf Date.
    :param days_in_month: Total days in the given month.
    :param start_date: First day of the month.
    :param end_date: Last day of the month.
    :param today: Today's date as a Datetime object.
    :param month: Month.
    :param year: Year.
    :returns: Missing Dates as a list.
    """
    logger.info(f"Find missing date of {calendar.month_name[month]} {year}.")
    missing_dates = []
    for day in range(1, days_in_month + 1):
        date_str = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
        if date_str not in dates_in_db:
            if month == today.month:
                # Handle the case when the month to scrape is the current month.
                if day < today.day:
                    logger.warning(f"This day has passed. Skip {date_str}")
                else:
                    missing_dates.append(date_str)
            else:
                missing_dates.append(date_str)
    logger.warning(f"Missing dates in {start_date} to {end_date}: {missing_dates}")
    return missing_dates


def find_dates_of_the_month_in_db(con, days_in_month, month, year) -> tuple:
    """
    Find Dates of the month on the Database.

    :param con: Sqlite3 Connection.
    :param days_in_month: Total days in the given month.
    :param month: Month.
    :param year: Year.

    :return: Tuple of (Dates, End Date, Start Date).
    """
    query = get_dates_of_each_month_asof_today_query()
    start_date = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime.datetime(year, month, days_in_month).strftime('%Y-%m-%d')
    result = con.execute(query, (start_date, end_date)).fetchall()
    dates_in_db = set([row[0] for row in result])
    return dates_in_db, end_date, start_date


def scrape_missing_dates(missing_dates: list, to_sqlite: bool = False):
    """
    Scrape missing dates with BasicScraper.
    :param missing_dates: Missing dates.
    :param to_sqlite: If True, load the data to the SQLite database, else save to CSV.
                Set to False as default.
    :return: None
    """
    if missing_dates:
        for date in missing_dates:
            scrape_with_basic_scraper(date, to_sqlite)
    else:
        logger.warning("No missing dates to scrape.")


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


def find_csv_files(directory) -> list[LiteralString | str | bytes]:
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

    return pd.concat(df_list)
