import datetime

import pytz

from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import scrape_whole_month
from set_details import Details


def test_whole_month_graphql_scraper():
    timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.datetime.now(timezone)
    current_mth = today.month

    details = Details(month=current_mth)

    df = scrape_whole_month(details=details, hotel_filter=True)

    assert not df.empty
    # Check column
    assert df.shape[1] == 7


def test_whole_month_graphql_scraper_past_date():
    timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.datetime.now(timezone)
    past_mth = today.month - 1

    details = Details(month=past_mth)

    df = scrape_whole_month(details=details, hotel_filter=True)

    assert df.empty
