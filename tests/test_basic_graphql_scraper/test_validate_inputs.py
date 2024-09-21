import pytest
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper

@pytest.mark.parametrize("city, check_in, check_out, selected_currency, expected", [
    ("Tokyo", "2024-07-05", "2024-07-06", "USD", True),
    ("", "2024-07-05", "2024-07-06", "USD", False),
    ("Tokyo", "", "2024-07-06", "USD", False),
    ("Tokyo", "2024-07-05", "", "USD", False),
    ("Tokyo", "2024-07-05", "2024-07-06", "", False),
])
def test_validate_inputs(city, check_in, check_out, selected_currency, expected):
    scraper = BasicGraphQLScraper(
        sqlite_name="test_db",
        city=city,
        country="Japan",
        check_in=check_in,
        check_out=check_out,
        group_adults=1,
        num_rooms=1,
        group_children=0,
        selected_currency=selected_currency,
        scrape_only_hotel=True
    )
    assert scraper._validate_inputs() == expected