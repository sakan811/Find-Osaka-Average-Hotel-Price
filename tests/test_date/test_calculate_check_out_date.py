from datetime import date

from japan_avg_hotel_price_finder.date_utils.date_utils import calculate_check_out_date


def test_regular_case():
    current_date = date(2023, 7, 15)
    expected_checkout = date(2023, 7, 16)
    assert calculate_check_out_date(current_date, 1) == expected_checkout

def test_month_end():
    current_date = date(2023, 7, 31)
    expected_checkout = date(2023, 8, 1)
    assert calculate_check_out_date(current_date, 1) == expected_checkout

def test_year_end():
    current_date = date(2023, 12, 31)
    expected_checkout = date(2024, 1, 1)
    assert calculate_check_out_date(current_date, 1) == expected_checkout

def test_leap_year():
    current_date = date(2024, 2, 28)
    expected_checkout = date(2024, 2, 29)
    assert calculate_check_out_date(current_date, 1) == expected_checkout

def test_multiple_nights():
    current_date = date(2023, 7, 15)
    expected_checkout = date(2023, 7, 18)
    assert calculate_check_out_date(current_date, 3) == expected_checkout

def test_zero_nights():
    current_date = date(2023, 7, 15)
    expected_checkout = date(2023, 7, 15)
    assert calculate_check_out_date(current_date, 0) == expected_checkout

def test_negative_nights():
    current_date = date(2023, 7, 15)
    expected_checkout = date(2023, 7, 14)
    assert calculate_check_out_date(current_date, -1) == expected_checkout
