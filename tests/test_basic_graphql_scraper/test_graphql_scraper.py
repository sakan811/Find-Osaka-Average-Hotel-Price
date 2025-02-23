import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from freezegun import freeze_time

from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper

country = 'Japan'
FIXED_DATE = "2024-01-15 12:00:00"

@pytest.mark.asyncio
@freeze_time(FIXED_DATE, tz_offset=0)
async def test_graphql_scraper():
    # Using fixed dates instead of current time
    check_in = "2024-01-15"
    check_out = "2024-01-16"
    
    mock_data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'name': 'popular_filters', 'urlId': 'ht_id=204'}],
                    'pagination': {'nbResultsTotal': 2},
                    'breadcrumbs': [
                        {'name': country, 'destType': 'COUNTRY'},
                        {'name': 'Osaka', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': [check_in],
                            'checkout': [check_out]
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 1,
                        'nbChildren': 0,
                        'nbRooms': 1
                    },
                    'results': [
                        {
                            'displayName': {'text': 'Test Hotel 1'},
                            'basicPropertyData': {
                                'reviewScore': {'score': 8.5}
                            },
                            'blocks': [{
                                'finalPrice': {
                                    'amount': 100.0,
                                    'currency': 'USD'
                                }
                            }],
                            'location': {'displayLocation': 'Test Address 1'}
                        },
                        {
                            'displayName': {'text': 'Test Hotel 2'},
                            'basicPropertyData': {
                                'reviewScore': {'score': 9.0}
                            },
                            'blocks': [{
                                'finalPrice': {
                                    'amount': 150.0,
                                    'currency': 'USD'
                                }
                            }],
                            'location': {'displayLocation': 'Test Address 2'}
                        }
                    ]
                }
            }
        }
    }

    scraper = BasicGraphQLScraper(city='Osaka', num_rooms=1, group_adults=1, group_children=0, check_out=check_out,
                                  check_in=check_in, selected_currency='USD', scrape_only_hotel=True, country=country)
    
    # Create mock response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_data)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    # Create mock session
    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Mock all necessary methods
    with patch('aiohttp.ClientSession', return_value=mock_session), \
         patch.object(scraper, '_find_total_page_num', return_value=1), \
         patch.object(scraper, '_check_city_data', return_value='Osaka'), \
         patch.object(scraper, '_check_country_data', return_value=country), \
         patch.object(scraper, '_check_currency_data', return_value='USD'), \
         patch.object(scraper, '_check_hotel_filter_data', return_value=True):
        
        # First check info
        scraper.data = mock_data  # Set the data directly for check_info
        total_pages = await scraper.check_info()
        assert total_pages == 1
        
        # Then scrape data
        df = await scraper.scrape_graphql()

    # Basic DataFrame checks
    assert not df.empty
    assert df.shape[0] == 2  # Check row count
    assert list(df['Hotel'].values) == ['Test Hotel 1', 'Test Hotel 2']
    assert list(df['Price'].values) == [100.0, 150.0]
    assert list(df['Review'].values) == [8.5, 9.0]
    assert all(df['City'] == 'Osaka')
    assert all(df['Date'] == check_in)


@pytest.mark.asyncio
@freeze_time(FIXED_DATE, tz_offset=0)
async def test_graphql_scraper_incorrect_date():
    # Using fixed dates
    check_in = "2024-01-15"
    check_out = "2024-01-14"  # Intentionally incorrect date
    
    mock_data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'name': 'popular_filters', 'urlId': 'ht_id=204'}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': country, 'destType': 'COUNTRY'},
                        {'name': 'Osaka', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': [check_in],
                            'checkout': ["2024-01-16"]  # Different from check_out
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 1,
                        'nbChildren': 0,
                        'nbRooms': 1
                    }
                }
            }
        }
    }
    
    scraper = BasicGraphQLScraper(city='Osaka', num_rooms=1, group_adults=1, group_children=0, check_out=check_out,
                                  check_in=check_in, selected_currency='USD', scrape_only_hotel=True, country=country)

    # Create mock response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_data)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    # Create mock session
    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Mock all necessary methods
    with patch('aiohttp.ClientSession', return_value=mock_session), \
         patch.object(scraper, '_find_total_page_num', return_value=1), \
         patch.object(scraper, '_check_city_data', return_value='Osaka'), \
         patch.object(scraper, '_check_country_data', return_value=country), \
         patch.object(scraper, '_check_currency_data', return_value='USD'), \
         patch.object(scraper, '_check_hotel_filter_data', return_value=True):
        
        scraper.data = mock_data  # Set the data directly for check_info
        with pytest.raises(SystemExit):
            await scraper.check_info()


if __name__ == '__main__':
    pytest.main()
