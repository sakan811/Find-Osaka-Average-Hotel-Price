import pytest
import pandas as pd
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper

@pytest.mark.asyncio
async def test_scrape_graphql_valid_inputs(mocker):
    # Mocking the methods that interact with external services
    mocker.patch('japan_avg_hotel_price_finder.graphql_scraper_func.graphql_request_func.get_header', return_value={})
    mocker.patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._get_response_data', return_value={})
    mocker.patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper.check_info', return_value=1)
    mocker.patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._scrape_data_from_endpoint', return_value=[pd.DataFrame()])

    scraper = BasicGraphQLScraper(
        sqlite_name='test_db',
        city='Tokyo',
        country='Japan',
        check_in='2023-10-01',
        check_out='2023-10-10',
        group_adults=2,
        num_rooms=1,
        group_children=0,
        selected_currency='USD',
        scrape_only_hotel=True
    )

    result = await scraper.scrape_graphql()
    assert isinstance(result, pd.DataFrame)

def test_validate_inputs():
    scraper = BasicGraphQLScraper(
        sqlite_name='test_db',
        city='Tokyo',
        country='Japan',
        check_in='2023-10-01',
        check_out='2023-10-10',
        group_adults=2,
        num_rooms=1,
        group_children=0,
        selected_currency='USD',
        scrape_only_hotel=True
    )
    assert scraper._validate_inputs() is True

    scraper.city = ''
    assert scraper._validate_inputs() is False

def test_get_graphql_query():
    scraper = BasicGraphQLScraper(
        sqlite_name='test_db',
        city='Tokyo',
        country='Japan',
        check_in='2023-10-01',
        check_out='2023-10-10',
        group_adults=2,
        num_rooms=1,
        group_children=0,
        selected_currency='USD',
        scrape_only_hotel=True
    )
    query = scraper._get_graphql_query()
    assert isinstance(query, dict)
    assert 'operationName' in query
    assert 'variables' in query