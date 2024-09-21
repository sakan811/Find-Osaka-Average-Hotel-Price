import pytest
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper

@pytest.mark.parametrize("data, expected_currency", [
    ({"data": {"searchQueries": {"search": {"results": [{"blocks": [{"finalPrice": {"currency": "USD"}}]}]}}}}, "USD"),
    ({"data": {"searchQueries": {"search": {"results": [{"blocks": [{"finalPrice": {"currency": "JPY"}}]}]}}}}, "JPY"),
    ({"data": {"searchQueries": {"search": {"results": [{"blocks": [{"finalPrice": {"currency": "EUR"}}]}]}}}}, "EUR"),
    ({"data": {"searchQueries": {"search": {"results": []}}}}, None)
])
def test_check_currency_data(data, expected_currency):
    scraper = BasicGraphQLScraper(
        sqlite_name="test_db",
        city="Tokyo",
        country="Japan",
        check_in="2024-07-05",
        check_out="2024-07-06",
        group_adults=1,
        num_rooms=1,
        group_children=0,
        selected_currency="USD",
        scrape_only_hotel=True
    )
    scraper.data = data
    if expected_currency is None:
        assert scraper._check_currency_data() is None
    else:
        assert scraper._check_currency_data() == expected_currency


@pytest.mark.parametrize("data, expected_currency", [
    ({}, None)
])
def test_check_currency_data_error_handle(data, expected_currency):
    scraper = BasicGraphQLScraper(
        sqlite_name="test_db",
        city="Tokyo",
        country="Japan",
        check_in="2024-07-05",
        check_out="2024-07-06",
        group_adults=1,
        num_rooms=1,
        group_children=0,
        selected_currency="USD",
        scrape_only_hotel=True
    )
    scraper.data = data
    if expected_currency is None:
        with pytest.raises(KeyError):
            scraper._check_currency_data()
    else:
        assert scraper._check_currency_data() == expected_currency