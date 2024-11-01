import datetime
import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine

from check_missing_dates import MissingDateChecker


@pytest.fixture
def missing_date_checker():
    engine = create_engine('sqlite:///test_check_missing_dates.db')
    return MissingDateChecker(engine=engine, city='Tokyo')


def test_check_missing_dates_all_dates_scraped_current_month(missing_date_checker):
    count_of_date_by_mth_asof_today_list = [('2023-10', 31)]
    current_month = '2023-10'
    missing_date_list = []
    today = datetime.datetime(2023, 10, 1)
    year = 2023
    missing_date_checker.check_missing_dates(count_of_date_by_mth_asof_today_list, current_month, missing_date_list,
                                             today, year)

    assert len(missing_date_list) == 0


def test_check_missing_dates_all_dates_scraped_future_month(missing_date_checker):
    count_of_date_by_mth_asof_today_list = [('2023-10', 31)]
    current_month = '2023-09'
    missing_date_list = []
    today = datetime.datetime(2023, 9, 1)
    year = 2023
    missing_date_checker.check_missing_dates(count_of_date_by_mth_asof_today_list, current_month, missing_date_list,
                                             today, year)

    assert len(missing_date_list) == 0


def test_check_missing_dates_all_dates_scraped_past_month(missing_date_checker):
    count_of_date_by_mth_asof_today_list = [('2023-10', 31)]
    current_month = '2023-10'
    missing_date_list = []
    today = datetime.datetime(2023, 11, 1)
    year = 2023
    missing_date_checker.check_missing_dates(count_of_date_by_mth_asof_today_list, current_month, missing_date_list,
                                             today, year)

    assert len(missing_date_list) == 0


def test_check_missing_dates_some_dates_missing(missing_date_checker):
    count_of_date_by_mth_asof_today_list = [('2023-10', 28)]
    current_month = '2023-10'
    missing_date_list = []
    today = datetime.datetime(2023, 10, 1)
    year = 2023
    missing_date_checker.find_dates_of_the_month_in_db = MagicMock(
        return_value=({'2023-10-01', '2023-10-02', '2023-10-03'}, '2023-10-31', '2023-10-01')
    )
    missing_date_checker.check_missing_dates(count_of_date_by_mth_asof_today_list, current_month, missing_date_list,
                                             today, year)

    assert len(missing_date_list) > 0


def test_check_missing_dates_no_data(missing_date_checker):
    count_of_date_by_mth_asof_today_list = []
    current_month = '2023-10'
    missing_date_list = []
    today = datetime.datetime(2023, 10, 31)
    year = 2023
    missing_date_checker.check_missing_dates(count_of_date_by_mth_asof_today_list, current_month, missing_date_list,
                                             today, year)

    assert len(missing_date_list) == 0


def test_check_missing_dates_some_dates_missing_multiple_months(missing_date_checker):
    count_of_date_by_mth_asof_today_list = [('2023-10', 28), ('2023-11', 25)]
    current_month = '2023-11'
    missing_date_list = []
    today = datetime.datetime(2023, 10, 15)
    year = 2023

    def mock_find_dates(days_in_month, month, year):
        if month == 10:
            return ({'2023-10-01', '2023-10-02', '2023-10-03'}, '2023-10-31', '2023-10-01')
        elif month == 11:
            return ({'2023-11-01', '2023-11-02', '2023-11-03', '2023-11-04', '2023-11-05'}, '2023-11-30', '2023-11-01')

    missing_date_checker.find_dates_of_the_month_in_db = MagicMock(side_effect=mock_find_dates)

    missing_date_checker.check_missing_dates(count_of_date_by_mth_asof_today_list, current_month, missing_date_list,
                                             today, year)

    assert len(missing_date_list) > 0
    assert any(date.startswith('2023-10-') for date in missing_date_list)
    assert any(date.startswith('2023-11-') for date in missing_date_list)

    october_missing = [date for date in missing_date_list if date.startswith('2023-10-')]
    november_missing = [date for date in missing_date_list if date.startswith('2023-11-')]

    assert len(october_missing) == 17  # From 2023-10-15 to 2023-10-31
    assert set(october_missing) == set([f'2023-10-{i:02d}' for i in range(15, 32)])

    assert len(november_missing) == 25  # From 2023-11-06 to 2023-11-30
    assert set(november_missing) == set([f'2023-11-{i:02d}' for i in range(6, 31)])