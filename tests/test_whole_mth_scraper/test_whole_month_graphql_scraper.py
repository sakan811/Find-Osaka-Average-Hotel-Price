import datetime

import pytest

from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper


@pytest.mark.asyncio
async def test_whole_month_graphql_scraper():
    today = datetime.datetime.now()
    current_mth = today.month
    current_year = today.year

    scraper = WholeMonthGraphQLScraper(month=current_mth, city='Osaka', year=current_year, start_day=1, nights=1,
                                       num_rooms=1, group_adults=1, group_children=0, sqlite_name='',
                                       selected_currency='USD', scrape_only_hotel=True, check_in='', check_out='',
                                       country='Japan')
    df = await scraper.scrape_whole_month()

    assert not df.empty
    # Check column
    assert df.shape[1] == 8


@pytest.mark.asyncio
async def test_whole_month_graphql_scraper_past_date():
    today = datetime.datetime.now()
    past_mth = today.month - 1
    current_year = today.year

    scraper = WholeMonthGraphQLScraper(month=past_mth, city='Osaka', year=current_year, start_day=1, nights=1,
                                       num_rooms=1, group_adults=1, group_children=0, sqlite_name='',
                                       selected_currency='USD', scrape_only_hotel=True, check_in='', check_out='',
                                       country='Japan')
    df = await scraper.scrape_whole_month()

    assert df.empty
