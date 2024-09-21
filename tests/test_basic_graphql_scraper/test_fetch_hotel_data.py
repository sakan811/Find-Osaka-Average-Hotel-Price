import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from japan_avg_hotel_price_finder.graphql_scraper_func.graphql_request_func import fetch_hotel_data


@pytest.mark.asyncio
async def test_fetch_hotel_data_success():
    url = "http://example.com/graphql"
    headers = {"Content-Type": "application/json"}
    graphql_query = {"query": "some graphql query"}
    expected_data = {"data": {"searchQueries": {"search": {"results": [{"id": "1", "name": "Hotel One"}]}}}}

    with aioresponses() as m:
        m.post(url, payload=expected_data)

        async with ClientSession() as session:
            result = await fetch_hotel_data(session, url, headers, graphql_query)

        assert result == [{"id": "1", "name": "Hotel One"}]
        assert len(result) == 1

@pytest.mark.asyncio
async def test_fetch_hotel_data_non_200_status():
    url = "http://example.com/graphql"
    headers = {"Content-Type": "application/json"}
    graphql_query = {"query": "some graphql query"}

    with aioresponses() as m:
        m.post(url, status=404)

        async with ClientSession() as session:
            result = await fetch_hotel_data(session, url, headers, graphql_query)

        assert result == []

@pytest.mark.asyncio
async def test_fetch_hotel_data_invalid_json():
    url = "http://example.com/graphql"
    headers = {"Content-Type": "application/json"}
    graphql_query = {"query": "some graphql query"}

    with aioresponses() as m:
        m.post(url, payload="Invalid JSON")

        async with ClientSession() as session:
            result = await fetch_hotel_data(session, url, headers, graphql_query)

        assert result == []

@pytest.mark.asyncio
async def test_fetch_hotel_data_missing_keys():
    url = "http://example.com/graphql"
    headers = {"Content-Type": "application/json"}
    graphql_query = {"query": "some graphql query"}
    invalid_data = {"data": {"searchQueries": {}}}

    with aioresponses() as m:
        m.post(url, payload=invalid_data)

        async with ClientSession() as session:
            result = await fetch_hotel_data(session, url, headers, graphql_query)

        assert result == []

if __name__ == "__main__":
    pytest.main()
