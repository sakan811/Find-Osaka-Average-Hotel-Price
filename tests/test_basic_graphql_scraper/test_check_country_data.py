from datetime import timedelta, datetime

import pytest
import pandas as pd
from pydantic import ValidationError

from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper


@pytest.mark.asyncio
async def test_scrape_graphql_valid_inputs(mocker):
    # Create a non-empty DataFrame with the expected structure
    non_empty_df = pd.DataFrame({
        'Hotel': ['Hotel A', 'Hotel B'],
        'Review': [4.5, 4.2],
        'Price': [100, 120]
    })

    # Mocking the methods that interact with external services
    mocker.patch('japan_avg_hotel_price_finder.graphql_scraper_func.graphql_request_func.get_header', return_value={})
    mocker.patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._get_response_data', return_value={})
    mocker.patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper.check_info', return_value=1)
    mocker.patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._scrape_data_from_endpoint',
                 return_value=[non_empty_df])

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

    # Check if the result is a DataFrame and not empty
    assert isinstance(result, pd.DataFrame)
    assert not result.empty

    # Check if the result has the expected columns after transformation
    expected_columns = ['Hotel', 'Review', 'Price', 'City', 'Date', 'AsOf', 'Price/Review']
    assert all(column in result.columns for column in expected_columns)

    # Check if the data has been transformed correctly
    assert result['City'].iloc[0] == 'Tokyo'
    assert result['Date'].iloc[0] == '2023-10-01'
    assert 'Price/Review' in result.columns


def test_validate_inputs():
    # Test valid inputs
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


def test_validate_missing_inputs():
    with pytest.raises(ValidationError):
        BasicGraphQLScraper()


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

    # Check if the query is a dictionary and has the required top-level keys
    assert isinstance(query, dict)
    assert 'operationName' in query
    assert 'variables' in query
    assert 'query' in query

    # Check if the operationName is correct
    assert query['operationName'] == 'FullSearch'

    # Check if the variables contain the correct information
    variables = query['variables']
    input_data = variables['input']

    # Check location information
    assert 'location' in input_data
    assert input_data['location']['searchString'] == 'Tokyo, Japan'
    assert input_data['location']['destType'] == 'CITY'

    # Check dates
    assert 'dates' in input_data
    assert input_data['dates']['checkin'] == '2023-10-01'
    assert input_data['dates']['checkout'] == '2023-10-10'

    # Check other parameters
    assert input_data['childrenAges'] == [0]
    assert input_data['doAvailabilityCheck'] is False
    assert input_data['enableCampaigns'] is True
    assert input_data['nbAdults'] == 2
    assert input_data['nbChildren'] == 0
    assert input_data['nbRooms'] == 1

    # Check filters
    if scraper.scrape_only_hotel:
        assert input_data['filters']['selectedFilters'] == 'ht_id=204'
    else:
        assert 'selectedFilters' not in input_data['filters']

    # Check if the query string is present and non-empty
    assert isinstance(query['query'], str)
    assert len(query['query']) > 0

    # Check for the presence of other expected keys
    expected_keys = ['flexibleDatesConfig', 'metaContext', 'pagination', 'sorters']
    for key in expected_keys:
        assert key in input_data

    # Check pagination
    assert input_data['pagination']['offset'] == 0
    assert input_data['pagination']['rowsPerPage'] == 100

    # Check sorters
    assert 'selectedSorter' in input_data['sorters']
    assert input_data['sorters']['selectedSorter'] is None

    # Test with scrape_only_hotel set to False
    scraper.scrape_only_hotel = False
    query = scraper._get_graphql_query()
    assert 'selectedFilters' not in query['variables']['input']['filters']
