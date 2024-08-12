import datetime

import pytest
import pytz

from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper


@pytest.mark.asyncio
async def test_graphql_scraper():
    timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.datetime.now(timezone)
    check_in = today.strftime('%Y-%m-%d')
    tomorrow = today + datetime.timedelta(days=1)
    check_out = tomorrow.strftime('%Y-%m-%d')
    scraper = BasicGraphQLScraper(city='Osaka', check_in=check_in, check_out=check_out, selected_currency='USD'
                                  , scrape_only_hotel=False)
    df = await scraper.scrape_graphql()

    assert not df.empty
    # Check column
    assert df.shape[1] == 8


@pytest.mark.asyncio
async def test_graphql_scraper_only_hotel():
    timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.datetime.now(timezone)
    check_in = today.strftime('%Y-%m-%d')
    tomorrow = today + datetime.timedelta(days=1)
    check_out = tomorrow.strftime('%Y-%m-%d')
    scraper = BasicGraphQLScraper(city='Osaka', check_in=check_in, check_out=check_out, selected_currency='USD'
                                  , scrape_only_hotel=True)
    df = await scraper.scrape_graphql()

    assert not df.empty
    # Check column
    assert df.shape[1] == 8


if __name__ == '__main__':
    pytest.main()
