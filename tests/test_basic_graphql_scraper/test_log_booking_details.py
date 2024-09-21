import pytest

from japan_avg_hotel_price_finder.booking_details import BookingDetails
from japan_avg_hotel_price_finder.graphql_scraper import log_booking_details
from japan_avg_hotel_price_finder.configure_logging import main_logger

main_logger.setLevel('DEBUG')

@pytest.fixture
def booking_details():
    return BookingDetails(
        city='Tokyo',
        country='Japan',
        check_in='2023-10-01',
        check_out='2023-10-10',
        group_adults=2,
        num_rooms=1,
        group_children=0,
        selected_currency='JPY',
        scrape_only_hotel=True,
        sqlite_name='test_db.sqlite'
    )

def test_log_booking_details(caplog, booking_details):
    with caplog.at_level('DEBUG'):
        log_booking_details(booking_details)

    for key in booking_details.__annotations__.keys():
        value = getattr(booking_details, key)
        assert f'BookingDetails {key}: {value}' in caplog.text

@pytest.fixture
def booking_details_different():
    return BookingDetails(
        city='Osaka',
        country='Japan',
        check_in='2023-11-01',
        check_out='2023-11-05',
        group_adults=1,
        num_rooms=1,
        group_children=1,
        selected_currency='USD',
        scrape_only_hotel=False,
        sqlite_name='test_db_different.sqlite'
    )

def test_log_booking_details_different(caplog, booking_details_different):
    with caplog.at_level('DEBUG'):
        log_booking_details(booking_details_different)

    for key in booking_details_different.__annotations__.keys():
        value = getattr(booking_details_different, key)
        assert f'BookingDetails {key}: {value}' in caplog.text

@pytest.fixture
def booking_details_missing_optional():
    return BookingDetails(
        city='Kyoto',
        country='Japan',
        check_in='2023-12-01',
        check_out='2023-12-10',
        group_adults=3,
        num_rooms=2,
        group_children=0,
        selected_currency='EUR',
        scrape_only_hotel=True
    )

def test_log_booking_details_missing_optional(caplog, booking_details_missing_optional):
    with caplog.at_level('DEBUG'):
        log_booking_details(booking_details_missing_optional)

    for key in booking_details_missing_optional.__annotations__.keys():
        value = getattr(booking_details_missing_optional, key)
        assert f'BookingDetails {key}: {value}' in caplog.text

@pytest.fixture
def booking_details_edge_case():
    return BookingDetails(
        city='Nagoya',
        country='Japan',
        check_in='2023-12-01',
        check_out='2023-12-01',
        group_adults=2,
        num_rooms=1,
        group_children=0,
        selected_currency='GBP',
        scrape_only_hotel=True,
        sqlite_name='test_db_edge_case.sqlite'
    )

def test_log_booking_details_edge_case(caplog, booking_details_edge_case):
    with caplog.at_level('DEBUG'):
        log_booking_details(booking_details_edge_case)

    for key in booking_details_edge_case.__annotations__.keys():
        value = getattr(booking_details_edge_case, key)
        assert f'BookingDetails {key}: {value}' in caplog.text