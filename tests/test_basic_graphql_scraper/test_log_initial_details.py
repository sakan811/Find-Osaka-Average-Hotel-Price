import pytest
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.configure_logging import main_logger

main_logger.setLevel('DEBUG')

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

def test_log_initial_details(caplog, scraper):
    with caplog.at_level('DEBUG'):
        scraper._log_initial_details()

    assert "City: Tokyo | Check-in: 2023-10-01 | Check-out: 2023-10-10" in caplog.text
    assert "Currency: JPY" in caplog.text
    assert "Adults: 2 | Children: 0 | Rooms: 1" in caplog.text
    assert "Only hotel properties: True" in caplog.text

def test_check_city_data(scraper):
    # Valid case
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'breadcrumbs': [
                        {'name': 'Tokyo'}
                    ]
                }
            }
        }
    }
    assert scraper._check_city_data() == 'Tokyo'

    # Error case: Missing 'name' field
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'breadcrumbs': [
                        {}
                    ]
                }
            }
        }
    }

    assert scraper._check_city_data() == 'Not Match'

def test_check_country_data(scraper):
    # Valid case
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'breadcrumbs': [
                        {'name': 'Japan'}
                    ]
                }
            }
        }
    }
    assert scraper._check_country_data() == 'Japan'

    # Error case: Missing 'name' field
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'breadcrumbs': [
                        {}
                    ]
                }
            }
        }
    }

    assert scraper._check_country_data() == ''

def test_check_currency_data(scraper):
    # Valid case
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'results': [
                        {
                            'blocks': [
                                {'finalPrice': {'currency': 'JPY'}}
                            ]
                        }
                    ]
                }
            }
        }
    }
    assert scraper._check_currency_data() == 'JPY'

    # Error case: Missing 'finalPrice' field
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'results': [
                        {
                            'blocks': [
                                {}
                            ]
                        }
                    ]
                }
            }
        }
    }
    assert scraper._check_currency_data() is None


def test_check_hotel_filter_data(scraper):
    # Valid case
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

    # Error case: Missing 'urlId' field
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [
                        {}
                    ]
                }
            }
        }
    }
    assert scraper._check_hotel_filter_data() is False