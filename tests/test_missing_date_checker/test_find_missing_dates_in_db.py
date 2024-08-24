import datetime
from unittest.mock import patch, MagicMock
from dateutil.relativedelta import relativedelta

import pytest

from check_missing_dates import MissingDateChecker


@pytest.fixture
def mock_sqlite3():
    with patch('sqlite3.connect') as mock_connect:
        yield mock_connect


@pytest.fixture
def checker():
    return MissingDateChecker("test.db", "Test City")


@pytest.fixture
def mock_today():
    today = datetime.datetime(2024, 8, 15)
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = today
        mock_datetime.today.return_value = today
        yield today


def test_current_month(mock_sqlite3, checker, mock_today):
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_today
        mock_datetime.today.return_value = mock_today
        mock_datetime.strptime.return_value = mock_today

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(mock_today.strftime('%Y-%m'), mock_today.day)]
        mock_sqlite3.return_value.__enter__.return_value.execute.return_value = mock_cursor

        with patch('japan_avg_hotel_price_finder.utils.get_count_of_date_by_mth_asof_today_query'):
            with patch.object(checker, 'find_dates_of_the_month_in_db', return_value=([], mock_today.replace(day=1).strftime('%Y-%m-%d'), mock_today.strftime('%Y-%m-%d'))):
                with patch('check_missing_dates.find_missing_dates', return_value=[
                    (mock_today + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                    (mock_today + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
                ]):
                    result = checker.find_missing_dates_in_db()

        assert len(result) == 2
        assert result[0] == (mock_today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        assert result[1] == (mock_today + datetime.timedelta(days=2)).strftime('%Y-%m-%d')


def test_future_month(mock_sqlite3, checker, mock_today):
    future_date = mock_today + relativedelta(months=1)
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_today
        mock_datetime.today.return_value = mock_today
        mock_datetime.strptime.return_value = future_date

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(future_date.strftime('%Y-%m'), future_date.day)]
        mock_sqlite3.return_value.__enter__.return_value.execute.return_value = mock_cursor

        with patch('japan_avg_hotel_price_finder.utils.get_count_of_date_by_mth_asof_today_query'):
            with patch('check_missing_dates.find_missing_dates', return_value=[]):
                result = checker.find_missing_dates_in_db()

        assert result == []


def test_past_month(mock_sqlite3, checker, mock_today):
    past_date = mock_today - relativedelta(months=1)
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_today
        mock_datetime.today.return_value = mock_today
        mock_datetime.strptime.return_value = past_date

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(past_date.strftime('%Y-%m'), past_date.day)]
        mock_sqlite3.return_value.__enter__.return_value.execute.return_value = mock_cursor

        with patch('japan_avg_hotel_price_finder.utils.get_count_of_date_by_mth_asof_today_query'):
            with patch.object(checker, 'find_dates_of_the_month_in_db', return_value=([], past_date.replace(day=1).strftime('%Y-%m-%d'), past_date.replace(day=31).strftime('%Y-%m-%d'))):
                with patch('check_missing_dates.find_missing_dates', return_value=[past_date.replace(day=31).strftime('%Y-%m-%d')]):
                    result = checker.find_missing_dates_in_db()

        assert len(result) == 1
        assert result[0] == past_date.replace(day=31).strftime('%Y-%m-%d')


def test_no_data(mock_sqlite3, checker, mock_today):
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_today
        mock_datetime.today.return_value = mock_today
        mock_datetime.strptime.return_value = mock_today

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_sqlite3.return_value.__enter__.return_value.execute.return_value = mock_cursor

        with patch('japan_avg_hotel_price_finder.utils.get_count_of_date_by_mth_asof_today_query'):
            result = checker.find_missing_dates_in_db()

        assert result == []