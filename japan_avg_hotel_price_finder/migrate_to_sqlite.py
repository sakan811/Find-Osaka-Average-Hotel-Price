import sqlite3

import pandas as pd
from loguru import logger


def migrate_data_to_sqlite(df_filtered: pd.DataFrame) -> None:
    """
    Migrate hotel data to sqlite database.
    :param df_filtered: pandas dataframe.
    :return: None
    """
    logger.info('Connecting to SQLite database (or create it if it doesn\'t exist)...')

    db = 'avg_japan_hotel_price.db'
    with sqlite3.connect(db) as con:
        query = '''
        CREATE TABLE IF NOT EXISTS HotelPrice (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Hotel TEXT ,
            Price REAL,
            Review REAL,
            "Price/Review" REAL,
            City TEXT,
            Date TEXT 
        )
        '''

        con.execute(query)

        data_type = {
            'Hotel': 'text primary key',
            'Price': 'real',
            'Review': 'real',
            'Price/Review': 'real',
            'City': 'text',
            'Date': 'text'
        }

        # Save the DataFrame to a table named 'HotelPrice'
        df_filtered.to_sql('HotelPrice', con=con, if_exists='append', index=False, dtype=data_type)

        logger.info(f'Data has been saved to {db}')

        create_average_room_price_by_date_view(db)


def create_average_room_price_by_date_view(db: str) -> None:
    """
    Create AverageRoomPriceByDate view
    :param db: SQLite database path
    :return: None
    """
    with sqlite3.connect(db) as con:
        query = '''
        CREATE VIEW IF NOT EXISTS AverageRoomPriceByDate AS 
        select Date, avg(Price) as AveragePrice, City
        from HotelPrice
        GROUP BY Date
        '''
        con.execute(query)


if __name__ == '__main__':
    pass
