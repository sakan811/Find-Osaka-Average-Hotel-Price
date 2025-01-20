from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Session

from check_missing_dates import MissingDateChecker


@pytest.fixture
def mock_today():
    return datetime(2023, 12, 31)


@pytest.fixture
def missing_date_checker(mock_today):
    engine = create_engine('sqlite:///test.db')
    return MissingDateChecker(engine=engine, city='TestCity')


@pytest.fixture
def mock_session(mock_today):
    session = MagicMock(spec=Session)
    session.bind = MagicMock()
    return session


def test_find_missing_dates_in_db_no_data(missing_date_checker, mock_session, mock_today):
    missing_date_checker.Session = MagicMock(return_value=mock_session)
    mock_session.query.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = []

    result = missing_date_checker.find_missing_dates_in_db(mock_today.year)

    assert result == []


def test_find_missing_dates_in_db_all_dates_present(missing_date_checker, mock_session, mock_today):
    missing_date_checker.Session = MagicMock(return_value=mock_session)
    mock_data = [
        (mock_today.strftime('%Y-%m'), 31)  # Use the actual number of days in the month
    ]
    mock_session.query.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = mock_data

    with patch('check_missing_dates.MissingDateChecker.check_missing_dates') as mock_check:
        mock_check.return_value = None
        result = missing_date_checker.find_missing_dates_in_db(mock_today.year)

    assert result == []


def test_find_missing_dates_in_db_some_dates_missing(missing_date_checker, mock_session, mock_today):
    missing_date_checker.Session = MagicMock(return_value=mock_session)
    mock_data = [
        (mock_today.strftime('%Y-%m'), 25)  # Assuming 6 days missing in December
    ]

    # Mock the dialect
    mock_dialect = MagicMock(spec=sqlite.dialect)
    mock_session.bind.dialect = mock_dialect

    with patch('check_missing_dates.get_date_count_by_month') as mock_get_date_count, \
            patch('check_missing_dates.get_dates_in_db') as mock_get_dates_in_db, \
            patch('check_missing_dates.MissingDateChecker.check_missing_dates') as mock_check:
        mock_get_date_count.return_value = mock_data
        mock_get_dates_in_db.return_value = []  # Simulate no dates in DB

        def side_effect(*args, **kwargs):
            for i in range(26, 32):
                date = mock_today + timedelta(days=i - 25)
                args[2].append(date.strftime('%Y-%m-%d'))

        mock_check.side_effect = side_effect
        result = missing_date_checker.find_missing_dates_in_db(mock_today.year)

    assert len(result) == 6
    expected_dates = [(mock_today + timedelta(days=i - 25)).strftime('%Y-%m-%d') for i in range(26, 32)]
    assert result == expected_dates


def test_find_missing_dates_in_db_multiple_months_missing(missing_date_checker, mock_session, mock_today):
    missing_date_checker.Session = MagicMock(return_value=mock_session)

    # Simulate missing data across two months, e.g., December and January
    mock_data = [
        (mock_today.strftime('%Y-%m'), 25),  # Assuming 6 days missing in December
        ((mock_today + timedelta(days=31)).strftime('%Y-%m'), 20)  # Assuming 11 days missing in January
    ]

    # Mock the dialect
    mock_dialect = MagicMock(spec=sqlite.dialect)
    mock_session.bind.dialect = mock_dialect

    mock_session.query.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = mock_data

    with patch('check_missing_dates.MissingDateChecker.check_missing_dates') as mock_check:
        def side_effect(*args, **kwargs):
            # Handle missing dates in December
            for i in range(26, 32):
                date_dec = mock_today + timedelta(days=i - 25)
                args[2].append(date_dec.strftime('%Y-%m-%d'))
            # Handle missing dates in January
            for i in range(1, 12):
                date_jan = (mock_today + timedelta(days=31)).replace(day=i)
                args[2].append(date_jan.strftime('%Y-%m-%d'))

        mock_check.side_effect = side_effect
        result = missing_date_checker.find_missing_dates_in_db(mock_today.year)

    assert len(result) == 17  # 6 missing in December + 11 missing in January
    # Check if all dates are either in the current month/year, next month/year, or the month after
    assert all(
        date.startswith(f"{mock_today.year}-{mock_today.month:02d}-") or
        date.startswith(f"{mock_today.year + 1}-01-") for date in result
    )

    # Verify the specific dates
    expected_dates = [
                         # December missing dates
                         (mock_today + timedelta(days=i - 25)).strftime('%Y-%m-%d') for i in range(26, 32)
                     ] + [
                         # January missing dates
                         (mock_today.replace(month=12, day=31) + timedelta(days=i)).strftime('%Y-%m-%d') for i in
                         range(1, 12)
                     ]
    assert result == expected_dates


@pytest.mark.parametrize("exception", [Exception("Database error"), ValueError("Invalid query")])
def test_find_missing_dates_in_db_exception_handling(missing_date_checker, mock_session, exception):
    missing_date_checker.Session = MagicMock(return_value=mock_session)
    mock_session.query.side_effect = exception

    result = missing_date_checker.find_missing_dates_in_db(2023)

    assert result == []


@pytest.mark.parametrize("mock_today", [
    datetime(2023, 12, 31),  # Year rollover
    datetime(2024, 2, 28),  # Leap year
    datetime(2024, 2, 29),  # Last day of leap year
    datetime(2025, 2, 28),  # Last day of February in non-leap year
], indirect=True)
def test_find_missing_dates_in_db_special_dates(missing_date_checker, mock_session, mock_today):
    missing_date_checker.Session = MagicMock(return_value=mock_session)
    mock_data = [
        (mock_today.strftime('%Y-%m'), mock_today.day - 1)  # Assuming the last day is missing
    ]
    mock_session.query.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = mock_data

    with patch('check_missing_dates.MissingDateChecker.check_missing_dates') as mock_check:
        mock_check.side_effect = lambda *args, **kwargs: args[2].append(mock_today.strftime('%Y-%m-%d'))
