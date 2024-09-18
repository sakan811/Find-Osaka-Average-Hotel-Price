import datetime
import pytest
from unittest.mock import MagicMock

from check_missing_dates import MissingDateChecker


@pytest.fixture
def missing_date_checker():
    return MissingDateChecker(sqlite_name='test_check_missing_dates.db', city='Tokyo')


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