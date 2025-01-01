import datetime
import pytz

import pytest
from pydantic import ValidationError

from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper


@pytest.mark.asyncio
async def test_whole_month_graphql_scraper():
    today = datetime.datetime.now(pytz.UTC)
    current_mth = today.month
    current_year = today.year

    scraper = WholeMonthGraphQLScraper(month=current_mth, city='Osaka', year=current_year, start_day=1, nights=1,
                                       num_rooms=1, group_adults=1, group_children=0,
                                       selected_currency='USD', scrape_only_hotel=True, check_in='', check_out='',
                                       country='Japan')
    df = await scraper.scrape_whole_month()

    assert not df.empty
    # Check column
    assert df.shape[1] == 8


@pytest.mark.asyncio
async def test_whole_month_graphql_scraper_past_date():
    """Test scraper with a past date"""
    scraper = WholeMonthGraphQLScraper(
        year=2023,
        month=1,  # Using January as a valid past month
        day=1,
        city='Osaka',
        country='Japan',
        check_in='',  # These will be calculated by the scraper
        check_out='',
        num_rooms=1,
        group_adults=1,
        group_children=0,
        selected_currency='USD',
        scrape_only_hotel=True
    )
    
    # Test the scraper functionality
    result = await scraper.scrape_whole_month()  # Note: changed to scrape_whole_month() and added await
    
    # Add assertions to verify the result
    assert result is not None
    assert not result.empty  # Changed to check DataFrame is not empty
    assert result.shape[1] == 8  # Verify expected number of columns


def test_whole_month_graphql_scraper_invalid_month():
    """Test scraper with invalid month value"""
    with pytest.raises(ValidationError) as exc_info:
        WholeMonthGraphQLScraper(
            year=2023,
            month=0,  # This should raise ValidationError
            day=1,
            city='Osaka',
            country='Japan',
            check_in='',
            check_out='',
            num_rooms=1,
            group_adults=1,
            group_children=0,
            selected_currency='USD',
            scrape_only_hotel=True
        )
    
    # Verify the error message
    assert "Input should be greater than 0" in str(exc_info.value)