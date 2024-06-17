import datetime

import pytest
import pytz

from japan_avg_hotel_price_finder.scrape import create_df_from_scraped_data, BasicScraper
from set_details import Details


def test_create_df_from_scraped_data():
    check_in = "2024-06-01"
    check_out = "2024-06-05"
    city = "London"
    hotel_data_dict = {
        "Hotel": ["Hotel A", "Hotel B"],
        "Price": [100, 150],
        "Review": [4.5, 4.0]
    }
    df = create_df_from_scraped_data(check_in, check_out, city, hotel_data_dict)
    assert not df.empty

    # Check row
    assert df.shape[0] == 2

    # Check column
    assert df.shape[1] == 7

    check_in = "2024-06-01"
    check_out = "2024-06-05"
    city = "London"
    hotel_data_dict = {}
    df = create_df_from_scraped_data(check_in, check_out, city, hotel_data_dict)
    assert df.empty

    # Check row
    assert df.shape[0] == 0

    # Check column
    assert df.shape[1] == 0


def test_scraper() -> None:
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    # Define the timezone
    city_timezone = pytz.timezone('Asia/Singapore')

    # Get the current date in the specified timezone
    today = datetime.datetime.now(city_timezone).date()
    month = today.month
    year = today.year
    check_in = datetime.date(year, month, 25).strftime('%Y-%m-%d')
    check_out = datetime.date(year, month, 25) + datetime.timedelta(days=1)
    check_out = check_out.strftime('%Y-%m-%d')

    sqlite_name = 'test_scraper.db'

    hotel_stay = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms,
        group_children=group_children, selected_currency=selected_currency,
        month=month, year=year, sqlite_name=sqlite_name
    )

    scraper = BasicScraper(hotel_stay)
    data_tuple = scraper.start_scraping_process(check_in, check_out)
    df = data_tuple[0]

    assert not df.empty

    # Check column
    assert df.shape[1] == 7


if __name__ == '__main__':
    pytest.main()
