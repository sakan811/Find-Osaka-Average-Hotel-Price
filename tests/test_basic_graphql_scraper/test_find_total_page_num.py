import pytest
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper

@pytest.fixture
def graphql_scraper():
    return BasicGraphQLScraper(
        sqlite_name='test.db',
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

@pytest.mark.asyncio
async def test_find_total_page_num_success(graphql_scraper):
    graphql_scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {
                        'nbResultsTotal': 5
                    }
                }
            }
        }
    }
    total_page_num = await graphql_scraper._find_total_page_num()
    assert total_page_num == 5

@pytest.mark.asyncio
async def test_find_total_page_num_type_error(graphql_scraper):
    graphql_scraper.data = {}
    total_page_num = await graphql_scraper._find_total_page_num()
    assert total_page_num == 0