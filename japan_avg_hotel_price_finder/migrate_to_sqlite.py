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
from loguru import logger

from set_details import Details


def migrate_data_to_sqlite(df_filtered: pd.DataFrame) -> None:
    """
    Migrate hotel data to sqlite database.
    :param df_filtered: pandas dataframe.
    :return: None
    """
    logger.info('Connecting to SQLite database (or create it if it doesn\'t exist)...')

    db = Details.sqlite_name
    with sqlite3.connect(db) as con:
        query = '''
        CREATE TABLE IF NOT EXISTS HotelPrice (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Hotel TEXT,
            Price REAL,
            Review REAL,
            "Price/Review" REAL,
            City TEXT,
            Date TEXT,
            AsOf TEXT
        )
        '''

        con.execute(query)

        data_type = {
            'Hotel': 'text primary key',
            'Price': 'real',
            'Review': 'real',
            'Price/Review': 'real',
            'City': 'text',
            'Date': 'text',
            'AsOf': 'text'
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
