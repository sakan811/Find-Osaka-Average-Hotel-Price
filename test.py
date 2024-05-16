import pytest

from japan_avg_hotel_price_finder.scrape_each_date import ScrapeEachDate


def test_full_process() -> None:
    city = 'Osaka'
    group_adults = '1'
    num_rooms = '1'
    group_children = '0'
    selected_currency = 'USD'

    scrape_each_date = ScrapeEachDate(city, group_adults, num_rooms, selected_currency, group_children)
    df = scrape_each_date.scrape_until_month_end(20, 6, 2024, 1)

    assert df is not None


if __name__ == '__main__':
    pytest.main([__file__])
