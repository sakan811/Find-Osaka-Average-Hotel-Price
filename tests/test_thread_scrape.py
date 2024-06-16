import datetime
import pytest
import pytz

from japan_avg_hotel_price_finder.thread_scrape import ThreadPoolScraper
from set_details import Details


def test_thread_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    start_day = 1
    month = today.month
    year = today.year
    nights = 1

    sqlite_name = 'test_thread_scraper.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    thread_scrape = ThreadPoolScraper(hotel_stay)
    df = thread_scrape.thread_scrape(timezone=city_timezone, max_workers=5)

    assert not df.empty

    # Check column
    assert df.shape[1] == 7


def test_thread_scraper_past_month() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    start_day = 27
    month = today.month - 1
    year = today.year
    nights = 1

    sqlite_name = 'test_thread_scraper_past_month.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        start_day=start_day, month=month, year=year, nights=nights, sqlite_name=sqlite_name
    )

    thread_scrape = ThreadPoolScraper(hotel_stay)
    df = thread_scrape.thread_scrape(timezone=city_timezone, max_workers=5)

    assert df is None


if __name__ == '__main__':
    pytest.main()