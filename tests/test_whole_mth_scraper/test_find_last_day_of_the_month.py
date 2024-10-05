import pytest
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper

@pytest.fixture
def scraper():
    return WholeMonthGraphQLScraper(
        city="Tokyo",
        country="Japan",
        sqlite_name="test.db",
        check_in="2023-01-01",
        check_out="2023-01-02",
        group_adults=1,
        num_rooms=1,
        group_children=0,
        selected_currency="USD",
        scrape_only_hotel=True,
        year=2023,
        month=1,
        start_day=1,
        nights=1
    )

@pytest.mark.asyncio
async def test_find_last_day_of_the_month(scraper):
    # Test regular months
    scraper.year, scraper.month = 2023, 4  # April
    assert await scraper._find_last_day_of_the_month() == 30

    scraper.year, scraper.month = 2023, 5  # May
    assert await scraper._find_last_day_of_the_month() == 31

    # Test February in a non-leap year
    scraper.year, scraper.month = 2023, 2
    assert await scraper._find_last_day_of_the_month() == 28

    # Test February in a leap year
    scraper.year, scraper.month = 2024, 2
    assert await scraper._find_last_day_of_the_month() == 29

    # Test edge cases
    scraper.year, scraper.month = 2023, 12  # December
    assert await scraper._find_last_day_of_the_month() == 31

    scraper.year, scraper.month = 2023, 1  # January
    assert await scraper._find_last_day_of_the_month() == 31

@pytest.mark.asyncio
async def test_find_last_day_of_the_month_invalid_input(scraper):
    # Test invalid month
    scraper.year, scraper.month = 2023, 13
    with pytest.raises(ValueError):
        await scraper._find_last_day_of_the_month()

    # Test invalid year (assuming your class validates the year)
    scraper.year, scraper.month = -1, 1
    with pytest.raises(ValueError):
        await scraper._find_last_day_of_the_month()