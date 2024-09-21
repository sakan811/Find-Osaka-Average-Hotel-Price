import pytest
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper

@pytest.fixture
def scraper():
    return BasicGraphQLScraper(
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

def test_check_hotel_filter_data_true(scraper):
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [
                        {'urlId': 'ht_id=204'}
                    ]
                }
            }
        }
    }
    assert scraper._check_hotel_filter_data() is True

def test_check_hotel_filter_data_false(scraper):
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [
                        {'urlId': 'ht_id=999'}
                    ]
                }
            }
        }
    }
    assert scraper._check_hotel_filter_data() is False

def test_check_hotel_filter_data_key_error(scraper):
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {}
            }
        }
    }
    assert scraper._check_hotel_filter_data() is False