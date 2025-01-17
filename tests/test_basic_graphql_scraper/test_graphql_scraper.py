import datetime

import pytest
import pytz

from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper


country = 'Japan'

@pytest.mark.asyncio
async def test_graphql_scraper():
    timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.datetime.now(timezone)
    check_in = today.strftime('%Y-%m-%d')
    tomorrow = today + datetime.timedelta(days=1)
    check_out = tomorrow.strftime('%Y-%m-%d')
    scraper = BasicGraphQLScraper(city='Osaka', num_rooms=1, group_adults=1, group_children=0, check_out=check_out,
                                  check_in=check_in, selected_currency='USD', scrape_only_hotel=True, country=country)

    df = await scraper.scrape_graphql()

    assert not df.empty
    # Check column
    assert df.shape[1] == 8


@pytest.mark.asyncio
async def test_graphql_scraper_incorrect_date():
    timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.datetime.now(timezone)
    check_in = today.strftime('%Y-%m-%d')
    yesterday = today - datetime.timedelta(days=1)
    check_out = yesterday.strftime('%Y-%m-%d')
    scraper = BasicGraphQLScraper(city='Osaka', num_rooms=1, group_adults=1, group_children=0, check_out=check_out,
                                  check_in=check_in, selected_currency='USD', scrape_only_hotel=True, country=country)

    # Mock the response data to simulate a mismatch in dates
    scraper.data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': country, 'destType': 'COUNTRY'},
                        {'name': 'Osaka', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': [check_in],
                            'checkout': [(today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')]  # Different from check_out
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 1,
                        'nbChildren': 0,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }

    with pytest.raises(SystemExit):
        await scraper.check_info()


if __name__ == '__main__':
    pytest.main()
