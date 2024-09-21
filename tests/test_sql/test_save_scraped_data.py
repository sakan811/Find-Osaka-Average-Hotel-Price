import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from japan_avg_hotel_price_finder.sql.save_to_db import save_scraped_data

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'hotel_name': ['Hotel A', 'Hotel B'],
        'price': [100, 200]
    })

@pytest.fixture
def empty_dataframe():
    return pd.DataFrame()

@patch('japan_avg_hotel_price_finder.sql.save_to_db.main_logger')
@patch('japan_avg_hotel_price_finder.sql.save_to_db.migrate_data_to_sqlite')
def test_save_scraped_data_non_empty(mock_migrate, mock_logger, sample_dataframe):
    db_path = 'test_db.sqlite'
    save_scraped_data(sample_dataframe, db_path)
    mock_logger.info.assert_called_with(f'Save data to SQLite database: {db_path}')
    mock_migrate.assert_called_once_with(sample_dataframe, db_path)

@patch('japan_avg_hotel_price_finder.sql.save_to_db.main_logger')
@patch('japan_avg_hotel_price_finder.sql.save_to_db.migrate_data_to_sqlite')
def test_save_scraped_data_empty(mock_migrate, mock_logger, empty_dataframe):
    db_path = 'test_db.sqlite'
    save_scraped_data(empty_dataframe, db_path)
    mock_logger.warning.assert_called_with('The dataframe is empty. No data to save')
    mock_migrate.assert_not_called()