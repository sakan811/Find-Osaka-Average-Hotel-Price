import datetime

import pytz

from japan_avg_hotel_price_finder.graphql_scraper import scrape_whole_month
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