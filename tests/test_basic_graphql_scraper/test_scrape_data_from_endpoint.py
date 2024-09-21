import pytest
from unittest.mock import patch, AsyncMock
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
@patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._fetch_hotel_data', new_callable=AsyncMock)
@patch('japan_avg_hotel_price_finder.graphql_scraper.extract_hotel_data')
async def test_scrape_data_from_endpoint_case1(mock_extract_hotel_data, mock_fetch_hotel_data, scraper, caplog):
    # Normal case
    mock_fetch_hotel_data.return_value = [[{'hotel': 'Hotel1'}], [{'hotel': 'Hotel2'}]]
    mock_extract_hotel_data.side_effect = lambda df_list, hotel_data_list: df_list.append(hotel_data_list)

    with caplog.at_level('INFO'):
        df_list = await scraper._scrape_data_from_endpoint(2)

    assert len(df_list) == 2
    assert [{'hotel': 'Hotel1'}] in df_list
    assert [{'hotel': 'Hotel2'}] in df_list

@pytest.mark.asyncio
@patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._fetch_hotel_data', new_callable=AsyncMock)
@patch('japan_avg_hotel_price_finder.graphql_scraper.extract_hotel_data')
async def test_scrape_data_from_endpoint_case2(mock_extract_hotel_data, mock_fetch_hotel_data, scraper):
    # Normal case 2
    mock_fetch_hotel_data.return_value = [[{'hotel': 'Hotel1'}], [{}]]
    mock_extract_hotel_data.side_effect = lambda df_list, hotel_data_list: df_list.append(hotel_data_list)

    df_list = await scraper._scrape_data_from_endpoint(2)

    assert len(df_list) == 2
    assert [{'hotel': 'Hotel1'}] in df_list
    assert [{}] in df_list

@pytest.mark.asyncio
@patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._fetch_hotel_data', new_callable=AsyncMock)
@patch('japan_avg_hotel_price_finder.graphql_scraper.extract_hotel_data')
async def test_scrape_data_from_endpoint_case3(mock_extract_hotel_data, mock_fetch_hotel_data, scraper):
    # Normal case 3
    mock_fetch_hotel_data.return_value = [[{'hotel': 'Hotel1'}], [{'blocks': 'invalid_data'}]]
    mock_extract_hotel_data.side_effect = lambda df_list, hotel_data_list: df_list.append(hotel_data_list)

    df_list = await scraper._scrape_data_from_endpoint(2)

    assert len(df_list) == 2
    assert [{'hotel': 'Hotel1'}] in df_list
    assert [{'blocks': 'invalid_data'}] in df_list

@pytest.mark.asyncio
@patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._fetch_hotel_data', new_callable=AsyncMock)
@patch('japan_avg_hotel_price_finder.graphql_scraper.extract_hotel_data')
async def test_scrape_data_from_endpoint_case4(mock_extract_hotel_data, mock_fetch_hotel_data, scraper):
    # Normal case 4
    mock_fetch_hotel_data.return_value = [[{'hotel': 'Hotel1'}], [{'blocks': [{}]}]]
    mock_extract_hotel_data.side_effect = lambda df_list, hotel_data_list: df_list.append(hotel_data_list)

    df_list = await scraper._scrape_data_from_endpoint(2)

    assert len(df_list) == 2
    assert [{'hotel': 'Hotel1'}] in df_list
    assert [{'blocks': [{}]}] in df_list

@pytest.mark.asyncio
@patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper._fetch_hotel_data', new_callable=AsyncMock)
@patch('japan_avg_hotel_price_finder.graphql_scraper.extract_hotel_data')
async def test_scrape_data_from_endpoint_case5(mock_extract_hotel_data, mock_fetch_hotel_data, scraper):
    # Normal case 5
    mock_fetch_hotel_data.return_value = [[{'hotel': 'Hotel1'}]]
    mock_extract_hotel_data.side_effect = lambda df_list, hotel_data_list: df_list.append(hotel_data_list)

    df_list = await scraper._scrape_data_from_endpoint(1)

    assert len(df_list) == 1
    assert [{'hotel': 'Hotel1'}] in df_list