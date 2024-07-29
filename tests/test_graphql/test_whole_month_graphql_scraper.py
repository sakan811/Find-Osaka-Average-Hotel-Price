import datetime

import pytest
import pytz

from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper


@pytest.mark.asyncio
async def test_whole_month_graphql_scraper():
    timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.datetime.now(timezone)
    current_mth = today.month

    scraper = WholeMonthGraphQLScraper(month=current_mth)
    df = await scraper.scrape_whole_month()

    assert not df.empty
    # Check column
    assert df.shape[1] == 7


@pytest.mark.asyncio
async def test_whole_month_graphql_scraper_past_date():
    timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.datetime.now(timezone)
    past_mth = today.month - 1

    scraper = WholeMonthGraphQLScraper(month=past_mth)
    df = await scraper.scrape_whole_month()

    assert df.empty
