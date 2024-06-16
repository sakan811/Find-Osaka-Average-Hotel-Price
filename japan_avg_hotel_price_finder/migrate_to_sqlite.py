#    Copyright 2024 Sakan Nirattisaykul
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import sqlite3

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from set_details import Details


logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')


def migrate_data_to_sqlite(df_filtered: pd.DataFrame, details: Details) -> None:
    """
    Migrate hotel data to sqlite database.
    :param df_filtered: pandas dataframe.
    :param details: Details dataclass object.
    :return: None
    """
    logger.info('Connecting to SQLite database (or create it if it doesn\'t exist)...')

    db = details.sqlite_name
    with sqlite3.connect(db) as con:
        con.execute("PRAGMA journal_mode=WAL")

        query = '''
        CREATE TABLE IF NOT EXISTS HotelPrice (
            ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Hotel TEXT NOT NULL,
            Price REAL NOT NULL,
            Review REAL NOT NULL,
            "Price/Review" REAL NOT NULL,
            City TEXT NOT NULL,
            Date TEXT NOT NULL,
            AsOf TEXT NOT NULL
        )
        '''

        con.execute(query)

        hotel_price_dtype: dict = get_hotel_price_dtype()

        # Save the DataFrame to a table named 'HotelPrice'
        df_filtered.to_sql('HotelPrice', con=con, if_exists='append', index=False, dtype=hotel_price_dtype)

        logger.info(f'Data has been saved to {db}')

        create_average_room_price_by_date_view(db)


def get_hotel_price_dtype() -> dict:
    """
    Get HotelPrice datatype.
    :return: HotelPrice datatype.
    """
    logger.info('Get HotelPrice datatype...')
    hotel_price_dtype = {
        'Hotel': 'text not null primary key',
        'Price': 'real not null',
        'Review': 'real not null',
        'Price/Review': 'real not null',
        'City': 'text not null',
        'Date': 'text not null',
        'AsOf': 'text not null'
    }
    return hotel_price_dtype


def create_average_room_price_by_date_view(db: str) -> None:
    """
    Create AverageRoomPriceByDate view
    :param db: SQLite database path
    :return: None
    """
    with sqlite3.connect(db) as con:
        con.execute("PRAGMA journal_mode=WAL")
        query = '''
        CREATE VIEW IF NOT EXISTS AverageRoomPriceByDate AS 
        select Date, avg(Price) as AveragePrice, City
        from HotelPrice
        GROUP BY Date
        '''
        con.execute(query)


if __name__ == '__main__':
    pass
