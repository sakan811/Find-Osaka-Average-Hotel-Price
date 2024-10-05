from datetime import date

import pytest

from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper


@pytest.fixture
def scraper():
    return WholeMonthGraphQLScraper(
        sqlite_name="test_db.sqlite",
        city="Test City",
        country="Test Country",
        check_in="2023-07-01",  # Use a fixed date for testing
        check_out="2023-07-02",  # Use a fixed date for testing
        nights=1,
        year=2023,  # Add this if it's a required field
        month=7,    # Add this if it's a required field
        start_day=1 # Add this if it's a required field
    )


def test_regular_case(scraper):
    current_date = date(2023, 7, 15)
    expected_checkout = date(2023, 7, 16)
    assert scraper._calculate_check_out_date(current_date) == expected_checkout

def test_month_end(scraper):
    current_date = date(2023, 7, 31)
    expected_checkout = date(2023, 8, 1)
    assert scraper._calculate_check_out_date(current_date) == expected_checkout

def test_year_end(scraper):
    current_date = date(2023, 12, 31)
    expected_checkout = date(2024, 1, 1)
    assert scraper._calculate_check_out_date(current_date) == expected_checkout

def test_leap_year(scraper):
    current_date = date(2024, 2, 28)
    expected_checkout = date(2024, 2, 29)
    assert scraper._calculate_check_out_date(current_date) == expected_checkout

def test_multiple_nights(scraper):
    scraper.nights = 3
    current_date = date(2023, 7, 15)
    expected_checkout = date(2023, 7, 18)
    assert scraper._calculate_check_out_date(current_date) == expected_checkout

def test_zero_nights(scraper):
    scraper.nights = 0
    current_date = date(2023, 7, 15)
    expected_checkout = date(2023, 7, 15)
    assert scraper._calculate_check_out_date(current_date) == expected_checkout

def test_negative_nights(scraper):
    scraper.nights = -1
    current_date = date(2023, 7, 15)
    expected_checkout = date(2023, 7, 14)
    assert scraper._calculate_check_out_date(current_date) == expected_checkout
