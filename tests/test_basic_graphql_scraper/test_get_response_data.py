import pytest
from aioresponses import aioresponses

from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper


@pytest.fixture
def scraper():
    return BasicGraphQLScraper(
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

@pytest.mark.asyncio
async def test_get_response_data_success(scraper):
    """Test successful GraphQL response."""
    graphql_query = {"query": "{ hotels { name } }"}
    mock_response = {"data": {"hotels": [{"name": "Hotel A"}, {"name": "Hotel B"}]}}

    with aioresponses() as mocked:
        mocked.post(scraper.url, payload=mock_response)

        result = await scraper._get_response_data(graphql_query)
        assert result == mock_response

@pytest.mark.asyncio
async def test_get_response_data_error_status(scraper):
    """Test non-200 status code handling."""
    graphql_query = {"query": "{ hotels { name } }"}

    with aioresponses() as mocked:
        mocked.post(scraper.url, status=404)

        result = await scraper._get_response_data(graphql_query)
        assert result == {}  # As per your implementation for non-200 response

@pytest.mark.asyncio
async def test_get_response_data_invalid_json(scraper):
    """Test invalid JSON in the response."""
    graphql_query = {"query": "{ hotels { name } }"}

    with aioresponses() as mocked:
        mocked.post(scraper.url, body="invalid json")

        result = await scraper._get_response_data(graphql_query)
        assert result == {}


@pytest.mark.asyncio
async def test_get_response_data_content_type_error(scraper):
    """Test handling of ContentTypeError in the response."""
    graphql_query = {"query": "{ hotels { name } }"}

    with aioresponses() as mocked:
        mocked.post(
            scraper.url,
            payload="This is not JSON",
            content_type="text/plain",
            status=200
        )

        result = await scraper._get_response_data(graphql_query)

    assert result == {}