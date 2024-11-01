from unittest.mock import patch

import pandas as pd
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from japan_avg_hotel_price_finder.sql.save_to_db import migrate_data_to_database
from japan_avg_hotel_price_finder.sql.db_model import Base, HotelPrice


@pytest.fixture
def sqlite_engine(tmp_path):
    db = tmp_path / 'test_successful_connection_to_sqlite.db'
    engine = create_engine(f'sqlite:///{db}')
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(sqlite_engine):
    Session = sessionmaker(bind=sqlite_engine)
    return Session()


def test_successful_connection_to_sqlite(sqlite_engine, db_session):
    # Given
    df_filtered = pd.DataFrame({
        'Hotel': ['Hotel A', 'Hotel B'],
        'Price': [100, 150],
        'Review': [4.5, 3.8],
        'Price/Review': [22.2, 39.5],
        'Location': ['San Francisco', 'San Francisco'],
        'City': ['City X', 'City Y'],
        'Date': ['2022-01-01', '2022-01-02'],
        'AsOf': [pd.Timestamp('2022-01-01'), pd.Timestamp('2022-01-02')]
    })

    # When
    migrate_data_to_database(df_filtered, sqlite_engine)

    # Then
    inspector = inspect(sqlite_engine)
    assert 'HotelPrice' in inspector.get_table_names()

    result = db_session.query(HotelPrice).all()
    assert len(result) > 0


@patch('japan_avg_hotel_price_finder.sql.save_to_db.create_avg_hotel_price_by_dow_table')
@patch('japan_avg_hotel_price_finder.sql.save_to_db.create_avg_hotel_room_price_by_date_table')
@patch('japan_avg_hotel_price_finder.sql.save_to_db.create_avg_room_price_by_review_table')
@patch('japan_avg_hotel_price_finder.sql.save_to_db.create_avg_hotel_price_by_month_table')
@patch('japan_avg_hotel_price_finder.sql.save_to_db.create_avg_room_price_by_location')
def test_handle_empty_dataframe(mock_location, mock_month, mock_review, mock_date, mock_dow, sqlite_engine, db_session):
    # Given
    df_filtered = pd.DataFrame(columns=['Hotel', 'Price', 'Review', 'Location', 'Price/Review', 'City', 'Date', 'AsOf'])

    # When
    migrate_data_to_database(df_filtered, sqlite_engine)

    # Then
    inspector = inspect(sqlite_engine)
    assert 'HotelPrice' in inspector.get_table_names()

    result = db_session.query(HotelPrice).all()
    assert len(result) == 0

    # Assert that all the aggregation functions were called
    mock_dow.assert_called_once()
    mock_date.assert_called_once()
    mock_review.assert_called_once()
    mock_month.assert_called_once()
    mock_location.assert_called_once()