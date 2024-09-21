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

def test_check_city_data_match(scraper):
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'breadcrumbs': [
                        {'name': 'Tokyo'},
                        {'name': 'Osaka'}
                    ]
                }
            }
        }
    }
    assert scraper._check_city_data() == 'Tokyo'

def test_check_city_data_no_match(scraper):
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'breadcrumbs': [
                        {'name': 'Osaka'},
                        {'name': 'Kyoto'}
                    ]
                }
            }
        }
    }
    assert scraper._check_city_data() == 'Not Match'

def test_check_city_data_key_error(scraper):
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'breadcrumbs': [
                        {'wrong_key': 'Tokyo'}
                    ]
                }
            }
        }
    }

    assert scraper._check_city_data() == 'Not Match'