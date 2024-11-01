from unittest.mock import patch, Mock

import pandas as pd
import pytest
from sqlalchemy import Engine

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

@pytest.fixture
def mock_engine():
    return Mock(spec=Engine)

@patch('japan_avg_hotel_price_finder.sql.save_to_db.main_logger')
@patch('japan_avg_hotel_price_finder.sql.save_to_db.migrate_data_to_database')
def test_save_scraped_data_non_empty(mock_migrate, mock_logger, sample_dataframe, mock_engine):
    save_scraped_data(sample_dataframe, mock_engine)
    mock_logger.info.assert_any_call("Saving scraped data...")
    mock_logger.info.assert_any_call('Save data to a database')
    mock_migrate.assert_called_once_with(sample_dataframe, mock_engine)

@patch('japan_avg_hotel_price_finder.sql.save_to_db.main_logger')
@patch('japan_avg_hotel_price_finder.sql.save_to_db.migrate_data_to_database')
def test_save_scraped_data_empty(mock_migrate, mock_logger, empty_dataframe, mock_engine):
    save_scraped_data(empty_dataframe, mock_engine)
    mock_logger.info.assert_called_with("Saving scraped data...")
    mock_logger.warning.assert_called_with('The dataframe is empty. No data to save')
    mock_migrate.assert_not_called()