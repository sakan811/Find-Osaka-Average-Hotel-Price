import sqlite3

import pandas as pd

from japan_avg_hotel_price_finder.sql.migrate_to_sqlite import migrate_data_to_sqlite


def test_successful_connection_to_sqlite():
    # Given
    df_filtered = pd.DataFrame({
        'Hotel': ['Hotel A', 'Hotel B'],
        'Price': [100, 150],
        'Review': [4.5, 3.8],
        'Price/Review': [22.2, 39.5],
        'Location': ['San Francisco', 'San Francisco'],
        'City': ['City X', 'City Y'],
        'Date': ['2022-01-01', '2022-01-02'],
        'AsOf': ['2022-01-01', '2022-01-02']
    })
    db = 'test_successful_connection_to_sqlite.db'

    # When
    migrate_data_to_sqlite(df_filtered, db)

    # Then
    with sqlite3.connect(db) as con:
        result = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='HotelPrice';").fetchone()
        assert result is not None
        result = con.execute("SELECT * FROM HotelPrice;").fetchall()
        assert len(result) > 0


def test_handle_empty_dataframe():
    # Given
    df_filtered = pd.DataFrame(columns=['Hotel', 'Price', 'Review', 'Location', 'Price/Review', 'City', 'Date', 'AsOf'])
    db = 'test_handle_empty_dataframe.db'

    # When
    migrate_data_to_sqlite(df_filtered, db)

    # Then
    with sqlite3.connect(db) as con:
        result = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='HotelPrice';").fetchone()
        assert result is not None
        result = con.execute("SELECT * FROM HotelPrice;").fetchall()
        assert len(result) == 0