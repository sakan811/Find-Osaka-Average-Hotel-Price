import datetime
import sqlite3

import pytest

from check_missing_dates import scrape_missing_dates, BookingDetails
from japan_avg_hotel_price_finder.sql.sql_query import get_count_of_date_by_mth_asof_today_query


@pytest.mark.asyncio
async def test_scrape_missing_dates() -> None:
    db = 'test_scrape_missing_dates.db'

    booking_details_param = BookingDetails(city='Osaka', group_adults=1, num_rooms=1, group_children=0,
                                           selected_currency='USD', scrape_only_hotel=True, sqlite_name=db)

    today = datetime.datetime.today()
    if today.month == 12:
        month = 1
        year = today.year + 1
    else:
        month = today.month + 1
        year = today.year

    month_str = str(month)
    if len(month_str) == 1:
        month_str = '0' + month_str

    first_missing_date = f'{year}-{month_str}-01'
    second_missing_date = f'{year}-{month_str}-11'
    third_missing_date = f'{year}-{month_str}-20'
    missing_dates = [first_missing_date, second_missing_date, third_missing_date]
    await scrape_missing_dates(missing_dates_list=missing_dates, booking_details_class=booking_details_param)

    with sqlite3.connect(db) as con:
        query = get_count_of_date_by_mth_asof_today_query()
        result = con.execute(query, ('Osaka',)).fetchall()
        for row in result:
            assert row[1] == 3


if __name__ == '__main__':
    pytest.main()
