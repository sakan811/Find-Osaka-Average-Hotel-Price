import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.sql.migrate_to_sqlite import migrate_data_to_sqlite


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