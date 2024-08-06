import datetime
import os

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.migrate_to_sqlite import migrate_data_to_sqlite


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

    today_date = today.date()

    try:
        entered_date = datetime.date(year, month, day)
        if entered_date < today_date:
            return True
        else:
            return False
    except ValueError:
        main_logger.error("Invalid date. Returning False")
        return False


def get_count_of_date_by_mth_asof_today_query():
    """
    Return SQLite query to count distinct dates for each month from the HotelPrice table, where the AsOf date is today.
    :returns: SQLite query.
    """
    query = '''
        SELECT strftime('%Y-%m', Date) AS Month, count(distinct Date) AS DistinctDateCount, date(AsOf) AS AsOfDate
        FROM HotelPrice
        WHERE AsOf LIKE date('now') || '%'
        GROUP BY Month;
        '''
    return query


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

    main_logger.info("Find all .csv files in the directory and its subdirectories")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                main_logger.debug(f'Found CSV file: {file}')
                csv_files.append(os.path.join(root, file))

    return csv_files


def convert_csv_to_df(csv_files: list) -> pd.DataFrame:
    """
    Convert CSV files to Pandas DataFrame.
    :param csv_files: List of CSV files.
    :returns: Pandas DataFrame.
    """
    main_logger.info("Converting CSV files to Pandas DataFrame...")
    df_list = []
    for csv_file in csv_files:
        main_logger.info(f'Convert CSV: {csv_file} to DataFrame.')
        df = pd.read_csv(csv_file)
        df_list.append(df)

    if df_list:
        return pd.concat(df_list)


def save_scraped_data(dataframe: pd.DataFrame, db: str) -> None:
    """
    Save scraped data to SQLite database.
    :param dataframe: Pandas DataFrame.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Saving scraped data...")
    if not dataframe.empty:
        main_logger.info(f'Save data to SQLite database: {db}')
        migrate_data_to_sqlite(dataframe, db)
    else:
        main_logger.warning('The dataframe is empty. No data to save')
